import ast
import json
from pathlib import Path
import re
import unittest

import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
PARAM_HEADER = REPOSITORY_ROOT / "openpilot/common/params_keys.h"
PARAM_INCLUDE = REPOSITORY_ROOT / "openpilot/nrdr/params/generated/params_keys.inc"
TICI_PANEL = REPOSITORY_ROOT / "openpilot/selfdrive/ui/sunnypilot/layouts/settings/lane_centering.py"
MICI_PANEL = REPOSITORY_ROOT / "openpilot/selfdrive/ui/mici/layouts/settings/lane_centering.py"
SUNNYLINK_ROOT = REPOSITORY_ROOT / "openpilot/sunnypilot/sunnylink"
NRDR_STEERING = REPOSITORY_ROOT / "openpilot/nrdr/ui/sunnylink/pages/steering.yaml"
CUSTOM_SCHEMA = REPOSITORY_ROOT / "openpilot/cereal/custom.capnp"
LOG_SCHEMA = REPOSITORY_ROOT / "openpilot/cereal/log.capnp"
SERVICES = REPOSITORY_ROOT / "openpilot/cereal/services.py"
CARD = REPOSITORY_ROOT / "openpilot/selfdrive/car/card.py"
DEVELOPER_ELEMENTS = REPOSITORY_ROOT / "openpilot/selfdrive/ui/sunnypilot/onroad/developer_ui/elements.py"
STATUS_HELPER = REPOSITORY_ROOT / "openpilot/selfdrive/ui/sunnypilot/onroad/lane_centering_status.py"
UI_STATE_SP = REPOSITORY_ROOT / "openpilot/selfdrive/ui/sunnypilot/ui_state.py"

LANE_CENTERING_KEYS = (
  "LaneCentering",
  "LaneCenteringMinSpeed",
  "LaneCenteringPauseOnSignal",
  "LaneCenterOffset",
  "LaneCenteringStrength",
  "LaneCenteringE2EAuthority",
)


def _collect_keys(node, found: list[str]) -> None:
  if isinstance(node, dict):
    if isinstance(node.get("key"), str):
      found.append(node["key"])
    for name, value in node.items():
      if name not in ("visibility", "enablement", "options"):
        _collect_keys(value, found)
  elif isinstance(node, list):
    for value in node:
      _collect_keys(value, found)


