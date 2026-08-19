from openpilot.common.params import Params, UnknownKeyName
from opendbc.car import structs
from opendbc.car.common.conversions import Conversions as CV
from opendbc.car.honda.values import CAR


TORQUE_MOD_PID_CARS = frozenset({
  CAR.HONDA_ACCORD,
  CAR.HONDA_CIVIC,
  CAR.HONDA_CIVIC_BOSCH,
  CAR.HONDA_CIVIC_BOSCH_DIESEL,
  CAR.HONDA_CLARITY,
  CAR.HONDA_CRV_5G,
  CAR.HONDA_INSIGHT,
})

_EXTENDED_TORQUE_LIMITS = {
  CAR.HONDA_CLARITY: 3840,
  CAR.HONDA_CIVIC: 3840,
  CAR.HONDA_CIVIC_BOSCH: 4096,
  CAR.HONDA_CIVIC_BOSCH_DIESEL: 4096,
  CAR.HONDA_INSIGHT: 4096,
  CAR.HONDA_NBOX_2G: 4096,
  CAR.HONDA_CRV_5G: 4096,
}

_LOW_SPEED = 25.0 * CV.MPH_TO_MS
_PID_BP = [0.0, _LOW_SPEED - 1e-3, _LOW_SPEED, 50.0 * CV.MPH_TO_MS]
_KP = [0.018, 0.024, 0.048, 0.060]
_KI = [0.006, 0.008, 0.016, 0.020]
_KF = [2.4e-6, 1.8e-6, 3.6e-6, 6.0e-6]
_RADAR_FW = b"36802-TBA-A160"


def _use_civic_bosch_radar(candidate, car_fw, docs: bool) -> bool:
  if candidate != CAR.HONDA_CIVIC_BOSCH:
    return False
  if any(fw.ecu == structs.CarParams.Ecu.fwdRadar and _RADAR_FW in fw.fwVersion for fw in car_fw):
    return True
  if docs:
    return False
  try:
    return Params().get_bool("HondaCivicRadarTryout")
  except UnknownKeyName:
    return False


def _restore_pid_tune(cp: structs.CarParams, candidate) -> None:
  if cp.lateralTuning.which() != "torque":
    return

  cp.lateralTuning.init("pid")
  if candidate in (CAR.HONDA_CRV_6G, CAR.ACURA_MDX_4G):
    cp.lateralTuning.pid.kpBP, cp.lateralTuning.pid.kpV = [[0, 10], [0.05, 0.5]]
    cp.lateralTuning.pid.kiBP, cp.lateralTuning.pid.kiV = [[0, 10], [0.0125, 0.125]]
  elif candidate == CAR.ACURA_RDX_3G_MMR:
    cp.lateralTuning.pid.kpV, cp.lateralTuning.pid.kiV = [[0.2], [0.06]]
  elif candidate in CAR.HONDA_FIT_4G:
    cp.lateralTuning.pid.kpV, cp.lateralTuning.pid.kiV = [[0.2], [0.05]]
  else:
    cp.lateralTuning.pid.kpV, cp.lateralTuning.pid.kiV = [[0.8], [0.24]]


def configure_honda_platform(cp: structs.CarParams, candidate, car_fw, docs: bool) -> None:
  _restore_pid_tune(cp, candidate)
  if candidate == CAR.HONDA_CRV_5G:
    cp.wheelSpeedFactor = 1.0
  elif candidate == CAR.HONDA_PILOT:
    cp.autoResumeSng = True
    cp.minEnableSpeed = -1.0

  if _use_civic_bosch_radar(candidate, car_fw, docs):
    cp.radarUnavailable = False


def configure_modified_eps(cp: structs.CarParams, candidate) -> None:
  if candidate in _EXTENDED_TORQUE_LIMITS:
    torque_limit = _EXTENDED_TORQUE_LIMITS[candidate]
    cp.lateralParams.torqueBP, cp.lateralParams.torqueV = [[0, torque_limit], [0, torque_limit]]
    cp.lateralTuning.pid.kf = 3.6e-6
    cp.lateralTuning.pid.kfBP, cp.lateralTuning.pid.kfV = [_PID_BP, _KF]
    cp.steerAtStandstill = True
    cp.autoResumeSng = True
    cp.minEnableSpeed = -1.0
    cp.minSteerSpeed = -1.0

  if candidate == CAR.HONDA_ACCORD:
    bp = [0.0, 25.0 * CV.MPH_TO_MS, 50.0 * CV.MPH_TO_MS]
    cp.lateralTuning.pid.kfBP, cp.lateralTuning.pid.kfV = [bp, [6.0e-5, 3.0e-5, 3.0e-5]]

  if candidate in TORQUE_MOD_PID_CARS:
    cp.lateralTuning.pid.kpBP, cp.lateralTuning.pid.kpV = [_PID_BP, _KP]
    cp.lateralTuning.pid.kiBP, cp.lateralTuning.pid.kiV = [_PID_BP, _KI]
