"""Opt-in Kegman Civic speed PI and a modern selected-plan reference adapter.

Donor: kegman/openpilot 05475df8aabe1c71a502dec58516a8f7cbc522ae.
The PI's output is normalized BRAKE, not the acceleration passed to the PCM.
"""
from dataclasses import dataclass
import math

import numpy as np

from opendbc.car.honda.legacy_pcm import DT, KI_BP, KI_V, KP_BP, KP_V, brake_limit, compute_gb


def legacy_pcm_enabled(CP, CP_SP) -> bool:
  from opendbc.car.honda.pcm_test_modes import qualified
  from opendbc.car.honda.values import HondaFlags
  return qualified(CP, CP_SP, HondaFlags.NIDEC_PCM_LEGACY)


def fixed_pcm_cruise_enabled(CP, CP_SP) -> bool:
  from opendbc.car.honda.pcm_test_modes import qualified
  from opendbc.car.honda.values import HondaFlags
  return qualified(CP, CP_SP, HondaFlags.NIDEC_PCM_FIXED_CRUISE)


class LegacySpeedPI:
  """100 Hz donor PI: KF=1, KD=0, zero deadzone, converted anti-windup."""
  def __init__(self):
    self.reset()

  def reset(self):
    self.p = self.i = self.f = self.control = self.sat_count = 0.0
    self.saturated = False

  def update(self, target: float, speed: float, accel: float) -> float:
    error = target - speed
    self.p = error * float(np.interp(speed, KP_BP, KP_V))
    self.f = accel
    integral = self.i + error * float(np.interp(speed, KI_BP, KI_V)) * DT
    negative_limit = -brake_limit(speed)
    candidate = compute_gb(self.p + self.f + integral, speed)
    if ((error >= 0 and (candidate <= 0.0 or integral < 0.0)) or
        (error <= 0 and (candidate >= negative_limit or integral > 0.0))):
      self.i = integral
    control = compute_gb(self.p + self.f + self.i, speed)
    saturated = (control < negative_limit or control > 0.0) and abs(error) > 0.1
    self.sat_count = float(np.clip(self.sat_count + (DT if saturated else -DT), 0.0, 1.0))
    self.saturated = self.sat_count > 0.8
    self.control = float(np.clip(control, negative_limit, 0.0))
    return self.control


@dataclass(frozen=True)
class LegacyReference:
  speed: float
  accel: float
  future_speed: float


class SelectedPlanReference:
  """Integrate FINAL selected aTarget, never the unrelated MPC speeds array.

  The same 2 s measured-speed anchoring used by today's planner prevents drift.
  The 2 s constant-acceleration projection is only a stop/start intent estimate;
  it is not an added propulsion-speed lead. No planner publication changes.
  """
  def __init__(self):
    self.speed = None

  def reset(self):
    self.speed = None

  def update(self, v_ego: float, a_target: float, accel_limits, cruise_speed: float) -> LegacyReference:
    accel = float(np.clip(a_target, *accel_limits))
    if self.speed is None:
      self.speed = max(0.0, v_ego)
    self.speed += DT / (2.0 + DT) * (v_ego - self.speed)
    self.speed = max(0.0, self.speed + accel * DT)
    future_speed = max(0.0, self.speed + accel * 2.0)
    # The actual user target is an upper bound even when car-side cruise is 90.
    # LegacyLongControl rejects an unset/invalid target before calling here.
    if math.isfinite(cruise_speed) and 0.0 <= cruise_speed < 255.0:
      # Lowering set speed must not turn into an instantaneous speed-error step
      # (especially 0 mph). The selected deceleration determines the approach.
      self.speed = min(self.speed, max(v_ego, cruise_speed / 3.6))
      future_speed = min(future_speed, cruise_speed / 3.6)
    return LegacyReference(self.speed, accel, future_speed)


class LegacyLongControl:
  def __init__(self):
    from opendbc.car.structs import car
    self.states = car.CarControl.Actuators.LongControlState
    self.pid = LegacySpeedPI()
    self.reference = SelectedPlanReference()
    self.reset()

  def reset(self):
    self.pid.reset()
    self.reference.reset()
    self.long_control_state = self.states.off
    self.last_output_gb = self.brake = self.v_pid = self.target_accel = 0.0

  def update(self, active, CS, a_target, should_stop, accel_limits, reference_valid=True):
    finite = all(math.isfinite(x) for x in (CS.vEgo, CS.aEgo, CS.vCruise, a_target, *accel_limits))
    # vCruise is the internal kph target, not car-side PCM cruise. Zero is a
    # valid stop request; 255 is the unset sentinel. Do not rely on engagement
    # or plan freshness to reject an invalid target while already active.
    if (not active or not reference_valid or not finite or not 0.0 <= CS.vCruise < 255.0 or
        CS.gasPressed or CS.brakePressed):
      self.reset()
      return 0.0

    ref = self.reference.update(CS.vEgo, a_target, accel_limits, CS.vCruise)
    state, states = self.long_control_state, self.states
    stopping = ((CS.vEgo < 2.0 and CS.cruiseState.standstill) or
                (CS.vEgo < 0.5 and (should_stop or (self.v_pid < 0.31 and ref.future_speed < 0.31))))
    starting = ref.future_speed > 0.5 and not should_stop and not CS.cruiseState.standstill
    if state == states.off:
      state = states.pid
    elif state == states.pid and stopping:
      state = states.stopping
    elif state == states.stopping and starting:
      state = states.starting
    elif state == states.starting:
      if stopping:
        state = states.stopping
      elif self.last_output_gb >= -0.2:
        state = states.pid
    self.long_control_state = state

    output = self.last_output_gb
    if state == states.pid:
      self.v_pid = ref.speed
      output = self.pid.update(ref.speed, max(CS.vEgo, 0.3), ref.accel)
    elif state == states.stopping:
      if not CS.standstill or output > -0.25:
        output -= 0.2 * DT
      output = float(np.clip(output, -brake_limit(CS.vEgo), 0.0))
      self.v_pid = CS.vEgo
      self.pid.reset()
    elif state == states.starting:
      if output < -0.2:
        output += 0.8 * DT
      self.v_pid = CS.vEgo
      self.pid.reset()
    self.last_output_gb = output
    self.brake = -min(output, 0.0)
    # Deliberately separate planner acceleration from the PI's brake output.
    self.target_accel = ref.accel
    return self.target_accel
