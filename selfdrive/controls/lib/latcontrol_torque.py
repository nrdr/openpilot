import math
import numpy as np
from collections import deque

from cereal import log
from opendbc.car.gm.values import CAR as GM_CAR
from opendbc.car.honda.values import CAR as HONDA_CAR, HondaFlags
from opendbc.car.hyundai.values import CAR as HYUNDAI_CAR
from opendbc.car.lateral import get_friction
from openpilot.common.constants import ACCELERATION_DUE_TO_GRAVITY, CV
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.pid import PIDController
from openpilot.selfdrive.controls.lib.drive_helpers import MIN_SPEED
from openpilot.selfdrive.controls.lib.latcontrol import LatControl
from openpilot.starpilot.common.testing_grounds import testing_ground

# At higher speeds (25+mph) we can assume:
# Lateral acceleration achieved by a specific car correlates to
# torque applied to the steering rack. It does not correlate to
# wheel slip, or to speed.

# This controller applies torque to achieve desired lateral
# accelerations. To compensate for the low speed effects the
# proportional gain is increased at low speeds by the PID controller.
# Additionally, there is friction in the steering wheel that needs
# to be overcome to move it at all, this is compensated for too.

KP = 0.6
KI = 0.35

INTERP_SPEEDS = [1, 1.5, 2.0, 3.0, 5, 7.5, 10, 15, 30]
KP_INTERP = [250, 120, 65, 30, 11.5, 5.5, 3.5, 2.0, KP]

LOW_SPEED_X = [0, 10, 20, 30]
LOW_SPEED_Y = [12, 10.5, 8, 5]
MAX_LAT_JERK_UP = 2.5            # m/s^3

LP_FILTER_CUTOFF_HZ = 1.2
JERK_LOOKAHEAD_SECONDS = 0.19
JERK_GAIN = 0.22
LAT_ACCEL_REQUEST_BUFFER_SECONDS = 1.0
VERSION = 2
DEBUG_TORQUE_TUNE = False
FF_SCALE_BLEND_LAT_ACCEL = 0.05
DEADZONE_BOOST_LAT_ACCEL = 0.15
UNWIND_D_DES_THRESHOLD = -1.0
UNWIND_LAT_ACCEL_NEAR_ZERO = 0.3
MIN_LATERAL_CONTROL_SPEED = 0.3
CIVIC_BOSCH_MODIFIED_B_FIXED_FRICTION_THRESHOLD = 0.30
CIVIC_BOSCH_MODIFIED_B_TRANSITION_SPEED = 12.0
CIVIC_BOSCH_MODIFIED_B_PHASE_SCALE = 0.10
CIVIC_BOSCH_MODIFIED_B_FF_ONSET = 0.18
CIVIC_BOSCH_MODIFIED_B_FF_ONSET_WIDTH = 0.07
CIVIC_BOSCH_MODIFIED_B_FF_CUTOFF = 1.00
CIVIC_BOSCH_MODIFIED_B_FF_CUTOFF_WIDTH = 0.30
CIVIC_BOSCH_MODIFIED_B_FF_REDUCTION_LEFT = 0.11
CIVIC_BOSCH_MODIFIED_B_FF_REDUCTION_RIGHT = 0.08
CIVIC_BOSCH_MODIFIED_B_TURN_IN_BOOST_LEFT = 0.08
CIVIC_BOSCH_MODIFIED_B_TURN_IN_BOOST_RIGHT = 0.10
CIVIC_BOSCH_MODIFIED_B_UNWIND_TAPER_LEFT = 0.22
CIVIC_BOSCH_MODIFIED_B_UNWIND_TAPER_RIGHT = 0.24
CIVIC_BOSCH_MODIFIED_B_TURN_IN_FRICTION_BOOST_LEFT = 0.04
CIVIC_BOSCH_MODIFIED_B_TURN_IN_FRICTION_BOOST_RIGHT = 0.05
CIVIC_BOSCH_MODIFIED_B_UNWIND_FRICTION_REDUCTION_LEFT = 0.15
CIVIC_BOSCH_MODIFIED_B_UNWIND_FRICTION_REDUCTION_RIGHT = 0.18

BOLT_2022_2023_CARS = (
  GM_CAR.CHEVROLET_BOLT_ACC_2022_2023,
  GM_CAR.CHEVROLET_BOLT_ACC_2022_2023_PEDAL,
  GM_CAR.CHEVROLET_BOLT_CC_2022_2023,
)
BOLT_2018_2021_CARS = (
  GM_CAR.CHEVROLET_BOLT_CC_2018_2021,
)
BOLT_2017_CARS = (
  GM_CAR.CHEVROLET_BOLT_CC_2017,
)
BOLT_CARS = BOLT_2022_2023_CARS + BOLT_2018_2021_CARS + BOLT_2017_CARS
VOLT_STANDARD_CARS = (
  GM_CAR.CHEVROLET_VOLT,
  GM_CAR.CHEVROLET_VOLT_ASCM,
  GM_CAR.CHEVROLET_VOLT_CAMERA,
  GM_CAR.CHEVROLET_VOLT_CC,
)
GENESIS_G90_CARS = (
  HYUNDAI_CAR.GENESIS_G90,
)
IONIQ_6_CARS = (
  HYUNDAI_CAR.HYUNDAI_IONIQ_6,
)
KIA_EV6_CARS = (
  HYUNDAI_CAR.KIA_EV6,
)

BOLT_2017_LATERAL_TESTING_GROUND_ID = testing_ground.id_3
BOLT_2017_STEER_RATIO_TEST_SCALE = 1.045
BOLT_2017_STEER_RATIO_ONSET_SPEED = 20.0 * CV.MPH_TO_MS
BOLT_2017_STEER_RATIO_ONSET_WIDTH = 4.0 * CV.MPH_TO_MS
BOLT_2017_CENTER_TAPER_LAT = 0.10
BOLT_2017_CENTER_TAPER_WIDTH = 0.03
BOLT_2017_CENTER_TAPER_GAIN = 0.055
BOLT_2017_TORQUE_SCALE_BP = [0.0, 0.2, 0.5, 1.0, 1.5, 2.5]
BOLT_2017_TORQUE_SCALE_LEFT = [1.0, 1.0, 1.065, 1.060, 1.055, 1.045]
BOLT_2017_TORQUE_SCALE_RIGHT = [1.0, 1.0, 1.035, 1.020, 0.995, 0.985]
BOLT_2017_TRANSITION_SPEED = 10.0
BOLT_2017_PHASE_SCALE = 0.12
BOLT_2017_TURN_IN_BOOST_LEFT = 0.28
BOLT_2017_TURN_IN_BOOST_RIGHT = 0.18
BOLT_2017_UNWIND_TAPER_LEFT = 0.08
BOLT_2017_UNWIND_TAPER_RIGHT = 0.28

BOLT_2018_2021_LATERAL_TESTING_GROUND_ID = testing_ground.id_4
BOLT_2018_2021_STEER_RATIO_TEST_SCALE = 1.01
BOLT_2018_2021_TORQUE_GAIN_LEFT = 0.090
BOLT_2018_2021_TORQUE_GAIN_RIGHT = 0.050
BOLT_2018_2021_TORQUE_ONSET = 0.18
BOLT_2018_2021_TORQUE_ONSET_WIDTH = 0.08
BOLT_2018_2021_TORQUE_CUTOFF = 1.05
BOLT_2018_2021_TORQUE_CUTOFF_WIDTH = 0.24
BOLT_2018_2021_JERK_TAPER_CUTOFF = 0.42
BOLT_2018_2021_CENTER_TAPER_LAT = 0.12
BOLT_2018_2021_CENTER_TAPER_WIDTH = 0.04
BOLT_2018_2021_CENTER_TAPER_GAIN = 0.35
BOLT_2018_2021_TRANSITION_SPEED = 8.5
BOLT_2018_2021_PHASE_SCALE = 0.10
BOLT_2018_2021_TURN_IN_BOOST_LEFT = 0.22
BOLT_2018_2021_TURN_IN_BOOST_RIGHT = 0.12
BOLT_2018_2021_UNWIND_TAPER_GAIN_LEFT = 0.80
BOLT_2018_2021_UNWIND_TAPER_GAIN_RIGHT = 1.04
BOLT_2018_2021_FRICTION_MULT = 1.01
BOLT_2018_2021_FRICTION_LAT_RISE = 0.24
BOLT_2018_2021_FRICTION_JERK_RISE = 0.28
BOLT_2018_2021_TURN_IN_THRESHOLD_REDUCTION_LEFT = 0.16
BOLT_2018_2021_TURN_IN_THRESHOLD_REDUCTION_RIGHT = 0.16
BOLT_2018_2021_UNWIND_THRESHOLD_INCREASE_LEFT = 0.15
BOLT_2018_2021_UNWIND_THRESHOLD_INCREASE_RIGHT = 0.25
BOLT_2018_2021_TURN_IN_FRICTION_BOOST_LEFT = 0.08
BOLT_2018_2021_TURN_IN_FRICTION_BOOST_RIGHT = 0.08
BOLT_2018_2021_UNWIND_FRICTION_REDUCTION_LEFT = 0.17
BOLT_2018_2021_UNWIND_FRICTION_REDUCTION_RIGHT = 0.27

BOLT_2022_2023_LATERAL_TESTING_GROUND_ID = testing_ground.id_5
BOLT_2022_2023_FF_GAIN_LEFT = 0.13
BOLT_2022_2023_FF_GAIN_RIGHT = 0.07
BOLT_2022_2023_FF_ONSET = 0.12
BOLT_2022_2023_FF_ONSET_WIDTH = 0.07
BOLT_2022_2023_FF_CUTOFF = 1.35
BOLT_2022_2023_FF_CUTOFF_WIDTH = 0.28
BOLT_2022_2023_TRANSITION_SPEED = 9.0
BOLT_2022_2023_PHASE_SCALE = 0.12
BOLT_2022_2023_TURN_IN_BOOST_LEFT = 0.12
BOLT_2022_2023_TURN_IN_BOOST_RIGHT = 0.06
BOLT_2022_2023_UNWIND_TAPER_LEFT = 0.28
BOLT_2022_2023_UNWIND_TAPER_RIGHT = 0.24
BOLT_2022_2023_FRICTION_MULT = 1.15
BOLT_2022_2023_FRICTION_LAT_RISE = 0.22
BOLT_2022_2023_FRICTION_JERK_RISE = 0.26
BOLT_2022_2023_TURN_IN_THRESHOLD_REDUCTION_LEFT = 0.14
BOLT_2022_2023_TURN_IN_THRESHOLD_REDUCTION_RIGHT = 0.08
BOLT_2022_2023_UNWIND_THRESHOLD_INCREASE_LEFT = 0.20
BOLT_2022_2023_UNWIND_THRESHOLD_INCREASE_RIGHT = 0.16
BOLT_2022_2023_TURN_IN_FRICTION_BOOST_LEFT = 0.08
BOLT_2022_2023_TURN_IN_FRICTION_BOOST_RIGHT = 0.04
BOLT_2022_2023_UNWIND_FRICTION_REDUCTION_LEFT = 0.21
BOLT_2022_2023_UNWIND_FRICTION_REDUCTION_RIGHT = 0.17

