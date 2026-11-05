#!/usr/bin/env python3
"""Bounded desktop captures using the stock Raylib replay runner (no device access)."""
import argparse
import hashlib
import html
import json
import os
import platform
import shutil
import signal
import struct
import subprocess
import sys
from pathlib import Path

if __package__:
  from tools.ui.preview_scenarios import SCENARIOS, UNSUPPORTED, FIXTURE
else:
  from preview_scenarios import SCENARIOS, UNSUPPORTED, FIXTURE

ROOT = Path(__file__).resolve().parents[2]
DEVICES = {"tici": ("C3X", 2160, 1080), "mici": ("C4", 536, 240)}
LIMITATION = "Real desktop UI rendering with synthetic replay messages; no camera feed, vehicle, or physical-device validation."


def capture_environment(device: str, output: Path) -> dict[str, str]:
  env = os.environ.copy()
  # Import-time options must not leak from another local UI session.
  # LOG_ROOT bypasses prefix isolation and OpenpilotPrefix cleans it on exit.
  for key in ("BURN_IN", "PROFILE_STARTUP", "OPENPILOT_PREFIX", "PYTHONOPTIMIZE", "LOG_ROOT", "COMMA_CACHE", "PARAMS_ROOT", "ZMQ"):
    env.pop(key, None)
  env.update({
    "PYTHONPATH": str(ROOT), "PYTHONDONTWRITEBYTECODE": "1",
    "BIG": "1" if device == "tici" else "0", "SUNNYPILOT_UI": "1", "SCALE": "1",
    "RAYLIB_BACKEND": "headless", "WINDOWED": "0", "OFFSCREEN": "1", "FPS": "60",
    "RECORD": "1", "RECORD_OUTPUT": str(output / "replay.mp4"), "RECORD_QUALITY": "0",
    "RECORD_SPEED": "1", "RECORD_BITRATE": "", "ENABLE_VSYNC": "0", "STRICT_MODE": "0",
    "SHOW_FPS": "0", "SHOW_TOUCHES": "0", "SHOW_MOUSE_COORDS": "0", "GRID": "0", "PROFILE_RENDER": "0", "PRIME_TYPE": "0",
  })
  return env


def check_host() -> None:
  if platform.system() != "Linux" or Path("/AGNOS").exists():
    raise RuntimeError("Captures require a Linux PC (Ubuntu 24.04 or WSL2 Ubuntu), not native Windows or an AGNOS device.")
  if sys.version_info[:2] != (3, 12):
    raise RuntimeError("Use the repository's Python 3.12 environment: source .venv/bin/activate")
  missing = [name for name in ("ffmpeg", "ffprobe") if shutil.which(name) is None]
  if missing:
    raise RuntimeError(f"Missing executables: {', '.join(missing)}. Install ffmpeg, libgles2 and libegl1.")


def run_bounded(command: list[str], *, env: dict[str, str], log: Path, timeout: int) -> None:
  # A process group includes the runner's ffmpeg child. Do not leave it behind on timeout.
  with log.open("wb") as stream:
    with subprocess.Popen(command, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True) as proc:
      try:
        result = proc.wait(timeout=timeout)
      except BaseException:
        try:
          os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
          pass
        proc.wait()
        raise
      if result:
        raise RuntimeError(f"Capture exited {result}; see {log.name}")


def png_dimensions(path: Path) -> tuple[int, int]:
  with path.open("rb") as stream:
    header = stream.read(24)
  if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
    raise RuntimeError(f"Not a PNG capture: {path}")
  return struct.unpack(">II", header[16:24])


def validate_markers(markers: dict, device: str) -> None:
  _, width, height = DEVICES[device]
  if markers["device"] != device or markers["size"] != [width, height]:
    raise RuntimeError("Wrong device identity or render size")
  if list(markers["captures"]) != list(SCENARIOS[device]):
    raise RuntimeError("Missing or unexpected replay checkpoints")
  previous = -1
  for name, checkpoint in markers["captures"].items():
    frame = checkpoint["frame"]
    if type(frame) is not int or not previous < frame < markers["end_frame"]:
      raise RuntimeError(f"Invalid checkpoint frame: {name}")
    if checkpoint["started"] != name.startswith("onroad"):
      raise RuntimeError(f"Wrong ignition state: {name}")
    previous = frame


