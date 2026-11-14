"""Aragon's historical speed-error PI, isolated to the Nidec pedal selection."""
import math

from opendbc.car.honda.values import HondaFlags
from openpilot.common.pid import PIDController
from openpilot.common.realtime import DT_CTRL, DT_MDL
from openpilot.nrdr.features.longitudinal.longcontrol import NrdrLongControl, _personality_index


KP_BP = (0.0, 5.0, 35.0)
KI_BP = (0.0, 35.0)
# Aggressive, Standard, Relaxed, Econ. Deliberately not acceleration-error gains.
PERSONALITY_GAINS = (
  ((3.6, 2.4, 1.5), (0.54, 0.36)),
  ((2.4, 1.6, 1.0), (0.36, 0.24)),
  ((1.2, 0.8, 0.5), (0.18, 0.12)),
  ((0.6, 0.4, 0.25), (0.09, 0.06)),
)


def personal_pedal_enabled(CP, CP_SP):
  return bool(CP.brand == "honda" and CP.openpilotLongitudinalControl
              and CP.flags & HondaFlags.NIDEC and CP.flags & HondaFlags.PERSONAL_PEDAL
              and CP_SP.enableGasInterceptor and not CP.flags & HondaFlags.MVL_LONGITUDINAL)


def speed_reference(plan, age):
  # The MPC starts at v_desired_filter.x: the current reference carried from
  # the PREVIOUS final arbitration, corrected toward measured speed at tau=2s.
  # Only this initial point is shared by all candidates. Future MPC speeds may
  # disagree with the winning cruise/model request. Advance this point using
  # final aTarget, never an unselected future trajectory or dashboard set speed.
  if not plan.speeds or not math.isfinite(plan.speeds[0]) or not math.isfinite(plan.aTarget):
    return None
  return max(0.0, plan.speeds[0] + plan.aTarget * min(max(age, 0.0), DT_MDL))


class PersonalPedalControl(NrdrLongControl):
  def __init__(self, CP, CP_SP):
    super().__init__(CP, CP_SP)
    kp, ki = PERSONALITY_GAINS[1]
    self.pid = PIDController((KP_BP, kp), (KI_BP, ki), rate=1 / DT_CTRL)
    self.plan = None
    self.plan_age = 0.0
    self.v_pid = 0.0

  def set_plan(self, plan, updated):
    self.plan = plan
    self.plan_age = 0.0 if updated else self.plan_age + DT_CTRL

  def _update_pid_scale(self, personality, was_pid):
    index = _personality_index(personality)
    kp, ki = PERSONALITY_GAINS[1 if index is None else index]
    self.pid._k_p, self.pid._k_i = (KP_BP, kp), (KI_BP, ki)
    # This mode's four fixed profiles do not reinterpret saved Standard sliders.
    self.pid_scale = 1.0

  def _accel_limits(self, accel_limits, v_ego):
    return accel_limits

  def _pid_accel(self, CS, a_target):
    reference = speed_reference(self.plan, self.plan_age) if self.plan is not None else None
    self.v_pid = CS.vEgo if reference is None else reference
    if reference is None:
      self.pid.reset()
    return self.pid.update(self.v_pid - CS.vEgo, speed=CS.vEgo, feedforward=a_target,
                           freeze_integrator=reference is None)
