from types import SimpleNamespace
from unittest.mock import Mock, call

from openpilot.selfdrive.ui.mici.layouts import main as main_module
from openpilot.selfdrive.ui.mici.layouts.main import MiciMainLayout
from openpilot.system.ui.lib.scroll_panel2 import ScrollState
from openpilot.system.ui.widgets.scroller import _Scroller


class FakeScrollPanel:
  def __init__(self, offset: float):
    self.offset = offset
    self.state = ScrollState.STEADY

  def get_offset(self) -> float:
    return self.offset

  def set_offset(self, offset: float) -> None:
    self.offset = offset


def _layout(scroller=None) -> MiciMainLayout:
  layout = MiciMainLayout.__new__(MiciMainLayout)
  layout._prev_onroad = False
  layout._prev_standstill = False
  layout._onroad_time_delay = None
  layout._onboarding_window = object()
  layout._home_layout = SimpleNamespace(rect=SimpleNamespace(x=536.0))
  layout._car_onroad_layout = SimpleNamespace(rect=SimpleNamespace(x=1072.0))
  layout._body_onroad_layout = SimpleNamespace(rect=SimpleNamespace(x=1072.0))
  layout._scroller = scroller or SimpleNamespace(scroll_to=Mock())
  return layout


def _runtime(monkeypatch, *, started: bool, standstill: bool, now: list[float]):
  state = SimpleNamespace(
    started=started,
    is_body=False,
    sm={"carState": SimpleNamespace(standstill=standstill)},
  )
  app = SimpleNamespace(
    widget_in_stack=Mock(return_value=False),
    pop_widgets_to=Mock(),
  )
  monkeypatch.setattr(main_module, "ui_state", state)
  monkeypatch.setattr(main_module, "gui_app", app)
  monkeypatch.setattr(main_module, "rl", SimpleNamespace(get_time=lambda: now[0]))
  return state, app


def test_ignition_off_jumps_home_in_same_frame_without_popping_settings(monkeypatch):
  now = [10.0]
  state, app = _runtime(monkeypatch, started=False, standstill=False, now=now)
  layout = _layout()
  layout._prev_onroad = True
  layout._onroad_time_delay = 9.0

  layout._handle_transitions()

  assert not layout._prev_onroad
  assert layout._onroad_time_delay is None
  assert layout._scroller.scroll_to.call_args_list == [call(536, smooth=False)]
  app.pop_widgets_to.assert_not_called()
  assert not state.started


def test_instant_scroll_cancels_active_animation_even_when_already_at_destination():
  scroller = _Scroller.__new__(_Scroller)
  scroller.scroll_panel = FakeScrollPanel(-536.0)
  scroller._scrolling_to = (-1072.0, True, True)
  scroller._pending_lift = set()

  scroller.scroll_to(0.0, smooth=False)
  offset_after_jump = scroller.scroll_panel.get_offset()
  scroller._update_state()

  assert not scroller.is_auto_scrolling
  assert scroller.scroll_panel.get_offset() == offset_after_jump == -536.0


def test_rapid_onroad_then_offroad_cancels_delayed_onroad_transition(monkeypatch):
  now = [20.0]
  state, app = _runtime(monkeypatch, started=True, standstill=True, now=now)
  layout = _layout()

  layout._handle_transitions()
  assert layout._onroad_time_delay == 20.0

  now[0] = 20.5
  state.started = False
  layout._handle_transitions()
  assert layout._onroad_time_delay is None

  # Advance beyond ONROAD_DELAY and let stale carState leave standstill. Neither
  # condition may reopen the onroad page after ignition has gone off.
  now[0] = 25.0
  state.sm["carState"].standstill = False
  layout._handle_transitions()

  assert layout._scroller.scroll_to.call_args_list == [call(536, smooth=False)]
  app.pop_widgets_to.assert_not_called()
