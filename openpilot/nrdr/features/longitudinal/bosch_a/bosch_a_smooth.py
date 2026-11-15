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
from openpilot.nrdr.features.longitudinal.bosch_a.bosch_a_ghost import GhostLetoff
from openpilot.nrdr.features.longitudinal.bosch_a.gate import active_for, vehicle_supported

# Ghost let-off (bosch_a_ghost.py, G4 with the 1.5 s no-gas hold): the planner skips the release coast while this is on.
# nrdr enables it only with Bosch-A Radar; the donor also enabled vision-only operation.
# Donor replay (2026-11-14, main 1141 / second 99 /
# event / pb pools): score.py harder 0, real_softer 0, phantom_harder 0; 0 rows brake harder than base; cc 15:25 brake
# gone ~0.5 s sooner; 84 s7 / a2 s42 unchanged.
# ghost: replay evidence on the vasm-jetson bridge base (main 1141 / second 99 score 0/0/0, 0 rows harder); ported to nrdr, not replayed there, not driven
GHOST_ARM = True

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
    self.ghost_enabled = GHOST_ARM and active_for(CP)
    self.dt = dt
    self.rise_ticks = BRAKE_RELEASE_DWELL_TICKS + 1
    self.ghost = GhostLetoff(dt)  # ghost let-off; bosch_a_ghost.py

  def action_t(self, actuator_delay: float) -> float:
    return planner_action_t(actuator_delay, self.enabled)

  def step(self, prev: float, target: float, reset: bool, lead_one=None, raw_y: dict[int, float] | None = None,
           v_ego: float = 0.0, model_lead0=None, skip: bool = False) -> float:
    """Last shaper before the final clip. `prev` is last cycle's published target. `reset` covers disengaged and standstill.
    `lead_one`, `raw_y`, `v_ego`, `model_lead0` and `skip` (lane change, blinker or gas pressed) feed the let-off;
    a caller that passes no lead_one keeps the base let-off."""
    if not self.enabled or reset:
      self.rise_ticks = BRAKE_RELEASE_DWELL_TICKS + 1
      self.ghost.reset()
      return float(target)
    if self.ghost_enabled and lead_one is not None:
      jerk, floor = self.ghost.update(lead_one, float(prev), float(v_ego), raw_y, model_lead0, skip=skip)
      if self.ghost.no_gas:
        target = min(float(target), 0.0)
      base = brake_release_limited_target(prev, target, self.dt)
      base, self.rise_ticks = brake_release_dwell_target(prev, base, self.rise_ticks)
      if jerk is None or prev >= 0.0:
        return base
      fast = min(float(target), max(prev + BRAKE_RELEASE_JERK * self.dt, min(prev + jerk * self.dt, floor)))
      if fast > base:
        self.rise_ticks = BRAKE_RELEASE_DWELL_TICKS + 1
      return float(max(base, fast))
    target = brake_release_limited_target(prev, target, self.dt)
    target, self.rise_ticks = brake_release_dwell_target(prev, target, self.rise_ticks)
    return target
