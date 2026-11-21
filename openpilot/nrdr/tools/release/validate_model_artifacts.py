"""Check shared-device release assets and compiler provenance without unpickling."""

import argparse
import hashlib
import json
from pathlib import Path

from openpilot.common.file_chunker import open_file_chunked
from openpilot.nrdr.features.services import ARTIFACT_ABI, TINYGRAD_RUNTIME_REF

LFS_HEADER = b'version https://git-lfs.github.com/spec/v1'


def _asset_size(path: Path, root: Path) -> int:
  if not path.resolve().is_relative_to(root):
    raise ValueError(f'release asset escapes build tree: {path}')
  if not path.is_file():
    raise ValueError(f'missing release asset: {path}')
  with path.open('rb') as stream:
    if stream.read(len(LFS_HEADER)).startswith(LFS_HEADER):
      raise ValueError(f'unhydrated Git LFS pointer: {path}')
  return path.stat().st_size


def _nonempty(path: Path, root: Path) -> None:
  if _asset_size(path, root) == 0:
    raise ValueError(f'empty release asset: {path}')


def _chunked_asset(path: Path, root: Path) -> str:
  manifest = Path(f'{path}.chunkmanifest')
  # A stray malformed manifest is still a packaging error, even if a whole file
  # currently shadows it in open_file_chunked.
  if manifest.exists():
    _nonempty(manifest, root)
    count_text = manifest.read_text(encoding='ascii').strip()
    if not count_text.isdecimal() or not 1 <= int(count_text) <= 1000:
      raise ValueError(f'invalid chunk count: {manifest}')
    count = int(count_text)
    if sum(_asset_size(Path(f'{path}.chunk{i:02d}of{count:02d}'), root) for i in range(1, count + 1)) == 0:
      raise ValueError(f'empty chunked model: {path}')
  else:
    _nonempty(path, root)
  with open_file_chunked(str(path)) as stream:
    return hashlib.file_digest(stream, 'sha256').hexdigest()


def validate_model_artifacts(build_root: Path) -> None:
  root = build_root.resolve(strict=True)
  models = root / 'openpilot/selfdrive/modeld/models'
  manifest_path = root / 'openpilot/nrdr/config/model_artifacts.json'
  _nonempty(manifest_path, root)
  manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
  if manifest.get('tinygrad_ref') != TINYGRAD_RUNTIME_REF or manifest.get('abi') != ARTIFACT_ABI:
    raise ValueError('release model manifest does not match this compiler ABI')
  for relative, expected in manifest['tinygrad_files'].items():
    path = root / 'tinygrad_repo' / relative
    _nonempty(path, root)
    if hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest() != expected:
      raise ValueError(f'release tinygrad source mismatch: {relative}')

  names = ['dmonitoring_model_tinygrad.pkl', 'driving_tinygrad.pkl']
  names += [f'{prefix}_{resolution}_tinygrad.pkl' for prefix in ('driving_warp', 'dm_warp') for resolution in ('1928x1208', '1344x760')]
  for name in names:
    path = models / name
    digest = _chunked_asset(path, root)
    stamp = Path(str(path) + '.nrdr-abi.json')
    _nonempty(stamp, root)
    record = json.loads(stamp.read_text(encoding='utf-8'))
    if (record.get('abi') != ARTIFACT_ABI or record.get('tinygrad_ref') != TINYGRAD_RUNTIME_REF or
        record.get('artifact_sha256') != digest or record.get('device') != 'QCOM'):
      raise ValueError(f'model provenance/QCOM backend mismatch: {name}')
    if '_warp_' in name:
      expected_camera = [int(part) for part in name.split('_')[-2].split('x')]
      if record.get('camera') != expected_camera:
        raise ValueError(f'warp camera mismatch: {name}')
    elif record.get('source_sha256') != manifest['source_models'][name.replace('_tinygrad.pkl', '.onnx')
         if name.startswith('dmonitoring') else 'driving_supercombo.onnx']['sha256']:
      raise ValueError(f'model source weights mismatch: {name}')

  big_path = models / 'big_driving_tinygrad.pkl'
  if big_path.exists() or Path(str(big_path) + '.chunkmanifest').exists():
    if _chunked_asset(big_path, root) != manifest['precompiled'][big_path.name]:
      raise ValueError('big default does not match the pinned upstream artifact')


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('build_root', type=Path)
  arguments = parser.parse_args()
  validate_model_artifacts(arguments.build_root)
  print('Model asset gate passed: matching compiler ABI, model weights and both C3/C4 camera warps')
