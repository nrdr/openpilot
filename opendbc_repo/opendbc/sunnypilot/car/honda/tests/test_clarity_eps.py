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


@pytest.mark.parametrize("build", [0x09, 0x0A])
def test_authority_build_holds_through_a_press_on_the_plan(build):
  ci = clarity(PTM2, angle=True, override_fade_up_s=2.0)                  # nrdr's angle-mode default; release uses POST_PRESS_AUTH_S
  Feed(ci).run(8, build=build)
  assert ci.CS.eps_cal_status.angle_ready and ci.CS.eps_cal_status.authority_ready
  _, d = e4(ci, False, 0.0, 0.0)
  assert d[3] == 0x07                                                     # lateral off: no CUT
  eng = [e4(ci, True, 10.0, 0.0)[1] for _ in range(220)]
  assert eng[0][3] == 0xF7 and eng[-1][3] == 0x07                         # every engage starts at zero authority
  assert [d[3] >> 4 for d in eng] == sorted((d[3] >> 4 for d in eng), reverse=True)
  plan = _deg(eng[-1])
  assert plan == pytest.approx(10.0, abs=0.051)
  press = [e4(ci, True, 10.0, -5.0, pressed=True)[1] for _ in range(60)]
  assert press[0][3] == 0xF7 and all(d[2] == 0xA0 and d[3] == 0xF7 for d in press)   # request held, authority 0 at once
  assert all(_deg(d) == pytest.approx(plan, abs=0.051) for d in press)    # the target stays on the plan (Hyundai/Kia style)
  rel = [e4(ci, True, 10.0, -5.0)[1] for _ in range(130)]
  assert all(_deg(d) == pytest.approx(plan, abs=0.051) for d in rel)      # release: the target does not move; authority returns
  cut = [d[3] >> 4 for d in rel]
  assert cut == sorted(cut, reverse=True) and rel[-1][3] == 0x07          # authority back over POST_PRESS_AUTH_S (1.25 s)
  assert next(i for i, c in enumerate(cut) if c == 0) == pytest.approx(121, abs=2)
  assert not hasattr(ce.AngleModeSender, "follow")


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
  rel = [r.update(True, False, 2.0) for _ in range(130)]                  # after a press: POST_PRESS_AUTH_S (1.25 s)
  assert next(i for i, c in enumerate(rel) if c == 0) == pytest.approx(121, abs=2)
  assert r.update(False, False, 0.0) == 15 and r.update(True, False, 0.0) == 0   # Fade Up 0: full at once on engage


@pytest.mark.parametrize("build", [0x09, 0x0A])
def test_cap3_profile_on_authority_builds(build):
  ci = clarity(PTM2, angle=True, clarity_angle_cap3=True)
  f = Feed(ci)
  f.run(4, build=build, active=3, requested=3)
  _, d = e4(ci, False)
  assert d[3] == 0x09 and ci.CS.eps_cal_status.requested == 4
  f.run(4, build=build, active=4, requested=4)
  assert ci.CS.eps_cal_status.cap3_active and ci.CS.eps_cal_status.authority_ready


@pytest.mark.parametrize("build", [0x06, 0x07, 0x08])
def test_unreleased_builds_fault(build):
  ci = clarity(PTM2, angle=True)
  Feed(ci).run(8, build=build)                                            # 0x06-0x08 were experiments, not supported here
  assert ci.CS.eps_cal_status.fault == "unknown_build" and not ci.CS.eps_cal_status.angle_ready


# --- protocol v2 (build 0x0B): 0x6A4 layout 4, byte 3 = MODE 1 | AUTH ---

