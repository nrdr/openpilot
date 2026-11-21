"""Opt-in PTM measurement and Clarity model-blend endpoint experiment.

Keep experimental overrides here; do not retune the shared production core to
change this controller. Admission, driver override, inactivity, command limits
and model timing remain inherited from PTM. The shared geometry resolver applies
the Testing-only 250-degree endpoint to eligible Clarity models; the core is unchanged.
"""
import math
import time

from openpilot.common.swaglog import cloudlog
from openpilot.nrdr.features.lateral.latcontrol_fw import LatControlFirmware
from openpilot.nrdr.features.lateral.vfn_eps_core import HondaEpsFirmwareFeedforward, HondaEpsLateralCore


class PtmTestingFeedforward(HondaEpsFirmwareFeedforward):
  """Testing-only feedforward extension point; no experimental changes yet."""


class PtmTestingCore(HondaEpsLateralCore):
  """Capture actual state around one unchanged production-core update.

  Derived anti-windup, cap and filter attribution belongs in offline analysis,
  not a second implementation of those decisions in the control loop.
  """

  def reset(self):
    super().reset()
    self.trace = None

  def _measurement_state(self):
    return {
      "integral": float(self.pid.i), "p": float(self.pid.p), "d": float(self.pid.d), "weightedFf": float(self.pid.f),
      "ffAngleValid": self.ff.prev_angle is not None,
      "ffAngle": float(self.ff.prev_angle) if self.ff.prev_angle is not None else 0.0,
      "ffRate": float(self.ff.rate), "ffR5": float(self.ff.r5), "ffOutput": float(self.ff.output),
      "ffLoad": float(self.ff.load), "ffRamp": float(self.ff_ramp), "ffWeight": float(self.ff_weight),
      "sincePressValid": math.isfinite(self.since_press_s),
      "sincePress": float(self.since_press_s) if math.isfinite(self.since_press_s) else 0.0,
      "filterState": float(self.output_lpf.x), "filterAlpha": float(self.output_lpf.alpha), "output": float(self.output),
    }

  def update(self, desired_angle_no_offset, angle_offset, angle, v_ego, roll, steering_pressed, steer_limited,
             *, optimized_lane_change=False, override_fade_up_s=0.0):
    before = self._measurement_state()
    output = super().update(desired_angle_no_offset, angle_offset, angle, v_ego, roll, steering_pressed, steer_limited,
                            optimized_lane_change=optimized_lane_change, override_fade_up_s=override_fade_up_s)
    self.trace = {
      "coreUpdated": True, "desiredAngleNoOffset": float(desired_angle_no_offset), "angleOffset": float(angle_offset),
      "measuredAngle": float(angle), "speed": float(v_ego), "roll": float(roll),
      "effectivePressed": bool(steering_pressed), "passedSteerLimited": bool(steer_limited),
      "optimizedLaneChange": bool(optimized_lane_change), "overrideFadeUp": float(override_fade_up_s),
      "before": before, "after": self._measurement_state(),
    }
    return output


class LatControlPtmTesting(LatControlFirmware):
  core_type = PtmTestingCore
  feedforward_type = PtmTestingFeedforward
  ptm_testing = True

  def __init__(self, CP, CP_SP, CI, dt):
    super().__init__(CP, CP_SP, CI, dt)
    self._last_measurement_ns = None
    cloudlog.info("PTM Testing selected: measurement v1; eligible Clarity model blend ends at 250 degrees")

  def update(self, active, CS, VM, params, steer_limited_by_safety, desired_curvature,
             calibrated_pose, curvature_limited, lat_delay):
    entry_ns = time.monotonic_ns()
    previous_entry_ns = self._last_measurement_ns
    self._last_measurement_ns = entry_ns
    previous_angle = self.prev_angle
    previous_pressed = self.pressed_prev
    previous_pressed_duration = self.pressed_duration
    self.core.trace = None
    output, angle, pid_log = super().update(active, CS, VM, params, steer_limited_by_safety, desired_curvature,
                                           calibrated_pose, curvature_limited, lat_delay)
    trace = dict(self.core.trace or {})
    trace.update({
      "version": 1, "entryMonoTime": entry_ns, "intervalValid": previous_entry_ns is not None,
      "interval": (entry_ns - previous_entry_ns) * 1e-9 if previous_entry_ns is not None else 0.0,
      "nominalDt": float(self.dt), "rawPressed": bool(CS.steeringPressed), "driverTorque": float(CS.steeringTorque),
      "curvatureInput": float(desired_curvature), "curvatureLimited": bool(curvature_limited),
      "previousDesiredAngle": float(previous_angle), "previousPressed": bool(previous_pressed),
      "previousPressedDuration": float(previous_pressed_duration),
      "modelValid": self.model_v2 is not None,
      "modelFrameId": int(getattr(self.model_v2, "frameId", 0)),
      "modelTimestampEof": int(getattr(self.model_v2, "timestampEof", 0)),
    })
    pid_log.ptmTesting = trace
    return output, angle, pid_log
