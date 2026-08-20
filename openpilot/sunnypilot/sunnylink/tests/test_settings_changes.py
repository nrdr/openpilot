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

import json
import os
import sys
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest


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


SCHEMA_VALIDATOR_PATH = os.path.join(os.path.dirname(DEFINITION_PATH), "settings_ui.schema.json")


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


@pytest.fixture(scope="module")
def schema():
  return generate_schema()


class TestMadsBrandGates:
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


class TestTestManeuversSection:
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


class TestValidator:
  def test_validator_accepts_real_json(self):
    """settings_ui.json validates against settings_ui.schema.json."""
    jsonschema = pytest.importorskip("jsonschema")
    with open(DEFINITION_PATH) as f:
      data = json.load(f)
    with open(SCHEMA_VALIDATOR_PATH) as f:
      validator = json.load(f)
    jsonschema.validate(instance=data, schema=validator)


class TestTorqueOptionGeneration:
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


class TestReleaseBranchGates:
  @pytest.mark.parametrize("key", [
    "EnableGithubRunner",
    "QuickBootToggle",
  ])
  def test_sp_dev_items_gate_on_is_sp_release(self, schema, key):
    """sunnypilot dev items must hide on sunnypilot release branches (is_sp_release gate)."""
    item = _find_item(schema, key)
    assert item is not None, f"{key} not found in schema"
    rules = (item.get("visibility") or []) + (item.get("enablement") or [])
    assert _references_capability_field(rules, "is_sp_release"), f"{key} missing is_sp_release gate"


class TestSpuriousOffroadGatesDropped:
  def test_disengage_on_accelerator_has_no_offroad_only(self, schema):
    item = _find_item(schema, "DisengageOnAccelerator")
    assert item is not None
    assert "offroad_only" not in _flatten_rule_types(item.get("enablement"))

  def test_dynamic_experimental_has_no_offroad_only(self, schema):
    item = _find_item(schema, "DynamicExperimentalControl")
    assert item is not None
    assert "offroad_only" not in _flatten_rule_types(item.get("enablement"))


class TestNrdrLongitudinalOptions:
  PERSONALITY_SCALE_KEYS = (
    "LongPidTuneScaleAggressive",
    "LongPidTuneScaleStandard",
    "LongPidTuneScaleRelaxed",
    "LongPidTuneScaleEcon",
  )

  @pytest.mark.parametrize(("key", "widget"), [
    ("NrdrHondaFullBrakeAuthority", "toggle"),
    ("NrdrRoenAccelerationLimits", "toggle"),
    ("NrdrCruiseOverspeedAllowance", "option"),
  ])
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

  @pytest.mark.parametrize("key", PERSONALITY_SCALE_KEYS)
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

  @pytest.mark.parametrize(
    ("key", "default"),
    tuple(zip(PERSONALITY_SCALE_KEYS, (200, 100, 80, 50), strict=True)),
  )
  def test_personality_pid_scale_describes_default(self, schema, key, default):
    item = _find_item(schema, key)
    assert item is not None
    assert f"Defaults to {default}%" in item.get("details", "")


class TestNrdrSteerRatioMode:
  HANDCRAFTED_LOCKED_KEYS = (
    "NrdrLegacyDualBpSteerRatio",
    "NrdrSteerRatioCenterClarity", "NrdrSteerRatioOuterClarity",
    "NrdrSteerRatioCenterCivic", "NrdrSteerRatioOuterCivic",
    "NrdrSteerRatioCenterAccord", "NrdrSteerRatioOuterAccord",
    "NrdrSteerRatioCenterCrv5g", "NrdrSteerRatioOuterCrv5g",
    "NrdrSteerRatioCenterInsight", "NrdrSteerRatioOuterInsight",
    "NrdrLatStiction",
    "HondaCenterScale",
    "NrdrDriverOverrideThreshold",
    "NrdrOverrideThresholdCenterBoost",
    "HondaOverrideFadeDownSecs",
    "HondaOverrideFadeUpSecs",
    "NrdrNnlcEnabled",
  )

  def test_handcrafted_profile_is_first_and_documents_winning_behavior(self, schema):
    section = _find_section(schema, "steering", "nrdr")
    assert section is not None
    assert section["items"][0]["key"] == "NrdrHandcraftedLateralTune"

    item = section["items"][0]
    assert item.get("widget") == "toggle"
    assert "offroad_only" in _flatten_rule_types(item.get("enablement"))
    description = f"{item.get('description', '')} {item.get('details', '')}".lower()
    assert "off by default" in description
    assert "enable this" in description
    assert "leave this off" in description
    assert "clarity-derived" in description
    assert "firmware-derived" in description
    assert "70 degrees" in description and "90 degrees" in description
    assert "predictive stiction" in description
    assert "nnlc disabled" in description
    assert "pid-only" in description
    assert "vehicle's own steering geometry" in description

  @pytest.mark.parametrize("key", HANDCRAFTED_LOCKED_KEYS)
  def test_winning_profile_controls_are_locked_while_handcrafted_is_on(self, schema, key):
    item = _find_item(schema, key)
    assert item is not None
    assert "NrdrHandcraftedLateralTune" in json.dumps(item.get("enablement") or [])

  def test_legacy_mode_is_explicit_and_fingerprint_scoped(self, schema):
    item = _find_item(schema, "NrdrLegacyDualBpSteerRatio")
    assert item is not None
    assert item.get("widget") == "toggle"
    visibility = json.dumps(item.get("visibility") or [])
    assert "HONDA_CLARITY" in visibility
    assert "HONDA_CIVIC" in visibility
    assert "HONDA_ACCORD" in visibility
    assert "HONDA_CRV_5G" in visibility
    assert "HONDA_INSIGHT" in visibility
    enablement = json.dumps(item.get("enablement") or [])
    assert "NrdrHandcraftedLateralTune" in enablement
    assert "not_engaged" in enablement

  @pytest.mark.parametrize("key", [
    "NrdrSteerRatioCenterClarity", "NrdrSteerRatioOuterClarity",
    "NrdrSteerRatioCenterCivic", "NrdrSteerRatioOuterCivic",
    "NrdrSteerRatioCenterAccord", "NrdrSteerRatioOuterAccord",
    "NrdrSteerRatioCenterCrv5g", "NrdrSteerRatioOuterCrv5g",
    "NrdrSteerRatioCenterInsight", "NrdrSteerRatioOuterInsight",
  ])
  def test_steer_ratio_endpoints_cannot_change_while_engaged(self, schema, key):
    item = _find_item(schema, key)
    assert item is not None
    assert "not_engaged" in json.dumps(item.get("enablement") or [])

  def test_firmware_mode_documents_exact_handoff(self, schema):
    item = _find_item(schema, "NrdrLegacyDualBpSteerRatio")
    details = item.get("details", "")
    assert "exactly through 70 degrees" in details
    assert "70 to 90 degrees" in details
    assert "above 90 degrees" in details


class TestNotEngagedReplacement:
  @pytest.mark.parametrize("key", [
    "AlphaLongitudinalEnabled",
    "ToyotaEnforceStockLongitudinal",
    "ToyotaStopAndGoHack",
  ])
  def test_offroad_only_replaced_with_not_engaged(self, schema, key):
    """These items should use not_engaged, not offroad_only."""
    item = _find_item(schema, key)
    assert item is not None, f"{key} not found"
    rule_types = _flatten_rule_types(item.get("enablement"))
    assert "offroad_only" not in rule_types, f"{key} still uses offroad_only"
    assert "not_engaged" in rule_types, f"{key} missing not_engaged"
