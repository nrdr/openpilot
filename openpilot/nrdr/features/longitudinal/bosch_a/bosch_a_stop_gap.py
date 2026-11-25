"""Bosch-A stop-and-go: hold the stop behind a stopped car, and no gas while crawling inside the stop gap.

Owner 2026-10-29, route 46 (00000046--852fb6caa2, 15:30-15:55, a white Audi braking over and over at walking speed):
"comma still got a little too close at times". From the car's own log (rlog seg 15, sendcan ACC_CONTROL):
  15:37.92: stopped 4.1 m behind the stopped Audi (radar vLead <= 0.42). The model's shouldStop dropped for 2 frames and
    the MPC's own stop flag was false, so longcontrol went stopping -> pid -> stopping. Those 0.1 s sent
    STANDSTILL_RELEASE=1, BRAKE_REQUEST=0 and gas 35-38; back in stopping the brake restarted from -0.06 at 0.3 m/s^3.
    The car rolled off at 15:38.40 with no pedal pressed, reached 0.73 m/s and stopped again at 2.98 m.
  15:39 and 15:52: crawling at 0.55-0.82 m/s, 3.6 m behind the Audi rolling at 0.7. The planner's own speed (the MPC
    start state) read 0.07-0.29, so its gap law saw nothing to brake for; the model asked +0.11 at 3.67 m and the car
    closed to 2.86 m.

So, on a Bosch-A Honda, with a radar lead:
  1. Stop hold: once stopped with the lead closer than HOLD_D_M and slower than RELEASE_LEAD_V, shouldStop stays on
     (no standstill release, no gas) until the lead pulls off (vLead >= RELEASE_LEAD_V and at least RELEASE_DV faster
     than us) or the radar loses it. RELEASE_LEAD_V is Dom's breakaway lead speed
     (lead_takeoff.BREAKAWAY_MIN_LEAD_SPEED), so a real departure still releases.
  2. Crawl cap: under CRAWL_V_MAX the target is capped at NO_GAS_ACCEL inside CRAWL_CLOSE_D_M unless the lead is pulling
     away at least RELEASE_DV faster than us, and from there out to CRAWL_D_M (long_mpc STOP_DISTANCE) only while the
     gap is closing. Applied across the whole 6 m on seg 15 it also cut the gas at 5-6 m while following at matched
     speed (15:26, 15:31, the lead 0.0-0.1 m/s slower), which would only make the crawl jerkier. NO_GAS_ACCEL is just under the Honda Bosch gas
     floor (CarControllerParams.BOSCH_GAS_LOOKUP_BP[0] = -0.2): above it the car sends gas, below it a brake request.
Both only ever add braking. dRel, vLead and the radar points are untouched (D-041/D-042). Static and log evidence only.
"""
from openpilot.common.realtime import DT_MDL
from openpilot.nrdr.features.longitudinal.bosch_a.gate import vehicle_supported

HOLD_D_M = 8.0           # stopped this close behind a stopped radar lead: hold (STOP_DISTANCE 6 m + 2 m of margin)
RELEASE_LEAD_V = 0.6     # m/s, lead_takeoff.BREAKAWAY_MIN_LEAD_SPEED; the stopped Audi read up to 0.42
RELEASE_DV = 0.25        # m/s faster than us counts as pulling away (lead_takeoff.departure_floor close case; 0.3 cut
                         # 46 15:48.50, the lead 0.28 faster and accelerating away)
STANDSTILL_V = 0.3       # drive_helpers.should_stop speed
CRAWL_V_MAX = 2.0        # m/s
CRAWL_D_M = 6.0          # long_mpc STOP_DISTANCE: no gas while closing
CLOSING_DV = 0.2         # m/s slower than us counts as closing (46 15:26.95 cut the gas at 0.03)
CRAWL_CLOSE_D_M = 4.5    # no gas unless the lead pulls away (46: stopped at 4.17 m was already close for the owner)
NO_GAS_ACCEL = -0.25     # m/s^2, just under the Bosch gas floor -0.2
# Earlier release (owner-approved road test 2026-11-03, route 0000007c--0ea998a750 16:59 "didn't want to move"): the gap
# opening this far past the hold minimum with the lead at least this fast also releases, and counts as pulling away until
# the gap closes again. Open-loop replay on 7c/72/75/76 + 46 seg 15: release 0/0.25/0.51 s earlier on the 8 launches that
# hold (median 0.25 s); 10 triggers in 23 standstill episodes, all real pull-aways. The stopped Audi on 46 at 15:37.9
# (vLead 0.29-0.32) opened 0.06 m. Replay only; nothing here is road-validated.
RELEASE_GROWTH_M = 0.4
RELEASE_GROWTH_LEAD_V = 0.3


def closest_radar_lead(leads):
  radar = [lead for lead in leads if lead is not None and bool(getattr(lead, 'present', False)) and
           bool(getattr(lead, 'radar', False)) and float(lead.dRel) > 0.0]
  return min(radar, key=lambda lead: float(lead.dRel)) if radar else None


def pulling_away(lead, v_ego: float) -> bool:
  v_lead = float(lead.vLead)
  return v_lead >= RELEASE_LEAD_V and v_lead - v_ego >= RELEASE_DV


class BoschAStopGap:
  def __init__(self, CP, dt: float = DT_MDL):
    # honda_bosch_a_long.active_for's gate (radar on), via the exception-safe vehicle_supported
    self.enabled = vehicle_supported(CP) and not bool(getattr(CP, 'radarUnavailable', True))
    self.dt = dt
    self.hold_d = None  # closest dRel while holding; None while not holding (replay/debug)
    self.released_d = None  # hold minimum of a gap-growth release, latched while the gap stays open

  def reset(self):
    self.hold_d = None
    self.released_d = None

  def opened(self, lead, base_d) -> bool:
    return base_d is not None and float(lead.dRel) - base_d >= RELEASE_GROWTH_M and \
      float(lead.vLead) >= RELEASE_GROWTH_LEAD_V

  @property
  def holding(self) -> bool:
    return self.hold_d is not None

  def step(self, *, lead_one, lead_two, target: float, should_stop: bool, v_ego: float, standstill: bool,
           reset_state: bool) -> tuple[float, bool]:
    """Last shaper before the final clip. Returns (target, should_stop); both only move toward more braking."""
    if not self.enabled or reset_state:
      self.reset()
      return float(target), bool(should_stop)
    lead = closest_radar_lead((lead_one, lead_two))
    if lead is None:
      self.reset()
      return float(target), bool(should_stop)
    d_rel = float(lead.dRel)

    if not self.opened(lead, self.released_d):
      self.released_d = None
    if self.hold_d is not None:
      if pulling_away(lead, v_ego):
        self.reset()
      elif self.opened(lead, self.hold_d):
        self.released_d, self.hold_d = self.hold_d, None
      else:
        self.hold_d = min(self.hold_d, d_rel)
    elif (standstill or v_ego < STANDSTILL_V) and d_rel < HOLD_D_M and \
        float(lead.vLead) < RELEASE_LEAD_V and self.released_d is None:
      self.hold_d = d_rel
    if self.holding:
      return float(min(target, NO_GAS_ACCEL)), True

    if v_ego < CRAWL_V_MAX and ((d_rel < CRAWL_CLOSE_D_M and not pulling_away(lead, v_ego) and
                                 self.released_d is None) or
                                (d_rel < CRAWL_D_M and float(lead.vLead) < v_ego - CLOSING_DV)):
      target = min(target, NO_GAS_ACCEL)
    return float(target), bool(should_stop)
