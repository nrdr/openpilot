import math
import numpy as np

from cereal import car
from opendbc.car.honda.values import CAR
from openpilot.common.constants import CV
from openpilot.sunnypilot.selfdrive.car.cruise_ext import VCruiseHelperSP


# WARNING: this value was determined based on the model's training distribution,
#          model predictions above this speed can be unpredictable
# V_CRUISE's are in kph
V_CRUISE_MIN = 8
V_CRUISE_MAX = 145
V_CRUISE_UNSET = 255
V_CRUISE_INITIAL = 40
V_CRUISE_INITIAL_EXPERIMENTAL_MODE = 105
IMPERIAL_INCREMENT = round(CV.MPH_TO_KPH, 1)  # round here to avoid rounding errors incrementing set speed

ButtonEvent = car.CarState.ButtonEvent
ButtonType = car.CarState.ButtonEvent.Type
CRUISE_LONG_PRESS = 50
CRUISE_NEAREST_FUNC = {
  ButtonType.accelCruise: math.ceil,
  ButtonType.decelCruise: math.floor,
}
CRUISE_INTERVAL_SIGN = {
  ButtonType.accelCruise: +1,
  ButtonType.decelCruise: -1,
}

# Honda/Clarity cluster MPH rounding quirks (legacy behavior).
# These constants model the integer MPH ladder the cluster displays in imperial mode.
HONDA_MPH_PER_KPH = 0.6233
HONDA_MPH_OFFSET = 0.0995


def _honda_kph_to_mph(kph: float) -> int:
  """Convert KPH to the integer MPH value the Honda cluster would display."""
  return int(round(kph * HONDA_MPH_PER_KPH + HONDA_MPH_OFFSET))


def _honda_mph_to_kph(mph: float) -> float:
  """Inverse mapping to a KPH value that will round/display as the requested MPH on the cluster."""
  return (float(mph) - HONDA_MPH_OFFSET) / HONDA_MPH_PER_KPH


