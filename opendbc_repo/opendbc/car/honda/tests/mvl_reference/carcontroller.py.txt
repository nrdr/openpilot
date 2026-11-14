import math
import threading
import time
from collections import deque
from queue import Empty, Queue

import numpy as np
from openpilot.common.params import Params
from opendbc.car.common.conversions import Conversions as CV

from opendbc.can import CANPacker
from opendbc.car import ACCELERATION_DUE_TO_GRAVITY, Bus, DT_CTRL, rate_limit, make_tester_present_msg, structs
from opendbc.car.honda import hondacan
from opendbc.car.honda.values import CAR, CruiseButtons, HondaFlags, CarControllerParams, CruiseSettings
from opendbc.car.interfaces import CarControllerBase
from opendbc.car.common.pid import PIDController
from opendbc.car.honda import lane_path
from opendbc.car.honda import hud_objects
from opendbc.car.honda.nidec_long_helpers import nidec_speed_lead_mps, nidec_speed_channel_pinned, nidec_set_speed_governed

from opendbc.sunnypilot.car.honda.mads import MadsCarController
from opendbc.sunnypilot.car.honda.gas_interceptor import GasInterceptorCarController
from opendbc.sunnypilot.car.honda.icbm import IntelligentCruiseButtonManagementInterface
from opendbc.sunnypilot.car.honda.eps_mod import EpsModCarController
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP

VisualAlert = structs.CarControl.HUDControl.VisualAlert
LongCtrlState = structs.CarControl.Actuators.LongControlState


def compute_gb_honda_bosch(accel, speed):
  # TODO returns 0s, is unused
  return 0.0, 0.0


def compute_gb_honda_nidec(accel, speed, creep_factor):
  creep_brake = 0.0
  creep_speed = 2.3
  creep_brake_value = 0.15
  if speed < creep_speed:
    creep_brake = (creep_speed - speed) / creep_speed * creep_brake_value
  gb = float(accel) / 4.8 - creep_brake * creep_factor
  creep_impact = -creep_brake
  return np.clip(-gb, 0.0, 1.0), creep_impact


def compute_gb_honda_interceptor(accel, speed):
  # gas/brake split for the pedal interceptor: gas from positive accel, brake from negative,
  # with the fixed creep brake (no learned creep_factor; this is the pre-0111-port behavior)
  creep_brake = 0.0
  creep_speed = 2.3
  creep_brake_value = 0.15
  if speed < creep_speed:
    creep_brake = (creep_speed - speed) / creep_speed * creep_brake_value
  gb = float(accel) / 4.8 - creep_brake
  return np.clip(gb, 0.0, 1.0), np.clip(-gb, 0.0, 1.0)


def compute_gas_brake(accel, speed, CP):
  if CP.flags & HondaFlags.BOSCH:
    return compute_gb_honda_bosch(accel, speed)
  else:
    # only reached with the gas interceptor; wire-gas Nidec uses compute_gb_honda_nidec directly
    return compute_gb_honda_interceptor(accel, speed)


# TODO not clear this does anything useful
def actuator_hysteresis(brake, braking, brake_steady):
  # hyst params
  brake_hyst_on = 0.02    # to activate brakes exceed this value
  brake_hyst_off = 0.005  # to deactivate brakes below this value
  brake_hyst_gap = 0.01   # don't change brake command for small oscillations within this value

  # *** hysteresis logic to avoid brake blinking. go above 0.1 to trigger
  if (brake < brake_hyst_on and not braking) or brake < brake_hyst_off:
    brake = 0.
  braking = brake > 0.

  # for small brake oscillations within brake_hyst_gap, don't change the brake command
  if brake == 0.:
    brake_steady = 0.
  elif brake > brake_steady + brake_hyst_gap:
    brake_steady = brake - brake_hyst_gap
  elif brake < brake_steady - brake_hyst_gap:
    brake_steady = brake + brake_hyst_gap
  brake = brake_steady

  return brake, braking, brake_steady


def brake_pump_hysteresis(apply_brake, apply_brake_last, last_pump_ts, ts):
  pump_on = False

  # reset pump timer if:
  # - there is an increment in brake request
  # - we are applying steady state brakes and we haven't been running the pump
  #   for more than 20s (to prevent pressure bleeding)
  if apply_brake > apply_brake_last or (ts - last_pump_ts > 20. and apply_brake > 0):
    last_pump_ts = ts

  # once the pump is on, run it for at least 0.2s
  if ts - last_pump_ts < 0.2 and apply_brake > 0:
    pump_on = True

  return pump_on, last_pump_ts


def process_hud_alert(hud_alert):
  alert_fcw = False
  alert_steer_required = False

  # Make sure FCW is prioritized over steering required
  # TODO: implement separate available LDW alert
  if hud_alert == VisualAlert.fcw:
    alert_fcw = True
  elif hud_alert in (VisualAlert.steerRequired, VisualAlert.ldw):
    alert_steer_required = True

  return alert_fcw, alert_steer_required


# Nidec multi-band gas/speed channels: the old two-band scheme (pure low band below 10 m/s,
# pure high band above 16 m/s, linear blend between) generalizes to piecewise-linear
# interpolation across these nodes. The gas channel gets extra nodes at 0/10/20/30 mph and
# the speed channel at 5/15/25/35 mph, offset from each other so the two channels don't
# equilibrate on exactly the same frames; the pre-existing low (10 m/s) and high (16 m/s)
# nodes keep their persisted values and param keys. Tuples are sorted by node speed (m/s).
NIDEC_GAS_BANDS = (
  ("00", 0.0),
  ("10", 10.0 * CV.MPH_TO_MS),
  ("20", 20.0 * CV.MPH_TO_MS),
  ("low", 10.0),
  ("30", 30.0 * CV.MPH_TO_MS),
  ("high", 16.0),
)
NIDEC_SPEED_BANDS = (
  ("05", 5.0 * CV.MPH_TO_MS),
  ("15", 15.0 * CV.MPH_TO_MS),
  ("low", 10.0),
  ("25", 25.0 * CV.MPH_TO_MS),
  ("35", 35.0 * CV.MPH_TO_MS),
  ("high", 16.0),
)

# the low/high nodes keep the param keys the two-band scheme persisted, so learned state survives
NIDEC_GAS_FACTOR_KEYS: dict[str, str] = {band: f"HondaGasFactor{band}Params" for band, _ in NIDEC_GAS_BANDS}
NIDEC_GAS_FACTOR_KEYS["low"] = "HondaGasFactorLowParams"
NIDEC_GAS_FACTOR_KEYS["high"] = "HondaGasFactorParams"
NIDEC_GAS_ALPHA_KEYS: dict[str, str] = {band: f"HondaGasAlpha{band}Params" for band, _ in NIDEC_GAS_BANDS}
NIDEC_GAS_ALPHA_KEYS["low"] = "HondaGasAlphaLowParams"
NIDEC_GAS_ALPHA_KEYS["high"] = "HondaGasAlphaParams"
NIDEC_SPEED_FACTOR_KEYS: dict[str, str] = {band: f"HondaSpeedFactor{band}Params" for band, _ in NIDEC_SPEED_BANDS}
NIDEC_SPEED_FACTOR_KEYS["low"] = "HondaSpeedFactorLowParams"
NIDEC_SPEED_FACTOR_KEYS["high"] = "HondaSpeedFactorParams"
NIDEC_SPEED_ALPHA_KEYS: dict[str, str] = {band: f"HondaSpeedAlpha{band}Params" for band, _ in NIDEC_SPEED_BANDS}
NIDEC_SPEED_ALPHA_KEYS["low"] = "HondaSpeedAlphaLowParams"
NIDEC_SPEED_ALPHA_KEYS["high"] = "HondaSpeedAlphaParams"

# Speed-channel learner backstops. These are plant-plausibility bounds, not tuning: a persisted
# value outside them is a poisoned learner state, not something a Nidec PCM can have taught us.
# The speed factor is m/s of PCM_SPEED lead per m/s2 of requested accel; the servo's dv gain
# was identified at 0.33-0.46 (m/s2)/(m/s) on the MDX (speedfactor 2.2-3.0), and a gain above
# 1 (m/s2)/(m/s), i.e. a factor below 1.0, is not a plausible comfort-tuned ACC servo.
# The upper bound is a loop-gain bound, not a plant bound: nidec_pid's integral correction rides
# the same factor onto the wire, so the error loop's gain is k_i * sf * dv_gain behind ~0.9 s of
# servo dead time, and an integral loop goes unstable at k_i*sf*gain*lag ~ pi/2. The CR-V 2015
# (route a6354c3dcf16e7cf/25: dv gain 0.14 small-signal, 0.08 large-signal, the weakest servo
# identified so far) needs a factor of ~7-12; with its persisted factor at 23-43 the highway hold
# loop (k_i 0.5) was past that bound and limit-cycled at ~6 s: every aEgo overshoot wound the
# integrator to -0.1..-0.25, which became -5..-10 m/s of lead, a 2-3 s fuel cut at -0.5 m/s2, and
# -17 kph in 30 s against a +0.1 m/s2 plan. 16 keeps that loop inside the bound for a 0.14 gain
# (1.0 rad) and leaves headroom above the weakest measured plant; it binds only on poison.
NIDEC_SPEED_FACTOR_DEFAULT = 4.0
NIDEC_SPEED_FACTOR_MIN = 1.0
NIDEC_SPEED_FACTOR_MAX = 16.0
# zero-accel servo offset, m/s; measured -0.18..+0.46 per speed band on the MDX
NIDEC_SPEED_ALPHA_MAX = 1.5
# speed-channel ceiling, m/s2; every Nidec PCM sustains at least this on its speed channel
# (stock ramps run +0.5..0.8 m/s2), so a lower value is a collapsed learner, not a measurement
NIDEC_SAT_ACCEL_DEFAULT = 0.9
NIDEC_SAT_ACCEL_MIN = 0.3
# derived knee bounds, m/s of lead. Below DV_SAT_MIN the servo is never treated as saturated:
# stock itself launches with a 2.8 m/s lead and the MDX's linear band extends to ~2.5 m/s, so
# an undershoot with less lead than that is speedfactor's information, not the ceiling's.
# Beyond DV_SAT_MAX the lead is provably past servo response (marginal dv gain 0.009 in the
# 30-90 m/s band, route 1d7), so surplus lead there is bled regardless of what sat_accel says.
NIDEC_DV_SAT_MIN = 2.5
NIDEC_DV_SAT_MAX = 10.0
# The speed-channel learners compare aEgo against the command the servo is answering NOW, i.e. the
# one sent a servo lag ago (~1 s on the MDX and Pilot logs), not the current one. Learning against
# the current command bills the first second of every step-up (aEgo still at the old level, error
# = the whole step, weight = the new command) to speedfactor as growth: on a car whose ceiling is
# above what the planner asks (so the knee ratchet never engages) that is ~+9% per pull with
# nothing to balance it, and speedfactor rides to the DV_SAT_MAX bleed and sits there (bench: a
# second stable point at ~3x the true factor, reached from any high start). Under-estimating the
# lag leaves some of that; over-estimating it bills ramp-downs as growth instead, so 0.9 s is
# taken from the logs rather than rounded up.
NIDEC_SERVO_LAG_FRAMES = 90
# aEgo is ~0.06 m/s2 white per frame on the Pilot. The ceiling gates need a settled level, not
# a sample: a consecutive-frame counter on raw aEgo cannot hold across 150 frames unless the
# margin is several sigma, which is what left a too-high ceiling unfalsifiable (0.1 m/s2 short
# of the planner's max is a 1.6-sigma margin). One-pole filter, ~0.2 s.
NIDEC_AEGO_FILTER_ALPHA = 0.05


def band_weights(bands, v_ego):
  # hat-function weights of piecewise-linear interpolation across the band nodes: exactly the
  # two nodes bracketing v_ego get nonzero weight (summing to 1), and outside the grid the edge
  # node gets all of it. These weights blend the per-band values into the sent target and gate
  # how much each band learns from a frame, generalizing the old low_w/(1-low_w) two-band split.
  weights = {band: 0.0 for band, _ in bands}
  if v_ego <= bands[0][1]:
    weights[bands[0][0]] = 1.0
  elif v_ego >= bands[-1][1]:
    weights[bands[-1][0]] = 1.0
  else:
    for (band_lo, spd_lo), (band_hi, spd_hi) in zip(bands[:-1], bands[1:], strict=True):
      if spd_lo <= v_ego <= spd_hi:
        frac = (v_ego - spd_lo) / (spd_hi - spd_lo)
        weights[band_lo] = 1.0 - frac
        weights[band_hi] = frac
        break
  return weights


