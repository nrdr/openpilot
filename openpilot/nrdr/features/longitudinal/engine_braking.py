"""Fresh, free-cruise permission for the optional Civic PCM coast experiment."""
import math

from opendbc.car.honda.civic_pcm import uses_civic_pcm


class EngineBrakeSettingsReporter:
  """Record the choice consumed by controls, not just permission to activate."""
  def __init__(self):
    self.last = None

  def update(self, live, generation: int, *, enabled: bool, allowance_mph: float, supported: bool) -> None:
    signature = (enabled, allowance_mph, supported)
    if signature == self.last:
      return
    self.last = signature
    # Use the parameter worker's existing log queue: no disk I/O in controls.
    # A diagnostic failure must never affect actuation or mutate the setting.
    try:
      live.record_applied_settings("pcm_engine_braking", generation,
                                   configured_enabled=enabled, allowance_mph=allowance_mph,
                                   supported=supported)
    except Exception:
      pass


def engine_brake_context(CP, CP_SP, sm, enabled: bool, allowance_mph: float) -> tuple[bool, bool, int]:
  services = ['carState', 'selfdriveState', 'radarState', 'longitudinalPlan', 'longitudinalPlanSP']
  if not enabled or not uses_civic_pcm(CP, CP_SP) or not sm.all_checks(services):
    return False, False, 0
  cs, plan, plan_sp = sm['carState'], sm['longitudinalPlan'], sm['longitudinalPlanSP']
  set_speed = cs.vCruise / 3.6
  values = (set_speed, cs.vEgo, allowance_mph, plan_sp.vTarget, plan.aTarget)
  if not all(math.isfinite(v) for v in values) or not 0 < allowance_mph <= 10 or not 5 < set_speed < 70:
    return False, False, 0
  permitted = (not sm['selfdriveState'].experimentalMode and not plan.shouldStop and
               not (sm['radarState'].leadOne.present or sm['radarState'].leadTwo.present) and
               str(plan_sp.longitudinalPlanSource) == 'cruise' and
               str(plan.longitudinalPlanSource) == 'cruise' and plan_sp.vTarget >= set_speed - 0.01 and
               cs.vEgo > 5.0 and not (cs.gasPressed or cs.brakePressed or cs.stockAeb))
  # Outside the allowance the ordinary speed/brake controller has priority.
  permitted = bool(permitted and cs.vEgo <= set_speed + allowance_mph * 0.44704)
  stamp = min(sm.logMonoTime[name] for name in services) if permitted else 0
  return permitted, bool(permitted and cs.vEgo > set_speed), int(stamp)
