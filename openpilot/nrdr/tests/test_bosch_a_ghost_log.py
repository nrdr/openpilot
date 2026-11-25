"""bosch_a_ghost cloudlog: fire / clear / end events, and logging never changes the output."""
import random
from types import SimpleNamespace
from unittest.mock import patch

import openpilot.nrdr.features.longitudinal.bosch_a.bosch_a_release as bs

CP = SimpleNamespace(brand="honda", carFingerprint="HONDA_CIVIC_BOSCH", openpilotLongitudinalControl=True, radarUnavailable=False)


def _lead(d, v, tid=39, y=0.2):
  return SimpleNamespace(present=True, dRel=d, vRel=v, radarTrackId=tid, vLeadK=20.0 + v, aLeadK=0.0, yRel=y)


def _run(rel, steps):
  out, prev = [], -1.5
  for kw in steps:
    prev = rel.step(prev=prev, v_ego=20.0, **kw)
    out.append(prev)
  return out


def _ghost_then_moves_out():
  steps = [{"lead_one": _lead(20.0, -3.0), "target": -1.5, "raw_y": {39: 0.2}}] * 3
  steps += [{"lead_one": None, "target": 0.5, "raw_y": {39: 0.2 + 0.3 * i}} for i in range(10)]  # lead dropped, track slides out
  steps += [{"lead_one": None, "target": 0.5, "raw_y": {}}] * 70  # runs out on GHOST_MAX_S
  return steps


def test_fire_clear_end_logged():
  with patch.object(bs, 'cloudlog') as log:
    _run(bs.BoschARelease(CP), _ghost_then_moves_out())
  evs = [c.kwargs for c in log.event.call_args_list if c.args == ('bosch_a_ghost',)]
  assert [e['ev'] for e in evs] == ['fire', 'clear', 'end']
  assert evs[0]['tid'] == 39 and evs[0]['d0'] == 20.0
  assert evs[1]['how'] == 'raw_y'
  assert evs[2]['why'] == 'ttl' and evs[2]['cleared']


def test_reset_ends_a_live_ghost():
  rel = bs.BoschARelease(CP)
  with patch.object(bs, 'cloudlog') as log:
    _run(rel, _ghost_then_moves_out()[:5])
    rel.step(lead_one=None, prev=0.0, target=0.0, reset_state=True)
  evs = [c.kwargs for c in log.event.call_args_list]
  assert evs[-1]['ev'] == 'end' and evs[-1]['why'] == 'reset'


def test_logging_never_changes_output():
  rng = random.Random(7)
  for _ in range(30):
    steps = []
    for _ in range(200):
      r = rng.random()
      lead = None if r < 0.2 else _lead(rng.uniform(5, 80), rng.uniform(-6, 3), tid=rng.choice([-1, 3, 39]), y=rng.uniform(-3, 3))
      steps.append({"lead_one": lead, "target": rng.uniform(-3, 1), "raw_y": {39: rng.uniform(-4, 4)} if rng.random() < 0.7 else {},
                        "gas_pressed": rng.random() < 0.03, "reset_state": rng.random() < 0.02})
    with patch.object(bs, 'cloudlog'):
      quiet = _run(bs.BoschARelease(CP), steps)
    with patch.object(bs, 'cloudlog') as log:
      log.event.side_effect = RuntimeError('logger down')
      broken = _run(bs.BoschARelease(CP), steps)
    with patch.object(bs, '_log_ghost', lambda *a: None):
      none = _run(bs.BoschARelease(CP), steps)
    assert quiet == broken == none
