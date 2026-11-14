"""Implausible radar-drop bound on leadOne (owner bookmark, route 000000a2--794ebefbf7 seg 50, 2026-11-07).

Static tests only; no replay or road evidence for this specific bound yet.
"""
from types import SimpleNamespace
import unittest

from openpilot.selfdrive.controls.radard import RADAR_TO_CAMERA
from openpilot.nrdr.features.longitudinal.bosch_a.honda_bosch_a_long import (
    END_MODEL_DROP_MPS, IMPLAUSIBLE_DROP_DT, MAX_S, MODEL_RANGE_SHRINK_MAX_M, RETRIGGER_COOLDOWN_S,
    ImplausibleDropBound, bound_implausible_drop)


def lead(v_lead, v_rel, a_lead_k=-3.0, d_rel=18.0, track_id=24, present=True, radar=True):
  return SimpleNamespace(present=present, radar=radar, radarTrackId=track_id, dRel=d_rel, vLead=v_lead,
                          vLeadK=v_lead, vRel=v_rel, aLeadK=a_lead_k, aLeadTau=0.6)


def model(v=11.0, x=19.5, a=0.0, prob=1.0):
  return SimpleNamespace(leadsV3=[SimpleNamespace(prob=prob, x=[x], v=[v], a=[a])])


def radar_state(lead_one, lead_two=None):
  return SimpleNamespace(leadOne=lead_one, leadTwo=lead_two if lead_two is not None else
                          SimpleNamespace(present=False, radar=False, radarTrackId=-1, dRel=0., vLead=0.,
                                          vLeadK=0., vRel=0., aLeadK=0., aLeadTau=0.6))


N_WINDOW = round(0.5 / IMPLAUSIBLE_DROP_DT)  # frames spanning DROP_WINDOW_S


def run(state, v_lead_seq, v_ego=10.3, d_rel=18.0, model_v_seq=None, model_x=19.5, model_x_seq=None,
        model_prob=1.0, track_id=24):
  """Feed one radarState per v_lead in v_lead_seq; return the list of returned radarStates."""
  out = []
  for i, v_lead in enumerate(v_lead_seq):
    mv = model_v_seq[i] if model_v_seq is not None else 11.0
    mx = model_x_seq[i] if model_x_seq is not None else model_x
    rs = radar_state(lead(v_lead, v_lead - v_ego, d_rel=d_rel, track_id=track_id))
    out.append(bound_implausible_drop(rs, model(v=mv, x=mx, prob=model_prob), state))
  return out


