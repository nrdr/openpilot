"""CMBS feedback uses camera status, not button guesses or masked dashboard output."""
import ast
from pathlib import Path
import sys
from types import SimpleNamespace as NS

import pytest

from opendbc.can.packer import CANPacker
from opendbc.can.parser import CANParser
from opendbc.car import Bus
from openpilot.cereal import custom
from openpilot.nrdr.features.driver_policy.stock_cmbs import (
  CONFIRM_TIME_NS, STATUS_MAX_AGE_NS, StockCmbsAlerts, publish_stock_cmbs_status,
)


ROOT = Path(__file__).resolve().parents[3]
DBC = 'honda_civic_touring_2016_can_generated'


def source():
  cp = CANParser(DBC, [('ACC_HUD', 10)], 2)
  ci = NS(CP=NS(brand='honda', carFingerprint='HONDA_CIVIC'), can_parsers={Bus.cam: cp})
  return ci, cp, CANPacker(DBC)


def publish(ci, now):
  sp = custom.CarStateSP.new_message()
  publish_stock_cmbs_status(ci, sp, now)
  return sp


@pytest.mark.parametrize('off', [0, 1])
@pytest.mark.parametrize('fault_bit', [None, 'FCM_OFF', 'FCM_PROBLEM'])
def test_camera_setting_is_independent_of_fault_bits_and_masked_output(off, fault_bit):
  ci, cp, packer = source()
  values = {'FCM_OFF_2': off}
  if fault_bit:
    values[fault_bit] = 1
  now = 1_000_000_000
  cp.update([(now, [packer.make_can_msg('ACC_HUD', 2, values),
                    packer.make_can_msg('ACC_HUD', 0, {}),
                    packer.make_can_msg('ACC_HUD', 128, {})])])
  before = dict(cp.vl['ACC_HUD'])
  sp = publish(ci, now)
  assert str(sp.stockCmbsStatus) == ('disabled' if off else 'enabled')
  assert sp.stockCmbsOffOrProblem == bool(fault_bit)
  assert sp.stockCmbsStatusMonoTime == now
  assert dict(cp.vl['ACC_HUD']) == before  # no mutation of outgoing HUD source


def test_unseen_stale_future_and_bad_checksum_do_not_make_up_enabled_status():
  ci, cp, packer = source()
  now = 1_000_000_000
  assert str(publish(ci, now).stockCmbsStatus) == 'unknown'
  message = packer.make_can_msg('ACC_HUD', 2, {'FCM_OFF_2': 1})
  cp.update([(now, [message])])
  assert str(publish(ci, now + STATUS_MAX_AGE_NS).stockCmbsStatus) == 'disabled'
  assert str(publish(ci, now + STATUS_MAX_AGE_NS + 1).stockCmbsStatus) == 'unknown'
  assert str(publish(ci, now - 1).stockCmbsStatus) == 'unknown'
  bad = packer.make_can_msg('ACC_HUD', 2, {'FCM_OFF_2': 0})
  bad = (bad[0], bad[1][:-1] + bytes([bad[1][-1] ^ 1]), bad[2])
  cp.update([(now + STATUS_MAX_AGE_NS + 1, [bad])])
  assert str(publish(ci, now + STATUS_MAX_AGE_NS + 1).stockCmbsStatus) == 'unknown'


@pytest.mark.parametrize('brand,platform', [('toyota', 'HONDA_CIVIC'), ('honda', 'HONDA_CLARITY'),
                                         ('honda', 'HONDA_CIVIC_BOSCH'), ('honda', 'UNKNOWN')])
def test_unverified_platforms_have_no_status(brand, platform):
  ci, _, _ = source()
  ci.CP.brand, ci.CP.carFingerprint = brand, platform
  assert str(publish(ci, 1_000_000_000).stockCmbsStatus) == 'unknown'


def test_missing_camera_is_unknown():
  ci, _, _ = source()
  ci.can_parsers.clear()
  assert str(publish(ci, 1_000_000_000).stockCmbsStatus) == 'unknown'


@pytest.mark.parametrize('initial,other', [('enabled', 'disabled'), ('disabled', 'enabled')])
def test_startup_is_silent_and_each_stable_transition_fires_once(initial, other):
  tracker = StockCmbsAlerts()
  now = 1_000_000_000
  for status, expected in [(initial, False), (other, True), (initial, True)]:
    assert not tracker.update(status, now, True)
    assert not tracker.update(status, now + CONFIRM_TIME_NS - 1, True)
    assert tracker.update(status, now + CONFIRM_TIME_NS, True) == expected
    assert not tracker.update(status, now + CONFIRM_TIME_NS + 1, True)
    now += 400_000_000


