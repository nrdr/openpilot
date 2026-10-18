"""Saved selection identity and per-model compiler provenance; no native I/O."""
import ast
import asyncio
import copy
import hashlib
import os
from pathlib import Path
from types import ModuleType, SimpleNamespace

import numpy as np

import pytest

from openpilot.cereal import custom
from openpilot.nrdr.features.services import ModelAdmissionError, TINYGRAD_RUNTIME_REF


class ParamsMemory:
  def __init__(self, values):
    self.values = copy.deepcopy(values)
    self.writes = []

  def get(self, key):
    return self.values.get(key)

  def put(self, key, value, **_kwargs):
    self.values[key] = value
    self.writes.append((key, value))


def saved_pop(minimum=19):
  return custom.ModelManagerSP.ModelBundle(internalName='PMV2', displayName='Pop Model v2', index=59, generation=12,
                                          ref='source-model-ref', runner='tinygrad', is20hz=True, minimumSelectorVersion=minimum,
                                          overrides=[{'key': 'lat', 'value': '.0'}, {'key': 'long', 'value': '.3'}]).to_dict()


def definitions(relative, namespace):
  path = Path(__file__).resolve().parents[3] / relative
  tree = ast.parse(path.read_text(encoding='utf-8'))
  tree.body = [node for node in tree.body if isinstance(node, (ast.Assign, ast.AnnAssign, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
  module = ModuleType('selection_test')
  module.__dict__.update(namespace)
  exec(compile(tree, str(path), 'exec'), module.__dict__)
  return module


@pytest.fixture
def helpers():
  # Execute all real definitions with platform I/O imports replaced, not mocked
  # selection behavior. Native model-manager tests cover the real import graph.
  return definitions('openpilot/sunnypilot/models/helpers.py', {
    'custom': custom, 'np': np, 'os': os, 'hashlib': hashlib, 'Params': ParamsMemory,
    'Paths': SimpleNamespace(model_root=lambda: ''), 'chestnut_present': lambda: False,
    'cloudlog': SimpleNamespace(error=lambda *_: None)})


def test_selector_v19_retains_exact_pop_preference_and_replaces_only_stale_runner_cache(monkeypatch, helpers):
  raw = saved_pop()
  params = ParamsMemory({'ModelManager_ActiveBundle': raw, 'ModelRunnerTypeCache': int(custom.ModelManagerSP.Runner.stock)})
  monkeypatch.setattr(helpers, 'chestnut_present', lambda: False)
  assert helpers.get_selected_bundle(params).to_dict() == raw
  assert helpers.get_active_model_runner(params) == int(custom.ModelManagerSP.Runner.tinygrad)
  assert params.values['ModelManager_ActiveBundle'] == raw
  assert params.writes == [('ModelRunnerTypeCache', int(custom.ModelManagerSP.Runner.tinygrad))]


@pytest.mark.parametrize('raw', [saved_pop(18), {'invalid': True}, 'not a bundle'])
def test_unsupported_saved_selection_cannot_turn_into_default(raw, helpers):
  params = ParamsMemory({'ModelManager_ActiveBundle': raw})
  with pytest.raises(ModelAdmissionError, match='no default substituted'):
    helpers.get_selected_bundle(params)
  assert params.values['ModelManager_ActiveBundle'] == raw
  assert params.writes == []


def test_catalog_mismatch_keeps_saved_preference(monkeypatch, helpers):
  raw = saved_pop()
  params = ParamsMemory({'ModelManager_ActiveBundle': raw})
  monkeypatch.setattr(helpers, 'cloudlog', SimpleNamespace(error=lambda *_: None))
  helpers._LAST_VALIDATED_RAW.clear()
  helpers._validate_active_bundle(params, 'qcom', [custom.ModelManagerSP.ModelBundle(internalName='other', ref='another-ref')])
  assert params.values['ModelManager_ActiveBundle'] == raw
  assert not params.writes


def test_compiler_ref_is_per_bundle_not_model_source_ref_or_catalog_blanket(helpers):
  # Fetching, manifest writes and networking are outside this pure parser test.
  source = Path(__file__).resolve().parents[3] / 'openpilot/sunnypilot/models/fetcher.py'
  node = next(node for node in ast.parse(source.read_text(encoding='utf-8')).body if isinstance(node, ast.ClassDef) and node.name == 'ModelParser')
  namespace = {'custom': custom, 'is_bundle_version_compatible': helpers.is_bundle_version_compatible}
  exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), 'exec'), namespace)
  ModelParser = namespace['ModelParser']
  base = {'short_name': 'PMV2', 'display_name': 'Pop', 'index': 59, 'generation': 12, 'environment': 'development', 'runner': 'tinygrad',
              'is_20hz': True, 'minimum_selector_version': '19', 'models': [], 'ref': 'model-source', 'overrides': {'long': '.3'}}
  parsed = ModelParser.parse_models({'tinygrad_ref': 'catalog-compiler', 'bundles': [base, dict(base, tinygrad_ref=TINYGRAD_RUNTIME_REF)]})
  assert [bundle.tinygradRef for bundle in parsed] == ['catalog-compiler', TINYGRAD_RUNTIME_REF]
  assert all(bundle.ref == 'model-source' and bundle.overrides[0].value == '.3' for bundle in parsed)


