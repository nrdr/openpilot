"""Clarity mode-switch / angle-loop EPS (clarity_eps.py): 0xE4 byte 3 mode request, the 0x6A4 interlock, angle mode,
the 3.0 m/s^2 profile (build 0x05) and the 39990+TRW+A020 software ID."""
from dataclasses import replace

import numpy as np
import pytest

from opendbc.can import CANPacker
from opendbc.car import gen_empty_fingerprint, structs
from opendbc.car.honda.interface import CarInterface
from opendbc.car.honda.values import CAR
from opendbc.sunnypilot.car.honda import clarity_eps as ce
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from opendbc.sunnypilot.car.interfaces import setup_interfaces
from opendbc.sunnypilot.car.tests.runtime_config import make_test_car_config, with_honda_config

PTM = b"39990-TRW,A020\x00\x00"
PTM2 = b"39990+TRW+A020\x00\x00"
STOCK = b"39990-TRW-A020\x00\x00"
DBC = "honda_clarity_hybrid_2018_can_generated"


def clarity(fw=PTM, angle=False, **live):
  config = with_honda_config(make_test_car_config(), clarity_angle_mode=angle)
  live = {"override_fade_up_s": 0.0, **live}
  config.honda.provider.live_tuning = replace(config.honda.provider.live_tuning, steer_delta_limiter_enabled=False,
                                            live_learning_gas=False, **live)
  car_fw = [structs.CarParams.CarFw(ecu="eps", fwVersion=fw, address=0x18DA30F1)]
  fp = gen_empty_fingerprint()
  cp = CarInterface.get_params(CAR.HONDA_CLARITY, fp, car_fw, False, False, False, interface_config=config)
  sp = CarInterface.get_params_sp(cp, CAR.HONDA_CLARITY, fp, car_fw, False, False, False)
  setup_interfaces(CarInterface, cp, sp, config)
  ci = CarInterface(cp, sp, config)
  ci.update([])
  return ci


class Feed:
  def __init__(self, ci):
    self.ci, self.t, self.n = ci, 1_000_000_000, 0
    self.packer = CANPacker(DBC)

  def status(self, active=3, requested=3, build=0x04, running=True, fault=0, why=0):
    vals = {"REQUESTED_MODE": requested, "ACTIVE_MODE": active, "ANGLE_LOOP_RUNNING": int(running), "BUILD_ID": build,
            "ANGLE_FAULT": fault, "ANGLE_FAULT_WHY": why, "ANGLE_TARGET_HELD": int(running), "ANGLE_LOOP_ACTIVE": int(running),
            "COUNTER": self.n % 4}
    self.n += 1
    return self.packer.make_can_msg("EPS_CAL_STATUS", 0, vals)

  def run(self, k, **kw):
    for _ in range(k):
      self.t += 10_000_000
      addr, dat, bus = self.status(**kw)
      self.ci.update([(self.t, [(addr, dat, bus)])])
      self.t += 10_000_000
      self.ci.update([(self.t, [])])


_CLOCK = [2_000_000_000]


def e4(ci, lat, angle_des=0.0, measured=0.0, v=10.0, pressed=False, torque=0.0, t=None):
  t = _CLOCK if t is None else t
  ci.CS.out.vEgo = v
  ci.CS.out.steeringAngleDeg = measured
  ci.CS.out.steeringRateDeg = 0.0
  ci.CS.out.steeringPressed = pressed
  ci.CS.steer_control_active = True
  cc = structs.CarControl(enabled=lat, latActive=lat)
  cc.actuators.steeringAngleDeg = angle_des
  cc.actuators.torque = torque
  t[0] += 10_000_000
  out, msgs = ci.apply(cc.as_reader(), structs.CarControlSP(), t[0])
  f = [bytes(d) for a, d, _ in msgs if a == 0xE4]
  assert len(f) == 1
  return out, f[0]


# --- torque mode: byte 3 request, firmware recognition ---

