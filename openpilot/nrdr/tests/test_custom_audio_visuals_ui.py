"""UI contracts and callbacks without loading graphics, IPC, or sound runtime."""

import ast
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
import unittest

from openpilot.nrdr.params.tuning_policy import tuning_write_allowed


ROOT = Path(__file__).resolve().parents[3]
TICI = ROOT / "openpilot/nrdr/ui/settings/custom_audio_visuals.py"
MICI = ROOT / "openpilot/selfdrive/ui/mici/layouts/settings/custom_audio_visuals.py"
DEVICE = MICI.with_name("device.py")
KEY = "NrdrEngagementSoundPack"
DESCRIPTION = (
  "Choose engage, disengage and engagement-refused sounds with their matching automatic volume. Other alerts are unchanged. " +
  "Applies to the next chime without reboot. Quiet Mode still mutes these sounds."
)


class _Params:
  def __init__(self):
    self.values = {}
    self.writes = []

  def get(self, key, return_default=False):
    return self.values.get(key, 0 if return_default and key == KEY else None)

  def put(self, key, value, **kwargs):
    self.values[key] = value
    self.writes.append((key, value, kwargs))


class _Widget:
  def __init__(self):
    self.shows = self.hides = 0

  def show_event(self):
    self.shows += 1

  def hide_event(self):
    self.hides += 1


class _Scroller(_Widget):
  def __init__(self, items=(), **kwargs):
    super().__init__()
    self._items = list(items)

  def add_widgets(self, items):
    self._items.extend(items)


class _NavScroller(_Widget):
  def __init__(self):
    super().__init__()
    self._scroller = _Scroller()


class _Choice:
  def __init__(self, text="", options=(), **kwargs):
    self.text = text
    self.options = list(options)
    self.config = kwargs
    self.value = self.selected = None

  def set_value(self, value):
    self.value = value

  def set_selected_button(self, index):
    self.selected = index

  def set_click_callback(self, callback):
    self.callback = callback


def _load_class(path, class_name, params, methods=None):
  tree = ast.parse(path.read_text(encoding="utf-8"))
  cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
  if methods is not None:
    cls.body = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in methods]
  tree.body = [cls]
  env = {
    "Widget": _Widget, "NavScroller": _NavScroller, "Scroller": _Scroller, "NavButton": _Choice,
    "Callable": Callable, "Params": lambda: params, "tr": lambda text: text,
    "ui_state": SimpleNamespace(params=params), "BigMultiToggle": _Choice,
    "multiple_button_item_sp": lambda **kwargs: SimpleNamespace(config=kwargs, action_item=_Choice()),
  }
  exec(compile(tree, str(path), "exec"), env)
  return env[class_name]


class TestCustomAudioVisualsUi(unittest.TestCase):
  def setUp(self):
    self.params = _Params()

  def test_c3x_segmented_choice_binding_copy_and_refresh(self):
    back_calls = []
    layout = _load_class(TICI, "CustomAudioVisualsLayout", self.params)(lambda: back_calls.append(True))
    control = layout._engagement_sounds
    self.assertEqual(control.config["param"], KEY)
    self.assertEqual(control.config["title"](), "Engagement Sounds")
    self.assertEqual(control.config["description"](), DESCRIPTION)
    self.assertEqual([label() for label in control.config["buttons"]], ["Current", "June 2026"])
    self.assertEqual(layout._scroller._items, [control])
    for value, expected in ((None, 0), (1, 1), (0, 0), (8, 0)):
      self.params.values[KEY] = value
      layout.show_event()
      self.assertEqual(control.action_item.selected, expected)
      layout.hide_event()
    self.assertEqual((layout._scroller.shows, layout._scroller.hides), (4, 4))
    layout._back_button.callback()
    self.assertEqual(back_calls, [True])
    self.assertEqual(self.params.writes, [])

  def test_c4_small_screen_choice_writes_only_sound_pack_and_refreshes(self):
    layout = _load_class(MICI, "CustomAudioVisualsLayoutMici", self.params)()
    control = layout._engagement_sounds
    self.assertEqual(control.text.replace("\n", " "), "Engagement Sounds")
    self.assertEqual(control.options, ["Current", "June 2026"])
    self.assertEqual(control.config["font_size"], 40)
    self.assertEqual(control.config["description"], DESCRIPTION)
    self.assertEqual(layout._scroller._items, [control])
    layout.show_event()
    self.assertEqual(control.value, "Current")
    for label, value in (("June 2026", 1), ("Current", 0)):
      control.config["select_callback"](label)
      self.assertEqual(self.params.writes[-1], (KEY, value, {"block": True}))
    self.params.values[KEY] = 1  # Sunnylink changed it while the panel was closed.
    layout.show_event()
    self.assertEqual(control.value, "June 2026")
    self.params.values[KEY] = 99
    layout.show_event()
    self.assertEqual(control.value, "Current")
    self.assertEqual(len(self.params.writes), 2)

  def test_c4_device_entry_stays_last_after_derived_layout_additions(self):
    cls = _load_class(DEVICE, "DeviceLayoutMici", self.params, methods={"show_event"})
    layout = cls()
    before, extra = object(), object()
    layout._custom_audio_visuals_btn = object()
    layout._scroller._items = [before, layout._custom_audio_visuals_btn, extra]
    for _ in range(2):
      layout.show_event()
      self.assertEqual(layout._scroller._items, [before, extra, layout._custom_audio_visuals_btn])
    self.assertEqual(layout.shows, 2)

  def test_shared_widget_policy_does_not_lock_sound_choice(self):
    self.params.values.update({
      "NrdrSuggestedSettings": True, "NrdrHandcraftedLateralTune": True,
      "HondaLiveLearningGas": True, "NrdrLateralController": 1, "QuietMode": True,
    })
    for offroad in (False, True):
      for brand in ("", "honda", "toyota"):
        with self.subTest(offroad=offroad, brand=brand):
          self.assertTrue(tuning_write_allowed(self.params, KEY, CP=SimpleNamespace(brand=brand), is_offroad=offroad))
    self.assertEqual(self.params.writes, [])


if __name__ == "__main__":
  unittest.main()
