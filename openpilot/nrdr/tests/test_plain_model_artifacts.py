"""Execute portable models on tinygrad's Python backend; no device or model downloads."""
import copy
import io
import os
import pickle
from unittest.mock import patch

import numpy as np
import pytest

from tinygrad import Tensor, TinyJit
from tinygrad.helpers import Context

from openpilot.sunnypilot.modeld_v2 import helpers, plain_artifact as plain
from openpilot.sunnypilot.modeld_v2.plain_artifact_compiler import capture_frame, record_kernel_linear, serialize_jit


@pytest.fixture(autouse=True)
def python_backend():
  with Context(DEV='PYTHON'):
    yield


def tensor(value):
  return Tensor(np.array(value, dtype=np.float32), device='PYTHON').realize()


@pytest.mark.parametrize('short,long', [('f16', 'float16'), ('f32', 'float32'), ('f64', 'float64'), ('bf16', 'bfloat16'),
                                      *[(f'{prefix}{bits}', f'{name}{bits}') for prefix, name in [('i', 'int'), ('u', 'uint')]
                                        for bits in (8, 16, 32, 64)]])
def test_current_portable_dtype_names_match_pinned_runtime(short, long):
  assert plain._dtype(f'dtypes.{short}') == plain._dtype(f'dtypes.{long}')


def compiled(fn, inputs, output_container=None):
  run = TinyJit(fn)
  with record_kernel_linear() as recorded:
    run(**inputs)
    run(**inputs)
  check, _ = capture_frame(run, inputs, output_container)
  return serialize_jit(run, recorded[0], check)


def test_round_trip_weights_reference_cache_and_changed_inputs(tmp_path):
  weights = tensor(np.arange(16).reshape(4, 4) / 16)
  inputs = {'x': tensor([[1, 2, 3, 4]])}
  header, blob = compiled(lambda x: (x @ weights + 1).contiguous(), inputs)
  path = str(tmp_path / 'model.pkl')
  metadata = {'metadata': {'output_slices': {'plan': slice(0, 4)}}}
  plain.write_bundle(path, {'run_policy': (header, blob)}, metadata)
  result = helpers.load_model(path)
  assert result['metadata'] == metadata['metadata']
  assert plain.cache_is_fresh(path)
  assert os.path.getsize(path + '.cache') < os.path.getsize(path) + 8192
  for cached in (False, True):
    with patch.object(plain, 'PlainJit', side_effect=AssertionError('expected cached graph')) if cached else patch.object(plain, 'PlainJit', wraps=plain.PlainJit):
      run = plain.load_model(path, cache=cached)['run_policy']
    for value in (np.zeros((1, 4)), np.full((1, 4), 2)):
      np.testing.assert_allclose(run(x=tensor(value)).numpy(), value @ weights.numpy() + 1, atol=1e-5)
  stat = os.stat(path)
  os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns + 1_000_000))
  assert not plain.cache_is_fresh(path)


@pytest.mark.parametrize('kind', ['tuple', 'list'])
def test_multiple_outputs_and_buffer_views(kind):
  inputs = {'x': tensor(np.arange(16))}
  def fn(x):
    result = (x * 2).contiguous()
    outputs = (result, result[4:8].contiguous())
    return outputs if kind == 'tuple' else list(outputs)
  header, blob = compiled(fn, inputs)
  result = plain.PlainJit(header, blob)(**inputs)
  assert type(result).__name__ == kind
  np.testing.assert_array_equal(result[0].numpy(), np.arange(16) * 2)
  np.testing.assert_array_equal(result[1].numpy(), np.arange(4, 8) * 2)


def test_native_output_container_and_recurrent_state(tmp_path):
  inputs = {'x': tensor([1, 2, 3, 4]), 'state': tensor([0, 0, 0, 0]),
            'output_buffers': {'outputs': tensor([0, 0, 0, 0]), 'next_state': tensor([0, 0, 0, 0])}}
  def fn(x, state, output_buffers):
    output_buffers['outputs'].assign(x + state).realize()
    output_buffers['next_state'].assign(state + 1).realize()
  header, blob = compiled(fn, inputs, 'output_buffers')
  path = str(tmp_path / 'native.pkl')
  plain.write_bundle(path, {'run': (header, blob)})
  for cache in (False, True):
    run = plain.load_model(path, cache=cache)['run']
    for frame in range(4):
      inputs['state'] = tensor(np.full(4, frame))
      assert run(**inputs) is None
      np.testing.assert_array_equal(inputs['output_buffers']['outputs'].numpy(), np.arange(1, 5) + frame)
      np.testing.assert_array_equal(inputs['output_buffers']['next_state'].numpy(), frame + 1)


