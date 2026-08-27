import ast
from importlib import import_module
from pathlib import Path

import pytest


LEGACY_FEATURE_EXPORTS = {
  "cruise": (
    "openpilot.nrdr.features.driver_policy.cruise",
    ("ButtonType", "NrdrCruise"),
  ),
  "dec": (
    "openpilot.nrdr.features.driver_policy.dec",
    ("enforce_mode_dwell", "slow_down_threshold"),
  ),
  "hud_submode": (
    "openpilot.nrdr.features.driver_policy.hud_submode",
    ("SUBMODE_WINDOW_DEFAULT_S", "SUBMODE_WINDOW_MAX_S", "SUBMODE_WINDOW_MIN_S", "consume_button_press"),
  ),
  "long_tune": (
    "openpilot.nrdr.features.longitudinal.long_tune",
    (
      "CRUISE_SCALE_COUNT", "CRUISE_SCALE_RANGE", "DEFAULT_CRUISE_SCALE", "FOLLOW_OFFSET_RANGE",
      "JERK_FACTOR_KEYS", "JERK_FACTOR_RANGE", "LEAD_FIELDS", "LOW_SPEED_JERK_BP", "NRDR_LONG_TUNE_PATH",
      "PERSONALITIES", "SCALAR_FIELDS", "STOPPING_FIELDS", "LongTune", "main", "write_tune",
    ),
  ),
  "longcontrol": (
    "openpilot.nrdr.features.longitudinal.longcontrol",
    (
      "DREL_FILTER_ALPHA", "DREL_FILTER_FRAMES", "LONG_PID_SCALE_DEFAULTS", "LONG_PID_SCALE_EPSILON",
      "LONG_PID_SCALE_KEYS", "LONG_PID_SCALE_SLEW_PER_SECOND", "ROEN_ACCEL_BP", "ROEN_NIDEC_ACCEL_MAX",
      "LongCtrlState", "NrdrLongControl", "effective_long_pid_scale", "longitudinal_pid_gains", "scaled_pid_limits",
    ),
  ),
  "longitudinal_mpc": (
    "openpilot.nrdr.features.longitudinal.longitudinal_mpc",
    (
      "BRAKE_ENGAGE_DELAY", "BRAKE_PERSISTENCE", "BRAKE_RELEASE_TIME", "CROSSFADE_FRAMES", "CRUISE_MAX_ACCEL",
      "LEAD_ACCEL_FILTER_TAU", "LEAD_ACCEL_TAU_MAX", "LEAD_ACCEL_TAU_NORMALIZER", "MAX_EFFECTIVE_BRAKE",
      "MIN_TRACK_AGE", "PERSONALITY_JERK", "PERSONALITY_NAMES", "PERSONALITY_T_FOLLOW", "MpcPolicyResult",
      "NrdrLongitudinalMpc",
    ),
  ),
  "longitudinal_planner": (
    "openpilot.nrdr.features.longitudinal.longitudinal_planner",
    (
      "CRUISE_ACCEL_VALUES", "CRUISE_OVERSPEED_BRAKING_BUFFER", "CRUISE_OVERSPEED_DRIVING_BUFFER",
      "LAUNCH_COMMIT_TIME", "LAUNCH_DISARM_SPEED", "LAUNCH_MAX_ACCEL", "LAUNCH_MOVING_SPEED", "ROEN_ACCEL_BP",
      "ROEN_PLANNER_ACCEL", "ROEN_TURN_ACCEL_THRESHOLD", "NrdrLongitudinalPlanner", "apply_cruise_overspeed_allowance",
    ),
  ),
  "longitudinal_stopping": (
    "openpilot.nrdr.features.longitudinal.longitudinal_stopping",
    ("ACCELERATION_DUE_TO_GRAVITY", "CONTROL_DT", "HARD_HOLD_FLOOR", "compute_stopping_accel"),
  ),
  "lane_change": (
    "openpilot.nrdr.features.driver_policy.lane_change",
    ("driver_nudging", "torque_controller_active", "torque_from_lateral_accel"),
  ),
  "mads": (
    "openpilot.nrdr.features.driver_policy.mads",
    ("AutoLkas",),
  ),
  "radar": (
    "openpilot.nrdr.features.radar.radar",
    ("NrdrRadar",),
  ),
  "radar_core": (
    "openpilot.nrdr.features.radar.radar_core",
    ("ACCEL_TAU", "COAST_CYCLES", "STATIONARY_SPEED", "CivicBoschKalmanParams", "CivicBoschTrack"),
  ),
  "speed_limit": (
    "openpilot.nrdr.features.driver_policy.speed_limit",
    (
      "HONDA_MPH_OFFSET", "HONDA_MPH_PER_KPH", "LIMIT_AHEAD_PREEMPTIVE_DISTANCE", "SpeedLimitConfirmation",
      "apply_map_limit", "compare_cluster_target", "honda_kph_to_mph", "honda_mph_to_kph", "is_honda",
      "pre_active_icon", "quantize_set_speed",
    ),
  ),
  "speed_limit_assist": (
    "openpilot.nrdr.features.driver_policy.speed_limit_assist",
    ("AssistState", "ButtonType", "NrdrSpeedLimitAssist"),
  ),
}

