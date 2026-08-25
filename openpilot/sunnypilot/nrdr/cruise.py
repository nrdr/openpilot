import math

from opendbc.car.structs import car
from openpilot.common.constants import CV
from openpilot.common.params import Params
from openpilot.sunnypilot.nrdr.hud_submode import consume_button_press


ButtonType = car.CarState.ButtonEvent.Type
_MPH_PER_KPH = 0.6233
_MPH_OFFSET = 0.0995


def _kph_to_cluster_mph(kph: float) -> int:
  return int(round(kph * _MPH_PER_KPH + _MPH_OFFSET))


def _cluster_mph_to_kph(mph: float) -> float:
  return (float(mph) - _MPH_OFFSET) / _MPH_PER_KPH


class NrdrCruise:
  def __init__(self, CP):
    self.is_honda = CP.brand == "honda"
    self.is_metric = True
    self.params = Params()

  def begin_update(self, is_metric: bool) -> None:
    self.is_metric = is_metric

  def allow_speed_change(self) -> bool:
    return consume_button_press(self.params)

  def update_honda_imperial(self, helper, CS, button_type, long_press: bool, v_cruise_max: float) -> float | None:
    if self.is_metric or not self.is_honda:
      return None

    current_mph = _kph_to_cluster_mph(float(helper.v_cruise_kph))
    round_to_nearest, delta_mph = helper.update_v_cruise_delta(long_press, 1.0)
    direction = 1 if button_type == ButtonType.accelCruise else -1

    if round_to_nearest and current_mph % int(delta_mph) != 0:
      nearest = math.ceil if direction > 0 else math.floor
      current_mph = nearest(current_mph / delta_mph) * int(delta_mph)
    else:
      current_mph += int(delta_mph) * direction

    if CS.gasPressed and button_type in (ButtonType.decelCruise, ButtonType.setCruise):
      current_mph = max(current_mph, _kph_to_cluster_mph(CS.vEgo * CV.MS_TO_KPH))

    return min(max(round(_cluster_mph_to_kph(current_mph), 1), helper.v_cruise_min), v_cruise_max)

  def initial_speed(self, speed_kph: float) -> float:
    if not self.is_metric and self.is_honda:
      speed_kph = _cluster_mph_to_kph(_kph_to_cluster_mph(speed_kph))
    return round(speed_kph, 1)
