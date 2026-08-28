from types import SimpleNamespace

import pytest

from openpilot.cereal import messaging
from openpilot.sunnypilot.system import params_migration


LEGACY_DEFAULTS = {
  "NrdrSteerRatioCenterClarity": 18.50,
  "NrdrSteerRatioOuterClarity": 12.72,
  "NrdrSteerRatioCenterCivic": 17.24,
  "NrdrSteerRatioOuterCivic": 10.93,
  "NrdrSteerRatioCenterAccord": 18.31,
  "NrdrSteerRatioOuterAccord": 11.82,
  "NrdrSteerRatioCenterCrv5g": 17.94,
  "NrdrSteerRatioOuterCrv5g": 12.30,
  "NrdrSteerRatioCenterInsight": 16.82,
  "NrdrSteerRatioOuterInsight": 12.58,
}


class FakeParams:
  def __init__(self, values=None):
    self.values = dict(values or {})
    self.puts = []

  def get(self, key, *, return_default=False, **_kwargs):
    if key in self.values:
      return self.values[key]
    return LEGACY_DEFAULTS.get(key) if return_default else None

  def put(self, key, value, *, block=False):
    assert block
    self.puts.append((key, value))
    self.values[key] = value


class FailOnceParams(FakeParams):
  def __init__(self, values=None, *, fail_key):
    super().__init__(values)
    self.fail_key = fail_key
    self.failed = False

  def put(self, key, value, *, block=False):
    if key == self.fail_key and not self.failed:
      self.failed = True
      raise RuntimeError(f"simulated interrupted write for {key}")
    super().put(key, value, block=block)


def test_nrdr_steer_ratio_migration_preserves_attached_family_values():
  params = FakeParams({
    "CarPlatformBundle": {"platform": "HONDA_CLARITY"},
    "NrdrLearnSteerRatio": True,
    "NrdrSteerRatioCenterClarity": 19.25,
    "NrdrSteerRatioOuterClarity": 13.10,
  })

  params_migration._migrate_nrdr_steer_ratio_mode(params)

  assert params.values["NrdrSteerRatioManualCenter"] == 19.25
  assert params.values["NrdrSteerRatioManualFinal"] == 13.10
  assert params.values["NrdrSteerRatioMode"] == 1
  assert params.puts[-1] == ("NrdrSteerRatioMode", 1)


def test_nrdr_steer_ratio_migration_uses_fresh_manual_defaults_without_identity():
  params = FakeParams()

  params_migration._migrate_nrdr_steer_ratio_mode(params)

  assert params.values["NrdrSteerRatioManualCenter"] == 15.38
  assert params.values["NrdrSteerRatioManualFinal"] == 10.93
  assert params.values["NrdrSteerRatioMode"] == 0


def test_nrdr_steer_ratio_migration_uses_fresh_defaults_for_known_car_without_stored_legacy_values():
  params = FakeParams({"CarPlatformBundle": {"platform": "HONDA_CLARITY"}})

  params_migration._migrate_nrdr_steer_ratio_mode(params)

  assert params.values["NrdrSteerRatioManualCenter"] == 15.38
  assert params.values["NrdrSteerRatioManualFinal"] == 10.93


def test_nrdr_steer_ratio_migration_preserves_each_stored_legacy_endpoint_independently():
  params = FakeParams({
    "CarPlatformBundle": {"platform": "HONDA_CLARITY"},
    "NrdrSteerRatioCenterClarity": 19.25,
  })

  params_migration._migrate_nrdr_steer_ratio_mode(params)

  assert params.values["NrdrSteerRatioManualCenter"] == 19.25
  assert params.values["NrdrSteerRatioManualFinal"] == 10.93


def test_nrdr_steer_ratio_migration_is_idempotent_and_never_overwrites_new_keys():
  params = FakeParams({
    "CarPlatformBundle": {"platform": "HONDA_ACCORD"},
    "NrdrLearnSteerRatio": True,
    "NrdrSteerRatioMode": 3,
    "NrdrSteerRatioManualFinal": 9.87,
  })

  params_migration._migrate_nrdr_steer_ratio_mode(params)
  assert params.values["NrdrSteerRatioMode"] == 3
  assert params.values["NrdrSteerRatioManualCenter"] == 15.38
  assert params.values["NrdrSteerRatioManualFinal"] == 9.87

  first_puts = list(params.puts)
  params_migration._migrate_nrdr_steer_ratio_mode(params)
  assert params.puts == first_puts


def test_nrdr_steer_ratio_migration_retries_an_interrupted_manual_pair_before_mode():
  params = FailOnceParams(
    {
      "CarPlatformBundle": {"platform": "HONDA_CLARITY"},
      "NrdrLearnSteerRatio": True,
      "NrdrSteerRatioCenterClarity": 19.25,
      "NrdrSteerRatioOuterClarity": 13.10,
    },
    fail_key="NrdrSteerRatioManualFinal",
  )

  params_migration._migrate_nrdr_steer_ratio_mode(params)

  assert params.values["NrdrSteerRatioManualCenter"] == 19.25
  assert "NrdrSteerRatioManualFinal" not in params.values
  assert "NrdrSteerRatioMode" not in params.values

  params_migration._migrate_nrdr_steer_ratio_mode(params)

  assert params.values["NrdrSteerRatioManualCenter"] == 19.25
  assert params.values["NrdrSteerRatioManualFinal"] == 13.10
  assert params.values["NrdrSteerRatioMode"] == 1
  assert params.puts[-1] == ("NrdrSteerRatioMode", 1)


