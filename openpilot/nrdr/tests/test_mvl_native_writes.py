"""Execute native write handlers without a renderer, hardware or native Params."""
import ast
from collections.abc import Callable, Sequence
from pathlib import Path
from types import SimpleNamespace as NS
from typing import Union

import pytest

from opendbc.car.structs import car
from openpilot.nrdr.params.tuning_policy import MVL_LOCK_KEYS, tuning_write_allowed

ROOT = Path(__file__).resolve().parents[3]


class Params(dict):
  def __init__(self, **values):
    super().__init__(values)
    self.writes = []

  def get(self, key, *args, **kwargs):
    return super().get(key)

  def get_bool(self, key, *args):
    return bool(self.get(key))

  def put(self, key, value, **kwargs):
    self.writes.append((key, value))
    self[key] = value

  put_bool = put


def state(saved=False, active=False, brand="honda"):
  cp = car.CarParams.new_message(brand=brand, openpilotLongitudinalControl=True, flags=131072 if active else 0)
  params = Params(HondaLiveLearningGas=saved, CarParams=cp.to_bytes(), ExperimentalMode=False, ExperimentalModeConfirmed=True)
  return NS(CP=cp, CP_SP=NS(), params=params, has_longitudinal_control=True, experimental_mode=False,
            experimental_mode_confirmed=True, sm=NS(updated={"selfdriveState": False}))


class Widget:
  def __init__(self, *args, **kwargs):
    self._enabled = True
    self._checked = self._state = kwargs.get("initial_state", False)
    self.callback = kwargs.get("toggle_callback", kwargs.get("callback"))
    self._options = args[1] if len(args) > 1 and isinstance(args[1], list) else []
    self.value = self._options[0] if self._options else ""

  @property
  def enabled(self):
    return self._enabled() if callable(self._enabled) else self._enabled

  def set_enabled(self, enabled):
    self._enabled = enabled

  def _handle_mouse_release(self, pos):
    self._checked = self._state = not self._checked
    if self._options:
      self.value = self._options[(self._options.index(self.value) + 1) % len(self._options)]
    if self.callback:
      self.callback(self._checked)

  def set_checked(self, value):
    self._checked = self._state = value

  set_state = set_checked

  def set_value(self, value):
    self.value = value

  def _update_state(self):
    pass


def definitions(path, names, env, methods=None):
  tree = ast.parse((ROOT / path).read_text(encoding="utf-8"))
  tree.body = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
  if methods is not None:
    for cls in tree.body:
      if isinstance(cls, ast.ClassDef):
        cls.body = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in methods]
  exec(compile(tree, path, "exec"), env)
  return env


def widget_env(params):
  return {"Params": lambda: params, "tuning_write_allowed": tuning_write_allowed, "Callable": Callable,
          # This suite checks widget admission; the real lock/protocol is covered
          # by test_mvl_personality_sync with atomic files and separate processes.
          "write_personality": lambda p, value: p.put("LongitudinalPersonality", value, block=True),
          "Sequence": Sequence, "Union": Union, "MousePos": object, "Widget": Widget,
          "rl": NS(Texture=object, Rectangle=lambda *a: NS(x=0, y=0, width=100, height=100), check_collision_point_rec=lambda *a: True),
          "style": NS(TOGGLE_WIDTH=100, BUTTON_HEIGHT=100), "LABEL_WIDTH": 350}


def mici_control(kind, params, key):
  env = widget_env(params)
  env.update(BigToggle=Widget, BigCircleToggle=Widget, BigMultiToggle=Widget)
  definitions("openpilot/selfdrive/ui/mici/widgets/button.py",
              {"_ParamWritePolicy", "BigParamControl", "BigCircleParamControl", "BigMultiParamToggle"}, env)
  return env[kind]("control", key, ["off", "on"]) if kind == "BigMultiParamToggle" else env[kind]("control", key)


@pytest.mark.parametrize("kind", ["BigParamControl", "BigCircleParamControl", "BigMultiParamToggle"])
@pytest.mark.parametrize("saved,active", [(True, False), (False, True)])
@pytest.mark.parametrize("key", sorted(MVL_LOCK_KEYS))
def test_mici_every_conflicting_key_is_visibly_locked_and_cannot_write(kind, saved, active, key):
  ui = state(saved, active)
  ui.params[key] = 0
  control = mici_control(kind, ui.params, key)
  control.set_enabled(True)  # A layout refresh must not override the policy.
  assert not control.enabled
  control._handle_mouse_release(None)  # Deliberately bypass normal hit testing.
  assert not ui.params.writes and ui.params[key] == 0