PURE_MODULES = ("dec", "hud_submode", "long_tune", "mads")
NUMPY_MODULES = ("longitudinal_mpc", "longitudinal_stopping")
PLATFORM_MODULES = ("radar_core",)
RUNTIME_MODULES = tuple(name for name in LEGACY_FEATURE_EXPORTS if name not in (*PURE_MODULES, *NUMPY_MODULES, *PLATFORM_MODULES))


def _assert_module_identity(legacy_name: str) -> None:
  canonical_name, expected_exports = LEGACY_FEATURE_EXPORTS[legacy_name]
  canonical = import_module(canonical_name)
  legacy = import_module(f"openpilot.sunnypilot.nrdr.{legacy_name}")
  assert legacy.__all__ == expected_exports
  for name in expected_exports:
    assert getattr(legacy, name) is getattr(canonical, name), f"{legacy_name}.{name}"


@pytest.mark.parametrize("legacy_name", PURE_MODULES)
def test_pure_legacy_feature_modules_preserve_object_identity(legacy_name):
  _assert_module_identity(legacy_name)


@pytest.mark.parametrize("legacy_name", NUMPY_MODULES)
def test_numpy_legacy_feature_modules_preserve_object_identity(legacy_name):
  pytest.importorskip("numpy")
  _assert_module_identity(legacy_name)


@pytest.mark.parametrize("legacy_name", PLATFORM_MODULES)
def test_platform_legacy_feature_modules_preserve_object_identity(legacy_name):
  pytest.importorskip("numpy")
  pytest.importorskip("setproctitle")
  _assert_module_identity(legacy_name)


@pytest.mark.parametrize("legacy_name", RUNTIME_MODULES)
def test_runtime_legacy_feature_modules_preserve_object_identity(legacy_name):
  pytest.importorskip("numpy")
  pytest.importorskip("opendbc")
  pytest.importorskip("capnp")
  _assert_module_identity(legacy_name)


def test_legacy_modules_are_explicit_forwarders_only():
  repository_root = Path(__file__).resolve().parents[3]
  for legacy_name, (canonical_name, expected_exports) in LEGACY_FEATURE_EXPORTS.items():
    path = repository_root / "openpilot" / "sunnypilot" / "nrdr" / f"{legacy_name}.py"
    tree = ast.parse(path.read_text(), filename=path.name)
    definitions = [node for node in tree.body if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))]
    imports = [node for node in tree.body if isinstance(node, ast.ImportFrom)]
    assert not definitions, legacy_name
    assert len(imports) == 1, legacy_name
    assert imports[0].module == canonical_name, legacy_name
    assert tuple(alias.name for alias in imports[0].names) == expected_exports, legacy_name
