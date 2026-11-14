"""Compatibility exports for NRDR parameter profiles.

New code should import these objects from :mod:`openpilot.nrdr.params.profiles`.
"""

from openpilot.nrdr.params.profiles import (
  CLARITY_CURRENT_LATERAL_2026_08_28,
  CLARITY_HANDCRAFTED_LATERAL_VALUES_V17,
  CLARITY_ROAD_TESTED_2026_08_21,
  HANDCRAFTED_EXTERNAL_PARAM_KEYS,
  HANDCRAFTED_LATERAL_PROFILES,
  HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS,
  HONDA_TORQUE_MOD_HANDCRAFTED_VALUES,
  HandcraftedLateralProfile,
  HandcraftedLateralUnavailableError,
  ProfileParamStore,
  ProfileValue,
  consume_handcrafted_lateral_request,
  get_handcrafted_lateral_profile,
  handcrafted_lateral_profile_matches,
  handcrafted_lateral_profile_status,
  handcrafted_lateral_profile_supported,
  handcrafted_lateral_success_marker,
)

ParamsLike = ProfileParamStore
ParamValue = ProfileValue

__all__ = (
  "CLARITY_CURRENT_LATERAL_2026_08_28",
  "CLARITY_HANDCRAFTED_LATERAL_VALUES_V17",
  "CLARITY_ROAD_TESTED_2026_08_21",
  "HANDCRAFTED_EXTERNAL_PARAM_KEYS",
  "HANDCRAFTED_LATERAL_PROFILES",
  "HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS",
  "HONDA_TORQUE_MOD_HANDCRAFTED_VALUES",
  "HandcraftedLateralProfile",
  "HandcraftedLateralUnavailableError",
  "ParamValue",
  "ParamsLike",
  "consume_handcrafted_lateral_request",
  "get_handcrafted_lateral_profile",
  "handcrafted_lateral_profile_matches",
  "handcrafted_lateral_profile_status",
  "handcrafted_lateral_profile_supported",
  "handcrafted_lateral_success_marker",
)
