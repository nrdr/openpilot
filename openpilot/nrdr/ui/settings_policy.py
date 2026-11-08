from openpilot.system.ui.lib.multilang import tr
from openpilot.nrdr.params.tuning_policy import tuning_write_allowed


CRUISE_PARAMS = (
  "CustomAccIncrementsEnabled",
  "SmartCruiseControlVision",
  "SmartCruiseControlMap",
)

UI_CONSTRAINT_PARAMS = (
  "ExperimentalMode",
  "CustomAccIncrementsEnabled",
  "SmartCruiseControlVision",
  "SmartCruiseControlMap",
)


def snapshot_params(params, keys):
  return {key: value for key in keys if (value := params.get(key)) is not None}


def _restore_params(params, values, CP=None):
  for key, value in values.items():
    # Parked preconfiguration permits explicit edits, not automatic replay of
    # an old UI snapshot while a saved/previous controller owns these choices.
    if tuning_write_allowed(params, key, CP=CP, is_offroad=False):
      params.put(key, value)


def restore_params(params, values):
  _restore_params(params, values)


def apply_cruise_preferences(layout, state, values, has_long, has_icbm):
  # The legacy snapshot argument is intentionally ignored: refresh must never
  # replay a saved value over a newer explicit user/Sunnylink choice.
  editable = state.is_offroad()
  if editable:
    layout.custom_acc_toggle.set_description(tr("You can set this now. It activates once your car is detected and supports custom cruise increments."))
    layout.custom_acc_toggle.show_description(True)

  # Only presentation changes while parked. Runtime capabilities and ICBM's
  # separate hardware admission remain unchanged.
  layout.accel_boost_toggle.action_item.set_enabled(editable or has_long)
  layout.custom_acc_toggle.action_item.set_enabled(editable)
  layout.scc_v_toggle.action_item.set_enabled(editable or has_long or has_icbm)
  layout.scc_m_toggle.action_item.set_enabled(editable or has_long or has_icbm)
  layout._on_custom_acc_toggle(layout.custom_acc_toggle.action_item.get_state())


def apply_speed_limit_preferences(control, state, value, available):
  # Availability changes presentation only. Never replay this UI snapshot over
  # a newer explicit choice made on the device or through Sunnylink.
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


def hide_global_controller_settings(items):
  return items[:-5]
