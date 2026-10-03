from collections.abc import Callable

from openpilot.nrdr.params import NrdrParamKey


def model_lateral_delay_schedule(params, CP) -> Callable[[float], float] | None:
  """Read once at modeld start: the speed schedule Yaw Control is tuned with, or None to keep lagd/SteerDelay.

  Mirrors controlsd_ext's controller selection, so the model is only told this schedule when controlsd
  runs the controller it was measured on. Other cars return before waiting on CarParamsSP.
  """
  if str(CP.brand) != "honda" or str(CP.carFingerprint) != "HONDA_CLARITY" or CP.lateralTuning.which() != "pid":
    return None
  if params.get(NrdrParamKey.NRDR_LATERAL_CONTROLLER) != 1:
    return None

  from openpilot.nrdr.features.lateral.yaw_control_timing import clarity_lateral_delay, delay_schedule_enabled
  if not delay_schedule_enabled(params):
    return None

  import openpilot.cereal.messaging as messaging
  from openpilot.cereal import custom
  from openpilot.nrdr.features.lateral.controller_selection import yaw_controller_available
  CP_SP = messaging.log_from_bytes(params.get("CarParamsSP", block=True), custom.CarParamsSP)
  return clarity_lateral_delay if yaw_controller_available(CP, CP_SP) else None
