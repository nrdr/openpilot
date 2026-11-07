"""Rebuild a pinned legacy selection, then explicitly verify its camera/backend offline.

Never changes Params, selected-model identity, installed source, or original chunks.
The verify command runs synthetic frames only; it is not a road-safety validation.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from openpilot.common.file_chunker import open_file_chunked
from openpilot.nrdr.features.services import ARTIFACT_ABI, TINYGRAD_RUNTIME_REF, ModelAdmissionError, artifact_sha256, runtime_provenance


def read_selection(path: Path) -> dict:
  selection = json.loads(path.read_text(encoding="utf-8"))
  if isinstance(selection, str):
    selection = json.loads(selection)
  if not isinstance(selection, dict):
    raise ModelAdmissionError("Expected the saved ModelManager_ActiveBundle JSON, not a replacement selection")
  return selection


def rebuild_recipe(selection: dict, source_artifact: Path) -> tuple[str, dict]:
  source_sha = artifact_sha256(source_artifact)
  recipe = runtime_provenance()["legacy_rebuilds"].get(source_sha)
  if not recipe or recipe["model_ref"] != selection.get("ref") or recipe["model_name"] != selection.get("internalName"):
    raise ModelAdmissionError("No source-pinned rebuild recipe for this exact saved selection; nothing was substituted")
  expected = selection["models"][0]["artifact"]["downloadUri"]["sha256"].lower()
  if source_sha != expected:
    raise ModelAdmissionError("Original selected artifact does not match its saved SHA256")
  return source_sha, recipe


def record_path(source_artifact: Path) -> Path:
  return Path(str(source_artifact) + ".nrdr-migration.json")


def write_record(destination: Path, record: dict) -> None:
  temporary = destination.with_name(destination.name + ".tmp")
  temporary.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
  temporary.replace(destination)


def compile_targets_match(recorded: str, current: str) -> bool:
  """Compare the full target, not Device.DEFAULT's device-family shorthand."""
  from tinygrad.helpers import Target
  try:
    if not recorded or not current:
      return False
    recorded_targets = tuple(Target.parse(target) for target in recorded.split(';'))
    current_targets = tuple(Target.parse(target) for target in current.split(';'))
    return all(target.device for target in recorded_targets + current_targets) and recorded_targets == current_targets
  except (AttributeError, RuntimeError):
    return False


def build(selection: dict, source_artifact: Path, source_dir: Path, camera: tuple[int, int]) -> dict:
  source_artifact = source_artifact.resolve()
  source_sha, recipe = rebuild_recipe(selection, source_artifact)
  for name, asset in recipe["source_models"].items():
    path = source_dir / name
    if not path.is_file() or path.stat().st_size != asset["size"] or artifact_sha256(path) != asset["sha256"]:
      raise ModelAdmissionError(f"Missing or mismatched original ONNX source: {path}")
  device = os.environ.get("DEV", "CPU:LLVM")
  destination_dir = source_artifact.parent / ".nrdr-migrations" / source_sha / TINYGRAD_RUNTIME_REF / f"{camera[0]}x{camera[1]}"
  destination_dir.mkdir(parents=True, exist_ok=True)
  destination = destination_dir / "driving.pkl"
  with tempfile.TemporaryDirectory(prefix="build-", dir=destination_dir) as staging:
    output = Path(staging) / "compiler.pkl"
    command = [sys.executable, "-m", "openpilot.sunnypilot.modeld_v2.compile_modeld", "--model-type", recipe["model_type"],
               "--model-size", "x".join(map(str, recipe["model_size"])), "--camera-resolutions", "x".join(map(str, camera)),
               "--benchmark-runs", "1", "--output", str(output),
               "--vision-onnx", str((source_dir / "driving_vision.onnx").resolve()),
               "--policy-onnx", str((source_dir / "driving_policy.onnx").resolve())]
    if recipe["frame_skip"] is not None:
      command += ["--frame-skip", str(recipe["frame_skip"])]
    subprocess.run(command, check=True, env=dict(os.environ, DEV=device))
    combined = Path(staging) / "driving.pkl"
    with open_file_chunked(str(output)) as source, combined.open("wb") as target:
      shutil.copyfileobj(source, target)
    compiled_sha = artifact_sha256(combined)
    combined.replace(destination)
  record = {"abi": ARTIFACT_ABI, "tinygrad_ref": TINYGRAD_RUNTIME_REF, "source_artifact_sha256": source_sha,
            "model_ref": selection["ref"], "model_name": selection["internalName"], "camera": list(camera),
            "artifact": destination.relative_to(source_artifact.parent).as_posix(), "artifact_sha256": compiled_sha,
            "source_models": recipe["source_models"], "device": device, "verified": False}
  write_record(record_path(source_artifact), record)
  return record


