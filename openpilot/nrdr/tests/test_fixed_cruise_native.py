"""Native imports/messages acceptance for the parent's isolated Linux overlay.

No CAN, device Params reads/writes, native optimizer or onroad processes.
"""
import sys

import pytest

if sys.platform == "win32":
  pytest.skip("Native cruise acceptance runs in isolated Linux staging", allow_module_level=True)

from opendbc.car.honda.pcm_test_modes import FIXED_CRUISE_MPS
from opendbc.car.honda.values import CAR, HondaFlags
from opendbc.car.structs import car
from openpilot.cereal import custom
from openpilot.common.constants import CV
from openpilot.nrdr.features.driver_policy import cruise as nrdr_cruise
from openpilot.nrdr.tests.test_mvl_cruise import DEFAULTS, Params
from openpilot.selfdrive.car.cruise import VCruiseHelper
from openpilot.sunnypilot.selfdrive.car import cruise_ext


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