class TestLaneCenteringStack(unittest.TestCase):
  def test_existing_defaults_remain_exact(self) -> None:
    source = PARAM_HEADER.read_text(encoding="utf-8")
    expected = {
      "LaneCentering": 'PERSISTENT | BACKUP, BOOL, "0"',
      "LaneCenteringE2EAuthority": 'PERSISTENT | BACKUP, FLOAT, "1.0"',
      "LaneCenteringPauseOnSignal": 'PERSISTENT | BACKUP, BOOL, "1"',
      "LaneCenterOffset": 'PERSISTENT | BACKUP, FLOAT, "0.0"',
    }
    for key, attributes in expected.items():
      with self.subTest(key=key):
        self.assertEqual(len(re.findall(rf'\{{"{key}", \{{{re.escape(attributes)}\}}\}}', source)), 1)
    generated = PARAM_INCLUDE.read_text(encoding="utf-8")
    self.assertNotIn('"LaneCenteringMinSpeed"', source)
    self.assertEqual(generated.count('{"LaneCenteringMinSpeed", {PERSISTENT | BACKUP, INT, "50"}}'), 1)
    self.assertEqual(generated.count('{"LaneCenteringStrength", {PERSISTENT | BACKUP, FLOAT, "0.30"}}'), 1)

  def test_controls_are_rehomed_out_of_developer_pages(self) -> None:
    developer_sources = (
      REPOSITORY_ROOT / "openpilot/selfdrive/ui/sunnypilot/layouts/settings/developer.py",
      REPOSITORY_ROOT / "openpilot/selfdrive/ui/mici/layouts/settings/developer.py",
    )
    for path in developer_sources:
      with self.subTest(path=path):
        source = path.read_text(encoding="utf-8")
        self.assertFalse(any(key in source for key in LANE_CENTERING_KEYS))

    for path in (TICI_PANEL, MICI_PANEL):
      with self.subTest(path=path):
        source = path.read_text(encoding="utf-8")
        for key in LANE_CENTERING_KEYS:
          self.assertIn(key, source)

    tici_settings = (REPOSITORY_ROOT / "openpilot/selfdrive/ui/sunnypilot/layouts/settings/settings.py").read_text(encoding="utf-8")
    nrdr_lateral = (REPOSITORY_ROOT / "openpilot/nrdr/ui/settings/lateral_tuning.py").read_text(encoding="utf-8")
    mici_settings = (REPOSITORY_ROOT / "openpilot/selfdrive/ui/mici/layouts/settings/settings.py").read_text(encoding="utf-8")
    mici_toggles = (REPOSITORY_ROOT / "openpilot/selfdrive/ui/mici/layouts/settings/toggles.py").read_text(encoding="utf-8")
    self.assertNotIn("LaneCenteringLayout()", tici_settings)
    self.assertIn("LaneCenteringLayout()", nrdr_lateral)
    self.assertNotIn("LaneCenteringLayoutMici()", mici_settings)
    self.assertIn("LaneCenteringLayoutMici()", mici_toggles)

  def test_local_write_callbacks_require_offroad_and_not_engaged(self) -> None:
    tici = TICI_PANEL.read_text(encoding="utf-8")
    mici = MICI_PANEL.read_text(encoding="utf-8")
    self.assertIn("if self._write_allowed():", tici)
    self.assertIn("return ui_state.is_offroad() and not ui_state.engaged", tici)
    self.assertEqual(tici.count("if not self._write_allowed():"), 1)
    self.assertEqual(tici.count("if not self._settings_writable():"), 1)
    self.assertIn("return ui_state.is_offroad() and not ui_state.engaged", mici)
    self.assertEqual(mici.count("if not self._write_allowed():"), 1)
    self.assertEqual(mici.count("if not self._settings_writable():"), 5)
    self.assertNotIn('param="LaneCentering"', tici)

  def test_sunnylink_stack_is_nested_under_nrdr_lateral_tuning(self) -> None:
    self.assertFalse((SUNNYLINK_ROOT / "settings_ui_src/pages/lane_centering.yaml").exists())
    source_extension = yaml.safe_load(NRDR_STEERING.read_text(encoding="utf-8"))
    source_developer = yaml.safe_load((SUNNYLINK_ROOT / "settings_ui_src/pages/developer.yaml").read_text(encoding="utf-8"))
    compiled = json.loads((SUNNYLINK_ROOT / "settings_ui.json").read_text(encoding="utf-8"))

    nrdr_section = next(section for section in source_extension["sections"] if section["id"] == "nrdr")
    self.assertEqual(nrdr_section["title"], "nrdr Lateral Tuning")
    source_panels = [panel for panel in nrdr_section["sub_panels"] if panel["id"] == "nrdr_lane_centering_stack"]
    self.assertEqual(len(source_panels), 1)
    source_panel = source_panels[0]
    self.assertEqual(source_panel["label"], "Lane Centering Stack")
    self.assertIsNone(source_panel["trigger_key"])

    source_keys: list[str] = []
    developer_keys: list[str] = []
    _collect_keys(source_panel, source_keys)
    _collect_keys(source_developer, developer_keys)
    self.assertEqual(tuple(source_keys), LANE_CENTERING_KEYS)
    self.assertFalse(set(LANE_CENTERING_KEYS) & set(developer_keys))

    sibling_ids = [panel["id"] for panel in nrdr_section["sub_panels"]]
    self.assertLess(sibling_ids.index("nrdr_pidf_ground"), sibling_ids.index("nrdr_lane_centering_stack"))
    self.assertLess(sibling_ids.index("nrdr_lane_centering_stack"), sibling_ids.index("nrdr_steer_filters"))

    items = source_panel["items"]
    for item in items:
      with self.subTest(key=item["key"]):
        self.assertIn({"$ref": "#/macros/offroad"}, item["enablement"])
        self.assertIn({"$ref": "#/macros/not_engaged"}, item["enablement"])
    for item in items[1:]:
      self.assertIn({"type": "param", "key": "LaneCentering", "equals": True}, item["enablement"])

    minimum_speed = items[1]
    self.assertEqual(
      {field: minimum_speed[field] for field in ("min", "max", "step", "unit")},
      {"min": 12, "max": 100, "step": 1, "unit": "mph"},
    )
    self.assertIn("5 m/s controller floor", minimum_speed["description"])
    self.assertIn("two confident boundaries", items[0]["details"])
    self.assertIn("When the paths agree, it requests no correction", items[0]["details"])
    self.assertIn("matching model timing", items[0]["details"])
    self.assertIn("not road-validated", items[0]["description"])
    self.assertEqual(items[2]["title"], "Fade on Turn Signal")
    self.assertIn("always suspend", items[2]["description"])
    self.assertIn("regardless of this setting", items[2]["description"])
    strength = items[4]
    self.assertEqual(strength["title"], "Lane-Centering Strength")
    self.assertEqual({field: strength[field] for field in ("min", "max", "step")}, {"min": 0.0, "max": 1.0, "step": 0.05})
    self.assertIn("0.30 is the default", strength["description"])
    self.assertIn("1.0 requests the lane-center path", strength["description"])
    self.assertIn("without raising the existing maximum correction ceiling", strength["description"])
    self.assertEqual(items[5]["title"], "Model Break-In")
    self.assertIn("more than 0.15 m", items[5]["description"])
    self.assertIn("zero by 0.50 m", items[5]["description"])
    lane_centering_copy = json.dumps(source_panel)
    self.assertNotIn("StarPilot", lane_centering_copy)
    self.assertNotIn("SPLC", lane_centering_copy)

    self.assertFalse(any(page["id"] == "lane_centering" for page in compiled["panels"]))
    compiled_steering = next(page for page in compiled["panels"] if page["id"] == "steering")
    compiled_nrdr = next(section for section in compiled_steering["sections"] if section["id"] == "nrdr")
    self.assertEqual(compiled_nrdr["title"], "nrdr Lateral Tuning")
    compiled_panels = [panel for panel in compiled_nrdr["sub_panels"] if panel["id"] == "nrdr_lane_centering_stack"]
    self.assertEqual(len(compiled_panels), 1)
    self.assertEqual(compiled_panels[0]["label"], "Lane Centering Stack")
    self.assertIsNone(compiled_panels[0]["trigger_key"])
    compiled_keys: list[str] = []
    _collect_keys(compiled_panels[0], compiled_keys)
    self.assertEqual(tuple(compiled_keys), LANE_CENTERING_KEYS)

    all_source_keys: list[str] = []
    for source_root in (SUNNYLINK_ROOT / "settings_ui_src", REPOSITORY_ROOT / "openpilot/nrdr/ui/sunnylink"):
      for path in source_root.rglob("*.yaml"):
        _collect_keys(yaml.safe_load(path.read_text(encoding="utf-8")), all_source_keys)
    all_compiled_keys: list[str] = []
    _collect_keys(compiled, all_compiled_keys)
    for key in LANE_CENTERING_KEYS:
      with self.subTest(unique_key=key):
        self.assertEqual(all_source_keys.count(key), 1)
        self.assertEqual(all_compiled_keys.count(key), 1)

  def test_control_path_reads_canonical_mph_setting_once_per_snapshot(self) -> None:
    controlsd = (REPOSITORY_ROOT / "openpilot/selfdrive/controls/controlsd.py").read_text(encoding="utf-8")
    extension = (REPOSITORY_ROOT / "openpilot/sunnypilot/selfdrive/controls/controlsd_ext.py").read_text(encoding="utf-8")
    self.assertEqual(extension.count('self.params.get("LaneCenteringMinSpeed", return_default=True)'), 1)
    self.assertEqual(extension.count('self.params.get("LaneCenteringStrength", return_default=True)'), 1)
    self.assertEqual(controlsd.count("self.lane_centering_min_speed_mph"), 1)
    self.assertEqual(controlsd.count("self.lane_centering_strength"), 1)
    tici = TICI_PANEL.read_text(encoding="utf-8")
    mici = MICI_PANEL.read_text(encoding="utf-8")
    self.assertIn("value_normalizer=lane_centering_min_speed_mph", tici)
    self.assertIn("lane_centering_min_speed_mph(ui_state.params.get", mici)

  def test_migration_is_restrictive_and_does_not_enable_lane_centering(self) -> None:
    source = PARAM_HEADER.read_text(encoding="utf-8")
    generated = PARAM_INCLUDE.read_text(encoding="utf-8")
    self.assertIn('{"LaneCentering", {PERSISTENT | BACKUP, BOOL, "0"}}', source)
    self.assertIn('{"LaneCenteringMinSpeed", {PERSISTENT | BACKUP, INT, "50"}}', generated)
    self.assertIn('{"LaneCenteringStrength", {PERSISTENT | BACKUP, FLOAT, "0.30"}}', generated)
    self.assertIn("Existing enabled installs adopt the new 50 mph minimum", NRDR_STEERING.read_text(encoding="utf-8"))

  def test_driver_override_is_wired_without_other_starpilot_controls(self) -> None:
    controlsd = (REPOSITORY_ROOT / "openpilot/selfdrive/controls/controlsd.py").read_text(encoding="utf-8")
    controller = (REPOSITORY_ROOT / "openpilot/selfdrive/controls/lib/lane_centering.py").read_text(encoding="utf-8")
    self.assertIn("bool(CS.steeringPressed), model_frame=self.sm.logMonoTime['modelV2']", controlsd)
    self.assertIn("CC.latActive and not self.sm.valid['lateralManeuverPlan']", controlsd)
    self.assertIn("if driver_override:", controller)
    for prohibited in ("left_only", "right_only", "visualizer", "turn_hold", "turn_lead", "lane_change_jerk"):
      self.assertNotIn(prohibited, controller)

  def test_observability_uses_reserved_low_rate_service_outside_card(self) -> None:
    schema = CUSTOM_SCHEMA.read_text(encoding="utf-8")
    log_schema = LOG_SCHEMA.read_text(encoding="utf-8")
    services = SERVICES.read_text(encoding="utf-8")
    controller = (REPOSITORY_ROOT / "openpilot/selfdrive/controls/lib/lane_centering.py").read_text(encoding="utf-8")
    controlsd = (REPOSITORY_ROOT / "openpilot/selfdrive/controls/controlsd.py").read_text(encoding="utf-8")
    extension = (REPOSITORY_ROOT / "openpilot/sunnypilot/selfdrive/controls/controlsd_ext.py").read_text(encoding="utf-8")
    card = CARD.read_text(encoding="utf-8")
    developer_elements = DEVELOPER_ELEMENTS.read_text(encoding="utf-8")
    status_helper = STATUS_HELPER.read_text(encoding="utf-8")
    ui_state = UI_STATE_SP.read_text(encoding="utf-8")

    self.assertIn("struct LaneCenteringStateSP @0xcb9fd56c7057593a", schema)
    self.assertNotIn("struct CustomReserved10 @0xcb9fd56c7057593a", schema)
    self.assertIn("laneCenteringStateSP @136 :Custom.LaneCenteringStateSP;", log_schema)
    self.assertNotIn("customReserved10 @136", log_schema)
    self.assertIn('"laneCenteringStateSP": (True, 10., 1)', services)

    car_control_block = re.search(r"struct CarControlSP .*?(?=struct BackupManagerSP)", schema, flags=re.DOTALL)
    self.assertIsNotNone(car_control_block)
    self.assertNotIn("LaneCentering", car_control_block.group())
    self.assertNotIn("laneCenteringStateSP", card)

    reason_block = re.search(r"enum Reason \{(?P<body>.*?)\n  \}", schema, flags=re.DOTALL)
    self.assertIsNotNone(reason_block)
    expected_reasons = (
      "unavailable @0;", "disabled @1;", "lateralInactive @2;", "invalidInput @3;", "modelInvalid @4;",
      "driverOverride @5;", "laneChange @6;", "belowSpeed @7;", "turnSignalFade @8;", "laneDataInvalid @9;",
      "laneConfidenceLow @10;", "laneGeometryInvalid @11;", "centered @12;", "modelAuthority @13;", "correcting @14;",
      "zeroStrength @15;",
    )
    for reason in expected_reasons:
      self.assertIn(reason, reason_block.group("body"))

    # New readers of old logs see ordinal zero, which must never claim active.
    self.assertTrue(reason_block.group("body").lstrip().startswith("unavailable @0;"))
    self.assertNotIn("diagnostics", controlsd)
    self.assertIn("source = self.lane_centering.diagnostics", extension)
    self.assertIn("LANE_CENTERING_STATE_PUBLISH_INTERVAL = 10", extension)
    self.assertIn("def publish_lane_centering_state", extension)
    self.assertLess(controlsd.index("self.publish(CC, lac_log)"), controlsd.index("self.run_ext(self.sm, self.pm)"))
    self.assertLess(extension.index("self.publish_ext(CC_SP, sm, pm)"),
                    extension.index("self.publish_lane_centering_state(self.lane_centering_state(), pm)"))
    self.assertIn("class LaneCenteringDiagnostics", controller)
    self.assertIn('"laneCenteringStateSP"', ui_state)
    self.assertIn("class LaneCenteringStatusElement", developer_elements)
    self.assertIn('getattr(reason, "raw", reason)', status_helper)
    self.assertIn('return UiElement(value, "LANE CTR", "", color)', developer_elements)
    status_source = developer_elements[developer_elements.index("class LaneCenteringStatusElement"):]
    self.assertNotIn("callback", status_source)

  def test_diagnostics_cannot_feed_control_branches_state_or_returns(self) -> None:
    controller = (REPOSITORY_ROOT / "openpilot/selfdrive/controls/lib/lane_centering.py").read_text(encoding="utf-8")
    tree = ast.parse(controller)

    for node in ast.walk(tree):
      if isinstance(node, ast.If):
        self.assertNotIn("diagnostics", ast.unparse(node.test))
      elif isinstance(node, ast.Return) and node.value is not None:
        self.assertNotIn("diagnostics", ast.unparse(node.value))
      elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        writes_control_state = any(
          isinstance(part, ast.Attribute) and part.attr in ("_correction", "_speed_armed")
          for target in targets for part in ast.walk(target)
        )
        if writes_control_state:
          self.assertNotIn("diagnostics", ast.unparse(node.value))

  def test_lane_centering_publish_cadence_and_order(self) -> None:
    extension = (REPOSITORY_ROOT / "openpilot/sunnypilot/selfdrive/controls/controlsd_ext.py").read_text(encoding="utf-8")
    tree = ast.parse(extension)
    controls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "ControlsExt")
    run_ext = next(node for node in controls.body if isinstance(node, ast.FunctionDef) and node.name == "run_ext")

    # Execute the exact production method body in a dependency-free harness so
    # this cadence regression also runs on hosts without the native msgq build.
    for argument in (*run_ext.args.posonlyargs, *run_ext.args.args, *run_ext.args.kwonlyargs):
      argument.annotation = None
    run_ext.returns = None
    harness = ast.ClassDef(
      name="Harness",
      bases=[],
      keywords=[],
      body=[run_ext],
      decorator_list=[],
    )
    module = ast.fix_missing_locations(ast.Module(
      body=[
        ast.Assign(
          targets=[ast.Name(id="LANE_CENTERING_STATE_PUBLISH_INTERVAL", ctx=ast.Store())],
          value=ast.Constant(value=10),
        ),
        harness,
      ],
      type_ignores=[],
    ))
    namespace = {}
    exec(compile(module, "controlsd_ext_run_ext", "exec"), namespace)

    instance = namespace["Harness"]()
    instance._lane_centering_state_publish_frame = 0
    events = []
    current_cycle = [0]
    instance.state_control_ext = lambda sm: "car-control"
    instance.publish_ext = lambda cc, sm, pm: events.append((current_cycle[0], "carControlSP"))
    instance.lane_centering_state = lambda: "lane-centering"
    instance.publish_lane_centering_state = lambda state, pm: events.append((current_cycle[0], "laneCenteringStateSP"))

    for cycle in range(21):
      current_cycle[0] = cycle
      instance.run_ext(None, None)

    self.assertEqual([cycle for cycle, service in events if service == "carControlSP"], list(range(21)))
    self.assertEqual([cycle for cycle, service in events if service == "laneCenteringStateSP"], [0, 10, 20])
    for cycle in (0, 10, 20):
      self.assertLess(events.index((cycle, "carControlSP")), events.index((cycle, "laneCenteringStateSP")))


if __name__ == "__main__":
  unittest.main()
