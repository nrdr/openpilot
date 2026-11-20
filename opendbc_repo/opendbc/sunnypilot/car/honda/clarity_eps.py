"""Clarity EPS calibration modes and angle mode (mode-switch / angle-loop EPS builds), ported from the night-star7
personal branch (2026-11-16..18). The EPS firmware: rwd-xray lab/clarity CLARITY_MODESW_MM_P2_20261116 (build 0x02),
CLARITY_ANGLE_MODE_20261117 (0x04), CLARITY_ANGLE_MODE_0x05_20261118 (0x05, software ID 39990+TRW+A020),
CLARITY_ANGLE_MODE_0x09_20261119 (0x09, same software ID).

0xE4 byte 3 standard (v1): bit 0 control type (0 torque, 1 angle); bits 3:1 mode slot: 0 stock, 1 CleanPTM (0x02),
2 P2 slot (0x04), 3 angle 4.0 m/s^2 (0x07), 4 angle 3.0 m/s^2 (0x09, build 0x05+); bits 7:4 reserved 0, except on the
authority build (0x09), where they are the angle loop's authority cut CUT (0 = full .. 15 = none). Stock and
older PTM firmware never read byte 3. Modes switch only at LKAS idle (252 ms).
0x6A4 EPS_CAL_STATUS (50 Hz, only these builds): requested / active mode, build ID, angle-loop state. openpilot sends an
angle payload only while the EPS reports the requested angle mode on a build that has it (EpsCalStatus.angle_ready).

Angle mode (steerControlType angle, startup setting, angle PTM ID 39990+TRW+A020 only): bytes 0-1 = -10 x target deg (0x14A STEER_ANGLE raw), byte 2 bit 5
with the request. The target is a rate- and acceleration-limited trajectory inside the EPS's jump/slew/lateral-accel
limits, starting at the wheel's angle and rate, its limits fading in over Override Fade Up; Steering Angle Rate Limit
caps it further. On builds 0x04/0x05 the request drops on every driver press. On the authority build the request stays
up through a press: the loop's authority drops to 0 at once (CUT 15), the sent target follows the wheel, and after the
release the target moves from the wheel to the plan with the engage fade while authority comes back over Override Fade Up.
"""
import numpy as np

from opendbc.car import DT_CTRL, structs
from opendbc.car.carlog import carlog
from opendbc.car.honda.values import CAR
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP

EPS_MODE_ANGLE = 3            # byte 3 bits 3:1
BYTE3_ANGLE = (EPS_MODE_ANGLE << 1) | 1
EPS_MODE_ANGLE_CAP3 = 4       # build 0x05: mode 4 = the same angle loop with a 3.0 m/s^2 clamp (byte 3 = 0x09)
CAP3_BUILDS = {0x05, 0x09}    # builds that have mode 4
AUTH_BUILDS = {0x09}          # builds with the angle-loop authority gain: 0xE4 byte 3 bits 7:4 = CUT (0 = full .. 15 = none)
AMAX_CAP3_SCALE = 3.0 / 4.0   # angle_ref AMAX4_SCALE: mode 4's clamp table = mode 3's x 0.75 (clamp angle is linear in a_lat)
ANGLE_PAYLOAD = 0x20          # byte 2 bit 5 (DBC SET_ME_X00 holds byte 2 bits 6:0)
RAW_PER_DEG = -10.0           # 0x14A STEER_ANGLE factor is -0.1

# EPS limits (angle_ref.py v3: JUMP, SLEW, AMAX), speed m/s
_V = [0., 5., 8., 10., 12., 15., 20., 25., 30.]
EPS_JUMP_DEG = [4.0, 4.0, 3.1, 2.5, 1.9, 1.0, 1.0, 1.0, 1.0]                     # per 10 ms
EPS_SLEW_DEG_S = [170.0, 170.0, 170.0, 143.9, 103.1, 69.7, 43.8, 31.8, 25.3]
ANGLE_STEP_DEG = [min(0.6 * j, 0.9 * s * DT_CTRL) for j, s in zip(EPS_JUMP_DEG, EPS_SLEW_DEG_S, strict=True)]
AMAX_V = [5., 8., 10., 12., 16., 20., 25., 30.]
EPS_AMAX_DEG = [379., 160., 109., 80.3, 50.0, 35.3, 25.7, 20.4]
ANGLE_MAX_FRAC = 0.95
# target trajectory (v2): rate and acceleration limits by speed, engage fade
_VT = [0., 5., 10., 15., 20., 30.]
TARGET_RATE_DEG_S = [150., 150., 100., 60., 40., 25.]
TARGET_ACCEL_DEG_S2 = [450., 600., 450., 300., 225., 180.]    # 1.5 x torque-mode hands-off p99 (11-15 route)
ENGAGE_S, ENGAGE_FLOOR = 1.5, 0.15    # limits ramp 15% -> 100% after the request rises; ENGAGE_S = default engage time
RAW_MAX = 32767