@pytest.mark.parametrize('reason', ['invalid', 'unknown', 'zero_stamp', 'backwards', 'gap'])
def test_reconnect_is_a_new_baseline_not_a_fake_toggle(reason):
  tracker = StockCmbsAlerts()
  tracker.update('enabled', 1_000_000_000, True)
  tracker.update('enabled', 1_200_000_000, True)
  status, stamp, valid = {
    'invalid': ('disabled', 1_300_000_000, False), 'unknown': ('unknown', 1_300_000_000, True),
    'zero_stamp': ('disabled', 0, True), 'backwards': ('disabled', 900_000_000, True),
    'gap': ('disabled', 2_000_000_000, True),
  }[reason]
  assert not tracker.update(status, stamp, valid)
  assert not tracker.update('disabled', 2_100_000_000, True)
  assert not tracker.update('disabled', 2_300_000_000, True)


def test_repeated_stale_message_and_one_packet_glitch_do_not_confirm():
  tracker = StockCmbsAlerts()
  tracker.update('enabled', 1_000_000_000, True)
  tracker.update('enabled', 1_200_000_000, True)
  for _ in range(100):
    assert not tracker.update('disabled', 1_300_000_000, True)
  assert not tracker.update('enabled', 1_400_000_000, True)
  assert not tracker.update('enabled', 1_600_000_000, True)
  assert tracker.confirmed == 'enabled'


def test_host_wiring_runs_after_car_update_and_outside_engagement_gate():
  source = (ROOT / 'openpilot/selfdrive/car/card.py').read_text()
  assert source.index('self.CI.update(can_list)') < source.index('publish_stock_cmbs_status(self.CI, CS_SP, can_list[-1][0])')
  source = (ROOT / 'openpilot/selfdrive/selfdrived/selfdrived.py').read_text()
  tree = ast.parse(source)
  cls = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == 'SelfdriveD')
  update = next(x for x in cls.body if isinstance(x, ast.FunctionDef) and x.name == 'update_events')
  assert any(isinstance(x, ast.Expr) and ast.unparse(x) == 'self.nrdr.update_stock_cmbs(CS, self.sm, self.events_sp)'
             for x in update.body)


@pytest.mark.skipif(sys.platform == 'win32', reason='Requires native openpilot messaging/Params; also run on parked C4')
@pytest.mark.parametrize('status', ['enabled', 'disabled'])
@pytest.mark.parametrize('fault', [False, True])
def test_native_notification_is_informational_and_yields_to_collision_alert(status, fault):
  from openpilot.nrdr.hooks.selfdrived import NrdrSelfdrive
  from openpilot.selfdrive.selfdrived.alertmanager import AlertManager
  from openpilot.selfdrive.selfdrived.events import EVENTS, EventName
  from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP, ET, EventNameSP
  from openpilot.sunnypilot.selfdrive.selfdrived.events_base import Priority, AlertStatus, AudibleAlert, VisualAlert

  class State(dict):
    valid = True

    def all_checks(self, services):
      assert services == ['carStateSP']
      return self.valid

  nrdr = NrdrSelfdrive()
  sm = State(carStateSP=custom.CarStateSP.new_message(stockCmbsStatus='disabled' if status == 'enabled' else 'enabled'))
  cs = NS(canValid=True)
  events = EventsSP()
  for stamp in (1_000_000_000, 1_200_000_000):
    sm['carStateSP'].stockCmbsStatusMonoTime = stamp
    nrdr.update_stock_cmbs(cs, sm, events)
  assert not events.names
  sm['carStateSP'].stockCmbsStatus = status
  sm['carStateSP'].stockCmbsOffOrProblem = fault
  for stamp in (1_300_000_000, 1_500_000_000):
    sm['carStateSP'].stockCmbsStatusMonoTime = stamp
    nrdr.update_stock_cmbs(cs, sm, events)
  assert events.names == [EventNameSP.stockCmbsStatusChanged]
  assert set(events.get_events_mapping()[events.names[0]]) == {ET.PERMANENT}
  alert, = events.create_alerts([ET.PERMANENT], [None, cs, sm, False, 0, None])
  assert alert.alert_text_1 == f'Stock CMBS: {status.capitalize()}'
  assert alert.alert_text_2 == ('Setting only; factory reports off/fault' if fault else 'Setting only; availability unverified')
  assert alert.duration == 300 and alert.priority == Priority.LOWER
  assert alert.alert_status == AlertStatus.normal
  assert alert.audible_alert == AudibleAlert.none and alert.visual_alert == VisualAlert.none
  manager = AlertManager()
  manager.add_many(1, [alert])
  manager.process_alerts(1, set())
  assert manager.current_alert is alert
  collision = EVENTS[EventName.fcw][ET.PERMANENT]
  collision.alert_type = 'fcw/permanent'
  manager.add_many(2, [collision])
  manager.process_alerts(2, set())
  assert manager.current_alert is collision
  # Changing live telemetry cannot rewrite an already queued confirmation.
  sm['carStateSP'].stockCmbsStatus = 'unknown'
  assert alert.alert_text_1 == f'Stock CMBS: {status.capitalize()}'
