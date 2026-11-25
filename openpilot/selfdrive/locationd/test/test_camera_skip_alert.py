import unittest
from unittest.mock import patch

import numpy as np

from openpilot.cereal import messaging
from openpilot.selfdrive.locationd.locationd import classify_camera_skip
from openpilot.selfdrive.modeld.fill_model_msg import fill_pose_msg as stock_pose
from openpilot.selfdrive.selfdrived.events import ET, EventName, Events, ImmediateDisableAlert
from openpilot.selfdrive.selfdrived.state import State, StateMachine
from openpilot.sunnypilot.modeld_v2.fill_model_msg import fill_pose_msg as sunny_pose


class TestCameraSkipAlert(unittest.TestCase):
  def setUp(self):
    self.now = 1_000_000_000
    self.outputs = {k: np.ones((1, 6)) for k in ('pose', 'pose_stds', 'wide_from_device_euler', 'road_transform',
                                                 'wide_from_device_euler_stds', 'road_transform_stds')}

  def sample(self, frame, skipped, previous, *, fill=sunny_pose, calibrated=True, other_ok=True, age_ms=80, bad_field=None):
    cam = messaging.new_message('cameraOdometry')
    fill(cam, self.outputs, frame, skipped, self.now - age_ms * 1_000_000, calibrated)
    motion = messaging.new_message('deviceMotion', valid=True, logMonoTime=self.now)
    motion.deviceMotion.inputsOK = cam.valid and other_ok
    motion.deviceMotion.sensorsOK = motion.deviceMotion.posenetOK = True
    if bad_field == 'valid':
      motion.valid = False
    elif bad_field:
      setattr(motion.deviceMotion, bad_field, False)
    prev = classify_camera_skip(motion, cam.cameraOdometry, cam.valid, other_ok, previous)
    self.assertEqual(motion.deviceMotion.inputsOK, cam.valid and other_ok)
    return motion, prev

  def test_both_publishers_and_boundary(self):
    for fill in (stock_pose, sunny_pose):
      _, previous = self.sample(30, 0, None, fill=fill)
      for skips in (1, 2, 3, 4):
        with self.subTest(fill=fill.__module__, skips=skips):
          m, after = self.sample(31 + skips, skips, previous, fill=fill)
          self.assertEqual(m.deviceMotion.isolatedCameraSkip, skips in (1, 2))
          self.assertIsNone(after)
          second, _ = self.sample(33 + skips, 1, after, fill=fill)
          self.assertFalse(second.deviceMotion.isolatedCameraSkip)

  def test_unknown_or_unhealthy_inputs_never_deferred(self):
    cases = ((32, 1, None, {}), (32, 0, 30, {'calibrated': False}), (32, 1, 30, {'calibrated': False}),
             (33, 1, 30, {}), (32, 1, 30, {'other_ok': False}), (32, 1, 30, {'age_ms': 151}),
             (32, 1, 30, {'bad_field': 'sensorsOK'}), (32, 1, 30, {'bad_field': 'posenetOK'}),
             (32, 1, 30, {'bad_field': 'valid'}))
    for frame, skipped, prev, kwargs in cases:
      with self.subTest(frame=frame, skipped=skipped, prev=prev, kwargs=kwargs):
        m, _ = self.sample(frame, skipped, prev, **kwargs)
        self.assertFalse(m.deviceMotion.isolatedCameraSkip)
    self.outputs['pose'][0, 0] = np.nan
    self.assertFalse(self.sample(32, 1, 30)[0].deviceMotion.isolatedCameraSkip)

  def test_only_presentation_waits(self):
    sm = messaging.SubMaster(['deviceMotion'])
    events = Events()
    machine = StateMachine()
    machine.state = State.enabled
    m, prev = self.sample(32, 1, 30)
    last_motion = None

    def tick(motion, now, remaining=None):
      nonlocal last_motion
      new = motion is not last_motion
      if new:
        motion.logMonoTime = now
      sm.update_msgs(now / 1e9, [motion] if new else [])
      last_motion = motion
      events.clear()
      if not motion.deviceMotion.inputsOK:
        events.add(EventName.locationdTemporaryError)
      machine.update(events)
      args = [None, None, sm, False, machine.soft_disable_timer if remaining is None else remaining, None]
      with patch('openpilot.selfdrive.selfdrived.events.time.monotonic_ns', return_value=now):
        return events.create_alerts([ET.SOFT_DISABLE], args), events.create_alerts([ET.NO_ENTRY], args)
    soft, no_entry = tick(m, self.now)
    self.assertEqual(soft, [])
    self.assertEqual(len(no_entry), 1)
    self.assertEqual(machine.state, State.softDisabling)
    self.assertTrue(events.to_msg()[0].softDisable)
    self.assertIsInstance(tick(m, self.now + 10_000_000, remaining=1)[0][0], ImmediateDisableAlert)
    self.assertTrue(tick(m, self.now + 100_000_000)[0])  # no newer pose
    second, _ = self.sample(34, 1, prev)
    self.assertTrue(tick(second, self.now + 110_000_000)[0])
    good, _ = self.sample(35, 0, None)
    self.assertEqual(tick(good, self.now + 150_000_000), ([], []))
    self.assertEqual(machine.state, State.enabled)
    severe, _ = self.sample(39, 3, 35)
    self.assertTrue(tick(severe, self.now + 200_000_000)[0])
    for i in range(1, machine.soft_disable_timer + 1):
      tick(severe, self.now + 200_000_000 + i * 10_000_000)
    self.assertEqual(machine.state, State.disabled)