ANGLE_PTM_SEPARATOR = b"+"   # "39990+TRW+A020": the PTM 2.0 / angle PTM software ID ("-" stock, "," torque PTM)


def is_angle_ptm_id(fw_version: bytes) -> bool:
  """The angle PTM software ID: '+' in both separator slots (39990+TRW+A020)."""
  v = bytes(fw_version)
  return len(v) >= 10 and v[5:6] == ANGLE_PTM_SEPARATOR and v[9:10] == ANGLE_PTM_SEPARATOR


def apply_angle_mode(CP, CP_SP, requested: bool) -> None:
  """Startup choice (HondaCarConfig.clarity_angle_mode). Only a Clarity whose EPS reports the angle PTM ID
  (39990+TRW+A020, builds 0x05 on) can select angle mode; torque PTM ("," IDs) and every other car are untouched.
  At runtime the 0x6A4 interlock still gates the payload on the reported build and mode."""
  if requested and CP.carFingerprint == CAR.HONDA_CLARITY and CP_SP.flags & HondaFlagsSP.EPS_MODIFIED and \
     CP_SP.flags & HondaFlagsSP.EPS_ANGLE_PTM:
    CP_SP.flags |= HondaFlagsSP.CLARITY_ANGLE_MODE.value
    CP.steerControlType = structs.CarParams.SteerControlType.angle


def angle_mode(CP_SP) -> bool:
  return bool(CP_SP.flags & HondaFlagsSP.CLARITY_ANGLE_MODE)


def angle_limit(v_ego: float, amax_scale: float = 1.0) -> float:
  return ANGLE_MAX_FRAC * amax_scale * float(np.interp(v_ego, AMAX_V, EPS_AMAX_DEG))


def angle_to_raw(angle_deg: float) -> int:
  return int(max(-RAW_MAX, min(RAW_MAX, round(angle_deg * RAW_PER_DEG))))


class AngleModeSender:
  """Turns actuators.steeringAngleDeg into the 0xE4 angle payload. update() returns (raw, request, payload_bit)."""
  def __init__(self):
    self.apply_angle = 0.0
    self.apply_rate = 0.0
    self.active_frames = 0
    self.sent_active = False
    self.after_press = False  # authority build: after a press the fade uses POST_PRESS_FADE_S until the request drops

  def update(self, lat_active: bool, desired_deg: float, measured_deg: float, v_ego: float,
             angle_ready: bool, measured_rate_deg_s: float = 0.0, engage_s: float = ENGAGE_S,
             amax_scale: float = 1.0, rate_limit_deg_s: float = 0.0) -> tuple[int, bool, int]:
    active = bool(lat_active and angle_ready)
    if not active:
      self.apply_angle, self.apply_rate = float(measured_deg), float(measured_rate_deg_s)
      self.active_frames, self.sent_active, self.after_press = 0, False, False
      return 0, False, 0
    if self.after_press:                      # until the request drops: switching back mid-fade would shrink the limits
      engage_s = POST_PRESS_FADE_S
    lim = angle_limit(v_ego, amax_scale)    # amax_scale = AMAX_CAP3_SCALE while the EPS runs mode 4
    # clamp the target, not the output, so the output still moves along the limited trajectory (from a measured angle
    # above the clamp it walks down to it instead of jumping, which the EPS would reject)
    target = float(np.clip(float(desired_deg), -lim, lim))
    fade = 1.0 if engage_s <= 0.0 else min(1.0, ENGAGE_FLOOR + (1.0 - ENGAGE_FLOOR) * self.active_frames * DT_CTRL / engage_s)
    rate_cap = min(float(np.interp(v_ego, _VT, TARGET_RATE_DEG_S)), float(np.interp(v_ego, _V, ANGLE_STEP_DEG)) / DT_CTRL)
    if rate_limit_deg_s > 0.0:                # Steering Angle Rate Limit (Night Star / Galaxy), 0 = off
      rate_cap = min(rate_cap, rate_limit_deg_s)
    rate_max = fade * rate_cap
    accel_max = fade * float(np.interp(v_ego, _VT, TARGET_ACCEL_DEG_S2))
    err = target - self.apply_angle
    # exact discrete braking curve: the fastest rate from which the trajectory can still stop at the target with
    # accel_max per frame (the continuous sqrt(2*A*e) overshoots by a frame)
    ad = accel_max * DT_CTRL
    brake = ad * (((0.25 + 2.0 * abs(err) / (ad * DT_CTRL)) ** 0.5) - 0.5) if ad > 0 else 0.0
    rate_des = float(np.sign(err)) * min(rate_max, brake, abs(err) / DT_CTRL)
    self.apply_rate += float(np.clip(rate_des - self.apply_rate, -accel_max * DT_CTRL, accel_max * DT_CTRL))
    # rate_max shapes rate_des only, so a wheel already turning faster at engage eases down at accel_max instead of being
    # stopped in one frame; the EPS's own per-frame jump limit stays a hard bound
    step_rate = float(np.interp(v_ego, _V, ANGLE_STEP_DEG)) / DT_CTRL
    self.apply_rate = float(np.clip(self.apply_rate, -step_rate, step_rate))
    self.apply_angle += self.apply_rate * DT_CTRL
    self.active_frames += 1
    self.sent_active = True
    return angle_to_raw(self.apply_angle), True, ANGLE_PAYLOAD

  def follow(self, measured_deg: float, measured_rate_deg_s: float, v_ego: float) -> tuple[int, bool, int]:
    """Authority build, driver pressing: the target follows the wheel (at most the EPS per-frame jump limit) instead of
    the plan, and the trajectory restarts there with the wheel's rate and the engage fade, like a fresh engage. Holding
    the plan target instead pulled the wheel toward a target the driver was leaving and left it 28 deg (p90 82) away at
    release (route 000000ed)."""
    step = float(np.interp(v_ego, _V, ANGLE_STEP_DEG))
    self.apply_angle += float(np.clip(float(measured_deg) - self.apply_angle, -step, step))
    self.apply_rate, self.active_frames, self.sent_active, self.after_press = float(measured_rate_deg_s), 0, True, True
    return angle_to_raw(self.apply_angle), True, ANGLE_PAYLOAD


