"""PTM Controller using Biscuit-Labs 45e5b91fae firmware calibrations and fixed timing.

Shared steer-ratio selection, driver override and model-scoped Optimized Lane Changes
remain nrdr features. Plan models use no extra command delay; other model sources use
the calibration's hardcoded delay, with the donor's one-second transition between them.
"""
import math

import numpy as np

from openpilot.cereal import log
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.controls.lib.latcontrol import LatControl
from openpilot.nrdr.features.lateral.controller_selection import firmware_controller_profile
from openpilot.nrdr.features.lateral.vfn_eps_core import (
  CIVIC_BOSCH_C020, CIVIC_EPS_LOAD, CIVIC_I_SCALE, CIVIC_P_SCALE, CIVIC_TBA_A030, CIVIC_TBA_C120, CIVIC_TEG_A010,
  CIVIC_TEG_EPS_LOAD, CIVIC_TGG_A120, CIVIC_TGG_EPS_LOAD, CRV_I_SCALE, CRV_P_SCALE, CRV_TLA_A040, CRV_TLA_A220, CRV_TLA_EPS_LOAD,
  INSIGHT_TXM_A040, INSIGHT_TXM_EPS_LOAD, RDX_TJB_A220, RDX_TJB_EPS_LOAD,
  ODYSSEY_THR_A020, ODYSSEY_THR_EPS_LOAD, RIDGELINE_T6Z_A110, RIDGELINE_T6Z_EPS_LOAD,
  HondaEpsFirmwareFeedforward, HondaEpsLateralCore,
)
from openpilot.nrdr.features.lateral.model_source import CMD_DELAY_RAMP_S, PLAN
from openpilot.nrdr.features.lateral.yaw_control_timing import CommandDelay, command_delay, prediction_delay_schedule
from openpilot.nrdr.features.lateral.latcontrol_pid import _eps_modified_steering_pressed
from openpilot.nrdr.features.lateral.lane_change_tuning import optimized_lane_change_active

VFN_SOURCE_COMMIT = "f837ca86a639b1c20a0ce23bb8acf0ebbc6a05d4"
GAIN_BP = [0.0, 11.175, 11.176, 22.352]
KP = [0.018, 0.024, 0.048, 0.060]
KI = [0.006, 0.008, 0.016, 0.020]
ANGLE_RATE_LIMIT = 300.0
# Calibrations with their own image constants, column load and residual-PID trims; the Clarity uses the module defaults.
_OWN_CALIBRATIONS = {
  "civic_bosch_c020": (CIVIC_BOSCH_C020, CIVIC_EPS_LOAD, CIVIC_P_SCALE, CIVIC_I_SCALE),
  "civic_teg_a010": (CIVIC_TEG_A010, CIVIC_TEG_EPS_LOAD, CIVIC_P_SCALE, CIVIC_I_SCALE),
  "insight_txm_a040": (INSIGHT_TXM_A040, INSIGHT_TXM_EPS_LOAD, CIVIC_P_SCALE, CIVIC_I_SCALE),
  # Corrected-PTM starting calibrations: load and trims carried from the nearest measured car (see vfn_eps_core)
  "civic_tba_c120": (CIVIC_TBA_C120, CIVIC_EPS_LOAD, CIVIC_P_SCALE, CIVIC_I_SCALE),
  "civic_tgg_a120": (CIVIC_TGG_A120, CIVIC_TGG_EPS_LOAD, CIVIC_P_SCALE, CIVIC_I_SCALE),
  "civic_tba_a030": (CIVIC_TBA_A030, CIVIC_TEG_EPS_LOAD, CIVIC_P_SCALE, CIVIC_I_SCALE),
  "crv_tla_a040": (CRV_TLA_A040, CRV_TLA_EPS_LOAD, CRV_P_SCALE, CRV_I_SCALE),
  "crv_tla_a220": (CRV_TLA_A220, CRV_TLA_EPS_LOAD, CRV_P_SCALE, CRV_I_SCALE),
  "rdx_tjb_a220": (RDX_TJB_A220, RDX_TJB_EPS_LOAD, (1., 1., 0.7), (1., 1., 1.)),
  "odyssey_thr_a020": (ODYSSEY_THR_A020, ODYSSEY_THR_EPS_LOAD, (1., 1., 0.7), (1., 1., 1.)),
  "ridgeline_t6z_a110": (RIDGELINE_T6Z_A110, RIDGELINE_T6Z_EPS_LOAD, (1., 1., 1.), (1., 1., 1.)),
}


