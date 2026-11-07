"""LKAS HUD flags and routing, without any vehicle I/O."""
from types import SimpleNamespace

import pytest

from opendbc.can import CANParser
from opendbc.car import Bus, gen_empty_fingerprint, structs
from opendbc.car.honda.hondacan import create_lkas_hud
from opendbc.car.honda.interface import CarInterface
from opendbc.car.honda.tests.test_lane_path import model_at
from opendbc.car.honda.values import CAR, DBC, HondaFlags
from opendbc.sunnypilot.car.tests.runtime_config import make_test_car_config


class CapturePacker:
  def make_can_msg(self, name, bus, values):
    return name, bus, dict(values)


@pytest.mark.parametrize("ext_hud", [False, True])
@pytest.mark.parametrize("alt_radar", [False, True])
@pytest.mark.parametrize("open_long", [False, True])
@pytest.mark.parametrize("lat_active", [False, True])
def test_rdm_and_beep_flags_follow_hud_and_radar_type(ext_hud, alt_radar, open_long, lat_active):
  flags = HondaFlags.BOSCH
  if ext_hud:
    flags |= HondaFlags.BOSCH_EXT_HUD
  if alt_radar:
    flags |= HondaFlags.BOSCH_ALT_RADAR
  cp = SimpleNamespace(flags=flags, openpilotLongitudinalControl=open_long,
                       carFingerprint=CAR.ACURA_RDX_3G_MMR if alt_radar else CAR.HONDA_INSIGHT)
  messages = create_lkas_hud(
    CapturePacker(), 2, cp, None, lat_active, True, False, True, {}, False, False, SimpleNamespace(),
  )

  expected_names = ["LKAS_HUD_A", "LKAS_HUD_B"] if ext_hud and not open_long else ["LKAS_HUD"]
  assert [name for name, _, _ in messages] == expected_names
  expected = {
    "LKAS_READY": 1,
    "LKAS_STATE_CHANGE": 1,
    "STEERING_REQUIRED": True,
    "SOLID_LANES": lat_active,
    "DASHED_LANES": False,
    "BEEP": 0,
  }
  if not ext_hud or alt_radar:
    expected.update(RDM_OFF=1, LANE_ASSIST_BEEP_OFF=1)
  for _, bus, values in messages:
    assert bus == 2
    # Exact payload equality also protects normal extended HUDs: no new RDM or
    # beep fields there, and no unrelated lane/alert changes on ALT_RADAR.
    assert values == expected


@pytest.mark.parametrize("car", [CAR.HONDA_CIVIC_2022, CAR.ACURA_MDX_4G_MMR])
def test_lane_transition_pulse_and_model_path_on_wire(car):
  radarless = car == CAR.HONDA_CIVIC_2022
  config, fp = make_test_car_config(), gen_empty_fingerprint()
  cp = CarInterface.get_params(car, fp, [], False, False, False, config)
  sp = CarInterface.get_params_sp(cp, car, fp, [], False, False, False)
  ci = CarInterface(cp, sp, config)
  ci.update([])
  ci.CS.out.vEgo = 25.
  ci.CS.steer_control_active = True
  decoder = CANParser(DBC[car][Bus.pt], [("LKAS_HUD", 10)] + ([("LKAS_HUD_2", 5)] if radarless else []), ci.CC.CAN.lkas)
  model = model_at(1.)
  model.leadsV3 = []
  cc, cc_sp = structs.CarControl(), structs.CarControlSP()
  cc_sp.mads.available = True
  for frame in range(931):
    tick = frame // 10
    cc.latActive = tick >= 31  # MADS lateral only, ACC remains off
    cc_sp.mads.enabled = cc.latActive
    cc.actuators.torque = 1.0 if 62 <= tick < 93 else 0.25
    cc.hudControl.visualAlert = "steerRequired" if tick == 93 else "none"
    ci.CS.out.steerFaultPermanent = tick == 93
    # Model availability changes independently of the lateral state and the HUD pulse.
    now = (frame + 1) * 10_000_000
    _, messages = ci.apply(cc.as_reader(), cc_sp, now, model if tick % 4 < 2 else None)
    if frame % 10:
      continue
    decoder.update([(now, messages)])
    signals = decoder.vl["LKAS_HUD"]
    assert signals["LKAS_STATE_CHANGE"] == (tick < 30 or 31 <= tick < 61 or (radarless and 62 <= tick < 92) or tick == 93)
    assert signals["DASHED_LANES"] == (radarless or cc.latActive)
    assert signals["SOLID_LANES"] == (cc.latActive and (not radarless or not 62 <= tick < 93))
    assert signals["STEERING_REQUIRED"] == signals["LKAS_PROBLEM"] == (tick == 93)
    if radarless and frame % 20 == 0:
      path = decoder.vl["LKAS_HUD_2"]
      assert path["LEFT_LANE"] == path["RIGHT_LANE"] == (3 if tick % 4 < 2 else 0)
      assert bool(path["LANE_LENGTH"]) == (tick % 4 < 2)
