import threading
import time

from openpilot.common.test import OpenpilotTestCase
from openpilot.cereal import log, messaging
from openpilot.cereal.messaging import SubMaster, PubMaster
from openpilot.selfdrive.ui.soundd import SELFDRIVE_STATE_TIMEOUT, check_selfdrive_timeout_alert
from openpilot.sunnypilot.selfdrive.ui.quiet_mode import ALERTS_ALWAYS_PLAY, QuietMode

AudibleAlert = log.SelfdriveState.AudibleAlert


class TestSoundd(OpenpilotTestCase):
  def test_quiet_mode_preserves_critical_alerts(self):
    quiet_mode = QuietMode.__new__(QuietMode)
    quiet_mode.enabled = True

    critical_alerts = {
      AudibleAlert.warningSoft,
      AudibleAlert.warningImmediate,
      AudibleAlert.promptDistracted,
      AudibleAlert.promptRepeat,
    }
    assert ALERTS_ALWAYS_PLAY == critical_alerts
    assert all(quiet_mode.should_play_sound(alert) for alert in critical_alerts)

    noncritical_alerts = {
      AudibleAlert.engage,
      AudibleAlert.disengage,
      AudibleAlert.refuse,
      AudibleAlert.prompt,
      AudibleAlert.preAlert,
      AudibleAlert.complete,
    }
    assert not any(quiet_mode.should_play_sound(alert) for alert in noncritical_alerts)
    assert not quiet_mode.should_play_sound(AudibleAlert.none)

    quiet_mode.enabled = False
    assert all(quiet_mode.should_play_sound(alert) for alert in critical_alerts | noncritical_alerts)
    assert not quiet_mode.should_play_sound(AudibleAlert.none)

  def test_check_selfdrive_timeout_alert(self, mocker):
    sm = SubMaster(['selfdriveState', 'selfdriveStateSP'])
    pm = PubMaster(['selfdriveState', 'selfdriveStateSP'])

    cs = messaging.new_message('selfdriveState')
    cs.selfdriveState.enabled = True
    threading.Timer(0.01, pm.send, args=("selfdriveState", cs)).start()
    sm.update(100)
    assert sm.updated['selfdriveState']

    sm.recv_time['selfdriveState'] = 0
    clock = mocker.patch("openpilot.selfdrive.ui.soundd.time.monotonic", return_value=SELFDRIVE_STATE_TIMEOUT)
    assert not check_selfdrive_timeout_alert(sm)

    clock.return_value = SELFDRIVE_STATE_TIMEOUT + 0.1
    assert check_selfdrive_timeout_alert(sm)

    clock.return_value = SELFDRIVE_STATE_TIMEOUT + 10
    assert not check_selfdrive_timeout_alert(sm)

  def test_check_selfdrive_timeout_alert_mads_lateral_only(self):
    sm = SubMaster(['selfdriveState', 'selfdriveStateSP'])
    pm = PubMaster(['selfdriveState', 'selfdriveStateSP'])

    for _ in range(100):
      cs = messaging.new_message('selfdriveState')
      cs.selfdriveState.enabled = False

      ss_sp = messaging.new_message('selfdriveStateSP')
      ss_sp.selfdriveStateSP.mads.enabled = True

      pm.send("selfdriveState", cs)
      pm.send("selfdriveStateSP", ss_sp)

      time.sleep(0.01)

      sm.update(0)

      assert not check_selfdrive_timeout_alert(sm)

    for _ in range(SELFDRIVE_STATE_TIMEOUT * 110):
      sm.update(0)
      time.sleep(0.01)

    assert check_selfdrive_timeout_alert(sm)

  # TODO: add test with micd for checking that soundd actually outputs sounds
