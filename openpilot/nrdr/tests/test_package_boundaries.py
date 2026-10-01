import ast
from importlib import import_module
from pathlib import Path
import sys
from tokenize import open as open_python_source
import unittest

import openpilot.nrdr
from openpilot.nrdr.params import NrdrParamKey, ParamReader, ParamValue, read_bool, read_float


MIGRATED_PARAM_CONSUMERS = (
  "openpilot/nrdr/features/lateral/interpolated_torque_pif.py",
  "openpilot/nrdr/features/lateral/latcontrol_pid.py",
  "openpilot/nrdr/features/lateral/nnlc.py",
  "openpilot/nrdr/features/lateral/tune_learner.py",
  "openpilot/nrdr/features/longitudinal/longcontrol.py",
  "openpilot/nrdr/features/longitudinal/longitudinal_planner.py",
)

LATERAL_COMPATIBILITY_EXPORTS = {
  "honda_vgr": (
    "HONDA_VGR_PROFILES", "Q14", "RAW_UNITS_PER_DEGREE", "HondaVgrProfile",
    "get_honda_vgr_profile", "normalize_honda_eps_firmware",
  ),
  "lat_stiction": ("LatStiction", "LatStictionState"),
  "latcontrol_clarity_hybrid": (
    "BLEND_TO_NNLC_SECONDS", "BLEND_TO_PID_SECONDS", "NNLC_BLEND_HALF_WIDTH",
    "NNLC_DEFAULT_ACTIVATION_SPEED", "ClarityHybridExtension", "LatControlClarityHybrid",
    "clarity_nnlc_blend_target",
  ),
  "latcontrol_pid": (
    "CENTER_BOOST_SPEED_FADE", "CENTER_TAPER_FADE_TAU", "CIVIC_TEG_CENTER_BOOST_FADE_DEG",
    "LOW_SPEED_MAX", "MPH_TO_MS", "RATE_DAMPING_REFERENCE", "RATE_DAMPING_UNWIND_ANGLE",
    "STANDARD_SPEED_MAX", "NrdrLatControlPID",
  ),
  "nnlc": ("NrdrNnlc",),
  "nnlc_model": ("MODEL_PATHS", "get_forced_nnlc_model", "is_nnlc_forced"),
  "pid": ("FeedforwardPIDController",),
  "tune_learner": (
    "ANGLE_BIN_DEG", "ANGLE_MAX_DEG", "ERROR_GATE_FULL_DEG", "ERR_REJECT_DEG",
    "LEARN_MIN_SPEED_MS", "LEARN_RATE_REF", "MIN_ABS_DES", "MS_TO_MPH", "N_ANGLE",
    "N_SPEED", "RATE_GATE_DEG_S", "SAVE_FRAMES", "SPEED_BIN_MPH", "SPEED_MAX_MPH",
    "TRIM_HARD_FRAC", "TuneLearner",
  ),
}

PHASE_TWO_CONSUMERS = (
  "openpilot/selfdrive/car/card.py",
  "openpilot/nrdr/ui/settings/lateral_tuning.py",
  "openpilot/nrdr/ui/settings/override_tuning.py",
  "openpilot/nrdr/ui/settings/pidf_ground.py",
  "openpilot/nrdr/ui/settings/steer_filters.py",
  "openpilot/nrdr/ui/settings/vehicle_model_learning.py",
  "openpilot/nrdr/features/services/car_tune_report.py",
  "openpilot/nrdr/hooks/controlsd.py",
  "openpilot/nrdr/features/lateral/latcontrol_pid.py",
  "openpilot/nrdr/features/longitudinal/longcontrol.py",
  "openpilot/nrdr/features/longitudinal/longitudinal_planner.py",
  "openpilot/nrdr/features/lateral/nnlc.py",
  "openpilot/nrdr/ui/settings_policy.py",
  "openpilot/nrdr/features/lateral/tune_learner.py",
  "openpilot/sunnypilot/sunnylink/capabilities.py",
  "openpilot/system/manager/manager.py",
)

