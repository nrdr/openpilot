"""Saved-choice UI guards without starting hardware, Params, or rendering."""
import ast
from collections.abc import Callable
import math
from pathlib import Path
import struct
from types import SimpleNamespace as NS

import pytest

from opendbc.car import structs
from opendbc.car.honda.values import CAR, HONDA_BOSCH
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.nrdr.ui.honda_pcm import pcm_tuning_available, saved_pcm_mode, saved_wind_brake, save_pcm_choice


ROOT = Path(__file__).resolve().parents[3]


class Params:
  def __init__(self, **values):
    self.values = values
    self.writes = []

  def get(self, key):
    return self.values.get(key)

  def get_bool(self, key):
    return bool(self.get(key))

  def put(self, key, value, **_):
    self.values[key] = value
    self.writes.append((key, value))

  put_bool = put


def state(**overrides):
  CP = structs.CarParams(brand="honda", carFingerprint="HONDA_CIVIC", openpilotLongitudinalControl=True)
  CP_SP = structs.CarParamsSP(enableGasInterceptor=overrides.pop("enableGasInterceptor", False))
  for key, value in overrides.items():
    setattr(CP, key, value)
  return NS(CP=CP, CP_SP=CP_SP, params=Params(), is_offroad=lambda: True)


@pytest.mark.parametrize("car", list(CAR))
def test_exact_nidec_catalog_and_openlong_eligibility(car):
  ui = state(carFingerprint=str(car))
  assert pcm_tuning_available(ui.CP, ui.CP_SP, ui.params) == (car not in HONDA_BOSCH)


@pytest.mark.parametrize("overrides", [
  {"brand": "toyota"}, {"carFingerprint": "UNKNOWN_HONDA"},
  {"openpilotLongitudinalControl": False}, {"enableGasInterceptor": True},
])
def test_ineligible_control_cannot_save(overrides):
  ui = state(**overrides)
  assert not pcm_tuning_available(ui.CP, ui.CP_SP, ui.params)
  assert not save_pcm_choice(ui, "NrdrHondaPcmMode", 1)
  assert not save_pcm_choice(ui, "NrdrHondaWindBrake", False)
  assert not ui.params.writes


@pytest.mark.parametrize("bundle", [False, True, "honda", {}, {"brand": "honda"},
                                    {"brand": "honda", "platform": "HONDA_CLARITY"},
                                    {"brand": "toyota", "platform": "HONDA_CIVIC"}])
def test_stale_or_invalid_manual_identity_fails_closed(bundle):
  ui = state()
  ui.params.values["CarPlatformBundle"] = bundle
  assert not pcm_tuning_available(ui.CP, ui.CP_SP, ui.params)
  assert not save_pcm_choice(ui, "NrdrHondaPcmMode", 2)
  assert not ui.params.writes


def test_matching_identity_and_missing_vehicle():
  ui = state()
  ui.params.values["CarPlatformBundle"] = {"brand": "honda", "platform": "HONDA_CIVIC"}
  assert pcm_tuning_available(ui.CP, ui.CP_SP, ui.params)
  assert not pcm_tuning_available(None, ui.CP_SP, ui.params)
  assert not pcm_tuning_available(ui.CP, None, ui.params)
  ui.CP_SP.flags |= HondaFlagsSP.STOCK_LONGITUDINAL
  assert not pcm_tuning_available(ui.CP, ui.CP_SP, ui.params)


@pytest.mark.parametrize("value", [None, True, False, -1, 3, 1.0, "1", b"1", {}])
def test_saved_mode_never_coerces_old_bool_or_invalid_values(value):
  params = Params(NrdrHondaEcuMatchedLong=True, NrdrHondaPcmMode=value)
  assert saved_pcm_mode(params) == 0
  assert saved_wind_brake(params) is True
  assert not params.writes


@pytest.mark.parametrize("key,value", [("NrdrHondaPcmMode", 0), ("NrdrHondaPcmMode", 1), ("NrdrHondaPcmMode", 2),
                                      ("NrdrHondaWindBrake", False), ("NrdrHondaWindBrake", True)])
def test_save_is_parked_only_and_requests_restart_without_claiming_active_state(key, value):
  ui = state()
  assert save_pcm_choice(ui, key, value)
  assert ui.params.writes == [(key, value), ("OnroadCycleRequested", True)]
  assert (saved_pcm_mode(ui.params) if key == "NrdrHondaPcmMode" else saved_wind_brake(ui.params)) == value
  ui.params.writes.clear()
  ui.is_offroad = lambda: False
  assert not save_pcm_choice(ui, key, value)
  assert not ui.params.writes