@pytest.mark.parametrize("kind", ["BigParamControl", "BigCircleParamControl", "BigMultiParamToggle"])
@pytest.mark.parametrize("key", ["LongitudinalPersonality", "DisengageOnAccelerator", "AlwaysOnDM",
                                "AlphaLongitudinalEnabled", "HondaEnforceStockLongitudinal", "LaneGuidanceMode", "NrdrResetLiveGas"])
def test_mici_mvl_does_not_disable_personalities_safeguards_hardware_lateral_or_reset(kind, key):
  ui = state(True, True)
  ui.params[key] = 0
  control = mici_control(kind, ui.params, key)
  assert control.enabled
  control._handle_mouse_release(None)
  assert ui.params.writes == [(key, 1)]


@pytest.mark.parametrize("kind", ["BigParamControl", "BigCircleParamControl", "BigMultiParamToggle"])
def test_mici_rechecks_after_callbacks_and_keeps_caller_disable_gates(kind):
  ui = state()
  ui.params["AccelBoostSP"] = 0
  control = mici_control(kind, ui.params, "AccelBoostSP")
  control.set_enabled(lambda: False)
  control._handle_mouse_release(None)
  assert not ui.params.writes
  control.set_enabled(True)
  control.callback = lambda *_: ui.params.update(HondaLiveLearningGas=True)
  control._handle_mouse_release(None)
  assert not ui.params.writes and not control.enabled
  assert control.value == "off" if kind == "BigMultiParamToggle" else not control._checked


@pytest.mark.parametrize("kind", ["BigParamControl", "BigCircleParamControl", "BigMultiParamToggle"])
def test_mici_non_honda_does_not_inherit_saved_honda_lock(kind):
  ui = state(True, brand="toyota")
  ui.params["AccelBoostSP"] = 0
  control = mici_control(kind, ui.params, "AccelBoostSP")
  assert control.enabled
  control._handle_mouse_release(None)
  assert ui.params.writes == [("AccelBoostSP", 1)]


def tici_control(kind, params, key):
  env = widget_env(params)
  env.update(Toggle=Widget, ToggleAction=Widget, MultipleButtonAction=Widget, ItemAction=Widget)
  definitions("openpilot/system/ui/widgets/toggle.py", {"Toggle"}, env)
  definitions("openpilot/system/ui/sunnypilot/widgets/toggle.py", {"ToggleSP"}, env)
  definitions("openpilot/system/ui/sunnypilot/widgets/list_view.py", {"ToggleActionSP", "MultipleButtonActionSP"}, env)
  definitions("openpilot/system/ui/sunnypilot/widgets/option_control.py", {"OptionControlSP"}, env)
  obj = env[kind].__new__(env[kind])
  obj._enabled = True
  if kind == "ToggleActionSP":
    obj.toggle = env["ToggleSP"](param=key)
  else:
    obj.params, obj.param_key = params, key
    obj.current_value = obj.selected_button = 0
    obj.min_value, obj.max_value, obj.value_map = 0, 100, None
    obj.use_float_scaling = False
    obj.on_value_changed = obj.callback = None
    obj.buttons, obj.button_width, obj.enabled_buttons = ["off", "on"], 50, None
    obj._rect = NS(x=0, y=0, width=100, height=100)
  return obj


@pytest.mark.parametrize("kind", ["ToggleActionSP", "MultipleButtonActionSP", "OptionControlSP"])
@pytest.mark.parametrize("key", sorted(MVL_LOCK_KEYS))
@pytest.mark.parametrize("saved,active", [(True, False), (False, True)])
def test_tici_bound_widgets_show_policy_disabled_and_block_stale_direct_writes(kind, key, saved, active):
  ui = state(saved, active)
  ui.params[key] = 0
  control = tici_control(kind, ui.params, key)
  control.set_enabled(True)
  assert not control.enabled
  if kind == "ToggleActionSP":
    control.toggle._handle_mouse_release(None)
  elif kind == "OptionControlSP":
    control.set_value(1)
  else:
    control._handle_mouse_release(None)
  assert not ui.params.writes and ui.params[key] == 0


@pytest.mark.parametrize("kind,key", [("ToggleActionSP", "AccelBoostSP"), ("MultipleButtonActionSP", "SpeedLimitMode")])
def test_tici_post_callback_cannot_write_after_mvl_becomes_selected(kind, key):
  ui = state()
  ui.params[key] = 0
  control = tici_control(kind, ui.params, key)
  def callback(*_):
    ui.params.update(HondaLiveLearningGas=True)
  if kind == "ToggleActionSP":
    control.toggle._callback = callback
    control.toggle._handle_mouse_release(None)
  else:
    control.callback = callback
    control._handle_mouse_release(None)
  assert not ui.params.writes