def verify(selection: dict, source_artifact: Path, camera: tuple[int, int]) -> dict:
  import numpy as np
  from tinygrad.device import Device
  from tinygrad.helpers import DEV
  from openpilot.sunnypilot.modeld_v2.helpers import load_oob
  from openpilot.sunnypilot.modeld_v2.model_adapters import get_model_adapter
  from openpilot.sunnypilot.modeld_v2.parse_model_outputs import Parser

  source_artifact = source_artifact.resolve()
  source_sha, recipe = rebuild_recipe(selection, source_artifact)
  record = json.loads(record_path(source_artifact).read_text(encoding="utf-8"))
  target = (source_artifact.parent / record["artifact"]).resolve()
  if (not target.is_relative_to(source_artifact.parent) or record.get("abi") != ARTIFACT_ABI or
      record.get("tinygrad_ref") != TINYGRAD_RUNTIME_REF or record.get("source_artifact_sha256") != source_sha or
      record.get("model_ref") != selection["ref"] or record.get("model_name") != selection["internalName"] or
      record.get("camera") != list(camera) or record.get("source_models") != recipe["source_models"] or
      not compile_targets_match(record.get("device"), repr(DEV)) or record.get("artifact_sha256") != artifact_sha256(target)):
    raise ModelAdmissionError("Rebuild provenance, backend, camera, or artifact changed; refusing verification")
  # Revoke an earlier admission before executing any changed verification path.
  record["verified"] = False
  write_record(record_path(source_artifact), record)
  with target.open("rb") as stream:
    jits = load_oob(stream)
  adapter = get_model_adapter(jits, *camera, Device.DEFAULT, Device.DEFAULT, Device.DEFAULT)
  frames, transforms, _ = adapter.get_dummy_inputs()
  parser = Parser()
  summaries = []
  previous = None
  changed = False
  for frame in range(6):
    for name in frames:
      frames[name][:] = 16 if frame < 3 else 96
    adapter.copy_frames(frames)
    for name, value in adapter.numpy_inputs.items():
      if name in ("tfm", "big_tfm"):
        value[:] = transforms[adapter._road_key if name == "tfm" else adapter._wide_key]
      elif name == "traffic_convention":
        value[:] = [1., 0.]
      elif name in ("lateral_control_params", "action_t"):
        value[:] = [20., .2] if name == "lateral_control_params" else [.3, .4]
    outputs = adapter.run()
    arrays = [output.numpy().flatten() for output in outputs]
    if not arrays or not all(array.size and np.isfinite(array).all() for array in arrays):
      raise ModelAdmissionError("Selected model produced empty/non-finite synthetic outputs")
    parsed = parser.parse_vision_outputs({key: arrays[0][None, sl] for key, sl in adapter.vision_output_slices.items()})
    vision_hidden_state = parsed.get('hidden_state')
    for array, slices in zip(arrays[1:], adapter._policy_slices_list, strict=True):
      policy = parser.parse_policy_outputs({key: array[None, sl] for key, sl in slices.items()})
      parsed = parser.merge_policy_outputs(parsed, policy, vision_hidden_state=vision_hidden_state)
    if "plan" not in parsed or not np.isfinite(parsed["plan"]).all():
      raise ModelAdmissionError("Selected model plan parsing failed")
    flat = np.concatenate(arrays)
    changed |= previous is not None and not np.array_equal(previous, flat)
    previous = flat.copy()
    summaries.append({"sizes": [array.size for array in arrays], "finite": True})
  if not changed:
    raise ModelAdmissionError("Selected model outputs never changed across synthetic inputs")
  adapter.reset_warmup_buffers()
  record.update(verified=True, verification={"kind": "synthetic-adapter-and-parser", "frames": summaries, "input_response_changed": True})
  write_record(record_path(source_artifact), record)
  return record


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("operation", choices=("build", "verify"))
  parser.add_argument("--selection", type=Path, required=True)
  parser.add_argument("--source-artifact", type=Path, required=True)
  parser.add_argument("--source-dir", type=Path)
  parser.add_argument("--camera", required=True, help="WIDTHxHEIGHT")
  args = parser.parse_args()
  # build() uses this default too; set it before importing tinygrad in verify().
  os.environ.setdefault('DEV', 'CPU:LLVM')
  camera = tuple(map(int, args.camera.split("x")))
  if len(camera) != 2 or camera not in ((1344, 760), (1928, 1208)):
    parser.error("Expected a supported C3/C4 camera resolution")
  selection = read_selection(args.selection)
  if args.operation == "build":
    if args.source_dir is None:
      parser.error("build requires --source-dir with the exact pinned ONNX inputs")
    record = build(selection, args.source_artifact, args.source_dir, camera)
  else:
    record = verify(selection, args.source_artifact, camera)
  print(json.dumps(record, indent=2))


if __name__ == "__main__":
  main()