@pytest.mark.parametrize("key,value", [("NrdrHondaEcuMatchedLong", True), ("NrdrHondaPcmMode", True),
                                      ("NrdrHondaPcmMode", 3), ("NrdrHondaWindBrake", 1)])
def test_invalid_writes_are_rejected(key, value):
  ui = state()
  assert not save_pcm_choice(ui, key, value)
  assert not ui.params.writes


class Widget:
  LABEL_HORIZONTAL_PADDING = 40
  LABEL_VERTICAL_PADDING = 23

  def __init__(self, text, options=None, **kwargs):
    self.text, self.options, self.kwargs = text, options, kwargs
    self.value = None
    self._rect = NS(width=402, height=180)
    self._txt_enabled_toggle = NS(width=84, height=66)

  def set_enabled(self, value):
    self.enabled = value

  def set_value(self, value):
    self.value = value

  def set_checked(self, value):
    self.value = value

  def set_click_callback(self, callback):
    self.click_callback = callback

  def _update_state(self):
    pass


def test_mici_saved_selection_refresh_and_click_time_recheck():
  path = ROOT / "openpilot/nrdr/ui/settings/pcm_modes_mici.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  tree.body = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name in ("PcmModeControl", "WindBrakeControl")]
  ui = state()
  env = {"BigMultiToggle": Widget, "BigToggle": Widget, "ui_state": ui, "tr": lambda s: s,
         "pcm_tuning_available": pcm_tuning_available, "saved_pcm_mode": saved_pcm_mode,
         "saved_wind_brake": saved_wind_brake, "save_pcm_choice": save_pcm_choice}
  exec(compile(tree, str(path), "exec"), env)
  mode, wind = env["PcmModeControl"](), env["WindBrakeControl"]()
  assert mode.text == "PCM Command Shaping"
  assert mode.kwargs["description"].startswith("Honda Nidec: ECU-Matched PCM Command Shaping. ")
  assert mode.options == ["Off", "ECU-Matched", "Experimental"]
  assert mode.value == "Off" and wind.kwargs["initial_state"] is True
  mode._select("Experimental")
  wind._select(False)
  assert mode.value == "Experimental" and wind.value is False
  ui.params.values.update(NrdrHondaPcmMode=1, NrdrHondaWindBrake=True)
  mode._update_state()
  wind._update_state()
  assert mode.value == "ECU-Matched" and wind.value is True
  ui.is_offroad = lambda: False
  ui.params.writes.clear()
  assert not mode.enabled() and not wind.enabled()
  mode._select("Experimental")
  wind._select(False)
  assert not ui.params.writes
  assert mode.value == "ECU-Matched" and wind.value is True


def _font_advance_upper_bound(filename, text, font_size):
  """Bundled TTF advances at raylib's 200px load size, rounded upward.

  No display/font-library dependency. Only format-4 Unicode cmap is needed
  for these English labels. The 1.16 scale is the mici text renderer's scale.
  """
  data = (ROOT / "openpilot/selfdrive/assets/fonts" / filename).read_bytes()
  def u16(offset):
    return struct.unpack_from(">H", data, offset)[0]
  tables = {data[p:p + 4].decode(): struct.unpack_from(">I", data, p + 8)[0]
            for p in range(12, 12 + 16 * u16(4), 16)}
  ascender, descender = struct.unpack_from(">hh", data, tables["hhea"] + 4)
  load_scale = 200 / (ascender - descender)
  cmap = tables["cmap"]
  cmap = next(cmap + struct.unpack_from(">I", data, p + 4)[0]
              for p in range(cmap + 4, cmap + 4 + 8 * u16(cmap + 2), 8)
              if u16(p) in (0, 3) and u16(cmap + struct.unpack_from(">I", data, p + 4)[0]) == 4)
  segments = u16(cmap + 6) // 2
  ends = cmap + 14
  starts = ends + 2 * segments + 2
  deltas = starts + 2 * segments
  ranges = deltas + 2 * segments
  advances = []
  for char in text:
    code = ord(char)
    index = next(i for i in range(segments) if u16(starts + 2 * i) <= code <= u16(ends + 2 * i))
    offset = u16(ranges + 2 * index)
    glyph = code if offset == 0 else u16(ranges + 2 * index + offset + 2 * (code - u16(starts + 2 * index)))
    glyph = (glyph + u16(deltas + 2 * index)) & 0xffff
    assert glyph != 0
    metric = min(glyph, u16(tables["hhea"] + 34) - 1)
    advances.append(math.ceil(u16(tables["hmtx"] + 4 * metric) * load_scale))
  return sum(advances) * font_size * 1.16 / 200


