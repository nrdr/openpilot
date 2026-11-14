"""Native Cruise preconfiguration must not change capability or replay preferences."""
from types import SimpleNamespace as NS

import pytest

from opendbc.car.honda.values import HondaFlags
from openpilot.nrdr.params.tuning_policy import tuning_write_allowed
from openpilot.nrdr.ui.icbm import icbm_available
from openpilot.nrdr.tests.test_experimental_button_regressions import RecordingParams
from openpilot.nrdr.tests.test_mvl_native_writes import definitions, tici_control
from openpilot.nrdr.tests.test_nidec_pcm_experiments import cp_bytes


TOGGLES = {"accel_boost_toggle": "AccelBoostSP", "custom_acc_toggle": "CustomAccIncrementsEnabled",
           "scc_v_toggle": "SmartCruiseControlVision", "scc_m_toggle": "SmartCruiseControlMap"}
INCREMENTS = {"custom_acc_short_increment": "CustomAccShortPressIncrement", "custom_acc_long_increment": "CustomAccLongPressIncrement"}
PREFERENCES = (*TOGGLES.values(), *INCREMENTS.values())


class Params(RecordingParams):
  def get(self, key, *args, **kwargs):
    return super().get(key)


class Item:
  def __init__(self, params, key):
    self.params, self.key = params, key
    self.action_item = self
    self.description = ""
    self._enabled = True
    self.value = params.get(key)

  @property
  def enabled(self):
    return self._enabled and tuning_write_allowed(self.params, self.key)

  def set_enabled(self, value):
    self._enabled = value

  def set_state(self, value):
    self.value = value

  def get_state(self):
    return self.value

  def set_description(self, value):
    self.description = value

  def show_description(self, value):
    self.description_visible = value

  def set_visible(self, value):
    self.visible = value


def cruise_layout(offroad, vehicle, mode, initial=True):
  flags = {"custom": 0, "mvl": HondaFlags.MVL_LONGITUDINAL, "legacy": 524288}[mode]
  params = Params({"IsOffroad": offroad, "HondaLiveLearningGas": mode == "mvl", "NrdrHondaLegacyPcm": mode == "legacy",
                   "CarParamsPersistent": cp_bytes(flags), **dict.fromkeys(TOGGLES.values(), initial),
                   "CustomAccShortPressIncrement": 3, "CustomAccLongPressIncrement": 5})
  has_long, has_icbm = vehicle in ("long", "fixed"), vehicle == "icbm"
  cp = None if vehicle == "missing" else NS(brand="honda", carFingerprint="unsupported", flags=0, openpilotLongitudinalControl=has_long,
                                           pcmCruise=vehicle in ("stock", "fixed"), alphaLongitudinalAvailable=False)
  cp_sp = None if vehicle == "missing" else NS(intelligentCruiseButtonManagementAvailable=has_icbm, pcmCruiseSpeed=vehicle != "fixed",
                                              enableGasInterceptor=False)
  ui = NS(params=params, CP=cp, CP_SP=cp_sp, has_longitudinal_control=has_long, has_icbm=has_icbm, is_offroad=lambda: offroad)
  env = {"ui_state": ui, "tr": lambda text: text, "tuning_write_allowed": tuning_write_allowed,
         "icbm_available": icbm_available,
         "Widget": type("Widget", (), {"_update_state": lambda self: None})}
  for name in ("ICBM_DESC", "ICMB_UNAVAILABLE", "ICMB_UNAVAILABLE_LONG_AVAILABLE", "ICMB_UNAVAILABLE_LONG_UNAVAILABLE",
               "ONROAD_ONLY_DESCRIPTION", "ACC_PCMCRUISE_DISABLED_DESCRIPTION", "ACC_ENABLED_DESCRIPTION", "ACC_NOLONG_DESCRIPTION"):
    env[name] = name
  definitions("openpilot/nrdr/ui/settings_policy.py", {"apply_cruise_preferences"}, env)
  definitions("openpilot/selfdrive/ui/sunnypilot/layouts/settings/cruise.py", {"CruiseLayout"}, env,
              {"_update_state", "_on_custom_acc_toggle"})
  layout = env["CruiseLayout"]()
  for attr, key in {**TOGGLES, **INCREMENTS, "icbm_toggle": "IntelligentCruiseButtonManagement"}.items():
    setattr(layout, attr, Item(params, key))
  return layout, ui, env["apply_cruise_preferences"]


@pytest.mark.parametrize("offroad", [False, True])
@pytest.mark.parametrize("vehicle", ["missing", "stock", "long", "icbm", "fixed"])
@pytest.mark.parametrize("mode", ["custom", "mvl", "legacy"])
@pytest.mark.parametrize("initial", [False, True])
def test_refresh_preserves_preferences_and_only_relaxes_parked_normal_controls(offroad, vehicle, mode, initial):
  layout, ui, _ = cruise_layout(offroad, vehicle, mode, initial)
  before = {key: ui.params.get(key) for key in PREFERENCES}
  capabilities = (ui.CP, ui.CP_SP, ui.has_longitudinal_control, ui.has_icbm)
  for _ in range(3):
    layout._update_state()
  ui.params.flush()
  assert {key: ui.params.get(key) for key in PREFERENCES} == before
  assert not any(action[1] in PREFERENCES for action in ui.params.actions)
  assert capabilities == (ui.CP, ui.CP_SP, ui.has_longitudinal_control, ui.has_icbm)
  assert layout.icbm_toggle.enabled is (offroad and vehicle == "icbm")
  assert layout.custom_acc_toggle.enabled is offroad
  assert layout.custom_acc_short_increment.enabled is offroad
  assert layout.custom_acc_long_increment.enabled is offroad
  assert layout.accel_boost_toggle.enabled is (offroad or vehicle in ("long", "fixed"))
  assert layout.scc_v_toggle.enabled is (offroad or vehicle in ("long", "fixed", "icbm"))
  assert layout.scc_m_toggle.enabled is layout.scc_v_toggle.enabled


@pytest.mark.parametrize("offroad", [False, True])
@pytest.mark.parametrize("mode", ["mvl", "legacy"])
@pytest.mark.parametrize("key", PREFERENCES)
def test_explicit_generic_widget_writes_keep_onroad_mode_guard(offroad, mode, key):
  _, ui, _ = cruise_layout(offroad, "missing", mode)
  kind = "OptionControlSP" if key in INCREMENTS.values() else "ToggleActionSP"
  control = tici_control(kind, ui.params, key)
  writable = True
  assert control.enabled is writable
  if kind == "OptionControlSP":
    control.set_value(4)
  else:
    control.toggle._handle_mouse_release(None)
  ui.params.flush()
  assert ui.params.actions == ([("put", key, 4 if kind == "OptionControlSP" else False)] if writable else [])


@pytest.mark.parametrize("offroad", [False, True])
@pytest.mark.parametrize("mode", ["custom", "mvl", "legacy"])
def test_legacy_snapshot_argument_cannot_replay_a_newer_choice(offroad, mode):
  layout, ui, apply = cruise_layout(offroad, "stock", mode, initial=False)
  before = dict(ui.params.values)
  apply(layout, ui, dict.fromkeys(PREFERENCES, True), False, False)
  ui.params.flush()
  assert ui.params.values == before and not ui.params.actions