@pytest.mark.parametrize("fw,byte3", [(PTM, 0x02), (PTM2, 0x02), (STOCK, 0x00)])
def test_torque_mode_byte3(fw, byte3):
  ci = clarity(fw)
  _, d = e4(ci, True, torque=0.1)
  assert d[3] == byte3 and not d[2] & 0x20


def test_ptm2_id_is_a_modified_clarity_like_ptm():
  a, b = clarity(PTM2), clarity(PTM)
  assert a.CP_SP.flags & HondaFlagsSP.EPS_MODIFIED and b.CP_SP.flags & HondaFlagsSP.EPS_MODIFIED
  assert list(a.CP.lateralParams.torqueBP) == list(b.CP.lateralParams.torqueBP)


def test_torque_mode_without_status_frame_is_ok_and_wrong_mode_faults():
  ci = clarity(PTM)
  f = Feed(ci)
  for _ in range(20):
    f.t += 10_000_000
    ci.update([(f.t, [])])
  assert ci.CS.eps_cal_status.fault == ""                                  # stock/CleanPTM/P1 send no 0x6A4: fine
  f.run(8, active=0, requested=1, build=0x02, running=False)
  assert ci.CS.eps_cal_status.fault == "inactive_mode"                     # mode switch pending: steer fault
  f.run(8, active=1, requested=1, build=0x02, running=False)
  assert ci.CS.eps_cal_status.fault == ""


# --- angle mode ---

def test_angle_mode_setting_selects_angle_on_the_angle_ptm_id_only():
  ci = clarity(PTM2, angle=True)
  assert ci.CP_SP.flags & HondaFlagsSP.CLARITY_ANGLE_MODE and ci.CP.steerControlType == structs.CarParams.SteerControlType.angle
  for fw in (STOCK, PTM):                                                 # stock and torque PTM ("," IDs): no angle mode
    ci = clarity(fw, angle=True)
    assert not ci.CP_SP.flags & HondaFlagsSP.CLARITY_ANGLE_MODE and ci.CP.steerControlType != structs.CarParams.SteerControlType.angle
  off = clarity(PTM2, angle=False)
  assert off.CP.steerControlType != structs.CarParams.SteerControlType.angle


@pytest.mark.parametrize("fw,ok", [(PTM2, True), (PTM, False), (STOCK, False), (b"39990+TRW,A020\x00\x00", False),
                                   (b"39990,TRW+A020\x00\x00", False), (b"", False)])
def test_angle_ptm_id_needs_plus_in_both_slots(fw, ok):
  assert ce.is_angle_ptm_id(fw) == ok
  if fw:
    assert bool(clarity(fw).CP_SP.flags & HondaFlagsSP.EPS_ANGLE_PTM) == ok


def test_torque_ptm_with_angle_setting_stays_a_torque_car():
  ci = clarity(PTM, angle=True)
  _, d = e4(ci, True, torque=0.1)
  assert d[3] == 0x02


def test_no_angle_payload_until_the_eps_reports_the_angle_mode():
  ci = clarity(PTM2, angle=True)
  for _ in range(30):                                                     # no 0x6A4 at all (stock/CleanPTM/P1 firmware)
    _, d = e4(ci, True, 20.0)
    assert d[0:3] == bytes(3) and d[3] == 0x07
  f = Feed(ci)
  f.run(8, build=0x02, active=1, requested=3, running=False)              # MM 0x02: no angle loop
  _, d = e4(ci, True, 20.0)
  assert d[0:3] == bytes(3) and not ci.CS.eps_cal_status.angle_ready


