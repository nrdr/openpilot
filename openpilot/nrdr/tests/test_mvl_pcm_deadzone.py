"""Speed-deadzone replacement: real units, saved-state isolation and UI/RPC contract."""
from dataclasses import replace

import pytest

from openpilot.nrdr.params.pcm_speed_deadzone import (
  PCM_SPEED_DEADZONE_KEY as KEY, PCM_SPEED_DEADZONE_DEFAULT, PCM_SPEED_DEADZONE_DESCRIPTION,
  PCM_SPEED_DEADZONE_DETAILS, decode_speed_deadzone, read_speed_deadzone,
)
from openpilot.nrdr.tests.test_honda_pcm_ui import Params, state, native_layout
from openpilot.nrdr.tests.test_mvl_settings import encoded, rpc as rpc_fixture
from openpilot.nrdr.tests.test_opendbc_boundary import FakeParams
from openpilot.nrdr.tests.test_parked_tuning_schema import items_in
from openpilot.nrdr.ui.honda_pcm import saved_pcm_speed_deadzone, save_pcm_speed_deadzone
from openpilot.sunnypilot.selfdrive.car.opendbc_config import build_sunnypilot_car_config
from openpilot.sunnypilot.sunnylink.tools.compile_settings_ui import compile_schema, DEFAULT_SRC

CAP = "nrdr_mvl_pcm_deadzone_available"
VALUES = tuple(tick / 100 for tick in range(21))
INVALID = (True, False, -1, .21, 2, 5, 10, .155, float("nan"), float("inf"), "", "true", b"\xff", {}, [])


@pytest.fixture
def rpc():
  return rpc_fixture.__wrapped__()


@pytest.mark.parametrize("value", VALUES)
def test_real_speed_units_and_existing_selections(value):
  for raw in (value, str(value), str(value).encode()):
    assert decode_speed_deadzone(raw) == value
  assert saved_pcm_speed_deadzone(Params(**{KEY: value})) == value


@pytest.mark.parametrize("value", INVALID)
def test_invalid_values_are_not_repaired_or_written(value):
  assert decode_speed_deadzone(value) is None
  assert read_speed_deadzone(value) == 0
  ui = state()
  assert not save_pcm_speed_deadzone(ui, value)
  assert not ui.params.writes


def test_missing_is_default_and_old_acceleration_units_are_not_migrated(tmp_path):
  params = FakeParams({"NrdrMvlPcmDeadzone": 10})
  cfg = build_sunnypilot_car_config(params, start_worker=False, metadata_path=tmp_path / "meta.json")
  assert cfg.honda.civic_pcm_speed_deadzone == PCM_SPEED_DEADZONE_DEFAULT == .15
  assert cfg.honda.mvl_pcm_deadzone == 0
  assert not params.writes
  params.values[KEY] = 0.
  disabled = build_sunnypilot_car_config(params, start_worker=False, metadata_path=tmp_path / "off.json")
  assert disabled.honda.civic_pcm_speed_deadzone == 0.
  assert cfg == replace(disabled, honda=replace(disabled.honda, provider=cfg.honda.provider, civic_pcm_speed_deadzone=.15))


def test_speed_choice_is_latched_for_the_drive(tmp_path):
  params = FakeParams({KEY: .05})
  cfg = build_sunnypilot_car_config(params, start_worker=False, metadata_path=tmp_path / "meta.json")
  params.values[KEY] = .2
  cfg.honda.provider.refresh_all()
  assert cfg.honda.civic_pcm_speed_deadzone == .05
  next_drive = build_sunnypilot_car_config(params, start_worker=False, metadata_path=tmp_path / "next.json")
  assert next_drive.honda.civic_pcm_speed_deadzone == .2
  assert not params.writes


@pytest.mark.parametrize("value", VALUES)
@pytest.mark.parametrize("offroad", [True, False])
def test_native_slider_saves_real_value_without_changing_other_settings(value, offroad):
  ui = state()
  ui.params.values.update(IsOffroad=offroad, HondaLiveLearningGas=True, NrdrHondaPcmMode=0, NrdrHondaWindBrake=True)
  assert save_pcm_speed_deadzone(ui, value) is offroad
  assert ui.params.writes == ([(KEY, value), ("OnroadCycleRequested", True)] if offroad else [])
  assert ui.params.get("NrdrHondaPcmMode") == 0 and ui.params.get_bool("NrdrHondaWindBrake")


@pytest.mark.parametrize("value", VALUES)
@pytest.mark.parametrize("compressed", [False, True])
def test_remote_slider_saves_real_value(rpc, value, compressed):
  save, params, caps = rpc
  caps[CAP] = True
  save({KEY: encoded(value, compressed)}, compressed)
  assert params.get(KEY) == value and type(params.get(KEY)) is float
  assert params.get_bool("OnroadCycleRequested")


@pytest.mark.parametrize("value", INVALID)
def test_remote_malformed_values_rejected_before_any_batch_write(rpc, value):
  save, params, caps = rpc
  caps[CAP] = True
  with pytest.raises(ValueError):
    save({"ExperimentalMode": encoded(1), KEY: encoded(value)})
  assert not params.writes


def test_retired_acceleration_setting_cannot_be_written(rpc):
  save, params, _ = rpc
  with pytest.raises(ValueError, match="Retired"):
    save({"NrdrMvlPcmDeadzone": encoded(10)})
  assert not params.writes


@pytest.mark.parametrize("offroad,capability", [(False, True), (True, False), (True, None)])
def test_remote_road_and_hardware_guards(rpc, offroad, capability):
  save, params, caps = rpc
  params.values["IsOffroad"] = offroad
  caps[CAP] = capability
  with pytest.raises(ValueError):
    save({KEY: encoded(.15)})
  assert not params.writes


def test_web_slider_and_native_admission_do_not_depend_on_selected_mode():
  items = {item["key"]: item for item in items_in(compile_schema(DEFAULT_SRC))}
  assert "NrdrMvlPcmDeadzone" not in items
  web = items[KEY]
  assert web["widget"] == "option"
  assert (web["min"], web["max"], web["step"], web["unit"]) == (0, .2, .01, "m/s")
  assert web["description"] == PCM_SPEED_DEADZONE_DESCRIPTION
  assert web["details"] == PCM_SPEED_DEADZONE_DETAILS
  ui = state(openpilotLongitudinalControl=False)
  ui.params.values.update(NrdrHondaPcmMode=0, HondaLiveLearningGas=False)
  layout = native_layout(ui)
  layout._update_state()
  assert layout._mvl_pcm_deadzone.enabled
  assert save_pcm_speed_deadzone(ui, .15)
