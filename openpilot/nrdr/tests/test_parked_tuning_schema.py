"""Parked Sunnylink editing changes presentation, never controller ownership."""
import copy
import json
from pathlib import Path

import pytest

from openpilot.nrdr.params.tuning_policy import LEGACY_PCM_LOCK_KEYS, LONG_SCALE_KEYS, MVL_LOCK_KEYS, RETIRED_TUNING_KEYS, SUGGESTED_DESCRIPTION
from openpilot.nrdr.params.mvl_pcm_deadzone import MVL_PCM_DEADZONE_DESCRIPTION
from openpilot.nrdr.params.nidec_pcm import PCM_EXPERIMENT_DETAILS
from openpilot.nrdr.ui.sunnylink_schema import apply_sunnylink_metadata
from openpilot.sunnypilot.sunnylink.tools.compile_settings_ui import DEFAULT_OUT, DEFAULT_SRC, compile_schema


def evaluate(rule, values):
  kind = rule["type"]
  if kind == "offroad_only":
    return values.get("IsOffroad") is True
  if kind == "not_engaged":
    return values.get("engaged") is False
  if kind in ("param", "capability"):
    return values.get(rule.get("key", rule.get("field"))) == rule["equals"]
  if kind == "not":
    return not evaluate(rule["condition"], values)
  if kind in ("all", "any"):
    return (all if kind == "all" else any)(evaluate(condition, values) for condition in rule["conditions"])
  raise AssertionError(f"Unhandled schema rule: {rule}")


def allowed(item, values, field="enablement"):
  return all(evaluate(rule, values) for rule in item.get(field, []))


def mode_values(*, offroad=True, saved=True, active=True, exempt=False, legacy=True):
  return {"IsOffroad": offroad, "HondaLiveLearningGas": saved, "nrdr_mvl_longitudinal_active": active,
          "nrdr_mvl_tuning_exempt": exempt, "nrdr_honda_legacy_pcm_locked": legacy}


def items_in(node):
  if isinstance(node, dict):
    if "widget" in node and "key" in node:
      yield node
    for value in node.values():
      yield from items_in(value)
  elif isinstance(node, list):
    for value in node:
      yield from items_in(value)


@pytest.fixture(scope="module")
def schema():
  return compile_schema(DEFAULT_SRC)


@pytest.fixture(scope="module")
def items(schema):
  return {item["key"]: item for item in items_in(schema)}


@pytest.mark.parametrize("key", sorted(MVL_LOCK_KEYS | LEGACY_PCM_LOCK_KEYS))
def test_parked_editing_accepts_saved_and_cached_modes_without_clearing_capabilities(key):
  values = mode_values()  # Both saved/latched modes deliberately remain true.
  snapshot = dict(values)
  item = apply_sunnylink_metadata({"key": key})
  assert allowed(item, values)
  assert values == snapshot
  for rule in item["enablement"]:
    assert rule["type"] == "any"
    assert rule["conditions"][0] == {"type": "offroad_only"}
    assert rule["conditions"][1]["type"] == "not"


@pytest.mark.parametrize("key", ["LongPidTuneScaleStandard", "AccelBoostSP", "HondaLiveLearningGas", "NrdrMvlPcmDeadzone"])
@pytest.mark.parametrize("offroad", [False, True, None])
@pytest.mark.parametrize("saved,active,exempt,legacy", [
  (False, False, False, False),
  (True, False, False, False),  # Saved ON, controller not yet selected.
  (False, True, False, False),  # Saved OFF, cached CP still MVL.
  (True, True, False, False),
  (True, False, True, False),  # Other vehicle ignores saved Honda mode.
  (False, False, False, True),  # Saved/latched Legacy ownership capability.
  (True, True, False, True),
])
def test_mode_rule_keeps_onroad_semantics_and_requires_positive_offroad_evidence(key, offroad, saved, active, exempt, legacy):
  values = mode_values(offroad=offroad, saved=saved, active=active, exempt=exempt, legacy=legacy)
  blocked = ((key in MVL_LOCK_KEYS and (active or saved and not exempt)) or
             (key in LEGACY_PCM_LOCK_KEYS and legacy))
  assert allowed(apply_sunnylink_metadata({"key": key}), values) is (offroad is True or not blocked)


