"""Atomic wrapper around the pinned generic ONNX/warp compilers."""
import argparse
from pathlib import Path
import subprocess
import sys
import tempfile

from openpilot.nrdr.features.services import artifact_sha256, runtime_provenance, write_artifact_record


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("kind", choices=("onnx", "warp"))
  parser.add_argument("--output", required=True)
  parser.add_argument("--onnx")
  parser.add_argument("--camera", help="Camera dimensions for warp provenance: WIDTHxHEIGHT")
  args, extra = parser.parse_known_args()
  manifest = runtime_provenance()
  root = Path(__file__).resolve().parents[3]
  compiler = root / "tinygrad_repo/examples/openpilot" / f"compile_{args.kind}.py"
  destination = Path(args.output).resolve()
  destination.parent.mkdir(parents=True, exist_ok=True)
  source_sha = artifact_sha256(args.onnx) if args.onnx else None
  expected = manifest.get('source_models', {}).get(Path(args.onnx).name, {}).get('sha256') if args.onnx else None
  if expected and source_sha != expected:
    raise ValueError('Default ONNX weights do not match the pinned model/runtime migration')
  if args.onnx:
    with open(args.onnx, "rb") as stream:
      if stream.read(64).startswith(b"version https://git-lfs.github.com/spec/v1"):
        raise ValueError("ONNX asset is an LFS pointer, not model weights")
  with tempfile.TemporaryDirectory(prefix=".nrdr-compile-", dir=destination.parent) as staging:
    temporary = Path(staging) / destination.name
    command = [sys.executable, str(compiler)]
    command += [args.onnx, str(temporary)] if args.kind == "onnx" else ["--output", str(temporary)]
    subprocess.run(command + extra, check=True)
    # Verify the output can be decoded before replacing a previous valid build.
    from openpilot.selfdrive.modeld.helpers import load_oob
    import pickle
    with temporary.open("rb") as stream:
      artifact = load_oob(stream) if args.kind == "onnx" else pickle.load(stream)
    required = {"run", "input_specs"} | ({"output_specs"} if args.kind == "onnx" else set())
    if not required.issubset(artifact):
      raise ValueError("Compiler produced an unexpected artifact ABI")
    write_artifact_record(temporary, source_sha256=source_sha,
                          camera=tuple(map(int, args.camera.split("x"))) if args.camera else None)
    record = Path(str(temporary) + ".nrdr-abi.json")
    # Artifact first, provenance last: an interruption fails admission, never admits stale code.
    temporary.replace(destination)
    record.replace(Path(str(destination) + ".nrdr-abi.json"))


if __name__ == "__main__":
  main()