@pytest.mark.parametrize("kind", ["ToggleActionSP", "MultipleButtonActionSP", "OptionControlSP"])
@pytest.mark.parametrize("key", ["AccelBoostSP", "ExperimentalMode", "SmartCruiseControlVision", "CustomAccIncrementsEnabled",
                                "CustomAccShortPressIncrement", "CustomAccLongPressIncrement"])
def test_tici_global_sunny_preferences_remain_editable_after_vehicle_swap(kind, key):
  ui = state(True, brand="toyota")
  ui.params[key] = 0
  control = tici_control(kind, ui.params, key)
  assert control.enabled
  if kind == "ToggleActionSP":
    control.toggle._handle_mouse_release(None)
  elif kind == "OptionControlSP":
    control.set_value(1)
  else:
    control._handle_mouse_release(None)
  assert ui.params.writes == [(key, 1)]


def experimental_layout(ui, mici):
  dialogs = []
  env = {"Widget": Widget, "NavScroller": Widget, "ui_state": ui, "tuning_write_allowed": tuning_write_allowed,
         "DialogResult": NS(CONFIRM=1), "tr": lambda s: s,
         "gui_app": NS(push_widget=dialogs.append), "ExperimentalModeConfirmPage": lambda cb: cb,
         "ConfirmDialog": lambda *a, **kw: kw["callback"]}
  path = "openpilot/selfdrive/ui/mici/layouts/settings/toggles.py" if mici else "openpilot/selfdrive/ui/layouts/settings/toggles.py"
  name = "TogglesLayoutMici" if mici else "TogglesLayout"
  definitions(path, {name}, env, {"_experimental_mode_editable", "_on_experimental_mode", "_handle_experimental_mode_toggle", "_update_state"})
  layout = env[name]()
  action = Widget()
  layout._params, layout._locked_toggles = ui.params, set()
  layout._toggles = {"ExperimentalMode": NS(action_item=action, title="Experimental", description="")}
  layout._experimental_btn = action
  action.set_enabled(layout._experimental_mode_editable)
  layout._update_experimental_mode_icon = lambda: None
  return layout, dialogs, action


@pytest.mark.parametrize("mici", [False, True])
@pytest.mark.parametrize("saved,active", [(False, False), (True, False), (False, True), (True, True)])
@pytest.mark.parametrize("selected", [False, True])
@pytest.mark.parametrize("offroad", [False, True])
def test_experimental_manual_on_off_remains_live_during_mvl_restart_states(mici, saved, active, selected, offroad):
  ui = state(saved, active)
  ui.is_offroad = lambda: offroad
  ui.started = ui.engaged = not offroad
  ui.params["ExperimentalMode"] = not selected
  layout, dialogs, action = experimental_layout(ui, mici)
  select = layout._on_experimental_mode if mici else layout._handle_experimental_mode_toggle
  layout._update_state()
  assert action.enabled and layout._experimental_mode_editable()
  assert not ui.params.writes  # Refresh must never change the saved preference.
  select(selected)
  assert not dialogs
  assert ui.params.writes == [("ExperimentalMode", selected)]
  assert ui.params["ExperimentalMode"] is selected


@pytest.mark.parametrize("mici", [False, True])
@pytest.mark.parametrize("saved,active", [(True, False), (False, True), (True, True)])
def test_experimental_confirmation_allows_mvl_selection_or_restart_race(mici, saved, active):
  ui = state()
  ui.params["ExperimentalModeConfirmed"] = False
  layout, dialogs, action = experimental_layout(ui, mici)
  select = layout._on_experimental_mode if mici else layout._handle_experimental_mode_toggle
  select(True)
  assert len(dialogs) == 1 and not ui.params.writes
  ui.params["HondaLiveLearningGas"] = saved
  ui.CP.flags = 131072 if active else 0
  assert layout._experimental_mode_editable()
  dialogs[0]() if mici else dialogs[0](1)
  assert ui.params["ExperimentalMode"] is True
  assert ui.params["ExperimentalModeConfirmed"] is True
  assert sorted(ui.params.writes) == [("ExperimentalMode", True), ("ExperimentalModeConfirmed", True)]
  ui.params.writes.clear()
  select(False)
  assert ui.params.writes == [("ExperimentalMode", False)]


