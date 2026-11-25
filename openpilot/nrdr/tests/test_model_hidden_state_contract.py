"""Declared ONNX heads and per-frame vision features, without model/GPU execution."""
import __future__
import ast
import base64
from functools import partial
import importlib
from pathlib import Path
import pickle
import sys
from types import SimpleNamespace as NS

import numpy as np
import pytest

from openpilot.sunnypilot.modeld_v2.parse_model_outputs import Parser


@pytest.mark.parametrize('module_name', [
  'openpilot.sunnypilot.modeld_v2.compile_modeld',
  'openpilot.sunnypilot.modeld_v2.get_model_metadata',
])
@pytest.mark.parametrize('declared', [
  {'hidden_state': slice(1064, 1576), 'meta': slice(0, 55)},
  {'plan': slice(0, 990), 'desire_state': slice(990, 998), 'pad': slice(-2, None)},
  {},
])
def test_metadata_readers_preserve_only_declared_heads(tmp_path, module_name, declared):
  # The policy slices are the exact declaration in pinned Pop ONNX 853c6634...
  # Its real 512-element vision feature is 1064:1576 in ONNX 940e9006...
  module = importlib.import_module(module_name)
  def varint(value):
    result = bytearray()
    while value >= 128:
      result.append((value & 127) | 128)
      value >>= 7
    return bytes(result + bytes([value]))

  def field(number, payload):
    return varint((number << 3) | 2) + varint(len(payload)) + payload

  # A metadata-only ONNX ModelProto. Both actual production protobuf readers
  # and their metadata extraction run; no graph, weights or inference needed.
  prop = field(1, b'output_slices') + field(2, base64.b64encode(pickle.dumps(declared)))
  path = tmp_path / 'metadata.onnx'
  path.write_bytes(field(14, prop))
  actual = module.make_metadata_dict(path)
  assert actual['output_slices'] == declared


def _model_run():
  source = Path(__file__).resolve().parents[3] / 'openpilot/sunnypilot/modeld_v2/modeld.py'
  tree = ast.parse(source.read_text(encoding='utf-8'))
  cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'ModelState')
  method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == 'run')
  namespace = {'np': np}
  exec(compile(ast.Module(body=[method], type_ignores=[]), str(source), 'exec',
               flags=__future__.annotations.compiler_flag), namespace)
  return namespace['run']


@pytest.mark.parametrize('fabricated_policy_slice', [False, True])
@pytest.mark.parametrize('policy_count', [1, 2])
@pytest.mark.parametrize('has_prev_feature', [False, True])
@pytest.mark.parametrize('runtime', [
  'portable-source',
  pytest.param('imported-model-state', marks=pytest.mark.skipif(sys.platform == 'win32',
               reason='Real ModelState import requires native msgq/Params; exercised by the Linux native gate')),
])
def test_split_export_is_the_current_vision_feature_and_other_heads_are_unchanged(
    fabricated_policy_slice, policy_count, has_prev_feature, runtime):
  rng = np.random.default_rng(73)
  vision = rng.standard_normal((1, 1576)).astype(np.float32)
  policies = [rng.standard_normal((1, 1000)).astype(np.float32) + i * 10 for i in range(policy_count)]
  slices = {'plan': slice(0, 990), 'desire_state': slice(990, 998), 'pad': slice(-2, None)}
  if fabricated_policy_slice:
    # Existing rebuilt artifacts contain this invented, overlapping policy head.
    slices['hidden_state'] = slice(0, 512)
  raw = tuple(NS(numpy=lambda value=value: value) for value in [vision, *policies])
  numpy_inputs = {'desire': np.zeros(8, dtype=np.float32), 'tfm': np.zeros((3, 3)), 'big_tfm': np.zeros((3, 3))}
  if has_prev_feature:
    numpy_inputs['prev_feat'] = np.zeros(512, dtype=np.float32)
  attrs = {'adapter': NS(is_native=False, copy_frames=lambda _: None, run=lambda: raw),
           'numpy_inputs': numpy_inputs, '_desire_key': 'desire', 'prev_desire': np.zeros(8), 'generation': 12,
           '_road_key': 'img', '_wide_key': 'big_img', 'chestnut': False, 'parser': Parser(),
           '_combined_model_type': 'split' if policy_count == 1 else 'multi_policy',
           'vision_output_slices': {'hidden_state': slice(1064, 1576)},
           '_policy_slices_list': [dict(slices) for _ in policies],
           '_policy_keys': ['policy'] if policy_count == 1 else ['off_policy', 'on_policy'],
           '_has_on_policy': policy_count == 2}
  if runtime == 'imported-model-state':
    from openpilot.sunnypilot.modeld_v2.modeld import ModelState
    # Keep the real class/properties/run/parser; substitute only inference and
    # frame transport. No constructor, GPU model, Params or live IPC needed.
    state = ModelState.__new__(ModelState)
    state.__dict__.update(attrs)
    run = state.run
  else:
    state = NS(**attrs, desire_key='desire')
    run = partial(_model_run(), state)
  transforms = {'img': np.eye(3), 'big_img': np.eye(3)}
  result = run({}, transforms, {'desire': np.zeros(8)})
  expected_policy = Parser().parse_policy_outputs({key: policies[-1][:, value].copy() for key, value in slices.items()})
  assert set(result) == set(expected_policy) | {'hidden_state'}
  np.testing.assert_array_equal(result['hidden_state'], vision[:, 1064:1576])
  for key, value in expected_policy.items():
    if key != 'hidden_state':
      np.testing.assert_array_equal(result[key], value)
  if has_prev_feature:
    np.testing.assert_array_equal(numpy_inputs['prev_feat'], vision[0, 1064:1576])

  # It is this frame's feature, not last frame's queue value or a mutable view
  # into the next inference. Do not fix the export by dropping the latent head.
  before = result['hidden_state'].copy()
  vision[:] += 2
  for policy in policies:
    policy[:] -= 3
  following = run({}, transforms, {'desire': np.zeros(8)})
  np.testing.assert_array_equal(following['hidden_state'], vision[:, 1064:1576])
  np.testing.assert_array_equal(result['hidden_state'], before)


def test_merge_preserves_policy_hidden_state_when_vision_does_not_declare_one():
  policy_hidden = np.array([[19., 23.]], dtype=np.float32)
  parsed = {'plan': np.ones((1, 2), dtype=np.float32), 'hidden_state': policy_hidden}
  result = Parser.merge_policy_outputs({}, parsed, vision_hidden_state=None)
  assert set(result) == set(parsed)
  assert result['hidden_state'] is policy_hidden


def test_verifier_uses_the_runtime_merge_with_the_original_vision_feature():
  source = Path(__file__).resolve().parents[3] / 'openpilot/nrdr/tools/model_rebuild.py'
  tree = ast.parse(source.read_text(encoding='utf-8'))
  verify = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'verify')
  calls = [node for node in ast.walk(verify) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
           and node.func.attr == 'merge_policy_outputs']
  assert len(calls) == 1
  assert ast.unparse(calls[0].func) == 'parser.merge_policy_outputs'
  assert ast.unparse(next(arg.value for arg in calls[0].keywords if arg.arg == 'vision_hidden_state')) == 'vision_hidden_state'
