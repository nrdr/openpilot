"""Bosch-A brake release smoothing and short plan read-ahead (always on for Bosch-A Hondas, no toggle).

Ported from openpilot-radar ns-bosch-radar-testing, where these were tuned against mvl's sp-honda-dev planner:
  ffe967495d  brake release limit: while braking, the target rises at most BRAKE_RELEASE_JERK per second.
  927f430189  brake release dwell: a brake is held BRAKE_RELEASE_DWELL_TICKS cycles before it may rise.
  b03716e918  short plan read-ahead: the MPC plan is read PLANNER_ACTION_T_S ahead instead of delay + DT_MDL.
Not ported: 75f27bd6cd (coast-ceiling slew). It smoothed an output clip that stepped when the throttle gate flipped.
Neither planner here has that clip; the gate only limits a_cruise, which get_cruise_accel already slews.

Evidence: ns replay only (16 log windows, jerk RMS 0.82x, brake onset unchanged by the release steps). The read-ahead
cost there was the hardest brake onset up to 0.3 s later and closed-loop min gap 6.0 -> 5.6 m. These numbers came from
a different planner. Here the evidence is static and unit tests only.
"""
from openpilot.common.realtime import DT_MDL
from openpilot.nrdr.features.longitudinal.bosch_a.gate import vehicle_supported

BRAKE_RELEASE_JERK = 2.5  # m/s^3
BRAKE_RELEASE_DWELL_TICKS = 2  # 0.1 s at DT_MDL
PLANNER_ACTION_T_S = 0.30  # s; never longer than the car's own delay + DT_MDL


def brake_release_limited_target(prev: float, target: float, dt: float) -> float:
  """While braking (prev < 0), the target may rise at most BRAKE_RELEASE_JERK * dt per step; it may always fall."""
  if prev >= 0.0:
    return float(target)
  return float(min(target, prev + BRAKE_RELEASE_JERK * dt))


def brake_release_dwell_target(prev: float, target: float, rise_ticks: int) -> tuple[float, int]:
  """While braking, a rise is held for the first BRAKE_RELEASE_DWELL_TICKS cycles that ask for it.
  Returns (target, rise_ticks). It only ever holds more braking, so it cannot delay brake onset."""
  if target <= prev + 1e-3:
    return float(target), 0
  rise_ticks += 1
  if prev < 0.0 and rise_ticks <= BRAKE_RELEASE_DWELL_TICKS:
    return float(prev), rise_ticks
  return float(target), rise_ticks


def planner_action_t(actuator_delay: float, enabled: bool) -> float:
  default = actuator_delay + DT_MDL
  return min(PLANNER_ACTION_T_S, default) if enabled else default


class BoschASmooth:
  def __init__(self, CP, dt: float = DT_MDL):
    self.enabled = vehicle_supported(CP)
    self.dt = dt
    self.rise_ticks = BRAKE_RELEASE_DWELL_TICKS + 1

  def action_t(self, actuator_delay: float) -> float:
    return planner_action_t(actuator_delay, self.enabled)

  def step(self, prev: float, target: float, reset: bool) -> float:
    """Last shaper before the final clip. `prev` is last cycle's published target. `reset` covers disengaged and standstill."""
    if not self.enabled or reset:
      self.rise_ticks = BRAKE_RELEASE_DWELL_TICKS + 1
      return float(target)
    target = brake_release_limited_target(prev, target, self.dt)
    target, self.rise_ticks = brake_release_dwell_target(prev, target, self.rise_ticks)
    return target
