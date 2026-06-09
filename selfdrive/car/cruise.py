import math
import numpy as np

from cereal import car
from openpilot.common.constants import CV
from openpilot.sunnypilot.selfdrive.car.cruise_ext import VCruiseHelperSP


# WARNING: this value was determined based on the model's training distribution,
#          model predictions above this speed can be unpredictable
# V_CRUISE's are in kph
V_CRUISE_MIN = 0
V_CRUISE_MAX = 169
V_CRUISE_UNSET = 255
V_CRUISE_INITIAL = 0
V_CRUISE_INITIAL_EXPERIMENTAL_MODE = 105

# Round here to avoid rounding errors incrementing set speed.
IMPERIAL_INCREMENT = round(CV.MPH_TO_KPH, 1)

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

# Honda cluster MPH rounding quirks (legacy behavior).
# These constants model the way many Honda clusters round MPH from a KPH internal value.
HONDA_MPH_PER_KPH = 0.6233
HONDA_MPH_OFFSET = 0.0995


def _honda_kph_to_mph(kph: float) -> int:
  """Convert KPH to the integer MPH value a Honda cluster would display."""
  return int(round(kph * HONDA_MPH_PER_KPH + HONDA_MPH_OFFSET))


def _honda_mph_to_kph(mph: float) -> float:
  """Inverse mapping to a KPH value that rounds back to the same Honda cluster MPH."""
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

    # Persist units so initialize_v_cruise can use the same mode as update_v_cruise.
    self.is_metric = True

  @property
  def v_cruise_initialized(self):
    return self.v_cruise_kph != V_CRUISE_UNSET

  def update_v_cruise(self, CS, enabled, is_metric):
    # Persist for initialize_v_cruise.
    self.is_metric = is_metric

    self.v_cruise_kph_last = self.v_cruise_kph

    self.get_minimum_set_speed(is_metric)

    _enabled = self.update_enabled_state(CS, enabled)

    if CS.cruiseState.available:
      if not self.CP.pcmCruise or (not self.CP_SP.pcmCruiseSpeed and _enabled):
        # If stock cruise is completely disabled, then we can use our own set speed logic.
        self._update_v_cruise_non_pcm(CS, _enabled, is_metric)
        self.update_speed_limit_assist_v_cruise_non_pcm()
        self.v_cruise_cluster_kph = self.v_cruise_kph
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

    if not self.CP.pcmCruise or not self.CP_SP.pcmCruiseSpeed:
      self.update_button_timers(CS, enabled)

  def _update_v_cruise_non_pcm(self, CS, enabled, is_metric):
    # Handle button presses. TODO: this should be in state_control, but a decelCruise press
    # would have the effect of both enabling and changing speed is checked after the state transition.
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

    # Don't adjust speed when pressing resume to exit standstill.
    cruise_standstill = self.button_change_states[button_type]["standstill"] or CS.cruiseState.standstill
    if button_type == ButtonType.accelCruise and cruise_standstill:
      return

    # Don't adjust speed if we've enabled since the button was depressed (some ports enable on rising edge).
    if not self.button_change_states[button_type]["enabled"]:
      return

    # Speed Limit Assist for Non PCM long cars.
    # True: Disallow set speed changes when user confirmed the target set speed during preActive state
    # False: Allow set speed changes as SLA is not requesting user confirmation
    if self.update_speed_limit_assist_pre_active_confirmed(button_type):
      return

    # Honda imperial rounding fix:
    # When on Honda + imperial + non-PCM, do stepping in MPH integer space using Honda's
    # display rounding behavior, then invert back to a KPH value that will display correctly.
    is_honda = getattr(self.CP, "carName", "") == "honda"
    if (not is_metric) and is_honda:
      cur_mph = _honda_kph_to_mph(float(self.v_cruise_kph))

      base_delta_mph = 1.0
      round_to_nearest, delta_mph = VCruiseHelperSP.update_v_cruise_delta(self, long_press, base_delta_mph)

      if round_to_nearest and (cur_mph % int(delta_mph) != 0):
        cur_mph = CRUISE_NEAREST_FUNC[button_type](cur_mph / delta_mph) * int(delta_mph)
      else:
        cur_mph += int(delta_mph) * CRUISE_INTERVAL_SIGN[button_type]

      # If set is pressed while overriding, clip cruise speed to minimum of vEgo.
      if CS.gasPressed and button_type in (ButtonType.decelCruise, ButtonType.setCruise):
        ego_mph = _honda_kph_to_mph(CS.vEgo * CV.MS_TO_KPH)
        cur_mph = max(cur_mph, ego_mph)

      v_new_kph = _honda_mph_to_kph(cur_mph)
      self.v_cruise_kph = np.clip(round(v_new_kph, 1), self.v_cruise_min, V_CRUISE_MAX)
      self.v_cruise_cluster_kph = self.v_cruise_kph
      return

    # Default behavior (non-Honda or metric).
    v_cruise_delta = 1.0 if is_metric else IMPERIAL_INCREMENT

    long_press, v_cruise_delta = VCruiseHelperSP.update_v_cruise_delta(self, long_press, v_cruise_delta)
    if long_press and self.v_cruise_kph % v_cruise_delta != 0:  # partial interval
      self.v_cruise_kph = CRUISE_NEAREST_FUNC[button_type](self.v_cruise_kph / v_cruise_delta) * v_cruise_delta
    else:
      self.v_cruise_kph += v_cruise_delta * CRUISE_INTERVAL_SIGN[button_type]

    # If set is pressed while overriding, clip cruise speed to minimum of vEgo.
    if CS.gasPressed and button_type in (ButtonType.decelCruise, ButtonType.setCruise):
      self.v_cruise_kph = max(self.v_cruise_kph, CS.vEgo * CV.MS_TO_KPH)

    self.v_cruise_kph = np.clip(round(self.v_cruise_kph, 1), self.v_cruise_min, V_CRUISE_MAX)

  def update_button_timers(self, CS, enabled):
    # Increment timer for buttons still pressed.
    for k in self.button_timers:
      if self.button_timers[k] > 0:
        self.button_timers[k] += 1

    for b in CS.buttonEvents:
      if b.type.raw in self.button_timers:
        # Start/end timer and store current state on change of button pressed.
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

      # Snap initial value onto Honda's MPH ladder when in imperial on Honda.
      is_honda = getattr(self.CP, "carName", "") == "honda"
      if (not self.is_metric) and is_honda:
        init_mph = _honda_kph_to_mph(v_init_kph)
        v_init_kph = _honda_mph_to_kph(init_mph)

      self.v_cruise_kph = np.clip(round(v_init_kph, 1), self.v_cruise_min, V_CRUISE_MAX)

    self.v_cruise_cluster_kph = self.v_cruise_kph