def test_mici_pcm_title_and_each_value_fit_left_of_three_pills():
  path = ROOT / "openpilot/nrdr/ui/settings/pcm_modes_mici.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  tree.body = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "PcmModeControl"]
  env = {"BigMultiToggle": Widget, "ui_state": state(), "tr": lambda s: s, "saved_pcm_mode": saved_pcm_mode}
  exec(compile(tree, str(path), "exec"), env)
  mode = env["PcmModeControl"]()
  title_width, value_width = mode._title_width_hint(), mode._subtitle_width_hint()
  assert title_width == value_width == 266
  pill_left = mode._rect.width - mode._txt_enabled_toggle.width
  assert mode.LABEL_HORIZONTAL_PADDING + title_width + mode.PILL_TEXT_GAP == pill_left
  assert mode.kwargs["font_size"] == 34

  lines = []
  for word in mode.text.split():
    joined = f"{lines[-1]} {word}" if lines else word
    if lines and _font_advance_upper_bound("Inter-Bold.ttf", joined, 34) <= title_width:
      lines[-1] = joined
    else:
      lines.append(word)
  assert lines == ["PCM Command", "Shaping"]
  assert all(_font_advance_upper_bound("Inter-Bold.ttf", line, 34) < title_width for line in lines)
  assert all(_font_advance_upper_bound("Inter-Regular.ttf", label, 36) < value_width for label in mode.options)
  # Match BigButton/UnifiedLabel's top title and bottom-aligned subtitle.
  title_height = 34 * 1.16 * (1 + .9 * (len(lines) - 1))
  value_height = 36 * 1.16
  content_height = mode._rect.height - 2 * mode.LABEL_VERTICAL_PADDING
  assert content_height - title_height - value_height > 17
  assert mode._txt_enabled_toggle.height + 2 * 35 <= mode._rect.height


def native_layout(ui, toggle_factory=None):
  from openpilot.nrdr.features.longitudinal.policy import nrdr_longitudinal_enabled

  class Item:
    def __init__(self, **kwargs):
      self.kwargs = kwargs
      self.action_item = self

    def set_enabled(self, enabled):
      self.enabled = enabled

    def set_visible(self, visible):
      self.visible = visible

    def set_selected_button(self, value):
      self.value = value

    set_state = set_selected_button

  path = ROOT / "openpilot/nrdr/ui/settings/longitudinal_tuning.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  tree.body = [n for n in tree.body if isinstance(n, ast.ClassDef)]
  env = {"Widget": Widget, "Callable": Callable, "tr": lambda s: s, "ui_state": ui,
         "nrdr_longitudinal_enabled": nrdr_longitudinal_enabled, "pcm_tuning_available": pcm_tuning_available,
         "saved_pcm_mode": saved_pcm_mode, "saved_wind_brake": saved_wind_brake, "save_pcm_choice": save_pcm_choice,
         "gas_reset_available": lambda: False, "large_reset_button": Item, "LineSeparatorSP": lambda _: NS(),
         "toggle_item_sp": toggle_factory or Item, "option_item_sp": Item, "multiple_button_item_sp": Item}
  exec(compile(tree, str(path), "exec"), env)
  layout = object.__new__(env["LongitudinalTuningLayout"])
  layout._tuning_items = layout._initialize_items()
  return layout


def test_native_refreshes_saved_not_active_choices_and_rechecks_clicks():
  ui = state()
  layout = native_layout(ui)
  layout._update_state()
  assert layout._pcm_mode.enabled and layout._wind_brake.enabled
  assert layout._pcm_mode.value == 0 and layout._wind_brake.value is True
  ui.params.values.update(NrdrHondaPcmMode=2, NrdrHondaWindBrake=False)
  layout._update_state()
  assert layout._pcm_mode.value == 2 and layout._wind_brake.value is False
  ui.is_offroad = lambda: False
  # Invoke saved callbacks before the next display update: they must recheck.
  layout._pcm_mode.kwargs["callback"](1)
  layout._wind_brake.kwargs["callback"](True)
  assert not ui.params.writes
  layout._update_state()
  assert not layout._pcm_mode.enabled and not layout._wind_brake.enabled
  assert layout._pcm_mode.value == 2 and layout._wind_brake.value is False