class TestImplausibleDropBound(unittest.TestCase):
  def test_a2_shape_bounds_the_phantom_brake(self):
    """12.5 -> 2.9 over 0.7 s, model v ~11, x 19.5, radar dRel 18."""
    state = ImplausibleDropBound()
    # 14 frames @ 0.05s = 0.7s; vLead ramps 12.5 -> 2.9, model stays ~11.
    n = round(0.7 / IMPLAUSIBLE_DROP_DT)
    seq = [12.5 + (2.9 - 12.5) * i / (n - 1) for i in range(n)]
    out = run(state, seq)
    bounded = out[-1].leadOne
    self.assertGreaterEqual(bounded.vLead, 11.0 - 1.0 - 1e-6)
    self.assertGreaterEqual(bounded.aLeadK, min(0.0, 0.0) - 1e-6)
    self.assertEqual(bounded.dRel, 18.0)

  def test_real_hard_brake_untouched(self):
    """8 m/s^2: drop 4 m/s over 0.5 s stays under DROP_MPS."""
    state = ImplausibleDropBound()
    n = N_WINDOW + 1
    seq = [12.0 - 8.0 * IMPLAUSIBLE_DROP_DT * i for i in range(n)]
    out = run(state, seq, model_v_seq=[11.5 - 0.1 * i for i in range(n)])
    self.assertIs(out[-1], out[-1])  # sanity
    self.assertFalse(hasattr(out[-1].leadOne, '_lead'))

  def test_model_also_drops_untouched(self):
    state = ImplausibleDropBound()
    n = N_WINDOW + 1
    # Flat for the window, then a single-step drop in the last frame, so the radar drop and the model drop are
    # compared across the same window instead of a gradual ramp racing the trigger check frame by frame.
    seq = [12.5] * (n - 1) + [12.5 - 9.09]
    model_seq = [11.0] * (n - 1) + [11.0 - 2.0]  # camera also drops 2 m/s in the window: a real slowdown, not a glitch
    out = run(state, seq, model_v_seq=model_seq)
    self.assertFalse(hasattr(out[-1].leadOne, '_lead'))

  def test_model_range_shrinks_untouched(self):
    """Same radar drop shape as the a2 case, but the camera lead's x shrinks 1.0 m over the window: not a glitch."""
    state = ImplausibleDropBound()
    n = N_WINDOW + 1
    seq = [12.5 - 10.0 * i / n for i in range(n)]
    model_x_seq = [19.5 - 1.0 * i / (n - 1) for i in range(n)]
    out = run(state, seq, model_x_seq=model_x_seq)
    self.assertFalse(hasattr(out[-1].leadOne, '_lead'))

  def test_model_range_shrinks_under_cap_triggers(self):
    """Same shape, camera x shrinks only 0.2 m (< MODEL_RANGE_SHRINK_MAX_M): still a glitch, bound fires."""
    state = ImplausibleDropBound()
    n = N_WINDOW + 1
    self.assertLess(0.2, MODEL_RANGE_SHRINK_MAX_M)
    seq = [12.5 - 10.0 * i / n for i in range(n)]
    model_x_seq = [19.5 - 0.2 * i / (n - 1) for i in range(n)]
    out = run(state, seq, model_x_seq=model_x_seq)
    self.assertTrue(hasattr(out[-1].leadOne, '_lead'))

  def test_range_disagreement_untouched(self):
    state = ImplausibleDropBound()
    n = N_WINDOW + 1
    seq = [12.5 - 10.0 * i / n for i in range(n)]
    # model x far from radar dRel + RADAR_TO_CAMERA: disagreement of 6 m at window start.
    out = run(state, seq, d_rel=18.0, model_x=18.0 + RADAR_TO_CAMERA + 6.0)
    self.assertFalse(hasattr(out[-1].leadOne, '_lead'))

  def test_low_model_prob_untouched(self):
    state = ImplausibleDropBound()
    n = N_WINDOW + 1
    seq = [12.5 - 10.0 * i / n for i in range(n)]
    out = run(state, seq, model_prob=0.5)
    self.assertFalse(hasattr(out[-1].leadOne, '_lead'))

  def test_track_id_change_within_window_untouched(self):
    state = ImplausibleDropBound()
    n = N_WINDOW + 1
    half = n // 2
    out = []
    for i in range(n):
      v_lead = 12.5 - 10.0 * i / n
      tid = 24 if i < half else 62  # id changes mid-window
      rs = radar_state(lead(v_lead, v_lead - 10.3, track_id=tid))
      out.append(bound_implausible_drop(rs, model(), state))
    self.assertFalse(hasattr(out[-1].leadOne, '_lead'))

  def test_ends_at_max_s_and_on_model_drop(self):
    state = ImplausibleDropBound()
    n = N_WINDOW + 1
    seq = [12.5 - 10.0 * i / n for i in range(n)]
    out = run(state, seq)
    self.assertTrue(hasattr(out[-1].leadOne, '_lead'))  # active
    # hold v_lead low, model flat: bound should end once MAX_S has elapsed since trigger.
    extra_frames = round(MAX_S / IMPLAUSIBLE_DROP_DT) + 2
    for _ in range(extra_frames):
      rs = radar_state(lead(2.9, 2.9 - 10.3, track_id=24))
      out.append(bound_implausible_drop(rs, model(v=11.0), state))
    self.assertFalse(hasattr(out[-1].leadOne, '_lead'))

    # Separate run: model drops > END_MODEL_DROP_MPS since trigger -> release at once.
    state2 = ImplausibleDropBound()
    out2 = run(state2, seq)
    self.assertTrue(hasattr(out2[-1].leadOne, '_lead'))
    rs = radar_state(lead(2.9, 2.9 - 10.3, track_id=24))
    released = bound_implausible_drop(rs, model(v=11.0 - END_MODEL_DROP_MPS - 0.1), state2)
    self.assertFalse(hasattr(released.leadOne, '_lead'))

  def test_no_retrigger_within_cooldown(self):
    state = ImplausibleDropBound()
    n = N_WINDOW + 1
    seq = [12.5 - 10.0 * i / n for i in range(n)]
    run(state, seq)  # triggers partway through and is still active on track 24
    # Converge radar and model so the bound ends on track 24, arming its cooldown.
    rs = radar_state(lead(11.0, 11.0 - 10.3, track_id=24))
    out = bound_implausible_drop(rs, model(v=11.0), state)
    self.assertFalse(hasattr(out.leadOne, '_lead'))
    # Replay the same drop shape on the same track id, inside RETRIGGER_COOLDOWN_S: must not re-trigger.
    cooldown_frames = round(RETRIGGER_COOLDOWN_S / IMPLAUSIBLE_DROP_DT)
    out2 = None
    for i in range(min(cooldown_frames, n)):
      v_lead = seq[i]
      rs = radar_state(lead(v_lead, v_lead - 10.3, track_id=24))
      out2 = bound_implausible_drop(rs, model(v=11.0), state)
    self.assertFalse(hasattr(out2.leadOne, '_lead'))

  def test_no_mutation_of_radar_state_or_lead(self):
    state = ImplausibleDropBound()
    n = N_WINDOW + 1
    seq = [12.5 - 10.0 * i / n for i in range(n)]
    out = None
    original = None
    for v_lead in seq:
      original = lead(v_lead, v_lead - 10.3)
      rs = radar_state(original)
      out = bound_implausible_drop(rs, model(), state)
    self.assertEqual(original.vLead, seq[-1])
    self.assertEqual(original.aLeadK, -3.0)
    self.assertIsNot(out.leadOne, original)

  def test_vision_only_lead_untouched(self):
    state = ImplausibleDropBound()
    n = N_WINDOW + 1
    out = None
    for i in range(n):
      v_lead = 12.5 - 10.0 * i / n
      rs = radar_state(lead(v_lead, v_lead - 10.3, track_id=-1, radar=False))
      out = bound_implausible_drop(rs, model(), state)
    self.assertFalse(hasattr(out.leadOne, '_lead'))


if __name__ == '__main__':
  unittest.main()
