from openpilot.cereal import log


_NUDGE_TORQUE = 1200


def driver_nudging(car_state, direction) -> bool:
  nudged = car_state.steeringPressed or abs(car_state.steeringTorque) > _NUDGE_TORQUE
  correct_direction = (car_state.steeringTorque > 0 and direction == log.LaneChangeDirection.left) or \
                      (car_state.steeringTorque < 0 and direction == log.LaneChangeDirection.right)
  return nudged and correct_direction


def torque_controller_active(extension) -> bool:
  return extension.model_valid and extension.model_v2.meta.laneChangeState != log.LaneChangeState.off


def torque_from_lateral_accel(torque_function, lateral_accel: float, torque_params, lane_changing: bool) -> float:
  original_factor = torque_params.latAccelFactor
  if lane_changing:
    torque_params.latAccelFactor = original_factor * 2.0
  try:
    return torque_function(lateral_accel, torque_params)
  finally:
    torque_params.latAccelFactor = original_factor
