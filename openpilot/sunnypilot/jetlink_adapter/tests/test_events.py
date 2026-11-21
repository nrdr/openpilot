"""Exercise the real swap timer and its driver-visible fallback warning."""
from types import SimpleNamespace
from unittest import mock

from jetlink.openpilot.events import SwapEvents
from openpilot.common.realtime import DT_CTRL
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.selfdrived.events import Events, EventName
from openpilot.sunnypilot.selfdrive.selfdrived.accelerator_events import AcceleratorEvents, EventNameSP
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP, EVENTS_SP
from openpilot.sunnypilot.selfdrive.selfdrived.events_base import ET


class ModelMessages(dict):
  seen = alive = valid = {"modelV2": True}


class TestFallbackEvents(OpenpilotTestCase):
  def setUp(self):
    super().setUp()
    self.state = "running"
    self.swap = SwapEvents(DT_CTRL)
    tracker = SimpleNamespace(update=lambda fresh, big, engaged: self.swap.update(fresh, big, engaged, self.state))
    with mock.patch("openpilot.sunnypilot.jetlink_adapter.swap_events", return_value=tracker):
      self.accelerator = AcceleratorEvents()
    self.sm = ModelMessages(modelV2=SimpleNamespace(big=True))

  def tick(self, engaged=True):
    events, events_sp = Events(), EventsSP()
    self.accelerator.update(self.sm, engaged, events, events_sp)
    return events, events_sp

  def test_loss_warns_for_five_seconds_without_disengaging(self):
    self.tick()
    self.sm["modelV2"].big = False
    self.state = "failed"
    for _ in range(round(5 / DT_CTRL)):
      events, events_sp = self.tick()
      self.assertIn(EventNameSP.jetlinkLost, events_sp.events)
      self.assertEqual(events.events, [])
      self.assertFalse(events_sp.contains(ET.SOFT_DISABLE))
      self.assertFalse(events_sp.contains(ET.IMMEDIATE_DISABLE))
    self.assertNotIn(EventNameSP.jetlinkLost, self.tick()[1].events)
    alert = EVENTS_SP[EventNameSP.jetlinkLost][ET.PERMANENT]
    self.assertEqual(alert.alert_text_1, "TAKE CONTROL")
    self.assertIn("small model", alert.alert_text_2)

  def test_disengaging_cancels_loss_warning(self):
    self.tick()
    self.sm["modelV2"].big = False
    self.assertNotIn(EventNameSP.jetlinkLost, self.tick(engaged=False)[1].events)

  def test_native_chestnut_does_not_raise_jetlink_warning(self):
    self.state = "none"
    self.tick()
    self.sm["modelV2"].big = False
    self.assertEqual(self.tick()[1].events, [])

  def test_swap_still_blocks_entry_then_chimes(self):
    for _ in range(round(1 / DT_CTRL)):
      events, events_sp = self.tick(engaged=False)
      self.assertIn(EventName.bigModelLoading, events.events)
      self.assertNotIn(EventNameSP.bigModelReady, events_sp.events)
    events, events_sp = self.tick(engaged=False)
    self.assertNotIn(EventName.bigModelLoading, events.events)
    self.assertIn(EventNameSP.bigModelReady, events_sp.events)

  def test_disabled_adapter_is_inert(self):
    with mock.patch("openpilot.sunnypilot.jetlink_adapter.swap_events", return_value=None):
      self.accelerator = AcceleratorEvents()
    events, events_sp = self.tick()
    self.assertEqual((events.events, events_sp.events), ([], []))