def native_layout_with_real_toggle_handlers(ui):
  """Execute the production toggle handlers without graphics/native Params.

  A callback-only stub misses ToggleSP's automatic post-callback param write.
  Retain both real constructors and release handlers to catch that regression.
  """
  env = {"Widget": type("ToggleWidget", (), {}), "Callable": Callable, "MousePos": object,
         "Params": lambda: ui.params, "tuning_write_allowed": lambda *_: True}
  for relative, name in (("widgets/toggle.py", "Toggle"), ("sunnypilot/widgets/toggle.py", "ToggleSP")):
    path = ROOT / "openpilot/system/ui" / relative
    tree = ast.parse(path.read_text(encoding="utf-8"))
    tree.body = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == name]
    tree.body[0].body = [n for n in tree.body[0].body if isinstance(n, ast.FunctionDef) and n.name in (
      "__init__", "_handle_mouse_release", "set_state", "get_state",
    )]
    exec(compile(tree, str(path), "exec"), env)

  class Item:
    def __init__(self, **kwargs):
      self.kwargs = kwargs
      self.action_item = self
      self.enabled = kwargs.get("enabled", True)
      self.toggle = env["ToggleSP"](initial_state=kwargs.get("initial_state", False),
                                    callback=kwargs.get("callback"), param=kwargs.get("param"))

    def set_enabled(self, value):
      self.enabled = value
      self.toggle._enabled = value() if callable(value) else value

    def set_state(self, value):
      self.toggle.set_state(value)

  return native_layout(ui, Item)


@pytest.mark.parametrize("saved", [False, True])
def test_native_engine_saved_initial_state_refresh_and_guarded_save(saved):
  ui = state()
  ui.params.values["NrdrExperimentalEngineBraking"] = saved
  layout = native_layout_with_real_toggle_handlers(ui)
  engine = layout._engine_braking
  assert engine.kwargs.get("param") is None
  assert engine.kwargs["initial_state"] is saved
  assert engine.toggle.get_state() is saved
  assert engine.enabled()
  assert not ui.params.writes
  layout._update_state()
  assert engine.enabled is True
  ui.params.values["NrdrExperimentalEngineBraking"] = not saved
  layout._update_state()
  assert engine.toggle.get_state() is not saved
  assert not ui.params.writes
  engine.toggle._handle_mouse_release(None)
  assert engine.toggle.get_state() is saved
  assert ui.params.writes == [("NrdrExperimentalEngineBraking", saved), ("OnroadCycleRequested", True)]


@pytest.mark.parametrize("saved", [False, True])
@pytest.mark.parametrize("change", ["onroad", "interceptor", "stock", "missing_cp", "missing_cp_sp", "stale_identity",
                                   "openlong_off", "clarity", "pilot", "bosch", "non_honda"])
def test_native_engine_rejected_release_cannot_write_bound_param(change, saved):
  ui = state()
  ui.params.values["NrdrExperimentalEngineBraking"] = saved
  layout = native_layout_with_real_toggle_handlers(ui)
  layout._update_state()
  engine = layout._engine_braking
  assert engine.enabled
  if change == "onroad":
    ui.is_offroad = lambda: False
  elif change == "interceptor":
    ui.CP_SP.enableGasInterceptor = True
  elif change == "stock":
    ui.CP_SP.flags |= HondaFlagsSP.STOCK_LONGITUDINAL
  elif change == "missing_cp":
    ui.CP = None
  elif change == "missing_cp_sp":
    ui.CP_SP = None
  elif change == "stale_identity":
    ui.params.values["CarPlatformBundle"] = {"brand": "honda", "platform": "HONDA_CLARITY"}
  elif change == "openlong_off":
    ui.CP.openpilotLongitudinalControl = False
  elif change == "non_honda":
    ui.CP.brand = "toyota"
  else:
    ui.CP.carFingerprint = {"clarity": "HONDA_CLARITY", "pilot": "HONDA_PILOT", "bosch": "HONDA_CIVIC_BOSCH"}[change]
  # Deliberately click with a stale enabled widget, before any display refresh.
  engine.toggle._handle_mouse_release(None)
  assert not ui.params.writes
  assert ui.params.get_bool("NrdrExperimentalEngineBraking") is saved
  assert engine.toggle.get_state() is saved
  layout._update_state()
  assert engine.enabled is False
  assert engine.toggle.get_state() is saved
  # Direct callback invocations must be guarded as well.
  engine.kwargs["callback"](not saved)
  assert not ui.params.writes
  assert engine.toggle.get_state() is saved