VOLT_STANDARD_LATERAL_TESTING_GROUND_ID = testing_ground.id_3
VOLT_STANDARD_FF_GAIN_LEFT = 0.09
VOLT_STANDARD_FF_GAIN_RIGHT = 0.09
VOLT_STANDARD_FF_ONSET = 0.10
VOLT_STANDARD_FF_ONSET_WIDTH = 0.05
VOLT_STANDARD_FF_CUTOFF = 1.30
VOLT_STANDARD_FF_CUTOFF_WIDTH = 0.24
VOLT_STANDARD_TRANSITION_SPEED = 10.0
VOLT_STANDARD_PHASE_SCALE = 0.10
VOLT_STANDARD_TURN_IN_BOOST_LEFT = 0.18
VOLT_STANDARD_TURN_IN_BOOST_RIGHT = 0.52
VOLT_STANDARD_UNWIND_TAPER_LEFT = 0.22
VOLT_STANDARD_UNWIND_TAPER_RIGHT = 0.50
VOLT_STANDARD_FRICTION_MULT = 1.04
VOLT_STANDARD_FRICTION_LAT_RISE = 0.20
VOLT_STANDARD_FRICTION_JERK_RISE = 0.24
VOLT_STANDARD_TURN_IN_THRESHOLD_REDUCTION_LEFT = 0.10
VOLT_STANDARD_TURN_IN_THRESHOLD_REDUCTION_RIGHT = 0.30
VOLT_STANDARD_UNWIND_THRESHOLD_INCREASE_LEFT = 0.12
VOLT_STANDARD_UNWIND_THRESHOLD_INCREASE_RIGHT = 0.42
VOLT_STANDARD_TURN_IN_FRICTION_BOOST_LEFT = 0.05
VOLT_STANDARD_TURN_IN_FRICTION_BOOST_RIGHT = 0.16
VOLT_STANDARD_UNWIND_FRICTION_REDUCTION_LEFT = 0.12
VOLT_STANDARD_UNWIND_FRICTION_REDUCTION_RIGHT = 0.36
VOLT_STANDARD_CENTER_TAPER_MAX = 0.12
VOLT_STANDARD_CENTER_TAPER_LAT = 0.10
VOLT_STANDARD_CENTER_TAPER_LAT_WIDTH = 0.018
VOLT_STANDARD_CENTER_TAPER_SPEED = 20.0
VOLT_STANDARD_CENTER_TAPER_SPEED_WIDTH = 2.5

GENESIS_G90_LATERAL_TESTING_GROUND_ID = testing_ground.id_4
GENESIS_G90_FF_GAIN_LEFT = 0.17
GENESIS_G90_FF_GAIN_RIGHT = 0.16
GENESIS_G90_FF_ONSET = 0.10
GENESIS_G90_FF_ONSET_WIDTH = 0.05
GENESIS_G90_FF_CUTOFF = 1.75
GENESIS_G90_FF_CUTOFF_WIDTH = 0.36
GENESIS_G90_TRANSITION_SPEED = 8.5
GENESIS_G90_PHASE_SCALE = 0.12
GENESIS_G90_TURN_IN_BOOST_LEFT = 0.34
GENESIS_G90_TURN_IN_BOOST_RIGHT = 0.42
GENESIS_G90_UNWIND_TAPER_LEFT = 0.24
GENESIS_G90_UNWIND_TAPER_RIGHT = 0.34
GENESIS_G90_FRICTION_MULT = 1.02
GENESIS_G90_FRICTION_LAT_RISE = 0.22
GENESIS_G90_FRICTION_JERK_RISE = 0.24
GENESIS_G90_TURN_IN_THRESHOLD_REDUCTION_LEFT = 0.14
GENESIS_G90_TURN_IN_THRESHOLD_REDUCTION_RIGHT = 0.18
GENESIS_G90_UNWIND_THRESHOLD_INCREASE_LEFT = 0.16
GENESIS_G90_UNWIND_THRESHOLD_INCREASE_RIGHT = 0.26
GENESIS_G90_TURN_IN_FRICTION_BOOST_LEFT = 0.09
GENESIS_G90_TURN_IN_FRICTION_BOOST_RIGHT = 0.12
GENESIS_G90_UNWIND_FRICTION_REDUCTION_LEFT = 0.14
GENESIS_G90_UNWIND_FRICTION_REDUCTION_RIGHT = 0.22

IONIQ_6_FF_GAIN_LEFT = 0.040
IONIQ_6_FF_GAIN_RIGHT = 0.000
IONIQ_6_BASE_LAT_ACCEL_FACTOR_MULT = 1.15
IONIQ_6_BASE_FRICTION_THRESHOLD = 0.30
IONIQ_6_FF_ONSET = 0.10
IONIQ_6_FF_ONSET_WIDTH = 0.04
IONIQ_6_FF_CUTOFF = 0.48
IONIQ_6_FF_CUTOFF_WIDTH = 0.12
IONIQ_6_TRANSITION_SPEED = 10.0
IONIQ_6_PHASE_SCALE = 0.10
IONIQ_6_TURN_IN_BOOST_LEFT = 1.08
IONIQ_6_TURN_IN_BOOST_RIGHT = 1.24
IONIQ_6_UNWIND_TAPER_LEFT = 1.84
IONIQ_6_UNWIND_TAPER_RIGHT = 4.10
IONIQ_6_FRICTION_MULT = 0.995
IONIQ_6_FRICTION_LAT_RISE = 0.20
IONIQ_6_FRICTION_JERK_RISE = 0.24
IONIQ_6_TURN_IN_THRESHOLD_REDUCTION_LEFT = 0.34
IONIQ_6_TURN_IN_THRESHOLD_REDUCTION_RIGHT = 0.54
IONIQ_6_UNWIND_THRESHOLD_INCREASE_LEFT = 2.15
IONIQ_6_UNWIND_THRESHOLD_INCREASE_RIGHT = 5.00
IONIQ_6_TURN_IN_FRICTION_BOOST_LEFT = 0.18
IONIQ_6_TURN_IN_FRICTION_BOOST_RIGHT = 0.34
IONIQ_6_UNWIND_FRICTION_REDUCTION_LEFT = 1.86
IONIQ_6_UNWIND_FRICTION_REDUCTION_RIGHT = 4.55
IONIQ_6_CENTER_TAPER_MAX = 0.056
IONIQ_6_CENTER_TAPER_LAT = 0.22
IONIQ_6_CENTER_TAPER_LAT_WIDTH = 0.02
IONIQ_6_CENTER_TAPER_SPEED = 18.0
IONIQ_6_CENTER_TAPER_SPEED_WIDTH = 2.5
IONIQ_6_LOW_MID_CENTER_TAPER_MAX = 0.088
IONIQ_6_LOW_MID_CENTER_TAPER_LAT = 0.28
IONIQ_6_LOW_MID_CENTER_TAPER_LAT_WIDTH = 0.06
IONIQ_6_LOW_MID_CENTER_TAPER_SPEED_MIN = 8.5
IONIQ_6_LOW_MID_CENTER_TAPER_SPEED_MAX = 16.5
IONIQ_6_LOW_MID_CENTER_TAPER_SPEED_WIDTH = 1.5
IONIQ_6_DIRECTIONAL_TAPER_LAT_START = 0.15
IONIQ_6_DIRECTIONAL_TAPER_LAT_END = 0.90
IONIQ_6_DIRECTIONAL_TAPER_LAT_WIDTH = 0.08
IONIQ_6_DIRECTIONAL_TAPER_BASE_LEFT = 0.10
IONIQ_6_DIRECTIONAL_TAPER_BASE_RIGHT = 0.40
IONIQ_6_DIRECTIONAL_TAPER_UNWIND_LEFT = 1.20
IONIQ_6_DIRECTIONAL_TAPER_UNWIND_RIGHT = 2.30
IONIQ_6_DIRECTIONAL_TAPER_FLOOR_LEFT = 0.54
IONIQ_6_DIRECTIONAL_TAPER_FLOOR_RIGHT = 0.60
IONIQ_6_DIRECTIONAL_TAPER_UNWIND_FLOOR_LEFT = 0.10
IONIQ_6_DIRECTIONAL_TAPER_UNWIND_FLOOR_RIGHT = 0.04
IONIQ_6_OUTPUT_TAPER_SPEED = 8.5
IONIQ_6_OUTPUT_TAPER_SPEED_WIDTH = 2.5
IONIQ_6_OUTPUT_CENTER_TAPER_BLEND = 0.90
IONIQ_6_OUTPUT_DIRECTIONAL_TAPER_BLEND = 0.97

KIA_EV6_LATERAL_TESTING_GROUND_ID = testing_ground.id_6
KIA_EV6_LATERAL_TESTING_GROUND_VARIANT = "C"
KIA_EV6_FF_GAIN_LEFT = 0.07
KIA_EV6_FF_GAIN_RIGHT = 0.10
KIA_EV6_FF_ONSET = 0.08
KIA_EV6_FF_ONSET_WIDTH = 0.04
KIA_EV6_FF_CUTOFF = 0.60
KIA_EV6_FF_CUTOFF_WIDTH = 0.14
KIA_EV6_TRANSITION_SPEED = 11.0
KIA_EV6_PHASE_SCALE = 0.09
KIA_EV6_TURN_IN_BOOST_LEFT = 0.14
KIA_EV6_TURN_IN_BOOST_RIGHT = 0.22
KIA_EV6_UNWIND_TAPER_LEFT = 0.26
KIA_EV6_UNWIND_TAPER_RIGHT = 0.34
KIA_EV6_FRICTION_MULT = 1.01
KIA_EV6_FRICTION_LAT_RISE = 0.18
KIA_EV6_FRICTION_JERK_RISE = 0.22
KIA_EV6_TURN_IN_THRESHOLD_REDUCTION_LEFT = 0.10
KIA_EV6_TURN_IN_THRESHOLD_REDUCTION_RIGHT = 0.14
KIA_EV6_UNWIND_THRESHOLD_INCREASE_LEFT = 0.14
KIA_EV6_UNWIND_THRESHOLD_INCREASE_RIGHT = 0.18
KIA_EV6_TURN_IN_FRICTION_BOOST_LEFT = 0.03
KIA_EV6_TURN_IN_FRICTION_BOOST_RIGHT = 0.05
KIA_EV6_UNWIND_FRICTION_REDUCTION_LEFT = 0.12
KIA_EV6_UNWIND_FRICTION_REDUCTION_RIGHT = 0.15

VOLT_PLEXY_LATERAL_TESTING_GROUND_ID = testing_ground.id_7
VOLT_PLEXY_FF_GAIN_LEFT = 0.12
VOLT_PLEXY_FF_GAIN_RIGHT = 0.07
VOLT_PLEXY_FF_ONSET = 0.10
VOLT_PLEXY_FF_ONSET_WIDTH = 0.06
VOLT_PLEXY_FF_CUTOFF = 1.35
VOLT_PLEXY_FF_CUTOFF_WIDTH = 0.24
VOLT_PLEXY_TRANSITION_SPEED = 10.5
VOLT_PLEXY_PHASE_SCALE = 0.10
VOLT_PLEXY_TURN_IN_BOOST_LEFT = 0.22
VOLT_PLEXY_TURN_IN_BOOST_RIGHT = 0.24
VOLT_PLEXY_UNWIND_TAPER_LEFT = 0.22
VOLT_PLEXY_UNWIND_TAPER_RIGHT = 0.56
VOLT_PLEXY_FRICTION_MULT = 1.04
VOLT_PLEXY_FRICTION_LAT_RISE = 0.22
VOLT_PLEXY_FRICTION_JERK_RISE = 0.24
VOLT_PLEXY_TURN_IN_THRESHOLD_REDUCTION_LEFT = 0.16
VOLT_PLEXY_TURN_IN_THRESHOLD_REDUCTION_RIGHT = 0.12
VOLT_PLEXY_UNWIND_THRESHOLD_INCREASE_LEFT = 0.15
VOLT_PLEXY_UNWIND_THRESHOLD_INCREASE_RIGHT = 0.34
VOLT_PLEXY_TURN_IN_FRICTION_BOOST_LEFT = 0.08
VOLT_PLEXY_TURN_IN_FRICTION_BOOST_RIGHT = 0.06
VOLT_PLEXY_UNWIND_FRICTION_REDUCTION_LEFT = 0.16
VOLT_PLEXY_UNWIND_FRICTION_REDUCTION_RIGHT = 0.40


