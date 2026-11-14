"""nrdr startup parameter defaults and forced startup policy."""

from collections.abc import Callable

from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.nrdr.params.profiles import (
  COMMON_HANDCRAFTED_VALUES, HONDA_FILTER_HANDCRAFTED_VALUES, HONDA_PID_HANDCRAFTED_VALUES, seed_firmware_defaults,
)


STEER_RATIO_MANUAL_DEFAULTS = (15.38, 10.93)

# Legacy endpoint Params remain registered only so this one-time migration can
# preserve an existing owner's tune. They have no runtime consumers afterward.
_LEGACY_STEER_RATIO_ENDPOINTS = {
  "HONDA_CLARITY": ("NrdrSteerRatioCenterClarity", "NrdrSteerRatioOuterClarity", 18.50, 12.72),
  "HONDA_CIVIC": ("NrdrSteerRatioCenterCivic", "NrdrSteerRatioOuterCivic", 17.24, 10.93),
  "HONDA_CIVIC_BOSCH": ("NrdrSteerRatioCenterCivic", "NrdrSteerRatioOuterCivic", 17.24, 10.93),
  "HONDA_CIVIC_BOSCH_DIESEL": ("NrdrSteerRatioCenterCivic", "NrdrSteerRatioOuterCivic", 17.24, 10.93),
  "HONDA_ACCORD": ("NrdrSteerRatioCenterAccord", "NrdrSteerRatioOuterAccord", 18.31, 11.82),
  "HONDA_CRV_5G": ("NrdrSteerRatioCenterCrv5g", "NrdrSteerRatioOuterCrv5g", 17.94, 12.30),
  "HONDA_CRV_HYBRID": ("NrdrSteerRatioCenterCrv5g", "NrdrSteerRatioOuterCrv5g", 17.94, 12.30),
  "HONDA_INSIGHT": ("NrdrSteerRatioCenterInsight", "NrdrSteerRatioOuterInsight", 16.82, 12.58),
}


BOOL_DEFAULTS = {
  "QuietMode": True,
  "GsmMetered": False,
  "ExperimentalMode": False,
  "RecordFront": True,
  "RecordAudio": True,
  "LaneTurnDesire": True,
  "DynamicExperimentalControl": False,
  "SmartCruiseControlVision": True,
  "CustomAccIncrementsEnabled": True,
  "MadsMainCruiseAllowed": False,
  "HondaTorqueLowPassFilter": True,
  "RocketFuel": True,
  "BlindSpot": True,
  "TorqueBar": True,
  "RainbowMode": False,
  "StandstillTimer": True,
  "RoadNameToggle": True,
  "GreenLightAlert": True,
  "LeadDepartAlert": True,
  "TrueVEgoUI": False,
  "HideVEgoUI": False,
  "ShowTurnSignals": True,
  "SshEnabled": True,
  "ShowAdvancedControls": True,
  "LagdToggle": False,
  "EnableCopyparty": True,
}

VALUE_DEFAULTS = {
  "LaneTurnValue": 20.0,
  "AutoLaneChangeTimer": 1,
  "LongitudinalPersonality": 3,
  "SpeedLimitMode": 3,
  "SpeedLimitOffsetType": 1,
  "SpeedLimitValueOffset": 5,
  "CustomAccShortPressIncrement": 5,
  "CustomAccLongPressIncrement": 1,
  "NrdrDriverOverrideThreshold": 1500,
  "NrdrOverrideThresholdCenterBoost": 1000,
  "HondaOverrideFadeDownSecs": 0.50,
  "HondaOverrideFadeUpSecs": 2.0,
  "ChevronInfo": 4,
  "DevUIInfo": 3,
  "OnroadScreenOffBrightness": 1,
  "InteractivityTimeout": 120,
}

# Same baseline as Apply Suggested Settings, but only for keys that have never
# been saved. PTM Controller/SR wait for live CP admission; these defaults
# do not apply the preset lock or copy learned/manual geometry.
for _key, _value in COMMON_HANDCRAFTED_VALUES + HONDA_FILTER_HANDCRAFTED_VALUES + HONDA_PID_HANDCRAFTED_VALUES:
  (BOOL_DEFAULTS if type(_value) is bool else VALUE_DEFAULTS)[_key] = _value


def _write(params: Params, key: str, value, setter: Callable, *, force: bool = False, block: bool = False) -> bool:
  try:
    if force or params.get(key) is None:
      if block:
        setter(key, value, block=True)
      else:
        setter(key, value)
    return True
  except Exception:
    cloudlog.exception("failed to initialize nrdr param %s", key)
    return False


