"""Model-lead freshness / frame-age qualification for HumanFollowing.

Copied verbatim from SOURCE selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc.py (`_model_lead_clock_pair_ns`,
`LeadHorizon`, `HorizonVelocity`, `ModelHorizon`, `ModelLeadHistory`, `qualified_model_leads`). The planner hands
`qualified_model_leads(sm, now_ns, history)` to `human_following.upstream_lead_paths`; None (stale, mismatched or
unqualified model / radar / car frame) means the raw aLeadK extrapolation, which is never softer.
"""
import math
import time
from dataclasses import dataclass

from openpilot.nrdr.features.longitudinal.bosch_a.human_following import LEAD_T_IDXS_MODEL


def _model_lead_clock_pair_ns():
  clock = getattr(time, 'CLOCK_BOOTTIME', None)
  if clock is None:
    return None
  try:
    before = time.monotonic_ns()
    boot = time.clock_gettime_ns(clock)
    after = time.monotonic_ns()
  except OSError:
    return None
  return ((before + after) // 2, boot) if 0 <= after - before <= 1_000_000 else None


@dataclass(frozen=True)
class LeadHorizon:
  prob: float
  x: tuple[float, ...]
  y: tuple[float, ...]
  v: tuple[float, ...]
  t: tuple[float, ...]


@dataclass(frozen=True)
class HorizonVelocity:
  x: tuple[float, ...]


@dataclass(frozen=True)
class ModelHorizon:
  stamp: int
  receipt: int
  timestampEof: int
  velocity: HorizonVelocity
  leadsV3: tuple[LeadHorizon, ...]


class ModelLeadHistory:
  def __init__(self):
    self.frames = {}
    self.latest_stamp = 0

  def clear(self):
    self.frames.clear()
    self.latest_stamp = 0

  def observe(self, model, stamp, receipt):
    if stamp < self.latest_stamp:
      self.clear()
    if stamp == self.latest_stamp:
      return
    self.latest_stamp = stamp
    self.frames = {key: value for key, value in self.frames.items() if stamp - key <= 150_000_000}
    if len(model.leadsV3) < 2:
      return
    leads = []
    for index in range(2):
      lead = model.leadsV3[index]
      if any(len(getattr(lead, field)) != len(LEAD_T_IDXS_MODEL) for field in ('x', 'y', 'v', 't')):
        return
      leads.append(LeadHorizon(float(lead.prob), *(tuple(float(v) for v in getattr(lead, field)) for field in ('x', 'y', 'v', 't'))))
    self.frames[stamp] = ModelHorizon(stamp, receipt, int(model.timestampEof),
      HorizonVelocity((float(model.velocity.x[0]),)), tuple(leads))
    while len(self.frames) > 4:
      del self.frames[min(self.frames)]


def qualified_model_leads(sm, now_ns, history=None):
  try:
    pair = _model_lead_clock_pair_ns()
    if (type(now_ns) is not int or type(pair) is not tuple or len(pair) != 2 or
        any(type(value) is not int or value <= 0 for value in pair) or not 0 <= pair[0] - now_ns <= 150_000_000):
      return None
    for name in ('modelV2', 'radarState', 'carState'):
      if not all(getattr(sm, field, {}).get(name) is True for field in ('valid', 'alive', 'freq_ok')):
        return None
      stamp = sm.logMonoTime.get(name, 0)
      received = sm.recv_time.get(name, float('nan'))
      if type(received) not in (int, float) or not math.isfinite(received):
        return None
      receipt = int(received * 1e9)
      if type(stamp) is not int or not 0 < stamp <= receipt <= pair[0] or pair[0] - stamp > 150_000_000:
        return None
    model, radar, car = sm['modelV2'], sm['radarState'], sm['carState']
    eof = model.timestampEof
    eof_mono = eof - (pair[1] - pair[0])
    if (not car.canValid or car.canTimeout or any(radar.radarErrors.to_dict().values()) or
        radar.mdMonoTime <= 0 or radar.mdMonoTime > sm.logMonoTime['radarState'] or
        type(eof) is not int or not 0 < eof <= pair[1] or pair[1] - eof > 150_000_000 or
        not 0 < eof_mono <= sm.logMonoTime['modelV2'] or len(model.velocity.x) < 1 or
        not math.isfinite(float(model.velocity.x[0]))):
      return None
    if history is None:
      return model if radar.mdMonoTime == sm.logMonoTime['modelV2'] else None
    history.observe(model, sm.logMonoTime['modelV2'], int(sm.recv_time['modelV2'] * 1e9))
    selected = history.frames.get(int(radar.mdMonoTime))
    if selected is None:
      return None
    selected_eof_mono = selected.timestampEof - (pair[1] - pair[0])
    if (not 0 < selected.stamp <= selected.receipt <= pair[0] or pair[0] - selected.stamp > 150_000_000 or
        not 0 < selected.timestampEof <= pair[1] or pair[1] - selected.timestampEof > 150_000_000 or
        not 0 < selected_eof_mono <= selected.stamp):
      return None
    return selected
  except (AttributeError, IndexError, KeyError, TypeError, ValueError, OverflowError, OSError):
    return None
