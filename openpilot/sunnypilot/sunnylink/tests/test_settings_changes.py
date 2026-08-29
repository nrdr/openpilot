"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Per-bug regression tests for the Raylib-vs-schema parity audit. Each test
isolates one of the gating bugs that the design-overhaul branch fixes so a
future regression is loud and obvious. These tests are intentionally narrow
and additive — they do not replace the broader test_settings_schema.py.
"""
from __future__ import annotations

import ast
import json
import os
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
from typing import Any

from openpilot.common.parameterized import parameterized


# Schema generation only needs capability field declarations. Avoid loading the
# Linux-only hardware/IPC extensions when these source regressions run on Windows.
if sys.platform == "win32":
  hardware_module = ModuleType("openpilot.common.hardware")
  hardware_module.PC = True
  hardware_module.HARDWARE = SimpleNamespace(get_device_type=lambda: "pc")
  sys.modules.setdefault("openpilot.common.hardware", hardware_module)
  hardware_hw_module = ModuleType("openpilot.common.hardware.hw")
  hardware_hw_module.Paths = SimpleNamespace(persist_root=lambda: "")
  sys.modules.setdefault("openpilot.common.hardware.hw", hardware_hw_module)

  params_module = ModuleType("openpilot.common.params")
  params_module.Params = type("Params", (), {
    "get": lambda _self, _key, **_kwargs: None,
    "get_bool": lambda _self, _key: False,
  })
  params_module.UnknownKeyName = type("UnknownKeyName", (Exception,), {})
  sys.modules.setdefault("openpilot.common.params", params_module)

  swaglog_module = ModuleType("openpilot.common.swaglog")
  swaglog_module.cloudlog = SimpleNamespace(
    exception=lambda *_args, **_kwargs: None,
    warning=lambda *_args, **_kwargs: None,
  )
  sys.modules.setdefault("openpilot.common.swaglog", swaglog_module)

  messaging_module = ModuleType("openpilot.cereal.messaging")
  messaging_module.SubMaster = object
  sys.modules.setdefault("openpilot.cereal.messaging", messaging_module)

from openpilot.sunnypilot.sunnylink.tools.generate_settings_schema import (
  DEFINITION_PATH,
  TORQUE_VERSIONS_PATH,
  _build_torque_options,
  _load_torque_versions,
  generate_schema,
)
from openpilot.common.test import OpenpilotTestCase


SCHEMA_VALIDATOR_PATH = os.path.join(os.path.dirname(DEFINITION_PATH), "settings_ui.schema.json")


def _fold_static_string(node: ast.AST) -> str:
  if isinstance(node, ast.Constant) and isinstance(node.value, str):
    return node.value
  if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
    return _fold_static_string(node.left) + _fold_static_string(node.right)
  raise AssertionError(f"expected a static string expression, got {ast.dump(node)}")


def _walk_items(schema: dict[str, Any]):
  """Yield every item dict from the schema."""
  def _yield(item: dict[str, Any]):
    yield item
    for sub in item.get("sub_items", []):
      yield from _yield(sub)

  for panel in schema.get("panels", []):
    for section in panel.get("sections", []):
      for item in section.get("items", []):
        yield from _yield(item)
      for sp in section.get("sub_panels", []):
        for item in sp.get("items", []):
          yield from _yield(item)
    for item in panel.get("items", []):
      yield from _yield(item)
    for sp in panel.get("sub_panels", []):
      for item in sp.get("items", []):
        yield from _yield(item)
  for brand in schema.get("vehicle_settings", {}).values():
    items = brand.get("items", []) if isinstance(brand, dict) else brand
    for item in items:
      yield from _yield(item)


def _find_item(schema: dict[str, Any], key: str) -> dict[str, Any] | None:
  for item in _walk_items(schema):
    if item.get("key") == key:
      return item
  return None


def _find_section(schema: dict[str, Any], panel_id: str, section_id: str) -> dict[str, Any] | None:
  for panel in schema.get("panels", []):
    if panel.get("id") != panel_id:
      continue
    for section in panel.get("sections", []):
      if section.get("id") == section_id:
        return section
  return None


def _flatten_rule_types(rules: list[dict[str, Any]] | None) -> set[str]:
  out: set[str] = set()

  def _walk(rule: dict[str, Any]) -> None:
    out.add(rule.get("type", ""))
    if rule.get("type") == "not" and "condition" in rule:
      _walk(rule["condition"])
    elif rule.get("type") in ("any", "all"):
      for c in rule.get("conditions", []):
        _walk(c)

  for rule in rules or []:
    _walk(rule)
  return out


def _references_capability_field(rules: list[dict[str, Any]] | None, field: str) -> bool:
  found = False

  def _walk(rule: dict[str, Any]) -> None:
    nonlocal found
    if rule.get("type") == "capability" and rule.get("field") == field:
      found = True
    elif rule.get("type") == "not" and "condition" in rule:
      _walk(rule["condition"])
    elif rule.get("type") in ("any", "all"):
      for c in rule.get("conditions", []):
        _walk(c)

  for rule in rules or []:
    _walk(rule)
  return found


def schema():
  return generate_schema()


class TestMadsBrandGates(OpenpilotTestCase):
  def test_mads_main_cruise_has_brand_gate(self, schema):
    """MadsMainCruiseAllowed must gate on brand and tesla_has_vehicle_bus."""
    item = _find_item(schema, "MadsMainCruiseAllowed")
    assert item is not None
    assert _references_capability_field(item.get("enablement"), "brand")
    assert _references_capability_field(item.get("enablement"), "tesla_has_vehicle_bus")

  def test_mads_unified_engagement_has_brand_gate(self, schema):
    """MadsUnifiedEngagementMode must mirror MadsMainCruiseAllowed brand-gate."""
    item = _find_item(schema, "MadsUnifiedEngagementMode")
    assert item is not None
    assert _references_capability_field(item.get("enablement"), "brand")
    assert _references_capability_field(item.get("enablement"), "tesla_has_vehicle_bus")


class TestTestManeuversSection(OpenpilotTestCase):
  def test_lateral_maneuver_mode_in_test_maneuvers(self, schema):
    section = _find_section(schema, "developer", "test_maneuvers")
    assert section is not None, "developer.test_maneuvers section missing"
    keys = {item["key"] for item in section.get("items", [])}
    assert "LateralManeuverMode" in keys
    assert "LongitudinalManeuverMode" in keys

  def test_test_maneuvers_section_requires_attestation(self, schema):
    section = _find_section(schema, "developer", "test_maneuvers")
    assert section is not None
    assert section.get("attestation_required") is True

  def test_test_maneuvers_section_visibility_gate(self, schema):
    section = _find_section(schema, "developer", "test_maneuvers")
    assert section is not None
    visibility = section.get("visibility")
    assert visibility, "test_maneuvers must have visibility gate"
    vis_refs = json.dumps(visibility)
    assert "is_development" in vis_refs
    assert "is_sp_release" in vis_refs
    enablement = section.get("enablement") or []
    enable_refs = json.dumps(enablement)
    assert "ShowAdvancedControls" in enable_refs, \
      "test_maneuvers must gate ShowAdvancedControls via enablement"


class TestValidator(OpenpilotTestCase):
  def test_validator_accepts_real_json(self):
    """settings_ui.json validates against settings_ui.schema.json."""
    try:
      import jsonschema
    except ImportError:
      self.skipTest("jsonschema not installed")
    with open(DEFINITION_PATH) as f:
      data = json.load(f)
    with open(SCHEMA_VALIDATOR_PATH) as f:
      validator = json.load(f)
    jsonschema.validate(instance=data, schema=validator)


class TestTorqueOptionGeneration(OpenpilotTestCase):
  def test_torque_versions_match_generated_options(self, schema):
    versions = _load_torque_versions()
    assert versions, "latcontrol_torque_versions.json must have at least one version"
    expected = _build_torque_options(versions)
    item = _find_item(schema, "TorqueControlTune")
    if item is None:
      # nrdr intentionally hides the global Torque/NNLC controls. The Clarity
      # uses its fingerprint-scoped PID/NNLC hybrid and exposes only its safe knobs.
      assert _find_item(schema, "EnforceTorqueControl") is None
      assert _find_item(schema, "NrdrNnlcEnabled") is not None
      return
    assert item.get("options") == expected

  def test_torque_versions_path_resolves(self):
    assert os.path.exists(TORQUE_VERSIONS_PATH), (
      f"latcontrol_torque_versions.json not found at {TORQUE_VERSIONS_PATH}"
    )


class TestReleaseBranchGates(OpenpilotTestCase):
  @parameterized.expand([
    "EnableGithubRunner",
    "QuickBootToggle",
  ], names=["key"])
  def test_sp_dev_items_gate_on_is_sp_release(self, schema, key):
    """sunnypilot dev items must hide on sunnypilot release branches (is_sp_release gate)."""
    item = _find_item(schema, key)
    assert item is not None, f"{key} not found in schema"
    rules = (item.get("visibility") or []) + (item.get("enablement") or [])
    assert _references_capability_field(rules, "is_sp_release"), f"{key} missing is_sp_release gate"


class TestSpuriousOffroadGatesDropped(OpenpilotTestCase):
  def test_disengage_on_accelerator_has_no_offroad_only(self, schema):
    item = _find_item(schema, "DisengageOnAccelerator")
    assert item is not None
    assert "offroad_only" not in _flatten_rule_types(item.get("enablement"))

  def test_dynamic_experimental_has_no_offroad_only(self, schema):
    item = _find_item(schema, "DynamicExperimentalControl")
    assert item is not None
    assert "offroad_only" not in _flatten_rule_types(item.get("enablement"))


class TestDevicePowerPolicy(OpenpilotTestCase):
  def test_prevent_shutdown_is_offroad_only_and_precedes_timer(self, schema):
    section = _find_section(schema, "device", "general")
    assert section is not None
    keys = [item["key"] for item in section["items"]]
    prevent_index = keys.index("DisablePowerDown")
    assert keys[prevent_index + 1] == "MaxTimeOffroad"

    prevent = section["items"][prevent_index]
    assert prevent["widget"] == "toggle"
    assert prevent["title"] == "Prevent Automatic Shutdown"
    assert "offroad_only" in _flatten_rule_types(prevent.get("enablement"))

  def test_power_policy_copy_matches_native_ui(self, schema):
    prevent = _find_item(schema, "DisablePowerDown")
    assert prevent is not None
    sunnylink_copy = f"{prevent.get('title', '')} {prevent.get('description', '')} {prevent.get('details', '')}".lower()
    repo_root = Path(__file__).parents[4]
    canonical_copy = (repo_root / "openpilot" / "nrdr" / "ui" / "settings" /
                      "device_power.py").read_text(encoding="utf-8").lower()

    for phrase in (
      "prevent automatic shutdown",
      "automatic offroad shutdowns",
      "max time offroad timer",
      "low-voltage and estimated-battery safeguards",
      "drain the vehicle battery",
      "60-second grace period",
      "manual power off still works",
    ):
      assert phrase in sunnylink_copy
      assert phrase in canonical_copy

    assert "return ui_state.is_offroad() and not ui_state.params.get_bool(nrdrparamkey.disable_power_down)" in canonical_copy
    assert "enabled=ui_state.is_offroad" in canonical_copy
    assert "nrdrparamkey.disable_power_down" in canonical_copy
    assert "prevent automatic\\nshutdown" in canonical_copy
    assert "battery drain risk" in canonical_copy
    assert "ui_state.is_offroad" in canonical_copy

  def test_offroad_timer_is_subordinate_and_not_mislabeled(self, schema):
    timer = _find_item(schema, "MaxTimeOffroad")
    assert timer is not None
    assert timer["options"][0] == {"value": 0, "label": "No Time Limit"}
    assert "Always On" not in json.dumps(timer)
    assert "offroad_only" in _flatten_rule_types(timer.get("enablement"))
    assert {"type": "param", "key": "DisablePowerDown", "equals": False} in timer["enablement"]

    timer_copy = f"{timer.get('description', '')} {timer.get('details', '')}".lower()
    assert "applies only when prevent automatic shutdown is disabled" in timer_copy
    assert "battery safeguards may shut the device down sooner" in timer_copy


class TestNrdrLongitudinalOptions(OpenpilotTestCase):
  PERSONALITY_SCALE_KEYS = (
    "LongPidTuneScaleAggressive",
    "LongPidTuneScaleStandard",
    "LongPidTuneScaleRelaxed",
    "LongPidTuneScaleEcon",
  )

  @parameterized.expand([
    ("NrdrHondaFullBrakeAuthority", "toggle"),
    ("NrdrRoenAccelerationLimits", "toggle"),
    ("NrdrCruiseOverspeedAllowance", "option"),
  ], names=["key", "widget"])
  def test_options_are_independent_of_live_learning_gas(self, schema, key, widget):
    item = _find_item(schema, key)
    assert item is not None
    assert item.get("widget") == widget
    rules = json.dumps((item.get("visibility") or []) + (item.get("enablement") or []))
    assert "HondaLiveLearningGas" not in rules

  def test_overspeed_allowance_range(self, schema):
    item = _find_item(schema, "NrdrCruiseOverspeedAllowance")
    assert item is not None
    assert (item.get("min"), item.get("max"), item.get("step"), item.get("unit")) == (0, 10, 1, "mph")

  def test_longitudinal_default_descriptions(self, schema):
    roen = _find_item(schema, "NrdrRoenAccelerationLimits")
    live_gas = _find_item(schema, "HondaLiveLearningGas")
    assert "Enabled by default" in roen.get("details", "")
    assert "default OFF when a gas pedal interceptor is detected" in live_gas.get("details", "")
    assert "selection is preserved" in live_gas.get("details", "")

  def test_honda_bosch_a_radar_scope_is_explicit(self, schema):
    radar = _find_item(schema, "HondaBoschARadar")
    assert radar is not None
    copy = f"{radar.get('description', '')} {radar.get('details', '')}".lower()
    assert "stock longitudinal or openpilot alpha long" in copy
    assert "feed openpilot's lead tracking" in copy
    assert "factory honda aeb/cmbs remains unavailable" in copy

  @parameterized.expand(PERSONALITY_SCALE_KEYS, names=["key"])
  def test_personality_pid_scale_range(self, schema, key):
    item = _find_item(schema, key)
    assert item is not None
    assert item.get("widget") == "option"
    assert (item.get("min"), item.get("max"), item.get("step"), item.get("unit")) == (0, 500, 5, "%")

  def test_longitudinal_panel_follows_toggle_then_option_order(self, schema):
    section = _find_section(schema, "cruise", "nrdr")
    assert section is not None
    panel = next(sub_panel for sub_panel in section.get("sub_panels", []) if sub_panel.get("id") == "nrdr_longitudinal")
    items = panel.get("items", [])
    keys = [item["key"] for item in items]
    widgets = [item["widget"] for item in items]
    toggle_indices = [i for i, widget in enumerate(widgets) if widget == "toggle"]
    option_indices = [i for i, widget in enumerate(widgets) if widget == "option"]
    scale_indices = [keys.index(key) for key in self.PERSONALITY_SCALE_KEYS]

    assert keys[0] == "HondaLiveLearningGas"
    assert set(widgets) == {"toggle", "option"}
    assert max(toggle_indices) < min(option_indices)
    assert scale_indices == list(range(scale_indices[0], scale_indices[0] + len(self.PERSONALITY_SCALE_KEYS)))
    assert [keys[index] for index in scale_indices] == list(self.PERSONALITY_SCALE_KEYS)

  @parameterized.expand(
    tuple(zip(PERSONALITY_SCALE_KEYS, (200, 100, 80, 50), strict=True)),
    names=["key", "default"],
  )
  def test_personality_pid_scale_describes_default(self, schema, key, default):
    item = _find_item(schema, key)
    assert item is not None
    assert f"Defaults to {default}%" in item.get("details", "")


class TestInterpolatedTorquePifBlend(OpenpilotTestCase):
  KEYS = (
    "NrdrInterpolatedTorquePifBlend",
    "NrdrInterpolatedTorqueShare",
    "NrdrInterpolatedTorqueLatAccelFactor",
    "NrdrInterpolatedTorqueFriction",
    "NrdrInterpolatedTorqueFrictionStandard",
    "NrdrInterpolatedTorqueFrictionHighway",
  )

  def test_master_and_complete_tuple_are_onroad_editable_and_capability_gated(self, schema):
    master = _find_item(schema, self.KEYS[0])
    assert master is not None
    assert master["title"] == "Interpolated Torque/PIF Blend"
    assert "angle feedback through 2 m/s" in master["details"]
    assert "calibrated yaw at 5 m/s and above" in master["details"]
    assert "final request temporarily returns to 100% P/I/F" in master["details"]
    assert "does not reuse angle or update its controller state" in master["details"]
    assert "not historically road-proven on Honda" in master["details"]
    assert "save all six settings while driving" in master["details"]
    assert "next disengage and re-engage" in master["details"]
    assert "already disengaged, wait up to 10 seconds" in master["details"]
    assert "NNLC is bypassed and reset" in master["details"]
    assert [item["key"] for item in master["sub_items"]] == list(self.KEYS[1:])

    for item in (master, *master["sub_items"]):
      rules = item.get("enablement")
      assert "offroad_only" not in _flatten_rule_types(rules)
      assert _references_capability_field(rules, "nrdr_interpolated_torque_pif_blend_available")

    for item in master["sub_items"]:
      assert "NrdrInterpolatedTorquePifBlend" in json.dumps(item["enablement"])

  def test_locked_ranges_units_and_complementary_copy(self, schema):
    share = _find_item(schema, "NrdrInterpolatedTorqueShare")
    assert (share["min"], share["max"], share["step"], share["unit"]) == (0, 100, 1, "%")
    assert "Torque X% / P/I/F (100-X)%" in share["description"]

    laf = _find_item(schema, "NrdrInterpolatedTorqueLatAccelFactor")
    assert (laf["min"], laf["max"], laf["step"], laf["unit"]) == (0.1, 10.0, 0.1, "m/s²")
    assert "scales Torque feedback error" in laf["details"]
    assert "never direct friction" in laf["details"]

    friction_titles = {
      "NrdrInterpolatedTorqueFriction": "Low-Speed Torque Friction (Below 25mph)",
      "NrdrInterpolatedTorqueFrictionStandard": "Standard-Speed Torque Friction (25-50mph)",
      "NrdrInterpolatedTorqueFrictionHighway": "Highway Torque Friction (50mph+)",
    }
    for key, title in friction_titles.items():
      friction = _find_item(schema, key)
      assert (friction["min"], friction["max"], friction["step"]) == (0.0, 1.0, 0.01)
      assert friction["title"] == title
      assert "±1 mph handoff" in friction["details"]

  def test_nnlc_controls_are_mutually_exclusive(self, schema):
    for key in ("NrdrNnlcEnabled", "NrdrNnlcActivationSpeed", "NrdrNnlcKpGain", "NrdrNnlcKfGain", "NrdrNnlcKiGain"):
      rules = json.dumps(_find_item(schema, key).get("enablement") or [])
      assert "NrdrInterpolatedTorquePifBlend" in rules
      assert '"type": "not"' in rules


class TestNrdrSteerRatioMode(OpenpilotTestCase):
  FORMER_HANDCRAFTED_LOCKED_KEYS = (
    "NrdrLearnStiffness", "NrdrLearnAngleOffset", "NrdrStarPilotPid",
    "LatPScaleLowSpeed", "LatIScaleLowSpeed", "LatFScaleLowSpeed",
    "LatPScaleStandard", "LatIScaleStandard", "LatFScaleStandard",
    "LatPScaleHighway", "LatIScaleHighway", "LatFScaleHighway",
    "NrdrLatRateDamping", "NrdrLatRateDampingFadeSpeed",
    "HondaCenterScale", "HondaCenterBoostThreshold", "HondaCenterBoostMinSpeed",
    "NrdrLatStiction", "NrdrNnlcEnabled",
    "NrdrIncreaseOverrideTolerance", "NrdrDriverOverrideThreshold", "NrdrOverrideThresholdCenterBoost",
    "HondaDriverAssistDuringOverride", "HondaOverrideFadeDownSecs", "HondaOverrideFadeUpSecs", "HondaOverrideTorqueScale",
    "HondaTorqueLowPassFilter", "HondaLpfTauLowSpeed", "HondaLpfTauStandard", "HondaLpfTauHighway",
    "HondaSteerDeltaLimiter", "HondaSteerDeltaUp", "HondaSteerDeltaDown",
    "LagdToggle", "LagdToggleDelay",
  )

  def test_handcrafted_profile_is_first_and_documents_one_shot_behavior(self, schema):
    section = _find_section(schema, "steering", "nrdr")
    assert section is not None
    assert section["items"][0]["key"] == "NrdrHandcraftedLateralTune"

    item = section["items"][0]
    assert item.get("widget") == "toggle"
    assert item["title"] == "Apply Handcrafted Lateral Profile"
    assert "offroad_only" in _flatten_rule_types(item.get("enablement"))
    assert _references_capability_field(item.get("visibility"), "has_handcrafted_lateral_profile")
    description = f"{item.get('description', '')} {item.get('details', '')}".lower()
    assert "one-shot apply command" in description
    assert "turns this switch back off" in description
    assert "every value verifies" in description
    assert "wait a few seconds" in description
    assert "refresh" in description
    assert "manually editable" in description
    assert "never restored or overwritten" in description

  @parameterized.expand(FORMER_HANDCRAFTED_LOCKED_KEYS, names=["key"])
  def test_one_shot_profile_never_locks_formerly_owned_controls(self, schema, key):
    item = _find_item(schema, key)
    assert item is not None
    assert "NrdrHandcraftedLateralTune" not in json.dumps(item.get("enablement") or [])

  @parameterized.expand([
    "NrdrLearnSteerRatio", "NrdrLegacyDualBpSteerRatio", "NrdrLaneChangeEndpointSteerRatio",
    "NrdrSteerRatioCenterClarity", "NrdrSteerRatioOuterClarity",
    "NrdrSteerRatioCenterCivic", "NrdrSteerRatioOuterCivic",
    "NrdrSteerRatioCenterAccord", "NrdrSteerRatioOuterAccord",
    "NrdrSteerRatioCenterCrv5g", "NrdrSteerRatioOuterCrv5g",
    "NrdrSteerRatioCenterInsight", "NrdrSteerRatioOuterInsight",
  ], names=["key"])
  def test_legacy_steer_ratio_controls_are_not_exposed(self, schema, key):
    assert _find_item(schema, key) is None

  def test_atomic_mode_and_manual_pair_are_grouped(self, schema):
    section = _find_section(schema, "steering", "nrdr")
    panel = next(sub_panel for sub_panel in section["sub_panels"] if sub_panel["id"] == "nrdr_steer_ratio_tuning")
    assert panel["label"] == "Steer Ratio Tuning"
    assert [item["key"] for item in panel["items"]] == [
      "NrdrSteerRatioMode", "NrdrSteerRatioManualCenter", "NrdrSteerRatioManualFinal",
    ]

  def test_mode_selector_has_all_four_sources_and_availability_guards(self, schema):
    item = _find_item(schema, "NrdrSteerRatioMode")
    assert item["widget"] == "multiple_button"
    assert [(option["value"], option["label"]) for option in item["options"]] == [
      (0, "Manual"), (1, "Comma Learner"), (2, "nrdr Learner"), (3, "Firmware"),
    ]
    assert "offroad_only" not in json.dumps(item.get("enablement") or [])
    assert "next disengage and re-engage" in item["details"]
    assert "already disengaged, wait up to 10 seconds" in item["details"]
    assert "nrdr_raw_steer_ratio_available" in json.dumps(item["options"][2]["enablement"])
    assert "nrdr_firmware_steer_ratio_available" in json.dumps(item["options"][3]["enablement"])

  @parameterized.expand([
    ("NrdrSteerRatioManualCenter", "Manual Override On-Center Ratio", 15.38),
    ("NrdrSteerRatioManualFinal", "Manual Override Final Ratio", 10.93),
  ], names=["key", "title", "default"])
  def test_manual_controls_are_onroad_editable_in_manual_mode(self, schema, key, title, default):
    item = _find_item(schema, key)
    assert item["title"] == title
    assert (item["min"], item["max"], item["step"]) == (8.0, 25.0, 0.01)
    assert f"Default {default:.2f}" in item["description"]
    rules = json.dumps(item["enablement"])
    assert "offroad_only" not in rules
    assert "NrdrSteerRatioMode" in rules and '"equals": 0' in rules
    assert "nrdr_manual_steer_ratio_available" in rules
    assert "NrdrHandcraftedLateralTune" not in rules


class TestNotEngagedReplacement(OpenpilotTestCase):
  @parameterized.expand([
    "AlphaLongitudinalEnabled",
    "ToyotaEnforceStockLongitudinal",
    "ToyotaStopAndGoHack",
  ], names=["key"])
  def test_offroad_only_replaced_with_not_engaged(self, schema, key):
    """These items should use not_engaged, not offroad_only."""
    item = _find_item(schema, key)
    assert item is not None, f"{key} not found"
    rule_types = _flatten_rule_types(item.get("enablement"))
    assert "offroad_only" not in rule_types, f"{key} still uses offroad_only"
    assert "not_engaged" in rule_types, f"{key} missing not_engaged"