def extract_captures(output: Path, device: str) -> dict:
  markers = json.loads((output / "checkpoints.json").read_text())
  validate_markers(markers, device)
  probe = subprocess.run([
    "ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries",
    "stream=width,height,nb_read_frames", "-of", "json", str(output / "replay.mp4"),
  ], check=True, capture_output=True, text=True, timeout=60)
  video = json.loads(probe.stdout)["streams"][0]
  if [video["width"], video["height"]] != markers["size"] or int(video["nb_read_frames"]) != markers["end_frame"]:
    raise RuntimeError("Replay video size/frame count differs from the verified render checkpoints")
  # Decode once, not once per menu; runtime stays bounded as coverage grows.
  selection = "+".join(f"eq(n\\,{checkpoint['frame']})" for checkpoint in markers["captures"].values())
  subprocess.run([
    "ffmpeg", "-v", "error", "-nostdin", "-n", "-i", str(output / "replay.mp4"),
    "-vf", f"select={selection}", "-fps_mode", "vfr", "-frames:v", str(len(markers["captures"])),
    str(output / "frame-%03d.png"),
  ], check=True, timeout=120)
  if len(list(output.glob("frame-*.png"))) != len(markers["captures"]):
    raise RuntimeError("Encoder did not extract every requested menu checkpoint")
  for index, (name, checkpoint) in enumerate(markers["captures"].items(), start=1):
    destination = output / f"{name}.png"
    (output / f"frame-{index:03d}.png").rename(destination)
    if list(png_dimensions(destination)) != markers["size"]:
      raise RuntimeError(f"Wrong screenshot dimensions: {name}")
    checkpoint["file"] = destination.name
    checkpoint["sha256"] = hashlib.sha256(destination.read_bytes()).hexdigest()
  return markers


