"""Sunnylink schema adapter for declarative NRDR parameter metadata."""

from __future__ import annotations

import copy

from openpilot.nrdr.params.tuning_policy import (
  ANGLE_LOCKED_KEYS, ANGLE_TUNING_KEYS, MVL_DESCRIPTION, SUGGESTED_DESCRIPTION, SUGGESTED_LOCK_KEYS, YAW_FIXED_KEYS, LONG_SCALE_KEYS,
)

from openpilot.nrdr.params import NRDR_UI_METADATA_BY_KEY, get_ui_metadata


class SunnylinkMetadataConflict(ValueError):
  pass


def sunnylink_fields_for_key(key: str) -> dict:
  metadata = get_ui_metadata(key)
  numeric = metadata.numeric
  fields = {
    "widget": metadata.widget.value,
    "title": metadata.title,
    "description": metadata.description,
    "min": numeric.minimum,
    "max": numeric.maximum,
    "step": numeric.step,
  }
  if metadata.details is not None:
    fields["details"] = metadata.details
  if numeric.unit is not None:
    fields["unit"] = numeric.unit
  return fields


def apply_sunnylink_metadata(item: dict) -> dict:
  key = item.get("key")
  expected = sunnylink_fields_for_key(key) if key in NRDR_UI_METADATA_BY_KEY else {}

  merged = dict(item)
  if key == "HondaLiveLearningGas":
    merged["description"] = MVL_DESCRIPTION
  if key == "NrdrSuggestedSettings":
    merged["description"] = ""
    merged["details"] = SUGGESTED_DESCRIPTION
  for field, expected_value in expected.items():
    if field in merged and merged[field] != expected_value:
      raise SunnylinkMetadataConflict(
        f"{key}: explicit Sunnylink field {field!r} conflicts with shared NRDR UI metadata"
      )
    merged.setdefault(field, copy.deepcopy(expected_value))
  if key:
    enablement = copy.deepcopy(merged.get("enablement", []))
    if key in ANGLE_LOCKED_KEYS:
      enablement.append({"type": "not", "condition": {"type": "param", "key": "NrdrLateralController", "equals": 3}})
    if key in ANGLE_TUNING_KEYS:
      enablement.extend([{"type": "param", "key": "NrdrLateralController", "equals": 3},
                         {"type": "capability", "field": "nrdr_angle_controller_available", "equals": True}])
    if key == "MaxTimeOffroad":
      # The upstream timer stays on Device; its nrdr shutdown override now
      # lives under Steering. Keep the cross-page exclusion at the UI boundary.
      enablement.append({"type": "param", "key": "DisablePowerDown", "equals": False})
    if key in SUGGESTED_LOCK_KEYS or key.startswith(("NrdrSteerRatio", "LaneCenter", "NrdrLatRateDamping")):
      enablement.append({"type": "any", "conditions": [
        {"type": "offroad_only"},
        {"type": "not", "condition": {"type": "param", "key": "NrdrSuggestedSettings", "equals": True}},
      ]})
      # A pending preset write remains exclusive even while parked.
      enablement.append({"type": "not", "condition": {"type": "param", "key": "NrdrHandcraftedLateralTune", "equals": True}})
    if key in YAW_FIXED_KEYS or key.startswith("NrdrLatRateDamping"):
      for controller in (1, 2):
        enablement.append({"type": "not", "condition": {"type": "param", "key": "NrdrLateralController", "equals": controller}})
    if key in ("LagdToggle", "LagdToggleDelay"):
      enablement.append({"type": "not", "condition": {"type": "all", "conditions": [
        {"type": "any", "conditions": [
          {"type": "param", "key": "NrdrLateralController", "equals": controller} for controller in (1, 2)
        ]},
        {"type": "capability", "field": "nrdr_firmware_prediction_schedule", "equals": True},
      ]}})
    if key in LONG_SCALE_KEYS or key == "NrdrHondaFullBrakeAuthority":
      condition = {"type": "param", "key": "NrdrLongitudinalController", "equals": 0}
      enablement.append(condition)
      if key == "NrdrHondaFullBrakeAuthority":
        merged["visibility"] = [*merged.get("visibility", []), condition]
    if key in ("StaticFeedforwardLong", "NrdrHondaWindBrake"):
      enablement.append({"type": "not", "condition": {"type": "param", "key": "NrdrLongitudinalController", "equals": 3}})
    if enablement:
      merged["enablement"] = enablement
  return merged


__all__ = ("SunnylinkMetadataConflict", "apply_sunnylink_metadata", "sunnylink_fields_for_key")
