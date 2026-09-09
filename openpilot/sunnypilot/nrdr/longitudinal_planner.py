import numpy as np

from opendbc.car.honda.values import HondaFlags
from opendbc.car.interfaces import ACCEL_MAX
from openpilot.cereal import log
from openpilot.common.constants import CV
from openpilot.selfdrive.car.cruise import V_CRUISE_MAX
from openpilot.selfdrive.controls.lib.drive_helpers import get_accel_from_plan
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.sunnypilot.nrdr.live_params import get_live_params
from openpilot.sunnypilot.nrdr.params import read_bool, read_float


LAUNCH_DISARM_SPEED = 2.0
LAUNCH_COMMIT_TIME = 3.5
LAUNCH_MOVING_SPEED = 1.2
LAUNCH_MAX_ACCEL = 3.5
CRUISE_ACCEL_VALUES = (2.0, 1.6, 0.8, 0.6)
CRUISE_OVERSPEED_BRAKING_BUFFER = 0.1
CRUISE_OVERSPEED_DRIVING_BUFFER = 0.5
ROEN_ACCEL_BP = (0.0, 5.0, 20.0)
ROEN_PLANNER_ACCEL = (4.0, 4.0, 2.0)
ROEN_TURN_ACCEL_THRESHOLD = 1.3
# Positive-only acceleration ceilings from Sunny's C3 implementation
# (e8df8fad). C3 used a separate selector; NRDR's deliberately monotonic
# mapping keeps distance bar 1 on the stock platform ceiling and assigns bars
# 2 through 4 to C3 Sport, Normal, and Eco respectively.
C3_ACCEL_PROFILE_BP = (0.0, 1.0, 6.0, 8.0, 11.0, 15.0, 20.0, 25.0, 30.0, 55.0)
C3_ACCEL_PROFILE_NORMAL = (2.5, 2.5, 2.5, 1.70, 1.05, 0.81, 0.625, 0.42, 0.348, 0.12)
C3_ACCEL_PROFILE_ECO = (2.0, 2.0, 2.0, 1.4, 0.80, 0.68, 0.53, 0.32, 0.20, 0.085)
C3_ACCEL_PROFILE_SPORT = (3.5, 3.5, 2.8, 2.4, 1.4, 1.0, 0.89, 0.75, 0.50, 0.2)
C3_ACCEL_PROFILES_BY_PERSONALITY = (
  None,
  C3_ACCEL_PROFILE_SPORT,
  C3_ACCEL_PROFILE_NORMAL,
  C3_ACCEL_PROFILE_ECO,
)


def _personality_index(personality) -> int:
  raw = getattr(personality, "raw", personality)
  if isinstance(raw, bool):
    return int(log.LongitudinalPersonality.standard)
  try:
    index = int(raw)
    if float(raw) != index:
      raise ValueError
  except (OverflowError, TypeError, ValueError):
    return int(log.LongitudinalPersonality.standard)
  return index if 0 <= index < len(C3_ACCEL_PROFILES_BY_PERSONALITY) else int(log.LongitudinalPersonality.standard)


def c3_personality_accel_max(v_ego: float, personality) -> float | None:
  """Return the C3 positive ceiling mapped to NRDR's four distance bars."""
  profile = C3_ACCEL_PROFILES_BY_PERSONALITY[_personality_index(personality)]
  if profile is None:
    return None
  if isinstance(v_ego, bool):
    return None
  try:
    speed = float(v_ego)
  except (OverflowError, TypeError, ValueError):
    return None
  if not np.isfinite(speed):
    return None
  return float(np.interp(max(0.0, speed), C3_ACCEL_PROFILE_BP, profile))


def apply_cruise_overspeed_allowance(target: float, selected_target: float, set_speed: float,
                                     v_ego: float, accel: float, allowance: float) -> float:
  if allowance <= 0.0 or selected_target < set_speed or v_ego <= target:
    return target
  delta = v_ego - target
  buffer = min(CRUISE_OVERSPEED_BRAKING_BUFFER if accel < 0.0 else CRUISE_OVERSPEED_DRIVING_BUFFER, delta)
  return max(target, min(v_ego - buffer, set_speed + allowance))


