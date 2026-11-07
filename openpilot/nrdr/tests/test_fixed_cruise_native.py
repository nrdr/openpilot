"""Native imports/messages acceptance for the parent's isolated Linux overlay.

No CAN, device Params reads/writes, native optimizer or onroad processes.
"""
import sys

import pytest

if sys.platform == "win32":
  pytest.skip("Native cruise acceptance runs in isolated Linux staging", allow_module_level=True)

from opendbc.car.honda.interface import CarInterface
from opendbc.car.honda.pcm_test_modes import FIXED_CRUISE_MPS
from opendbc.car.honda.values import CAR, HondaFlags
from opendbc.car.structs import car
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.cereal import custom
from openpilot.common.constants import CV
from openpilot.nrdr.features.driver_policy import cruise as nrdr_cruise
from openpilot.nrdr.tests.test_mvl_cruise import DEFAULTS, Params
from openpilot.nrdr.tests.test_opendbc_boundary import FakeParams
from openpilot.selfdrive.car.cruise import VCruiseHelper
from openpilot.sunnypilot.selfdrive.car import cruise_ext
from openpilot.sunnypilot.selfdrive.car.opendbc_config import build_sunnypilot_car_config


@pytest.mark.parametrize("fixed", (False, True))
@pytest.mark.parametrize("legacy", (False, True))
@pytest.mark.parametrize("mvl", (False, True))
@pytest.mark.parametrize("metric", (False, True))
def test_native_fixed_target_ownership_and_resume(monkeypatch, fixed, legacy, mvl, metric):
  params = Params(DEFAULTS)
  monkeypatch.setattr(cruise_ext, "Params", lambda: params)
  monkeypatch.setattr(nrdr_cruise, "Params", lambda: params)
  monkeypatch.setattr(nrdr_cruise, "consume_button_press", lambda _: True)
  flags = HondaFlags.NIDEC
  if fixed:
    flags |= HondaFlags.NIDEC_PCM_FIXED_CRUISE
  if legacy:
    flags |= HondaFlags.NIDEC_PCM_LEGACY
  if mvl:
    flags |= HondaFlags.MVL_LONGITUDINAL
  cp = car.CarParams.new_message(brand="honda", carFingerprint=CAR.HONDA_CIVIC, flags=int(flags),
                                pcmCruise=True, openpilotLongitudinalControl=True)
  cp_sp = custom.CarParamsSP.new_message(pcmCruiseSpeed=not fixed)
  helper = VCruiseHelper(cp, cp_sp)
  cs = car.CarState.new_message(vEgo=0., cruiseState={"available": True, "speed": FIXED_CRUISE_MPS,
                                                    "speedCluster": FIXED_CRUISE_MPS})
  helper.update_v_cruise(cs, False, metric)
  helper.update_v_cruise(cs, True, metric)
  helper.initialize_v_cruise(cs, False)
  helper.update_v_cruise(cs, True, metric)
  expected = 0. if fixed else cs.cruiseState.speed * CV.MS_TO_KPH
  assert helper.v_cruise_kph == helper.v_cruise_cluster_kph == expected
  assert cp.pcmCruise
  for _ in range(10):
    cs.cruiseState.available = False
    helper.update_v_cruise(cs, False, not metric)
    assert not helper.v_cruise_initialized
  cs.cruiseState.available = True
  cs.vEgo = 25.
  cs.buttonEvents = [{"type": "accelCruise", "pressed": False}]
  helper.update_v_cruise(cs, True, not metric)
  helper.initialize_v_cruise(cs, True)
  assert helper.v_cruise_kph == helper.v_cruise_cluster_kph == expected
  if fixed:
    assert helper.v_cruise_min == 0
    for button in ("accelCruise", "decelCruise"):
      cs.buttonEvents = []
      helper.update_v_cruise(cs, True, metric)
      for pressed in (True, False):
        cs.buttonEvents = [{"type": button, "pressed": pressed}]
        helper.update_v_cruise(cs, True, metric)
      assert 0 <= helper.v_cruise_kph <= FIXED_CRUISE_MPS * CV.MS_TO_KPH
    assert helper.v_cruise_kph == 0.