def _sigmoid(x: float) -> float:
  if x >= 0.0:
    z = math.exp(-x)
    return 1.0 / (1.0 + z)

  z = math.exp(x)
  return z / (1.0 + z)


def get_friction_threshold(v_ego: float) -> float:
  # Keep the speed-scaled friction threshold behavior.
  return float(np.interp(v_ego, [1 * CV.MPH_TO_MS, 20 * CV.MPH_TO_MS, 75 * CV.MPH_TO_MS], [0.16, 0.19, 0.27]))


def civic_bosch_modified_lateral_testing_ground_active() -> bool:
  return testing_ground.use("8", "B")


def _civic_bosch_modified_b_low_speed_factor(v_ego: float) -> float:
  return 1.0 / (1.0 + (max(v_ego, 0.0) / CIVIC_BOSCH_MODIFIED_B_TRANSITION_SPEED) ** 2)


def _civic_bosch_modified_b_transition_phase(desired_lateral_accel: float, desired_lateral_jerk: float) -> float:
  return math.tanh((desired_lateral_accel * desired_lateral_jerk) / CIVIC_BOSCH_MODIFIED_B_PHASE_SCALE)


def _civic_bosch_modified_b_side_value(desired_lateral_accel: float, left_value: float, right_value: float) -> float:
  return left_value if desired_lateral_accel >= 0.0 else right_value


def get_civic_bosch_modified_b_ff_scale(desired_lateral_accel: float, desired_lateral_jerk: float, v_ego: float) -> float:
  if desired_lateral_accel == 0.0:
    return 1.0

  abs_lateral_accel = abs(desired_lateral_accel)
  onset = _sigmoid((abs_lateral_accel - CIVIC_BOSCH_MODIFIED_B_FF_ONSET) / CIVIC_BOSCH_MODIFIED_B_FF_ONSET_WIDTH)
  cutoff = _sigmoid((CIVIC_BOSCH_MODIFIED_B_FF_CUTOFF - abs_lateral_accel) / CIVIC_BOSCH_MODIFIED_B_FF_CUTOFF_WIDTH)
  base_reduction = _civic_bosch_modified_b_side_value(desired_lateral_accel,
                                                       CIVIC_BOSCH_MODIFIED_B_FF_REDUCTION_LEFT,
                                                       CIVIC_BOSCH_MODIFIED_B_FF_REDUCTION_RIGHT) * onset * cutoff

  phase = _civic_bosch_modified_b_transition_phase(desired_lateral_accel, desired_lateral_jerk)
  turn_in_weight = max(phase, 0.0)
  unwind_weight = max(-phase, 0.0)
  low_speed_factor = _civic_bosch_modified_b_low_speed_factor(v_ego)

  turn_in_boost = 1.0 + (_civic_bosch_modified_b_side_value(desired_lateral_accel,
                                                             CIVIC_BOSCH_MODIFIED_B_TURN_IN_BOOST_LEFT,
                                                             CIVIC_BOSCH_MODIFIED_B_TURN_IN_BOOST_RIGHT) *
                          turn_in_weight * (0.40 + 0.60 * low_speed_factor))
  unwind_taper = 1.0 - (_civic_bosch_modified_b_side_value(desired_lateral_accel,
                                                            CIVIC_BOSCH_MODIFIED_B_UNWIND_TAPER_LEFT,
                                                            CIVIC_BOSCH_MODIFIED_B_UNWIND_TAPER_RIGHT) *
                         unwind_weight * (0.35 + 0.65 * low_speed_factor))
  return (1.0 - base_reduction) * turn_in_boost * max(unwind_taper, 0.0)


def get_civic_bosch_modified_b_friction_scale(v_ego: float, desired_lateral_accel: float, desired_lateral_jerk: float) -> float:
  if desired_lateral_accel == 0.0 or desired_lateral_jerk == 0.0:
    return 1.0

  abs_lateral_accel = abs(desired_lateral_accel)
  onset = _sigmoid((abs_lateral_accel - CIVIC_BOSCH_MODIFIED_B_FF_ONSET) / CIVIC_BOSCH_MODIFIED_B_FF_ONSET_WIDTH)
  cutoff = _sigmoid((CIVIC_BOSCH_MODIFIED_B_FF_CUTOFF - abs_lateral_accel) / CIVIC_BOSCH_MODIFIED_B_FF_CUTOFF_WIDTH)
  envelope = onset * cutoff * _civic_bosch_modified_b_low_speed_factor(v_ego)
  phase = _civic_bosch_modified_b_transition_phase(desired_lateral_accel, desired_lateral_jerk)
  turn_in_weight = max(phase, 0.0)
  unwind_weight = max(-phase, 0.0)

  friction_scale = 1.0
  friction_scale += (_civic_bosch_modified_b_side_value(desired_lateral_accel,
                                                         CIVIC_BOSCH_MODIFIED_B_TURN_IN_FRICTION_BOOST_LEFT,
                                                         CIVIC_BOSCH_MODIFIED_B_TURN_IN_FRICTION_BOOST_RIGHT) *
                     envelope * turn_in_weight)
  friction_scale -= (_civic_bosch_modified_b_side_value(desired_lateral_accel,
                                                         CIVIC_BOSCH_MODIFIED_B_UNWIND_FRICTION_REDUCTION_LEFT,
                                                         CIVIC_BOSCH_MODIFIED_B_UNWIND_FRICTION_REDUCTION_RIGHT) *
                     envelope * unwind_weight)
  return min(max(friction_scale, 0.82), 1.06)


def bolt_2017_lateral_testing_ground_active() -> bool:
  return testing_ground.use(BOLT_2017_LATERAL_TESTING_GROUND_ID)


def _bolt_2017_sigmoid(x: float) -> float:
  return _sigmoid(x)


def _bolt_2017_high_speed_factor(v_ego: float) -> float:
  return _bolt_2017_sigmoid((max(v_ego, 0.0) - BOLT_2017_STEER_RATIO_ONSET_SPEED) / BOLT_2017_STEER_RATIO_ONSET_WIDTH)


def get_bolt_2017_steer_ratio_scale(v_ego: float) -> float:
  return 1.0 + ((BOLT_2017_STEER_RATIO_TEST_SCALE - 1.0) * _bolt_2017_high_speed_factor(v_ego))


def get_bolt_2017_center_taper_scale(desired_lateral_accel: float, v_ego: float) -> float:
  center_window = _bolt_2017_sigmoid((BOLT_2017_CENTER_TAPER_LAT - abs(desired_lateral_accel)) / BOLT_2017_CENTER_TAPER_WIDTH)
  return 1.0 - (BOLT_2017_CENTER_TAPER_GAIN * _bolt_2017_high_speed_factor(v_ego) * center_window)


def _bolt_2017_low_speed_factor(v_ego: float) -> float:
  return 1.0 / (1.0 + (max(v_ego, 0.0) / BOLT_2017_TRANSITION_SPEED) ** 2)


def _bolt_2017_transition_phase(desired_lateral_accel: float, desired_lateral_jerk: float) -> float:
  return math.tanh((desired_lateral_accel * desired_lateral_jerk) / BOLT_2017_PHASE_SCALE)


def _bolt_2017_side_value(desired_lateral_accel: float, left_value: float, right_value: float) -> float:
  return left_value if desired_lateral_accel >= 0.0 else right_value


def get_bolt_2017_base_torque_scale(desired_lateral_accel: float) -> float:
  if desired_lateral_accel == 0.0:
    return 1.0

  scale_values = BOLT_2017_TORQUE_SCALE_LEFT if desired_lateral_accel > 0.0 else BOLT_2017_TORQUE_SCALE_RIGHT
  return float(np.interp(abs(desired_lateral_accel), BOLT_2017_TORQUE_SCALE_BP, scale_values))


def get_bolt_2017_torque_scale(desired_lateral_accel: float, desired_lateral_jerk: float = 0.0, v_ego: float = 30.0) -> float:
  base_scale = get_bolt_2017_base_torque_scale(desired_lateral_accel)
  scale = base_scale
  if base_scale > 1.0 and desired_lateral_jerk != 0.0:
    low_speed_factor = _bolt_2017_low_speed_factor(v_ego)
    phase = _bolt_2017_transition_phase(desired_lateral_accel, desired_lateral_jerk)
    turn_in_weight = max(phase, 0.0)
    unwind_weight = max(-phase, 0.0)
    turn_in_boost = 1.0 + (_bolt_2017_side_value(desired_lateral_accel, BOLT_2017_TURN_IN_BOOST_LEFT, BOLT_2017_TURN_IN_BOOST_RIGHT) *
                            turn_in_weight * (0.35 + 0.65 * low_speed_factor))
    unwind_taper = 1.0 - (_bolt_2017_side_value(desired_lateral_accel, BOLT_2017_UNWIND_TAPER_LEFT, BOLT_2017_UNWIND_TAPER_RIGHT) *
                           unwind_weight * (0.45 + 0.55 * low_speed_factor))
    scale = 1.0 + ((base_scale - 1.0) * turn_in_boost * max(unwind_taper, 0.0))

  return scale * get_bolt_2017_center_taper_scale(desired_lateral_accel, v_ego)


def bolt_2018_2021_lateral_testing_ground_active() -> bool:
  return testing_ground.use(BOLT_2018_2021_LATERAL_TESTING_GROUND_ID)


def _bolt_2018_2021_sigmoid(x: float) -> float:
  return _sigmoid(x)


def _bolt_2018_2021_low_speed_factor(v_ego: float) -> float:
  return 1.0 / (1.0 + (max(v_ego, 0.0) / BOLT_2018_2021_TRANSITION_SPEED) ** 2)


def _bolt_2018_2021_transition_phase(desired_lateral_accel: float, desired_lateral_jerk: float) -> float:
  return math.tanh((desired_lateral_accel * desired_lateral_jerk) / BOLT_2018_2021_PHASE_SCALE)


def _bolt_2018_2021_side_value(desired_lateral_accel: float, left_value: float, right_value: float) -> float:
  return left_value if desired_lateral_accel >= 0.0 else right_value


def _bolt_2018_2021_transition_envelope(v_ego: float, desired_lateral_accel: float, desired_lateral_jerk: float) -> float:
  lat_factor = 1.0 - math.exp(-abs(desired_lateral_accel) / BOLT_2018_2021_FRICTION_LAT_RISE)
  jerk_factor = 1.0 - math.exp(-abs(desired_lateral_jerk) / BOLT_2018_2021_FRICTION_JERK_RISE)
  return _bolt_2018_2021_low_speed_factor(v_ego) * lat_factor * jerk_factor


def get_bolt_2018_2021_torque_scale(desired_lateral_accel: float) -> float:
  if desired_lateral_accel == 0.0:
    return 1.0

  gain = BOLT_2018_2021_TORQUE_GAIN_LEFT if desired_lateral_accel > 0.0 else BOLT_2018_2021_TORQUE_GAIN_RIGHT
  abs_lateral_accel = abs(desired_lateral_accel)
  onset = _bolt_2018_2021_sigmoid((abs_lateral_accel - BOLT_2018_2021_TORQUE_ONSET) / BOLT_2018_2021_TORQUE_ONSET_WIDTH)
  cutoff = _bolt_2018_2021_sigmoid((BOLT_2018_2021_TORQUE_CUTOFF - abs_lateral_accel) / BOLT_2018_2021_TORQUE_CUTOFF_WIDTH)
  return 1.0 + gain * onset * cutoff


