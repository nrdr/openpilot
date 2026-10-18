"""Firmware Controller: VFN Clarity A020 and James's Civic C020 EPS calibrations.

Uses the source controller's fixed gains, firmware-inversion feedforward, command
delay and output filter. Geometry is supplied by the shared steer-ratio selection,
just as for PIF; choosing this controller must not replace the user's ratio choice.
Optimized lane changes remain an explicit owner-requested adaptation. The command
delay ends (NrdrYawCommandDelayLow/High) remain Clarity-specific. Civic uses the
source Civic schedule plus the existing SunnyPilot port compensation. TEG-A010 has
its own calibration (the corrected PTM build's row 3, 3840 E4 per unit, its own
measured load, R6 from its A table) and keeps the C020's base gains, trims and command delay; it has
been driven on its corrected build. Insight TXM-A040 has its own calibration for its corrected PTM build
(the Clarity's own map and P table, 3840 E4 per unit, measured load, R6 from its A table)
with the C020's trims, the Civic command delay and the Clarity's model-delay schedule.
"""
import numpy as np

from openpilot.cereal import log
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.controls.lib.latcontrol import LatControl
from openpilot.nrdr.features.lateral.controller_selection import firmware_controller_profile
from openpilot.nrdr.features.lateral.vfn_eps_core import (
  CIVIC_BOSCH_C020, CIVIC_EPS_LOAD, CIVIC_I_SCALE, CIVIC_P_SCALE, CIVIC_TBA_A030, CIVIC_TBA_C120, CIVIC_TEG_A010,
  CIVIC_TEG_EPS_LOAD, CIVIC_TGG_A120, CRV_I_SCALE, CRV_P_SCALE, CRV_TLA_A040, CRV_TLA_A220, CRV_TLA_EPS_LOAD,
  INSIGHT_TXM_A040, INSIGHT_TXM_EPS_LOAD,
  HondaEpsFirmwareFeedforward, HondaEpsLateralCore,
)
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
  "civic_tgg_a120": (CIVIC_TGG_A120, CIVIC_EPS_LOAD, CIVIC_P_SCALE, CIVIC_I_SCALE),
  "civic_tba_a030": (CIVIC_TBA_A030, CIVIC_TEG_EPS_LOAD, CIVIC_P_SCALE, CIVIC_I_SCALE),
  "crv_tla_a040": (CRV_TLA_A040, CRV_TLA_EPS_LOAD, CRV_P_SCALE, CRV_I_SCALE),
  "crv_tla_a220": (CRV_TLA_A220, CRV_TLA_EPS_LOAD, CRV_P_SCALE, CRV_I_SCALE),
}


class LatControlFirmware(LatControl):
  owns_output_filter = True
  def __init__(self, CP, CP_SP, CI, dt):
    self.firmware_profile = firmware_controller_profile(CP, CP_SP)
    if self.firmware_profile is None:
      raise ValueError("Firmware control requires a supported modified EPS family with PID CarParams")
    super().__init__(CP, CP_SP, CI, dt)
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
    cloudlog.info("Firmware Controller profile=%s calibration=%s provisional=%s prediction_schedule=%s required_rwd=%s",
                  self.firmware_profile.name, self.firmware_profile.calibration,
                  self.firmware_profile.provisional, self.delay_schedule, self.firmware_profile.required_rwd or "-")
    self.cmd_delay = CommandDelay(dt)
    self.model_v2 = None
    self.prev_angle = 0.0
    self.pressed_duration = 0.0
    self.pressed_prev = False

  def update_model_v2(self, model_v2):
    self.model_v2 = model_v2

  def reset(self):
    super().reset()
    self.core.reset()
    self.pressed_duration = 0.0
    self.pressed_prev = False

  def update(self, active, CS, VM, params, steer_limited_by_safety, desired_curvature,
             calibrated_pose, curvature_limited, lat_delay):
    pid_log = log.ControlsState.LateralPIDState.new_message()
    pid_log.steeringAngleDeg = float(CS.steeringAngleDeg)
    pid_log.steeringRateDeg = float(CS.steeringRateDeg)
    delay = command_delay(self.live_tuning_snapshot, CS.vEgo, calibration=self.firmware_profile.calibration)
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
      self.reset()
      output = 0.0
    else:
      self.pressed_duration, pressed = _eps_modified_steering_pressed(
        bool(CS.steeringPressed), float(CS.steeringTorque), self.core.output,
        self.pressed_duration, self.pressed_prev)
      self.pressed_prev = pressed
      state = 0 if self.model_v2 is None else self.model_v2.meta.laneChangeState.raw
      optimized = optimized_lane_change_active(self.live_tuning_snapshot, state)
      output = self.core.update(desired, params.angleOffsetDeg, CS.steeringAngleDeg, CS.vEgo, params.roll,
                                pressed, steer_limited_by_safety, optimized_lane_change=optimized)
      output = float(np.clip(output, -self.steer_max, self.steer_max))
      pid_log.p = float(self.core.pid.p)
      pid_log.i = float(self.core.pid.i)
      pid_log.f = float(self.core.pid.f)
      pid_log.saturated = bool(self._check_saturation(
        self.steer_max - abs(output) < 1e-3, CS, steer_limited_by_safety, curvature_limited))
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