# After a press on the authority build both the target hand-back and the authority come back over this fixed time, not
# Override Fade Up (locked in angle mode, 1-2 s): the owner's car runs 0.5 s; ~1 s left the wheel lagging the model after
# a mid-turn release (route 000000ed). Fresh engages keep Override Fade Up.
POST_PRESS_FADE_S = 0.5


class AuthorityRamp:
  """Authority build: the angle loop's authority g (0..1) -> CUT = round(15 (1 - g)) for 0xE4 byte 3 bits 7:4. While the
  driver presses, g drops to 0 at once: the stock EPS latches LKAS off for ~2 s when the LKAS command stays above 44
  during a driver override, so the loop's output must fall below that, and a slower fade pulled the wheel toward center
  under the driver's hands (route 000000ed). After a release g climbs back over POST_PRESS_FADE_S, on a fresh engage
  over Override Fade Up (instantly when 0). The EPS slews its own gain toward CUT (build 0x09: 0 -> full in 0.34 s) and
  resets it to 0 whenever the loop activates."""
  def __init__(self):
    self.g = 0.0
    self.after_press = False

  def update(self, active: bool, pressed: bool, fade_up_s: float) -> int:
    if not active:
      self.g, self.after_press = 0.0, False
    elif pressed:
      self.g, self.after_press = 0.0, True
    else:
      ramp_s = POST_PRESS_FADE_S if self.after_press else fade_up_s
      self.g = min(1.0, self.g + DT_CTRL / ramp_s) if ramp_s > 0.0 else 1.0
      if self.g >= 1.0:
        self.after_press = False
    return int(round(15.0 * (1.0 - self.g)))


# build ID (0x6A4 byte 1) -> modes built in (bit k = mode k). The ID also fixes the frame layout. Each build's README
# records ID <-> bin/rwd sha256.
KNOWN_BUILDS = {
  # 20261119, ID 39990+TRW+A020 (bin f8d6aee3, rwd 6fef0b9c): 0x05 + angle-loop authority gain (CUT in byte 3 bits 7:4,
  # slews 0 -> full in 0.34 s, drops instantly) + stale window 32 -> 100 ms
  0x09: 0b11111,
  0x05: 0b11111,  # angle 3.0 profile 20261118, ID 39990+TRW+A020 (bin b4f5970d, rwd 1fbf3b63): 0x04's 0-3, 4 = 3.0 m/s^2 clamp
  0x04: 0b1111,  # angle mode 20261118 layout v3 (bin d884e27f, rwd bb4ff1b3): MM 0x02's 0-2, 3 = angle loop (CleanPTM tables, A280 flat)
  # MM 20261116 layout v2 (bin 2382007c, rwd a173fd71; 11-17 fixes: 252 ms switch debounce, IMASK 10 copy, no reload while
  # engaged): 0 stock, 1 CleanPTM, 2 P2 slot (= CleanPTM for now)
  0x02: 0b111,
}
ANGLE_BUILDS = {0x04, 0x05, 0x09}   # builds with the in-EPS angle loop (0x6A4 layout v3)
STATUS_TIMEOUT_FRAMES = 50   # carState updates (100 Hz): 0.5 s, 25 periods of the 50 Hz frame
MSG = "EPS_CAL_STATUS"