def get_bolt_2018_2021_dynamic_torque_scale(desired_lateral_accel: float, desired_lateral_jerk: float, v_ego: float) -> float:
  base_scale = get_bolt_2018_2021_torque_scale(desired_lateral_accel)
  extra_scale = max(base_scale - 1.0, 0.0)
  abs_lateral_accel = abs(desired_lateral_accel)
  low_speed_factor = _bolt_2018_2021_low_speed_factor(v_ego)
  high_speed_factor = 1.0 - low_speed_factor
  center_window = _bolt_2018_2021_sigmoid((BOLT_2018_2021_CENTER_TAPER_LAT - abs_lateral_accel) / BOLT_2018_2021_CENTER_TAPER_WIDTH)
  center_taper = 1.0 - (BOLT_2018_2021_CENTER_TAPER_GAIN * high_speed_factor * center_window)
  phase = _bolt_2018_2021_transition_phase(desired_lateral_accel, desired_lateral_jerk)
  turn_in_weight = max(phase, 0.0)
  jerk_taper = 1.0 / (1.0 + (abs(desired_lateral_jerk) / BOLT_2018_2021_JERK_TAPER_CUTOFF) ** 2)
  turn_in_boost = 1.0 + (_bolt_2018_2021_side_value(desired_lateral_accel, BOLT_2018_2021_TURN_IN_BOOST_LEFT, BOLT_2018_2021_TURN_IN_BOOST_RIGHT) *
                          turn_in_weight * low_speed_factor)
  unwind_weight = max(-phase, 0.0)
  unwind_taper = 1.0 - (_bolt_2018_2021_side_value(desired_lateral_accel, BOLT_2018_2021_UNWIND_TAPER_GAIN_LEFT, BOLT_2018_2021_UNWIND_TAPER_GAIN_RIGHT) *
                         unwind_weight * (0.55 + 0.45 * low_speed_factor))
  return 1.0 + (extra_scale * center_taper * jerk_taper * turn_in_boost * max(unwind_taper, 0.0))


def get_bolt_2018_2021_friction_threshold(v_ego: float, desired_lateral_accel: float = 0.0, desired_lateral_jerk: float = 0.0) -> float:
  base_threshold = get_friction_threshold(v_ego)
  transition_envelope = _bolt_2018_2021_transition_envelope(v_ego, desired_lateral_accel, desired_lateral_jerk)
  phase = _bolt_2018_2021_transition_phase(desired_lateral_accel, desired_lateral_jerk)
  turn_in_weight = max(phase, 0.0)
  unwind_weight = max(-phase, 0.0)
  threshold_scale = 1.0 - (_bolt_2018_2021_side_value(desired_lateral_accel, BOLT_2018_2021_TURN_IN_THRESHOLD_REDUCTION_LEFT, BOLT_2018_2021_TURN_IN_THRESHOLD_REDUCTION_RIGHT) *
                           transition_envelope * turn_in_weight)
  threshold_scale += (_bolt_2018_2021_side_value(desired_lateral_accel, BOLT_2018_2021_UNWIND_THRESHOLD_INCREASE_LEFT, BOLT_2018_2021_UNWIND_THRESHOLD_INCREASE_RIGHT) *
                      transition_envelope * unwind_weight)
  return base_threshold * min(max(threshold_scale, 0.82), 1.12)


def get_bolt_2018_2021_friction_scale(v_ego: float, desired_lateral_accel: float, desired_lateral_jerk: float) -> float:
  transition_envelope = _bolt_2018_2021_transition_envelope(v_ego, desired_lateral_accel, desired_lateral_jerk)
  phase = _bolt_2018_2021_transition_phase(desired_lateral_accel, desired_lateral_jerk)
  turn_in_weight = max(phase, 0.0)
  unwind_weight = max(-phase, 0.0)
  friction_scale = BOLT_2018_2021_FRICTION_MULT
  friction_scale += (_bolt_2018_2021_side_value(desired_lateral_accel, BOLT_2018_2021_TURN_IN_FRICTION_BOOST_LEFT, BOLT_2018_2021_TURN_IN_FRICTION_BOOST_RIGHT) *
                     transition_envelope * turn_in_weight)
  friction_scale -= (_bolt_2018_2021_side_value(desired_lateral_accel, BOLT_2018_2021_UNWIND_FRICTION_REDUCTION_LEFT, BOLT_2018_2021_UNWIND_FRICTION_REDUCTION_RIGHT) *
                     transition_envelope * unwind_weight)
  return min(max(friction_scale, 0.88), 1.10)


def bolt_2022_2023_lateral_testing_ground_active() -> bool:
  return testing_ground.use(BOLT_2022_2023_LATERAL_TESTING_GROUND_ID)


def _bolt_2022_2023_sigmoid(x: float) -> float:
  return _sigmoid(x)


def _bolt_2022_2023_low_speed_factor(v_ego: float) -> float:
  return 1.0 / (1.0 + (max(v_ego, 0.0) / BOLT_2022_2023_TRANSITION_SPEED) ** 2)


def _bolt_2022_2023_transition_phase(desired_lateral_accel: float, desired_lateral_jerk: float) -> float:
  return math.tanh((desired_lateral_accel * desired_lateral_jerk) / BOLT_2022_2023_PHASE_SCALE)


def _bolt_2022_2023_side_value(desired_lateral_accel: float, left_value: float, right_value: float) -> float:
  return left_value if desired_lateral_accel >= 0.0 else right_value


def _bolt_2022_2023_transition_envelope(v_ego: float, desired_lateral_accel: float, desired_lateral_jerk: float) -> float:
  lat_factor = 1.0 - math.exp(-abs(desired_lateral_accel) / BOLT_2022_2023_FRICTION_LAT_RISE)
  jerk_factor = 1.0 - math.exp(-abs(desired_lateral_jerk) / BOLT_2022_2023_FRICTION_JERK_RISE)
  return _bolt_2022_2023_low_speed_factor(v_ego) * lat_factor * jerk_factor


def get_bolt_2022_2023_ff_scale(desired_lateral_accel: float, desired_lateral_jerk: float, v_ego: float) -> float:
  if desired_lateral_accel == 0.0:
    return 1.0

  gain = _bolt_2022_2023_side_value(desired_lateral_accel, BOLT_2022_2023_FF_GAIN_LEFT, BOLT_2022_2023_FF_GAIN_RIGHT)
  abs_lateral_accel = abs(desired_lateral_accel)
  onset = _bolt_2022_2023_sigmoid((abs_lateral_accel - BOLT_2022_2023_FF_ONSET) / BOLT_2022_2023_FF_ONSET_WIDTH)
  cutoff = _bolt_2022_2023_sigmoid((BOLT_2022_2023_FF_CUTOFF - abs_lateral_accel) / BOLT_2022_2023_FF_CUTOFF_WIDTH)
  extra_scale = gain * onset * cutoff
  low_speed_factor = _bolt_2022_2023_low_speed_factor(v_ego)
  transition_envelope = _bolt_2022_2023_transition_envelope(v_ego, desired_lateral_accel, desired_lateral_jerk)
  phase = _bolt_2022_2023_transition_phase(desired_lateral_accel, desired_lateral_jerk)
  turn_in_weight = max(phase, 0.0)
  unwind_weight = max(-phase, 0.0)
  turn_in_boost = 1.0 + (_bolt_2022_2023_side_value(desired_lateral_accel, BOLT_2022_2023_TURN_IN_BOOST_LEFT, BOLT_2022_2023_TURN_IN_BOOST_RIGHT) *
                          turn_in_weight * low_speed_factor)
  unwind_envelope = (0.25 + 0.75 * low_speed_factor) * (1.0 + 0.45 * transition_envelope)
  unwind_taper = 1.0 - (_bolt_2022_2023_side_value(desired_lateral_accel, BOLT_2022_2023_UNWIND_TAPER_LEFT, BOLT_2022_2023_UNWIND_TAPER_RIGHT) *
                         unwind_weight * unwind_envelope)
  return 1.0 + (extra_scale * turn_in_boost * max(unwind_taper, 0.0))


def get_bolt_2022_2023_friction_threshold(v_ego: float, desired_lateral_accel: float = 0.0, desired_lateral_jerk: float = 0.0) -> float:
  base_threshold = get_friction_threshold(v_ego)
  transition_envelope = _bolt_2022_2023_transition_envelope(v_ego, desired_lateral_accel, desired_lateral_jerk)
  phase = _bolt_2022_2023_transition_phase(desired_lateral_accel, desired_lateral_jerk)
  turn_in_weight = max(phase, 0.0)
  unwind_weight = max(-phase, 0.0)
  threshold_scale = 1.0 - (_bolt_2022_2023_side_value(desired_lateral_accel, BOLT_2022_2023_TURN_IN_THRESHOLD_REDUCTION_LEFT, BOLT_2022_2023_TURN_IN_THRESHOLD_REDUCTION_RIGHT) *
                           transition_envelope * turn_in_weight)
  threshold_scale += (_bolt_2022_2023_side_value(desired_lateral_accel, BOLT_2022_2023_UNWIND_THRESHOLD_INCREASE_LEFT, BOLT_2022_2023_UNWIND_THRESHOLD_INCREASE_RIGHT) *
                      transition_envelope * unwind_weight)
  return base_threshold * min(max(threshold_scale, 0.84), 1.14)


def get_bolt_2022_2023_friction_scale(v_ego: float, desired_lateral_accel: float, desired_lateral_jerk: float) -> float:
  transition_envelope = _bolt_2022_2023_transition_envelope(v_ego, desired_lateral_accel, desired_lateral_jerk)
  phase = _bolt_2022_2023_transition_phase(desired_lateral_accel, desired_lateral_jerk)
  turn_in_weight = max(phase, 0.0)
  unwind_weight = max(-phase, 0.0)
  friction_scale = BOLT_2022_2023_FRICTION_MULT
  friction_scale += (_bolt_2022_2023_side_value(desired_lateral_accel, BOLT_2022_2023_TURN_IN_FRICTION_BOOST_LEFT, BOLT_2022_2023_TURN_IN_FRICTION_BOOST_RIGHT) *
                     transition_envelope * turn_in_weight)
  friction_scale -= (_bolt_2022_2023_side_value(desired_lateral_accel, BOLT_2022_2023_UNWIND_FRICTION_REDUCTION_LEFT, BOLT_2022_2023_UNWIND_FRICTION_REDUCTION_RIGHT) *
                     transition_envelope * unwind_weight)
  return min(max(friction_scale, 0.92), 1.22)


def volt_standard_lateral_testing_ground_active() -> bool:
  return testing_ground.use(VOLT_STANDARD_LATERAL_TESTING_GROUND_ID)


def _volt_standard_sigmoid(x: float) -> float:
  return _sigmoid(x)


def _volt_standard_low_speed_factor(v_ego: float) -> float:
  return 1.0 / (1.0 + (max(v_ego, 0.0) / VOLT_STANDARD_TRANSITION_SPEED) ** 2)


def _volt_standard_transition_phase(desired_lateral_accel: float, desired_lateral_jerk: float) -> float:
  return math.tanh((desired_lateral_accel * desired_lateral_jerk) / VOLT_STANDARD_PHASE_SCALE)


def _volt_standard_side_value(desired_lateral_accel: float, left_value: float, right_value: float) -> float:
  return left_value if desired_lateral_accel >= 0.0 else right_value


def _volt_standard_transition_envelope(v_ego: float, desired_lateral_accel: float, desired_lateral_jerk: float) -> float:
  lat_factor = 1.0 - math.exp(-abs(desired_lateral_accel) / VOLT_STANDARD_FRICTION_LAT_RISE)
  jerk_factor = 1.0 - math.exp(-abs(desired_lateral_jerk) / VOLT_STANDARD_FRICTION_JERK_RISE)
  return _volt_standard_low_speed_factor(v_ego) * lat_factor * jerk_factor


