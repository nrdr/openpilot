"""ICBM can be prepared while parked without changing controller ownership."""
from types import SimpleNamespace as NS

import pytest

from opendbc.car.honda.values import CAR, HondaFlags
from openpilot.nrdr.tests.test_experimental_button_regressions import RecordingParams
from openpilot.nrdr.tests.test_parked_tuning_schema import allowed, items_in
from openpilot.nrdr.ui.icbm import icbm_available, save_icbm_choice
from openpilot.sunnypilot.sunnylink.tools.compile_settings_ui import DEFAULT_SRC, compile_schema


def state(*, offroad=True, interceptor=False, long=True, saved=False):
  cp = NS(brand="honda", carFingerprint=CAR.HONDA_CIVIC, flags=HondaFlags.NIDEC,
          openpilotLongitudinalControl=long, dashcamOnly=False, passive=False)
  sp = NS(enableGasInterceptor=interceptor, intelligentCruiseButtonManagementAvailable=False)
  params = RecordingParams({"IntelligentCruiseButtonManagement": saved, "HondaEnforceStockLongitudinal": False})
  return NS(CP=cp, CP_SP=sp, params=params, is_offroad=lambda: offroad)


@pytest.mark.parametrize("long", [False, True])
@pytest.mark.parametrize("saved", [False, True])
def test_civic_preconfiguration_with_old_persistent_capability(long, saved):
  ui = state(long=long, saved=saved)
  assert icbm_available(ui.CP, ui.CP_SP)
  assert save_icbm_choice(ui, not saved)
  assert ui.params.get_bool("IntelligentCruiseButtonManagement") is not saved
  assert ui.params.get_bool("OnroadCycleRequested")
  assert not ui.params.get_bool("HondaEnforceStockLongitudinal")
  assert ui.CP.openpilotLongitudinalControl is long
  assert not ui.CP_SP.intelligentCruiseButtonManagementAvailable
  assert all(action[1] != "DoReboot" for action in ui.params.actions)


@pytest.mark.parametrize("offroad,interceptor,value", [(False, False, True), (True, True, True), (True, False, 1)])
def test_rejected_writes_leave_saved_choice_alone(offroad, interceptor, value):
  ui = state(offroad=offroad, interceptor=interceptor)
  assert not save_icbm_choice(ui, value)
  assert not ui.params.actions


def test_missing_identity_does_not_invent_hardware_support():
  assert not icbm_available(None, None)
  ui = state()
  ui.CP.carFingerprint = CAR.HONDA_CLARITY
  assert not icbm_available(ui.CP, ui.CP_SP)


def test_sunnylink_can_save_choice_before_stock_acc_is_active():
  items = {item["key"]: item for item in items_in(compile_schema(DEFAULT_SRC))}
  item = items["IntelligentCruiseButtonManagement"]
  values = {"IsOffroad": True, "icbm_available": True, "has_longitudinal_control": True}
  assert allowed(item, values) and allowed(item, values, "visibility")
  assert item["needs_onroad_cycle"]
  assert not item.get("requires_reboot", False)
  assert not allowed(item, values | {"IsOffroad": False})