def _stored_fingerprint(params: Params) -> str:
  try:
    bundle = params.get("CarPlatformBundle")
    if isinstance(bundle, dict) and bundle.get("platform"):
      return str(bundle["platform"])
  except Exception:
    pass

  for key in ("CarParamsPersistent", "CarParams"):
    try:
      cp_bytes = params.get(key)
      if not cp_bytes:
        continue
      from opendbc.car.structs import car
      with car.CarParams.from_bytes(cp_bytes) as CP:
        if CP.carFingerprint:
          return str(CP.carFingerprint)
    except Exception:
      continue
  return ""


def _legacy_bool(params: Params, key: str) -> bool:
  try:
    value = params.get(key)
  except Exception:
    return False
  if isinstance(value, bytes):
    return value.strip().lower() not in (b"", b"0", b"false")
  if isinstance(value, str):
    return value.strip().lower() not in ("", "0", "false")
  return bool(value)


def _migrate_steer_ratio_settings(params: Params) -> None:
  """Create the atomic mode/manual contract once, preserving an attached car's old endpoints."""
  try:
    mode_present = params.get("NrdrSteerRatioMode") is not None
    center_present = params.get("NrdrSteerRatioManualCenter") is not None
    final_present = params.get("NrdrSteerRatioManualFinal") is not None
    if mode_present and center_present and final_present:
      return
  except Exception:
    cloudlog.exception("failed to inspect steer-ratio migration state")
    return

  center, final = STEER_RATIO_MANUAL_DEFAULTS
  if legacy := _LEGACY_STEER_RATIO_ENDPOINTS.get(_stored_fingerprint(params)):
    center_key, final_key, _center_default, _final_default = legacy
    try:
      legacy_center = params.get(center_key)
    except Exception:
      legacy_center = None
    try:
      legacy_final = params.get(final_key)
    except Exception:
      legacy_final = None
    center = center if legacy_center is None else legacy_center
    final = final if legacy_final is None else legacy_final

  # Blocking writes make mode-last a durable ordering guarantee. Every key is
  # independently guarded, so an interrupted migration fills only what is
  # still missing on the next boot and never overwrites new-format values.
  center_ok = center_present or _write(params, "NrdrSteerRatioManualCenter", center, params.put, block=True)
  final_ok = final_present or _write(params, "NrdrSteerRatioManualFinal", final, params.put, block=True)
  if not mode_present and center_ok and final_ok:
    _write(params, "NrdrSteerRatioMode", 1 if _legacy_bool(params, "NrdrLearnSteerRatio") else 0,
           params.put, block=True)


def apply_defaults(params: Params) -> None:
  try:
    seed_firmware_defaults(params)
  except Exception:
    cloudlog.exception("failed to prepare admitted firmware defaults")
  _migrate_steer_ratio_settings(params)

  for key, value in BOOL_DEFAULTS.items():
    # Persist QuietMode before manager's generic defaults can seed it as false.
    _write(params, key, value, params.put_bool, block=True)

  for key, value in VALUE_DEFAULTS.items():
    _write(params, key, value, params.put, block=True)

  # Request a compatible PopV2 artifact only on first setup. A saved false is
  # an opt-out, not a missing preference, and model choices always win.
  if params.get("NrdrFirstRunSetupDone") is None and all(params.get(key) is None for key in (
    "NrdrAutoSelectModel", "ModelManager_ActiveBundle", "ModelManager_ActiveBundleChestnut", "ModelManager_DownloadRef",
  )):
    _write(params, "NrdrAutoSelectModel", True, params.put_bool, block=True)

  _write(params, "EnforceTorqueControl", False, params.put_bool, force=True)
  _write(params, "NeuralNetworkLateralControl", False, params.put_bool, force=True)
  from openpilot.nrdr.params.tuning_policy import reset_learning_scales
  reset_learning_scales(params)

  try:
    from openpilot.common.version import terms_version, terms_version_sp, training_version, sunnylink_consent_version
    required = {
      "HasAcceptedTerms": terms_version,
      "HasAcceptedTermsSP": terms_version_sp,
      "CompletedTrainingVersion": training_version,
      "CompletedSunnylinkConsentVersion": sunnylink_consent_version,
    }
    for key, value in required.items():
      _write(params, key, value, params.put, force=True)
    _write(params, "SunnylinkEnabled", True, params.put_bool, force=True)
  except Exception:
    cloudlog.exception("failed to initialize nrdr onboarding params")