def get_volt_standard_ff_scale(desired_lateral_accel: float, desired_lateral_jerk: float, v_ego: float) -> float:
  if desired_lateral_accel == 0.0:
    return 1.0

  gain = _volt_standard_side_value(desired_lateral_accel, VOLT_STANDARD_FF_GAIN_LEFT, VOLT_STANDARD_FF_GAIN_RIGHT)
  abs_lateral_accel = abs(desired_lateral_accel)
  onset = _volt_standard_sigmoid((abs_lateral_accel - VOLT_STANDARD_FF_ONSET) / VOLT_STANDARD_FF_ONSET_WIDTH)
  cutoff = _volt_standard_sigmoid((VOLT_STANDARD_FF_CUTOFF - abs_lateral_accel) / VOLT_STANDARD_FF_CUTOFF_WIDTH)
  extra_scale = gain * onset * cutoff
  phase = _volt_standard_transition_phase(desired_lateral_accel, desired_lateral_jerk)
  turn_in_weight = max(phase, 0.0)
  unwind_weight = max(-phase, 0.0)
  low_speed_factor = _volt_standard_low_speed_factor(v_ego)
  turn_in_boost = 1.0 + (_volt_standard_side_value(desired_lateral_accel, VOLT_STANDARD_TURN_IN_BOOST_LEFT, VOLT_STANDARD_TURN_IN_BOOST_RIGHT) *
                          turn_in_weight * low_speed_factor)
  unwind_taper = 1.0 - (_volt_standard_side_value(desired_lateral_accel, VOLT_STANDARD_UNWIND_TAPER_LEFT, VOLT_STANDARD_UNWIND_TAPER_RIGHT) *
                         unwind_weight * (0.30 + 0.70 * low_speed_factor))
  return 1.0 + (extra_scale * turn_in_boost * max(unwind_taper, 0.0))


def get_volt_standard_friction_threshold(v_ego: float, desired_lateral_accel: float = 0.0, desired_lateral_jerk: float = 0.0) -> float:
  base_threshold = get_friction_threshold(v_ego)
  transition_envelope = _volt_standard_transition_envelope(v_ego, desired_lateral_accel, desired_lateral_jerk)
  phase = _volt_standard_transition_phase(desired_lateral_accel, desired_lateral_jerk)
  turn_in_weight = max(phase, 0.0)
  unwind_weight = max(-phase, 0.0)
  threshold_scale = 1.0 - (_volt_standard_side_value(desired_lateral_accel, VOLT_STANDARD_TURN_IN_THRESHOLD_REDUCTION_LEFT, VOLT_STANDARD_TURN_IN_THRESHOLD_REDUCTION_RIGHT) *
                           transition_envelope * turn_in_weight)
  threshold_scale += (_volt_standard_side_value(desired_lateral_accel, VOLT_STANDARD_UNWIND_THRESHOLD_INCREASE_LEFT, VOLT_STANDARD_UNWIND_THRESHOLD_INCREASE_RIGHT) *
                      transition_envelope * unwind_weight)
  return base_threshold * min(max(threshold_scale, 0.84), 1.12)


def get_volt_standard_friction_scale(v_ego: float, desired_lateral_accel: float, desired_lateral_jerk: float) -> float:
  transition_envelope = _volt_standard_transition_envelope(v_ego, desired_lateral_accel, desired_lateral_jerk)
  phase = _volt_standard_transition_phase(desired_lateral_accel, desired_lateral_jerk)
  turn_in_weight = max(phase, 0.0)
  unwind_weight = max(-phase, 0.0)
  friction_scale = VOLT_STANDARD_FRICTION_MULT
  friction_scale += (_volt_standard_side_value(desired_lateral_accel, VOLT_STANDARD_TURN_IN_FRICTION_BOOST_LEFT, VOLT_STANDARD_TURN_IN_FRICTION_BOOST_RIGHT) *
                     transition_envelope * turn_in_weight)
  friction_scale -= (_volt_standard_side_value(desired_lateral_accel, VOLT_STANDARD_UNWIND_FRICTION_REDUCTION_LEFT, VOLT_STANDARD_UNWIND_FRICTION_REDUCTION_RIGHT) *
                     transition_envelope * unwind_weight)
  return min(max(friction_scale, 0.90), 1.14)


def get_volt_standard_center_taper_scale(desired_lateral_accel: float, v_ego: float) -> float:
  speed_weight = _volt_standard_sigmoid((v_ego - VOLT_STANDARD_CENTER_TAPER_SPEED) / VOLT_STANDARD_CENTER_TAPER_SPEED_WIDTH)
  center_weight = _volt_standard_sigmoid((VOLT_STANDARD_CENTER_TAPER_LAT - abs(desired_lateral_accel)) / VOLT_STANDARD_CENTER_TAPER_LAT_WIDTH)
  reduction = VOLT_STANDARD_CENTER_TAPER_MAX * speed_weight * center_weight
  return 1.0 - reduction


def genesis_g90_lateral_testing_ground_active() -> bool:
  return testing_ground.use(GENESIS_G90_LATERAL_TESTING_GROUND_ID)


def _genesis_g90_sigmoid(x: float) -> float:
  return _sigmoid(x)


def _genesis_g90_low_speed_factor(v_ego: float) -> float:
  return 1.0 / (1.0 + (max(v_ego, 0.0) / GENESIS_G90_TRANSITION_SPEED) ** 2)


def _genesis_g90_transition_phase(desired_lateral_accel: float, desired_lateral_jerk: float) -> float:
  return math.tanh((desired_lateral_accel * desired_lateral_jerk) / GENESIS_G90_PHASE_SCALE)


def _genesis_g90_side_value(desired_lateral_accel: float, left_value: float, right_value: float) -> float:
  return left_value if desired_lateral_accel >= 0.0 else right_value


def _genesis_g90_transition_envelope(v_ego: float, desired_lateral_accel: float, desired_lateral_jerk: float) -> float:
  lat_factor = 1.0 - math.exp(-abs(desired_lateral_accel) / GENESIS_G90_FRICTION_LAT_RISE)
  jerk_factor = 1.0 - math.exp(-abs(desired_lateral_jerk) / GENESIS_G90_FRICTION_JERK_RISE)
  return _genesis_g90_low_speed_factor(v_ego) * lat_factor * jerk_factor


def get_genesis_g90_ff_scale(desired_lateral_accel: float, desired_lateral_jerk: float, v_ego: float) -> float:
  if desired_lateral_accel == 0.0:
    return 1.0

  gain = _genesis_g90_side_value(desired_lateral_accel, GENESIS_G90_FF_GAIN_LEFT, GENESIS_G90_FF_GAIN_RIGHT)
  abs_lateral_accel = abs(desired_lateral_accel)
  onset = _genesis_g90_sigmoid((abs_lateral_accel - GENESIS_G90_FF_ONSET) / GENESIS_G90_FF_ONSET_WIDTH)
  cutoff = _genesis_g90_sigmoid((GENESIS_G90_FF_CUTOFF - abs_lateral_accel) / GENESIS_G90_FF_CUTOFF_WIDTH)
  extra_scale = gain * onset * cutoff
  phase = _genesis_g90_transition_phase(desired_lateral_accel, desired_lateral_jerk)
  turn_in_weight = max(phase, 0.0)
  unwind_weight = max(-phase, 0.0)
  low_speed_factor = _genesis_g90_low_speed_factor(v_ego)
  turn_in_boost = 1.0 + (_genesis_g90_side_value(desired_lateral_accel, GENESIS_G90_TURN_IN_BOOST_LEFT, GENESIS_G90_TURN_IN_BOOST_RIGHT) *
                          turn_in_weight * (0.35 + 0.65 * low_speed_factor))
  unwind_taper = 1.0 - (_genesis_g90_side_value(desired_lateral_accel, GENESIS_G90_UNWIND_TAPER_LEFT, GENESIS_G90_UNWIND_TAPER_RIGHT) *
                         unwind_weight * (0.30 + 0.70 * low_speed_factor))
  return 1.0 + (extra_scale * turn_in_boost * max(unwind_taper, 0.0))


def get_genesis_g90_friction_threshold(v_ego: float, desired_lateral_accel: float = 0.0, desired_lateral_jerk: float = 0.0) -> float:
  base_threshold = get_friction_threshold(v_ego)
  transition_envelope = _genesis_g90_transition_envelope(v_ego, desired_lateral_accel, desired_lateral_jerk)
  phase = _genesis_g90_transition_phase(desired_lateral_accel, desired_lateral_jerk)
  turn_in_weight = max(phase, 0.0)
  unwind_weight = max(-phase, 0.0)
  threshold_scale = 1.0 - (_genesis_g90_side_value(desired_lateral_accel, GENESIS_G90_TURN_IN_THRESHOLD_REDUCTION_LEFT, GENESIS_G90_TURN_IN_THRESHOLD_REDUCTION_RIGHT) *
                           transition_envelope * turn_in_weight)
  threshold_scale += (_genesis_g90_side_value(desired_lateral_accel, GENESIS_G90_UNWIND_THRESHOLD_INCREASE_LEFT, GENESIS_G90_UNWIND_THRESHOLD_INCREASE_RIGHT) *
                      transition_envelope * unwind_weight)
  return base_threshold * min(max(threshold_scale, 0.86), 1.12)


def get_genesis_g90_friction_scale(v_ego: float, desired_lateral_accel: float, desired_lateral_jerk: float) -> float:
  transition_envelope = _genesis_g90_transition_envelope(v_ego, desired_lateral_accel, desired_lateral_jerk)
  phase = _genesis_g90_transition_phase(desired_lateral_accel, desired_lateral_jerk)
  turn_in_weight = max(phase, 0.0)
  unwind_weight = max(-phase, 0.0)
  friction_scale = GENESIS_G90_FRICTION_MULT
  friction_scale += (_genesis_g90_side_value(desired_lateral_accel, GENESIS_G90_TURN_IN_FRICTION_BOOST_LEFT, GENESIS_G90_TURN_IN_FRICTION_BOOST_RIGHT) *
                     transition_envelope * turn_in_weight)
  friction_scale -= (_genesis_g90_side_value(desired_lateral_accel, GENESIS_G90_UNWIND_FRICTION_REDUCTION_LEFT, GENESIS_G90_UNWIND_FRICTION_REDUCTION_RIGHT) *
                     transition_envelope * unwind_weight)
  return min(max(friction_scale, 0.92), 1.12)


def _ioniq_6_sigmoid(x: float) -> float:
  return _sigmoid(x)


def _ioniq_6_low_speed_factor(v_ego: float) -> float:
  return 1.0 / (1.0 + (max(v_ego, 0.0) / IONIQ_6_TRANSITION_SPEED) ** 2)


def _ioniq_6_transition_phase(desired_lateral_accel: float, desired_lateral_jerk: float) -> float:
  return math.tanh((desired_lateral_accel * desired_lateral_jerk) / IONIQ_6_PHASE_SCALE)


def _ioniq_6_side_value(desired_lateral_accel: float, left_value: float, right_value: float) -> float:
  return left_value if desired_lateral_accel >= 0.0 else right_value


def _ioniq_6_transition_envelope(v_ego: float, desired_lateral_accel: float, desired_lateral_jerk: float) -> float:
  lat_factor = 1.0 - math.exp(-abs(desired_lateral_accel) / IONIQ_6_FRICTION_LAT_RISE)
  jerk_factor = 1.0 - math.exp(-abs(desired_lateral_jerk) / IONIQ_6_FRICTION_JERK_RISE)
  return _ioniq_6_low_speed_factor(v_ego) * lat_factor * jerk_factor


