"""Sunnylink schema adapter for declarative NRDR parameter metadata."""

from __future__ import annotations

import copy

from openpilot.nrdr.params import NRDR_UI_METADATA_BY_KEY, UiEditPolicy, get_ui_metadata


class SunnylinkMetadataConflict(ValueError):
  pass


_EDIT_POLICY_RULES = {
  UiEditPolicy.HANDCRAFTED_LATERAL_UNLOCKED: {"$ref": "#/macros/handcrafted_lateral_unlocked"},
}


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
  if metadata.edit_policies:
    fields["enablement"] = [copy.deepcopy(_EDIT_POLICY_RULES[policy]) for policy in metadata.edit_policies]
  return fields


def apply_sunnylink_metadata(item: dict) -> dict:
  key = item.get("key")
  if key not in NRDR_UI_METADATA_BY_KEY:
    return dict(item)
  expected = sunnylink_fields_for_key(key)

  merged = dict(item)
  for field, expected_value in expected.items():
    if field in merged and merged[field] != expected_value:
      raise SunnylinkMetadataConflict(
        f"{key}: explicit Sunnylink field {field!r} conflicts with shared NRDR UI metadata"
      )
    merged.setdefault(field, copy.deepcopy(expected_value))
  return merged


__all__ = ("SunnylinkMetadataConflict", "apply_sunnylink_metadata", "sunnylink_fields_for_key")