def test_angle_payload_ramps_from_the_wheel_and_drops_on_press():
  ci = clarity(PTM2, angle=True, override_fade_up_s=1.5)                   # Override Fade Up = the angle engage fade
  Feed(ci).run(8)                                                         # build 0x04, mode 3
  assert ci.CS.eps_cal_status.angle_ready
  e4(ci, False, 0.0, 5.0)
  ang = []
  for _ in range(300):
    out, d = e4(ci, True, 25.0, 5.0)
    assert d[2] == 0xA0 and d[3] == 0x07
    ang.append(int.from_bytes(d[0:2], "big", signed=True) / ce.RAW_PER_DEG)
  assert ang[0] == pytest.approx(5.0, abs=0.051) and max(np.diff(ang[:10])) <= 0.11 and ang[-1] == pytest.approx(25.0, abs=0.051)
  assert out.steeringAngleDeg == pytest.approx(25.0, abs=0.06) and out.torque == 0.0
  for _ in range(20):
    _, d = e4(ci, True, 25.0, 0.0, pressed=True)
    assert d[0:3] == bytes(3) and d[3] == 0x07


def test_angle_fault_stops_the_payload():
  ci = clarity(PTM2, angle=True)
  f = Feed(ci)
  f.run(8)
  e4(ci, True, 5.0)
  f.run(2, fault=1, why=2)
  assert ci.CS.eps_cal_status.fault == "angle_fault"
  _, d = e4(ci, True, 5.0)
  assert d[0:3] == bytes(3)


def test_cap3_profile_on_build_05_only():
  ci = clarity(PTM2, angle=True, clarity_angle_cap3=True)
  f = Feed(ci)
  f.run(4, build=0x05, active=3, requested=3)
  _, d = e4(ci, False)
  assert d[3] == 0x09 and ci.CS.eps_cal_status.requested == 4             # build 0x05 known, lateral off: switch
  f.run(4, build=0x05, active=4, requested=4)
  assert ci.CS.eps_cal_status.cap3_active and ci.CS.eps_cal_status.angle_ready
  for _ in range(3000):
    _, d = e4(ci, True, 600.0, v=12.0)
  a = int.from_bytes(d[0:2], "big", signed=True) / ce.RAW_PER_DEG
  assert a == pytest.approx(ce.angle_limit(12.0, ce.AMAX_CAP3_SCALE), abs=0.06)
  old = clarity(PTM2, angle=True, clarity_angle_cap3=True)
  Feed(old).run(8)                                                        # build 0x04: stays mode 3
  _, d = e4(old, False)
  assert d[3] == 0x07


def test_angle_rate_limit_setting_caps_the_target():
  ci = clarity(PTM2, angle=True, angle_rate_limit_deg_s=40.0)
  Feed(ci).run(8)
  e4(ci, False, v=5.0)
  prev, w = 0.0, []
  for _ in range(400):
    e4(ci, True, 300.0, v=5.0)
    w.append(abs(ci.CC.angle_sender.apply_angle - prev) / 0.01)
    prev = ci.CC.angle_sender.apply_angle
  assert max(w) <= 40.0 + 1e-6 and max(w) > 0.99 * 40.0


@pytest.mark.parametrize("v", [2.0, 8.0, 15.0, 30.0])
def test_sender_rate_and_acceleration_limits(v):
  s = ce.AngleModeSender()
  s.update(False, 0.0, 0.0, v, True)
  pa = pw = 0.0
  w, a = [], []
  for k in range(600):
    s.update(True, 60.0 * np.sign(np.sin(k / 40.0)), 0.0, v, True, engage_s=0.0)
    w.append((s.apply_angle - pa) / 0.01)
    a.append((w[-1] - pw) / 0.01)
    pa, pw = s.apply_angle, w[-1]
  assert max(map(abs, w)) <= float(np.interp(v, ce._VT, ce.TARGET_RATE_DEG_S)) + 1e-6
  assert max(map(abs, a)) <= float(np.interp(v, ce._VT, ce.TARGET_ACCEL_DEG_S2)) + 1e-6


# --- authority build (0x09): hold through a press, authority CUT in byte 3 bits 7:4 ---

def _deg(d):
  return int.from_bytes(d[0:2], "big", signed=True) / ce.RAW_PER_DEG


