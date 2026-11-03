"""Mutually exclusive lane-guidance mode selection.

``LaneGuidanceMode`` is the runtime source of truth.  The legacy
``LaneCentering`` bool is mirrored only so older builds and existing tooling
remain understandable after a downgrade.
"""

from __future__ import annotations

from enum import IntEnum
from typing import Protocol

class LaneGuidanceMode(IntEnum):
  MODEL_ONLY = 0
  NRDR = 1
  BLENDFUL = 2


class LaneGuidanceParamStore(Protocol):
  def get(self, key: str): ...
  def put(self, key: str, value: int, *, block: bool = False) -> None: ...
  def put_bool(self, key: str, value: bool, *, block: bool = False) -> None: ...


def try_parse_lane_guidance_mode(value) -> LaneGuidanceMode | None:
  """Strictly parse a mode, returning ``None`` for malformed input."""
  if isinstance(value, LaneGuidanceMode):
    return value
  if isinstance(value, bytes):
    try:
      value = value.decode()
    except UnicodeDecodeError:
      return None
  if isinstance(value, str):
    if value not in ("0", "1", "2"):
      return None
    value = int(value)
  elif type(value) is not int:
    # bool and float coercion can silently turn malformed storage into an
    # enabled correction path; accept only the typed integer contract.
    return None

  try:
    return LaneGuidanceMode(value)
  except ValueError:
    return None


def parse_lane_guidance_mode(value) -> LaneGuidanceMode:
  """Parse a stored mode and fail closed to the model-only path."""
  return try_parse_lane_guidance_mode(value) or LaneGuidanceMode.MODEL_ONLY


def lane_guidance_mode_from_params(params: LaneGuidanceParamStore) -> LaneGuidanceMode:
  try:
    value = params.get("LaneGuidanceMode")
  except Exception:
    # Unknown registries and transient storage failures must not enable either
    # correction path.
    value = None
  return parse_lane_guidance_mode(value)


def model_frame_lane_guidance_mode(model_mode, model_message_valid: bool,
                                   model_mono_time, current_model_mono_time) -> LaneGuidanceMode:
  """Return the mode explicitly attached to this model frame, or Model Only."""
  parsed_model_mode = try_parse_lane_guidance_mode(model_mode)
  matching_frame = (
    type(model_mono_time) is int
    and type(current_model_mono_time) is int
    and model_mono_time > 0
    and model_mono_time == current_model_mono_time
  )
  if not model_message_valid or not matching_frame or parsed_model_mode is None:
    return LaneGuidanceMode.MODEL_ONLY
  return parsed_model_mode


def model_action_lane_guidance_mode(model_mode, model_message_valid: bool) -> LaneGuidanceMode:
  """Return the mode carried atomically with one model action, or Model Only."""
  parsed_model_mode = try_parse_lane_guidance_mode(model_mode)
  if not model_message_valid or parsed_model_mode is None:
    return LaneGuidanceMode.MODEL_ONLY
  return parsed_model_mode


def nrdr_model_action_allowed(model_mode, model_message_valid: bool) -> bool:
  """Allow NRDR only when the current model action itself selected NRDR."""
  return model_action_lane_guidance_mode(model_mode, model_message_valid) == LaneGuidanceMode.NRDR


def nrdr_lane_centering_allowed(model_mode, model_message_valid: bool,
                                model_mono_time, current_model_mono_time) -> bool:
  """Allow NRDR only when the matching model frame explicitly selected it."""
  return model_frame_lane_guidance_mode(
    model_mode, model_message_valid, model_mono_time, current_model_mono_time,
  ) == LaneGuidanceMode.NRDR


def set_lane_guidance_mode(params: LaneGuidanceParamStore, mode, *, block: bool = True) -> LaneGuidanceMode:
  """Persist one canonical mode, then mirror the downgrade-compatibility bool."""
  parsed = parse_lane_guidance_mode(mode)
  params.put("LaneGuidanceMode", int(parsed), block=block)
  params.put_bool("LaneCentering", parsed == LaneGuidanceMode.NRDR, block=block)
  return parsed