@pytest.mark.parametrize("key", sorted(LONG_SCALE_KEYS))
def test_pid_scales_stay_visible_while_parked_without_bypassing_existing_visibility(key):
  original = {"key": key, "visibility": [{"type": "capability", "field": "has_longitudinal_control", "equals": True}]}
  item = apply_sunnylink_metadata(original)
  values = {**mode_values(), "has_longitudinal_control": True}
  assert allowed(item, values, "visibility") and allowed(item, values)
  values["has_longitudinal_control"] = False
  assert not allowed(item, values, "visibility")
  assert item["visibility"][:-1] == original["visibility"]


def test_existing_hardware_parked_and_engagement_rules_remain_independent():
  original = {
    "key": "AccelBoostSP",
    "enablement": [{"type": "offroad_only"}, {"type": "not_engaged"},
                   {"type": "capability", "field": "has_longitudinal_control", "equals": True}],
    "visibility": [{"type": "param", "key": "show_tuning", "equals": True}],
  }
  snapshot = copy.deepcopy(original)
  item = apply_sunnylink_metadata(original)
  assert original == snapshot
  assert item["enablement"][:-2] == original["enablement"]
  assert item["visibility"] == original["visibility"]
  values = {**mode_values(), "has_longitudinal_control": True, "show_tuning": True, "engaged": False}
  assert allowed(item, values)
  assert not allowed(item, {**values, "has_longitudinal_control": False})
  assert not allowed(item, {**values, "engaged": True})
  assert not allowed(item, {**values, "show_tuning": False}, "visibility")
  no_modes = {**values, **mode_values(offroad=False, saved=False, active=False, legacy=False)}
  assert not allowed(item, no_modes)  # Original offroad-only requirement survives even without either mode.


@pytest.mark.parametrize("key,restriction,value", [
  ("LatPScaleStandard", "NrdrHandcraftedLateralTune", True),
  ("LatPScaleStandard", "NrdrLateralController", 1),
  ("HondaTorqueLowPassFilter", "NrdrLateralController", 1),
  ("LaneCenterOffset", "NrdrHandcraftedLateralTune", True),
  ("LagdToggleDelay", "NrdrLateralController", 1),
])
def test_parked_mode_exception_does_not_unlock_lateral_guards(key, restriction, value):
  values = {**mode_values(), "NrdrSuggestedSettings": False, "NrdrHandcraftedLateralTune": False,
            "NrdrLateralController": 0, "nrdr_firmware_prediction_schedule": True}
  item = apply_sunnylink_metadata({"key": key})
  assert allowed(item, values)
  assert not allowed(item, {**values, restriction: value})
  assert item["enablement"][1] == {
    "type": "not", "condition": {"type": "param", "key": "NrdrHandcraftedLateralTune", "equals": True},
  }
  assert "offroad_only" not in json.dumps(item["enablement"][1:])


@pytest.mark.parametrize("key", ["LaneGuidanceMode", "LaneCenteringStrength", "NrdrSteerRatioSourceB",
                                 "LatPScaleStandard", "LagdToggle", "NrdrDeviceYawCorrection"])
@pytest.mark.parametrize("offroad", [False, True, None])
@pytest.mark.parametrize("suggested,pending", [(False, False), (True, False), (False, True), (True, True)])
def test_completed_preset_is_editable_parked_but_pending_apply_is_not(key, offroad, suggested, pending):
  values = {"IsOffroad": offroad, "NrdrSuggestedSettings": suggested, "NrdrHandcraftedLateralTune": pending,
            "NrdrLateralController": 0, "nrdr_firmware_prediction_schedule": False}
  snapshot = dict(values)
  assert allowed(apply_sunnylink_metadata({"key": key}), values) is ((offroad is True or not suggested) and not pending)
  assert values == snapshot  # Editing eligibility never clears the completed marker.