class LatControlFirmware(LatControl):
  owns_output_filter = True
  def __init__(self, CP, CP_SP, CI, dt):
    self.firmware_profile = firmware_controller_profile(CP, CP_SP)
    if self.firmware_profile is None:
      raise ValueError("PTM Controller requires a supported modified EPS family with PID CarParams")
    super().__init__(CP, CP_SP, CI, dt)
    honda_config = getattr(getattr(CI, "interface_config", None), "honda", None)
    self.honda_params_provider = getattr(honda_config, "provider", None)
    self.delay_schedule = prediction_delay_schedule(self.firmware_profile)
    if self.firmware_profile.calibration in _OWN_CALIBRATIONS:
      # Source Bosch base gains as well as its fixed trims, also on the TEG and the Insight, whose
      # trims are not measured. Never retune CP or increase CAN/safety limits.
      cal, load, p_scale, i_scale = _OWN_CALIBRATIONS[self.firmware_profile.calibration]
      self.core = HondaEpsLateralCore(GAIN_BP, KP, GAIN_BP, KI, dt,
        ff=HondaEpsFirmwareFeedforward(dt, cal=cal, load=load),
        p_scale=p_scale, i_scale=i_scale)
    else:
      self.core = HondaEpsLateralCore(GAIN_BP, KP, GAIN_BP, KI, dt)
    cloudlog.info("PTM Controller profile=%s calibration=%s provisional=%s prediction_schedule=%s required_rwd=%s",
                  self.firmware_profile.name, self.firmware_profile.calibration,
                  self.firmware_profile.provisional, self.delay_schedule, self.firmware_profile.required_rwd or "-")
    self.cmd_delay = CommandDelay(dt)
    self.cmd_delay_scale = 1.0
    self.model_v2 = None
    self.prev_angle = 0.0
    self.pressed_duration = 0.0
    self.pressed_prev = False
    self.inactive_frames = math.inf
    self.ride_through_frames = int(round(0.1 / dt)) if self.firmware_profile.calibration in ("rdx_tjb_a220", "odyssey_thr_a020") else 0

  def update_model_v2(self, model_v2):
    self.model_v2 = model_v2

  def _command_delay(self, v_ego: float) -> float:
    action = getattr(self.model_v2, "action", None)
    target = 0.0 if str(getattr(action, "lateralSource", "unknown")) == PLAN else 1.0
    step = self.dt / CMD_DELAY_RAMP_S
    self.cmd_delay_scale += max(min(target - self.cmd_delay_scale, step), -step)
    return self.cmd_delay_scale * command_delay(None, v_ego, calibration=self.firmware_profile.calibration)

  def reset(self):
    if self.ride_through_frames == 0 or self.inactive_frames > self.ride_through_frames:
      self._hard_reset()

  def _hard_reset(self):
    super().reset()
    self.core.reset()
    self.pressed_duration = 0.0
    self.pressed_prev = False

  def update(self, active, CS, VM, params, steer_limited_by_safety, desired_curvature,
             calibrated_pose, curvature_limited, lat_delay):
    pid_log = log.ControlsState.LateralPIDState.new_message()
    pid_log.steeringAngleDeg = float(CS.steeringAngleDeg)
    pid_log.steeringRateDeg = float(CS.steeringRateDeg)
    delay = self._command_delay(CS.vEgo)
    desired_curvature = self.cmd_delay.update(desired_curvature, delay)
    desired = self.steer_ratio_selection.desired_angle_no_offset(
      VM, CS.steeringAngleDeg, CS.vEgo, params.roll, desired_curvature)
    if active:
      step = ANGLE_RATE_LIMIT * self.dt
      desired = float(np.clip(desired, self.prev_angle - step, self.prev_angle + step))
    self.prev_angle = desired
    angle = desired + params.angleOffsetDeg
    pid_log.steeringAngleDesiredDeg = angle
    pid_log.angleError = angle - CS.steeringAngleDeg
    if not active:
      self.inactive_frames += 1
      if self.inactive_frames > self.ride_through_frames:
        self._hard_reset()
      else:
        # Donor's brief TJB/THR dropout handling: track internally, freeze I, send zero.
        self.core.update(desired, params.angleOffsetDeg, CS.steeringAngleDeg, CS.vEgo, params.roll, False, True)
      output = 0.0
    else:
      self.inactive_frames = 0
      self.pressed_duration, pressed = _eps_modified_steering_pressed(
        bool(CS.steeringPressed), float(CS.steeringTorque), self.core.output,
        self.pressed_duration, self.pressed_prev)
      self.pressed_prev = pressed
      state = 0 if self.model_v2 is None else self.model_v2.meta.laneChangeState.raw
      optimized = optimized_lane_change_active(self.live_tuning_snapshot, state)
      # Share the car controller's already-refreshed recovery setting; no new Params reads or polling.
      override_fade_up_s = (self.honda_params_provider.get_live_tuning(refresh_if_uninitialized=False).override_fade_up_s
                            if self.honda_params_provider is not None else 0.0)
      output = self.core.update(desired, params.angleOffsetDeg, CS.steeringAngleDeg, CS.vEgo, params.roll,
                                pressed, steer_limited_by_safety, optimized_lane_change=optimized,
                                override_fade_up_s=override_fade_up_s)
      # A command row may stop adding assist before the host's normalized limit.
      # Saturation reporting must follow the same usable ceiling as the core.
      output_limit = min(self.steer_max, self.core.ff.cal.output_ceiling())
      output = float(np.clip(output, -output_limit, output_limit))
      pid_log.p = float(self.core.pid.p)
      pid_log.i = float(self.core.pid.i)
      pid_log.f = float(self.core.pid.f)
      pid_log.saturated = bool(self._check_saturation(
        output_limit - abs(output) < 1e-3, CS, steer_limited_by_safety, curvature_limited))
    ff = self.core.ff
    pid_log.epsFfActive = bool(active)
    pid_log.epsFfWeight = float(self.core.ff_weight)
    pid_log.epsFfFeedforward = float(ff.output)
    pid_log.epsFfR5 = float(ff.r5)
    pid_log.epsFfLoad = float(ff.load)
    pid_log.epsFfDesiredRate = float(ff.rate)
    pid_log.commandDelay = float(delay)
    pid_log.active = bool(active)
    pid_log.output = output
    return output, angle, pid_log
