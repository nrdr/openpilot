"""Bosch-A coast first: for a distant lead tapping its brakes, lift off the gas before braking.

Owner 2026-11-01, route 71 (00000071--37216af48f) 12:03: at 70 mph a pickup 51-66 m ahead (1.6-2.0 s) braked for
about 2 s (aLeadK to -3.0, vLead 32.5 -> 25.4) and was back on the gas 1.5 s later. The planner went 0 -> -2.25 in
0.75 s. The closest gap was 50.9 m / 1.64 s. A coast at -0.5 from the same onset reaches about 49.5 m / 1.65 s
(open-loop kinematics on the logged lead, Long Sim), so the brake bought about 1.4 m. "I wouldn't mind if the car lets
go off the gas instead, then ramping up brake if needed" (owner 2026-10-20, 3a3 17:44).

While the gap is well clear, the brake is staged instead of cut: the target is floored at COAST_ACCEL when braking
starts and the floor descends at RAMP_JERK, so a lead that keeps braking still gets the full brake 1-2 s later. Every
tick re-checks a projection: the lead keeps its current decel (aLeadK, no recovery assumed) and we follow the staged
floor for HORIZON_S; if the projected gap ever drops under FLOOR_GAP_S * v + FLOOR_GAP_M, or the time gap is under
follow + GAP_MARGIN_S, or TTC, lead decel or FCW trip, the floor is dropped at once and the planner's target passes
untouched until it stops braking. It only raises a braking target (never adds gas above COAST_ACCEL, never touches the
radar points: D-041/D-042). Static and open-loop replay evidence only.

Owner 2026-11-05, route 0000008f bookmark 1 (4445.2): a car 37-40 m ahead (2.7 s, TTC 14.5 s) tapped its brakes at
about -3 for 1 s at 32 mph and we braked to -1.8. Coast first stood down on speed (14.1 < 15) and on the projection,
which held the lead's -3 for the full 3 s. "The car was still a distance away". So MIN_V_EGO is 13.5 and the
projection holds the lead's decel for LEAD_DECEL_HOLD_S, then holds the lead's speed. Replay (Long Sim, V-ASM 3b3d20056
with Stock Brake Feel and Human Following on, open loop on the logged lead): bookmark 1 coasts 1.75 s, peak -1.81 ->
-1.58, min gap unchanged (26.9 m); bookmark 2 (1.43 s gap) unchanged; 2f5 one frame later, e2ae and route 84 E1/E4
identical, 19 route-84 far brakes keep min gap and TTC; route 71 12:03 identical. Pooled 2.16 h: 14 new coasts
(37.1 -> 43.5/h), none lost, counts below -1 and -2 identical, max target change 0.18 m/s^2, closest new coast 2.29 s
gap / 9.9 s TTC. Replay only, not driven.
"""
from openpilot.common.realtime import DT_MDL
from openpilot.nrdr.features.longitudinal.bosch_a.bosch_a_stop_gap import closest_radar_lead
from openpilot.nrdr.features.longitudinal.bosch_a.gate import vehicle_supported

MIN_V_EGO = 13.5       # m/s (~30 mph); distant taps at road speed (was 15; 8f B1 at 14.1). The stop gap owns the stop.
COAST_ACCEL = -0.5     # m/s^2; lift-off plus a little (Civic gas-off at 70 mph ~ -0.4)
RAMP_JERK = 1.0        # m/s^3; staged floor: -0.5 -> -2.5 in 2 s
GAP_MARGIN_S = 0.35    # time gap must be at least follow + this (aggressive 1.25 -> 1.6; 71 12:03 bottomed at 1.64)
HORIZON_S = 3.0
LEAD_DECEL_HOLD_S = 1.5  # s; the projected lead brakes this long, then holds its speed (was the whole horizon)
FLOOR_GAP_S = 0.8      # projected gap floor: 0.8 s * v + 6 m (long_mpc STOP_DISTANCE)
FLOOR_GAP_M = 6.0
MIN_TTC_S = 5.0        # 71 12:03 at the speed low point: 51 m / 5.8 m/s = 8.8 s
MAX_LEAD_DECEL = -4.0  # m/s^2; harder than this is not a tap


def projected_gap_ok(d_rel: float, v_lead: float, a_lead: float, v_ego: float, floor_a: float) -> bool:
  a_lead = min(a_lead, 0.0)
  d, vl, ve, fa = d_rel, v_lead, v_ego, floor_a
  t = 0.0
  while t < HORIZON_S:
    d += (vl - ve) * DT_MDL
    if t < LEAD_DECEL_HOLD_S:
      vl = max(0.0, vl + a_lead * DT_MDL)
    ve = max(0.0, ve + fa * DT_MDL)
    fa -= RAMP_JERK * DT_MDL
    if d < FLOOR_GAP_S * ve + FLOOR_GAP_M:
      return False
    t += DT_MDL
  return True


class BoschACoastFirst:
  def __init__(self, CP, dt: float = DT_MDL):
    self.enabled = vehicle_supported(CP) and not bool(getattr(CP, 'radarUnavailable', True))
    self.dt = dt
    self.floor = None      # staged floor while coasting first; None when not active (replay/debug)
    self.bypassed = False  # latched for the rest of this braking event

  def reset(self):
    self.floor = None
    self.bypassed = False

  @property
  def active(self) -> bool:
    return self.floor is not None

  def step(self, *, lead_one, lead_two, target: float, v_ego: float, follow_s: float, fcw: bool,
           reset_state: bool) -> float:
    target = float(target)
    if not self.enabled or reset_state:
      self.reset()
      return target
    if target >= COAST_ACCEL:
      self.reset()  # not braking past a lift-off: the event is over
      return target
    if self.bypassed:
      return target
    lead = closest_radar_lead((lead_one, lead_two))
    floor = COAST_ACCEL if self.floor is None else self.floor - RAMP_JERK * self.dt
    if lead is None or fcw or v_ego < MIN_V_EGO or not self._clear(lead, v_ego, follow_s, floor):
      self.floor = None
      self.bypassed = True
      return target
    self.floor = floor
    return max(target, floor)

  @staticmethod
  def _clear(lead, v_ego: float, follow_s: float, floor: float) -> bool:
    d_rel, v_lead, a_lead = float(lead.dRel), float(lead.vLead), float(getattr(lead, 'aLeadK', 0.0))
    closing = v_ego - v_lead
    return (d_rel >= (follow_s + GAP_MARGIN_S) * v_ego and
            (closing <= 0.0 or d_rel / closing >= MIN_TTC_S) and
            a_lead >= MAX_LEAD_DECEL and
            projected_gap_ok(d_rel, v_lead, a_lead, v_ego, floor))