def test_compiled_blendful_keeps_custom_model_and_pending_apply_guards(items):
  item = items["LaneGuidanceMode"]
  sunny = next(option for option in item["options"] if option["value"] == 2)
  values = {"IsOffroad": True, "NrdrSuggestedSettings": True, "NrdrHandcraftedLateralTune": False,
            "custom_model_active": True}
  assert allowed(item, values) and allowed(sunny, values)
  assert not allowed(item, {**values, "NrdrHandcraftedLateralTune": True})
  assert not allowed(item, {**values, "IsOffroad": False})
  assert not allowed(sunny, {**values, "custom_model_active": False})


def test_compiled_firmware_compatibility_survives_parked_preset_exception(items):
  picker = items["NrdrLateralController"]
  firmware = next(option for option in picker["options"] if option["value"] == 1)
  values = {"IsOffroad": True, "NrdrSuggestedSettings": True, "NrdrHandcraftedLateralTune": False,
            "nrdr_yaw_controller_available": False, "NrdrLateralController": 1}
  assert allowed(picker, values)
  assert not allowed(firmware, values)
  assert not allowed(items["NrdrDeviceYawCorrection"], values, "visibility")


def test_compiled_cruise_has_no_blanket_preset_lock_and_preserves_icbm_action_guard(schema, items):
  page = next(panel for panel in schema["panels"] if panel["id"] == "cruise")
  assert not page.get("enablement")
  values = {**mode_values(), "NrdrSuggestedSettings": True, "NrdrHandcraftedLateralTune": False,
            "has_longitudinal_control": True, "has_icbm": False, "pcm_cruise": True}
  for key in ("ExperimentalMode", "DisengageOnAccelerator", "LongitudinalPersonality", "SpeedLimitMode",
              "SpeedLimitPolicy", "SmartCruiseControlVision", "SmartCruiseControlMap", "AccelBoostSP"):
    assert allowed(items[key], values), key
  assert allowed(items["CustomAccIncrementsEnabled"], values)
  assert not allowed(items["IntelligentCruiseButtonManagement"], values)


@pytest.mark.parametrize("offroad", [False, True, None])
@pytest.mark.parametrize("has_long,has_icbm,pcm_cruise", [(False, False, False), (True, False, True),
                                                       (True, False, False), (False, True, True)])
def test_cruise_parked_preconfiguration_checks_sections_and_items(schema, items, offroad, has_long, has_icbm, pcm_cruise):
  page = next(panel for panel in schema["panels"] if panel["id"] == "cruise")
  sections = {section["id"]: section for section in page["sections"]}
  values = {**mode_values(offroad=offroad, saved=False, active=False, legacy=False),
            "has_longitudinal_control": has_long, "has_icbm": has_icbm, "pcm_cruise": pcm_cruise,
            "CustomAccIncrementsEnabled": True}
  snapshot = dict(values)
  parked = offroad is True
  for key in ("ExperimentalMode", "LongitudinalPersonality"):
    assert (allowed(sections["core_cruise_features"], values) and allowed(items[key], values)) is (parked or has_long)

  scc = sections["smart_cruise"]
  assert allowed(scc, values) is (parked or has_long or has_icbm)
  for key in ("SmartCruiseControlVision", "SmartCruiseControlMap"):
    assert allowed(items[key], values, "visibility") is (parked or has_long or has_icbm)
    assert (allowed(scc, values) and allowed(items[key], values)) is (parked or has_long or has_icbm)
  assert (allowed(scc, values) and allowed(items["AccelBoostSP"], values)) is (parked or has_long)

  increments = sections["custom_acc_increments"]
  assert allowed(increments, values) is parked  # Existing mandatory offroad rule is retained.
  assert allowed(items["CustomAccIncrementsEnabled"], values) is parked
  subpanel = increments["sub_panels"][0]
  assert evaluate(subpanel["trigger_condition"], values)
  for key in ("CustomAccShortPressIncrement", "CustomAccLongPressIncrement"):
    assert (allowed(increments, values) and allowed(subpanel, values) and allowed(items[key], values)) is parked
    assert not allowed(items[key], {**values, "CustomAccIncrementsEnabled": False})
  assert values == snapshot  # Presentation does not promote hardware/activation capabilities.


