from dataclasses import asdict
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event, get_ident
import unittest

from opendbc.car.honda.interface import CarInterface as HondaCarInterface
from opendbc.car.honda.values import CAR as HONDA
from opendbc.sunnypilot.car.runtime_config import HondaLiveTuning

from openpilot.nrdr.car.opendbc import (
  FAST_PARAM_GROUP,
  HondaParamsProvider,
  OpendbcParamKey,
  SLOW_PARAM_GROUPS,
  build_opendbc_config,
)


class UnknownKeyName(Exception):
  pass


STARTUP_DEFAULTS = {
  OpendbcParamKey.HONDA_BOSCH_A_RADAR: True,
  OpendbcParamKey.HONDA_ENFORCE_STOCK_LONGITUDINAL: False,
  OpendbcParamKey.HYUNDAI_LONGITUDINAL_TUNING: 0,
  OpendbcParamKey.SUBARU_STOP_AND_GO: False,
  OpendbcParamKey.SUBARU_STOP_AND_GO_MANUAL_PARKING_BRAKE: False,
  OpendbcParamKey.TESLA_COOPERATIVE_STEERING: False,
  OpendbcParamKey.TESLA_MADS_SCREEN_BUTTON: 0,
  OpendbcParamKey.TOYOTA_ENFORCE_STOCK_LONGITUDINAL: False,
  OpendbcParamKey.TOYOTA_STOP_AND_GO_HACK: False,
}


class FakeParams:
  def __init__(self, values=None, defaults=None, unknown=()):
    self.values = {str(key): value for key, value in (values or {}).items()}
    self.defaults = {str(key): value for key, value in (defaults or STARTUP_DEFAULTS).items()}
    self.unknown = {str(key) for key in unknown}
    self.fail_keys = set()
    self.reads = []
    self.writes = []
    self.write_event = Event()

  def get(self, key, return_default=False):
    key = str(key)
    self.reads.append((key, get_ident()))
    if key in self.unknown:
      raise UnknownKeyName(key)
    if key in self.fail_keys:
      raise OSError(key)
    if key in self.values:
      return self.values[key]
    return self.defaults.get(key) if return_default else None

  def put_bool(self, key, value, block=False):
    self.put(key, bool(value), block)

  def put(self, key, value, block=False):
    key = str(key)
    if key in self.unknown:
      raise UnknownKeyName(key)
    self.values[key] = value
    self.writes.append((key, value, block, get_ident()))
    self.write_event.set()


