"""Check shared-device release assets without executing model pickle contents."""

import argparse
import json
from pathlib import Path


LFS_HEADER = b"version https://git-lfs.github.com/spec/v1"


def _asset_size(path: Path, root: Path) -> int:
  if not path.resolve().is_relative_to(root):
    raise ValueError(f"release asset escapes build tree: {path}")
  if not path.is_file():
    raise ValueError(f"missing release asset: {path}")
  with path.open("rb") as stream:
    if stream.read(len(LFS_HEADER)).startswith(LFS_HEADER):
      raise ValueError(f"unhydrated Git LFS pointer: {path}")
  return path.stat().st_size


def _nonempty(path: Path, root: Path) -> None:
  if _asset_size(path, root) == 0:
    raise ValueError(f"empty release asset: {path}")


def _chunked_asset(path: Path, root: Path) -> None:
  # Match open_file_chunked: a manifest takes precedence over a whole file.
  manifest = Path(f"{path}.chunkmanifest")
  if not manifest.exists():
    _nonempty(path, root)
    return
  _nonempty(manifest, root)
  count_text = manifest.read_text(encoding="ascii").strip()
  if not count_text.isdecimal() or not 1 <= int(count_text) <= 1000:
    raise ValueError(f"invalid chunk count: {manifest}")
  count = int(count_text)
  total = sum(_asset_size(Path(f"{path}.chunk{i:02d}of{count:02d}"), root) for i in range(1, count + 1))
  # SCons deliberately overestimates chunk counts; trailing empty chunks are valid.
  if total == 0:
    raise ValueError(f"empty chunked model: {path}")


def validate_model_artifacts(build_root: Path) -> None:
  root = build_root.resolve(strict=True)
  models = root / "openpilot/selfdrive/modeld/models"
  for resolution in ("1928x1208", "1344x760"):
    _nonempty(models / f"dm_warp_{resolution}_tinygrad.pkl", root)
  _nonempty(models / "dmonitoring_model_metadata.pkl", root)
  for name in ("dmonitoring_model_tinygrad.pkl", "driving_tinygrad.pkl"):
    _chunked_asset(models / name, root)
  devices_path = models / "tg_input_devices.json"
  _nonempty(devices_path, root)
  devices = json.loads(devices_path.read_text(encoding="utf-8"))
  if devices.get("openpilot.selfdrive.modeld.dmonitoringmodeld", {}).get("default", {}).get("DEV") != "QCOM":
    raise ValueError("shared comma release is missing the QCOM driver-monitoring backend")


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("build_root", type=Path)
  arguments = parser.parse_args()
  validate_model_artifacts(arguments.build_root)
  print("Model asset gate passed: driving model, driver monitoring, and both C3/C4 camera warps")