def get_ioniq_6_ff_scale(desired_lateral_accel: float, desired_lateral_jerk: float, v_ego: float) -> float:
  if desired_lateral_accel == 0.0:
    return 1.0

  gain = _ioniq_6_side_value(desired_lateral_accel, IONIQ_6_FF_GAIN_LEFT, IONIQ_6_FF_GAIN_RIGHT)
  abs_lateral_accel = abs(desired_lateral_accel)
  onset = _ioniq_6_sigmoid((abs_lateral_accel - IONIQ_6_FF_ONSET) / IONIQ_6_FF_ONSET_WIDTH)
  cutoff = _ioniq_6_sigmoid((IONIQ_6_FF_CUTOFF - abs_lateral_accel) / IONIQ_6_FF_CUTOFF_WIDTH)
  extra_scale = gain * onset * cutoff
  phase = _ioniq_6_transition_phase(desired_lateral_accel, desired_lateral_jerk)
  turn_in_weight = max(phase, 0.0)
  unwind_weight = max(-phase, 0.0)
  low_speed_factor = _ioniq_6_low_speed_factor(v_ego)
  turn_in_boost = 1.0 + (_ioniq_6_side_value(desired_lateral_accel, IONIQ_6_TURN_IN_BOOST_LEFT, IONIQ_6_TURN_IN_BOOST_RIGHT) *
                          turn_in_weight * low_speed_factor)
  unwind_taper = 1.0 - (_ioniq_6_side_value(desired_lateral_accel, IONIQ_6_UNWIND_TAPER_LEFT, IONIQ_6_UNWIND_TAPER_RIGHT) *
                         unwind_weight * (0.30 + 0.70 * low_speed_factor))
  return (1.0 + (extra_scale * turn_in_boost * max(unwind_taper, 0.0))) * get_ioniq_6_directional_taper_scale(desired_lateral_accel, desired_lateral_jerk)


def get_ioniq_6_friction_threshold(v_ego: float, desired_lateral_accel: float = 0.0, desired_lateral_jerk: float = 0.0) -> float:
  base_threshold = max(get_friction_threshold(v_ego), IONIQ_6_BASE_FRICTION_THRESHOLD)
  transition_envelope = _ioniq_6_transition_envelope(v_ego, desired_lateral_accel, desired_lateral_jerk)
  phase = _ioniq_6_transition_phase(desired_lateral_accel, desired_lateral_jerk)
  turn_in_weight = max(phase, 0.0)
  unwind_weight = max(-phase, 0.0)
  threshold_scale = 1.0 - (_ioniq_6_side_value(desired_lateral_accel, IONIQ_6_TURN_IN_THRESHOLD_REDUCTION_LEFT, IONIQ_6_TURN_IN_THRESHOLD_REDUCTION_RIGHT) *
                           transition_envelope * turn_in_weight)
  threshold_scale += (_ioniq_6_side_value(desired_lateral_accel, IONIQ_6_UNWIND_THRESHOLD_INCREASE_LEFT, IONIQ_6_UNWIND_THRESHOLD_INCREASE_RIGHT) *
                      transition_envelope * unwind_weight)
  return base_threshold * min(max(threshold_scale, 0.82), 1.18)


def get_ioniq_6_friction_scale(v_ego: float, desired_lateral_accel: float, desired_lateral_jerk: float) -> float:
  transition_envelope = _ioniq_6_transition_envelope(v_ego, desired_lateral_accel, desired_lateral_jerk)
  phase = _ioniq_6_transition_phase(desired_lateral_accel, desired_lateral_jerk)
  turn_in_weight = max(phase, 0.0)
  unwind_weight = max(-phase, 0.0)
  friction_scale = IONIQ_6_FRICTION_MULT
  friction_scale += (_ioniq_6_side_value(desired_lateral_accel, IONIQ_6_TURN_IN_FRICTION_BOOST_LEFT, IONIQ_6_TURN_IN_FRICTION_BOOST_RIGHT) *
                     transition_envelope * turn_in_weight)
  friction_scale -= (_ioniq_6_side_value(desired_lateral_accel, IONIQ_6_UNWIND_FRICTION_REDUCTION_LEFT, IONIQ_6_UNWIND_FRICTION_REDUCTION_RIGHT) *
                     transition_envelope * unwind_weight)
  return min(max(friction_scale, 0.82), 1.08)


def get_ioniq_6_center_taper_scale(desired_lateral_accel: float, v_ego: float) -> float:
  speed_weight = _ioniq_6_sigmoid((v_ego - IONIQ_6_CENTER_TAPER_SPEED) / IONIQ_6_CENTER_TAPER_SPEED_WIDTH)
  center_weight = _ioniq_6_sigmoid((IONIQ_6_CENTER_TAPER_LAT - abs(desired_lateral_accel)) / IONIQ_6_CENTER_TAPER_LAT_WIDTH)
  high_speed_reduction = IONIQ_6_CENTER_TAPER_MAX * speed_weight * center_weight

  low_mid_onset = _ioniq_6_sigmoid((v_ego - IONIQ_6_LOW_MID_CENTER_TAPER_SPEED_MIN) / IONIQ_6_LOW_MID_CENTER_TAPER_SPEED_WIDTH)
  low_mid_cutoff = _ioniq_6_sigmoid((IONIQ_6_LOW_MID_CENTER_TAPER_SPEED_MAX - v_ego) / IONIQ_6_LOW_MID_CENTER_TAPER_SPEED_WIDTH)
  low_mid_speed_weight = low_mid_onset * low_mid_cutoff
  low_mid_center_weight = _ioniq_6_sigmoid((IONIQ_6_LOW_MID_CENTER_TAPER_LAT - abs(desired_lateral_accel)) /
                                           IONIQ_6_LOW_MID_CENTER_TAPER_LAT_WIDTH)
  low_mid_reduction = IONIQ_6_LOW_MID_CENTER_TAPER_MAX * low_mid_speed_weight * low_mid_center_weight

  return 1.0 - min(high_speed_reduction + low_mid_reduction, 0.12)


def get_ioniq_6_directional_taper_scale(desired_lateral_accel: float, desired_lateral_jerk: float) -> float:
  if desired_lateral_accel == 0.0:
    return 1.0

  abs_lateral_accel = abs(desired_lateral_accel)
  onset = _ioniq_6_sigmoid((abs_lateral_accel - IONIQ_6_DIRECTIONAL_TAPER_LAT_START) / IONIQ_6_DIRECTIONAL_TAPER_LAT_WIDTH)
  cutoff = _ioniq_6_sigmoid((IONIQ_6_DIRECTIONAL_TAPER_LAT_END - abs_lateral_accel) / IONIQ_6_DIRECTIONAL_TAPER_LAT_WIDTH)
  band_weight = onset * cutoff
  phase = _ioniq_6_transition_phase(desired_lateral_accel, desired_lateral_jerk)
  unwind_weight = max(-phase, 0.0)
  base_reduction = _ioniq_6_side_value(desired_lateral_accel, IONIQ_6_DIRECTIONAL_TAPER_BASE_LEFT, IONIQ_6_DIRECTIONAL_TAPER_BASE_RIGHT)
  unwind_reduction = _ioniq_6_side_value(desired_lateral_accel, IONIQ_6_DIRECTIONAL_TAPER_UNWIND_LEFT, IONIQ_6_DIRECTIONAL_TAPER_UNWIND_RIGHT)
  reduction = band_weight * (base_reduction + unwind_reduction * unwind_weight)
  floor = _ioniq_6_side_value(desired_lateral_accel, IONIQ_6_DIRECTIONAL_TAPER_FLOOR_LEFT, IONIQ_6_DIRECTIONAL_TAPER_FLOOR_RIGHT)
  floor -= _ioniq_6_side_value(desired_lateral_accel, IONIQ_6_DIRECTIONAL_TAPER_UNWIND_FLOOR_LEFT, IONIQ_6_DIRECTIONAL_TAPER_UNWIND_FLOOR_RIGHT) * unwind_weight
  return max(1.0 - reduction, floor)


def get_ioniq_6_output_taper_scale(desired_lateral_accel: float, desired_lateral_jerk: float, v_ego: float) -> float:
  speed_weight = _ioniq_6_sigmoid((v_ego - IONIQ_6_OUTPUT_TAPER_SPEED) / IONIQ_6_OUTPUT_TAPER_SPEED_WIDTH)
  center_taper = get_ioniq_6_center_taper_scale(desired_lateral_accel, v_ego)
  directional_taper = get_ioniq_6_directional_taper_scale(desired_lateral_accel, desired_lateral_jerk)
  center_scale = 1.0 - ((1.0 - center_taper) * IONIQ_6_OUTPUT_CENTER_TAPER_BLEND * speed_weight)
  directional_scale = 1.0 - ((1.0 - directional_taper) * IONIQ_6_OUTPUT_DIRECTIONAL_TAPER_BLEND * speed_weight)
  return center_scale * directional_scale


def kia_ev6_lateral_testing_ground_active() -> bool:
  return testing_ground.use(KIA_EV6_LATERAL_TESTING_GROUND_ID, KIA_EV6_LATERAL_TESTING_GROUND_VARIANT)


def _kia_ev6_sigmoid(x: float) -> float:
  return _sigmoid(x)


def _kia_ev6_low_speed_factor(v_ego: float) -> float:
  return 1.0 / (1.0 + (max(v_ego, 0.0) / KIA_EV6_TRANSITION_SPEED) ** 2)


def _kia_ev6_transition_phase(desired_lateral_accel: float, desired_lateral_jerk: float) -> float:
  return math.tanh((desired_lateral_accel * desired_lateral_jerk) / KIA_EV6_PHASE_SCALE)


def _kia_ev6_side_value(desired_lateral_accel: float, left_value: float, right_value: float) -> float:
  return left_value if desired_lateral_accel >= 0.0 else right_value


def _kia_ev6_transition_envelope(v_ego: float, desired_lateral_accel: float, desired_lateral_jerk: float) -> float:
  lat_factor = 1.0 - math.exp(-abs(desired_lateral_accel) / KIA_EV6_FRICTION_LAT_RISE)
  jerk_factor = 1.0 - math.exp(-abs(desired_lateral_jerk) / KIA_EV6_FRICTION_JERK_RISE)
  return _kia_ev6_low_speed_factor(v_ego) * lat_factor * jerk_factor


def get_kia_ev6_ff_scale(desired_lateral_accel: float, desired_lateral_jerk: float, v_ego: float) -> float:
  if desired_lateral_accel == 0.0:
    return 1.0

  gain = _kia_ev6_side_value(desired_lateral_accel, KIA_EV6_FF_GAIN_LEFT, KIA_EV6_FF_GAIN_RIGHT)
  abs_lateral_accel = abs(desired_lateral_accel)
  onset = _kia_ev6_sigmoid((abs_lateral_accel - KIA_EV6_FF_ONSET) / KIA_EV6_FF_ONSET_WIDTH)
  cutoff = _kia_ev6_sigmoid((KIA_EV6_FF_CUTOFF - abs_lateral_accel) / KIA_EV6_FF_CUTOFF_WIDTH)
  extra_scale = gain * onset * cutoff
  phase = _kia_ev6_transition_phase(desired_lateral_accel, desired_lateral_jerk)
  turn_in_weight = max(phase, 0.0)
  unwind_weight = max(-phase, 0.0)
  low_speed_factor = _kia_ev6_low_speed_factor(v_ego)
  turn_in_boost = 1.0 + (_kia_ev6_side_value(desired_lateral_accel, KIA_EV6_TURN_IN_BOOST_LEFT, KIA_EV6_TURN_IN_BOOST_RIGHT) *
                          turn_in_weight * (0.35 + 0.65 * low_speed_factor))
  unwind_taper = 1.0 - (_kia_ev6_side_value(desired_lateral_accel, KIA_EV6_UNWIND_TAPER_LEFT, KIA_EV6_UNWIND_TAPER_RIGHT) *
                         unwind_weight * (0.35 + 0.65 * low_speed_factor))
  return 1.0 + (extra_scale * turn_in_boost * max(unwind_taper, 0.0))