def test_native_engine_missing_vehicle_is_safe_at_initialization_and_refresh():
  ui = state()
  ui.CP = ui.CP_SP = None
  layout = native_layout_with_real_toggle_handlers(ui)
  assert not layout._engine_braking.enabled()
  assert layout._engine_braking.toggle.get_state() is False
  layout._update_state()
  assert layout._engine_braking.enabled is False
  layout._engine_braking.kwargs["callback"](True)
  assert not ui.params.writes


def test_mici_controls_are_in_requested_order_and_wired_into_device_menu():
  path = ROOT / "openpilot/nrdr/ui/settings/pcm_modes_mici.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  tree.body = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "longitudinal_controls"]
  env = {"tr": lambda s: s, "BigParamControl": Widget, "LiveGasControl": lambda: "live",
         "mici_reset_button": lambda: "reset", "PcmModeControl": lambda: "mode", "WindBrakeControl": lambda: "wind",
         "EngineBrakeControl": lambda: "engine", "OverspeedAllowanceControl": lambda: "overspeed"}
  exec(compile(tree, str(path), "exec"), env)
  controls = env["longitudinal_controls"]()
  assert controls[:4] == ["live", "reset", "mode", "wind"]
  assert controls[4].text == "Keep Feedforward Static"
  assert controls[5:] == ["engine", "overspeed"]
  device = (ROOT / "openpilot/selfdrive/ui/sunnypilot/mici/layouts/device.py").read_text(encoding="utf-8")
  assert "self._longitudinal_controls = longitudinal_controls()" in device
  assert "self._scroller.add_widgets(self._longitudinal_controls)" in device


def compact_controls(ui):
  from openpilot.nrdr.features.longitudinal.policy import nrdr_longitudinal_enabled

  class Selector:
    def __init__(self):
      self.buttons = []
      self._scroller = NS(add_widgets=self.buttons.extend)

  pushed, popped = [], []
  path = ROOT / "openpilot/nrdr/ui/settings/pcm_modes_mici.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  tree.body = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name in ("EngineBrakeControl", "OverspeedAllowanceControl")]
  env = {"BigToggle": Widget, "BigButton": Widget, "NavScroller": Selector,
         "ui_state": ui, "tr": lambda s: s, "pcm_tuning_available": pcm_tuning_available,
         "save_pcm_choice": save_pcm_choice, "nrdr_longitudinal_enabled": nrdr_longitudinal_enabled,
         "gui_app": NS(push_widget=pushed.append, pop_widget=lambda: popped.append(True))}
  exec(compile(tree, str(path), "exec"), env)
  return env["EngineBrakeControl"](), env["OverspeedAllowanceControl"](), pushed, popped


def test_mici_engine_refreshes_saved_choice_and_rechecks_parked_state():
  ui = state()
  engine, _, _, _ = compact_controls(ui)
  assert engine.enabled()
  assert engine.kwargs["initial_state"] is False
  engine._select(True)
  assert ui.params.writes == [("NrdrExperimentalEngineBraking", True), ("OnroadCycleRequested", True)]
  assert engine.value is True
  ui.params.values["NrdrExperimentalEngineBraking"] = False
  engine._update_state()
  assert engine.value is False
  ui.params.writes.clear()
  ui.is_offroad = lambda: False
  assert not engine.enabled()
  engine._select(True)
  assert engine.value is False
  assert not ui.params.writes


@pytest.mark.parametrize("car", list(CAR))
def test_mici_engine_control_is_civic_pcm_only(car):
  ui = state(carFingerprint=str(car))
  engine, _, _, _ = compact_controls(ui)
  assert engine.enabled() == (car == CAR.HONDA_CIVIC)
  engine._select(True)
  assert bool(ui.params.writes) == (car == CAR.HONDA_CIVIC)


