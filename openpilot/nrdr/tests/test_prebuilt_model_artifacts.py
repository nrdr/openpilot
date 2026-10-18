import json
import hashlib
from pathlib import Path

import pytest

from openpilot.nrdr.tools.release.validate_model_artifacts import LFS_HEADER, validate_model_artifacts
from openpilot.nrdr.features.services import ARTIFACT_ABI, TINYGRAD_RUNTIME_REF


@pytest.fixture
def release_tree(tmp_path):
  models = tmp_path / "openpilot/selfdrive/modeld/models"
  models.mkdir(parents=True)
  for filename in (
    "dm_warp_1928x1208_tinygrad.pkl", "dm_warp_1344x760_tinygrad.pkl",
    "driving_warp_1928x1208_tinygrad.pkl", "driving_warp_1344x760_tinygrad.pkl",
    "dmonitoring_model_tinygrad.pkl", "driving_tinygrad.pkl",
  ):
    (models / filename).write_bytes(b"fixture model data")
    record = {'abi': ARTIFACT_ABI, 'tinygrad_ref': TINYGRAD_RUNTIME_REF, 'device': 'QCOM',
              'artifact_sha256': hashlib.sha256(b'fixture model data').hexdigest(), 'source_sha256': 'pinned source'}
    if '_warp_' in filename:
      record['camera'] = [int(part) for part in filename.split('_')[-2].split('x')]
    (models / (filename + '.nrdr-abi.json')).write_text(json.dumps(record))
  manifest = tmp_path / 'openpilot/nrdr/config/model_artifacts.json'
  manifest.parent.mkdir(parents=True)
  manifest.write_text(json.dumps({'abi': ARTIFACT_ABI, 'tinygrad_ref': TINYGRAD_RUNTIME_REF, 'tinygrad_files': {},
                                 'source_models': {'dmonitoring_model.onnx': {'sha256': 'pinned source'},
                                                   'driving_supercombo.onnx': {'sha256': 'pinned source'}}}))
  return tmp_path, models


def test_accepts_complete_shared_camera_assets(release_tree):
  root, _ = release_tree
  validate_model_artifacts(root)


@pytest.mark.parametrize("filename", (
  "dm_warp_1928x1208_tinygrad.pkl", "dm_warp_1344x760_tinygrad.pkl",
  "driving_warp_1928x1208_tinygrad.pkl", "driving_warp_1344x760_tinygrad.pkl",
  "dmonitoring_model_tinygrad.pkl", "driving_tinygrad.pkl", "driving_tinygrad.pkl.nrdr-abi.json",
))
def test_rejects_missing_assets(release_tree, filename):
  root, models = release_tree
  (models / filename).unlink()
  with pytest.raises(ValueError, match="missing release asset"):
    validate_model_artifacts(root)


@pytest.mark.parametrize("contents", (b"", LFS_HEADER + b"\noid sha256:unhydrated\nsize 2000000\n"))
def test_rejects_empty_or_lfs_asset(release_tree, contents):
  root, models = release_tree
  (models / "dm_warp_1928x1208_tinygrad.pkl").write_bytes(contents)
  with pytest.raises(ValueError):
    validate_model_artifacts(root)


def test_checks_all_chunks_and_accepts_trailing_empty_chunks(release_tree):
  root, models = release_tree
  path = models / "driving_tinygrad.pkl"
  path.unlink()
  Path(f"{path}.chunkmanifest").write_text("2")
  Path(f"{path}.chunk01of02").write_bytes(b"compiled model")
  with pytest.raises(ValueError, match="missing release asset"):
    validate_model_artifacts(root)
  Path(f"{path}.chunk02of02").write_bytes(b"")
  stamp = Path(str(path) + '.nrdr-abi.json')
  record = json.loads(stamp.read_text())
  record['artifact_sha256'] = hashlib.sha256(b'compiled model').hexdigest()
  stamp.write_text(json.dumps(record))
  validate_model_artifacts(root)
  Path(f"{path}.chunk01of02").write_bytes(LFS_HEADER)
  with pytest.raises(ValueError, match="unhydrated"):
    validate_model_artifacts(root)
  Path(f"{path}.chunk01of02").write_bytes(b"")
  with pytest.raises(ValueError, match="empty chunked model"):
    validate_model_artifacts(root)


@pytest.mark.parametrize("count", ("", "0", "-1", "one", "1001"))
def test_bad_manifest_does_not_fall_back_to_whole_model(release_tree, count):
  root, models = release_tree
  (models / "driving_tinygrad.pkl.chunkmanifest").write_text(count)
  with pytest.raises(ValueError):
    validate_model_artifacts(root)


def test_rejects_wrong_backend(release_tree):
  root, models = release_tree
  stamp = models / 'dmonitoring_model_tinygrad.pkl.nrdr-abi.json'
  record = json.loads(stamp.read_text())
  record['device'] = 'CPU'
  stamp.write_text(json.dumps(record))
  with pytest.raises(ValueError, match="QCOM"):
    validate_model_artifacts(root)
