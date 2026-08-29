import math
import unittest

from openpilot.nrdr.features.lateral.lat_stiction import LatStiction, LatStictionState


DT = 0.01
STEER_MAX = 1.0
V_EGO = 25.0


def make():
  return LatStiction(DT, STEER_MAX)


def settle_into_hold(stage, torque=0.30):
  error = 1.5
  output = torque
  for _ in range(200):
    output = stage.update(True, V_EGO, error, 0.0, 5.0, torque, False, False, False)
    error = max(error - 5.0 * DT, 0.05)
  for _ in range(100):
    output = stage.update(True, V_EGO, 0.05, 0.0, 0.0, torque, False, False, False)
    if stage.holding:
      break
  return output


def sign_for_test(value):
  return 1.0 if value >= 0.0 else -1.0


class TestLatStiction(unittest.TestCase):
  def test_track_is_exact_passthrough(self):
    stage = make()
    for i in range(100):
      live = 0.4 + 0.1 * math.sin(i * 0.1)
      output = stage.update(True, V_EGO, 4.0, 0.0, 2.0, live, False, False, False)
      self.assertEqual(output, live)
      self.assertEqual(stage.state, LatStictionState.TRACK)
      self.assertFalse(stage.freeze_integrator)

  def test_predictive_capture_starts_before_crossing(self):
    stage = make()
    error = 2.0
    first_capture_error = None
    for _ in range(100):
      output = stage.update(True, V_EGO, error, 0.0, 5.0, 0.35, False, False, False)
      if stage.state is LatStictionState.CAPTURE:
        first_capture_error = error
        self.assertEqual(output, 0.35)
        output = stage.update(True, V_EGO, error - 5.0 * DT, 0.0, 5.0, 0.35,
                              False, False, False)
        self.assertLess(output, 0.35)
        break
      error -= 5.0 * DT
    self.assertIsNotNone(first_capture_error)
    self.assertGreater(first_capture_error, 0.0)
    self.assertTrue(stage.freeze_integrator)
    self.assertEqual(stage.reason, "predictive_capture")

  def test_capture_only_removes_torque_that_drives_relative_motion(self):
    stage = make()
    stage._enter(LatStictionState.CAPTURE, 0.4)
    stage._state_s = stage.CAPTURE_RAMP_S
    stage.relative_motion = 20.0

    aligned = stage.update(True, V_EGO, 0.3, 0.0, 20.0, 0.40, False, False, False)
    opposed = stage.update(True, V_EGO, -0.1, 0.0, 20.0, -0.35, False, False, False)

    self.assertAlmostEqual(aligned, 0.24)
    self.assertEqual(opposed, -0.35)
    self.assertLessEqual(abs(aligned), 0.40)
    self.assertLessEqual(abs(opposed), 0.35)

  def test_capture_never_reverses_or_amplifies_torque(self):
    for torque in (-0.9, -0.2, 0.0, 0.2, 0.9):
      for rate in (-100.0, -10.0, 0.0, 10.0, 100.0):
        stage = make()
        stage._enter(LatStictionState.CAPTURE, torque)
        output = stage.update(True, V_EGO, sign_for_test(rate), 0.0, rate, torque,
                              False, False, False)
        self.assertLessEqual(abs(output), abs(torque) + 1e-12)
        self.assertGreaterEqual(output * torque, 0.0)

  def test_crossing_does_not_restore_wrong_direction_torque(self):
    stage = make()
    stage._enter(LatStictionState.CAPTURE, 0.4)
    stage._state_s = stage.CAPTURE_RAMP_S
    stage.relative_motion = 12.0
    before = stage.update(True, V_EGO, 0.1, 0.0, 12.0, 0.4, False, False, False)
    after = stage.update(True, V_EGO, -0.1, 0.0, 12.0, 0.4, False, False, False)

    self.assertEqual(stage.state, LatStictionState.CAPTURE)
    self.assertAlmostEqual(before, after)
    self.assertLess(after, 0.4)

  def test_settled_capture_holds_equilibrium_output(self):
    stage = make()
    held_output = settle_into_hold(stage)

    self.assertEqual(stage.state, LatStictionState.HOLD)
    self.assertTrue(stage.freeze_integrator)
    self.assertAlmostEqual(held_output, stage.hold_torque)
    for i in range(100):
      live = 0.3 + 0.08 * math.sin(i * 0.2)
      self.assertEqual(stage.update(True, V_EGO, 0.05, 0.0, 0.0, live,
                                    False, False, False), held_output)

  def test_hold_breakaway_reacquires_without_step(self):
    stage = make()
    held_output = settle_into_hold(stage)
    for _ in range(round(stage.MIN_HOLD_S / DT) + 1):
      held_output = stage.update(True, V_EGO, 0.05, 0.0, 0.0, held_output,
                                 False, False, False)
    outputs = [stage.update(True, V_EGO, 0.7, 0.0, 0.0, 0.65, False, False, False)]
    self.assertEqual(stage.state, LatStictionState.REACQUIRE)
    self.assertTrue(stage.freeze_integrator)
    self.assertAlmostEqual(outputs[0], held_output)

    for _ in range(round(stage.XFADE_S / DT) + 2):
      outputs.append(stage.update(True, V_EGO, 0.7, 0.0, 0.0, 0.65, False, False, False))
    self.assertEqual(stage.state, LatStictionState.TRACK)
    self.assertFalse(stage.freeze_integrator)
    self.assertAlmostEqual(outputs[-1], 0.65)
    max_step = abs(0.65 - held_output) * DT / stage.XFADE_S
    self.assertLessEqual(max(abs(b - a) for a, b in zip(outputs, outputs[1:], strict=False)),
                         max_step + 1e-12)

  def test_reacquire_never_preserves_torque_against_live_correction(self):
    stage = make()
    stage._enter(LatStictionState.REACQUIRE, 0.10, "outer_error")

    output = stage.update(True, V_EGO, -1.0, 0.0, 0.0, -0.35,
                          False, False, False)

    self.assertEqual(output, -0.35)
    self.assertEqual(stage.state, LatStictionState.TRACK)
    self.assertEqual(stage.reason, "direction_change")

  def test_target_discontinuity_restores_live_torque_immediately(self):
    stage = make()
    stage._enter(LatStictionState.HOLD, 0.25, "capture_settled")

    output = stage.update(True, V_EGO, -4.0, -200.0, 0.0, -0.40,
                          False, False, False)

    self.assertEqual(output, -0.40)
    self.assertEqual(stage.state, LatStictionState.TRACK)
    self.assertEqual(stage.reason, "target_discontinuity")

  def test_hold_releases_for_decisive_opposite_direction_torque(self):
    stage = make()
    stage._enter(LatStictionState.HOLD, 0.20, "capture_settled")

    dither = stage.update(True, V_EGO, -0.1, 0.0, 0.0, -0.02,
                          False, False, False)
    correction = stage.update(True, V_EGO, -0.1, 0.0, 0.0, -0.10,
                              False, False, False)

    self.assertEqual(dither, 0.20)
    self.assertEqual(correction, -0.10)
    self.assertEqual(stage.state, LatStictionState.TRACK)
    self.assertEqual(stage.reason, "direction_change")

  def test_safety_bypasses_are_immediate_exact_passthrough(self):
    cases = (
      {"active": False},
      {"pressed": True},
      {"lane": True},
      {"saturated": True},
    )
    for case in cases:
      stage = make()
      settle_into_hold(stage)
      output = stage.update(case.get("active", True), V_EGO, 0.0, 0.0, 0.0, 0.73,
                            case.get("pressed", False), case.get("lane", False),
                            case.get("saturated", False))
      self.assertEqual(output, 0.73, case)
      self.assertEqual(stage.state, LatStictionState.TRACK, case)
      self.assertFalse(stage.freeze_integrator, case)

  def test_zero_speed_is_not_a_bypass(self):
    stage = make()
    output = stage.update(True, 0.0, 0.4, 0.0, 10.0, 0.5, False, False, False)
    self.assertEqual(stage.state, LatStictionState.CAPTURE)
    self.assertEqual(output, 0.5)
    output = stage.update(True, 0.0, 0.3, 0.0, 10.0, 0.5, False, False, False)
    self.assertLess(output, 0.5)

  def test_moving_target_can_capture_and_hold_relative_position(self):
    stage = make()
    error = 1.0
    for _ in range(80):
      stage.update(True, V_EGO, error, 20.0, 25.0, 0.4, False, False, False)
      error = max(error - 5.0 * DT, 0.05)
      if stage.state is LatStictionState.CAPTURE:
        break
    self.assertEqual(stage.state, LatStictionState.CAPTURE)

    for _ in range(100):
      stage.update(True, V_EGO, 0.05, 20.0, 20.0, 0.4, False, False, False)
      if stage.state is LatStictionState.HOLD:
        break
    self.assertEqual(stage.state, LatStictionState.HOLD)

  def test_target_discontinuity_does_not_capture(self):
    stage = make()
    for _ in range(100):
      output = stage.update(True, V_EGO, 0.2, 150.0, 155.0, 0.4, False, False, False)
      self.assertEqual(output, 0.4)
      self.assertEqual(stage.state, LatStictionState.TRACK)

  def test_receding_error_does_not_capture(self):
    stage = make()
    for _ in range(100):
      output = stage.update(True, V_EGO, 0.5, 0.0, -8.0, 0.4, False, False, False)
      self.assertEqual(output, 0.4)
      self.assertEqual(stage.state, LatStictionState.TRACK)

  def test_capture_entry_is_bumpless(self):
    stage = make()
    error = 1.0
    previous = 0.4
    for _ in range(100):
      output = stage.update(True, V_EGO, error, 0.0, 20.0, 0.4, False, False, False)
      if stage.state is LatStictionState.CAPTURE:
        self.assertEqual(output, previous)
        next_output = stage.update(True, V_EGO, error - 20.0 * DT, 0.0, 20.0, 0.4,
                                   False, False, False)
        self.assertLessEqual(previous - next_output, stage.MAX_TORQUE_REMOVAL * DT / stage.CAPTURE_RAMP_S)
        break
      previous = output
      error -= 20.0 * DT
    else:
      self.fail("capture never started")

  def test_left_right_symmetry(self):
    left = make()
    right = make()
    for i in range(100):
      error = 1.5 - 0.03 * i
      desired_rate = 10.0
      wheel_rate = 15.0
      live = 0.35
      left_output = left.update(True, V_EGO, error, desired_rate, wheel_rate, live,
                                False, False, False)
      right_output = right.update(True, V_EGO, -error, -desired_rate, -wheel_rate, -live,
                                  False, False, False)
      self.assertEqual(left.state, right.state)
      self.assertAlmostEqual(left_output, -right_output)

  def test_capture_torque_removal_is_capped(self):
    stage = make()
    stage._enter(LatStictionState.CAPTURE, 1.0)
    stage._state_s = stage.CAPTURE_RAMP_S
    stage.relative_motion = 100.0
    output = stage.update(True, V_EGO, 0.2, 0.0, 100.0, 1.0, False, False, False)
    self.assertAlmostEqual(output, 1.0 - stage.MAX_TORQUE_REMOVAL)


if __name__ == "__main__":
  unittest.main()
