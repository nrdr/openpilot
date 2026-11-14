"""Exercise the real slider's press/drag/release without a physical display."""
import ast
from types import SimpleNamespace as NS

import pytest

from openpilot.nrdr.tests.test_honda_pcm_ui import ROOT, state
from openpilot.nrdr.ui.honda_pcm import mvl_pcm_deadzone_available, saved_pcm_speed_deadzone, save_pcm_speed_deadzone


def slider(compact=False):
  class Action:
    def __init__(self, **kwargs):
      self.enabled = True
      self.touch_valid = True

    def set_rect(self, rect):
      self._rect = rect

    def _touch_valid(self):
      return self.touch_valid

    def _handle_mouse_event(self, event):
      pass

    def hide_event(self):
      pass

  ui = state()
  ui.mouse_events = []
  path = ROOT / "openpilot/nrdr/ui/settings/pcm_speed_deadzone.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  tree.body = [n for n in tree.body if isinstance(n, ast.ClassDef)]
  def noop(*a, **k):
    pass
  rl = NS(Rectangle=lambda x, y, width, height: NS(x=x, y=y, width=width, height=height),
          check_collision_point_rec=lambda p, r: r.x <= p.x <= r.x + r.width and r.y <= p.y <= r.y + r.height,
          Vector2=lambda *a: a, Color=lambda *a: a, WHITE=1, GRAY=2, DARKGRAY=3,
          draw_rectangle_rounded=noop, draw_line_ex=noop, draw_circle=noop)
  env = {"ItemAction": Action, "rl": rl, "ui_state": ui, "mvl_pcm_deadzone_available": mvl_pcm_deadzone_available,
         "saved_pcm_speed_deadzone": saved_pcm_speed_deadzone, "save_pcm_speed_deadzone": save_pcm_speed_deadzone,
         "tr": lambda x: x, "PCM_SPEED_DEADZONE_TITLE": "PCM Speed-Error Deadzone", "gui_label": noop,
         "TextAlignment": NS(CENTER=0), "gui_app": ui}
  exec(compile(tree, str(path), "exec"), env)
  return env["PcmSpeedDeadzoneSlider"](compact), ui


def event(control, fraction, *, pressed=False, released=False):
  track = control._track()
  return NS(pos=NS(x=track.x + track.width * fraction, y=track.y + track.height / 2),
            left_pressed=pressed, left_released=released)


@pytest.mark.parametrize("compact", [False, True])
@pytest.mark.parametrize("fraction,expected", [(0, 0.), (.25, .05), (.75, .15), (1, .2)])
def test_slider_previews_then_saves_once_on_release(compact, fraction, expected):
  control, ui = slider(compact)
  assert control.value == .15
  control._handle_mouse_event(event(control, fraction, pressed=True))
  control._render(control._rect)
  assert control.value == expected and not ui.params.writes
  control._handle_mouse_event(event(control, fraction, released=True))
  assert ui.params.writes == [("NrdrPcmSpeedDeadzone", expected), ("OnroadCycleRequested", True)]


@pytest.mark.parametrize("reason", ["onroad", "hardware", "scroll", "hidden"])
def test_drag_cannot_save_after_state_or_scroll_change(reason):
  control, ui = slider(True)
  control._handle_mouse_event(event(control, 1, pressed=True))
  if reason == "onroad":
    ui.params.values["IsOffroad"] = False
  elif reason == "hardware":
    ui.CP_SP.enableGasInterceptor = True
  elif reason == "scroll":
    control.touch_valid = False
  else:
    control.hide_event()
  control._render(control._rect)
  control._handle_mouse_event(event(control, 1, released=True))
  assert not ui.params.writes


def test_compact_slider_captures_drag_before_carousel_scrolls():
  control, ui = slider(True)
  ui.mouse_events = [event(control, .5, pressed=True)]
  assert control.captures_horizontal_scroll()
  control._handle_mouse_event(ui.mouse_events[0])
  ui.mouse_events = [event(control, 1)]
  assert control.captures_horizontal_scroll()
  control._handle_mouse_event(ui.mouse_events[0])
  control._handle_mouse_event(event(control, 1, released=True))
  assert not control.captures_horizontal_scroll()
  assert ui.params.values["NrdrPcmSpeedDeadzone"] == .2
  ui.mouse_events = [event(control, .5, pressed=True)]
  ui.mouse_events[0].pos.y = control._rect.y + 20
  assert not control.captures_horizontal_scroll()  # Swipe the card title to navigate.