def write_report(output: Path, report: dict) -> None:
  (output / "manifest.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
  esc = html.escape
  sections = []
  for device, result in report["devices"].items():
    label, width, height = DEVICES[device]
    sections.append(f"<section><h2>{label} / {device} — {width} × {height}</h2>")
    sections.append("<h3>Unsupported / not captured</h3><ul>" + "".join(
      f"<li>{esc(surface)}: {esc(reason)}</li>" for surface, reason in UNSUPPORTED[device].items()) + "</ul>")
    if result["status"] != "captured":
      sections.append(f'<p class="error">FAILED: {esc(result["error"])}</p><a href="{device}/capture.log">Capture log</a>')
    else:
      for name, checkpoint in result["captures"].items():
        source = f"{device}/{name}.png"
        sections.append(f'<figure><figcaption>{name} · frame {checkpoint["frame"]}</figcaption>' +
                        f'<a href="{source}"><img src="{source}" alt="{label} {name}" loading="lazy"></a></figure>')
      sections.append(f'<p><a href="{device}/replay.mp4">Replay video</a> · <a href="{device}/capture.log">Capture log</a></p>')
    sections.append("</section>")
  page = f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>nrdr UI previews</title><style>
body{{background:#17191d;color:#eee;font:16px system-ui;max-width:1200px;margin:auto;padding:24px}}
a{{color:#89cfff}}img{{max-width:100%;height:auto;border:1px solid #555}}figure{{margin:24px 0}}
figcaption{{margin-bottom:8px}}section{{border-top:1px solid #555;margin-top:24px}}.error{{color:#ffacac}}
</style><h1>nrdr UI previews</h1><p>{esc(LIMITATION)}</p><p>{esc(FIXTURE)}</p>
<p>Source: <code>{esc(report['commit'])}</code> · dirty worktree: {str(report['dirty']).lower()}</p>
<p><a href="manifest.json">Capture provenance and checksums</a></p>{''.join(sections)}</html>
"""
  (output / "index.html").write_text(page, encoding="utf-8")


def capture_worker(device: str, output: Path) -> None:
  check_host()
  if not __debug__:
    raise RuntimeError("Preview state assertions require Python without -O")
  if any(path.name != "capture.log" for path in output.iterdir()):
    raise RuntimeError("Worker output already contains artifacts")
  env = capture_environment(device, output)
  os.environ.clear()
  os.environ.update(env)
  # Keep the PC backend: only select the UI-facing hardware identity. Never instantiate HardwareComma.
  from unittest.mock import patch
  from openpilot.common.hardware import HARDWARE, PC
  from openpilot.common.prefix import OpenpilotPrefix

  if not PC:
    raise RuntimeError("Refusing to run on a physical device")
  with OpenpilotPrefix(), patch.object(HARDWARE, "get_device_type", return_value=device):
    from openpilot.selfdrive.ui.tests.diff import replay
    from tools.ui.preview_scenarios import build_preview_script, setup_vehicle_fixture
    replay.setup_state()  # Must precede importing UI singletons, as in the stock runner.
    setup_vehicle_fixture()
    from openpilot.selfdrive.ui.tests.diff import replay_script
    from openpilot.selfdrive.ui.lib.prime_state import PrimeState

    markers = {"device": device, "captures": {}}

    def build(pm, main_layout, variant):
      return build_preview_script(pm, main_layout, variant, device, markers)

    # No account/network polling for the stock deterministic test dongle.
    with (patch.object(replay_script, "build_script", build), patch.object(replay, "DIFF_OUT_DIR", str(output)),
          patch.object(PrimeState, "start", return_value=None)):
      replay.run_replay("tizi" if device == "tici" else "mici")
    validate_markers(markers, device)
    (output / "checkpoints.json").write_text(json.dumps(markers, indent=2) + "\n", encoding="utf-8")


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--device", choices=["all", *DEVICES], default="all")
  parser.add_argument("--output", type=Path, required=True, help="New or empty directory; existing reports are never overwritten")
  parser.add_argument("--timeout", type=int, default=180, help="Replay timeout per device, seconds (1-600); probe/extraction capped at 60/120s")
  parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
  args = parser.parse_args()
  if not 1 <= args.timeout <= 600:
    parser.error("--timeout must be between 1 and 600 seconds")
  output = args.output.resolve()
  try:
    check_host()
    if args.worker:
      if args.device == "all":
        parser.error("worker requires one device")
      capture_worker(args.device, output)
      return 0
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
      raise RuntimeError("Output must be a new or empty directory (refusing to mix stale screenshots).")
    output.mkdir(parents=True, exist_ok=True)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, timeout=10).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True, timeout=10).strip())
    report = {"commit": commit, "dirty": dirty, "limitation": LIMITATION, "fixture": FIXTURE,
              "unsupported": UNSUPPORTED, "host": platform.platform(), "devices": {}}
    devices = DEVICES if args.device == "all" else [args.device]
    for device in devices:
      target = output / device
      target.mkdir()
      try:
        run_bounded([sys.executable, str(Path(__file__).resolve()), "--worker", "--device", device, "--output", str(target)],
                    env=capture_environment(device, target), log=target / "capture.log", timeout=args.timeout)
        report["devices"][device] = {"status": "captured", **extract_captures(target, device)}
      except (RuntimeError, OSError, subprocess.SubprocessError, ValueError, KeyError, IndexError) as exc:
        report["devices"][device] = {"status": "failed", "error": str(exc)}
        print(f"{device}: {exc}", file=sys.stderr)
      write_report(output, report)
    print(f"Preview report: {output / 'index.html'}")
    return int(any(result["status"] != "captured" for result in report["devices"].values()))
  except (RuntimeError, OSError, subprocess.SubprocessError) as exc:
    print(f"UI preview unavailable: {exc}", file=sys.stderr)
    return 1


if __name__ == "__main__":
  sys.exit(main())