class HondaParamWriter:
  # Each Params.put is write + fsync + rename + fsync(dir); the dir fsync forces an ext4 journal
  # commit that first flushes every dirty page in the filesystem (loggerd's buffered video). The
  # band learners grew the per-minute flush to ~33 keys, and firing those back-to-back is ~66
  # fsyncs in one burst that other synchronous params users (hardwared, mapd) then wait behind.
  # Writes are paced one key per PARAM_WRITE_SPACING and unchanged values are skipped.
  PARAM_WRITE_SPACING = 1.0  # s

  def __init__(self):
    self._params = Params()
    self._queue = Queue()
    self._written: dict[str, float] = {}
    self._thread = threading.Thread(target=self._run, name="honda-param-writer", daemon=True)
    self._thread.start()

  def put_many(self, values):
    self._queue.put({key: float(value) for key, value in values.items()})

  def _drain(self, pending, block):
    # Collapse queued snapshots so delayed writes keep only the newest value per key.
    try:
      if block:
        pending.update(self._queue.get())
      while True:
        pending.update(self._queue.get_nowait())
    except Empty:
      pass

  def _run(self):
    pending: dict[str, float] = {}
    while True:
      self._drain(pending, block=not pending)

      key, value = next(iter(pending.items()))
      del pending[key]
      if self._written.get(key) == value:
        continue

      # block=True keeps the pacing on the disk op itself rather than on a handoff to the
      # C++ async queue, which would re-create the burst
      self._params.put(key, value, block=True)
      self._written[key] = value
      time.sleep(self.PARAM_WRITE_SPACING)