def test_parked_cruise_preferences_do_not_bypass_actual_option_or_hardware_action_gates(items):
  values = {**mode_values(), "has_longitudinal_control": True, "has_icbm": False, "icbm_available": False,
            "nrdr_longitudinal_tuning_available": False, "brand": "honda", "is_sp_release": False}
  econ = next(option for option in items["LongitudinalPersonality"]["options"] if option["value"] == 3)
  assert allowed(items["LongitudinalPersonality"], values)
  assert not allowed(econ, values)
  assert not allowed(items["IntelligentCruiseButtonManagement"], values, "visibility")
  assert not allowed(items["IntelligentCruiseButtonManagement"], values)
  assist = next(option for option in items["SpeedLimitMode"]["options"] if option["value"] == 3)
  assert allowed(assist, values)
  assert not allowed(assist, {**values, "brand": "rivian"})
  assert not allowed(assist, {**values, "brand": "tesla", "is_sp_release": True})
  assert not allowed(assist, {**values, "has_longitudinal_control": False})


def test_suggested_copy_uses_parent_owned_shared_description(items):
  assert items["NrdrSuggestedSettings"]["description"] == SUGGESTED_DESCRIPTION
  assert "parked" in SUGGESTED_DESCRIPTION
  assert "Turn Suggested Settings OFF to unlock" not in items["NrdrDeviceYawCorrection"]["details"]


@pytest.mark.parametrize("key,capability", [
  ("NrdrHondaPcmMode", "nrdr_honda_pcm_tuning_available"),
  ("NrdrHondaWindBrake", "nrdr_honda_pcm_tuning_available"),
  ("HondaLiveLearningGas", "nrdr_honda_mvl_selection_available"),
  ("NrdrMvlPcmDeadzone", "nrdr_mvl_pcm_deadzone_available"),
])
def test_compiled_parked_controls_preserve_hardware_gates(items, key, capability):
  values = {**mode_values(), capability: True}
  assert allowed(items[key], values)
  assert allowed(items[key], values, "visibility")
  assert not allowed(items[key], {**values, capability: False})
  assert not allowed(items[key], {**values, "IsOffroad": False})


def test_compiled_deadzone_can_be_saved_with_mvl_off_but_still_requires_confirmed_pcm(items):
  item = items["NrdrMvlPcmDeadzone"]
  values = {**mode_values(saved=False, active=False, legacy=False), "nrdr_mvl_pcm_deadzone_available": True}
  assert allowed(item, values) and allowed(item, values, "visibility")
  values["nrdr_mvl_pcm_deadzone_available"] = False
  assert not allowed(item, values) and not allowed(item, values, "visibility")
  assert [option["value"] for option in item["options"]] == [0, 2, 5, 10]


def test_compiled_schema_keeps_pid_controls_and_omits_retired_tuning(items):
  for key in LONG_SCALE_KEYS - {"LongPidTuneScale"}:
    assert allowed(items[key], mode_values(), "visibility")
    assert allowed(items[key], mode_values())
  assert not RETIRED_TUNING_KEYS.intersection(items)
  assert not any(key.startswith("NrdrNnlc") for key in items)


def test_compiled_copy_explains_saved_choices_instead_of_parked_lockout(items):
  for key in (LONG_SCALE_KEYS - {"LongPidTuneScale"}) | {"HondaLiveLearningGas", "NrdrHondaLegacyPcm",
                                                       "NrdrHondaFullBrakeAuthority", "NrdrRoenAccelerationLimits"}:
    details = items[key]["details"]
    assert "editable while parked" in details.lower()
    assert "use depends on the selected controller" in details
    assert "Unavailable while MVL" not in details
    assert "locked" not in details
  assert items["NrdrHondaLegacyPcm"]["details"] == PCM_EXPERIMENT_DETAILS["NrdrHondaLegacyPcm"]
  assert items["NrdrMvlPcmDeadzone"]["description"] == MVL_PCM_DEADZONE_DESCRIPTION
  assert "even with MVL off" in items["NrdrMvlPcmDeadzone"]["description"]
  assert "no gas interceptor" in items["NrdrHondaLegacyPcm"]["details"]
  assert "gas interceptor" in items["NrdrRoenAccelerationLimits"]["details"]


def test_generated_schema_matches_existing_compiler(schema):
  assert schema == json.loads(Path(DEFAULT_OUT).read_text(encoding="utf-8"))
