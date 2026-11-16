"""Parked saved choices are separate from the previous drive's controller mode."""
import itertools

import pytest

from opendbc.car.honda.values import HondaFlags
from openpilot.nrdr.params.tuning_policy import (
  MVL_LOCK_KEYS, RETIRED_TUNING_KEYS, SUGGESTED_LOCK_KEYS, mvl_tuning_locked, tuning_write_allowed,
)
from openpilot.nrdr.tests.test_honda_pcm_ui import Params, native_layout, state
from openpilot.nrdr.tests.test_nidec_pcm_experiments import cp_bytes
from openpilot.nrdr.ui.honda_pcm import save_live_gas_choice, save_pcm_speed_deadzone, save_pcm_choice


@pytest.mark.parametrize("key", sorted(MVL_LOCK_KEYS))
@pytest.mark.parametrize("saved_mvl,saved_legacy", list(itertools.product((False, True), repeat=2)))
@pytest.mark.parametrize("flags", [0, HondaFlags.MVL_LONGITUDINAL, 524288])
def test_all_conflicting_saved_choices_editable_parked_even_after_a_different_drive(key, saved_mvl, saved_legacy, flags):
  params = Params(IsOffroad=True, HondaLiveLearningGas=saved_mvl, NrdrHondaLegacyPcm=saved_legacy,
                  CarParamsPersistent=cp_bytes(flags))
  before = dict(params.values)
  assert tuning_write_allowed(params, key)
  assert params.values == before and not params.writes


@pytest.mark.parametrize("raw", [None, b"corrupt", cp_bytes(524288)])
def test_parked_editing_does_not_require_valid_current_or_persistent_mode(raw):
  params = Params(IsOffroad=True, HondaLiveLearningGas=False, NrdrHondaLegacyPcm=False,
                  CarParams=raw, CarParamsPersistent=cp_bytes(HondaFlags.MVL_LONGITUDINAL))
  assert tuning_write_allowed(params, "LongPidTuneScaleStandard")
  assert tuning_write_allowed(params, "SmartCruiseControlVision")
  assert not params.writes


@pytest.mark.parametrize("parked", [False, None, "garbage"])
@pytest.mark.parametrize("flags", [HondaFlags.MVL_LONGITUDINAL, 524288])
def test_modes_do_not_lock_saved_tuning_even_with_unknown_road_state(parked, flags):
  params = Params(IsOffroad=parked, HondaLiveLearningGas=False, NrdrHondaLegacyPcm=False,
                  CarParamsPersistent=cp_bytes(flags))
  assert tuning_write_allowed(params, "LongPidTuneScaleStandard")
  assert tuning_write_allowed(params, "NrdrHondaWindBrake")


def test_ui_road_state_can_override_stale_stored_road_state_without_changing_ownership():
  params = Params(IsOffroad=True, HondaLiveLearningGas=True, NrdrHondaLegacyPcm=True,
                  CarParamsPersistent=cp_bytes(524288))
  assert mvl_tuning_locked(params)
  assert tuning_write_allowed(params, "LongPidTuneScaleStandard")
  assert tuning_write_allowed(params, "LongPidTuneScaleStandard", is_offroad=False)
  params.values["IsOffroad"] = False
  assert tuning_write_allowed(params, "LongPidTuneScaleStandard", is_offroad=True)
  assert not params.writes


@pytest.mark.parametrize("key", sorted(RETIRED_TUNING_KEYS))
def test_parked_preconfiguration_does_not_resurrect_retired_settings(key):
  assert not tuning_write_allowed(Params(IsOffroad=True), key)


@pytest.mark.parametrize("key", sorted(SUGGESTED_LOCK_KEYS - RETIRED_TUNING_KEYS) + ["NrdrSteerRatioMode", "LaneCenteringStrength"])
def test_completed_preset_allows_parked_editing_but_pending_application_is_still_guarded(key):
  params = Params(IsOffroad=True, NrdrSuggestedSettings=True)
  before = dict(params.values)
  assert tuning_write_allowed(params, key)
  assert params.values == before and not params.writes
  assert not tuning_write_allowed(params, key, is_offroad=False)
  params.values["NrdrHandcraftedLateralTune"] = True
  assert not tuning_write_allowed(params, key)


def test_actual_firmware_guards_unchanged():
  assert not tuning_write_allowed(Params(IsOffroad=True, NrdrLateralController=1), "LatPScaleStandard")
  assert not tuning_write_allowed(Params(IsOffroad=True, NrdrLateralController=1), "LagdToggle",
                                  firmware_prediction_schedule=True)


@pytest.mark.parametrize("flags", [HondaFlags.MVL_LONGITUDINAL, 524288])
def test_parked_native_configuration_keeps_old_cp_but_saves_choices(flags):
  ui = state(flags=int(HondaFlags.NIDEC | flags))
  ui.params.values.update(IsOffroad=True, HondaLiveLearningGas=False, NrdrHondaLegacyPcm=False)
  before_flags = ui.CP.flags
  layout = native_layout(ui)
  layout._update_state()
  for name in ("_pcm_mode", "_wind_brake", "_static_feedforward_long", "_live_learning_gas", "_mvl_pcm_deadzone",
               "_long_pid_tune_scale_standard", "_stop_accel", "_standstill_gap"):
    assert getattr(layout, name).enabled, name
  assert layout._long_pid_tune_scale_standard.visible
  assert save_live_gas_choice(ui, True)
  assert save_pcm_speed_deadzone(ui, .05)
  assert save_pcm_choice(ui, "NrdrHondaWindBrake", False)
  assert ui.params.get("NrdrHondaLegacyPcm") is False
  assert ui.CP.flags == before_flags
  ui.params.writes.clear()
  ui.is_offroad = lambda: False
  assert not save_live_gas_choice(ui, False)
  assert not save_pcm_speed_deadzone(ui, 0)
  assert not save_pcm_choice(ui, "NrdrHondaWindBrake", True)
  assert not ui.params.writes