def get_kia_ev6_friction_threshold(v_ego: float, desired_lateral_accel: float = 0.0, desired_lateral_jerk: float = 0.0) -> float:
  base_threshold = get_friction_threshold(v_ego)
  transition_envelope = _kia_ev6_transition_envelope(v_ego, desired_lateral_accel, desired_lateral_jerk)
  phase = _kia_ev6_transition_phase(desired_lateral_accel, desired_lateral_jerk)
  turn_in_weight = max(phase, 0.0)
  unwind_weight = max(-phase, 0.0)
  threshold_scale = 1.0 - (_kia_ev6_side_value(desired_lateral_accel, KIA_EV6_TURN_IN_THRESHOLD_REDUCTION_LEFT, KIA_EV6_TURN_IN_THRESHOLD_REDUCTION_RIGHT) *
                           transition_envelope * turn_in_weight)
  threshold_scale += (_kia_ev6_side_value(desired_lateral_accel, KIA_EV6_UNWIND_THRESHOLD_INCREASE_LEFT, KIA_EV6_UNWIND_THRESHOLD_INCREASE_RIGHT) *
                      transition_envelope * unwind_weight)
  return base_threshold * min(max(threshold_scale, 0.82), 1.16)


def get_kia_ev6_friction_scale(v_ego: float, desired_lateral_accel: float, desired_lateral_jerk: float) -> float:
  transition_envelope = _kia_ev6_transition_envelope(v_ego, desired_lateral_accel, desired_lateral_jerk)
  phase = _kia_ev6_transition_phase(desired_lateral_accel, desired_lateral_jerk)
  turn_in_weight = max(phase, 0.0)
  unwind_weight = max(-phase, 0.0)
  friction_scale = KIA_EV6_FRICTION_MULT
  friction_scale += (_kia_ev6_side_value(desired_lateral_accel, KIA_EV6_TURN_IN_FRICTION_BOOST_LEFT, KIA_EV6_TURN_IN_FRICTION_BOOST_RIGHT) *
                     transition_envelope * turn_in_weight)
  friction_scale -= (_kia_ev6_side_value(desired_lateral_accel, KIA_EV6_UNWIND_FRICTION_REDUCTION_LEFT, KIA_EV6_UNWIND_FRICTION_REDUCTION_RIGHT) *
                     transition_envelope * unwind_weight)
  return min(max(friction_scale, 0.90), 1.10)


def volt_plexy_lateral_testing_ground_active() -> bool:
  return testing_ground.use(VOLT_PLEXY_LATERAL_TESTING_GROUND_ID)


def _volt_plexy_sigmoid(x: float) -> float:
  return _sigmoid(x)


def _volt_plexy_low_speed_factor(v_ego: float) -> float:
  return 1.0 / (1.0 + (max(v_ego, 0.0) / VOLT_PLEXY_TRANSITION_SPEED) ** 2)


def _volt_plexy_transition_phase(desired_lateral_accel: float, desired_lateral_jerk: float) -> float:
  return math.tanh((desired_lateral_accel * desired_lateral_jerk) / VOLT_PLEXY_PHASE_SCALE)


def _volt_plexy_side_value(desired_lateral_accel: float, left_value: float, right_value: float) -> float:
  return left_value if desired_lateral_accel >= 0.0 else right_value


def _volt_plexy_transition_envelope(v_ego: float, desired_lateral_accel: float, desired_lateral_jerk: float) -> float:
  lat_factor = 1.0 - math.exp(-abs(desired_lateral_accel) / VOLT_PLEXY_FRICTION_LAT_RISE)
  jerk_factor = 1.0 - math.exp(-abs(desired_lateral_jerk) / VOLT_PLEXY_FRICTION_JERK_RISE)
  return _volt_plexy_low_speed_factor(v_ego) * lat_factor * jerk_factor


def get_volt_plexy_ff_scale(desired_lateral_accel: float, desired_lateral_jerk: float, v_ego: float) -> float:
  if desired_lateral_accel == 0.0:
    return 1.0

  gain = _volt_plexy_side_value(desired_lateral_accel, VOLT_PLEXY_FF_GAIN_LEFT, VOLT_PLEXY_FF_GAIN_RIGHT)
  abs_lateral_accel = abs(desired_lateral_accel)
  onset = _volt_plexy_sigmoid((abs_lateral_accel - VOLT_PLEXY_FF_ONSET) / VOLT_PLEXY_FF_ONSET_WIDTH)
  cutoff = _volt_plexy_sigmoid((VOLT_PLEXY_FF_CUTOFF - abs_lateral_accel) / VOLT_PLEXY_FF_CUTOFF_WIDTH)
  extra_scale = gain * onset * cutoff
  phase = _volt_plexy_transition_phase(desired_lateral_accel, desired_lateral_jerk)
  turn_in_weight = max(phase, 0.0)
  unwind_weight = max(-phase, 0.0)
  low_speed_factor = _volt_plexy_low_speed_factor(v_ego)
  turn_in_boost = 1.0 + (_volt_plexy_side_value(desired_lateral_accel, VOLT_PLEXY_TURN_IN_BOOST_LEFT, VOLT_PLEXY_TURN_IN_BOOST_RIGHT) *
                          turn_in_weight * low_speed_factor)
  unwind_taper = 1.0 - (_volt_plexy_side_value(desired_lateral_accel, VOLT_PLEXY_UNWIND_TAPER_LEFT, VOLT_PLEXY_UNWIND_TAPER_RIGHT) *
                         unwind_weight * (0.35 + 0.65 * low_speed_factor))
  return 1.0 + (extra_scale * turn_in_boost * max(unwind_taper, 0.0))


def get_volt_plexy_friction_threshold(v_ego: float, desired_lateral_accel: float = 0.0, desired_lateral_jerk: float = 0.0) -> float:
  base_threshold = get_friction_threshold(v_ego)
  transition_envelope = _volt_plexy_transition_envelope(v_ego, desired_lateral_accel, desired_lateral_jerk)
  phase = _volt_plexy_transition_phase(desired_lateral_accel, desired_lateral_jerk)
  turn_in_weight = max(phase, 0.0)
  unwind_weight = max(-phase, 0.0)
  threshold_scale = 1.0 - (_volt_plexy_side_value(desired_lateral_accel, VOLT_PLEXY_TURN_IN_THRESHOLD_REDUCTION_LEFT, VOLT_PLEXY_TURN_IN_THRESHOLD_REDUCTION_RIGHT) *
                           transition_envelope * turn_in_weight)
  threshold_scale += (_volt_plexy_side_value(desired_lateral_accel, VOLT_PLEXY_UNWIND_THRESHOLD_INCREASE_LEFT, VOLT_PLEXY_UNWIND_THRESHOLD_INCREASE_RIGHT) *
                      transition_envelope * unwind_weight)
  return base_threshold * min(max(threshold_scale, 0.84), 1.14)


def get_volt_plexy_friction_scale(v_ego: float, desired_lateral_accel: float, desired_lateral_jerk: float) -> float:
  transition_envelope = _volt_plexy_transition_envelope(v_ego, desired_lateral_accel, desired_lateral_jerk)
  phase = _volt_plexy_transition_phase(desired_lateral_accel, desired_lateral_jerk)
  turn_in_weight = max(phase, 0.0)
  unwind_weight = max(-phase, 0.0)
  friction_scale = VOLT_PLEXY_FRICTION_MULT
  friction_scale += (_volt_plexy_side_value(desired_lateral_accel, VOLT_PLEXY_TURN_IN_FRICTION_BOOST_LEFT, VOLT_PLEXY_TURN_IN_FRICTION_BOOST_RIGHT) *
                     transition_envelope * turn_in_weight)
  friction_scale -= (_volt_plexy_side_value(desired_lateral_accel, VOLT_PLEXY_UNWIND_FRICTION_REDUCTION_LEFT, VOLT_PLEXY_UNWIND_FRICTION_REDUCTION_RIGHT) *
                     transition_envelope * unwind_weight)
  return min(max(friction_scale, 0.90), 1.12)