@pytest.mark.parametrize("mici", [False, True])
def test_experimental_confirmation_rechecks_hardware_availability(mici):
  ui = state(True, True)
  ui.params["ExperimentalModeConfirmed"] = False
  layout, dialogs, action = experimental_layout(ui, mici)
  select = layout._on_experimental_mode if mici else layout._handle_experimental_mode_toggle
  select(True)
  assert len(dialogs) == 1 and not ui.params.writes
  ui.CP.openpilotLongitudinalControl = ui.has_longitudinal_control = False
  dialogs[0]() if mici else dialogs[0](1)
  select(True)
  layout._update_state()
  assert not layout._experimental_mode_editable() and not action.enabled
  assert not ui.params.writes and not action._checked


def test_tici_experimental_confirmation_cancel_does_not_write():
  ui = state(True, True)
  ui.params["ExperimentalModeConfirmed"] = False
  layout, dialogs, action = experimental_layout(ui, False)
  layout._handle_experimental_mode_toggle(True)
  dialogs[0](0)
  assert not ui.params.writes and not action._checked


@pytest.mark.parametrize("mici", [False, True])
def test_experimental_settings_remain_available_on_non_honda(mici):
  ui = state(True, brand="toyota")
  layout, _, _ = experimental_layout(ui, mici)
  select = layout._on_experimental_mode if mici else layout._handle_experimental_mode_toggle
  assert layout._experimental_mode_editable()
  select(True)
  assert ui.params.writes == [("ExperimentalMode", True)]


@pytest.mark.parametrize("saved,active", [(False, False), (True, False), (False, True), (True, True)])
@pytest.mark.parametrize("selected", [False, True])
@pytest.mark.parametrize("openlong,confirmed", [(True, True), (False, True), (True, False)])
def test_home_and_onroad_shortcuts_keep_manual_mode_and_availability_guards(saved, active, selected, openlong, confirmed):
  ui = state(saved, active)
  ui.CP.openpilotLongitudinalControl = ui.has_longitudinal_control = openlong
  ui.params["ExperimentalModeConfirmed"] = ui.experimental_mode_confirmed = confirmed
  ui.params["ExperimentalMode"] = ui.experimental_mode = not selected
  expected = [("ExperimentalMode", selected)] if openlong and confirmed else []
  env = {"Widget": Widget, "ui_state": ui, "tuning_write_allowed": tuning_write_allowed, "time": NS(monotonic=lambda: 1.)}
  definitions("openpilot/selfdrive/ui/mici/layouts/home.py", {"MiciHomeLayout"}, env, {"_update_state"})
  home = env["MiciHomeLayout"]()
  home.is_pressed = home._is_pressed_prev = True
  home._mouse_down_t = 0.
  home._update_state()
  assert ui.params.writes == expected
  assert ui.experimental_mode is (selected if expected else not selected)
  ui.params.writes.clear()
  ui.params["ExperimentalMode"] = not selected
  definitions("openpilot/selfdrive/ui/onroad/exp_button.py", {"ExpButton"}, env, {"_is_toggle_allowed", "_handle_mouse_release"})
  button = env["ExpButton"]()
  button._params, button._experimental_mode = ui.params, not selected
  button._hold_duration = 2.
  button._handle_mouse_release(None)
  assert button._is_toggle_allowed() is (openlong and confirmed)
  assert ui.params.writes == expected


@pytest.mark.parametrize("saved,active", [(True, False), (False, True)])
def test_preference_refresh_cannot_replay_conflicting_values(saved, active):
  ui = state(saved, active)
  env = {"tuning_write_allowed": tuning_write_allowed, "tr": lambda s: s}
  definitions("openpilot/nrdr/ui/settings_policy.py", {"_restore_params", "restore_params", "apply_speed_limit_preferences"}, env)
  env["restore_params"](ui.params, dict.fromkeys(MVL_LOCK_KEYS, 1))
  env["apply_speed_limit_preferences"](None, ui, 3, True)
  assert not ui.params.writes
  env["restore_params"](ui.params, {"AlwaysOnDM": True, "LongitudinalPersonality": 3})
  assert ui.params.writes == [("AlwaysOnDM", True), ("LongitudinalPersonality", 3)]


@pytest.mark.parametrize("saved,active,text", [(False, False, "MVL inactive"), (True, False, "MVL next drive"),
                                             (False, True, "MVL active\nOff next drive"), (True, True, "MVL active")])
