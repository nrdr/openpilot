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