class LatControlTorque(LatControl):
  def __init__(self, CP, CI, dt):
    super().__init__(CP, CI, dt)
    self.torque_params = CP.lateralTuning.torque.as_builder()
    self.torque_from_lateral_accel = CI.torque_from_lateral_accel()
    self.lateral_accel_from_torque = CI.lateral_accel_from_torque()
    self.pid = PIDController([INTERP_SPEEDS, KP_INTERP], KI, rate=1/self.dt)
    self.update_limits()
    self.steering_angle_deadzone_deg = self.torque_params.steeringAngleDeadzoneDeg
    self.lat_accel_request_buffer_len = int(LAT_ACCEL_REQUEST_BUFFER_SECONDS / self.dt)
    self.lat_accel_request_buffer = deque([0.] * self.lat_accel_request_buffer_len, maxlen=self.lat_accel_request_buffer_len)
    self.lookahead_frames = int(JERK_LOOKAHEAD_SECONDS / self.dt)
    self.jerk_filter = FirstOrderFilter(0.0, 1 / (2 * np.pi * LP_FILTER_CUTOFF_HZ), self.dt)
    self.previous_measurement = 0.0
    self.measurement_rate_filter = FirstOrderFilter(0.0, 1 / (2 * np.pi * (MAX_LAT_JERK_UP - 0.5)), self.dt)
    self.low_speed_reset_threshold = max(CP.minSteerSpeed, MIN_LATERAL_CONTROL_SPEED)
    self.steer_release_i_decay = 0.8
    self.prev_steering_pressed = False
    self.debug_counter = 0
    self.prev_desired_lateral_accel = 0.0

    self.is_bolt = CP.carFingerprint in BOLT_CARS
    self.is_bolt_2022_2023 = CP.carFingerprint in BOLT_2022_2023_CARS
    self.is_bolt_2018_2021 = CP.carFingerprint in BOLT_2018_2021_CARS
    self.is_bolt_2017 = CP.carFingerprint in BOLT_2017_CARS
    self.is_volt_standard = CP.carFingerprint in VOLT_STANDARD_CARS
    self.is_genesis_g90 = CP.carFingerprint in GENESIS_G90_CARS
    self.is_ioniq_6 = CP.carFingerprint in IONIQ_6_CARS
    self.is_kia_ev6 = CP.carFingerprint in KIA_EV6_CARS
    self.is_civic_bosch_modified = CP.carFingerprint == HONDA_CAR.HONDA_CIVIC_BOSCH and bool(CP.flags & HondaFlags.EPS_MODIFIED)
    self.is_volt_cc = CP.carFingerprint == GM_CAR.CHEVROLET_VOLT_CC
    self.is_silverado = CP.carFingerprint == GM_CAR.CHEVROLET_SILVERADO
    self.use_bolt_ff_scaling = self.is_bolt_2022_2023 or self.is_bolt_2018_2021 or self.is_bolt_2017
    self.use_bolt_ki_multiplier = self.use_bolt_ff_scaling
    self.torque_ff_scale_pos = 1.0
    self.torque_ff_scale_neg = 1.0
    self.torque_deadzone_boost = float(getattr(self.torque_params, "kfDEPRECATED", 0.0))
    self.torque_ki_mult = 1.0
    if self.is_ioniq_6:
      self.torque_params.latAccelFactor *= IONIQ_6_BASE_LAT_ACCEL_FACTOR_MULT
    if self.is_bolt:
      kp_scale = getattr(self.torque_params, "kp", getattr(self.torque_params, "kpDEPRECATED", 1.0))
      ki_scale = getattr(self.torque_params, "ki", getattr(self.torque_params, "kiDEPRECATED", 1.0))
      kd_scale = getattr(self.torque_params, "kd", getattr(self.torque_params, "kdDEPRECATED", 1.0))
      self.torque_ff_scale_pos = float(kp_scale)
      self.torque_ff_scale_neg = float(ki_scale)
      self.torque_ki_mult = float(kd_scale)
      if self.use_bolt_ki_multiplier and self.torque_ki_mult > 0.0 and self.torque_ki_mult != 1.0:
        self.pid._k_i = [self.pid._k_i[0], [k * self.torque_ki_mult for k in self.pid._k_i[1]]]

  def update_live_torque_params(self, latAccelFactor, latAccelOffset, friction):
    if self.is_ioniq_6:
      latAccelFactor *= IONIQ_6_BASE_LAT_ACCEL_FACTOR_MULT
    self.torque_params.latAccelFactor = latAccelFactor
    self.torque_params.latAccelOffset = latAccelOffset
    self.torque_params.friction = friction
    self.update_limits()

  def update_limits(self):
    self.pid.set_limits(self.lateral_accel_from_torque(self.steer_max, self.torque_params),
                        self.lateral_accel_from_torque(-self.steer_max, self.torque_params))

  def update(self, active, CS, VM, params, steer_limited_by_safety, desired_curvature, curvature_limited, lat_delay, calibrated_pose, model_data, starpilot_toggles):
    pid_log = log.ControlsState.LateralTorqueState.new_message()
    pid_log.version = VERSION
    if not active:
      output_torque = 0.0
      pid_log.active = False
      self.pid.reset()
      self.previous_measurement = 0.0
      self.measurement_rate_filter.x = 0.0
      self.lat_accel_request_buffer = deque([0.] * self.lat_accel_request_buffer_len, maxlen=self.lat_accel_request_buffer_len)
      self.prev_desired_lateral_accel = 0.0
    else:
      if self.prev_steering_pressed and not CS.steeringPressed:
        self.pid.i *= self.steer_release_i_decay

      measured_curvature = -VM.calc_curvature(math.radians(CS.steeringAngleDeg - params.angleOffsetDeg), CS.vEgo, params.roll)
      roll_compensation = params.roll * ACCELERATION_DUE_TO_GRAVITY
      curvature_deadzone = abs(VM.calc_curvature(math.radians(self.steering_angle_deadzone_deg), CS.vEgo, 0.0))
      lateral_accel_deadzone = curvature_deadzone * CS.vEgo ** 2

      delay_frames = int(np.clip(lat_delay / self.dt, 1, self.lat_accel_request_buffer_len))
      expected_lateral_accel = self.lat_accel_request_buffer[-delay_frames]
      future_desired_lateral_accel = desired_curvature * CS.vEgo ** 2
      self.lat_accel_request_buffer.append(future_desired_lateral_accel)
      raw_lateral_jerk = (future_desired_lateral_accel - expected_lateral_accel) / max(lat_delay, self.dt)
      raw_lateral_jerk = np.clip(raw_lateral_jerk, -MAX_LAT_JERK_UP, MAX_LAT_JERK_UP)
      desired_lateral_jerk = np.clip(self.jerk_filter.update(raw_lateral_jerk), -MAX_LAT_JERK_UP, MAX_LAT_JERK_UP)
      gravity_adjusted_future_lateral_accel = future_desired_lateral_accel - roll_compensation
      setpoint = expected_lateral_accel + desired_lateral_jerk * lat_delay
      desired_lateral_accel_rate = (setpoint - self.prev_desired_lateral_accel) / self.dt
      unwind_detected = (desired_lateral_accel_rate < UNWIND_D_DES_THRESHOLD and
                         abs(setpoint) < UNWIND_LAT_ACCEL_NEAR_ZERO)
      self.prev_desired_lateral_accel = setpoint

      measurement = measured_curvature * CS.vEgo ** 2
      measurement_rate = self.measurement_rate_filter.update((measurement - self.previous_measurement) / self.dt)
      measurement_rate = np.clip(measurement_rate, -MAX_LAT_JERK_UP, MAX_LAT_JERK_UP)
      self.previous_measurement = measurement

      low_speed_factor = (np.interp(CS.vEgo, LOW_SPEED_X, LOW_SPEED_Y) / max(CS.vEgo, MIN_SPEED)) ** 2
      current_kp = np.interp(CS.vEgo, self.pid._k_p[0], self.pid._k_p[1])
      error = setpoint - measurement
      error_with_lsf = error * (1 + low_speed_factor / max(current_kp, 1e-3))

      # do error correction in lateral acceleration space, convert at end to handle non-linear torque responses correctly
      pid_log.error = float(error_with_lsf)
      ff = gravity_adjusted_future_lateral_accel
      # latAccelOffset corrects roll compensation bias from device roll misalignment relative to car roll
      ff -= self.torque_params.latAccelOffset
      ff_scale = 1.0
      if self.use_bolt_ff_scaling:
        ff_scale = np.interp(ff, [-FF_SCALE_BLEND_LAT_ACCEL, 0.0, FF_SCALE_BLEND_LAT_ACCEL],
                             [self.torque_ff_scale_neg, 1.0, self.torque_ff_scale_pos])
      ff *= ff_scale
      bolt_2022_2023_tuned_path_active = self.is_bolt_2022_2023
      bolt_2018_2021_tuned_path_active = self.is_bolt_2018_2021
      volt_standard_test_active = self.is_volt_standard and volt_standard_lateral_testing_ground_active()
      genesis_g90_test_active = self.is_genesis_g90 and genesis_g90_lateral_testing_ground_active()
      ioniq_6_active = self.is_ioniq_6
      kia_ev6_test_active = self.is_kia_ev6 and kia_ev6_lateral_testing_ground_active()
      volt_plexy_test_active = self.is_volt_cc and volt_plexy_lateral_testing_ground_active()
      volt_standard_center_taper = get_volt_standard_center_taper_scale(setpoint, CS.vEgo) if volt_standard_test_active else 1.0
      ioniq_6_center_taper = get_ioniq_6_center_taper_scale(setpoint, CS.vEgo) if ioniq_6_active else 1.0
      friction_threshold = get_friction_threshold(CS.vEgo)
      friction_scale = 1.0
      if bolt_2022_2023_tuned_path_active:
        ff *= get_bolt_2022_2023_ff_scale(setpoint, desired_lateral_jerk, CS.vEgo)
        friction_threshold = get_bolt_2022_2023_friction_threshold(CS.vEgo, setpoint, desired_lateral_jerk)
        friction_scale = get_bolt_2022_2023_friction_scale(CS.vEgo, setpoint, desired_lateral_jerk)
      elif bolt_2018_2021_tuned_path_active:
        friction_threshold = get_bolt_2018_2021_friction_threshold(CS.vEgo, setpoint, desired_lateral_jerk)
        friction_scale = get_bolt_2018_2021_friction_scale(CS.vEgo, setpoint, desired_lateral_jerk)
      elif volt_standard_test_active:
        ff *= get_volt_standard_ff_scale(setpoint, desired_lateral_jerk, CS.vEgo) * volt_standard_center_taper
        friction_threshold = get_volt_standard_friction_threshold(CS.vEgo, setpoint, desired_lateral_jerk)
        friction_scale = get_volt_standard_friction_scale(CS.vEgo, setpoint, desired_lateral_jerk)
        friction_scale = 1.0 + ((friction_scale - 1.0) * volt_standard_center_taper)
      elif genesis_g90_test_active:
        ff *= get_genesis_g90_ff_scale(setpoint, desired_lateral_jerk, CS.vEgo)
        friction_threshold = get_genesis_g90_friction_threshold(CS.vEgo, setpoint, desired_lateral_jerk)
        friction_scale = get_genesis_g90_friction_scale(CS.vEgo, setpoint, desired_lateral_jerk)
      elif ioniq_6_active:
        ff *= get_ioniq_6_ff_scale(setpoint, desired_lateral_jerk, CS.vEgo) * ioniq_6_center_taper
        friction_threshold = get_ioniq_6_friction_threshold(CS.vEgo, setpoint, desired_lateral_jerk) / max(ioniq_6_center_taper, 1e-3)
        friction_scale = get_ioniq_6_friction_scale(CS.vEgo, setpoint, desired_lateral_jerk)
        friction_scale = 1.0 + ((friction_scale - 1.0) * ioniq_6_center_taper)
      elif kia_ev6_test_active:
        ff *= get_kia_ev6_ff_scale(setpoint, desired_lateral_jerk, CS.vEgo)
        friction_threshold = get_kia_ev6_friction_threshold(CS.vEgo, setpoint, desired_lateral_jerk)
        friction_scale = get_kia_ev6_friction_scale(CS.vEgo, setpoint, desired_lateral_jerk)
      elif volt_plexy_test_active:
        ff *= get_volt_plexy_ff_scale(setpoint, desired_lateral_jerk, CS.vEgo)
        friction_threshold = get_volt_plexy_friction_threshold(CS.vEgo, setpoint, desired_lateral_jerk)
        friction_scale = get_volt_plexy_friction_scale(CS.vEgo, setpoint, desired_lateral_jerk)
      elif self.is_civic_bosch_modified and civic_bosch_modified_lateral_testing_ground_active():
        ff *= get_civic_bosch_modified_b_ff_scale(setpoint, desired_lateral_jerk, CS.vEgo)
        friction_threshold = CIVIC_BOSCH_MODIFIED_B_FIXED_FRICTION_THRESHOLD
        friction_scale = get_civic_bosch_modified_b_friction_scale(CS.vEgo, setpoint, desired_lateral_jerk)
      ff += friction_scale * get_friction(error_with_lsf + JERK_GAIN * desired_lateral_jerk, lateral_accel_deadzone, friction_threshold, self.torque_params)
      deadzone_boost_active = False
      if self.torque_deadzone_boost > 0.0 and abs(gravity_adjusted_future_lateral_accel) < DEADZONE_BOOST_LAT_ACCEL:
        boost_scale = np.interp(abs(gravity_adjusted_future_lateral_accel), [0.0, DEADZONE_BOOST_LAT_ACCEL], [1.0, 0.0])
        ff += np.sign(gravity_adjusted_future_lateral_accel) * self.torque_deadzone_boost * boost_scale
        deadzone_boost_active = True

      if CS.vEgo < self.low_speed_reset_threshold:
        self.pid.reset()
      freeze_integrator = (steer_limited_by_safety or CS.steeringPressed or
                           CS.vEgo < self.low_speed_reset_threshold or unwind_detected)
      output_lataccel = self.pid.update(pid_log.error, error_rate=-measurement_rate, speed=CS.vEgo, feedforward=ff, freeze_integrator=freeze_integrator)
      output_torque = self.torque_from_lateral_accel(output_lataccel, self.torque_params)
      if self.is_bolt_2017:
        output_torque *= get_bolt_2017_torque_scale(setpoint, desired_lateral_jerk, CS.vEgo)
      elif bolt_2018_2021_tuned_path_active:
        output_torque *= get_bolt_2018_2021_dynamic_torque_scale(setpoint, desired_lateral_jerk, CS.vEgo)
      elif volt_standard_test_active:
        output_torque *= volt_standard_center_taper
      pid_log.active = True
      pid_log.p = float(self.pid.p)
      pid_log.i = float(self.pid.i)
      pid_log.d = float(self.pid.d)
      pid_log.f = float(self.pid.f)
      pid_log.output = float(-output_torque)  # TODO: log lat accel?
      pid_log.actualLateralAccel = float(measurement)
      pid_log.desiredLateralAccel = float(setpoint)
      pid_log.desiredLateralJerk = float(desired_lateral_jerk)
      pid_log.saturated = bool(self._check_saturation(self.steer_max - abs(output_torque) < 1e-3, CS, steer_limited_by_safety, curvature_limited))

      if DEBUG_TORQUE_TUNE and self.is_bolt:
        self.debug_counter += 1
        if self.debug_counter % 50 == 0:
          print(f"bolt_torque ff_scale={ff_scale:.3f} pos={self.torque_ff_scale_pos:.3f} "
                f"neg={self.torque_ff_scale_neg:.3f} deadzone_boost_active={deadzone_boost_active}")

    self.prev_steering_pressed = CS.steeringPressed

    # TODO left is positive in this convention
    return -output_torque, 0.0, pid_log