@pytest.mark.parametrize("offroad", [False, True])
def test_mici_mode_status_uses_road_state_and_latched_mode(saved, active, text, offroad):
  from openpilot.nrdr.ui.honda_pcm import live_gas_status
  ui = state(saved, active)
  ui.is_offroad = lambda: offroad
  env = {"BigToggle": Widget, "ui_state": ui, "tr": lambda s: s, "live_gas_status": live_gas_status}
  definitions("openpilot/nrdr/ui/settings/pcm_modes_mici.py", {"LiveGasControl"}, env, {"_mode_status", "_refresh", "_update_state"})
  control = env["LiveGasControl"]()
  control._update_state()
  assert control.value == (("MVL next drive" if saved else "MVL Off next drive") if offroad else text)
  assert control._checked is saved
  ui.params["HondaLiveLearningGas"] = not saved
  control._update_state()
  assert control._checked is not saved and ("active" in control.value and "inactive" not in control.value) is (active and not offroad)
  if offroad:
    assert control.value == ("MVL Off next drive" if saved else "MVL next drive")
  assert not ui.params.writes


def test_mici_live_mode_status_fits_below_the_title_and_left_of_the_toggle():
  from openpilot.nrdr.tests.test_honda_pcm_ui import _font_advance_upper_bound
  path = ROOT / "openpilot/nrdr/ui/settings/pcm_modes_mici.py"
  cls = next(n for n in ast.parse(path.read_text()).body if isinstance(n, ast.ClassDef) and n.name == "LiveGasControl")
  init = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "__init__")
  size = next(k.value.value for n in ast.walk(init) if isinstance(n, ast.Call) for k in n.keywords if k.arg == "font_size")
  assert _font_advance_upper_bound("Inter-Bold.ttf", "Live Learning Gas", size) < 266
  for line in ("MVL active", "MVL inactive", "Off next drive", "MVL next drive", "MVL Off next drive", "Legacy next drive", "MVL saved", "MVL Off"):
    assert _font_advance_upper_bound("Inter-Regular.ttf", line, 36) < 322
  assert size * 1.16 + 2 * 36 * 1.16 < 180 - 2 * 23


@pytest.mark.parametrize("mici", [False, True])
@pytest.mark.parametrize("saved,active", [(True, False), (False, True)])
def test_lateral_diagnostic_callback_can_clear_manual_experimental_without_unlocking_dec(mici, saved, active):
  ui = state(saved, active)
  ui.params["ExperimentalMode"] = True
  env = {"Widget": Widget, "NavScroller": Widget, "ui_state": ui, "tuning_write_allowed": tuning_write_allowed,
         "restart_needed_callback": lambda: None}
  path = "openpilot/selfdrive/ui/mici/layouts/settings/developer.py" if mici else "openpilot/selfdrive/ui/layouts/settings/developer.py"
  name = "DeveloperLayoutMici" if mici else "DeveloperLayout"
  definitions(path, {name}, env, {"_on_lat_maneuver_mode"})
  layout = env[name]()
  layout._params = ui.params
  action = Widget()
  action.action_item = action
  layout._joystick_toggle = layout._long_maneuver_toggle = action
  layout._on_lat_maneuver_mode(True)
  assert ui.params["ExperimentalMode"] is False
  assert ui.params.writes == [("LateralManeuverMode", True), ("ExperimentalMode", False),
                             ("JoystickDebugMode", False), ("LongitudinalManeuverMode", False)]
  assert not tuning_write_allowed(ui.params, "DynamicExperimentalControl", CP=ui.CP)


@pytest.mark.parametrize("saved,active", [(True, False), (False, True)])
def test_speed_limit_automatic_downgrade_and_refresh_never_write_while_locked(saved, active):
  ui = state(saved, active)
  ui.params["SpeedLimitMode"] = 3
  # Simulate a stale UI availability snapshot; the boot-latched CP remains authoritative.
  ui.has_longitudinal_control = ui.has_icbm = ui.is_sp_release = False
  ui.is_offroad = lambda: True
  env = {"Widget": Widget, "ui_state": ui, "tuning_write_allowed": tuning_write_allowed, "tr": lambda s: s,
         "SpeedLimitMode": NS(off=0, information=1, warning=2, assist=3), "SpeedLimitOffsetType": NS(off=0)}
  definitions("openpilot/nrdr/ui/settings_policy.py", {"apply_speed_limit_preferences"}, env)
  definitions("openpilot/selfdrive/ui/sunnypilot/layouts/settings/cruise_sub_layouts/speed_limit_settings.py",
              {"SpeedLimitSettingsLayout"}, env, {"_update_state"})
  layout = env["SpeedLimitSettingsLayout"]()
  layout._speed_limit_mode = NS(action_item=NS(set_enabled_buttons=lambda *_: None))
  layout._speed_limit_value_offset = NS(set_visible=lambda *_: None)
  layout._update_state()
  assert not ui.params.writes and ui.params["SpeedLimitMode"] == 3
