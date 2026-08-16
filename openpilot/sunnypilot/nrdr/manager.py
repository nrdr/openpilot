from collections.abc import Callable

from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.common.hardware import HARDWARE


BOOL_DEFAULTS = {
  "QuietMode": True,
  "GsmMetered": False,
  "ExperimentalMode": True,
  "RecordFront": True,
  "RecordAudio": True,
  "LaneTurnDesire": True,
  "DynamicExperimentalControl": True,
  "SmartCruiseControlVision": True,
  "CustomAccIncrementsEnabled": True,
  "MadsMainCruiseAllowed": False,
  "HondaTorqueLowPassFilter": True,
  "HondaUnwindLookahead": True,
  "NrdrNnlcEnabled": True,
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
  "LagdToggle": True,
  "EnableCopyparty": True,
}

VALUE_DEFAULTS = {
  "LaneTurnValue": 20.0,
  "AutoLaneChangeTimer": 1,
  "NrdrNnlcActivationSpeed": 30,
  "NrdrNnlcKpGain": 100,
  "NrdrNnlcKfGain": 50,
  "NrdrNnlcKiGain": 10,
  "LongitudinalPersonality": 3,
  "SpeedLimitMode": 3,
  "SpeedLimitOffsetType": 1,
  "SpeedLimitValueOffset": 5,
  "CustomAccShortPressIncrement": 5,
  "CustomAccLongPressIncrement": 1,
  "HondaOverrideFadeDownSecs": 0.1,
  "ChevronInfo": 4,
  "DevUIInfo": 3,
  "OnroadScreenOffBrightness": 1,
  "InteractivityTimeout": 120,
}


def _write(params: Params, key: str, value, setter: Callable, *, force: bool = False) -> None:
  try:
    if force or params.get(key) is None:
      setter(key, value)
  except Exception:
    cloudlog.exception("failed to initialize nrdr param %s", key)


def apply_defaults(params: Params) -> None:
  bool_defaults = dict(BOOL_DEFAULTS)
  if HARDWARE.get_device_type() == "mici":
    bool_defaults.pop("QuietMode")
  for key, value in bool_defaults.items():
    _write(params, key, value, params.put_bool)

  for key, value in VALUE_DEFAULTS.items():
    _write(params, key, value, params.put)

  _write(params, "EnforceTorqueControl", False, params.put_bool, force=True)
  _write(params, "NeuralNetworkLateralControl", False, params.put_bool, force=True)

  try:
    from openpilot.system.version import terms_version, terms_version_sp, training_version, sunnylink_consent_version
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