class FeedV2(Feed):
  """0x6A4 layout 4 through the layout-3 DBC signals of the same bytes (as clarity_eps.decode_layout4 reads them)."""
  def status_v4(self, mode=1, steering=True, fault=False, clamp=False, lkas=2, build=0x0B, reason=0):
    vals = {"REQUESTED_MODE": 0x8 | (0x4 if fault else 0) | (0x2 if steering else 0) | (0x1 if clamp else 0),
            "ANGLE_LOOP_RUNNING": (lkas >> 1) & 1, "ACTIVE_MODE": ((lkas & 1) << 2) | (mode & 3), "BUILD_ID": build,
            "ANGLE_TARGET_HELD": (reason >> 3) & 1, "ANGLE_FAULT_WHY": (reason >> 1) & 3, "ANGLE_FAULT": reason & 1,
            "COUNTER": self.n % 4}
    self.n += 1
    return self.packer.make_can_msg("EPS_CAL_STATUS", 0, vals)

  def run_v4(self, k, **kw):
    for _ in range(k):
      self.t += 10_000_000
      addr, dat, bus = self.status_v4(**kw)
      self.ci.update([(self.t, [(addr, dat, bus)])])
      self.t += 10_000_000
      self.ci.update([(self.t, [])])


def v2_car(**live):
  ci = clarity(PTM2, angle=True, **live)
  f = FeedV2(ci)
  f.run_v4(8)
  return ci, f


def test_byte3_codecs():
  assert ce.byte3_v1(3, 0) == 0x07 and ce.byte3_v1(4, 15) == 0xF9
  assert ce.byte3_v2(0) == 0xF1 and ce.byte3_v2(15) == 0x01            # AUTH = 15 - CUT: CUT 0 (full) -> AUTH 15
  for cut in range(16):
    b3 = ce.byte3_v2(cut)
    assert b3 & 0x3 == 1 and (b3 >> 2) & 0x3 == 0 and b3 >> 4 == 15 - cut


def test_v2_status_is_detected_and_decoded():
  ci = clarity(PTM2, angle=True)
  FeedV2(ci).run_v4(8, clamp=True, reason=7)
  s = ci.CS.eps_cal_status
  assert s.protocol == 2 and s.build_id == 0x0B and s.active_mode == 1 and s.clamp and s.reason == "AUTHORITY_ZERO"
  assert s.fault == "" and s.angle_ready and s.authority_ready


def test_v2_engage_press_on_the_plan_and_release():
  ci, _ = v2_car(override_fade_up_s=2.0)
  _, idle = e4(ci, False, 0.0, 0.0, v=20.0)
  assert idle[0:3] == bytes(3) and idle[3] == 0xF1                       # idle: MODE 1 requested, AUTH 15, no payload
  eng = [e4(ci, True, 5.0, 0.0, v=20.0)[1] for _ in range(220)]
  assert all(d[2] == 0xA0 and d[3] & 0x0F == 0x01 for d in eng)          # request + payload, MODE 1, bits 3:2 zero
  assert eng[0][3] == 0x01 and eng[-1][3] == 0xF1                        # every engage starts at zero authority
  auths = [d[3] >> 4 for d in eng]
  assert auths == sorted(auths)
  press = [e4(ci, True, 5.0, -8.0, v=20.0, pressed=True)[1] for _ in range(80)]
  assert all(d[2] == 0xA0 and d[3] == 0x01 for d in press)               # request held, AUTH 0 at once
  plan = _deg(eng[-1])
  assert all(_deg(d) == pytest.approx(plan, abs=0.051) for d in press)   # the target stays on the plan through the press
  rel = [e4(ci, True, 5.0, -8.0, v=20.0)[1] for _ in range(160)]
  ra = [d[3] >> 4 for d in rel]
  assert ra == sorted(ra) and rel[-1][3] == 0xF1                         # authority back over POST_PRESS_AUTH_S


def test_v2_frames_follow_the_receiver_rules():
  # the spec's receiver rules: MODE 0/1 only, bits 3:2 zero, payload exactly when (MODE 1 and request)
  ci, _ = v2_car()
  frames = [e4(ci, False)[1]] + [e4(ci, True, 5.0)[1] for _ in range(50)] + [e4(ci, True, 5.0, -3.0, pressed=True)[1] for _ in range(20)]
  for d in frames:
    mode, reserved, request, payload = d[3] & 3, (d[3] >> 2) & 3, bool(d[2] & 0x80), bool(d[2] & 0x20)
    assert mode == 1 and reserved == 0 and payload == request