FEATURE_CONSUMERS = {
  "openpilot/selfdrive/car/cruise.py": "openpilot.nrdr.features.driver_policy.cruise",
  "openpilot/selfdrive/controls/lib/longcontrol.py": "openpilot.nrdr.features.longitudinal.longcontrol",
  "openpilot/selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc.py": "openpilot.nrdr.features.longitudinal.longitudinal_mpc",
  "openpilot/selfdrive/controls/lib/longitudinal_planner.py": "openpilot.nrdr.features.longitudinal.longitudinal_planner",
  "openpilot/selfdrive/controls/radard.py": "openpilot.nrdr.features.radar.radar",
  "openpilot/selfdrive/ui/sunnypilot/onroad/speed_limit.py": "openpilot.nrdr.features.driver_policy.speed_limit",
  "openpilot/nrdr/hooks/selfdrived.py": "openpilot.nrdr.features.driver_policy.hud_submode",
  "openpilot/sunnypilot/selfdrive/car/cruise_ext.py": "openpilot.nrdr.features.driver_policy.speed_limit",
  "openpilot/sunnypilot/selfdrive/controls/lib/dec/dec.py": "openpilot.nrdr.features.driver_policy.dec",
  "openpilot/sunnypilot/selfdrive/controls/lib/longitudinal_planner.py": "openpilot.nrdr.features.driver_policy.speed_limit_assist",
  "openpilot/sunnypilot/selfdrive/controls/lib/speed_limit/speed_limit_resolver.py": "openpilot.nrdr.features.driver_policy.speed_limit",
}

CANONICAL_FEATURE_MODULES = (
  "openpilot/nrdr/features/driver_policy/cruise.py",
  "openpilot/nrdr/features/driver_policy/dec.py",
  "openpilot/nrdr/features/driver_policy/hud_submode.py",
  "openpilot/nrdr/features/driver_policy/lane_change.py",
  "openpilot/nrdr/features/driver_policy/mads.py",
  "openpilot/nrdr/features/driver_policy/speed_limit.py",
  "openpilot/nrdr/features/driver_policy/speed_limit_assist.py",
  "openpilot/nrdr/features/longitudinal/long_tune.py",
  "openpilot/nrdr/features/longitudinal/longcontrol.py",
  "openpilot/nrdr/features/longitudinal/longitudinal_mpc.py",
  "openpilot/nrdr/features/longitudinal/longitudinal_planner.py",
  "openpilot/nrdr/features/longitudinal/longitudinal_stopping.py",
  "openpilot/nrdr/features/radar/radar.py",
  "openpilot/nrdr/features/radar/radar_core.py",
)

HOOK_AND_UI_CONSUMERS = {
  "openpilot/selfdrive/car/car_events.py": ("openpilot.nrdr.hooks",),
  "openpilot/selfdrive/controls/controlsd.py": ("openpilot.nrdr.hooks",),
  "openpilot/selfdrive/controls/lib/desire_helper.py": ("openpilot.nrdr.features.driver_policy",),
  "openpilot/selfdrive/controls/lib/latcontrol_torque.py": ("openpilot.nrdr.features.driver_policy",),
  "openpilot/selfdrive/monitoring/policy.py": ("openpilot.nrdr.hooks",),
  "openpilot/selfdrive/selfdrived/selfdrived.py": ("openpilot.nrdr.hooks",),
  "openpilot/selfdrive/ui/sunnypilot/layouts/settings/cruise.py": ("openpilot.nrdr.ui",),
  "openpilot/selfdrive/ui/sunnypilot/layouts/settings/cruise_sub_layouts/speed_limit_settings.py": ("openpilot.nrdr.ui",),
  "openpilot/selfdrive/ui/sunnypilot/layouts/settings/models.py": ("openpilot.nrdr.ui",),
  "openpilot/selfdrive/ui/sunnypilot/layouts/settings/steering.py": ("openpilot.nrdr.ui",),
  "openpilot/selfdrive/ui/sunnypilot/layouts/settings/visuals.py": ("openpilot.nrdr.ui",),
  "openpilot/selfdrive/ui/sunnypilot/ui_state.py": ("openpilot.nrdr.ui",),
  "openpilot/sunnypilot/mads/mads.py": ("openpilot.nrdr.features.driver_policy", "openpilot.nrdr.hooks"),
  "openpilot/sunnypilot/mads/state.py": ("openpilot.nrdr.hooks",),
  "openpilot/sunnypilot/selfdrive/controls/controlsd_ext.py": ("openpilot.nrdr.hooks",),
  "openpilot/sunnypilot/selfdrive/selfdrived/events.py": ("openpilot.nrdr.hooks",),
}