def requested_eps_mode(CP, CP_SP) -> int:
  """The calibration mode openpilot asks for in 0xE4 byte 3: 3 in angle mode, 1 (CleanPTM) on any other modified-EPS
  Clarity, else 0 (byte 3 untouched)."""
  if angle_mode(CP_SP):
    return EPS_MODE_ANGLE
  return 1 if (CP_SP.flags & HondaFlagsSP.EPS_MODIFIED and CP.carFingerprint == CAR.HONDA_CLARITY) else 0


class EpsCalStatus:
  def __init__(self, CP, CP_SP):
    self.requested = requested_eps_mode(CP, CP_SP)
    self.enabled = self.requested != 0
    self.angle = self.requested == EPS_MODE_ANGLE   # angle mode chosen at startup; the mode (3 or 4) can follow set_angle_profile
    self.announced = False      # a valid 0x6A4 seen since start: this EPS is switch-capable
    self.frames_since = 0
    self.last_ts = 0
    self.active_mode = -1
    self.build_id = -1
    self.fault = ""             # "" = OK, else the reason
    # layout v3 (angle builds): the EPS angle loop's own view, for logging
    self.loop_running = False
    self.angle_fault_why = 0    # 1 jump, 2 stale, 3 angle invalid
    self.angle_ref_deg = 0.0
    self.angle_out = 0

  def update(self, cp) -> str:
    if not self.enabled:
      return ""
    ts = cp.ts_nanos[MSG]["COUNTER"]
    if ts and ts != self.last_ts:
      self.last_ts, self.frames_since, self.announced = ts, 0, True
    else:
      self.frames_since += 1
    if self.announced:
      fault = self._check(cp.vl[MSG])
    else:
      fault = "no_status" if self.angle else ""
    if fault != self.fault:
      carlog.warning(f"EPS_CAL_STATUS: {fault or 'ok'} (active mode {self.active_mode}, requested {self.requested}, build {self.build_id:#04x})")
      self.fault = fault
    return fault

  def _check(self, vl) -> str:
    if self.frames_since > STATUS_TIMEOUT_FRAMES:
      return "lost"
    self.active_mode, self.build_id = int(vl["ACTIVE_MODE"]), int(vl["BUILD_ID"])
    caps = KNOWN_BUILDS.get(self.build_id)
    if caps is None:
      return "unknown_build"
    if not (caps >> self.requested) & 1:
      return "mode_not_built"
    if self.active_mode != self.requested:
      return "inactive_mode"
    if self.angle:
      if self.build_id not in ANGLE_BUILDS:
        return "no_angle_loop"
      self.loop_running = bool(vl["ANGLE_LOOP_RUNNING"])
      self.angle_fault_why = int(vl["ANGLE_FAULT_WHY"])
      self.angle_ref_deg, self.angle_out = float(vl["ANGLE_REF"]), int(vl["ANGLE_OUT"])
      if vl["ANGLE_FAULT"]:
        return "angle_fault"
    return ""

  def set_angle_profile(self, cap3: bool) -> None:
    """Angle mode: request mode 4 (3.0 m/s^2) only once the EPS has reported a build that has it, else mode 3. The EPS
    switches at the next LKAS idle; until it reports the new mode, _check faults inactive_mode and no angle is sent."""
    if self.angle:
      self.requested = EPS_MODE_ANGLE_CAP3 if (cap3 and self.build_id in CAP3_BUILDS) else EPS_MODE_ANGLE

  @property
  def cap3_active(self) -> bool:
    return self.angle and self.requested == EPS_MODE_ANGLE_CAP3

  @property
  def authority_ready(self) -> bool:
    """Angle mode is ready on the authority build: hold the request through a press and send CUT in byte 3 bits 7:4."""
    return self.angle_ready and self.build_id in AUTH_BUILDS

  @property
  def angle_ready(self) -> bool:
    """Angle mode only: the EPS runs the angle loop's mode on an angle build, reports no fault, and is not lost."""
    return self.angle and self.announced and self.fault == ""