class CarController(CarControllerBase, MadsCarController, GasInterceptorCarController, IntelligentCruiseButtonManagementInterface,
                    EpsModCarController):
  def __init__(self, dbc_names, CP, CP_SP):
    CarControllerBase.__init__(self, dbc_names, CP, CP_SP)
    MadsCarController.__init__(self)
    GasInterceptorCarController.__init__(self, CP, CP_SP)
    IntelligentCruiseButtonManagementInterface.__init__(self, CP, CP_SP)
    EpsModCarController.__init__(self, CP, CP_SP)
    self.packer = CANPacker(dbc_names[Bus.pt])
    self.params = CarControllerParams(CP)
    self.CAN = hondacan.CanBus(CP)
    self.hud_object_author = hud_objects.HudObjectAuthor()
    self.lane_path_fitter = lane_path.LanePathFitter()
    self.dash_lane = lane_path.DashLane([lane_path.OFFSET_UNAVAILABLE] * lane_path.NUM_PTS, 0.0, False, False)
    self.lkas_hud_key = None
    self.lkas_state_change_frames = 0
    self.tja_control = bool(CP.flags & HondaFlags.BOSCH_TJA_CONTROL)
    self.param_writer = HondaParamWriter()

    self.braking = False
    self.brake_steady = 0.
    self.brake_last = 0.
    self.apply_brake_last = 0
    self.last_pump_ts = 0.
    self.stopping_counter = 0

    self.accel = 0.0
    self.speed = 0.0
    self.gas = 0.0
    self.brake = 0.0
    self.last_torque = 0.0
    self.bosch_last_gas = 0
    self.last_applied_brake = 0.0

    self.lkas_button_send_remaining = 0
    self.last_lkas_button_frame = 0
    self.radar_disable_counter = 0

    self.gasalpha = 0.0 if (Params().get("HondaGasAlphaParams") is None) else Params().get("HondaGasAlphaParams")
    self.gasfactor = 1.0 if (Params().get("HondaGasFactorParams") is None) else Params().get("HondaGasFactorParams")
    self.gasfactor_before_gasmax = self.gasfactor
    self.windfactor = 1.0 if (Params().get("HondaWindFactorParams") is None) else Params().get("HondaWindFactorParams")
    self.windfactor_before_gasmax = self.windfactor_before_brake = self.windfactor
    self.pitch = 0.0
    self.radar_mux = 0
    # stock RADAR_HUD_CANFD raises its CMBS bit only for a short burst after ACC engages (see
    # create_radar_hud_canfd); counted in 10 Hz hud ticks
    self.radar_hud_pulse = 0
    self.last_acc_enabled = False

    # Bosch extra-brake controller
    self.brake_pid = PIDController(k_p=0.0,
                                   k_i=1.0,
                                   pos_limit=0.0,
                                   neg_limit=-2.0,
                                   rate=50)
    self.brake_pid.reset()

    self.nidec_pid_factor = 0.0
    self.brake_pid_factor = 0.0

    self.nidec_pid = PIDController(k_p=([0,], [0,]),
                                   k_i=([0.01, 5., 35.], [1.2, 0.8, 0.5]),
                                   k_f=1,
                                   pos_limit=0., # self.params.NIDEC_ACCEL_MAX,
                                   neg_limit=self.params.NIDEC_ACCEL_MIN)
    self.nidec_pid.reset()

    self.nidec_brake_pid = PIDController(k_p=0.0,
                                   k_i=2.0,
                                   pos_limit=4.0,
                                   neg_limit=0,
                                   rate=50)
    self.nidec_brake_pid.reset()
    self.brake_pid_factor_non_lowspeed = 0.4 if (Params().get("HondaBrakePIDParams") is None) else Params().get("HondaBrakePIDParams")
    self.nidec_brake_pid.i = self.brake_pid_factor_non_lowspeed
    self.brake_pid_factor = 0.0

    self.prior_gas_average = 0.0
    self.average_factor = 0.5 if (Params().get("HondaFeedForwardParams") is None) else Params().get("HondaFeedForwardParams")
    self.average_factor = max(0.02, self.average_factor)  # same floor as the learner, so frame 1 is not a 1000x comparator
    self.average_factor_sens = 0.0  # d(prior_gas_average)/d(average_factor), recursive model sensitivity
    self.car_gas_per_pcm_gas = 0.3 if (Params().get("HondaCarGasScaleParams") is None) else Params().get("HondaCarGasScaleParams")
    self.creep_factor = 1.0 if (Params().get("HondaCreepFactorParams") is None) else Params().get("HondaCreepFactorParams")

    def load_param(key, default):
      value = Params().get(key)
      return float(default) if value is None else float(value)

    # Multi-band gas and speed channels (see NIDEC_GAS_BANDS / NIDEC_SPEED_BANDS): each node
    # carries its own factor/alpha, learns in proportion to its hat weight over the sent target
    # and persists under its own param key. The banding exists because one scalar per channel
    # equilibrates on highway frames and leaves the low-speed target wrong: the gas target is
    # normalized by NIDEC_MAX_ACCEL_V, whose shape (2.4 m/s2 at 4 m/s -> 0.6 at 20) is ~2x too
    # steep for this car (route 51: smoothed wire 48-97 for cmd 0.3-1.5 at 2-13 m/s with err
    # +0.18..+0.47, vs authority-limited err +0.05..+0.32 at 13-32 m/s), and the speed servo's
    # dv gain is lower below ~30 mph with a speed-dependent zero-accel offset (routes 18/19/1a:
    # undershoot +0.45 below 13.4 m/s vs +0.04 above).
    # The pre-existing low (10 m/s) / high (16 m/s) nodes load their old params; new nodes seed
    # from the old two-band blend evaluated at the node speed, so the first drive with this code
    # reproduces the previous curve exactly and starts from today's operating point.
    # Persisted speed-channel state is loaded as-is, never sanitized: a value outside the learner's
    # bounds is the visible trace of a learner bug (Pilot route b29245576c122ee6/3a booted with
    # HondaSpeedFactorParams 0.086 and HondaSatAccelParams 0.1, i.e. a 0.15 m/s lead at cmd +0.9
    # sent to the servo as "hold speed" for 40 s) and a boot-time fix-up would hide it. The
    # learner's own clips in update() move it onto the bound on its first tick, and it is
    # required to walk back from every corner of the box on its own.
    gf_high = load_param("HondaGasFactorParams", 1.0)
    gf_low = load_param("HondaGasFactorLowParams", gf_high)
    ga_high = load_param("HondaGasAlphaParams", 0.0)
    sf_high = load_param("HondaSpeedFactorParams", NIDEC_SPEED_FACTOR_DEFAULT)
    sa_high = load_param("HondaSpeedAlphaParams", 0.0)
    sf_low = load_param("HondaSpeedFactorLowParams", NIDEC_SPEED_FACTOR_DEFAULT)
    sa_low = load_param("HondaSpeedAlphaLowParams", 0.0)

    def old_two_band_blend(low_val, high_val, band_speed):
      low_w = float(np.interp(band_speed, [10.0, 16.0], [1.0, 0.0]))
      return low_w * low_val + (1.0 - low_w) * high_val

    self.gas_factors = {}
    self.gas_alphas = {}
    for band, band_speed in NIDEC_GAS_BANDS:
      self.gas_factors[band] = load_param(NIDEC_GAS_FACTOR_KEYS[band], old_two_band_blend(gf_low, gf_high, band_speed))
      # gas_alpha used to be a single scalar, so every node seeds from it
      self.gas_alphas[band] = load_param(NIDEC_GAS_ALPHA_KEYS[band], ga_high)
    self.gas_factors_before_gasmax = dict(self.gas_factors)
    self.gas_factors_nomaxspeed = dict(self.gas_factors)
    self.gas_alphas_nomaxspeed = dict(self.gas_alphas)

    self.speed_factors = {}
    self.speed_alphas = {}
    for band, band_speed in NIDEC_SPEED_BANDS:
      self.speed_factors[band] = load_param(NIDEC_SPEED_FACTOR_KEYS[band], old_two_band_blend(sf_low, sf_high, band_speed))
      self.speed_alphas[band] = load_param(NIDEC_SPEED_ALPHA_KEYS[band], old_two_band_blend(sa_low, sa_high, band_speed))

    self.windfactor = 1.0 if (Params().get("HondaWindFactorParams") is None) else Params().get("HondaWindFactorParams")
    self.windfactor_before_gasmax = self.windfactor_before_brake = self.windfactor
    self.sat_accel = load_param("HondaSatAccelParams", NIDEC_SAT_ACCEL_DEFAULT)
    self.sat_deficit_frames = self.sat_excess_frames = 0
    # (accel, wire gas pinned, speed-channel learn gate) per frame, read back a servo lag later
    self.speed_cmd_hist: deque[tuple[float, bool, bool]] = deque([(0.0, False, False)] * NIDEC_SERVO_LAG_FRAMES,
                                                                 maxlen=NIDEC_SERVO_LAG_FRAMES)
    self.a_ego_filt = 0.0
    self.new_accel = 0.0

    # launch governor: owns the standstill -> moving window with stock-shaped commands (small dv
    # step + immediate gas seed + X01 power flag) instead of the general pipeline. A huge dv step
    # into the PCM's low-pass produces dead time followed by a late surge. Both parameters
    # learn once per launch EVENT from direct measurements and are bracketed from both sides
    # (slow launch grows dv_launch, motion lurch shrinks it), so neither can run away; the range
    # clips are loose backstops that should not bind.
    self.dv_launch = 2.8 if (Params().get("HondaLaunchDvParams") is None) else Params().get("HondaLaunchDvParams")  # m/s; stock launches at 9.99 kph
    self.gas_launch = 110.0 if (Params().get("HondaLaunchGasParams") is None) else Params().get("HondaLaunchGasParams")  # PCM_GAS units; stock 104-114
    # the seed has to sit in the band where the PCM actually applies pedal to it: below ~100 the
    # wire is treated as no-torque (route 250: gas 1-99 gave +0.02 m/s2, same as gas 0; 100-197
    # +0.09; 198 +0.57), and stock launches at 104-114. The shrink-on-overshoot update walked the
    # persisted value down to 60 across EV launches where the seed was not even what produced
    # the overshoot (breakaway band), and growth needs ceiling evidence (pedal riding the seed)
    # that a seed in the no-torque band can never produce, so it was a one-way ratchet. Route 5d,
    # two engine-on launches at seed 60: pedal 0 for the whole 2 s window on the flat one, 4-12
    # on the +2.8 deg one (1.2 s to first motion, aEgo 0.1-0.3 against a 0.3-0.66 plan, window
    # timed out at 0.8 m/s). A persisted value below the band is poisoned, not learned: reset it.
    self.gas_launch_min = 100.0
    if self.gas_launch < self.gas_launch_min:
      self.gas_launch = 110.0
    # breakaway lead, used only until first motion: the EV creep response scales with dv, and
    # the stock-sized lead is not enough to break away reliably engine-off.
    # Hands over to dv_launch at first motion so nothing accumulates in the servo low-pass.
    self.dv_break = 6.0 if (Params().get("HondaLaunchDvBreakParams") is None) else Params().get("HondaLaunchDvBreakParams")  # m/s
    self.launch_active = False
    # gas-channel recovery window: opened at driver-gas override release, at launch window
    # exit, at openpilot brake release and at engage while rolling. In every case the wire gas
    # is coming out of a known dead state (the concurrent gas+brake guard zeroes it for the
    # whole brake period) and has to re-wind the PCM's internal pedal tracker; the +2/tick rise
    # clip alone spends ~1s just climbing 0->198 (routes 33/34: post-override err +0.9..+1.7 for
    # 2-2.5s; route 48: 28 brake->gas transitions, wire reached 100 at +0.62s median, pedal
    # onset +1.44s, aEgo>0.2 only at +2.3s, err +0.56 over the 3s; pedal onset tracked
    # wire>=100 (corr 0.71) plus the same ~0.6s PCM lag seen for cruise rises, so the climb
    # is the only part of that chain on our side — whether the PCM also has a fixed re-apply
    # dead time after its brake period is unresolved: the one fast-wire event still saw the
    # pedal at +1.44s, so the wire shaping here is bounded-benefit, while the learner gating
    # the window provides is the certain part).
    self.gas_recovery_ticks = 0
    self.gas_pressed_prev = False
    self.long_active_prev = False
    self.launch_ticks = 0
    self.launch_release_tick = -1
    self.launch_move_tick = -1
    self.launch_lurch_sum = 0.0
    self.launch_lurch_n = 0
    self.launch_err_sum = 0.0
    self.launch_err_n = 0
    self.launch_ceiling_ticks = 0

    self.latFactors = {
      "05": 1.0 if (Params().get("HondaLatAccelFactor05Params") is None) else Params().get("HondaLatAccelFactor05Params"),
      "10": 1.0 if (Params().get("HondaLatAccelFactor10Params") is None) else Params().get("HondaLatAccelFactor10Params"),
      "15": 1.0 if (Params().get("HondaLatAccelFactor15Params") is None) else Params().get("HondaLatAccelFactor15Params"),
      "20": 1.0 if (Params().get("HondaLatAccelFactor20Params") is None) else Params().get("HondaLatAccelFactor20Params"),
      "25": 1.0 if (Params().get("HondaLatAccelFactor25Params") is None) else Params().get("HondaLatAccelFactor25Params"),
      "30": 1.0 if (Params().get("HondaLatAccelFactor30Params") is None) else Params().get("HondaLatAccelFactor30Params"),
      "35": 1.0 if (Params().get("HondaLatAccelFactor35Params") is None) else Params().get("HondaLatAccelFactor35Params"),
      "40": 1.0 if (Params().get("HondaLatAccelFactor40Params") is None) else Params().get("HondaLatAccelFactor40Params"),
      "45": 1.0 if (Params().get("HondaLatAccelFactor45Params") is None) else Params().get("HondaLatAccelFactor45Params"),
      "50": 1.0 if (Params().get("HondaLatAccelFactor50Params") is None) else Params().get("HondaLatAccelFactor50Params"),
      "55": 1.0 if (Params().get("HondaLatAccelFactor55Params") is None) else Params().get("HondaLatAccelFactor55Params"),
      "60": 1.0 if (Params().get("HondaLatAccelFactor60Params") is None) else Params().get("HondaLatAccelFactor60Params")
    }

  def update(self, CC, CC_SP, CS, now_nanos):
    MadsCarController.update(self, self.CP, CC, CC_SP)
    gas_pedal_force = 0.0
    actuators = CC.actuators
    hud_control = CC.hudControl
    if self.CP.flags & HondaFlags.BOSCH:
      hud_v_cruise = hud_control.setSpeed / CS.v_cruise_factor if 0 < CS.out.vCruise < 255 else 255
    else:
      hud_v_cruise = hud_control.setSpeed / CS.v_cruise_factor if hud_control.speedVisible else 255
    pcm_cancel_cmd = CC.cruiseControl.cancel

    if len(CC.orientationNED) == 3:
      self.pitch = CC.orientationNED[1]
    hill_brake = math.sin(self.pitch) * ACCELERATION_DUE_TO_GRAVITY
    # Nidec: within this margin of the displayed set speed the PCM's own governor owns the
    # acceleration (see nidec_set_speed_governed), so no longitudinal learner may read the
    # response there. The gas channel has always been protected here; the CR-V showed the
    # speed channel needs it too.
    set_speed_governed = nidec_set_speed_governed(CS.out.vEgo, CS.out.cruiseState.speed)

    # wind brake from air resistance decel at high speed
    wind_brake = np.interp(CS.out.vEgo, [0.0, 2.3, 35.0], [0.001, 0.002, 0.15]) * self.windfactor # not in m/s2 units

    prior_windfactor = self.windfactor
    if CC.longActive:
      if self.CP.flags & HondaFlags.BOSCH:
        accel = actuators.accel
        adjust_accel = accel + hill_brake
        brake = 0.0
        gas, brake = compute_gas_brake(adjust_accel, CS.out.vEgo, self.CP)
      elif self.CP_SP.enableGasInterceptor or (self.CP_SP.flags & HondaFlagsSP.STOCK_LONGITUDINAL):
        # interceptor: the plan accel is the brake target for the Nidec brake path below (no PCM
        # gas servo, so no nidec_pid correction); gas goes out on the interceptor wire
        self.accel = actuators.accel
        accel = self.accel
        gas, brake = compute_gas_brake(actuators.accel + hill_brake, CS.out.vEgo, self.CP)
      elif self.CP.openpilotLongitudinalControl and not (self.CP.flags & HondaFlags.BOSCH):
        if (actuators.longControlState in (LongCtrlState.pid, LongCtrlState.stopping)) and \
           (CS.out.vEgo > 1e-5 or actuators.accel > 1e-5) \
           and (not CS.out.stockAeb) and (not CS.out.gasPressed):
          old_i = self.nidec_pid.i
          self.nidec_pid_factor = self.nidec_pid.update(error = actuators.accel - CS.out.aEgo, speed = CS.out.vEgo)
          if actuators.accel >= 1e-5 and CS.out.vEgo < 1.0: # don't drop PID at launch lurch
             self.nidec_pid_factor = self.nidec_pid.i = max(old_i, self.nidec_pid.i)
          self.accel = actuators.accel + self.nidec_pid_factor
          adjust_accel = self.accel + hill_brake

          # copy wind tuning from Bosch code
          gas_error = self.accel - CS.out.aEgo
          wind_learn_speed = 1000
          wind_adjust = 1 + wind_brake / wind_learn_speed
          # windfactor is the one gas-side learner that was not protected near the set speed: at
          # the governor the gas error is permanently positive (plan +0.7, car 0) and it climbed
          # toward its 3.0 clip, which also pushes the Nidec brake threshold (brake_last - wind_brake)
          # out to ~-2 m/s2 of plan before any brake is applied
          if not set_speed_governed:
            self.windfactor = np.clip(self.windfactor * (wind_adjust if (gas_error > 0) else 1.0/wind_adjust), 0.1, 3.0)
          gas_pedal_force = self.accel
          if gas_pedal_force <= 0.0: # don't reduce windfactor while braking, allow increases
            self.windfactor = max(self.windfactor, self.windfactor_before_brake)
          else:
            self.windfactor_before_brake = self.windfactor
          if not set_speed_governed:
            # drop to max values when not near speed limit
            self.gas_factors = dict(self.gas_factors_nomaxspeed)
            self.gas_alphas = dict(self.gas_alphas_nomaxspeed)
          if (gas_pedal_force >= self.params.BOSCH_ACCEL_MAX):
            # don't increase gasfactor nor windfactor at accel max, allow decreases
            for band in self.gas_factors:
              self.gas_factors[band] = min(self.gas_factors[band], self.gas_factors_before_gasmax[band])
            self.windfactor = min(self.windfactor, self.windfactor_before_gasmax)
          else:
            self.gas_factors_before_gasmax = dict(self.gas_factors)
            self.windfactor_before_gasmax = self.windfactor

        else:
          self.accel = actuators.accel + self.nidec_pid_factor
          adjust_accel = self.accel + hill_brake

        if (CS.out.brakePressed or CS.out.gasPressed or CS.out.vEgo < 1e-5) and (self.nidec_pid.i <= 0.01):
          self.nidec_pid.i += 0.01 # clear out nidec pid integral while acc not controlling car

        # Inside a launch window the brake target is the plan alone. adjust_accel carries the hill
        # term, and on a downhill stop that is a negative offset the brake path reads as a hold
        # request: route 5e t=191.5 (-4.1 deg, hill_brake -0.70) kept the brake on until the plan
        # exceeded +0.70 m/s2, 0.8 s after it went positive, and the gas+brake guard zeroed the
        # launch template on the wire for that whole time (release -> motion was 0.25 s once the
        # brake finally dropped, i.e. the dead time was all on this side). Grade is the speed
        # servo's job once rolling and the PCM holds at pcm_speed=0 before that. The creep term is
        # the same kind of hold against a ~zero plan (a fresh-boot creep_factor of 1.0 adds another
        # 0.8 s at 0.72 m/s2/s of plan ramp) and has no place in a launch either. Uphill is
        # unchanged: the window only opens on a positive plan, and a positive hill term never held
        # the brake. Everything outside the window keeps the hill/creep terms as before.
        if self.launch_active:
          brake, creep_impact = compute_gb_honda_nidec(self.accel, CS.out.vEgo, 0.0)
        else:
          brake, creep_impact = compute_gb_honda_nidec(adjust_accel, CS.out.vEgo, self.creep_factor)
        gas_error = self.accel - CS.out.aEgo
        if (actuators.longControlState == LongCtrlState.pid) and (not CS.out.stockAeb) and (not CS.out.gasPressed) \
               and (1e-5 <= CS.out.vEgo <= CS.out.cruiseState.speed - 2.):
          self.creep_factor = 0.0
          # self.creep_factor = np.clip(self.creep_factor + 0.001 * creep_impact * gas_error, 0.0, 3.0)
    else:
      self.accel = 0.0
      adjust_accel = self.accel
      brake = 0.0
      accel = 0.0
      gas, brake = 0.0, 0.0

    if CC.longActive and not (self.CP.flags & HondaFlags.BOSCH):
      accel = self.accel
    if CS.out.gasPressed or not CC.longActive:
      self.nidec_pid.reset()

    # *** rate limit steer ***
    limited_torque = rate_limit(actuators.torque, self.last_torque, -self.params.STEER_DELTA_DOWN * DT_CTRL,
                                self.params.STEER_DELTA_UP * DT_CTRL)
    if (self.CP.carFingerprint == CAR.ACURA_MDX_3G) and \
        (self.apply_brake_last > 0 or self.new_accel < 1e-5): # lower steer limits while braking
      brake_limit = float(233.0 / self.params.STEER_MAX)
      limited_torque = float(np.clip(limited_torque, -brake_limit, brake_limit))
    self.last_torque = limited_torque if CS.steer_control_active else 0.0

    # *** apply brake hysteresis ***
    pre_limit_brake, self.braking, self.brake_steady = actuator_hysteresis(brake, self.braking, self.brake_steady)

    # *** rate limit after the enable check ***
    self.brake_last = rate_limit(pre_limit_brake, self.brake_last, -2., 3 * DT_CTRL)

    # vehicle hud display, wait for one update from 10Hz 0x304 msg
    alert_fcw, alert_steer_required = process_hud_alert(hud_control.visualAlert)

    # **** process the car messages ****

    # steer torque is converted back to CAN reference (positive when steering right)
    apply_torque = int(np.clip(-limited_torque, -1.0, 1.0) * self.params.STEER_MAX)
    if self.eps_mod_lookup is not None:
      apply_torque = EpsModCarController.get_apply_torque(self, limited_torque)

    speed_val = np.clip(round(CS.out.vEgo * CV.MS_TO_MPH / 5.0) * 5, 5, 60)
    currentLatSpeed = f"{speed_val:02d}"
    if currentLatSpeed in self.latFactors and not CS.out.steeringPressed and CS.steer_control_active:
      if abs(limited_torque) > 0.9 and self.latFactors[currentLatSpeed] > abs(CS.out.steeringAngleDeg):
        self.latFactors[currentLatSpeed] /= 1.001
      if abs(limited_torque) < 0.9 and self.latFactors[currentLatSpeed] < abs(CS.out.steeringAngleDeg):
        self.latFactors[currentLatSpeed] *= 1.001

    # Send CAN commands
    can_sends = []

    # tester present - w/ no response (keeps radar disabled)
    if self.CP.flags & HondaFlags.BOSCH and not (self.CP.flags & HondaFlags.BOSCH_RADARLESS) and self.CP.openpilotLongitudinalControl:
      if self.CP.flags & HondaFlags.BOSCH_CANFD and CS.stock_acc_alive:
        # CAN FD: the radar is still transmitting. It is silenced from here rather than from
        # CarInterface.init(), and only once the comma relay is confirmed open: init() ran while the
        # panda was still in the ELM327 safety mode, so the replacement ACC_CONTROL stream was blocked
        # until the safety-mode switch landed, and whenever the switch took longer than ~110 ms after
        # the radar went silent the brake module latched CRUISE_FAULT (accFaulted) for the whole drive.
        # With the relay already open the stock radar keeps feeding the brake module (and, via panda
        # forwarding, the camera) right up to the switchover, and the replacement stream starts within
        # a few frames of radar silence (see CS.stock_acc_alive), well inside the fault threshold.
        if CS.canfd_relay_open:
          if self.radar_disable_counter % 50 == 0:
            # UDS extended diagnostic session, required before CommunicationControl
            can_sends.append((0x18DAB0F1, b'\x02\x10\x03\x00\x00\x00\x00\x00', self.CAN.pt))
          elif self.radar_disable_counter % 50 == 5:
            # UDS CommunicationControl disableRxAndTx (0x80 suppresses the response); the same request
            # CarInterface.init() used to send, retried every 0.5 s until the radar goes silent
            can_sends.append((0x18DAB0F1, b'\x03\x28\x83\x03\x00\x00\x00\x00', self.CAN.pt))
          self.radar_disable_counter += 1
      elif self.frame % 10 == 0:
        # tester present - w/ no response (keeps radar disabled)
        bus = 0 if self.CP.flags & HondaFlags.BOSCH_CANFD else 1
        can_sends.append(make_tester_present_msg(0x18DAB0F1, bus, suppress_response=True))

    # simulate canfd radar to prevent faults
    # These radar look-alikes are consumed by both the camera ECU (behind the relay, on the camera
    # bus) and the powertrain (radar bus). openpilot's own transmissions are not forwarded across the
    # open relay, so they must be sent explicitly on both buses. Each message is packed exactly once
    # so the packer's counter/checksum only advance once per cycle, then the identical bytes are
    # mirrored onto both buses (re-packing would double-increment the counter and desync the buses).
    # While the stock radar is still transmitting (drive start, before the deferred disable above has
    # silenced it), it authors all of these itself: sending look-alikes too would double them up.
    if (self.CP.flags & HondaFlags.BOSCH_CANFD) and self.CP.openpilotLongitudinalControl and not CS.stock_acc_alive:
      if CC.enabled and not self.last_acc_enabled:
        self.radar_hud_pulse = 30  # ~3 s at 10 Hz, matching the stock 2-6 s engage burst
      self.last_acc_enabled = CC.enabled
      radar_msgs = []
      if CS.hud_tick:
        radar_msgs.append(hondacan.create_radar_hud_canfd(self.packer, self.CAN.pt, CC.enabled, self.radar_hud_pulse > 0))
        if self.radar_hud_pulse > 0:
          self.radar_hud_pulse -= 1
      if CS.supp_tick:
        radar_msgs.append(hondacan.create_canfd_supplemental(self.packer, self.CAN.pt))
      if CS.radar_50hz_tick:
        # Cycle the radar MUX through the same banks the stock radar uses: 1-10, 17-26, 33-42, 49-58.
        # This counter also drives the LANE_PATH/HUD_OBJECTS mux below: it advances exactly one step
        # per transmitted frame, so the sweep stays contiguous even when a tick is missed (deriving
        # the mux from the frame counter skipped a mux on every missed tick, leaving holes in the
        # sweep the stock radar never produces).
        # These must be elif (not sequential if): a bare `if` that sets the bank start would fall
        # through to the `else` increment, skipping the bank-start values (17, 33, 49).
        if self.radar_mux >= 58:
          self.radar_mux = 1
        elif self.radar_mux == 10:
          self.radar_mux = 17
        elif self.radar_mux == 26:
          self.radar_mux = 33
        elif self.radar_mux == 42:
          self.radar_mux = 49
        else:
          self.radar_mux += 1
        # radar_msgs.extend(hondacan.create_canfd_50hz_radar_messages(self.packer, self.CAN.pt, self.radar_mux))
      if CS.radar_5hz_tick:
        # RADAR_LEAD's LANE_PATH_LENGTH must track the valid-point count of the LANE_PATH sweep we are
        # authoring; the stock radar keeps the two in lockstep and the dash won't draw lanes otherwise.
        # LEFT_LANE/RIGHT_LANE carry the per-side line-detected status (3/0) the same way the stock
        # radar mirrors the camera's LANE_LINES bits; the dash draws no lane lines while both are 0.
        radar_msgs.extend(hondacan.create_canfd_5hz_radar_messages(self.packer, self.CAN.pt, CS.radar_ref_counter,
                                                                   lane_path.canfd_lane_length(self.dash_lane),
                                                                   lane_path.LANE_LINE_ON if self.dash_lane.left_line else 0,
                                                                   lane_path.LANE_LINE_ON if self.dash_lane.right_line else 0))

      # mirror each packed frame onto both the powertrain bus and the camera bus
      for addr, dat, _ in radar_msgs:
        can_sends.append((addr, dat, self.CAN.pt))
        can_sends.append((addr, dat, self.CAN.camera))

    # Send steering command.
    can_sends.append(hondacan.create_steering_control(self.packer, self.CAN, apply_torque, CC.latActive, self.tja_control))

    wind_brake_ms2 = np.interp(CS.out.vEgo, [0.0, 13.4, 22.4, 31.3, 40.2], [0.000, 0.049, 0.136, 0.267, 0.441]) # in m/s2 units

    # launch governor state machine (Nidec): window from engaged standstill with a positive plan
    # until moving (>1.5 m/s) or timeout. Measurements are collected per tick, learner updates
    # happen once at a clean window exit (aborts from driver input or a negative plan learn nothing).
    if self.CP.openpilotLongitudinalControl and not (self.CP.flags & HondaFlags.BOSCH) and not self.CP_SP.enableGasInterceptor and \
       not (self.CP_SP.flags & HondaFlagsSP.STOCK_LONGITUDINAL):
      if not self.launch_active:
        if CC.longActive and (not CS.out.gasPressed) and (not CS.out.brakePressed) and \
             (CS.out.vEgo < 0.1) and (actuators.accel > 0.05):
          self.launch_active = True
          self.launch_ticks = 0
          self.launch_release_tick = -1
          self.launch_move_tick = -1
          self.launch_lurch_sum = 0.0
          self.launch_lurch_n = 0
          self.launch_err_sum = 0.0
          self.launch_err_n = 0
          self.launch_ceiling_ticks = 0
      else:
        self.launch_ticks += 1
        if (self.launch_release_tick < 0) and (self.apply_brake_last == 0):
          self.launch_release_tick = self.launch_ticks
        if (self.launch_move_tick < 0) and (CS.out.vEgo > 0.1):
          self.launch_move_tick = self.launch_ticks
        if (self.launch_move_tick >= 0) and (10 <= self.launch_ticks - self.launch_move_tick <= 50):
          # lurch: SUSTAINED accel beyond the plan just after breakaway (0.1-0.5s window). The
          # instantaneous aEgo at first motion spikes to ~3 m/s2 for a frame or two from wheel
          # speed breakaway quantization (routes 18/19/1a: every launch registered a "lurch"
          # that way, shrinking dv_launch 2.8 -> 2.0 while every launch was actually slow), so
          # only a windowed mean is a real lurch measurement.
          self.launch_lurch_sum += CS.out.aEgo - actuators.accel
          self.launch_lurch_n += 1
        if self.launch_move_tick >= 0:
          self.launch_err_sum += actuators.accel - CS.out.aEgo
          self.launch_err_n += 1
          # ceiling binding: engine running and applied pedal near the commanded seed, i.e. the
          # gas channel was actually delivering the ceiling, so more authority would have helped.
          # EV launches never satisfy this (pedal decoupled), so they produce no gas_launch growth.
          if (CS.engine_rpm > 500) and (CS.car_gas >= 0.8 * self.car_gas_per_pcm_gas * self.gas_launch):
            self.launch_ceiling_ticks += 1
        launch_aborted = (not CC.longActive) or CS.out.gasPressed or CS.out.brakePressed or (actuators.accel < -0.05)
        launch_done = (CS.out.vEgo > 1.5) or (self.launch_ticks >= 300)
        if launch_aborted or launch_done:
          if launch_done and not launch_aborted:
            # dv_break owns breakaway dead time vs lurch, one sign-correct update per launch:
            # motion later than 0.6s after brake release (or never, with the brake released >1s)
            # means more breakaway lead; sustained overshoot just after breakaway means less.
            # Bracketed from both sides.
            never_moved = (self.launch_move_tick < 0) and (self.launch_release_tick >= 0) and \
                          (self.launch_ticks - self.launch_release_tick > 100)
            launch_slow = never_moved or ((self.launch_move_tick >= 0) and (self.launch_release_tick >= 0) and
                                          (self.launch_move_tick - self.launch_release_tick > 60))
            if launch_slow:
              self.dv_break *= 1.05
            launch_lurch = (self.launch_lurch_sum / self.launch_lurch_n) if self.launch_lurch_n > 0 else 0.0
            if launch_lurch > 0.5:
              self.dv_break *= (1 - 0.05 * min(launch_lurch, 2.0))
            self.dv_break = float(np.clip(self.dv_break, 2.0, 12.0))
            # post-motion window tracking splits by channel ownership: undershoot with the pedal
            # riding the commanded ceiling engine-on means more gas would have helped; undershoot
            # WITHOUT ceiling evidence (EV launches, where the pedal is decoupled from PCM_GAS)
            # belongs to the speed lead. Overshoot shrinks both slowly.
            if self.launch_err_n > 50:
              launch_err = self.launch_err_sum / self.launch_err_n
              if launch_err > 0.15:
                if self.launch_ceiling_ticks > 0.5 * self.launch_err_n:
                  self.gas_launch *= 1.03
                else:
                  self.dv_launch *= 1.03
              elif launch_err < -0.15:
                self.gas_launch *= 0.99
                self.dv_launch *= 0.99
              self.gas_launch = float(np.clip(self.gas_launch, self.gas_launch_min, self.params.NIDEC_GAS_MAX))
              self.dv_launch = float(np.clip(self.dv_launch, 1.0, 8.0))
          self.launch_active = False
          if launch_done and not launch_aborted:
            # hand the general pipeline a recovery window: the seed is usually below the
            # feedforward target at exit, and the +2/tick clip alone spends ~0.5s closing
            # that gap (route 33 launch t=549: gas 91 -> 183 over 0.5s, err +0.76 for 3s)
            self.gas_recovery_ticks = 200

      # driver-gas override release: the wire gas restarts from the mirror/zero while the plan
      # ramps positive immediately; open the recovery window on the falling edge.
      self.gas_recovery_ticks = max(self.gas_recovery_ticks - 1, 0)
      if CC.enabled and self.gas_pressed_prev and (not CS.out.gasPressed):
        self.gas_recovery_ticks = 200
      self.gas_pressed_prev = CS.out.gasPressed
      # engage while rolling: the wire was 0 (not longActive) and the plan is typically already
      # positive, so this is the same restart-from-dead-state as an override release (route 48:
      # 8 rolling engages without a prior gas press, err +0.35..+0.79 over 3s, wire>=100 at
      # 0.5-2.8s). Standstill engages are owned by the launch governor.
      if CC.longActive and (not self.long_active_prev) and (CS.out.vEgo > 0.1) and (not self.launch_active):
        self.gas_recovery_ticks = 200
      self.long_active_prev = CC.longActive

    if self.CP.openpilotLongitudinalControl and not (self.CP.flags & HondaFlags.BOSCH) and not self.CP_SP.enableGasInterceptor and \
       not (self.CP_SP.flags & HondaFlagsSP.STOCK_LONGITUDINAL):
      max_accel = np.interp(CS.out.vEgo, self.params.NIDEC_MAX_ACCEL_BP, self.params.NIDEC_MAX_ACCEL_V)
      # multi-band blends: piecewise-linear hat weights across the band nodes (the two bands
      # bracketing the current speed carry all the weight; edge bands saturate outside the grid)
      gas_w = band_weights(NIDEC_GAS_BANDS, CS.out.vEgo)
      speed_w = band_weights(NIDEC_SPEED_BANDS, CS.out.vEgo)
      sf_eff = sum(w * self.speed_factors[band] for band, w in speed_w.items())
      alpha_eff = sum(w * self.speed_alphas[band] for band, w in speed_w.items())
      # TODO this 1.44 is just to maintain previous behavior
      if not CC.longActive:
        if CC.enabled and CS.out.gasPressed and CS.car_gas_available:
          # driver-gas override: mirror the applied pedal onto the wire instead of zeroing it.
          # Stock keeps commanding through overrides (PCM_SPEED = set speed, PCM_GAS nonzero);
          # zeroing instead told the PCM "no torque" for the whole override, so its internal pedal
          # tracker unwound to zero and the release started from scratch (routes 33/34: pedal
          # stayed 0 until ~2s after release; at t=288.5 the commanded zero-torque second even
          # dropped the engine into idle-stop while moving, adding restart lag). The mirror also
          # keeps prior_gas_average — the model of the PCM's smoothed command — tracking the true
          # operating point through the override, and seeds the release rise clip from it.
          # moved to "not CC.longActive" block because powertrain sets ACC_STATUS = 0 when gasPressed
          # set pcm_speed to current speed + 9 to mirror stock
          pcm_speed = float(np.clip(CS.out.vEgo, 0.0, 100.0))
          pcm_accel = int(np.clip(CS.car_gas / max(self.car_gas_per_pcm_gas, 1e-3), 0.0, self.params.NIDEC_GAS_MAX))
        else:
          pcm_speed = 0.0
          pcm_accel = int(0.0)
      else:
        if self.launch_active:
          # stock-shaped launch lead (stock uses 9.99 kph): the general sf*accel+alpha lead is both
          # poisoned-prone and a step input the servo low-passes into dead time + late surge.
          # Until first motion the larger breakaway lead is used: EV creep response scales with dv,
          # and the post-motion lead alone was not enough to break away engine-off.
          speed_lead = self.dv_launch if CS.out.vEgo > 0.1 else self.dv_break
        else:
          speed_lead = nidec_speed_lead_mps(sf_eff, float(self.accel), alpha_eff)
        pcm_speed = float(np.clip(CS.out.vEgo + speed_lead, 0.0, 100.0))
        gas_accel = adjust_accel + wind_brake_ms2 * self.windfactor
        gf_eff = sum(w * self.gas_factors[band] for band, w in gas_w.items())
        ga_eff = sum(w * self.gas_alphas[band] for band, w in gas_w.items())
        pcm_accel = int(np.clip((ga_eff + gas_accel * gf_eff / 1.44) / max_accel, 0.0, 1.0) * self.params.NIDEC_GAS_MAX)
        if pcm_accel > 0:
          pcm_speed = max(pcm_speed, 1.0) # prevent fault by always sending positive speed during gas
      max_speedcontrol = (pcm_speed > 99.999)
      prior_speed_factors = dict(self.speed_factors)
      prior_speed_alphas = dict(self.speed_alphas)

      # feedforward for Nidec decaying-average gas pedal
      # inside a recovery window the rise clip opens to the stock launch envelope (+70/frame vs
      # stock's observed +74/frame): the +20/frame cruise clip is sized for smoothness around an
      # operating point, but coming out of an override/launch/brake there is no operating point yet —
      # holding it there spends a full second climbing 0->198 while PCM_GAS=0 gates off all power
      # (routes 33/34: aEgo fell to -0.3 against cmd +1.25 during that second, and the PCM's
      # pedal tracker + idle-stop restart stacked another ~1.5s on top).
      # The wide clip only applies while the wire is still below the feedforward target: the
      # window's job is to close the gap from the dead state to the operating point. Beyond the
      # target the 1/average_factor lead (~30x at the learned ~0.035) already overshoots, and
      # letting that run at +70/frame just triples the sawtooth amplitude the PCM has to smooth
      # (bench: 0->140 in 0.2s against a target of 50) for no gain in reaching the target.
      prior_accel = int(self.new_accel)
      max_increase = 7 if (self.gas_recovery_ticks > 0 and prior_accel < pcm_accel) else 2  # per 100Hz tick, x10 per sent frame
      # When GAS_PEDAL_2 is absent the direct-measurement learner cannot run; use a fixed factor so
      # feedforward stays stable on platforms that do not report applied pedal position.
      effective_average_factor = self.average_factor if CS.car_gas_available else 0.5
      self.new_accel = int((pcm_accel - self.prior_gas_average * (1 - effective_average_factor)) / effective_average_factor)
      self.new_accel = int(np.clip(self.new_accel, 0, min(prior_accel + max_increase, self.params.NIDEC_GAS_MAX)))
      if self.launch_active:
        # gas seed: send the learned launch gas immediately (stock jumps to 104-114 in one frame,
        # within its observed +114/frame ramp envelope; ramping from 0 at +2/tick wastes ~0.5s of the
        # launch just climbing, and PCM_GAS=0 gates off all power on this platform). While the brake
        # is still applied the concurrent gas+brake protection below keeps the wire at 0; on window
        # exit the rise clip continues from the seed via prior_accel, so there is no discontinuity.
        launch_seed = self.gas_launch
        if (CS.engine_rpm < 500) and (CS.out.vEgo <= 0.1):
          # EV breakaway: midrange gas has no pedal coupling engine-off (route 1a t=3002: gas 108
          # held 2.6s, zero motion until the driver's pedal cranked the engine). The stock camera's
          # own EV plateau is saturation (198/200 observed while accelerating in EV), so command
          # the full authority band until first motion, then hand back to the learned seed.
          launch_seed = self.params.NIDEC_GAS_MAX
        self.new_accel = int(min(launch_seed, self.params.NIDEC_GAS_MAX))
      # recursive sensitivity of the model prediction to average_factor, advanced with the model itself;
      # used by the average_factor learner below (must be computed before prior_gas_average is updated)
      self.average_factor_sens = (self.new_accel - self.prior_gas_average) + (1 - effective_average_factor) * self.average_factor_sens
      self.prior_gas_average = self.prior_gas_average * (1 - effective_average_factor) + (self.new_accel * effective_average_factor)

      if (0 < self.new_accel < self.params.NIDEC_GAS_MAX) and (not CS.out.gasPressed) and \
           (self.apply_brake_last == 0) and (not self.launch_active) and (self.gas_recovery_ticks == 0):
        gasfactor_error = (self.accel - CS.out.aEgo)
        # the 0<wire<198 gate above is the gas channel's own observability condition (a pinned
        # wire cannot show what more gasfactor would do); the clip is a runaway backstop only.
        # 5.0 rather than the Bosch path's 3.0 because the Nidec target divides by
        # NIDEC_MAX_ACCEL_V (2.0-2.4 at 4-10 m/s): pinning the wire at cmd 0.85 there needs
        # gf ~3.5, which the low bands are expected to learn.
        gf_growth = 0.0001 * gasfactor_error * gas_accel
        # each band learns in proportion to its authority over the sent target
        for band, w in gas_w.items():
          self.gas_alphas[band] = float(np.clip(self.gas_alphas[band] + w * 0.0001 * gasfactor_error / 4.8, -3.0, 3.0))
          self.gas_factors[band] = float(np.clip(self.gas_factors[band] * (1 + w * gf_growth), 0.1, 5.0))
      # speed-channel delay line and settled-response filter run every frame, gated or not: the frame the
      # servo is answering now must be on record even if it was a brake frame (then it teaches nothing)
      accel_lag, gas_pinned, lag_learn_ok = self.speed_cmd_hist[0]
      self.speed_cmd_hist.append((float(self.accel), self.new_accel >= self.params.NIDEC_GAS_MAX,
                                  (not CS.out.gasPressed) and (self.apply_brake_last == 0) and CC.longActive and
                                  (not self.launch_active) and (self.gas_recovery_ticks == 0)))
      self.a_ego_filt += NIDEC_AEGO_FILTER_ALPHA * (CS.out.aEgo - self.a_ego_filt)
      if (not CS.out.gasPressed) and (self.apply_brake_last == 0): # adjust speedfactor and average_factor
        # errors are against the lagged command (see NIDEC_SERVO_LAG_FRAMES); the raw error drives the
        # gradient learners (noise averages out there), the filtered one drives the ceiling gates
        speedfactor_error = (accel_lag - CS.out.aEgo)
        speedfactor_error_f = (accel_lag - self.a_ego_filt)
        # The knee (dv_sat) is where the responsive line sf*accel meets the ceiling sf*sat_accel,
        # bounded to the range a Nidec servo can plausibly saturate in. Both sides are alpha-free:
        # with alpha inside both, dv_sent > dv_sat reduced to accel > sat_accel and the comparison
        # carried no information about the lead actually on the wire.
        # The unbounded knee is what collapsed the Pilot (route b29245576c122ee6/3a): a few
        # sustained highway pulls where the car lagged the plan dragged sat_accel down (symmetric
        # 0.002 rate, no maxed-channel evidence required), which shrank the knee, which turned
        # every undershoot into a bleed of the speed factor (rate ~ sf*(accel - sat), so it never
        # bottoms out), which cut the lead, which made the car undershoot more, until
        # HondaSatAccelParams sat on its 0.1 floor and HondaSpeedFactorParams at 0.086: the wire
        # carried PCM_SPEED = vEgo + 0.15 m/s with the plan at +0.9 m/s2, and with dv_sent > dv_sat
        # still true (0.15 > 0.1) the reductions-only ratchet made that state absorbing.
        dv_lead = sf_eff * accel_lag
        dv_sat = float(np.clip(sf_eff * self.sat_accel, NIDEC_DV_SAT_MIN, NIDEC_DV_SAT_MAX))
        in_sat = dv_lead > dv_sat
        # The knee has a mirror image: below -NIDEC_DV_SAT_MIN of lead the servo is at its coast
        # floor (PCM_SPEED has no brake authority), so a negative command that the coast cannot
        # deliver undershoots forever and err*accel_lag, both negative, is POSITIVE speed-factor
        # growth with nothing to falsify it. On the MDX the servo is linear to -2.5 m/s and the
        # error changes sign, so this never bound there; on the CR-V 2015 the coast floor is
        # -0.4 m/s2 for every lead from -1 to -40 m/s and the lead-following decels at -0.3..-0.7
        # were the largest growth term (closed-loop bench on that plant: 4 -> 20-52 without the
        # mirror, 7.5 with it from 4, 23 or 43; MDX-like plant 2.58 either way). Same remedy as
        # the positive knee: reductions only (see the ratchet below).
        in_coast = nidec_speed_channel_pinned(dv_lead, dv_sat) and not in_sat

        # average_factor learner: direct measurement (system ID), not tracking-error integration.
        # average_factor models the PCM's one-pole smoothing of our PCM_GAS commands, and
        # prior_gas_average is that model's prediction of the PCM's response. The actual response
        # is observable as the applied pedal (CAR_GAS ~= car_gas_per_pcm_gas * PCM_GAS), so move average_factor
        # along the model-fit gradient: prediction error times the recursive sensitivity computed
        # alongside the model above. The update sign flips around the PCM's true smoothing
        # constant, making the learner self-bounding: tracking error can't poison it, and at a
        # steady command rail the sensitivity decays away, so clipped/saturated frames teach it
        # nothing instead of teaching it the wrong direction. The per-tick step cap bounds noise
        # spikes; the range clip only protects the 1/average_factor feedforward division — the
        # equilibrium is interior (route 250 replay settles ~0.06-0.10, consistent with the PCM's
        # ~100ms pedal-apply lag), so it never binds.
        # gated on engine running (rpm>500): in EV mode the pedal is decoupled from PCM_GAS
        # (route 015: steady ratio 0.19 EV vs 0.47 engine-on, xcorr ~0), so EV frames would teach
        # both the scale EMA and the average_factor fit from an unrelated signal. Launch windows
        # are excluded too: the pedal applies seconds late there, which is not the smoothing
        # constant this model represents.
        if CC.longActive and (CS.out.vEgo > 1e-5) and CS.car_gas_available and \
             (CS.engine_rpm > 500) and (not self.launch_active) and (self.gas_recovery_ticks == 0):
          # car_gas_per_pcm_gas learner: direct ratio CAR_GAS / sent PCM_GAS (wire units).
          # Must use the wire command, NOT prior_gas_average: average_factor already nudges
          # prior_gas_average toward CAR_GAS/scale, so CAR_GAS/prior == scale at that joint
          # equilibrium and the scale learner never moves off its boot default (route 3b:
          # HondaCarGasScaleParams stuck at 0.3 for a full drive). Steady-wire gate skips
          # transients where the pedal lags the command.
          wire_gas = float(self.new_accel)
          if (wire_gas > 20.0) and (CS.car_gas > 5.0) and (abs(wire_gas - prior_accel) <= 1.0):
            scale_sample = CS.car_gas / wire_gas
            self.car_gas_per_pcm_gas += 0.0005 * (scale_sample - self.car_gas_per_pcm_gas)

          self.car_gas_per_pcm_gas = max(0.00001, self.car_gas_per_pcm_gas)
          gas_measured = CS.car_gas / self.car_gas_per_pcm_gas
          averagefactor_error = (gas_measured - self.prior_gas_average) / self.params.NIDEC_GAS_MAX
          averagefactor_step = 0.005 * averagefactor_error * self.average_factor_sens / self.params.NIDEC_GAS_MAX
          # This learner had been frozen since the rpm gate was added (CS.engine_rpm read 0 on the
          # MDX, see carstate), so the per-tick cap was never exercised on this car. Replaying it
          # on route 48 wire/pedal with the gate open: at +-0.001/tick it swings 0.001 <-> 0.10 on
          # a minute timescale from any start (a full-range move every second on a pedal signal
          # with ~0.01 wire correlation) and sits on the floor 157s of a 22min engaged drive. At
          # 0.001 the 1/average_factor lead is 1000x and prior_gas_average has a 10s memory, i.e.
          # the rail-to-rail bang-bang of failure mode #10. A 10x slower cap needs >=10s of
          # consistent evidence for a full-range move, and the 0.02 floor (50x lead, 0.5s
          # memory) keeps the feedforward in the sawtooth-tracking regime it has been driving in
          # at 0.035; replay band with both: 0.020-0.057 over the route.
          self.average_factor = float(np.clip(self.average_factor + np.clip(averagefactor_step, -0.0001, 0.0001),
                                              0.02, 1.0))

        # ceiling learner: identifies max accel capability, learn situation exist for a second before adjusting.
        # A ceiling is a max-type quantity, so the two directions carry different evidence and
        # run at different rates: the car demonstrably beating the estimate for a second is
        # direct proof (fast), while a deficit is only ceiling evidence when the channel is
        # provably maxed. Two tiers of "maxed":
        #  - lead at or past the DV_SAT_MAX clip with the wire pinned: surplus lead there
        #    provably does nothing (the same premise as the bleed below), so whatever the car
        #    settles at IS the ceiling, undershoot or not. Direct proof, same rate as excess.
        #  - lead at or past the DV_SAT_MIN knee floor, wire pinned, and a settled undershoot
        #    > 0.1: the servo is being pushed well beyond hold-speed and is not delivering. This
        #    can still be a soft servo the speed factor has yet to learn, so it runs 10x slower
        #    and the fast excess branch takes the estimate back up as soon as the factor catches up.
        # Neither tier is gated on in_sat: in_sat = dv_lead > min(sf*sat, DV_SAT_MAX) reduces to
        # accel > sat_accel whenever sat_accel is over-estimated, which the planner never asks
        # for, so a too-high ceiling could only be falsified by first inflating the speed factor
        # to the DV_SAT_MAX clip (bench: 3x overshoot at low commands for several drives).
        if (self.a_ego_filt > self.sat_accel) and (not CS.out.gasPressed) and (CC.longActive) and (not self.launch_active):
          self.sat_excess_frames += 1
        else:
          self.sat_excess_frames = 0
        # deficit samples are only ceiling evidence when the gas channel is in a settled state:
        # inside launch/recovery windows the pedal is provably lagging the wire (routes 33/34:
        # aEgo < 0 against cmd +1.25 while the wire ramped and the pedal applied ~2s late), so
        # counting those ticks drags sat_accel down for a gas-transient it does not own
        # (sat_accel fell 1.01 -> 0.86 between routes 33 and 34 while cruise tracking was clean).
        # lag_learn_ok / gas_pinned are the lagged frame's: a brake or launch frame a lag ago is
        # what the car is answering now, whatever this frame looks like.
        # The set-speed governor is the one place where a pinned wire plus a settled undershoot is
        # NOT the ceiling: the PCM holds ~3% under the displayed CRUISE_SPEED whatever the lead
        # (CR-V route 25: dv +11, gas 198, plan +0.7, aEgo 0.0 for 20 s at 116-117 kph / 120 set).
        # That stretch read as lead_maxed direct proof and took sat_accel 0.69 -> 0.37.
        lead_maxed = dv_lead > NIDEC_DV_SAT_MAX
        if lag_learn_ok and gas_pinned and (self.a_ego_filt < self.sat_accel) and (not set_speed_governed) and \
             (lead_maxed or ((dv_lead >= NIDEC_DV_SAT_MIN) and (speedfactor_error_f > 0.1))) and \
             (not CS.out.gasPressed) and (CC.longActive) and (not self.launch_active) and (self.gas_recovery_ticks == 0):
          self.sat_deficit_frames += 1
        else:
          self.sat_deficit_frames = 0
        if self.sat_excess_frames > 100:
          sat_rate = 0.002
        elif self.sat_deficit_frames > 150:
          sat_rate = 0.002 if lead_maxed else 0.0002
        else:
          sat_rate = 0.0
        if sat_rate > 0.0:
          self.sat_accel = float(np.clip(self.sat_accel + sat_rate * (self.a_ego_filt - self.sat_accel),
                                         NIDEC_SAT_ACCEL_MIN, self.params.NIDEC_ACCEL_MAX - 0.1))

        # recovery windows are excluded like launch windows: the undershoot there is gas-channel
        # dead time, not speed-servo response, and it was double-billed — growing/bleeding
        # sf and alpha (sf_low fell 1.27 -> 0.60 across routes 33/34, mostly in these windows).
        # Both the frame being answered (lag_learn_ok) and this one have to be clean. Near the set
        # speed the PCM's governor answers, not the servo (alpha rode to its cap there on CR-V
        # route 25 while the plan asked +0.7 against a car the PCM was holding at 0).
        if lag_learn_ok and CC.longActive and (CS.out.vEgo > 1e-5) and (not self.launch_active) and (self.gas_recovery_ticks == 0) and \
             (not set_speed_governed):
          if (speedfactor_error > 0) and (dv_lead > NIDEC_DV_SAT_MAX):
            # beyond DV_SAT_MAX surplus lead provably does nothing, so undershoot there is not
            # growth fuel (that loop is what rode speedfactor to ~511): bleed toward the clip
            # instead (min-norm: prefer the smallest lead with the same output), rate-limited
            # to 0.5%/tick. The ratchet below only prevents growth; this is the convergence
            # force that actually deflates a poisoned-high state.
            # The bleed used to run whenever dv_sent > dv_sat, i.e. whenever accel > sat_accel:
            # there its rate scales with sf itself, so it is a multiplicative decay with no
            # floor, and it is exactly what ground the Pilot's speed factor from 4.0 to 0.086.
            # Below the clip, a ceiling-limited pull is the ceiling learner's information and
            # the ratchet alone keeps it from being growth fuel.
            sf_growth = -min(0.0005 * (dv_lead - NIDEC_DV_SAT_MAX), 0.005)
          else:
            sf_growth = 0.001 * speedfactor_error * accel_lag
          # each band learns in proportion to its authority over the sent lead
          for band, w in speed_w.items():
            self.speed_factors[band] = float(np.clip(self.speed_factors[band] * (1 + w * sf_growth),
                                                     NIDEC_SPEED_FACTOR_MIN, NIDEC_SPEED_FACTOR_MAX))
            # alpha's cap used to be dv_sat itself, which is self-referential (alpha was inside
            # dv_sat) and pinned alpha at 0.1 on the Pilot once the knee had collapsed
            alpha_delta = w * 0.001 * speedfactor_error
            # Do not drag alpha down while the current plan is already asking for acceleration:
            # after lead/brake the lagged error is still negative for ~1 s and was poisoning alpha
            # into the absorbing hold-speed state described above.
            if self.accel > 0.05 and alpha_delta < 0.0:
              alpha_delta = 0.0
            self.speed_alphas[band] = float(np.clip(self.speed_alphas[band] + alpha_delta,
                                                    -NIDEC_SPEED_ALPHA_MAX, NIDEC_SPEED_ALPHA_MAX))
        if max_speedcontrol or in_sat or in_coast: # only allow learning reductions
          # speed-channel saturation is a speed-channel condition. gasfactor/gas_alpha used to
          # be ratcheted here too, which made "pcm_speed at its clip" (68% of low-speed accel
          # frames on route 51, with speedfactor_low pinned at its clamp) forbid the gas target
          # from ever growing on exactly the frames that undershoot most: the ratchet was
          # active on 10% of the gas-learner's gated ticks but those ran err +0.45 vs +0.045
          # on the rest, and it discarded +0.14 of +0.18 total ln-growth over the drive. The
          # gas learners keep their own observability gate (0 < wire < 198) above; windfactor
          # has no saturation gate of its own, so it stays.
          for band in self.speed_factors:
            self.speed_factors[band] = min(prior_speed_factors[band], self.speed_factors[band])
            self.speed_alphas[band] = min(prior_speed_alphas[band], self.speed_alphas[band])
          self.windfactor = min(prior_windfactor, self.windfactor)

    elif self.CP_SP.enableGasInterceptor or (self.CP_SP.flags & HondaFlagsSP.STOCK_LONGITUDINAL) or not CC.longActive:
      # Gas interceptor (0x201 on bus) and stock-longitudinal mode do not drive PCM_GAS via ACC_HUD
      pcm_speed = 0.0
      pcm_accel = int(0.0)
    elif self.CP.flags & HondaFlags.BOSCH:
      # Bosch: pcm_speed/pcm_accel for ACC_HUD only; gas/brake commands use separate path below
      speed_control = 0
      max_accel = np.interp(CS.out.vEgo, self.params.NIDEC_MAX_ACCEL_BP, self.params.NIDEC_MAX_ACCEL_V)
      pcm_speed_BP = [-wind_brake,
                      -wind_brake * (3 / 4),
                      0.0,
                      0.5]
      if not CC.longActive:
        pcm_speed = 0.0
        pcm_accel = int(0.0)
      else:
        pcm_speed_V = [0.0,
                       np.clip(CS.out.vEgo - 2.0, 0.0, 100.0),
                       np.clip(CS.out.vEgo + 2.0, 0.0, 100.0),
                       np.clip(CS.out.vEgo + 5.0, 0.0, 100.0)]
        pcm_speed = float(np.interp(gas - brake, pcm_speed_BP, pcm_speed_V))
        pcm_accel = int(np.clip((accel / 1.44) / max_accel, 0.0, 1.0) * self.params.NIDEC_GAS_MAX)
    if not self.CP.openpilotLongitudinalControl:
      if self.frame % 2 == 0 and not (self.CP.flags & (HondaFlags.BOSCH_RADARLESS | HondaFlags.BOSCH_CANFD)) and not (self.CP.flags & HondaFlags.NIDEC):
        can_sends.append(hondacan.create_bosch_supplemental_1(self.packer, self.CAN))
      # If using stock ACC, spam cancel command to kill gas when OP disengages.
      if pcm_cancel_cmd:
        can_sends.append(hondacan.spam_buttons_command(self.packer, self.CAN, CruiseButtons.CANCEL, 0, CS.scm_ambient_light, self.CP))
      elif CC.cruiseControl.resume:
        can_sends.append(hondacan.spam_buttons_command(self.packer, self.CAN, CruiseButtons.RES_ACCEL, 0, CS.scm_ambient_light, self.CP))

    else:
      # Send gas and brake commands.
      if self.frame % 2 == 0:
        ts = self.frame * DT_CTRL

        if self.CP.flags & HondaFlags.BOSCH:
          if (accel < 1e-3) and (CS.out.vEgo < 3.0) and not (-1e-3 < CS.out.vEgo < 1e-3):
            brake_addon = self.brake_pid.update(error = accel - CS.out.aEgo, speed = CS.out.vEgo)
            targetaccel = min(accel,accel + brake_addon)
          else:
            if self.brake_pid.i < 0.0:
              self.brake_pid.i = min(0.0, self.brake_pid.i + 0.02) # release 1m/s2 @ 50hz
            else:
              self.brake_pid.reset()
            targetaccel = min(accel,accel + self.brake_pid.i)
          if actuators.longControlState == LongCtrlState.stopping:  # simulate the old stoppingDecelRate of 0.1 m/s^2/s @ 50hz
            targetaccel = max(targetaccel, self.last_applied_brake - 0.002)
          self.last_applied_brake = targetaccel
          self.accel = float(np.clip(targetaccel, self.params.BOSCH_ACCEL_MIN, self.params.BOSCH_ACCEL_MAX))
          gas_pedal_force = targetaccel + wind_brake_ms2 * self.windfactor + hill_brake + self.gasalpha

          # live-learn gas pedal adjustments when openpilot is controlling gas
          if (actuators.longControlState == LongCtrlState.pid) and (not CS.out.gasPressed):
            gas_error = accel - CS.out.aEgo
            if self.CP.carFingerprint in (CAR.HONDA_INSIGHT, CAR.HONDA_CIVIC_BOSCH): # gas pedal reacts too slowly
              learn_speed = 150
            elif self.CP.carFingerprint in (CAR.ACURA_RDX_3G, CAR.ACURA_RDX_3G_MMR): # Prevent overreacting to turbo lag
              learn_speed = 300
            else:
              learn_speed = 50
            if gas_error != 0.0 and gas_pedal_force > 0:
              self.gasfactor = np.clip(self.gasfactor + gas_error / learn_speed * gas_pedal_force, 0.01, 3.0)
            if (-0.5 < gas_pedal_force - self.gasalpha < 0.1) and (CS.out.vEgo > 1.0):
              self.gasalpha = float(np.clip(self.gasalpha + gas_error / learn_speed / 10.0, 0.0, 0.4))
            if gas_error != 0.0 and (not CS.out.brakePressed) and (CS.out.vEgo > 0.0):
              if self.CP.carFingerprint in (CAR.ACURA_RDX_3G, CAR.ACURA_RDX_3G_MMR): # Faster reaction
                wind_learn_speed = 100
              else:
                wind_learn_speed = 1000
              wind_adjust = 1 + wind_brake_ms2 / wind_learn_speed
              self.windfactor = np.clip(self.windfactor * (wind_adjust if (gas_error > 0) else 1.0/wind_adjust), 0.1, 3.0)
            if gas_pedal_force <= 0.0: # don't reduce windfactor while braking, allow increases
              self.windfactor = max(self.windfactor, self.windfactor_before_brake)
            else:
              self.windfactor_before_brake = self.windfactor
            if gas_pedal_force >= self.params.BOSCH_ACCEL_MAX: # don't increase gasfactor nor windfactor at accel max, allow decreases
              self.gasfactor = min(self.gasfactor, self.gasfactor_before_gasmax)
              self.windfactor = min(self.windfactor, self.windfactor_before_gasmax)
            else:
              self.gasfactor_before_gasmax = self.gasfactor
              self.windfactor_before_gasmax = self.windfactor
          self.gas = float(np.interp((gas_pedal_force) * self.gasfactor,
                                     [0, self.params.BOSCH_GAS_LOOKUP_BP[1]], self.params.BOSCH_GAS_LOOKUP_V))

          # limit gas ramp to 60 units per frame, matches stock.  Higher sometimes causes powertrain to ignore gas command.
          max_gas = max(60, self.bosch_last_gas + 60)
          self.gas = min(self.gas, max_gas)
          self.bosch_last_gas = self.gas

          stopping = actuators.longControlState == LongCtrlState.stopping
          self.stopping_counter = self.stopping_counter + 1 if stopping else 0
          # CAN FD: never overlap the stock radar's own ACC_CONTROL stream; ours starts within a few
          # frames of the radar going silent (see the deferred radar disable above)
          if not (self.CP.flags & HondaFlags.BOSCH_CANFD and CS.stock_acc_alive):
            can_sends.extend(hondacan.create_acc_commands(self.packer, self.CAN, CC.enabled, CC.longActive, self.accel, self.gas,
                                                          self.stopping_counter, self.CP, gas_pedal_force))
        elif not (self.CP_SP.flags & HondaFlagsSP.STOCK_LONGITUDINAL):
          apply_brake = np.clip(self.brake_last - wind_brake, 0.0, 1.0)
          if (apply_brake > 0) and (actuators.longControlState == LongCtrlState.pid) and (CS.out.vEgo > 1e-5) and (not CS.out.stockAeb):
              if not ((self.accel >= 1e-5) and CS.out.vEgo < 1.0): # don't wind PID at launch lurch
                self.brake_pid_factor = self.nidec_brake_pid.update(error = -(self.accel - CS.out.aEgo) * apply_brake, speed = CS.out.vEgo)
          if (CS.out.vEgo >= 2): # save pid above 2m/s
            self.brake_pid_factor_non_lowspeed = self.brake_pid_factor
          if (CS.out.vEgo < 1e-5) and (self.accel < 1e-5): # gradually restore 2m/s pid after stopped
            self.nidec_brake_pid.i = float(np.clip(self.brake_pid_factor_non_lowspeed, self.nidec_brake_pid.i - 0.01, self.nidec_brake_pid.i + 0.01))
          brakefactor = 1 + self.brake_pid_factor
          if actuators.longControlState == LongCtrlState.stopping:  # simulate the old stoppingDecelRate of 0.1 m/s^2/s @ 50hz
            apply_brake = min(apply_brake * brakefactor, self.last_applied_brake + 0.00042) / brakefactor
          self.last_applied_brake = apply_brake * brakefactor
          apply_brake = int(np.clip(apply_brake * brakefactor * self.params.NIDEC_BRAKE_MAX, 0, self.params.NIDEC_BRAKE_MAX - 1))
          pump_on, self.last_pump_ts = brake_pump_hysteresis(apply_brake, self.apply_brake_last, self.last_pump_ts, ts)

          # limit brake release to 32 units per frame to match factory
          apply_brake = max(self.apply_brake_last - 32, apply_brake)

          pcm_override = CC.longActive or CS.out.stockAeb
          if apply_brake > 0: # prevent fault from concurrent gas + brake
            pcm_speed = 0.0
            self.new_accel = 0

          can_sends.append(hondacan.create_brake_command(self.packer, self.CAN, apply_brake, pump_on,
                                                         pcm_override, pcm_cancel_cmd, alert_fcw,
                                                         CS.stock_brake, self.CP_SP))
          if self.CP_SP.enableGasInterceptor:
            gas_error = actuators.accel - CS.out.aEgo
            if (not CS.out.gasPressed) and (actuators.longControlState == LongCtrlState.pid) and (self.gasint_nolearn_ticks == 0):
              if gas_error != 0.0 and gas > 0.0:
                self.gasfactor = np.clip(self.gasfactor + gas_error / 600 * (gas * 4.8), 0.1, 3.0)
              if gas_error != 0.0 and (not CS.out.brakePressed) and (CS.out.vEgo > 0.0):
                wind_adjust = 1 + (wind_brake * 4.8) / 1000
                self.windfactor = np.clip(self.windfactor * (wind_adjust if (gas_error > 0) else 1.0/wind_adjust), 0.1, 5.0)
              if gas <= 0.0: # don't reduce windfactor while braking, allow increases
                self.windfactor = max(self.windfactor, self.windfactor_before_brake)
              else:
                self.windfactor_before_brake = self.windfactor
            can_sends.extend(GasInterceptorCarController.update(self, CC, CS, gas * self.gasfactor, brake, wind_brake, self.packer, self.frame))
            self.gasint_nolearn_ticks = max(0, self.gasint_nolearn_ticks - 1)

          # during a driver-gas override the wire now carries the pedal mirror set above, so
          # the PCM tracker (and the feedforward state) stay wound to the true operating
          # point; platforms without GAS_PEDAL_2 keep the old zeroing since there is nothing
          # to mirror. (A previous branch here set 198 during gasPressed and was immediately
          # overwritten by the zeroing below — dead code, removed.)
          if (apply_brake > 0) or (CS.out.gasPressed and not CS.car_gas_available):
            self.new_accel = 0

          # openpilot brake release: the guard above held the wire at 0 for the whole brake
          # period, so the gas channel restarts from a dead state exactly like an override
          # release, and 86% of releases have the plan positive within 1s (route 48: 1.9
          # releases/min engaged). Without the window the +2/tick clip alone puts ~0.6s of the
          # ~2s post-brake deficit on the wire before the PCM's own lag even starts, and the
          # dead window was billed to the speed/gas learners as servo undershoot (45% of the
          # speedfactor_low growth fuel came from the 13% of ticks in these windows; the
          # average_factor learner saw 3.5x its usual downward per-tick pressure there).
          # Launch windows own their own release and open the window at exit.
          if (self.apply_brake_last > 0) and (apply_brake == 0) and CC.longActive and (not self.launch_active):
            self.gas_recovery_ticks = 200

          if not set_speed_governed:
            self.gas_factors_nomaxspeed = dict(self.gas_factors)
            self.gas_alphas_nomaxspeed = dict(self.gas_alphas)
          else:
            # store lower than low max speed or current
            for band in self.gas_factors:
              self.gas_factors_nomaxspeed[band] = min(self.gas_factors_nomaxspeed[band], self.gas_factors[band])
              self.gas_alphas_nomaxspeed[band] = min(self.gas_alphas_nomaxspeed[band], self.gas_alphas[band])

          self.apply_brake_last = apply_brake
          self.brake = apply_brake / self.params.NIDEC_BRAKE_MAX

    # Send dashboard UI commands. On CAN FD, ACC_HUD is a radar/ADAS look-alike that openpilot only
    # owns when it has disabled the radar (op longitudinal); in stock ACC the real system sends it and
    # the non-long safety config doesn't allowlist it.
    speed_control = 0 if self.CP.flags & HondaFlags.BOSCH else self.launch_active
    if (self.CP.flags & HondaFlags.BOSCH_CANFD) and CS.hud_tick and self.CP.openpilotLongitudinalControl and not CS.stock_acc_alive:
        can_sends.append(hondacan.create_acc_hud(self.packer, self.CAN.pt, self.CP, CC.enabled, pcm_speed, actuators.accel,
                                                 hud_control, hud_v_cruise, CS.is_metric, CS.acc_hud, speed_control,
                                                 self.CP.openpilotLongitudinalControl))

    # Send dashboard UI commands.
    if self.frame % 10 == 0:
      if self.CP.openpilotLongitudinalControl:
        if not (self.CP.flags & HondaFlags.BOSCH_CANFD):
          # On Nidec, this also controls longitudinal positive acceleration
          acc_hud_pcm_accel = self.new_accel if self.CP.openpilotLongitudinalControl and not (self.CP.flags & HondaFlags.BOSCH) and \
                              not self.CP_SP.enableGasInterceptor and not (self.CP_SP.flags & HondaFlagsSP.STOCK_LONGITUDINAL) else pcm_accel
          can_sends.append(hondacan.create_acc_hud(self.packer, self.CAN.pt, self.CP, CC.enabled, pcm_speed, acc_hud_pcm_accel,
                                                   hud_control, hud_v_cruise, CS.is_metric, CS.acc_hud, speed_control,
                                                   self.CP.openpilotLongitudinalControl))

      steering_available = CS.out.cruiseState.available and CS.out.vEgo > max(self.params.STEER_GLOBAL_MIN_SPEED, self.CP.minSteerSpeed)
      reduced_steering = CS.out.steeringPressed
      if self.CP.flags & HondaFlags.BOSCH:
        steer_maxed = abs(apply_torque) >= self.params.STEER_MAX
      else:
        steer_maxed = (abs(apply_torque) >= self.params.STEER_MAX) or not (CS.steer_control_active)

      lkas_state_change = None
      if self.CP.flags & (HondaFlags.BOSCH_RADARLESS | HondaFlags.BOSCH_CANFD):
        # Hold for 3 seconds on transitions to fade in lanes
        hud_key = CC.latActive and not steer_maxed
        if hud_key != self.lkas_hud_key:
          self.lkas_hud_key = hud_key
          self.lkas_state_change_frames = 30  # 3s at the 10Hz LKAS_HUD rate, matching stock pulse length
        lkas_state_change = self.lkas_state_change_frames > 0
        self.lkas_state_change_frames = max(0, self.lkas_state_change_frames - 1)

      can_sends.extend(hondacan.create_lkas_hud(self.packer, self.CAN.lkas, self.CP, hud_control, CC.latActive,
                                                steering_available, reduced_steering, alert_steer_required, CS.lkas_hud, self.dashed_lanes,
                                                steer_maxed, CS, lkas_state_change=lkas_state_change))

      if self.CP.openpilotLongitudinalControl:
        # TODO: combining with create_acc_hud block above will change message order and will need replay logs regenerated
        if self.CP.flags & HondaFlags.BOSCH and not (self.CP.flags & HondaFlags.BOSCH_RADARLESS) and not (self.CP.flags & HondaFlags.BOSCH_CANFD):
          can_sends.append(hondacan.create_radar_hud(self.packer, self.CAN.pt))
        if self.CP.carFingerprint == CAR.HONDA_CIVIC_BOSCH:
          can_sends.append(hondacan.create_legacy_brake_command(self.packer, self.CAN.pt))
        if not (self.CP.flags & HondaFlags.BOSCH):
          self.speed = pcm_speed
          if not self.CP_SP.enableGasInterceptor:
            self.gas = pcm_accel / self.params.NIDEC_GAS_MAX

    # Render OP's lane and lead car on the dash. On CAN FD these are radar look-alikes that only exist
    # (and are only allowed by panda safety) when the radar is disabled, i.e. openpilot longitudinal;
    # in stock ACC the real radar still owns LANE_PATH/HUD_OBJECTS, so don't author them.
    if ((self.frame % 2 == 0 and self.CP.flags & HondaFlags.BOSCH_RADARLESS) or
        (CS.radar_50hz_tick and self.CP.flags & HondaFlags.BOSCH_CANFD and self.CP.openpilotLongitudinalControl
         and not CS.stock_acc_alive)):
      leads = hud_objects.leads_from_model(self.model, CS.out.vEgo)
      lead = leads[0]
      lead_d = lead.dRel if lead.status else 0.0  # extend the lane out to the lead (0 = no lead)
      canfd = bool(self.CP.flags & HondaFlags.BOSCH_CANFD)
      self.dash_lane = self.lane_path_fitter.update(self.model, CS.out.vEgo, lead_d, canfd)
      # Important: same mux for lane_path and hud_objects. Lane display freezes if muxes don't match.
      if self.CP.flags & HondaFlags.BOSCH_CANFD:
        # self.radar_mux advances one step per 50Hz tick (above), so the mux sweep stays contiguous
        # across missed ticks, unlike a frame-derived mux.
        mux = self.radar_mux
        # No LKAS_HUD_2 on CAN FD: the dash reads the lane length from the stock radar's in-band
        # terminator, so reshape the path into the terminated-prefix form (see lane_path.py).
        lane_offsets = lane_path.canfd_lane_offsets(self.dash_lane)
      else:
        mux = lane_path.MUX_CYCLE[(self.frame // 2) % len(lane_path.MUX_CYCLE)]
        lane_offsets = self.dash_lane.offsets
      lane_msg = lane_path.create_lane_path(self.packer, self.CAN.lkas, lane_offsets, mux)
      can_sends.append(lane_msg)

      # CAN FD cars have no camera HUD_OBJECTS to poll (the disabled radar owned it), so there are no
      # secondary vehicle locations: author OP's lead in slot 0 with the other slots blank (tracks=None).
      tracks = CS.hud_object_tracker.snapshot() if CS.hud_object_tracker is not None else None
      if self.CP.openpilotLongitudinalControl:
        # For OP long, replace lead car and forward rest of objects
        hud_msg = self.hud_object_author.create(self.packer, self.CAN.lkas, lead, tracks, mux, now_nanos * 1e-9,
                                                extra_leads=leads[1:], canfd=canfd)
      else:
        # For ACC, forward objects but with our mux
        hud_msg = hud_objects.forward_hud_object(self.packer, self.CAN.lkas, mux, tracks)
      can_sends.append(hud_msg)

      # On CAN FD the camera (behind the relay) also consumes these radar look-alikes, and openpilot's
      # own TX is not forwarded across the open relay. Mirror the identical packed bytes onto the camera
      # bus (packed once above, so the counter/checksum don't double-increment and both buses match).
      if self.CP.flags & HondaFlags.BOSCH_CANFD:
        for addr, dat, _ in (lane_msg, hud_msg):
          can_sends.append((addr, dat, self.CAN.camera))

    if self.frame % 20 == 0 and self.CP.flags & HondaFlags.BOSCH_RADARLESS:
      # COUNTER_2 trails the packer's COUNTER (frame//20 % 4) by one. TODO: do we need the - 1 trail?
      dl = self.dash_lane
      can_sends.append(lane_path.create_lkas_hud_2(self.packer, self.CAN.lkas, (self.frame // 20 - 1) % 4,
                                                   dl.reach, dl.lane_cross, dl.left_line, dl.right_line))

    # Radarless + CAN FD: when stock LKAS is active, the touch-steering-wheel timer/nag eventually forces an ACC
    # disengagement (on CAN FD it shows up as a brake tap from the VSA). Disable LKAS automatically and block the
    # driver's LKAS button from reaching the camera by taking over SCM_BUTTONS on the camera bus while engaged
    # (panda blocks the forwarded stock SCM_BUTTONS when engaged; the standard button spamming isn't reliably
    # accepted by the camera).
    if self.CP.flags & (HondaFlags.BOSCH_RADARLESS | HondaFlags.BOSCH_CANFD) and CC.enabled and self.frame % 4 == 0 and \
        not pcm_cancel_cmd and not CC.cruiseControl.resume:
      if self.lkas_button_send_remaining == 0 and CS.lkas_hud["LKAS_READY"] and self.frame >= self.last_lkas_button_frame + 500:
        self.lkas_button_send_remaining = 3

      if self.lkas_button_send_remaining > 0:
        self.last_lkas_button_frame = self.frame
        self.lkas_button_send_remaining -= 1
        cruise_setting = CruiseSettings.LKAS
      elif CS.cruise_setting == CruiseSettings.LKAS:
        cruise_setting = 0  # block driver's LKAS button press
      else:
        cruise_setting = CS.cruise_setting

      can_sends.append(hondacan.spam_buttons_command(self.packer, self.CAN, CS.cruise_buttons, cruise_setting,
                                                     CS.scm_ambient_light, self.CP, bus=self.CAN.camera))

    # Intelligent Cruise Button Management
    can_sends.extend(IntelligentCruiseButtonManagementInterface.update(self, CC_SP, CS, self.packer, self.frame,
                                                                       self.last_button_frame, self.CAN))

    new_actuators = actuators.as_builder()
    new_actuators.torque = self.last_torque
    if self.CP.flags & HondaFlags.BOSCH:
      new_actuators.speed = float(self.gasalpha)
      new_actuators.accel = self.accel
      new_actuators.gas = float(self.gasfactor)
      new_actuators.brake = float(self.windfactor)
      new_actuators.torqueOutputCan = apply_torque
    else:
      new_actuators.speed = float(self.nidec_pid_factor)
      new_actuators.accel = float(self.accel)
      new_actuators.gas = float(self.average_factor)
      new_actuators.brake = float(self.sat_accel)
      new_actuators.torqueOutputCan = float(self.speed_factors["low"])

    if self.frame % 6000 == 0:
      if self.CP.flags & HondaFlags.BOSCH or self.CP_SP.enableGasInterceptor:
        # the interceptor path learns gasfactor/windfactor like Bosch (gasalpha stays at its loaded value)
        self.param_writer.put_many({
          "HondaGasAlphaParams": self.gasalpha,
          "HondaGasFactorParams": self.gasfactor,
          "HondaWindFactorParams": self.windfactor,
        })
      elif self.CP.openpilotLongitudinalControl and not (self.CP.flags & HondaFlags.BOSCH) and not self.CP_SP.enableGasInterceptor and \
           not (self.CP_SP.flags & HondaFlagsSP.STOCK_LONGITUDINAL):
        learned_values = {
          "HondaFeedForwardParams": self.average_factor,
          "HondaBrakePIDParams": self.brake_pid_factor_non_lowspeed,
          "HondaCreepFactorParams": self.creep_factor,
          "HondaWindFactorParams": self.windfactor,
          "HondaSatAccelParams": self.sat_accel,
          "HondaCarGasScaleParams": self.car_gas_per_pcm_gas,
          "HondaLaunchDvParams": self.dv_launch,
          "HondaLaunchGasParams": self.gas_launch,
          "HondaLaunchDvBreakParams": self.dv_break,
        }
        for band, _ in NIDEC_GAS_BANDS:
          learned_values[NIDEC_GAS_FACTOR_KEYS[band]] = self.gas_factors_nomaxspeed[band]
          learned_values[NIDEC_GAS_ALPHA_KEYS[band]] = self.gas_alphas_nomaxspeed[band]
        for band, _ in NIDEC_SPEED_BANDS:
          learned_values[NIDEC_SPEED_FACTOR_KEYS[band]] = self.speed_factors[band]
          learned_values[NIDEC_SPEED_ALPHA_KEYS[band]] = self.speed_alphas[band]
        self.param_writer.put_many(learned_values)

    if self.frame % 12000 == 30 and (self.CP.flags & HondaFlags.NIDEC):
      self.param_writer.put_many({
        "HondaLatAccelFactor05Params": self.latFactors["05"],
        "HondaLatAccelFactor10Params": self.latFactors["10"],
        "HondaLatAccelFactor15Params": self.latFactors["15"],
        "HondaLatAccelFactor20Params": self.latFactors["20"],
        "HondaLatAccelFactor25Params": self.latFactors["25"],
        "HondaLatAccelFactor30Params": self.latFactors["30"],
        "HondaLatAccelFactor35Params": self.latFactors["35"],
        "HondaLatAccelFactor40Params": self.latFactors["40"],
        "HondaLatAccelFactor45Params": self.latFactors["45"],
        "HondaLatAccelFactor50Params": self.latFactors["50"],
        "HondaLatAccelFactor55Params": self.latFactors["55"],
        "HondaLatAccelFactor60Params": self.latFactors["60"],
      })

    self.frame += 1
    return new_actuators, can_sends
