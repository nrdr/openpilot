from openpilot.system.ui.lib.multilang import tr


CRUISE_PARAMS = (
  "CustomAccIncrementsEnabled",
  "DynamicExperimentalControl",
  "SmartCruiseControlVision",
  "SmartCruiseControlMap",
)

UI_CONSTRAINT_PARAMS = (
  "ExperimentalMode",
  "DynamicExperimentalControl",
  "CustomAccIncrementsEnabled",
  "SmartCruiseControlVision",
  "SmartCruiseControlMap",
)


def snapshot_params(params, keys):
  return {key: value for key in keys if (value := params.get(key)) is not None}


def _restore_params(params, values):
  for key, value in values.items():
    params.put(key, value)


def restore_params(params, values):
  _restore_params(params, values)


def apply_cruise_preferences(layout, state, values, has_long, has_icbm):
  _restore_params(state.params, values)

  if state.is_offroad():
    layout.custom_acc_toggle.set_description(tr("You can set this now. It activates once your car is detected and supports custom cruise increments."))
    layout.custom_acc_toggle.show_description(True)

  if has_long or has_icbm:
    return

  editable = state.is_offroad()
  layout.custom_acc_toggle.action_item.set_enabled(editable)
  layout.dec_toggle.action_item.set_enabled(editable)
  layout.scc_v_toggle.action_item.set_enabled(editable)
  layout.scc_m_toggle.action_item.set_enabled(editable)
  layout._on_custom_acc_toggle(layout.custom_acc_toggle.action_item.get_state())


def apply_speed_limit_preferences(control, state, value, available):
  if value is not None:
    state.params.put("SpeedLimitMode", value)

  if available:
    return

  enabled = {0, 1, 2}
  brand = state.CP.brand if state.CP is not None else None
  disallowed = brand == "rivian" or (brand == "tesla" and state.is_sp_release)
  if state.is_offroad() and not disallowed:
    enabled.add(3)
  control.action_item.set_enabled_buttons(enabled)


def apply_chevron_preference(control, state, value):
  if state.has_longitudinal_control:
    return

  state.params.put("ChevronInfo", value)
  control.action_item.set_selected_button(value)
  control.action_item.set_enabled(state.is_offroad())


def apply_handcrafted_delay_controls(layout, state):
  from openpilot.nrdr.params import is_handcrafted_lateral_enabled

  fingerprint = str(state.CP.carFingerprint) if state.CP is not None else ""
  enabled = not is_handcrafted_lateral_enabled(fingerprint, state.params)
  layout.lagd_toggle.action_item.set_enabled(enabled)
  layout.delay_control.action_item.set_enabled(enabled)


def hide_global_controller_settings(items):
  return items[:-5]