@pytest.mark.parametrize("change", ["interceptor", "stock", "missing_cp", "missing_cp_sp", "stale_identity", "openlong_off"])
def test_mici_engine_selection_rechecks_vehicle_after_menu_opens(change):
  ui = state()
  engine, _, _, _ = compact_controls(ui)
  assert engine.enabled()
  if change == "interceptor":
    ui.CP_SP.enableGasInterceptor = True
  elif change == "stock":
    ui.CP_SP.flags |= HondaFlagsSP.STOCK_LONGITUDINAL
  elif change == "missing_cp":
    ui.CP = None
  elif change == "missing_cp_sp":
    ui.CP_SP = None
  elif change == "stale_identity":
    ui.params.values["CarPlatformBundle"] = {"brand": "honda", "platform": "HONDA_CLARITY"}
  else:
    ui.CP.openpilotLongitudinalControl = False
  assert not engine.enabled()
  engine._select(True)
  assert engine.value is False and not ui.params.writes


@pytest.mark.parametrize("value", range(11))
def test_mici_overspeed_uses_separate_nav_choices_and_saves_each_value(value):
  ui = state()
  ui.params.values["NrdrCruiseOverspeedAllowance"] = 5
  _, allowance, pushed, popped = compact_controls(ui)
  assert allowance.value == "5 mph"
  allowance.click_callback()
  assert len(pushed) == 1
  choices = pushed[0].buttons
  assert [button.text for button in choices] == [f"{i} mph" for i in range(11)]
  assert [button.kwargs["value"] for button in choices] == ["selected" if i == 5 else "" for i in range(11)]
  choices[value].click_callback()
  assert ui.params.writes == [("NrdrCruiseOverspeedAllowance", value)]
  assert allowance.value == f"{value} mph"
  assert popped == [True]
  ui.params.values["NrdrCruiseOverspeedAllowance"] = 10 - value
  allowance._update_state()
  assert allowance.value == f"{10 - value} mph"


@pytest.mark.parametrize("value", [None, True, False, -1, 11, 1.0, "5", b"5", {}])
def test_mici_overspeed_invalid_values_do_not_write_or_navigate(value):
  ui = state()
  ui.params.values["NrdrCruiseOverspeedAllowance"] = value
  _, allowance, pushed, popped = compact_controls(ui)
  assert allowance.value == "0 mph"
  allowance._select(value)
  assert not ui.params.writes and not pushed and not popped


@pytest.mark.parametrize("change", ["onroad", "non_honda", "missing_cp"])
def test_mici_overspeed_rechecks_before_opening_and_saving(change):
  ui = state()
  _, allowance, pushed, popped = compact_controls(ui)
  allowance.click_callback()
  choice = pushed[0].buttons[8]
  if change == "onroad":
    ui.is_offroad = lambda: False
  elif change == "non_honda":
    ui.CP.brand = "toyota"
  else:
    ui.CP = None
  assert not allowance.enabled() and not choice.enabled()
  choice.click_callback()
  allowance.click_callback()
  assert not ui.params.writes and not popped and len(pushed) == 1


def test_mici_device_show_refresh_is_not_position_dependent():
  calls = []

  class DeviceBase:
    def show_event(self):
      calls.append("base")

  path = ROOT / "openpilot/selfdrive/ui/sunnypilot/mici/layouts/device.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  tree.body = [n for n in tree.body if isinstance(n, ast.ClassDef)]
  env = {"DeviceLayoutMici": DeviceBase}
  exec(compile(tree, str(path), "exec"), env)
  device = object.__new__(env["DeviceLayoutMiciSP"])
  device._disable_power_down = NS(refresh=lambda: calls.append("power"))
  device._longitudinal_controls = [NS(), NS(refresh=lambda: calls.append("static")),
                                   NS(refresh=lambda: calls.append("engine")), NS(refresh=lambda: calls.append("overspeed")), NS()]
  device.show_event()
  assert calls == ["base", "power", "static", "engine", "overspeed"]


def test_mici_new_control_labels_fit_the_compact_cards():
  engine, allowance, _, _ = compact_controls(state())
  for control, width, has_value in ((engine, engine._title_width_hint(), False), (allowance, 322, True)):
    size = control.kwargs["font_size"]
    lines = []
    for word in control.text.split():
      joined = f"{lines[-1]} {word}" if lines else word
      if lines and _font_advance_upper_bound("Inter-Bold.ttf", joined, size) <= width:
        lines[-1] = joined
      else:
        lines.append(word)
    assert all(_font_advance_upper_bound("Inter-Bold.ttf", line, size) <= width for line in lines)
    title_height = size * 1.16 * (1 + .9 * (len(lines) - 1))
    assert title_height + (36 * 1.16 if has_value else 0) <= 180 - 2 * 23
