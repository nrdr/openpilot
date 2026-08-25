"""Compatibility exports for NRDR parameter profiles.

New code should import these objects from :mod:`openpilot.nrdr.params.profiles`.
"""

from openpilot.nrdr.params.profiles import (
  CLARITY_ROAD_TESTED_2026_08_21,
  HANDCRAFTED_EXTERNAL_PARAM_KEYS,
  HANDCRAFTED_LATERAL_PROFILES,
  HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS,
  HONDA_TORQUE_MOD_HANDCRAFTED_VALUES,
  HandcraftedLateralProfile,
  ProfileParamStore,
  ProfileValue,
  apply_handcrafted_lateral_profile,
  get_handcrafted_lateral_profile,
  get_steer_ratio_endpoint_profile,
  is_handcrafted_lateral_enabled,
  restore_handcrafted_lateral_profile,
)

ParamsLike = ProfileParamStore
ParamValue = ProfileValue

__all__ = (
  "CLARITY_ROAD_TESTED_2026_08_21",
  "HANDCRAFTED_EXTERNAL_PARAM_KEYS",
  "HANDCRAFTED_LATERAL_PROFILES",
  "HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS",
  "HONDA_TORQUE_MOD_HANDCRAFTED_VALUES",
  "HandcraftedLateralProfile",
  "ParamValue",
  "ParamsLike",
  "apply_handcrafted_lateral_profile",
  "get_handcrafted_lateral_profile",
  "get_steer_ratio_endpoint_profile",
  "is_handcrafted_lateral_enabled",
  "restore_handcrafted_lateral_profile",
)
