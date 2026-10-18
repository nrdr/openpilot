"""Artifact admission tests never execute a pickle or change device preferences."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from openpilot.nrdr.features.services import model_artifacts as admission
from openpilot.nrdr.tools import model_rebuild


@pytest.fixture
def runtime(monkeypatch):
  manifest = {'precompiled': {}, 'legacy_rebuilds': {}}
  monkeypatch.setattr(admission, 'runtime_provenance', lambda: manifest)
  monkeypatch.setattr(model_rebuild, 'runtime_provenance', lambda: manifest)
  return manifest


def bundle(path, compiler_ref=''):
  return NS(models=[NS(artifact=NS(downloadUri=NS(sha256=admission.artifact_sha256(path))))], tinygradRef=compiler_ref,
            ref='model-source-ref', internalName='PMV2', displayName='Selected Pop')


def test_unknown_default_pkl_is_not_unpickled(tmp_path, runtime):
  path = tmp_path / 'driving.pkl'
  path.write_bytes(b'old ABI')
  with pytest.raises(admission.ModelAdmissionError, match='Rebuild required'):
    admission.admit_default_artifact(path)
  admission.write_artifact_record(path, source_sha256='source')
  assert admission.admit_default_artifact(path) == path
  path.write_bytes(b'changed model')
  with pytest.raises(admission.ModelAdmissionError):
    admission.admit_default_artifact(path)


def test_pinned_precompiled_hash_cannot_admit_pointer_or_different_contents(tmp_path, runtime):
  path = tmp_path / 'big_driving_tinygrad.pkl'
  path.write_bytes(b'pinned upstream model')
  runtime['precompiled'][path.name] = admission.artifact_sha256(path)
  assert admission.admit_default_artifact(path) == path
  path.write_bytes(b'version https://git-lfs.github.com/spec/v1')
  with pytest.raises(admission.ModelAdmissionError):
    admission.admit_default_artifact(path)


def test_model_ref_is_never_assumed_to_be_compiler_ref(tmp_path, runtime):
  path = tmp_path / 'selected.pkl'
  path.write_bytes(b'legacy')
  selection = bundle(path)
  selection.ref = admission.TINYGRAD_RUNTIME_REF
  with pytest.raises(admission.ModelAdmissionError, match='No default was substituted'):
    admission.admit_selected_artifact(path, selection, (1344, 760))
  assert selection.internalName == 'PMV2'
  selection.tinygradRef = admission.TINYGRAD_RUNTIME_REF
  assert admission.admit_selected_artifact(path, selection, (1344, 760)) == path


@pytest.mark.parametrize('change', ['camera', 'sha', 'source', 'verified', 'abi', 'path', 'model', 'compiler'])
def test_migration_requires_every_identity_and_validation_gate(tmp_path, runtime, change):
  path = tmp_path / 'selected.pkl'
  path.write_bytes(b'original selection')
  selected = bundle(path)
  compiled = tmp_path / 'compiled.pkl'
  compiled.write_bytes(b'new compiled model')
  record = {'source_artifact_sha256': selected.models[0].artifact.downloadUri.sha256, 'model_ref': selected.ref,
                'model_name': selected.internalName, 'verified': True, 'camera': [1344, 760], 'artifact': compiled.name,
                'tinygrad_ref': admission.TINYGRAD_RUNTIME_REF, 'artifact_sha256': admission.artifact_sha256(compiled), 'abi': admission.ARTIFACT_ABI}
  stamp = Path(str(path) + '.nrdr-migration.json')
  stamp.write_text(json.dumps(record))
  assert admission.admit_selected_artifact(path, selected, (1344, 760)) == compiled
  key, value = {'camera': ('camera', [1928, 1208]), 'sha': ('artifact_sha256', 'wrong'),
                'source': ('source_artifact_sha256', 'wrong'), 'verified': ('verified', False), 'abi': ('abi', 'old'),
                'path': ('artifact', '../escape.pkl'), 'model': ('model_name', 'default'), 'compiler': ('tinygrad_ref', 'old')}[change]
  record[key] = value
  stamp.write_text(json.dumps(record))
  with pytest.raises(admission.ModelAdmissionError):
    admission.admit_selected_artifact(path, selected, (1344, 760))


def test_atomic_failed_compile_keeps_existing_model_and_stamp(tmp_path, runtime, monkeypatch):
  from openpilot.nrdr.tools import model_compile
  path, source = tmp_path / 'existing.pkl', tmp_path / 'model.onnx'
  path.write_bytes(b'working previous compile')
  source.write_bytes(b'onnx weights')
  stamp = Path(str(path) + '.nrdr-abi.json')
  stamp.write_bytes(b'previous stamp')
  monkeypatch.setattr(model_compile, 'runtime_provenance', lambda: runtime)
  monkeypatch.setattr('sys.argv', ['compile', 'onnx', '--onnx', str(source), '--output', str(path)])
  def fail(*_args, **_kwargs):
    raise RuntimeError('compiler failed')
  monkeypatch.setattr(model_compile.subprocess, 'run', fail)
  with pytest.raises(RuntimeError, match='compiler failed'):
    model_compile.main()
  assert path.read_bytes() == b'working previous compile'
  assert stamp.read_bytes() == b'previous stamp'


def test_pop_recipe_pins_exact_sources_and_preserves_selection(tmp_path, runtime):
  path = tmp_path / 'pop.pkl'
  path.write_bytes(b'selected source')
  digest = hashlib.sha256(path.read_bytes()).hexdigest()
  selection = {'ref': 'source-ref', 'internalName': 'PMV2', 'index': 59, 'overrides': [{'key': 'long', 'value': '.3'}],
                   'models': [{'artifact': {'downloadUri': {'sha256': digest}}}]}
  original = json.dumps(selection, sort_keys=True)
  runtime['legacy_rebuilds'][digest] = {'model_ref': 'source-ref', 'model_name': 'PMV2'}
  assert model_rebuild.rebuild_recipe(selection, path)[0] == digest
  assert json.dumps(selection, sort_keys=True) == original
  selection['internalName'] = 'another model'
  with pytest.raises(admission.ModelAdmissionError):
    model_rebuild.rebuild_recipe(selection, path)


def test_committed_runtime_manifest_matches_the_checked_out_source():
  manifest = json.loads(admission.MANIFEST.read_text(encoding='utf-8'))
  root = Path(__file__).resolve().parents[3] / 'tinygrad_repo'
  if not (root / 'tinygrad/engine/jit.py').exists():
    pytest.skip('Native source bundle must include tinygrad source')
  assert manifest['tinygrad_ref'] == admission.TINYGRAD_RUNTIME_REF
  for name, digest in manifest['tinygrad_files'].items():
    assert hashlib.sha256((root / name).read_bytes().replace(b'\r\n', b'\n')).hexdigest() == digest