def test_host_to_device_copy_round_trip(tmp_path):
  inputs = {'host': Tensor(np.arange(8, dtype=np.float32), device='NPY').realize()}
  header, blob = compiled(lambda host: (host.to('PYTHON') + 3).contiguous(), inputs)
  assert any(call['kind'] == 'copy' for call in header['calls'])
  path = str(tmp_path / 'upload.pkl')
  plain.write_bundle(path, {'run': (header, blob)})
  for _ in range(2):
    run = plain.load_model(path)['run']
    np.testing.assert_array_equal(run(**inputs).numpy(), np.arange(8) + 3)


@pytest.mark.parametrize('bad', [np.nan, np.inf, 1234.])
def test_reference_mismatch_is_not_cached(tmp_path, bad):
  header, blob = compiled(lambda x: (x + 1).contiguous(), {'x': tensor([1, 2])})
  header = copy.deepcopy(header)
  damaged = bytearray(blob)
  stored = header['check']['outputs'][0]
  a, b = stored['data']
  values = np.frombuffer(damaged, dtype=stored['dtype'], count=(b - a) // 4, offset=a)
  values[0] = bad
  path = str(tmp_path / 'bad.pkl')
  plain.write_bundle(path, {'run': (header, memoryview(damaged))})
  with pytest.raises(plain.ArtifactMismatch):
    plain.load_model(path)
  assert not os.path.exists(path + '.cache')


def test_matching_nan_reference_is_rejected_and_unverified_execution_cannot_seed_cache(tmp_path):
  header, blob = compiled(lambda x: (x * float('nan')).contiguous(), {'x': tensor([1, 2])})
  path = str(tmp_path / 'nan.pkl')
  plain.write_bundle(path, {'run': (header, blob)})
  plain.load_model(path, verify=False)
  assert not os.path.exists(path + '.cache')
  with pytest.raises(plain.ArtifactMismatch, match='non-finite'):
    plain.load_model(path)


def test_legacy_pickle_dispatch_and_restricted_portable_metadata(tmp_path):
  path = tmp_path / 'legacy.pkl'
  with path.open('wb') as f:
    helpers.dump_oob({'metadata': {'legacy': True}}, f)
  assert not helpers.is_plain_artifact(path)
  assert helpers.load_model(path) == {'metadata': {'legacy': True}}
  payload = path.read_bytes()
  chunked = tmp_path / 'chunked.pkl'
  midpoint = len(payload) // 2
  (tmp_path / 'chunked.pkl.chunkmanifest').write_text('2')
  (tmp_path / 'chunked.pkl.chunk01of02').write_bytes(payload[:midpoint])
  (tmp_path / 'chunked.pkl.chunk02of02').write_bytes(payload[midpoint:])
  assert not helpers.is_plain_artifact(chunked)
  assert helpers.load_model(chunked) == {'metadata': {'legacy': True}}
  with pytest.raises(pickle.UnpicklingError, match='not allowed'):
    plain._MetadataUnpickler(io.BytesIO(pickle.dumps(os.system))).load()


def test_sparse_kernel_slots_preserve_image_shape_without_gpu():
  call = {'signature': [['output', 0, 'dtypes.float', [16]], ['image', 1, 'dtypes.float', [2, 4, 4]]],
          'globals': [0, 3], 'outs': [0], 'ins': [3], 'global_size': [4, 1, 1], 'local_size': [4, 1, 1],
          'name': 'test', 'target': {'device': 'QCOM', 'renderer': 'CL', 'arch': 'a630'}}
  program = plain._program_uop(call, b'placeholder')
  params = program.src[1].src
  assert [p.arg.slot for p in params] == [0, 3]
  assert params[1].arg.image == (2, 4)
  assert program.arg.globals == (0, 3)
