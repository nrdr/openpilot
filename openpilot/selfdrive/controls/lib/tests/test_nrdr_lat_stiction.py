"""LatStiction unit tests in the August package layout. See NRDR_LATERAL_STICTION.md for design and constants."""
import math
import random
import unittest

from openpilot.selfdrive.controls.lib.nrdr_lat_stiction import LatStiction

DT = 0.01
STEER_MAX = 1.0
V = 25.0


def make():
  return LatStiction(DT, STEER_MAX)


def settle_into_hold(mh, torque=0.30, n=120):
  """Feed quiet settled frames until the stage parks; returns last output."""
  out = 0.0
  for _ in range(n):
    out = mh.update(True, V, 0.0, 0.0, 0.0, torque, False, False, False)
  return out


class TestLatStiction(unittest.TestCase):

  def test_enters_hold_and_kills_dither(self):
    mh = make()
    settle_into_hold(mh)
    self.assertTrue(mh.holding)
    rng = random.Random(0)
    outs = []
    for _ in range(500):  # noisy live torque + noisy tiny error, all sub-threshold
      live = 0.30 + rng.gauss(0.0, 0.05)
      e = rng.gauss(0.0, 0.05)
      outs.append(mh.update(True, V, e, 0.0, 0.0, live, False, False, False))
    self.assertTrue(mh.holding)
    span = max(outs) - min(outs)
    self.assertLess(span, 0.01, f"held output must be dead flat, span={span:.4f}")

  def test_breakaway_on_error(self):
    mh = make()
    settle_into_hold(mh)
    e_hi = mh.E_HI_V[-1]  # at 25+ m/s within interp of (0.9, 0.4) band
    for i in range(200):
      e = min(i * 0.02, 2.0)  # error ramps up
      mh.update(True, V, e, 0.0, 0.0, 0.5, False, False, False)
      if not mh.holding:
        break
    self.assertFalse(mh.holding, "must break away when error exceeds threshold")
    self.assertLess(e, 3.0 * e_hi, "breakaway should not wait far past the threshold")

  def test_never_holds_while_plan_turns(self):
    mh = make()
    for _ in range(300):  # zero error but the plan is actively steering
      mh.update(True, V, 0.0, 5.0, 2.0, 0.4, False, False, False)
    self.assertFalse(mh.holding, "FF-led motion: never park the wheel mid-plan")

  def test_drift_budget_escapes_slow_creep(self):
    mh = make()
    settle_into_hold(mh)
    e = 0.25  # persistent sub-threshold error
    t = 0.0
    for _ in range(1000):
      mh.update(True, V, e, 0.0, 0.0, 0.4, False, False, False)
      t += DT
      if not mh.holding:
        break
    self.assertFalse(mh.holding)
    self.assertLess(t, 2.5, f"drift budget must fire ~budget/error s, took {t:.2f}s")

  def test_micro_integrator_winds_toward_error(self):
    mh = make()
    settle_into_hold(mh, torque=0.30)
    h0 = mh.hold_torque
    for _ in range(50):  # 0.5 s of +0.2 deg held error
      mh.update(True, V, 0.2, 0.0, 0.0, 0.30, False, False, False)
    self.assertGreater(mh.hold_torque, h0)
    self.assertAlmostEqual(mh.hold_torque - h0, mh.KI_HOLD * 0.2 * 0.5, delta=0.002)

  def test_transitions_are_bumpless(self):
    mh = make()
    outs = []
    rng = random.Random(1)
    for i in range(3000):  # hold -> breakaway -> move -> re-settle, five full cycles
      c = i % 600
      tri = c / 300.0 if c < 300 else (600 - c) / 300.0  # continuous 0 -> 1 -> 0
      e = 1.5 * tri
      live = 0.30 + 0.25 * tri + rng.gauss(0.0, 0.01)
      outs.append(mh.update(True, V, e, 0.0, 0.0, live, False, False, False))
    max_step = max(abs(b - a) for a, b in zip(outs, outs[1:]))
    # worst legal step: hold->live gap crossed over XFADE_S plus live noise
    self.assertLess(max_step, 0.30 / (mh.XFADE_S / DT) + 0.05, f"step {max_step:.3f}")

  def test_no_chatter_on_borderline_error(self):
    mh = make()
    settle_into_hold(mh)
    e_hi = 0.4
    transitions = 0
    prev = mh.holding
    for i in range(2000):  # 20 s hovering right at the threshold
      e = e_hi + 0.05 * math.sin(i * DT * 8.0)
      mh.update(True, V, e, 0.0, 0.0, 0.4, False, False, False)
      if mh.holding != prev:
        transitions += 1
        prev = mh.holding
    self.assertLess(transitions, 12, f"{transitions} transitions in 20s = chatter")

  def test_bypasses_are_exact_passthrough(self):
    for kwargs in (dict(pressed=True), dict(lane=True), dict(sat=True), dict(v=2.0), dict(act=False)):
      mh = make()
      settle_into_hold(mh)
      outs = []
      for i in range(60):
        live = 0.5 + 0.1 * math.sin(i * 0.3)
        outs.append(mh.update(kwargs.get("act", True), kwargs.get("v", V), 0.0, 0.0, 0.0,
                              live, kwargs.get("pressed", False), kwargs.get("lane", False),
                              kwargs.get("sat", False)))
      # after the crossfade the output must equal live exactly
      live_last = 0.5 + 0.1 * math.sin(59 * 0.3)
      self.assertAlmostEqual(outs[-1], live_last, places=9, msg=str(kwargs))
      self.assertFalse(mh.holding, str(kwargs))

  def test_hold_torque_clamped(self):
    mh = make()
    settle_into_hold(mh, torque=0.95)
    for _ in range(5000):  # wind hard for 50 s
      mh.update(True, V, 0.3, 0.0, 0.0, 0.95, False, False, False)
      if not mh.holding:
        settle_into_hold(mh, torque=0.95)
    self.assertLessEqual(abs(mh.hold_torque), STEER_MAX + 1e-9)


if __name__ == "__main__":
  unittest.main()