class VCruiseHelper(VCruiseHelperSP):
  def __init__(self, CP, CP_SP):
    VCruiseHelperSP.__init__(self, CP, CP_SP)
    self.CP = CP
    self.v_cruise_kph = V_CRUISE_UNSET
    self.v_cruise_cluster_kph = V_CRUISE_UNSET
    self.v_cruise_kph_last = 0
    self.button_timers = {ButtonType.decelCruise: 0, ButtonType.accelCruise: 0}
    self.button_change_states = {btn: {"standstill": False, "enabled": False} for btn in self.button_timers}

    # Persist the last unit mode so initialize_v_cruise can match update_v_cruise behavior.
    self.is_metric = True

  @property
  def v_cruise_initialized(self):
    return self.v_cruise_kph != V_CRUISE_UNSET

  def update_v_cruise(self, CS, enabled, is_metric):
    self.is_metric = is_metric
    self.v_cruise_kph_last = self.v_cruise_kph

    self.get_minimum_set_speed(is_metric)

    if CS.cruiseState.available:
      _enabled = self.update_enabled_state(CS, enabled)
      if not self.CP.pcmCruise or (not self.CP_SP.pcmCruiseSpeed and _enabled):
        # If stock cruise is completely disabled, we can synthesize our own set speed logic.
        self._update_v_cruise_non_pcm(CS, _enabled, is_metric)
        self.update_speed_limit_assist_v_cruise_non_pcm()

        # For non-PCM, the synthesized target is also the desired cluster/display value.
        self.v_cruise_cluster_kph = self.v_cruise_kph

        self.update_button_timers(CS, enabled)
      else:
        self.v_cruise_kph = CS.cruiseState.speed * CV.MS_TO_KPH
        self.v_cruise_cluster_kph = CS.cruiseState.speedCluster * CV.MS_TO_KPH
        if CS.cruiseState.speed == 0:
          self.v_cruise_kph = V_CRUISE_UNSET
          self.v_cruise_cluster_kph = V_CRUISE_UNSET
        elif CS.cruiseState.speed == -1:
          self.v_cruise_kph = -1
          self.v_cruise_cluster_kph = -1
    else:
      self.v_cruise_kph = V_CRUISE_UNSET
      self.v_cruise_cluster_kph = V_CRUISE_UNSET

  def _update_v_cruise_non_pcm(self, CS, enabled, is_metric):
    # Handle button presses. A decel press can both enable and change speed, so this is evaluated after state transition.
    if not enabled:
      return

    long_press = False
    button_type = None

    for b in CS.buttonEvents:
      if b.type.raw in self.button_timers and not b.pressed:
        if self.button_timers[b.type.raw] > CRUISE_LONG_PRESS:
          return  # end long press
        button_type = b.type.raw
        break
    else:
      for k, timer in self.button_timers.items():
        if timer and timer % CRUISE_LONG_PRESS == 0:
          button_type = k
          long_press = True
          break

    if button_type is None:
      return

    # Do not adjust speed when pressing resume to exit standstill.
    cruise_standstill = self.button_change_states[button_type]["standstill"] or CS.cruiseState.standstill
    if button_type == ButtonType.accelCruise and cruise_standstill:
      return

    # Do not adjust speed if we've enabled since the button was depressed (some ports enable on rising edge).
    if not self.button_change_states[button_type]["enabled"]:
      return

    # Speed Limit Assist for non-PCM long cars.
    if self.update_speed_limit_assist_pre_active_confirmed(button_type):
      return

    # Clarity-only imperial rounding behavior:
    # Work in integer MPH space using the cluster's display ladder, then convert back to KPH.
    is_clarity = self.CP.carFingerprint == CAR.HONDA_CLARITY
    if (not is_metric) and is_clarity:
      cur_mph = _honda_kph_to_mph(float(self.v_cruise_kph))

      base_delta_mph = 1.0
      round_to_nearest, delta_mph = VCruiseHelperSP.update_v_cruise_delta(self, long_press, base_delta_mph)

      if round_to_nearest and (cur_mph % int(delta_mph) != 0):
        cur_mph = CRUISE_NEAREST_FUNC[button_type](cur_mph / delta_mph) * int(delta_mph)
      else:
        cur_mph += int(delta_mph) * CRUISE_INTERVAL_SIGN[button_type]

      # If set is pressed while overriding, clip the set speed to at least the current ego speed.
      if CS.gasPressed and button_type in (ButtonType.decelCruise, ButtonType.setCruise):
        ego_mph = _honda_kph_to_mph(CS.vEgo * CV.MS_TO_KPH)
        cur_mph = max(cur_mph, ego_mph)

      v_new_kph = _honda_mph_to_kph(cur_mph)
      self.v_cruise_kph = np.clip(round(v_new_kph, 1), self.v_cruise_min, V_CRUISE_MAX)
      self.v_cruise_cluster_kph = self.v_cruise_kph
      return

    # Default behavior for all other vehicles/modes.
    v_cruise_delta = 1.0 if is_metric else IMPERIAL_INCREMENT
    long_press, v_cruise_delta = VCruiseHelperSP.update_v_cruise_delta(self, long_press, v_cruise_delta)
    if long_press and self.v_cruise_kph % v_cruise_delta != 0:  # partial interval
      self.v_cruise_kph = CRUISE_NEAREST_FUNC[button_type](self.v_cruise_kph / v_cruise_delta) * v_cruise_delta
    else:
      self.v_cruise_kph += v_cruise_delta * CRUISE_INTERVAL_SIGN[button_type]

    if CS.gasPressed and button_type in (ButtonType.decelCruise, ButtonType.setCruise):
      self.v_cruise_kph = max(self.v_cruise_kph, CS.vEgo * CV.MS_TO_KPH)

    self.v_cruise_kph = np.clip(round(self.v_cruise_kph, 1), self.v_cruise_min, V_CRUISE_MAX)

  def update_button_timers(self, CS, enabled):
    # increment timer for buttons still pressed
    for k in self.button_timers:
      if self.button_timers[k] > 0:
        self.button_timers[k] += 1

    for b in CS.buttonEvents:
      if b.type.raw in self.button_timers:
        # Start/end timer and store current state on change of button pressed
        self.button_timers[b.type.raw] = 1 if b.pressed else 0
        self.button_change_states[b.type.raw] = {"standstill": CS.cruiseState.standstill, "enabled": enabled}

  def initialize_v_cruise(self, CS, experimental_mode: bool, dynamic_experimental_control: bool) -> None:
    # Initializing is handled by the PCM.
    if self.CP.pcmCruise:
      return

    initial_experimental_mode = experimental_mode and not dynamic_experimental_control
    initial = V_CRUISE_INITIAL_EXPERIMENTAL_MODE if initial_experimental_mode else V_CRUISE_INITIAL

    if any(b.type in (ButtonType.accelCruise, ButtonType.resumeCruise) for b in CS.buttonEvents) and self.v_cruise_initialized:
      self.v_cruise_kph = self.v_cruise_kph_last
    else:
      v_init_kph = float(np.clip(CS.vEgo * CV.MS_TO_KPH, initial, V_CRUISE_MAX))

      # Clarity-only imperial initialization:
      # Snap onto the same MPH ladder used by the cluster to avoid fractional-initial set speeds.
      is_clarity = self.CP.carFingerprint == CAR.HONDA_CLARITY
      if (not self.is_metric) and is_clarity:
        init_mph = _honda_kph_to_mph(v_init_kph)
        v_init_kph = _honda_mph_to_kph(init_mph)

      self.v_cruise_kph = np.clip(round(v_init_kph, 1), self.v_cruise_min, V_CRUISE_MAX)

    self.v_cruise_cluster_kph = self.v_cruise_kph