def test_authority_build_holds_through_a_press_and_follows_the_wheel():
  ci = clarity(PTM2, angle=True, override_fade_up_s=2.0)                  # nrdr's angle-mode default; release still 0.5 s
  Feed(ci).run(8, build=0x09)
  assert ci.CS.eps_cal_status.angle_ready and ci.CS.eps_cal_status.authority_ready
  _, d = e4(ci, False, 0.0, 0.0)
  assert d[3] == 0x07                                                     # lateral off: no CUT
  eng = [e4(ci, True, 10.0, 0.0)[1] for _ in range(220)]
  assert eng[0][3] == 0xF7 and eng[-1][3] == 0x07                         # every engage starts at zero authority
  assert [d[3] >> 4 for d in eng] == sorted((d[3] >> 4 for d in eng), reverse=True)
  press = [e4(ci, True, 10.0, -5.0, pressed=True)[1] for _ in range(60)]
  assert press[0][3] == 0xF7 and all(d[2] == 0xA0 and d[3] == 0xF7 for d in press)   # request held, authority 0 at once
  assert _deg(press[-1]) == pytest.approx(-5.0, abs=0.051)                # target follows the wheel
  rel = [e4(ci, True, 10.0, -5.0)[1] for _ in range(60)]
  assert abs(_deg(rel[0]) + 5.0) < 0.2                                    # release starts from the wheel
  assert all(_deg(b) >= _deg(a) - 1e-9 for a, b in zip(rel, rel[1:], strict=False)) and _deg(rel[-1]) > 0.0
  assert rel[-1][3] == 0x07 and [d[3] >> 4 for d in rel] == sorted((d[3] >> 4 for d in rel), reverse=True)   # back in 0.5 s
  more = [_deg(e4(ci, True, 10.0, -5.0)[1]) for _ in range(100)]          # no overshoot once the release fade is done
  assert max(more) <= 10.0 + 0.051 and more[-1] == pytest.approx(10.0, abs=0.051)


@pytest.mark.parametrize("build", [0x04, 0x05])
def test_older_angle_builds_drop_the_request_on_press_and_send_no_cut(build):
  ci = clarity(PTM2, angle=True)
  Feed(ci).run(8, build=build)
  assert not ci.CS.eps_cal_status.authority_ready
  e4(ci, False)
  assert all(e4(ci, True, 10.0)[1][3] == 0x07 for _ in range(30))
  _, d = e4(ci, True, 10.0, -5.0, pressed=True)
  assert d[0:3] == bytes(3) and d[3] == 0x07


def test_authority_ramp():
  r = ce.AuthorityRamp()
  assert r.update(False, False, 2.0) == 15
  up = [r.update(True, False, 2.0) for _ in range(220)]                   # fresh engage: Override Fade Up (2.0 s)
  assert up[-1] == 0 and next(i for i, c in enumerate(up) if c == 0) == pytest.approx(193, abs=2)   # CUT 0 from g > 29/30
  assert r.update(True, True, 2.0) == 15 and r.g == 0.0                   # a press: zero at once
  rel = [r.update(True, False, 2.0) for _ in range(60)]                   # after a press: POST_PRESS_FADE_S (0.5 s)
  assert next(i for i, c in enumerate(rel) if c == 0) == pytest.approx(49, abs=2)
  assert r.update(False, False, 0.0) == 15 and r.update(True, False, 0.0) == 0   # Fade Up 0: full at once on engage


def test_cap3_profile_on_build_09():
  ci = clarity(PTM2, angle=True, clarity_angle_cap3=True)
  f = Feed(ci)
  f.run(4, build=0x09, active=3, requested=3)
  _, d = e4(ci, False)
  assert d[3] == 0x09 and ci.CS.eps_cal_status.requested == 4
  f.run(4, build=0x09, active=4, requested=4)
  assert ci.CS.eps_cal_status.cap3_active and ci.CS.eps_cal_status.authority_ready


@pytest.mark.parametrize("build", [0x06, 0x07, 0x08])
def test_unreleased_builds_fault(build):
  ci = clarity(PTM2, angle=True)
  Feed(ci).run(8, build=build)                                            # 0x06-0x08 were experiments, not supported here
  assert ci.CS.eps_cal_status.fault == "unknown_build" and not ci.CS.eps_cal_status.angle_ready
