"""Actual adapter construction/NPY buffers with synthetic JITs, not GPU inference."""
import __future__
import ast
import base64
from pathlib import Path
import pickle
from types import SimpleNamespace as NS

import numpy as np
import pytest

from tinygrad.helpers import Context, DEV
from tinygrad.tensor import Tensor

from openpilot.nrdr.tools.model_rebuild import compile_targets_match

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture
def adapters():
  # NPY allocations and pointer views require neither LLVM nor a physical GPU.
  # Every production queue constructor is still used, not replaced with a mock.
  with Context(DEV='NPY'):
    from openpilot.sunnypilot.modeld_v2 import model_adapters
    yield model_adapters


def model_run_definition():
  source = ROOT / 'openpilot/sunnypilot/modeld_v2/modeld.py'
  cls = next(node for node in ast.parse(source.read_text(encoding='utf-8')).body if isinstance(node, ast.ClassDef) and node.name == 'ModelState')
  method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == 'run')
  namespace = {'np': np}
  exec(compile(ast.Module(body=[method], type_ignores=[]), str(source), 'exec', flags=__future__.annotations.compiler_flag), namespace)
  return namespace['run']


@pytest.mark.parametrize('chestnut', [False, True])
@pytest.mark.parametrize('layout,bad_output', [('supercombo', 0), ('multi_policy', 0), ('multi_policy', 1), ('multi_policy', 2)])
@pytest.mark.parametrize('bad_value', [np.nan, np.inf])
def test_invalid_inference_is_rejected_before_parsing_on_all_hardware(chestnut, layout, bad_output, bad_value):
  arrays = [np.ones(2, dtype=np.float32) for _ in range(1 if layout == 'supercombo' else 3)]
  arrays[bad_output][0] = bad_value
  tensors = [NS(numpy=lambda arr=arr: arr) for arr in arrays]
  def no_parse(*_args):
    raise AssertionError('invalid inference must not reach parsing/publication')
  state = NS(adapter=NS(copy_frames=lambda bufs: None, is_native=False,
                       run=lambda: tensors[0] if layout == 'supercombo' else tensors),
             numpy_inputs={'desire': np.zeros(8), 'tfm': np.eye(3), 'big_tfm': np.eye(3)},
             desire_key='desire', prev_desire=np.zeros(8), _road_key='img', _wide_key='big_img',
             chestnut=chestnut, _combined_model_type=layout, vision_output_slices={'plan': slice(0, 2)},
             parser=NS(parse_outputs=no_parse, parse_vision_outputs=no_parse))
  with pytest.raises(RuntimeError, match='model output not finite'):
    model_run_definition()(state, {}, {'img': np.eye(3), 'big_img': np.eye(3)}, {'desire': np.zeros(8)})


