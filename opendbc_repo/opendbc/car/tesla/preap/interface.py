import numpy as np

from opendbc.car import get_safety_config, structs
from opendbc.car.tesla.preap.constants import ACCEL_PREAP_BP, ACCEL_PREAP_PROFILES, PEDAL_LONG_K_BP, PEDAL_LONG_KI_V, PEDAL_LONG_KP_V
from opendbc.car.tesla.preap.nap_conf import nap_conf

PREAP_FLAG_ENABLE_PEDAL = 1
PREAP_FLAG_RADAR_EMULATION = 2
PREAP_FLAG_RADAR_BEHIND_NOSECONE = 4


def get_preap_accel_limits(current_speed: float) -> tuple[float, float]:
  try:
    from openpilot.common.params import Params
    personality = Params().get_int("LongitudinalPersonality")
  except Exception:
    personality = 1
  profile = ACCEL_PREAP_PROFILES.get(personality, ACCEL_PREAP_PROFILES[1])
  return -1.5, float(np.interp(current_speed, ACCEL_PREAP_BP, profile))


def get_preap_params(ret: structs.CarParams) -> structs.CarParams:
  safety_flags = 0
  if nap_conf.use_pedal:
    safety_flags |= PREAP_FLAG_ENABLE_PEDAL
  if nap_conf.radar_enabled:
    safety_flags |= PREAP_FLAG_RADAR_EMULATION
  if nap_conf.radar_behind_nosecone:
    safety_flags |= PREAP_FLAG_RADAR_BEHIND_NOSECONE

  use_pedal = nap_conf.use_pedal and nap_conf.pedal_calibrated
  ret.safetyConfigs = [get_safety_config(structs.CarParams.SafetyModel.teslaPreap, safety_flags)]
  ret.radarUnavailable = not nap_conf.radar_enabled
  ret.steerControlType = structs.CarParams.SteerControlType.angle
  ret.openpilotLongitudinalControl = use_pedal
  ret.pcmCruise = not use_pedal
  ret.alphaLongitudinalAvailable = False
  ret.steerLimitTimer = 0.4
  ret.steerActuatorDelay = 0.1
  ret.steerAtStandstill = True
  ret.vEgoStopping = 0.1
  ret.vEgoStarting = 0.1
  ret.stoppingDecelRate = 1.0

  if use_pedal:
    ret.longitudinalTuning.kpBP = PEDAL_LONG_K_BP
    ret.longitudinalTuning.kpV = PEDAL_LONG_KP_V
    ret.longitudinalTuning.kiBP = PEDAL_LONG_K_BP
    ret.longitudinalTuning.kiV = PEDAL_LONG_KI_V
    try:
      ret.longitudinalTuning.kf = 1.0
    except AttributeError:
      pass
    ret.longitudinalActuatorDelay = 0.4

  return ret
