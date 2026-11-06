"""Fresh Civic PCM coast permission, independent of the engine-braking choice."""
import math

from opendbc.car.honda.civic_pcm import uses_civic_pcm
from openpilot.cereal import log


State = log.SelfdriveState.OpenpilotState
SERVICES = ('carState', 'selfdriveState', 'radarState', 'longitudinalPlan', 'longitudinalPlanSP', 'driverMonitoringState')
# Only accommodate Float32 target conversion, not a materially reduced target.
TARGET_EPSILON_MS = 1e-5
DENIED = (False, 0.0, 0.0, 0)


def cruise_coast_context(CP, CP_SP, sm, allowance_mph: float) -> tuple[bool, float, float, int]:
  if not uses_civic_pcm(CP, CP_SP) or not sm.all_checks(SERVICES):
    return DENIED
  cs, plan, plan_sp = sm['carState'], sm['longitudinalPlan'], sm['longitudinalPlanSP']
  set_speed = cs.vCruise / 3.6
  values = (set_speed, cs.vEgo, allowance_mph, plan_sp.vTarget, plan.aTarget)
  if not all(math.isfinite(value) for value in values) or not 0 < allowance_mph <= 10 or not 5 < set_speed < 70:
    return DENIED
  # Identical to native Controls.publish's controlsState.forceDecel rule.
  # Do not subscribe to our own controlsState output (which would be one frame old).
  force_decel = bool(sm['driverMonitoringState'].noResponseForceDecel or
                     (sm['selfdriveState'].state == State.softDisabling))
  max_speed = set_speed + allowance_mph * 0.44704
  permitted = (not force_decel and not sm['selfdriveState'].experimentalMode and
               not (sm['radarState'].leadOne.present or sm['radarState'].leadTwo.present) and
               not plan.shouldStop and plan.aTarget >= 0 and plan.allowThrottle and
               str(plan.longitudinalPlanSource) == 'cruise' and str(plan_sp.longitudinalPlanSource) == 'cruise' and
               plan_sp.vTarget >= set_speed - TARGET_EPSILON_MS and
               5 < cs.vEgo <= max_speed and not (cs.gasPressed or cs.brakePressed or cs.stockAeb))
  if not permitted:
    return DENIED
  # Below-set recovery is still permitted. The receiver owns activation, checks
  # these bounds against local state and rejects stale/future/absent timestamps.
  stamp = min(sm.logMonoTime.get(name, 0) for name in SERVICES)
  return (True, set_speed, max_speed, int(stamp)) if stamp > 0 else DENIED
