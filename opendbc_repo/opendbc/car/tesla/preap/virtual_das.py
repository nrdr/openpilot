import math

from numpy import clip, interp

from opendbc.car.common.filter_simple import FirstOrderFilter, HighPassFilter
from opendbc.car.common.pid import PIDController
from opendbc.car.tesla.pedal.controller import PEDAL_RAMP_RATE_DOWN, PEDAL_RAMP_RATE_UP, get_zero_torque
from opendbc.car.tesla.preap.constants import (
  VDAS_AEGO_FILTER_RC,
  VDAS_FUTURE_T_BP,
  VDAS_FUTURE_T_V,
  VDAS_INNER_K_BP,
  VDAS_INNER_KI_V,
  VDAS_INNER_KP_V,
)
from opendbc.car.tesla.preap.ff_table_default import ACCEL_BP, DEFAULT_TABLE, SPEED_BP
from opendbc.car.tesla.preap.nap_conf import ACCEL_MAX, PEDAL_BP, PEDAL_DI_MIN, PEDAL_MAX_VALUES, REGEN_MAX

PID_ERROR_DEADBAND = 0.1
GRAVITY = 9.81
PITCH_LP_RC = 0.5
PITCH_HP_RC1 = 0.1
PITCH_HP_RC2 = 1.0
MAX_PITCH_COMPENSATION = 1.5


class GradeEstimator:
  def __init__(self, dt: float = 0.02):
    self.pitch_lp = FirstOrderFilter(0.0, PITCH_LP_RC, dt)
    self.pitch_hp = HighPassFilter(0.0, PITCH_HP_RC1, PITCH_HP_RC2, dt)

  def update(self, orientation_ned: list[float]) -> tuple[float, float]:
    if len(orientation_ned) < 2:
      return 0.0, 0.0
    pitch = orientation_ned[1]
    self.pitch_lp.update(pitch)
    self.pitch_hp.update(pitch)
    grade_accel = math.sin(self.pitch_lp.x) * GRAVITY
    pitch_comp = float(clip(math.sin(self.pitch_hp.x) * GRAVITY, -MAX_PITCH_COMPENSATION, MAX_PITCH_COMPENSATION))
    return grade_accel, pitch_comp

  def reset(self) -> None:
    self.pitch_lp.x = 0.0
    self.pitch_hp.x = 0.0
    self.pitch_hp._f1.x = 0.0
    self.pitch_hp._f2.x = 0.0


class JerkLimiter:
  def __init__(self, j_max: float = 2.5, dt: float = 0.02):
    self.j_max = j_max
    self.dt = dt
    self.a_limited = 0.0

  def update(self, a_cmd: float) -> float:
    da_max = self.j_max * self.dt
    self.a_limited += float(clip(a_cmd - self.a_limited, -da_max, da_max))
    return self.a_limited

  def reset(self, a_init: float = 0.0) -> None:
    self.a_limited = a_init


class FeedforwardModel:
  def __init__(self):
    self.speed_bp = list(SPEED_BP)
    self.accel_bp = list(ACCEL_BP)
    self.table = [list(row) for row in DEFAULT_TABLE]

  def get(self, a_cmd: float, v_ego: float, zero_torque_di: float) -> float:
    si = float(interp(v_ego, self.speed_bp, range(len(self.speed_bp))))
    si_lo = int(si)
    si_hi = min(si_lo + 1, len(self.speed_bp) - 1)
    sf = si - si_lo
    di_lo = float(interp(a_cmd, self.accel_bp, self.table[si_lo]))
    di_hi = float(interp(a_cmd, self.accel_bp, self.table[si_hi]))
    base_di = di_lo + sf * (di_hi - di_lo)

    if a_cmd < 0:
      blend = float(clip((a_cmd - REGEN_MAX) / (0.0 - REGEN_MAX), 0.0, 1.0))
    else:
      blend = float(1.0 - a_cmd / ACCEL_MAX)
    return base_di + zero_torque_di * blend


class VirtualDAS:
  def __init__(self, dt: float = 0.02):
    self.dt = dt
    self.jerk_limiter = JerkLimiter(dt=dt)
    self.ff_model = FeedforwardModel()
    self.grade_estimator = GradeEstimator(dt=dt)
    self.inner_pid = PIDController(
      k_p=(VDAS_INNER_K_BP, VDAS_INNER_KP_V),
      k_i=(VDAS_INNER_K_BP, VDAS_INNER_KI_V),
      k_f=0.0,
      pos_limit=PEDAL_RAMP_RATE_UP,
      neg_limit=-PEDAL_RAMP_RATE_DOWN,
      rate=1.0 / dt,
    )
    self.a_ego_filter = FirstOrderFilter(0.0, VDAS_AEGO_FILTER_RC, dt)
    self.prev_a_ego_filtered = 0.0
    self.prev_pedal_di = 0.0

  def update(self, a_cmd: float, v_ego: float, prev_pedal_di: float, a_ego: float = 0.0,
             freeze_integrator: bool = False, orientation_ned: list[float] | None = None) -> float:
    a_limited = self.jerk_limiter.update(a_cmd)
    grade_accel, pitch_comp = self.grade_estimator.update(orientation_ned or [])

    ff_di = self._feedforward(a_limited, v_ego) + pitch_comp
    a_ego_corrected = a_ego - grade_accel
    a_ego_filtered = self.a_ego_filter.update(a_ego_corrected)
    j_ego = (a_ego_filtered - self.prev_a_ego_filtered) / self.dt
    self.prev_a_ego_filtered = a_ego_filtered

    future_t = float(interp(v_ego, VDAS_FUTURE_T_BP, VDAS_FUTURE_T_V))
    error = a_limited - (a_ego_filtered + j_ego * future_t)
    if abs(error) < PID_ERROR_DEADBAND:
      error = 0.0

    pedal_di = ff_di + float(self.inner_pid.update(error, speed=v_ego, freeze_integrator=freeze_integrator))
    max_pedal_value = float(interp(v_ego, PEDAL_BP, PEDAL_MAX_VALUES))
    pedal_di = float(clip(pedal_di, PEDAL_DI_MIN, max_pedal_value))
    pedal_di = float(clip(pedal_di, prev_pedal_di - PEDAL_RAMP_RATE_DOWN, prev_pedal_di + PEDAL_RAMP_RATE_UP))
    self.prev_pedal_di = pedal_di
    return pedal_di

  def reset(self, a_init: float = 0.0, pedal_di_init: float = 0.0) -> None:
    self.jerk_limiter.reset(a_init)
    self.inner_pid.reset()
    self.grade_estimator.reset()
    self.a_ego_filter.x = 0.0
    self.prev_a_ego_filtered = 0.0
    self.prev_pedal_di = pedal_di_init

  def _feedforward(self, a_cmd: float, v_ego: float) -> float:
    zero_torque_di = get_zero_torque().get(v_ego)
    max_pedal_value = float(interp(v_ego, PEDAL_BP, PEDAL_MAX_VALUES))
    return float(clip(self.ff_model.get(a_cmd, v_ego, zero_torque_di), PEDAL_DI_MIN, max_pedal_value))