def test_v1_until_the_first_layout4_frame():
  ci = clarity(PTM2, angle=True)
  f = FeedV2(ci)
  f.run(8, build=0x0A)
  assert ci.CS.eps_cal_status.protocol == 1 and e4(ci, False)[1][3] == 0x07
  f.run_v4(4)
  assert ci.CS.eps_cal_status.protocol == 2 and e4(ci, False)[1][3] == 0xF1


def test_unknown_v2_build_never_steers():
  ci = clarity(PTM2, angle=True)
  FeedV2(ci).run_v4(8, build=0x0C)
  assert ci.CS.eps_cal_status.fault == "unknown_build"
  assert e4(ci, True, 5.0)[1][0:3] == bytes(3)


def test_v2_eps_not_in_angle_mode_waits():
  ci = clarity(PTM2, angle=True)
  f = FeedV2(ci)
  f.run_v4(8, mode=0, steering=False, reason=2)
  assert ci.CS.eps_cal_status.fault == "inactive_mode"
  _, d = e4(ci, True, 5.0)
  assert d[0:3] == bytes(3) and d[3] == 0xF1                             # asks for MODE 1 at idle, sends no payload
  f.run_v4(4)
  assert ci.CS.eps_cal_status.fault == ""


def test_v2_interlock_on_the_steering_bit_with_reason():
  ci, f = v2_car()
  e4(ci, False)
  e4(ci, True)
  f.run_v4(5, steering=False, reason=8, lkas=3)                          # 10 carState updates without STEERING
  assert ci.CS.eps_cal_status.fault == ""
  f.run_v4(1, steering=False, reason=8, lkas=3)
  assert ci.CS.eps_cal_status.fault == "loop_not_running (STOCK_LKAS_NOT_ENGAGED)"
  assert e4(ci, True)[1][0:3] == bytes(3)                                # the request drops
  f.run_v4(2)                                                            # the EPS steers again: the fault is still held,
  assert ci.CS.eps_cal_status.fault == "loop_not_running (STOCK_LKAS_NOT_ENGAGED)"   # with the reason it fired for
  f.run_v4(ce.LOOP_RETRY_FRAMES // 2 - 4)                                # 2 carState updates per status frame
  assert ci.CS.eps_cal_status.fault.startswith("loop_not_running")
  f.run_v4(2)
  assert ci.CS.eps_cal_status.fault == ""                                # 1 s after it fired the request may retry


def test_v2_interlock_never_flickers_when_the_eps_never_steers():
  # an EPS that never reports STEERING (stock LKAS locked out): the fault holds 1 s between retries instead of
  # toggling every 11 frames
  ci, f = v2_car()
  e4(ci, False)
  faults = []
  for _ in range(400):                                                   # 8 s: one 0xE4 and two carState updates per step
    e4(ci, True)
    f.run_v4(1, steering=False, reason=8, lkas=3)
    faults.append(ci.CS.eps_cal_status.fault != "")
  changes = sum(1 for a, b in zip(faults, faults[1:], strict=False) if a != b)
  # one retry cycle = 1 s held + 10 frames of request: about 2 changes per 1.1 s (without the hold: ~130 in 8 s)
  assert changes <= 16, changes
  assert sum(faults) >= 0.8 * len(faults)                                # and the fault is up nearly all the time


def test_v2_authority_zero_does_not_trip_the_interlock():
  ci, f = v2_car()
  e4(ci, False)
  for _ in range(40):
    e4(ci, True, 0.0, 0.0, pressed=True)
    f.run_v4(1, steering=True, reason=7)
  assert ci.CS.eps_cal_status.fault == ""


def test_v2_fault_bit_reports_its_reason():
  ci, f = v2_car()
  f.run_v4(2, steering=False, fault=True, reason=4)
  assert ci.CS.eps_cal_status.fault == "angle_fault (JUMP)" and not ci.CS.eps_cal_status.angle_ready


def test_v2_ignores_the_3_0_profile_setting():
  ci, f = v2_car(clarity_angle_cap3=True)
  e4(ci, False, v=15.0)
  f.run_v4(4)
  assert not ci.CS.eps_cal_status.cap3_active and ci.CS.eps_cal_status.fault == ""
  frames = [e4(ci, True, 80.0, 0.0, v=15.0)[1] for _ in range(300)]
  assert all(d[3] & 0x0F == 0x01 for d in frames)
  peak = max(abs(_deg(d)) for d in frames)
  assert peak == pytest.approx(ce.angle_limit(15.0), abs=0.06)           # one profile: panda's 3.6 m/s^2 angle


def test_v2_on_a_torque_mode_clarity_is_not_built():
  ci = clarity(PTM2, angle=False)
  FeedV2(ci).run_v4(8, mode=0, steering=False, reason=1)
  assert ci.CS.eps_cal_status.fault == "mode_not_built"


# --- panda: the angle bit and the sender's limits ---

def test_angle_mode_sets_the_panda_angle_bit_only_on_the_angle_ptm():
  from opendbc.sunnypilot.car.honda.values_ext import HondaSafetyFlagsSP
  bit = HondaSafetyFlagsSP.CLARITY_ANGLE
  assert clarity(PTM2, angle=True).CP_SP.safetyParam & bit
  assert not clarity(PTM2, angle=False).CP_SP.safetyParam & bit
  assert not clarity(PTM, angle=True).CP_SP.safetyParam & bit           # torque PTM: no angle mode, no bit
  assert not clarity(STOCK, angle=True).CP_SP.safetyParam & bit


def test_clarity_pedal_calibration_ignores_the_angle_bit():
  # clarity_braking.qualified compares the sunnypilot safety param exactly; the angle bit must not change its answer
  # (the same trap broke the pedal on the personal branch, fbf15b2cbb)
  from opendbc.car.honda import clarity_braking
  from opendbc.car.honda.values import HondaFlags
  from opendbc.sunnypilot.car.honda.values_ext import HondaSafetyFlagsSP
  CP = structs.CarParams(carFingerprint=CAR.HONDA_CLARITY, openpilotLongitudinalControl=True, pcmCruise=False, dashcamOnly=False,
                         flags=int(HondaFlags.NIDEC | HondaFlags.HYBRID))
  CP.safetyConfigs = [structs.CarParams.SafetyConfig(safetyModel=structs.CarParams.SafetyModel.hondaNidec, safetyParam=0)]
  base = HondaSafetyFlagsSP.NIDEC_HYBRID | HondaSafetyFlagsSP.GAS_INTERCEPTOR | HondaSafetyFlagsSP.CLARITY_INTERCEPTOR_BRAKE
  for sp, ok in ((base, True), (base | HondaSafetyFlagsSP.CLARITY_ANGLE, True), (base & ~HondaSafetyFlagsSP.GAS_INTERCEPTOR, False),
                 (base | HondaSafetyFlagsSP.STOCK_LONGITUDINAL, False)):
    CP_SP = structs.CarParamsSP(safetyParam=sp, enableGasInterceptor=True, flags=int(HondaFlagsSP.NIDEC_HYBRID))
    assert clarity_braking.qualified(CP, CP_SP) == ok, sp


@pytest.mark.parametrize("v", [2.0, 8.0, 15.0, 20.0, 30.0, 40.0])
def test_sender_stays_inside_the_panda_rule(v):
  # every sent angle within panda's 3.6 m/s^2 angle, every step within its jerk step, the first at the wheel; the hold
  # (request up, target on the plan) through a press that drags the wheel past the limit
  # panda's integer form (honda.h): |raw| <= int(lim x 10 + 1), |raw - last| <= int(step x 10 + 1), here at v (panda: v - 1,
  # which only widens both)
  s = ce.AngleModeSender()
  lim_can, step_can = int(ce.std_angle_limit(v) * 10 + 1), int(ce.std_angle_step(v) * 10 + 1)
  wheel, prev = 0.0, None
  for i in range(700):
    pressed = 200 <= i < 400
    wheel = wheel + 3.0 if pressed else wheel + 0.3 * (s.out_angle - wheel)
    raw, req, _ = s.update(True, 2.0 * ce.std_angle_limit(v) * (1 if (i // 150) % 2 == 0 else -1), wheel, v, True, 0.0, 0.0)
    if not req:
      prev = None
      continue
    assert abs(raw) <= lim_can, (v, i, raw)
    if prev is not None:
      assert abs(raw - prev) <= step_can, (v, i, raw, prev)
    prev = raw