class TestOpendbcBoundary(unittest.TestCase):
  def setUp(self):
    self._temporary_directory = TemporaryDirectory()
    self.addCleanup(self._temporary_directory.cleanup)
    self.tmp_path = Path(self._temporary_directory.name)

  def test_all_former_param_consumers_have_one_canonical_key_owner(self):
    grouped_keys = [key for group in (*SLOW_PARAM_GROUPS, FAST_PARAM_GROUP) for key in group]
    self.assertEqual(len(grouped_keys), len(set(grouped_keys)))
    self.assertSetEqual(set(grouped_keys), {
      OpendbcParamKey.HONDA_OVERRIDE_FADE_DOWN_SECS,
      OpendbcParamKey.HONDA_OVERRIDE_FADE_UP_SECS,
      OpendbcParamKey.HONDA_OVERRIDE_TORQUE_SCALE,
      OpendbcParamKey.HONDA_DRIVER_ASSIST_DURING_OVERRIDE,
      OpendbcParamKey.HONDA_LIVE_LEARNING_GAS,
      OpendbcParamKey.HONDA_TORQUE_LOW_PASS_FILTER,
      OpendbcParamKey.HONDA_LPF_TAU_LOW_SPEED,
      OpendbcParamKey.HONDA_LPF_TAU_STANDARD,
      OpendbcParamKey.HONDA_LPF_TAU_HIGHWAY,
      OpendbcParamKey.HONDA_STEER_DELTA_LIMITER,
      OpendbcParamKey.HONDA_STEER_DELTA_UP,
      OpendbcParamKey.HONDA_STEER_DELTA_DOWN,
      OpendbcParamKey.HONDA_STOPPING_DECEL_RATE,
      OpendbcParamKey.NRDR_INCREASE_OVERRIDE_TOLERANCE,
      OpendbcParamKey.NRDR_DRIVER_OVERRIDE_THRESHOLD,
      OpendbcParamKey.HONDA_CENTER_BOOST_THRESHOLD,
      OpendbcParamKey.NRDR_OVERRIDE_THRESHOLD_CENTER_BOOST,
      OpendbcParamKey.HONDA_ALT_DASHBOARD_SPEED,
      OpendbcParamKey.HONDA_ALT_DASHBOARD_DISTANCE,
      OpendbcParamKey.NRDR_CLEAR_DASH_FAULTS,
      OpendbcParamKey.HONDA_SPOOF_CAMERA_MESSAGES,
      OpendbcParamKey.NRDR_CRUISE_BUTTON_SUB_MODE,
      OpendbcParamKey.NRDR_HUD_SUB_MODE_UNTIL,
      OpendbcParamKey.NRDR_HONDA_ECU_MATCHED_LONG,
      OpendbcParamKey.NRDR_HONDA_FULL_BRAKE_AUTHORITY,
      OpendbcParamKey.NRDR_ROEN_ACCELERATION_LIMITS,
    })
    self.assertTrue(set(STARTUP_DEFAULTS).isdisjoint(grouped_keys))
    self.assertSetEqual(set(OpendbcParamKey), set(grouped_keys) | set(STARTUP_DEFAULTS) | {
      OpendbcParamKey.HONDA_GAS_FACTOR,
      OpendbcParamKey.HONDA_WIND_FACTOR,
    })

  def test_missing_startup_values_preserve_previous_interface_behavior(self):
    config = build_opendbc_config(FakeParams(), start_worker=False, metadata_path=self.tmp_path / "meta.json")
    self.assertFalse(config.honda.bosch_a_radar)
    self.assertFalse(config.honda.enforce_stock_longitudinal)
    self.assertEqual(config.hyundai.longitudinal_tuning, 0)
    self.assertFalse(config.subaru.stop_and_go)
    self.assertFalse(config.subaru.stop_and_go_manual_parking_brake)
    self.assertFalse(config.tesla.cooperative_steering)
    self.assertEqual(config.tesla.mads_screen_button, 0)
    self.assertFalse(config.toyota.enforce_stock_longitudinal)
    self.assertFalse(config.toyota.stop_and_go_hack)

  def test_honda_workers_stay_dormant_until_honda_interface_activation(self):
    params = FakeParams()
    config = build_opendbc_config(params, start_worker=True, metadata_path=self.tmp_path / "meta.json")
    provider = config.honda.provider
    try:
      self.assertFalse(provider._workers_started)
      self.assertFalse({key for key, _ in params.reads} & {str(key) for group in SLOW_PARAM_GROUPS for key in group})
      provider.initialize_live_learning_gas(False)
      self.assertTrue(provider._workers_started)
    finally:
      provider.close()

  def test_honda_state_and_controller_receive_the_same_typed_boundary(self):
    config = build_opendbc_config(FakeParams(), start_worker=False, metadata_path=self.tmp_path / "meta.json")
    cp = HondaCarInterface.get_non_essential_params(HONDA.HONDA_CLARITY, config)
    cp_sp = HondaCarInterface.get_non_essential_params_sp(cp, HONDA.HONDA_CLARITY)
    interface = HondaCarInterface(cp, cp_sp, config)

    self.assertIs(interface.interface_config, config)
    self.assertIs(interface.CS.nrdr.config, config.honda)
    self.assertIs(interface.CC.nrdr.config, config.honda)
    self.assertIs(interface.CS.nrdr.config.provider, interface.CC.nrdr.config.provider)

  def test_explicit_startup_values_preserve_typed_parity(self):
    params = FakeParams(values={key: (2 if key in (
      OpendbcParamKey.HYUNDAI_LONGITUDINAL_TUNING,
      OpendbcParamKey.TESLA_MADS_SCREEN_BUTTON,
    ) else True) for key in STARTUP_DEFAULTS})
    config = build_opendbc_config(params, start_worker=False, metadata_path=self.tmp_path / "meta.json")

    self.assertTrue(config.honda.bosch_a_radar)
    self.assertTrue(config.honda.enforce_stock_longitudinal)
    self.assertEqual(config.hyundai.longitudinal_tuning, 2)
    self.assertTrue(config.subaru.stop_and_go)
    self.assertTrue(config.subaru.stop_and_go_manual_parking_brake)
    self.assertTrue(config.tesla.cooperative_steering)
    self.assertEqual(config.tesla.mads_screen_button, 2)
    self.assertTrue(config.toyota.enforce_stock_longitudinal)
    self.assertTrue(config.toyota.stop_and_go_hack)

  def test_unknown_keys_receive_characterized_safe_fallbacks(self):
    params = FakeParams(unknown=STARTUP_DEFAULTS)
    config = build_opendbc_config(params, start_worker=False, metadata_path=self.tmp_path / "meta.json")

    self.assertFalse(config.honda.bosch_a_radar)
    self.assertFalse(config.honda.enforce_stock_longitudinal)
    self.assertEqual(config.hyundai.longitudinal_tuning, 0)
    self.assertFalse(config.subaru.stop_and_go)
    self.assertFalse(config.tesla.cooperative_steering)
    self.assertFalse(config.toyota.enforce_stock_longitudinal)

  def test_missing_live_values_match_historical_defaults(self):
    provider = HondaParamsProvider(FakeParams(), start_worker=False, metadata_path=self.tmp_path / "meta.json")
    tuning = provider.get_live_tuning()

    expected = HondaLiveTuning(
      generation=tuning.generation,
      override_fade_down_s=0.1,
      override_fade_up_s=0.1,
      override_torque_scale=0.0,
      driver_assist_during_override=True,
      live_learning_gas=True,
      torque_lpf_enabled=True,
      lpf_tau_low=0.1,
      lpf_tau_standard=0.1,
      lpf_tau_highway=0.05,
      steer_delta_limiter_enabled=False,
      steer_delta_up=3.0,
      steer_delta_down=3.0,
      stopping_decel_rate=0.3,
      increase_override_tolerance=False,
      driver_override_threshold=1400.0,
      center_override_threshold=1000.0,
      center_boost_angle=0.0,
      alt_dashboard_speed=0,
      alt_dashboard_distance=0,
      clear_dash_faults=True,
      spoof_camera_messages=False,
      sub_mode_enabled=False,
      sub_mode_until=0.0,
      ecu_matched_long=False,
      full_brake_authority=True,
      roen_acceleration_limits=True,
    )
    self.assertEqual(tuning, expected)

  def test_live_values_preserve_conversion_scaling_and_clamps(self):
    params = FakeParams(values={
      OpendbcParamKey.HONDA_OVERRIDE_FADE_DOWN_SECS: -1.0,
      OpendbcParamKey.HONDA_OVERRIDE_FADE_UP_SECS: 20.0,
      OpendbcParamKey.HONDA_OVERRIDE_TORQUE_SCALE: 25,
      OpendbcParamKey.HONDA_STOPPING_DECEL_RATE: 30,
      OpendbcParamKey.NRDR_DRIVER_OVERRIDE_THRESHOLD: -1,
      OpendbcParamKey.NRDR_OVERRIDE_THRESHOLD_CENTER_BOOST: "1800",
      OpendbcParamKey.HONDA_CENTER_BOOST_THRESHOLD: -5.0,
      OpendbcParamKey.HONDA_ALT_DASHBOARD_SPEED: 9,
      OpendbcParamKey.HONDA_ALT_DASHBOARD_DISTANCE: 9,
    })
    provider = HondaParamsProvider(params, start_worker=False, metadata_path=self.tmp_path / "meta.json")
    tuning = provider.get_live_tuning()

    self.assertEqual(tuning.override_fade_down_s, 0.0)
    self.assertEqual(tuning.override_fade_up_s, 10.0)
    self.assertEqual(tuning.override_torque_scale, 0.25)
    self.assertEqual(tuning.stopping_decel_rate, 0.3)
    self.assertEqual(tuning.driver_override_threshold, 1400.0)
    self.assertEqual(tuning.center_override_threshold, 1800.0)
    self.assertEqual(tuning.center_boost_angle, 0.0)
    self.assertEqual(tuning.alt_dashboard_speed, 3)
    self.assertEqual(tuning.alt_dashboard_distance, 2)

  def test_live_learning_default_is_initialized_by_openpilot(self):
    for gas_interceptor, expected in ((True, False), (False, True)):
      with self.subTest(gas_interceptor=gas_interceptor, expected=expected):
        params = FakeParams()
        provider = HondaParamsProvider(params, start_worker=False, metadata_path=self.tmp_path / "meta.json")
        provider.initialize_live_learning_gas(gas_interceptor)

        self.assertIs(params.values[str(OpendbcParamKey.HONDA_LIVE_LEARNING_GAS)], expected)
        self.assertIs(provider.get_live_tuning().live_learning_gas, expected)

  def test_live_learning_user_override_is_preserved(self):
    for existing in (True, False):
      with self.subTest(existing=existing):
        params = FakeParams(values={OpendbcParamKey.HONDA_LIVE_LEARNING_GAS: existing})
        provider = HondaParamsProvider(params, start_worker=False, metadata_path=self.tmp_path / "meta.json")
        provider.initialize_live_learning_gas(not existing)

        self.assertIs(params.values[str(OpendbcParamKey.HONDA_LIVE_LEARNING_GAS)], existing)
        self.assertEqual(params.writes, [])

  def test_group_refresh_is_atomic_and_fast_deadline_is_independent(self):
    values = {key: 1 for group in (*SLOW_PARAM_GROUPS, FAST_PARAM_GROUP) for key in group}
    params = FakeParams(values=values)
    provider = HondaParamsProvider(params, start_worker=False, metadata_path=self.tmp_path / "meta.json")
    initial = provider.get_live_tuning()

    first_group = SLOW_PARAM_GROUPS[0]
    params.values.update({str(key): 2 for key in first_group})
    self.assertTrue(provider.poll_once())
    self.assertGreater(provider.get_live_tuning().generation, initial.generation)

    stable = provider.get_live_tuning()
    failed_key = first_group[-1]
    provider._slot = 0
    params.values.update({str(key): 3 for key in first_group})
    params.fail_keys.add(str(failed_key))
    self.assertFalse(provider.poll_once())
    self.assertIs(provider.get_live_tuning(), stable)

    params.fail_keys.clear()
    params.values[str(FAST_PARAM_GROUP[0])] = 25.0
    self.assertTrue(provider.poll_fast())
    self.assertEqual(provider.get_live_tuning().sub_mode_until, 25.0)

  def test_factor_loading_validates_fingerprint_version_and_bounds(self):
    metadata_path = self.tmp_path / "meta.json"
    metadata_path.write_text(json.dumps({"car_fingerprint": "HONDA_CLARITY", "learn_version": 2}), encoding="utf-8")
    params = FakeParams(values={
      OpendbcParamKey.HONDA_GAS_FACTOR: 2.0,
      OpendbcParamKey.HONDA_WIND_FACTOR: 0.5,
    })
    provider = HondaParamsProvider(params, start_worker=False, metadata_path=metadata_path)

    self.assertEqual(provider.load_longitudinal_factors("HONDA_CLARITY"), (1.6, 0.6))
    self.assertEqual(provider.load_longitudinal_factors("HONDA_CIVIC"), (1.0, 1.0))

  def test_factor_persistence_runs_off_controller_thread(self):
    params = FakeParams()
    metadata_path = self.tmp_path / "meta.json"
    provider = HondaParamsProvider(params, refresh_period=1000.0, start_worker=True, metadata_path=metadata_path)
    caller_thread = get_ident()
    try:
      provider.persist_longitudinal_factors(1.2, 0.8, "HONDA_CLARITY")
      self.assertTrue(params.write_event.wait(1.0))
      for _ in range(100):
        if len(params.writes) >= 2 and metadata_path.exists():
          break
        Event().wait(0.01)

      self.assertEqual([(key, value, block) for key, value, block, _ in params.writes[-2:]], [
        (str(OpendbcParamKey.HONDA_GAS_FACTOR), 1.2, True),
        (str(OpendbcParamKey.HONDA_WIND_FACTOR), 0.8, True),
      ])
      self.assertTrue(all(thread_id != caller_thread for *_, thread_id in params.writes[-2:]))
      self.assertEqual(json.loads(metadata_path.read_text(encoding="utf-8")), {
        "car_fingerprint": "HONDA_CLARITY",
        "learn_version": 2,
      })
    finally:
      provider.close()

  def test_opendbc_and_all_production_callers_use_only_the_typed_boundary(self):
    repository_root = Path(__file__).resolve().parents[3]
    opendbc_root = repository_root / "opendbc_repo" / "opendbc"
    for path in opendbc_root.rglob("*.py"):
      if "tests" in path.parts:
        continue
      source = path.read_text(encoding="utf-8")
      self.assertNotIn("openpilot.common.params", source, str(path))

    caller_expectations = {
      "openpilot/selfdrive/car/card.py": "sunnypilot_interfaces.initialize_params(self.params)",
      "openpilot/selfdrive/controls/controlsd.py": "build_opendbc_config(self.params)",
      "openpilot/selfdrive/test/process_replay/process_replay.py": "build_opendbc_config(params)",
      "openpilot/nrdr/features/lateral/latcontrol_clarity_hybrid.py": "CI.interface_config",
      "openpilot/nrdr/features/services/car_tune_report.py": "build_opendbc_config(self.params, start_worker=False)",
      "openpilot/nrdr/ui/settings/lateral_tuning.py": "build_opendbc_config(ui_state.params, start_worker=False)",
    }
    for relative_path, seam in caller_expectations.items():
      with self.subTest(relative_path=relative_path):
        source = (repository_root / relative_path).read_text(encoding="utf-8")
        self.assertTrue(
          "from openpilot.nrdr.car.opendbc import build_opendbc_config" in source
          or "CI.interface_config" in source
          or "sunnypilot_interfaces.initialize_params" in source,
        )
        self.assertIn(seam, source)

    legacy_source = (repository_root / "openpilot/sunnypilot/selfdrive/car/interfaces.py").read_text(encoding="utf-8")
    self.assertNotIn("init_params_list_sp", legacy_source)
    self.assertIn("from openpilot.nrdr.car.opendbc import build_opendbc_config", legacy_source)
    self.assertIn("return build_opendbc_config(params)", legacy_source)

  def test_live_snapshot_is_plain_immutable_typed_data(self):
    provider = HondaParamsProvider(FakeParams(), start_worker=False, metadata_path=self.tmp_path / "meta.json")
    tuning = provider.get_live_tuning()
    self.assertSetEqual(set(asdict(tuning)), {field.name for field in tuning.__dataclass_fields__.values()})
    with self.assertRaises((AttributeError, TypeError)):
      tuning.lpf_tau_highway = 1.0