CANONICAL_HOOK_AND_UI_MODULES = (
  "openpilot/nrdr/hooks/controlsd.py",
  "openpilot/nrdr/hooks/driver_monitoring.py",
  "openpilot/nrdr/hooks/events.py",
  "openpilot/nrdr/hooks/events_sp.py",
  "openpilot/nrdr/hooks/selfdrived.py",
  "openpilot/nrdr/ui/settings_policy.py",
)


class TestPackageBoundaries(unittest.TestCase):
  def test_package_is_first_class_under_openpilot(self):
    package_path = Path(openpilot.nrdr.__file__).resolve().parent
    self.assertEqual(package_path.name, "nrdr")
    self.assertEqual(package_path.parent.name, "openpilot")
    self.assertIsNotNone(import_module("openpilot.nrdr.car"))
    self.assertIsNotNone(import_module("openpilot.nrdr.features"))
    self.assertIsNotNone(import_module("openpilot.nrdr.features.driver_policy"))
    self.assertIsNotNone(import_module("openpilot.nrdr.features.lateral"))
    self.assertIsNotNone(import_module("openpilot.nrdr.features.longitudinal"))
    self.assertIsNotNone(import_module("openpilot.nrdr.features.radar"))
    self.assertIsNotNone(import_module("openpilot.nrdr.hooks"))
    self.assertIsNotNone(import_module("openpilot.nrdr.tools"))
    self.assertIsNotNone(import_module("openpilot.nrdr.ui"))

  def test_legacy_parameter_module_forwards_public_objects(self):
    legacy = import_module("openpilot.sunnypilot.nrdr.params")
    self.assertIs(legacy.NrdrParamKey, NrdrParamKey)
    self.assertIs(legacy.ParamReader, ParamReader)
    self.assertIs(legacy.ParamValue, ParamValue)
    self.assertIs(legacy.read_bool, read_bool)
    self.assertIs(legacy.read_float, read_float)
    self.assertEqual(legacy.__all__, ("NrdrParamKey", "ParamReader", "ParamValue", "read_bool", "read_float"))

  def test_first_consumers_use_public_parameter_api(self):
    repository_root = Path(__file__).resolve().parents[3]
    for relative_path in MIGRATED_PARAM_CONSUMERS:
      with self.subTest(path=relative_path):
        source = (repository_root / relative_path).read_text()
        self.assertIn("from openpilot.nrdr.params import", source)
        self.assertNotIn("from openpilot.sunnypilot.nrdr.params import", source)

  def test_migrated_readers_do_not_use_static_string_keys(self):
    repository_root = Path(__file__).resolve().parents[3]
    failures: list[str] = []
    for relative_path in MIGRATED_PARAM_CONSUMERS:
      tree = ast.parse((repository_root / relative_path).read_text(), filename=relative_path)
      for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
          continue
        if node.func.id not in ("read_bool", "read_float") or len(node.args) < 2:
          continue
        key = node.args[1]
        if isinstance(key, ast.Constant) and isinstance(key.value, str):
          failures.append(f"{relative_path}:{node.lineno}: {key.value}")
    self.assertEqual(failures, [], "static parameter keys must use NrdrParamKey")

  def test_phase_two_consumers_use_the_public_facade(self):
    repository_root = Path(__file__).resolve().parents[3]
    forbidden = (
      "from openpilot.nrdr.params.defaults import",
      "from openpilot.nrdr.params.profiles import",
      "from openpilot.nrdr.params.snapshots import",
      "from openpilot.sunnypilot.nrdr.handcrafted_lateral import",
      "from openpilot.sunnypilot.nrdr.live_params import",
      "from openpilot.sunnypilot.nrdr.manager import",
    )
    for relative_path in PHASE_TWO_CONSUMERS:
      with self.subTest(path=relative_path):
        source = (repository_root / relative_path).read_text()
        self.assertIn("from openpilot.nrdr.params import", source)
        self.assertFalse(any(import_line in source for import_line in forbidden))

  def test_public_parameter_exports_are_lazy_and_complete(self):
    params_package = import_module("openpilot.nrdr.params")
    self.assertEqual(set(params_package.__all__), set(params_package._EXPORT_MODULES))
    self.assertEqual(len(params_package.__all__), len(set(params_package.__all__)))

  def test_feature_package_exports_are_lazy_and_complete(self):
    for module_name in (
      "openpilot.nrdr.features.driver_policy",
      "openpilot.nrdr.features.longitudinal",
      "openpilot.nrdr.features.radar",
    ):
      with self.subTest(module=module_name):
        feature_package = import_module(module_name)
        self.assertEqual(set(feature_package.__all__), set(feature_package._EXPORT_MODULES))
        self.assertEqual(len(feature_package.__all__), len(set(feature_package.__all__)))

  def test_hook_and_ui_package_exports_are_lazy_and_complete(self):
    for module_name in ("openpilot.nrdr.hooks", "openpilot.nrdr.ui"):
      with self.subTest(module=module_name):
        package = import_module(module_name)
        self.assertEqual(set(package.__all__), set(package._EXPORT_MODULES))
        self.assertEqual(len(package.__all__), len(set(package.__all__)))

  def test_feature_implementations_do_not_import_legacy_nrdr_modules(self):
    repository_root = Path(__file__).resolve().parents[3]
    for relative_path in CANONICAL_FEATURE_MODULES:
      with self.subTest(path=relative_path):
        source = (repository_root / relative_path).read_text()
        self.assertNotIn("openpilot.sunnypilot.nrdr", source)

  def test_production_consumers_import_canonical_feature_owners(self):
    repository_root = Path(__file__).resolve().parents[3]
    for relative_path, module_name in FEATURE_CONSUMERS.items():
      with self.subTest(path=relative_path):
        source = (repository_root / relative_path).read_text()
        self.assertIn(f"from {module_name} import", source)
        self.assertNotIn("from openpilot.sunnypilot.nrdr.", source)

  def test_hook_and_ui_implementations_do_not_import_legacy_nrdr_modules(self):
    repository_root = Path(__file__).resolve().parents[3]
    for relative_path in CANONICAL_HOOK_AND_UI_MODULES:
      with self.subTest(path=relative_path):
        source = (repository_root / relative_path).read_text()
        self.assertNotIn("openpilot.sunnypilot.nrdr", source)

  def test_framework_consumers_use_canonical_hook_and_policy_facades(self):
    repository_root = Path(__file__).resolve().parents[3]
    for relative_path, module_names in HOOK_AND_UI_CONSUMERS.items():
      with self.subTest(path=relative_path):
        source = (repository_root / relative_path).read_text()
        for module_name in module_names:
          self.assertIn(f"from {module_name} import", source)
        self.assertNotIn("from openpilot.sunnypilot.nrdr.", source)

  def test_legacy_namespace_contains_no_production_implementations(self):
    repository_root = Path(__file__).resolve().parents[3]
    legacy_dir = repository_root / "openpilot" / "sunnypilot" / "nrdr"
    for path in legacy_dir.glob("*.py"):
      if path.name == "__init__.py" or path.name.startswith("test_"):
        continue
      with self.subTest(path=path.name):
        tree = ast.parse(path.read_text(), filename=path.name)
        definitions = [
          node for node in tree.body
          if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        self.assertEqual(definitions, [])

  def test_production_code_never_imports_the_legacy_namespace(self):
    repository_root = Path(__file__).resolve().parents[3]
    legacy_dir = repository_root / "openpilot" / "sunnypilot" / "nrdr"
    offenders: list[str] = []
    for path in (repository_root / "openpilot").rglob("*.py"):
      if path.is_relative_to(legacy_dir) or path.name.startswith("test_") or {"test", "tests"} & set(path.parts):
        continue
      with open_python_source(path) as source_file:
        source = source_file.read()
      if "openpilot.sunnypilot.nrdr" in source:
        offenders.append(str(path.relative_to(repository_root)))
    self.assertEqual(offenders, [])

  def test_ui_metadata_keeps_params_dependency_direction(self):
    params_dir = Path(__file__).resolve().parent.parent / "params"
    tree = ast.parse((params_dir / "ui_metadata.py").read_text(), filename="ui_metadata.py")
    forbidden_prefixes = (
      "openpilot.common",
      "openpilot.nrdr.features",
      "openpilot.nrdr.hooks",
      "openpilot.nrdr.ui",
      "openpilot.selfdrive",
      "openpilot.system.ui",
      "openpilot.sunnypilot",
    )
    imported: list[str] = []
    for node in ast.walk(tree):
      if isinstance(node, ast.Import):
        imported.extend(alias.name for alias in node.names)
      elif isinstance(node, ast.ImportFrom) and node.module is not None:
        imported.append(node.module)
    self.assertFalse(any(name.startswith(forbidden_prefixes) for name in imported), imported)

  def test_legacy_steer_ratio_analysis_preserves_all_public_object_identities(self):
    canonical = import_module("openpilot.nrdr.tools.sr_correction_analysis")
    legacy = import_module("openpilot.sunnypilot.nrdr.sr_correction_analysis")
    canonical_path = Path(canonical.__file__).resolve()
    tree = ast.parse(canonical_path.read_text(), filename=canonical_path.name)
    module_defined: set[str] = set()
    for node in tree.body:
      if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
        if not node.name.startswith("_"):
          module_defined.add(node.name)
      elif isinstance(node, ast.Assign):
        for target in node.targets:
          if isinstance(target, ast.Name) and not target.id.startswith("_"):
            module_defined.add(target.id)
      elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and not node.target.id.startswith("_"):
        module_defined.add(node.target.id)

    self.assertIn("T", module_defined)
    self.assertEqual(set(legacy.__all__), module_defined)
    self.assertEqual(len(legacy.__all__), len(module_defined))
    for name in legacy.__all__:
      with self.subTest(name=name):
        self.assertIs(getattr(legacy, name), getattr(canonical, name))

  def test_canonical_steer_ratio_cli_imports_the_canonical_analysis_module(self):
    repository_root = Path(__file__).resolve().parents[3]
    source = (repository_root / "openpilot/nrdr/tools/steer_ratio/correction.py").read_text()
    self.assertIn("from openpilot.nrdr.tools.sr_correction_analysis import", source)
    self.assertNotIn("from openpilot.sunnypilot.nrdr.sr_correction_analysis import", source)

  def test_legacy_phase_detector_preserves_public_object_identities(self):
    canonical = import_module("openpilot.nrdr.features.lateral.phase_detector")
    legacy = import_module("openpilot.sunnypilot.nrdr.phase_detector")
    self.assertEqual(legacy.__all__, ("PHASE_SWITCH_MIN_SPEED", "phase_with_latch"))
    for name in legacy.__all__:
      with self.subTest(name=name):
        self.assertIs(getattr(legacy, name), getattr(canonical, name))

  def test_canonical_latcontrol_pid_uses_canonical_lateral_dependencies(self):
    repository_root = Path(__file__).resolve().parents[3]
    source = (repository_root / "openpilot/nrdr/features/lateral/latcontrol_pid.py").read_text()
    self.assertIn("from openpilot.nrdr.features.lateral.phase_detector import phase_with_latch", source)
    for module in ("honda_vgr", "lat_stiction", "phase_detector", "tune_learner"):
      with self.subTest(module=module):
        self.assertIn(f"from openpilot.nrdr.features.lateral.{module} import", source)
        self.assertNotIn(f"from openpilot.sunnypilot.nrdr.{module} import", source)

  def test_lateral_compatibility_modules_are_explicit_forwarders(self):
    repository_root = Path(__file__).resolve().parents[3]
    legacy_dir = repository_root / "openpilot" / "sunnypilot" / "nrdr"
    for module_name, expected_exports in LATERAL_COMPATIBILITY_EXPORTS.items():
      with self.subTest(module=module_name):
        tree = ast.parse((legacy_dir / f"{module_name}.py").read_text(), filename=module_name)
        import_nodes = [node for node in tree.body if isinstance(node, ast.ImportFrom)]
        self.assertEqual(len(import_nodes), 1)
        self.assertEqual(import_nodes[0].module, f"openpilot.nrdr.features.lateral.{module_name}")
        self.assertEqual(tuple(alias.name for alias in import_nodes[0].names), expected_exports)
        assignments = [node for node in tree.body if isinstance(node, ast.Assign)]
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0].targets[0].id, "__all__")
        self.assertEqual(ast.literal_eval(assignments[0].value), expected_exports)
        implementation_nodes = [
          node for node in tree.body
          if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        self.assertEqual(implementation_nodes, [])

  def test_portable_lateral_forwarders_preserve_object_identities(self):
    for module_name in ("honda_vgr", "lat_stiction", "pid"):
      with self.subTest(module=module_name):
        canonical = import_module(f"openpilot.nrdr.features.lateral.{module_name}")
        legacy = import_module(f"openpilot.sunnypilot.nrdr.{module_name}")
        self.assertEqual(legacy.__all__, canonical.__all__)
        for name in canonical.__all__:
          self.assertIs(getattr(legacy, name), getattr(canonical, name))

  @unittest.skipIf(sys.platform == "win32", "full controller imports require openpilot's Linux runtime")
  def test_runtime_lateral_forwarders_preserve_object_identities(self):
    for module_name in LATERAL_COMPATIBILITY_EXPORTS:
      with self.subTest(module=module_name):
        canonical = import_module(f"openpilot.nrdr.features.lateral.{module_name}")
        legacy = import_module(f"openpilot.sunnypilot.nrdr.{module_name}")
        self.assertEqual(legacy.__all__, canonical.__all__)
        for name in canonical.__all__:
          self.assertIs(getattr(legacy, name), getattr(canonical, name))

  def test_legacy_model_policy_preserves_all_public_object_identities(self):
    canonical = import_module("openpilot.nrdr.features.lateral.model_policy")
    legacy = import_module("openpilot.sunnypilot.nrdr.model_policy")
    self.assertEqual(legacy.__all__, canonical.__all__)
    for name in canonical.__all__:
      with self.subTest(name=name):
        self.assertIs(getattr(legacy, name), getattr(canonical, name))

  def test_legacy_steer_ratio_tuning_preserves_all_public_object_identities(self):
    canonical = import_module("openpilot.nrdr.features.lateral.steer_ratio_tuning")
    legacy = import_module("openpilot.sunnypilot.nrdr.steer_ratio_tuning")
    self.assertEqual(legacy.__all__, canonical.__all__)
    for name in canonical.__all__:
      with self.subTest(name=name):
        self.assertIs(getattr(legacy, name), getattr(canonical, name))

  def test_steer_ratio_policy_consumers_use_canonical_feature_modules(self):
    repository_root = Path(__file__).resolve().parents[3]
    consumers = (
      "openpilot/nrdr/tools/lateral/attribution.py",
      "openpilot/nrdr/ui/settings/pidf_ground.py",
      "openpilot/nrdr/features/services/car_tune_report.py",
      "openpilot/nrdr/features/lateral/latcontrol_pid.py",
      "openpilot/sunnypilot/sunnylink/capabilities.py",
    )
    for relative_path in consumers:
      with self.subTest(path=relative_path):
        source = (repository_root / relative_path).read_text()
        self.assertIn("from openpilot.nrdr.features.lateral.model_policy import", source)
        self.assertNotIn("from openpilot.sunnypilot.nrdr.model_policy import", source)

    controller = (repository_root / "openpilot/nrdr/features/lateral/latcontrol_pid.py").read_text()
    self.assertIn("from openpilot.nrdr.features.lateral.steer_ratio_tuning import", controller)
    self.assertNotIn("from openpilot.sunnypilot.nrdr.steer_ratio_tuning import", controller)
