from opendbc.car import structs
from opendbc.car.common.conversions import Conversions as CV
from opendbc.car.honda.values import CAR
from opendbc.sunnypilot.car.honda.values_ext import RDX_TJB_A220_PTM


TORQUE_MOD_PID_CARS = frozenset({
  CAR.HONDA_ACCORD,
  CAR.HONDA_CIVIC,
  CAR.HONDA_CIVIC_BOSCH,
  CAR.HONDA_CIVIC_BOSCH_DIESEL,
  CAR.HONDA_CLARITY,
  CAR.HONDA_CRV_5G,
  CAR.HONDA_INSIGHT,
})

# 0xE4 per unit of output: the EPS's own command clamp. The Clarity, Civic (Nidec and Bosch) and Insight EPS firmware
# clamps its command input at key 1663 = E4 3840, stock firmware and PTM builds alike (the PTM builds keep the stock
# E4 decode; read from the stock TRW, TBA-A030, TEG-A010, TBA-C020, TBA-C120, TGG-A120 and TXM-A040 images), so above
# 3840 the request did nothing. The CR-V's (TLA) clamps at 1774 = E4 4096.
_EXTENDED_TORQUE_LIMITS = {
  CAR.HONDA_CLARITY: 3840,
  CAR.HONDA_CIVIC: 3840,
  CAR.HONDA_CIVIC_BOSCH: 3840,
  CAR.HONDA_CIVIC_BOSCH_DIESEL: 4096,
  CAR.HONDA_INSIGHT: 3840,
  CAR.HONDA_NBOX_2G: 4096,
  CAR.HONDA_CRV_5G: 4096,
}

_NBOX_KF_BP = [0.0, 25.0 * CV.MPH_TO_MS - 1e-3, 25.0 * CV.MPH_TO_MS, 50.0 * CV.MPH_TO_MS]
_NBOX_KF = [0.0000024, 0.0000018, 0.0000036, 0.000006]


def _restore_pid_tune(cp: structs.CarParams, candidate) -> None:
  if cp.lateralTuning.which() != "torque":
    return

  cp.lateralTuning.init("pid")
  cp.lateralTuning.pid.kpBP = [0.0]
  cp.lateralTuning.pid.kiBP = [0.0]
  if candidate in (CAR.HONDA_CRV_6G, CAR.ACURA_MDX_4G):
    cp.lateralTuning.pid.kpBP, cp.lateralTuning.pid.kpV = [[0, 10], [0.05, 0.5]]
    cp.lateralTuning.pid.kiBP, cp.lateralTuning.pid.kiV = [[0, 10], [0.0125, 0.125]]
  elif candidate == CAR.ACURA_RDX_3G_MMR:
    cp.lateralTuning.pid.kpV, cp.lateralTuning.pid.kiV = [[0.2], [0.06]]
  elif candidate == CAR.HONDA_FIT_4G:
    cp.lateralTuning.pid.kpV, cp.lateralTuning.pid.kiV = [[0.2], [0.05]]
  else:
    cp.lateralTuning.pid.kpV, cp.lateralTuning.pid.kiV = [[0.8], [0.24]]


def is_rdx_tjb_a220_ptm(candidate, car_fw) -> bool:
  if candidate not in (CAR.ACURA_RDX_3G, CAR.ACURA_RDX_3G_MMR):
    return False
  # Ignore logging-only serial queries. Missing or conflicting image replies must not select this scale.
  images = {(fw.address, fw.subAddress, fw.fwVersion) for fw in car_fw if fw.ecu == "eps" and not fw.logging}
  return images == {(0x18DA30F1, 0, RDX_TJB_A220_PTM)}


def configure_honda_platform(cp: structs.CarParams, candidate, car_fw, docs: bool) -> None:
  _restore_pid_tune(cp, candidate)
  if candidate == CAR.HONDA_CRV_5G:
    cp.wheelSpeedFactor = 1.0
  elif candidate == CAR.HONDA_PILOT:
    cp.autoResumeSng = True
    cp.minEnableSpeed = -1.0

def configure_modified_eps(cp: structs.CarParams, candidate) -> None:
  if candidate in _EXTENDED_TORQUE_LIMITS:
    torque_limit = _EXTENDED_TORQUE_LIMITS[candidate]
    cp.lateralParams.torqueBP, cp.lateralParams.torqueV = [[0, torque_limit], [0, torque_limit]]
    cp.steerAtStandstill = True
    cp.autoResumeSng = True
    cp.minEnableSpeed = -1.0
    cp.minSteerSpeed = -1.0

  if candidate == CAR.HONDA_NBOX_2G:
    cp.lateralTuning.pid.kf = 0.0000036
    cp.lateralTuning.pid.kfBP, cp.lateralTuning.pid.kfV = [_NBOX_KF_BP, _NBOX_KF]

  if candidate in TORQUE_MOD_PID_CARS:
    cp.lateralTuning.pid.kpBP, cp.lateralTuning.pid.kpV = [[0.0], [0.03]]
    cp.lateralTuning.pid.kiBP, cp.lateralTuning.pid.kiV = [[0.0], [0.01]]
    cp.lateralTuning.pid.kf = 0.000012
    cp.lateralTuning.pid.kfBP = []
    cp.lateralTuning.pid.kfV = []