def test_host_configured_modified_eps_fixed_cruise_owns_target_below_stock_25mph(monkeypatch, tmp_path):
  # Match the saved choices from the affected native (non-interceptor) Civic.
  host_params = FakeParams({"NrdrHondaPcmFixedCruise": True, "NrdrHondaLegacyPcm": False,
                            "HondaLiveLearningGas": False, "HondaEnforceStockLongitudinal": False})
  config = build_sunnypilot_car_config(host_params, start_worker=False, metadata_path=tmp_path / "meta.json")
  fingerprint = {bus: {} for bus in range(7)}
  firmware = [car.CarParams.CarFw.new_message(ecu="eps", fwVersion=b"39990-TBA-A030,modified")]
  cp = CarInterface.get_params(CAR.HONDA_CIVIC, fingerprint, firmware, alpha_long=True, is_release=False,
                               docs=False, interface_config=config)
  # Modified EPS is temporarily dashcam-only until SP admission. Do not inject flags.
  assert cp.dashcamOnly
  minimum_enable_speed = cp.minEnableSpeed
  safety_configs = [safety.to_dict() for safety in cp.safetyConfigs]
  cp_sp = CarInterface.get_params_sp(cp, CAR.HONDA_CIVIC, fingerprint, firmware, alpha_long=True,
                                     is_release_sp=False, docs=False)
  assert not cp.dashcamOnly and cp_sp.flags & HondaFlagsSP.EPS_MODIFIED
  assert cp.flags & HondaFlags.NIDEC_PCM_FIXED_CRUISE
  assert not cp.flags & (HondaFlags.NIDEC_PCM_LEGACY | HondaFlags.MVL_LONGITUDINAL)
  assert cp.openpilotLongitudinalControl and cp.pcmCruise
  assert not cp_sp.enableGasInterceptor and not cp_sp.pcmCruiseSpeed

  # Only settings storage is replaced; admission, qualification and buttons are real.
  params = Params(DEFAULTS | {"NrdrCruiseButtonSubMode": False})
  monkeypatch.setattr(cruise_ext, "Params", lambda: params)
  monkeypatch.setattr(nrdr_cruise, "Params", lambda: params)
  helper = VCruiseHelper(cp, cp_sp)
  assert helper.fixed_cruise_enabled and not helper.mvl_enabled
  assert helper.v_cruise_max == FIXED_CRUISE_MPS * CV.MS_TO_KPH
  cs = car.CarState.new_message(vEgo=25. * CV.MPH_TO_MS,
                                cruiseState={"available": True, "speed": 25. * CV.MPH_TO_MS,
                                             "speedCluster": 25. * CV.MPH_TO_MS})
  stock_speed = cs.cruiseState.speed

  def engage(button):
    # card.py updates first, then initializes from the previous frame's buttons.
    previous = cs.as_reader().as_builder()
    previous.buttonEvents = [{"type": button, "pressed": False}]
    helper.update_v_cruise(previous, False, False)
    cs.buttonEvents = []
    helper.update_v_cruise(cs, True, False)
    helper.initialize_v_cruise(previous, False)
    helper.update_v_cruise(cs, True, False)

  def tap(button):
    for pressed in (True, False):
      cs.buttonEvents = [{"type": button, "pressed": pressed}]
      helper.update_v_cruise(cs, True, False)
    assert cs.cruiseState.speed == stock_speed

  engage("decelCruise")
  assert helper.v_cruise_min == 0
  assert round(helper.v_cruise_kph * .6233 + .0995) == 25
  for _ in range(25):
    previous_target = helper.v_cruise_kph
    tap("decelCruise")
    assert 0 <= helper.v_cruise_kph < previous_target
  assert helper.v_cruise_kph == helper.v_cruise_cluster_kph == 0.
  tap("accelCruise")
  assert 0 < helper.v_cruise_kph < 2.
  tap("decelCruise")
  assert helper.v_cruise_kph == 0.

  # Disengagement and unit changes must not restore the unchanged 25 mph readback.
  cs.buttonEvents = []
  cs.cruiseState.available = False
  helper.update_v_cruise(cs, False, True)
  assert not helper.v_cruise_initialized
  cs.cruiseState.available = True
  engage("accelCruise")
  assert helper.v_cruise_kph == helper.v_cruise_cluster_kph == 0.
  cs.vEgo = 0.
  cs.cruiseState.standstill = True
  engage("decelCruise")
  assert helper.v_cruise_kph == helper.v_cruise_cluster_kph == 0.
  tap("accelCruise")  # RES at standstill remains a no-increment action.
  assert helper.v_cruise_kph == 0.

  assert cp.pcmCruise and cp.minEnableSpeed == minimum_enable_speed
  assert [safety.to_dict() for safety in cp.safetyConfigs] == safety_configs
  assert cp_sp.safetyParam == 0
  assert not host_params.writes
  assert all(operation == "get" for operation, _ in params.calls)
