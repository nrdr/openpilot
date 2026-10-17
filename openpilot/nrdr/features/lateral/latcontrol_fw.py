"""Firmware controller on stock openpilot's LatControl interface, without SunnyPilot."""
import math
import numpy as np

from openpilot.cereal import log
from openpilot.selfdrive.controls.lib.latcontrol import LatControl
from openpilot.nrdr.features.lateral.steer_ratio_tuning import SteerRatioModeLatch, resolve_steer_ratio_selection
from openpilot.nrdr.features.lateral.vfn_eps_core import (
  CIVIC_BOSCH_C020, CIVIC_EPS_LOAD, CIVIC_I_SCALE, CIVIC_P_SCALE, CIVIC_TEG_A010, CIVIC_TEG_EPS_LOAD,
  INSIGHT_TXM_A040, INSIGHT_TXM_EPS_LOAD, HondaEpsFirmwareFeedforward, HondaEpsLateralCore,
)
from openpilot.nrdr.features.lateral.yaw_control_timing import CommandDelay, command_delay


GAIN_BP = [0.0, 11.175, 11.176, 22.352]
KP, KI = [.018, .024, .048, .060], [.006, .008, .016, .020]
ANGLE_RATE_LIMIT = 300.
CALIBRATIONS = {
  "civic_bosch_c020": (CIVIC_BOSCH_C020, CIVIC_EPS_LOAD),
  "civic_teg_a010": (CIVIC_TEG_A010, CIVIC_TEG_EPS_LOAD),
  "insight_txm_a040": (INSIGHT_TXM_A040, INSIGHT_TXM_EPS_LOAD),
}


class LatControlFirmware(LatControl):
  def __init__(self, CP, CI, dt, profile, settings):
    super().__init__(CP, CI, dt)
    self.profile, self.settings = profile, settings
    self.CP = CP
    self.comma_ratio = float(CP.steerRatio)
    if profile.calibration in CALIBRATIONS:
      calibration, load = CALIBRATIONS[profile.calibration]
      self.core = HondaEpsLateralCore(GAIN_BP, KP, GAIN_BP, KI, dt,
                                    ff=HondaEpsFirmwareFeedforward(dt, cal=calibration, load=load),
                                    p_scale=CIVIC_P_SCALE, i_scale=CIVIC_I_SCALE)
    else:
      self.core = HondaEpsLateralCore(GAIN_BP, KP, GAIN_BP, KI, dt)
    self.cmd_delay = CommandDelay(dt)
    self.prev_angle = 0.
    self.lane_change_state = 0
    self.selection = resolve_steer_ratio_selection(CP, settings)
    self.geometry_latch = SteerRatioModeLatch(self.selection)

  def prepare_geometry(self, live_ratio, active=False, valid=True):
    if valid and math.isfinite(live_ratio) and live_ratio >= .1:
      self.comma_ratio = float(live_ratio)
    self.selection = self.geometry_latch.update(resolve_steer_ratio_selection(self.CP, self.settings, self.comma_ratio), active)

  def reset(self):
    super().reset()
    self.core.reset()

  def update(self, active, CS, VM, params, steer_limited_by_safety, desired_curvature, curvature_limited, lat_delay):
    pid_log = log.ControlsState.LateralPIDState.new_message()
    pid_log.steeringAngleDeg, pid_log.steeringRateDeg = float(CS.steeringAngleDeg), float(CS.steeringRateDeg)
    delay = command_delay(self.settings, CS.vEgo, calibration=self.profile.calibration)
    desired_curvature = self.cmd_delay.update(desired_curvature, delay)
    desired = self.selection.desired_angle_no_offset(VM, CS.steeringAngleDeg, CS.vEgo, params.roll, desired_curvature)
    if active:
      desired = float(np.clip(desired, self.prev_angle - ANGLE_RATE_LIMIT * self.dt, self.prev_angle + ANGLE_RATE_LIMIT * self.dt))
    self.prev_angle = desired
    angle = desired + params.angleOffsetDeg
    pid_log.steeringAngleDesiredDeg = float(angle)
    pid_log.angleError = float(angle - CS.steeringAngleDeg)
    if not active:
      self.reset()
      output = 0.
    else:
      # Do not delay or weaken the stock steeringPressed signal on bare.
      optimize = str(self.settings.get("NrdrOptimizedLaneChanges", "1")).lower() in ("1", "true", "b'1'")
      output = float(np.clip(self.core.update(
        desired, params.angleOffsetDeg, CS.steeringAngleDeg, CS.vEgo, params.roll,
        bool(CS.steeringPressed), steer_limited_by_safety,
        optimized_lane_change=optimize and self.lane_change_state in (2, 3)), -self.steer_max, self.steer_max))
      pid_log.p, pid_log.i, pid_log.f = float(self.core.pid.p), float(self.core.pid.i), float(self.core.pid.f)
      pid_log.saturated = bool(self._check_saturation(
        self.steer_max - abs(output) < 1e-3, CS, steer_limited_by_safety, curvature_limited))
    pid_log.active, pid_log.output = bool(active), output
    pid_log.epsFfActive = bool(active)
    pid_log.epsFfFeedforward = float(self.core.ff.output)
    pid_log.epsFfR5 = float(self.core.ff.r5)
    pid_log.epsFfLoad = float(self.core.ff.load)
    pid_log.epsFfDesiredRate = float(self.core.ff.rate)
    pid_log.epsFfWeight = float(self.core.ff_weight)
    pid_log.commandDelay = float(delay)
    return output, angle, pid_log