@pytest.mark.parametrize('camera', [(1344, 760), (1928, 1208)])
def test_native_recurrent_image_state_is_not_a_camera_and_both_transforms_are_filled(adapters, camera):
  captures = []
  def warp(*, input_frame, M_inv):
    captures.append((input_frame.numpy().copy(), M_inv.numpy().copy()))
    return Tensor(np.zeros((2, 6, 2, 2), dtype=np.uint8), device='NPY')
  def model(*, output_buffers, **inputs):
    assert inputs['new_img'].shape == (2, 6, 2, 2)
    assert inputs['state_img_q'].shape == (2, 1, 6, 2, 2)
    np.testing.assert_array_equal(inputs['state_img_q'].numpy(), 0)
    output_buffers['outputs'].numpy()[:] = [[.1, .2]]
  specs = {'new_img': ((2, 6, 2, 2), '|u1', 'NPY'), 'state_img_q': ((2, 1, 6, 2, 2), '|u1', 'NPY'),
           'desire': ((8,), '<f4', 'NPY'), 'traffic_convention': ((2,), '<f4', 'NPY'), 'action_t': ((2,), '<f4', 'NPY')}
  metadata = {'input_shapes': {key: value[0] for key, value in specs.items()},
              'output_shapes': {'outputs': (1, 2), 'next_state_img_q': (2, 1, 6, 2, 2)},
              'metadata': {'output_slices': base64.b64encode(pickle.dumps({'plan': slice(0, 2)})).decode()}}
  jits = {'input_specs': specs, 'metadata': metadata, 'run': model,
          'output_specs': {'outputs': ((1, 2), '<f4', 'NPY'), 'next_state_img_q': ((2, 1, 6, 2, 2), '|u1', 'NPY')}, camera: warp}
  adapter = adapters.get_model_adapter(jits, *camera, 'NPY', 'NPY', 'NPY')
  assert adapter._vision_input_names == ['img', 'big_img']
  assert (adapter._road_key, adapter._wide_key) == ('img', 'big_img')
  assert 'state_img_q' in adapter.state_pairs and 'state_img_q' not in adapter.frame_buf_params
  frames, transforms, inputs = adapter.get_dummy_inputs()
  assert set(frames) == set(transforms) == {'img', 'big_img'}
  state = NS(adapter=adapter, numpy_inputs=adapter.numpy_inputs, desire_key=adapter._desire_key,
             prev_desire=np.zeros(8), _vision_input_names=adapter._vision_input_names, chestnut=False,
             _combined_model_type='supercombo', vision_output_slices=adapter.vision_output_slices,
             parser=NS(parse_outputs=lambda outputs: outputs))
  run = model_run_definition()
  # Same path warmup uses: both camera transforms must be initialized.
  run(state, frames, transforms, inputs)
  np.testing.assert_array_equal(captures[-1][1], np.stack([np.eye(3), np.eye(3)]))
  frames['img'][:] = 17
  frames['big_img'][:] = 93
  transforms['img'][0, 2] = 2.
  transforms['big_img'][0, 2] = 9.
  result = run(state, frames, transforms, inputs)
  np.testing.assert_array_equal(captures[-1][0][0], 17)
  np.testing.assert_array_equal(captures[-1][0][1], 93)
  np.testing.assert_array_equal(captures[-1][1], np.stack([transforms['img'], transforms['big_img']]))
  assert result['plan'].shape == (1, 2)


@pytest.mark.parametrize('chestnut', [False, True])
@pytest.mark.parametrize('portable', [False, True])
@pytest.mark.parametrize('layout', ['split', 'separate_supercombo', 'unified_supercombo'])
def test_legacy_dispatch_depends_on_artifact_layout_not_hardware(adapters, chestnut, portable, layout):
  camera = (16, 16)
  image_shapes = {'img': (1, 12, 2, 2), 'big_img': (1, 12, 2, 2)}
  policy_shapes = {'features_buffer': (1, 2, 2), 'desire_pulse': (1, 2, 8), 'traffic_convention': (1, 2)}
  metadata = ({'vision': {'input_shapes': image_shapes, 'output_slices': {'hidden_state': slice(0, 2)}},
               'policy': {'input_shapes': policy_shapes, 'output_slices': {'plan': slice(0, 2)}}} if layout == 'split' else
              {'model': {'input_shapes': image_shapes | policy_shapes, 'output_slices': {'plan': slice(0, 2)}}})
  warped_result, policy_calls, warp_calls = object(), [], []
  def warp(**inputs):
    warp_calls.append(inputs)
    return warped_result
  def policy(warped, **inputs):
    assert warped is warped_result
    policy_calls.append(inputs)
    return warped
  def unified(**inputs):
    policy_calls.append(inputs)
    assert set(inputs) == {'img_q', 'big_img_q', 'feat_q', 'desire_q', 'packed_npy_inputs'}
    return inputs['packed_npy_inputs']
  jits = {'metadata': metadata, camera: unified if layout == 'unified_supercombo' else warp}
  if portable:
    jits['input_devices'] = {'warp': 'NPY'}
  if layout != 'unified_supercombo':
    jits['run_policy'] = policy
  adapter = adapters.get_model_adapter(jits, *camera, 'NPY', 'NPY', 'NPY', chestnut=chestnut)
  adapter.numpy_inputs['tfm'][:] = 3
  adapter.numpy_inputs['big_tfm'][:] = 7
  adapter.numpy_inputs['desire'][:] = .25
  if not adapter.is_unified:
    np.testing.assert_array_equal(adapter.input_queues['tfm'].numpy(), 3)
    np.testing.assert_array_equal(adapter.input_queues['big_tfm'].numpy(), 7)
    assert np.count_nonzero(adapter.input_queues['packed_npy_inputs'].numpy() == .25) == 8
  assert adapter.is_unified == (layout == 'unified_supercombo')
  assert hasattr(adapter, 'frame_slots') == adapter.is_unified
  frames, _, _ = adapter.get_dummy_inputs()
  frames[adapter._road_key][:] = 37
  frames[adapter._wide_key][:] = 81
  adapter.copy_frames(frames)
  result = adapter.run()
  assert len(policy_calls) == 1
  if adapter.is_unified:
    assert adapter.run_warp is None and not warp_calls
    np.testing.assert_array_equal(adapter.frame_slots['img'], 37)
    np.testing.assert_array_equal(adapter.frame_slots['big_img'], 81)
  else:
    assert result is warped_result and len(warp_calls) == 2  # constructor warmup + run
    np.testing.assert_array_equal(warp_calls[-1]['frame'].numpy(), 37)
    np.testing.assert_array_equal(warp_calls[-1]['big_frame'].numpy(), 81)
    adapter.reset_warmup_buffers()
    assert not adapter.full_frames and not adapter._blob_cache