class NrdrLongitudinalPlanner:
  def __init__(self, CP, CP_SP, tune):
    self.CP = CP
    self.CP_SP = CP_SP
    self.tune = tune
    self.params = get_live_params("plannerd")
    self.settings_generation = -1
    self.v_ego_stopping = CP.deprecated.vEgoStopping
    self.cruise_scale = 1.0
    self.cruise_overspeed_allowance = 0.0
    self.roen_acceleration_limits = True
    self.launch_armed = False
    self._refresh_settings()

  def refresh(self) -> None:
    if self.settings_generation != self.params.generation:
      self._refresh_settings()

  def _refresh_settings(self) -> None:
    snapshot = self.params.snapshot
    self.v_ego_stopping = read_float(snapshot, "HondaVEgoStopping", self.CP.deprecated.vEgoStopping, 0.0, 5.0)
    self.cruise_scale = read_float(snapshot, "NrdrCruiseMismatchCorrection", 100.0, 95.0, 105.0) / 100.0
    self.cruise_overspeed_allowance = read_float(snapshot, "NrdrCruiseOverspeedAllowance", 0.0, 0.0, 10.0) * CV.MPH_TO_MS
    self.roen_acceleration_limits = read_bool(snapshot, "NrdrRoenAccelerationLimits", True)
    self.settings_generation = snapshot.generation

  @property
  def roen_enabled(self) -> bool:
    return bool(self.roen_acceleration_limits and self.CP.brand == "honda" and
                self.CP.flags & HondaFlags.NIDEC and self.CP_SP.enableGasInterceptor)

  def max_accel(self, v_ego: float) -> float:
    if self.roen_enabled:
      return float(np.interp(v_ego, ROEN_ACCEL_BP, ROEN_PLANNER_ACCEL))
    values = np.minimum(np.asarray(CRUISE_ACCEL_VALUES) * self.tune.a_cruise_max_scale, ACCEL_MAX)
    return float(np.interp(v_ego, (0.0, 10.0, 25.0, 40.0), values))

  def personality_accel_ceiling(self, v_ego: float, personality) -> float | None:
    """Return the C3 positive cruise/ACC ceiling without changing platform, coast, or braking limits."""
    return c3_personality_accel_max(v_ego, personality)

  def turn_accel_threshold(self) -> float:
    return ROEN_TURN_ACCEL_THRESHOLD if self.roen_enabled else 0.0

  def cruise_target(self, target: float, set_speed: float, v_ego: float, accel: float) -> float:
    if target <= 0.0:
      return target
    scaled_target = min(target * self.cruise_scale, V_CRUISE_MAX * CV.KPH_TO_MS)
    return apply_cruise_overspeed_allowance(
      scaled_target, target, set_speed, v_ego, accel, self.cruise_overspeed_allowance,
    )

  def launch_accel(self, sm, mpc_time_indices, action_time: float, v_ego: float,
                   should_stop: bool, output_accel: float, e2e_active: bool) -> float:
    if sm["carState"].standstill:
      self.launch_armed = True
    elif v_ego > LAUNCH_DISARM_SPEED:
      self.launch_armed = False

    model = sm["modelV2"]
    if (len(model.velocity.x) != ModelConstants.IDX_N or
        len(model.acceleration.x) != ModelConstants.IDX_N):
      return output_accel

    model_v = np.interp(mpc_time_indices, ModelConstants.T_IDXS, model.velocity.x)
    if (not self.launch_armed or not e2e_active or should_stop or
        np.interp(LAUNCH_COMMIT_TIME, mpc_time_indices, model_v) <= LAUNCH_DISARM_SPEED):
      return output_accel

    model_a = np.interp(mpc_time_indices, ModelConstants.T_IDXS, model.acceleration.x)
    time_cut = min(float(mpc_time_indices[np.argmax(model_v > LAUNCH_MOVING_SPEED)]), LAUNCH_COMMIT_TIME)
    shifted_time = mpc_time_indices + time_cut
    shifted_v = np.interp(shifted_time, mpc_time_indices, model_v)
    shifted_a = np.interp(shifted_time, mpc_time_indices, model_a)
    launch_accel = get_accel_from_plan(
      shifted_v,
      shifted_a,
      mpc_time_indices,
      action_t=action_time,
      v_ego_stopping=self.v_ego_stopping,
    )
    maximum = np.interp(v_ego, [LAUNCH_MOVING_SPEED, LAUNCH_DISARM_SPEED], [LAUNCH_MAX_ACCEL, 0.0])
    return max(output_accel, min(launch_accel, maximum))
