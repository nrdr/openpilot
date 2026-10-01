"""Sunnylink schema adapter for declarative NRDR parameter metadata."""

from __future__ import annotations

import copy

from openpilot.nrdr.params.tuning_policy import LONG_SCALE_KEYS, SUGGESTED_LOCK_KEYS, YAW_FIXED_KEYS

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
  for field, expected_value in expected.items():
    if field in merged and merged[field] != expected_value:
      raise SunnylinkMetadataConflict(
        f"{key}: explicit Sunnylink field {field!r} conflicts with shared NRDR UI metadata"
      )
    merged.setdefault(field, copy.deepcopy(expected_value))
  if key:
    enablement = copy.deepcopy(merged.get("enablement", []))
    if key in SUGGESTED_LOCK_KEYS or key.startswith(("NrdrSteerRatio", "LaneCenter", "NrdrLatRateDamping")):
      for switch in ("NrdrSuggestedSettings", "NrdrHandcraftedLateralTune"):
        enablement.append({"type": "not", "condition": {"type": "param", "key": switch, "equals": True}})
    if key in YAW_FIXED_KEYS or key.startswith(("NrdrSteerRatio", "NrdrLatRateDamping")):
      enablement.append({"type": "not", "condition": {"type": "param", "key": "NrdrLateralController", "equals": 1}})
    if key in LONG_SCALE_KEYS:
      condition = {"type": "not", "condition": {"type": "param", "key": "HondaLiveLearningGas", "equals": True}}
      enablement.append(condition)
      merged["visibility"] = [*copy.deepcopy(merged.get("visibility", [])), condition]
    if enablement:
      merged["enablement"] = enablement
  return merged


__all__ = ("SunnylinkMetadataConflict", "apply_sunnylink_metadata", "sunnylink_fields_for_key")