def test_legacy_missing_camera_is_explicitly_unsupported_not_a_generic_warp_abi_swap(adapters, monkeypatch):
  metadata = {'vision': {'input_shapes': {'img': (1, 12, 2, 2), 'big_img': (1, 12, 2, 2)}, 'output_slices': {}},
              'policy': {'input_shapes': {'desire_pulse': (1, 2, 8), 'features_buffer': (1, 2, 2)}, 'output_slices': {}}}
  def forbidden(*_args):
    raise AssertionError('Do not load a generic warp into the legacy call contract')
  monkeypatch.setattr(adapters.BaseModelAdapter, '_load_warp', forbidden)
  with pytest.raises(ValueError, match='rebuild it for this camera'):
    adapters.get_model_adapter({'metadata': metadata, 'run_policy': object()}, 16, 16, 'NPY', 'NPY', 'NPY', chestnut=True)


@pytest.mark.parametrize('device_inputs', [False, True])
def test_legacy_input_memory_matches_artifact_and_host_updates_reach_device(monkeypatch, device_inputs):
  from openpilot.sunnypilot.modeld_v2.compile_modeld import make_split_input_queues
  monkeypatch.delenv('CHESTNUT', raising=False)
  vision = {'img': (1, 12, 2, 2), 'big_img': (1, 12, 2, 2)}
  policy = {'desire_pulse': (1, 2, 8), 'features_buffer': (1, 2, 2), 'traffic_convention': (1, 2)}
  queues, arrays = make_split_input_queues(vision, policy, 2, device='PYTHON', device_inputs=device_inputs)
  for name in ('tfm', 'big_tfm', 'packed_npy_inputs'):
    assert queues[name].device == ('PYTHON' if device_inputs else 'NPY')
  for value in (.25, .75):
    arrays['tfm'][:] = value
    arrays['big_tfm'][:] = -value
    arrays['desire'][:] = value
    np.testing.assert_array_equal(queues['tfm'].numpy(), value)
    np.testing.assert_array_equal(queues['big_tfm'].numpy(), -value)
    assert np.count_nonzero(queues['packed_npy_inputs'].numpy() == value) == 8


@pytest.mark.parametrize('target,expected', [
  ('CPU:LLVM', 'CPU'), ('USB+AMD:LLVM', 'AMD'), ('QCOM', 'QCOM'), ('USB:1+AMD:LLVM:gfx1100', 'AMD'),
])
def test_full_compiler_target_matches_context_even_when_default_is_only_device_family(target, expected):
  from tinygrad.device import Device
  with Context(DEV=target):
    assert Device.DEFAULT == expected
    assert compile_targets_match(target, repr(DEV))


@pytest.mark.parametrize('recorded,current', [
  ('CPU:LLVM', 'CPU:CLANG'), ('USB+AMD:LLVM', 'PCI+AMD:LLVM'), ('USB:0+AMD:LLVM', 'USB:1+AMD:LLVM'),
  ('AMD:LLVM:gfx1100', 'AMD:LLVM:gfx1200'), ('QCOM', 'CPU:LLVM'), (';', ';'), ('', ''),
])
def test_full_compiler_target_rejects_different_renderer_interface_index_or_architecture(recorded, current):
  assert not compile_targets_match(recorded, current)


def test_verifier_uses_full_context_target_not_normalized_device_default():
  tree = ast.parse((ROOT / 'openpilot/nrdr/tools/model_rebuild.py').read_text(encoding='utf-8'))
  verify = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'verify')
  call = next(node for node in ast.walk(verify) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
              and node.func.id == 'compile_targets_match')
  assert ast.unparse(call.args[1]) == 'repr(DEV)'