def test_interpolated_torque_friction_migration_seeds_all_missing_bands_from_default_low():
  params = FakeParams()

  params_migration._migrate_interpolated_torque_friction(params)

  assert params.puts == [
    ("NrdrInterpolatedTorqueFriction", 0.50),
    ("NrdrInterpolatedTorqueFrictionStandard", 0.50),
    ("NrdrInterpolatedTorqueFrictionHighway", 0.50),
  ]


def test_interpolated_torque_friction_migration_preserves_legacy_tune_in_new_bands():
  params = FakeParams({"NrdrInterpolatedTorqueFriction": 0.12})

  params_migration._migrate_interpolated_torque_friction(params)

  assert params.values["NrdrInterpolatedTorqueFriction"] == 0.12
  assert params.values["NrdrInterpolatedTorqueFrictionStandard"] == 0.12
  assert params.values["NrdrInterpolatedTorqueFrictionHighway"] == 0.12
  assert params.puts == [
    ("NrdrInterpolatedTorqueFrictionStandard", 0.12),
    ("NrdrInterpolatedTorqueFrictionHighway", 0.12),
  ]


def test_interpolated_torque_friction_migration_never_overwrites_present_bands_and_is_idempotent():
  params = FakeParams({
    "NrdrInterpolatedTorqueFriction": 0.12,
    "NrdrInterpolatedTorqueFrictionStandard": 0.34,
  })

  params_migration._migrate_interpolated_torque_friction(params)

  assert params.values["NrdrInterpolatedTorqueFriction"] == 0.12
  assert params.values["NrdrInterpolatedTorqueFrictionStandard"] == 0.34
  assert params.values["NrdrInterpolatedTorqueFrictionHighway"] == 0.12
  first_puts = list(params.puts)
  params_migration._migrate_interpolated_torque_friction(params)
  assert params.puts == first_puts


def test_interpolated_torque_friction_migration_stops_dependents_when_low_seed_is_interrupted():
  params = FailOnceParams(fail_key="NrdrInterpolatedTorqueFriction")

  params_migration._migrate_interpolated_torque_friction(params)

  assert not params.values
  assert not params.puts

  params_migration._migrate_interpolated_torque_friction(params)
  assert params.puts == [
    ("NrdrInterpolatedTorqueFriction", 0.50),
    ("NrdrInterpolatedTorqueFrictionStandard", 0.50),
    ("NrdrInterpolatedTorqueFrictionHighway", 0.50),
  ]


def test_interpolated_torque_friction_migration_independently_retries_interrupted_band():
  params = FailOnceParams(
    {"NrdrInterpolatedTorqueFriction": 0.12},
    fail_key="NrdrInterpolatedTorqueFrictionStandard",
  )

  params_migration._migrate_interpolated_torque_friction(params)

  assert "NrdrInterpolatedTorqueFrictionStandard" not in params.values
  assert params.values["NrdrInterpolatedTorqueFrictionHighway"] == 0.12
  assert params.puts == [("NrdrInterpolatedTorqueFrictionHighway", 0.12)]

  params_migration._migrate_interpolated_torque_friction(params)
  assert params.values["NrdrInterpolatedTorqueFrictionStandard"] == 0.12
  assert params.puts[-1] == ("NrdrInterpolatedTorqueFrictionStandard", 0.12)


def test_interpolated_torque_friction_migration_runs_after_steer_ratio(monkeypatch):
  order = []
  params = FakeParams({
    "OnroadScreenOffBrightnessMigrated": params_migration.ONROAD_BRIGHTNESS_MIGRATION_VERSION,
    "OnroadScreenOffTimerMigrated": params_migration.ONROAD_BRIGHTNESS_TIMER_MIGRATION_VERSION,
  })
  monkeypatch.setattr(params_migration, "_migrate_car_platform_bundle", lambda _params: order.append("car"))
  monkeypatch.setattr(params_migration, "_migrate_nrdr_steer_ratio_mode", lambda _params: order.append("steer_ratio"))
  monkeypatch.setattr(params_migration, "_migrate_interpolated_torque_friction", lambda _params: order.append("friction"))
  monkeypatch.setattr(params_migration, "_migrate_tesla_mads_screen_button", lambda _params: order.append("tesla"))

  params_migration.run_migration(params)

  assert order == ["car", "steer_ratio", "friction", "tesla"]


@pytest.mark.parametrize("car_params_key", ["CarParamsPersistent", "CarParams"])
def test_nrdr_steer_ratio_migration_falls_back_to_each_carparams_store(monkeypatch, car_params_key):
  monkeypatch.setattr(
    messaging,
    "log_from_bytes",
    lambda data, _schema: SimpleNamespace(carFingerprint="HONDA_INSIGHT") if data == b"attached" else None,
  )
  params = FakeParams({car_params_key: b"attached"})

  params_migration._migrate_nrdr_steer_ratio_mode(params)

  assert params.values["NrdrSteerRatioManualCenter"] == 15.38
  assert params.values["NrdrSteerRatioManualFinal"] == 10.93
