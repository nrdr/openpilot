"""Bosch-A release coast: a lift instead of gas when a radar lead that was braking in our lane leaves it.

Owner bookmark, route 9e (replay evidence), 2026-11-07: following a car slowing to turn right, radar track 39 is
in our lane at 21 m, closing at 7 m/s, and openpilot is braking. As the car turns off, the radar lead is released at
-5.16 s (it is 1.24 m off centre). leadOne then becomes a camera lead 84-96 m away, the planner's accel target jumps
from braking to about +0.5, and the car asks for gas while the turning car is still partly in front of us. "I'd
rather it lift instead of adding gas" (owner, route 9e, 2026-11-07).

The earlier design kept a 1.8 m lateral path box around the departing track instead of reading the radar handover
directly. Census (2026-11-07) found it also re-kept a box truck in the next lane at -3.0 and cars riding the path
bend through ordinary turns, so it is not used here: this module only withholds gas off a release it can see
directly in radarState, and it never adds braking of its own.

Trigger (checked every planner cycle, previous leadOne vs current leadOne): the previous cycle's leadOne was a
present, radar-matched lead (radarTrackId >= 0) closing faster than RELEASE_VREL_MAX inside RELEASE_D_MAX, and in the
current cycle either leadOne is gone (not present) or it is a different track that jumped more than RELEASE_JUMP_M
farther away. For HOLD_S after that, the output accel is capped at 0 - it only removes positive accel, so a target
that is already braking passes through unchanged. The hold ends early if a lead within RELEASE_D_MAX that is closing
appears (the cap is harmless there, since the planner would already be braking for it). The trigger itself is
skipped during a lane change (modelV2.meta.laneChangeState != off) or with a turn signal on (carState.leftBlinker or
rightBlinker), since passing a slower car also releases its track and we want to accelerate there, and skipped while
the gas is pressed. Static/replay-evidence only, not driven.
"""
from types import SimpleNamespace

from openpilot.cereal import log
from openpilot.common.realtime import DT_MDL
from openpilot.nrdr.features.longitudinal.bosch_a.gate import vehicle_supported

RELEASE_VREL_MAX = -2.0  # m/s; previous lead must be closing at least this fast (9e: -7 m/s at release)
RELEASE_D_MAX = 40.0     # m; previous lead must be inside this (9e: 21 m at release)
RELEASE_JUMP_M = 20.0    # m; a handover lead farther than prev dRel + this counts as the same release (9e: 21 -> 84+)
HOLD_S = 1.0             # s; owner asked for "about a second" before resuming (route 9e, 2026-11-07)

LaneChangeState = log.LaneChangeState


def _closing_radar_lead(prev) -> bool:
  return (prev is not None and bool(getattr(prev, 'present', False)) and
          int(getattr(prev, 'radarTrackId', -1)) >= 0 and
          float(prev.vRel) < RELEASE_VREL_MAX and float(prev.dRel) < RELEASE_D_MAX)


def _released(prev, cur) -> bool:
  if not _closing_radar_lead(prev):
    return False
  if cur is None or not bool(getattr(cur, 'present', False)):
    return True
  return (int(getattr(cur, 'radarTrackId', -1)) != int(getattr(prev, 'radarTrackId', -1)) and
          float(cur.dRel) > float(prev.dRel) + RELEASE_JUMP_M)


def _close_closing_lead(lead) -> bool:
  return (lead is not None and bool(getattr(lead, 'present', False)) and
          float(lead.dRel) < RELEASE_D_MAX and float(lead.vRel) < 0.0)


def _snapshot(lead):
  """Copy the fields we compare, so the previous cycle never aliases a reused or rebuilt radarState lead."""
  if lead is None:
    return None
  return SimpleNamespace(present=bool(getattr(lead, 'present', False)), radarTrackId=int(getattr(lead, 'radarTrackId', -1)),
                         dRel=float(lead.dRel), vRel=float(lead.vRel))


class BoschAReleaseCoast:
  def __init__(self, CP, dt: float = DT_MDL):
    self.enabled = vehicle_supported(CP) and not bool(getattr(CP, 'radarUnavailable', True))
    self.dt = dt
    self.hold_s = 0.0
    self.prev_lead = None  # leadOne from the previous cycle

  def reset(self):
    self.hold_s = 0.0
    self.prev_lead = None

  def update(self, *, lead_one, target: float, lane_change_state=None, left_blinker: bool = False,
             right_blinker: bool = False, gas_pressed: bool = False, reset_state: bool = False) -> float:
    target = float(target)
    if not self.enabled or reset_state:
      self.reset()
      return target
    prev_lead, self.prev_lead = self.prev_lead, _snapshot(lead_one)

    skip = (lane_change_state is not None and lane_change_state != LaneChangeState.off) or left_blinker or right_blinker or gas_pressed
    if self.hold_s > 0.0:
      if skip or _close_closing_lead(lead_one):
        self.hold_s = 0.0  # a closing lead is back; the cap is harmless but the hold is done
      else:
        self.hold_s = max(0.0, self.hold_s - self.dt)

    if self.hold_s <= 0.0:
      if not skip and _released(prev_lead, lead_one):
        self.hold_s = HOLD_S

    return min(target, 0.0) if self.hold_s > 0.0 else target
