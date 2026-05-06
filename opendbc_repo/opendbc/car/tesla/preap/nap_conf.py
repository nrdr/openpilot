from openpilot.common.params import Params

from opendbc.car.tesla.preap.nap_params import NAPParamKeys

_params = Params()

PEDAL_DI_MIN = -5.0
PEDAL_DI_ZERO = 0.0
PEDAL_DI_PRESSED = 2.0
ACCEL_MAX = 2.5
REGEN_MAX = -1.5
PEDAL_BP = [0.0, 5.0, 12.0, 20.0, 30.0, 40.0]
PEDAL_MAX_VALUES = [50.0, 58.0, 66.0, 74.0, 82.0, 90.0]


def transform_di_to_pedal(val: float, pedal_zero: float, pedal_factor: float) -> float:
  return pedal_zero + (val - PEDAL_DI_ZERO) / (pedal_factor or 1.0)


def transform_pedal_to_di(val: float, pedal_zero: float, pedal_factor: float) -> float:
  return PEDAL_DI_ZERO + (val - pedal_zero) * (pedal_factor or 1.0)


class NAPConf:
  @property
  def adaptive_accel(self) -> bool:
    return _params.get_bool(NAPParamKeys.ADAPTIVE_ACCEL)

  @property
  def follow_distance(self) -> int:
    return max(1, min(7, _params.get_int(NAPParamKeys.FOLLOW_DISTANCE)))

  @property
  def use_pedal(self) -> bool:
    return _params.get_bool(NAPParamKeys.PEDAL_ENABLED)

  @property
  def pedal_calibrated(self) -> bool:
    if not _params.get_bool(NAPParamKeys.PEDAL_CALIB_DONE):
      return False
    return abs(self.pedal_factor) > 1e-6

  @property
  def pedal_can_zero(self) -> bool:
    return _params.get_int(NAPParamKeys.PEDAL_CAN_BUS) == 0

  @property
  def pedal_can_bus(self) -> int:
    return 0 if self.pedal_can_zero else 2

  @property
  def pedal_factor(self) -> float:
    return _params.get_float(NAPParamKeys.PEDAL_CALIB_FACTOR)

  @property
  def pedal_zero(self) -> float:
    return _params.get_float(NAPParamKeys.PEDAL_CALIB_ZERO)

  @property
  def radar_enabled(self) -> bool:
    return _params.get_bool(NAPParamKeys.RADAR_ENABLED)

  @property
  def radar_behind_nosecone(self) -> bool:
    return _params.get_bool(NAPParamKeys.RADAR_BEHIND_NOSECONE)

  @property
  def radar_offset(self) -> float:
    return _params.get_float(NAPParamKeys.RADAR_OFFSET)

  @property
  def double_pull_enabled(self) -> bool:
    return True

  @property
  def double_pull_window_ms(self) -> int:
    return 500

  def get_pedal_profile_values(self) -> list[float]:
    return PEDAL_MAX_VALUES

  def di_to_pedal(self, val: float) -> float:
    return transform_di_to_pedal(val, self.pedal_zero, self.pedal_factor)

  def pedal_to_di(self, val: float) -> float:
    return transform_pedal_to_di(val, self.pedal_zero, self.pedal_factor)


nap_conf = NAPConf()
