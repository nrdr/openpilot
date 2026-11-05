"""Portable tooling tests. These do not render UI or stand in for capture validation."""
import ast
import copy
from dataclasses import dataclass
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, patch

from tools.ui import capture_preview as preview
from tools.ui.preview_scenarios import MICI_LONGITUDINAL_INDEX, READ_ONLY_KEYS, build_preview_script, focus_item, open_read_only_selector, setup_vehicle_fixture


def checkpoints(device="tici"):
  return {
    "device": device, "size": list(preview.DEVICES[device][1:]), "end_frame": 453,
    "captures": {name: {"frame": 5 + index * 20, "started": name.startswith("onroad")}
                 for index, name in enumerate(preview.SCENARIOS[device])},
  }


class TestPreview(unittest.TestCase):
  def test_fixture_skips_optional_first_run_downloads(self):
    params = Mock()
    params_module = ModuleType("openpilot.common.params")
    params_module.Params = Mock(return_value=params)
    structs_module = ModuleType("opendbc.car.structs")
    structs_module.car = Mock()
    cereal_module = ModuleType("openpilot.cereal")
    cereal_module.custom = Mock()
    with patch.dict(sys.modules, {"openpilot.common.params": params_module, "opendbc.car.structs": structs_module,
                                 "openpilot.cereal": cereal_module}):
      setup_vehicle_fixture()
    params.put_bool.assert_any_call("NrdrFirstRunSetupDone", True, block=True)
    params.put_bool.assert_any_call("NrdrSuggestedSettings", False, block=True)
    self.assertFalse(any(call.args[0].startswith("Osm") for call in params.method_calls))

  def test_device_environment_is_explicit_and_isolated(self):
    inherited = {"BIG": "1", "SCALE": "0.4", "WINDOWED": "1", "RECORD_SPEED": "4", "BURN_IN": "1",
                 "OPENPILOT_PREFIX": "live", "SUNNYPILOT_UI": "0", "PYTHONOPTIMIZE": "1", "PRIME_TYPE": "5",
                 "LOG_ROOT": "/live/logs", "COMMA_CACHE": "/live/cache", "PARAMS_ROOT": "/live/params", "ZMQ": "1"}
    with patch.dict(os.environ, inherited):
      for device in preview.DEVICES:
        env = preview.capture_environment(device, Path("capture"))
        self.assertEqual(env["BIG"], "1" if device == "tici" else "0")
        for name in ("SCALE", "RECORD_SPEED", "SUNNYPILOT_UI"):
          self.assertEqual(env[name], "1")
        self.assertEqual(env["RAYLIB_BACKEND"], "headless")
        self.assertEqual(env["PRIME_TYPE"], "0")
        self.assertNotIn("OPENPILOT_PREFIX", env)
        self.assertNotIn("BURN_IN", env)
        self.assertNotIn("PYTHONOPTIMIZE", env)
        for key in ("LOG_ROOT", "COMMA_CACHE", "PARAMS_ROOT", "ZMQ"):
          self.assertNotIn(key, env)
      self.assertEqual(os.environ["OPENPILOT_PREFIX"], "live")

  def test_checkpoints_cover_both_devices(self):
    for device in preview.DEVICES:
      preview.validate_markers(checkpoints(device), device)

  def test_checkpoints_reject_wrong_identity_size_state_and_frames(self):
    changes = [
      lambda m: m.update(device="mici"),
      lambda m: m.update(size=[1080, 540]),
      lambda m: m["captures"].pop("settings"),
      lambda m: m["captures"]["onroad"].update(started=False),
      lambda m: m["captures"]["onroad"].update(frame=453),
      lambda m: m["captures"]["settings"].update(frame=60),
    ]
    for change in changes:
      with self.subTest(change=change):
        markers = checkpoints()
        change(markers)
        with self.assertRaises(RuntimeError):
          preview.validate_markers(markers, "tici")

  def test_png_dimensions_reject_non_image(self):
    with tempfile.TemporaryDirectory() as folder:
      path = Path(folder) / "test-header.png"
      path.write_bytes(b"not a screenshot")
      with self.assertRaises(RuntimeError):
        preview.png_dimensions(path)
      # Header-only unit fixture, never delivered as a captured image.
      path.write_bytes(b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", 536, 240))
      self.assertEqual(preview.png_dimensions(path), (536, 240))

  def test_report_only_links_successful_captures_and_escapes_errors(self):
    report = {"commit": "test", "dirty": True, "devices": {
      "tici": {"status": "captured", **checkpoints()},
      "mici": {"status": "failed", "error": "<script>not an image</script>"},
    }}
    with tempfile.TemporaryDirectory() as folder:
      output = Path(folder)
      preview.write_report(output, report)
      page = (output / "index.html").read_text(encoding="utf-8")
      self.assertEqual(page.count("<img "), len(preview.SCENARIOS["tici"]))
      self.assertNotIn("mici/offroad.png", page)
      self.assertIn("No native mici steer-ratio menu", page)
      self.assertNotIn("mici/steer-ratio.png", page)
      self.assertIn("&lt;script&gt;", page)
      self.assertIn(preview.LIMITATION, page)
      self.assertEqual(json.loads((output / "manifest.json").read_text()), report)

  def test_extraction_rejects_truncated_or_wrong_size_video(self):
    with tempfile.TemporaryDirectory() as folder:
      output = Path(folder)
      (output / "checkpoints.json").write_text(json.dumps(checkpoints()))
      for stream in ({"width": 2160, "height": 1080, "nb_read_frames": "452"},
                     {"width": 536, "height": 240, "nb_read_frames": "453"}):
        result = subprocess.CompletedProcess([], 0, stdout=json.dumps({"streams": [stream]}))
        with patch.object(preview.subprocess, "run", return_value=result) as run:
          with self.assertRaisesRegex(RuntimeError, "size/frame count"):
            preview.extract_captures(output, "tici")
          self.assertEqual(run.call_count, 1)  # No PNGs extracted from invalid video.

  def test_extracts_exact_checkpoint_frames_and_hashes(self):
    with tempfile.TemporaryDirectory() as folder:
      output = Path(folder)
      (output / "checkpoints.json").write_text(json.dumps(checkpoints()))
      commands = []

      def run(command, **kwargs):
        commands.append(command)
        if command[0] == "ffprobe":
          return subprocess.CompletedProcess(command, 0, stdout=json.dumps({"streams": [
            {"width": 2160, "height": 1080, "nb_read_frames": "453"},
          ]}))
        for index in range(1, len(preview.SCENARIOS["tici"]) + 1):
          Path(command[-1].replace("%03d", f"{index:03d}")).write_bytes(b"unit-test-only")
        return subprocess.CompletedProcess(command, 0)

      with patch.object(preview.subprocess, "run", side_effect=run), patch.object(preview, "png_dimensions", return_value=(2160, 1080)):
        markers = preview.extract_captures(output, "tici")
      self.assertEqual(len(commands), 2)  # One probe and one decode for every surface.
      selection = commands[1][commands[1].index("-vf") + 1]
      for index, name in enumerate(preview.SCENARIOS["tici"]):
        self.assertIn(f"eq(n\\,{5 + index * 20})", selection)
        self.assertIn("-n", commands[1])
        self.assertEqual(markers["captures"][name]["file"], f"{name}.png")
        self.assertEqual(len(markers["captures"][name]["sha256"]), 64)

  @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "optional ffmpeg integration check")
  def test_real_encoder_extraction_with_test_pattern_not_ui_capture(self):
    # Generated test pattern is temporary codec test data, not a UI preview artifact.
    with tempfile.TemporaryDirectory() as folder:
      output = Path(folder)
      subprocess.run([
        "ffmpeg", "-v", "error", "-nostdin", "-f", "lavfi", "-i", "testsrc2=size=536x240:rate=60",
        "-frames:v", "453", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(output / "replay.mp4"),
      ], check=True, timeout=30)
      (output / "checkpoints.json").write_text(json.dumps(checkpoints("mici")))
      result = preview.extract_captures(output, "mici")
      hashes = {checkpoint["sha256"] for checkpoint in result["captures"].values()}
      self.assertEqual(len(hashes), len(preview.SCENARIOS["mici"]))
      for name in preview.SCENARIOS["mici"]:
        self.assertEqual(preview.png_dimensions(output / f"{name}.png"), (536, 240))

  def test_only_existing_layout_surfaces_are_promised(self):
    self.assertTrue({"lateral", "longitudinal", "steer-ratio", "override", "lane-centering", "dm"} <= set(preview.SCENARIOS["tici"]))
    for name in ("lateral", "longitudinal", "steer-ratio", "override"):
      self.assertNotIn(name, preview.SCENARIOS["mici"])
      self.assertIn(name, preview.UNSUPPORTED["mici"])
    for device, names in preview.SCENARIOS.items():
      self.assertEqual(len(names), len(set(names)))
      self.assertLessEqual(len(names), 17)
      self.assertTrue({"engine-braking", "overshoot"} <= set(names))
      self.assertTrue({"onroad-personality", "onroad-lane-centering", "onroad-dm"} <= set(names))
      self.assertIn("advanced-dm", preview.UNSUPPORTED[device])

  def test_new_compact_controls_follow_unchanged_first_five(self):
    self.assertEqual(MICI_LONGITUDINAL_INDEX["longitudinal-pcm"], 2)
    self.assertEqual(MICI_LONGITUDINAL_INDEX["longitudinal-learning"], 0)
    self.assertEqual(MICI_LONGITUDINAL_INDEX["engine-braking"], 5)
    self.assertEqual(MICI_LONGITUDINAL_INDEX["overshoot"], 6)
    self.assertEqual(MICI_LONGITUDINAL_INDEX["overshoot-selector"], 6)
    self.assertIn("overshoot-selector", preview.SCENARIOS["mici"])

  def test_selector_opens_without_selecting_or_changing_params(self):
    values = dict(zip(READ_ONLY_KEYS, (False, 0), strict=True))
    params = SimpleNamespace(get=values.get)
    selector = SimpleNamespace(select=Mock())
    gui = SimpleNamespace(_nav_stack=[object()])
    control = SimpleNamespace(enabled=True, _click_callback=lambda: gui._nav_stack.append(selector))
    self.assertIs(open_read_only_selector(control, gui, params), selector)
    selector.select.assert_not_called()
    self.assertEqual(values, dict(zip(READ_ONLY_KEYS, (False, 0), strict=True)))
    control._click_callback = lambda: values.update(NrdrCruiseOverspeedAllowance=1)
    with self.assertRaisesRegex(AssertionError, "changed tuning params"):
      open_read_only_selector(control, gui, params)

  def test_focus_scrolls_actual_container_and_rejects_hidden_controls(self):
    item = SimpleNamespace(is_visible=True, rect=SimpleNamespace(x=800, y=600, width=200))
    panel = SimpleNamespace(_offset_filter_y=SimpleNamespace(x=-100), set_offset=Mock())
    scroller = SimpleNamespace(rect=SimpleNamespace(x=0, y=150, width=536), scroll_panel=panel, scroll_to=Mock())
    focus_item(scroller, item, horizontal=False)
    panel.set_offset.assert_called_once_with(-550)
    focus_item(scroller, item, horizontal=True)
    scroller.scroll_to.assert_called_once_with(632, smooth=False)
    item.is_visible = False
    with self.assertRaisesRegex(AssertionError, "hidden"):
      focus_item(scroller, item, horizontal=True)

  def test_expanded_plans_use_stock_script_and_stay_under_thirty_seconds(self):
    # Exercise scheduling with the actual stock Script classes, not a copied timer.
    # Import-only doubles avoid native dependencies; no widget rendering is claimed.
    source = ast.parse((preview.ROOT / "openpilot/selfdrive/ui/tests/diff/replay_script.py").read_text(encoding="utf-8"))
    classes = [node for node in source.body if isinstance(node, ast.ClassDef) and node.name in ("ScriptEvent", "Script")]
    module = ModuleType("preview_schedule_test_fixture")
    module.__dict__.update(dataclass=dataclass, TYPE_CHECKING=False, WAIT_SHORT=30, WAIT_LONG=60)
    tree = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), *classes], type_ignores=[])
    with patch.dict(sys.modules, {module.__name__: module}):
      exec(compile(ast.fix_missing_locations(tree), "stock_replay_script", "exec"), module.__dict__)

    for device in preview.DEVICES:
      gui = SimpleNamespace(width=preview.DEVICES[device][1], height=preview.DEVICES[device][2], big_ui=lambda device=device: device == "tici")
      state = SimpleNamespace(update_params=Mock(), CP=SimpleNamespace(brand="honda", carFingerprint="HONDA_CIVIC"),
                              params=SimpleNamespace(get=lambda key: None))
      nrdr = SimpleNamespace(_lateral_layout=object(), _longitudinal_layout=object())
      settings = SimpleNamespace(_panels={0: SimpleNamespace(instance=nrdr), 1: SimpleNamespace(instance=object())})
      main = SimpleNamespace(_onboarding_window=SimpleNamespace(completed=True), _layouts={1: settings}, _set_mode_for_state=Mock())
      imports = {
        "openpilot.cereal": {"log": object(), "messaging": object()},
        "openpilot.common.hardware": {"HARDWARE": SimpleNamespace(get_device_type=lambda device=device: device)},
        "openpilot.selfdrive.ui.tests.diff.replay": {"FPS": 60},
        "openpilot.selfdrive.ui.tests.diff.replay_script": {"Script": module.Script, "send_onroad": Mock()},
        "openpilot.selfdrive.ui.ui_state": {"ui_state": state},
        "openpilot.system.ui.lib.application": {"gui_app": gui},
        "openpilot.selfdrive.ui.layouts.main": {"MainState": SimpleNamespace(SETTINGS=1)},
        "openpilot.selfdrive.ui.layouts.settings.settings": {"PanelType": SimpleNamespace(NRDR=0, TOGGLES=1)},
        "openpilot.nrdr.ui.settings.layout": {"PanelType": object()},
        "openpilot.nrdr.ui.settings.lateral_tuning": {"LateralPanel": object()},
      }
      modules = {}
      for name, attributes in imports.items():
        modules[name] = ModuleType(name)
        modules[name].__dict__.update(attributes)
      markers = {"captures": {}}
      with patch.dict(sys.modules, modules):
        entries = build_preview_script(Mock(), main, "tizi" if device == "tici" else "mici", device, markers)
      names = [event.setup.__defaults__[0] for _, event in entries
               if event.setup is not None and "checkpoint" in getattr(event.setup, "__code__", SimpleNamespace(co_freevars=())).co_freevars]
      self.assertEqual(names, list(preview.SCENARIOS[device]))
      self.assertEqual(markers["end_frame"], 1398 if device == "tici" else 1276)
      self.assertLessEqual(entries[-1][0], 30 * 60)
      self.assertEqual([frame for frame, _ in entries], sorted(frame for frame, _ in entries))
      self.assertEqual(markers["unsupported"], preview.UNSUPPORTED[device])

  def test_capture_failure_is_nonzero_with_diagnostic_gallery(self):
    with tempfile.TemporaryDirectory() as folder:
      args = ["capture_preview.py", "--output", folder]
      with (patch.object(sys, "argv", args), patch.object(preview, "check_host"),
            # Linux platform probing can call subprocess.check_output too.
            patch.object(preview.platform, "platform", return_value="test-host"),
            patch.object(preview.subprocess, "check_output", side_effect=["abc\n", ""]),
            patch.object(preview, "run_bounded", side_effect=RuntimeError("native dependency missing")) as run):
        self.assertEqual(preview.main(), 1)
      self.assertEqual(run.call_count, 2)  # The other layout still gets attempted.
      report = json.loads((Path(folder) / "manifest.json").read_text())
      self.assertEqual(report["host"], "test-host")
      self.assertTrue(all(d["status"] == "failed" for d in report["devices"].values()))
      self.assertNotIn("<img ", (Path(folder) / "index.html").read_text(encoding="utf-8"))

  def test_existing_artifacts_are_not_overwritten(self):
    with tempfile.TemporaryDirectory() as folder:
      path = Path(folder) / "index.html"
      path.write_text("previous report")
      with (patch.object(sys, "argv", ["preview", "--output", folder]), patch.object(preview, "check_host"),
            patch.object(preview, "run_bounded") as run):
        self.assertEqual(preview.main(), 1)
      run.assert_not_called()
      self.assertEqual(path.read_text(), "previous report")

  def test_missing_checkpoints_cannot_be_marked_successful(self):
    markers = copy.deepcopy(checkpoints())
    markers["captures"] = {}
    with self.assertRaises(RuntimeError):
      preview.validate_markers(markers, "tici")

  def test_native_windows_is_rejected_before_native_imports(self):
    with patch.object(preview.platform, "system", return_value="Windows"):
      with self.assertRaisesRegex(RuntimeError, "Linux PC"):
        preview.check_host()

  def test_timeout_kills_the_whole_worker_group(self):
    with tempfile.TemporaryDirectory() as folder:
      with patch.object(preview.subprocess, "Popen") as popen, patch.object(preview.os, "killpg", create=True) as kill:
        proc = popen.return_value.__enter__.return_value
        proc.pid = 1234
        proc.wait.side_effect = [subprocess.TimeoutExpired("capture", 1), -9]
        # SIGKILL is absent on Windows, but the production path is Linux-only.
        with patch.object(preview.signal, "SIGKILL", 9, create=True):
          with self.assertRaises(subprocess.TimeoutExpired):
            preview.run_bounded(["capture"], env={}, log=Path(folder) / "capture.log", timeout=1)
        kill.assert_called_once_with(1234, 9)
        self.assertTrue(popen.call_args.kwargs["start_new_session"])


if __name__ == "__main__":
  unittest.main()