def test_catalog_parsing_does_not_touch_cached_chunk_manifest(tmp_path):
  source = Path(__file__).resolve().parents[3] / 'openpilot/sunnypilot/models/fetcher.py'
  node = next(node for node in ast.parse(source.read_text(encoding='utf-8')).body if isinstance(node, ast.ClassDef) and node.name == 'ModelParser')
  def forbidden(*_args, **_kwargs):
    raise AssertionError('Catalog parser must not write the model cache')
  namespace = {'custom': custom, 'Paths': SimpleNamespace(model_root=forbidden), 'os': SimpleNamespace(makedirs=forbidden)}
  exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), 'exec'), namespace)
  manifest = tmp_path / 'driving.pkl.chunkmanifest'
  manifest.write_text('2')
  artifact = namespace['ModelParser']._parse_artifact({
    'file_name': 'driving.pkl', 'download_uri': {'url': 'https://example.invalid/driving.pkl', 'sha256': 'digest'},
    'chunks': [{'file_name': f'driving.pkl.chunk{i:02d}of03', 'sha256': str(i)} for i in range(1, 4)]})
  assert len(artifact.chunks) == 3
  assert manifest.read_text() == '2'


def test_verified_cache_repairs_manifest_without_a_download_and_removes_stale_whole_file(tmp_path):
  from openpilot.common.file_chunker import get_chunk_name, get_manifest_path
  source = Path(__file__).resolve().parents[3] / 'openpilot/sunnypilot/models/manager.py'
  cls = next(node for node in ast.parse(source.read_text(encoding='utf-8')).body if isinstance(node, ast.ClassDef) and node.name == 'ModelManagerSP')
  node = next(node for node in cls.body if isinstance(node, ast.AsyncFunctionDef) and node.name == '_process_artifact')
  def verify_sync(path, expected):
    return Path(path).is_file() and hashlib.sha256(Path(path).read_bytes()).hexdigest() == expected
  async def verify(path, expected):
    return await asyncio.to_thread(verify_sync, path, expected)
  def forbidden(*_args, **_kwargs):
    raise AssertionError('Verified cache must not access the network')
  namespace = {'os': os, 'custom': custom, 'verify_file': verify, 'DownloadCancelled': type('Cancelled', (Exception,), {}),
               'cloudlog': SimpleNamespace(error=forbidden)}
  exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), 'exec'), namespace)
  artifact = SimpleNamespace(fileName='driving.pkl', downloadUri=SimpleNamespace(uri='https://example.invalid/model', sha256=''),
                             chunks=[], downloadProgress=SimpleNamespace())
  base = tmp_path / artifact.fileName
  base.write_bytes(b'old whole artifact')
  manifest = Path(get_manifest_path(str(base)))
  manifest.write_text('7')
  bodies = (b'new first chunk', b'new second chunk')
  for i, data in enumerate(bodies):
    Path(get_chunk_name(str(base), i, len(bodies))).write_bytes(data)
    artifact.chunks.append(SimpleNamespace(sha256=hashlib.sha256(data).hexdigest()))
  manager = SimpleNamespace(_download_interrupted=lambda: False, _download_chunked=forbidden, _download_file=forbidden,
                            _sync_artifact_progress=lambda *_: None, _report_status=lambda: None)
  asyncio.run(namespace['_process_artifact'](manager, artifact, str(tmp_path)))
  assert manifest.read_text() == '2' and not base.exists()
  assert artifact.downloadProgress.status == custom.ModelManagerSP.DownloadStatus.cached
  for i, data in enumerate(bodies):
    assert Path(get_chunk_name(str(base), i, len(bodies))).read_bytes() == data
