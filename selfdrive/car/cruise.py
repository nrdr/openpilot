import math
import numpy as np

from cereal import car
from openpilot.common.constants import CV
from openpilot.common.params import Params
from openpilot.sunnypilot.selfdrive.car.cruise_ext import VCruiseHelperSP


# WARNING: this value was determined based on the model's training distribution,
#          model predictions above this speed can be unpredictable
# V_CRUISE's are in kph
V_CRUISE_MIN = 8
V_CRUISE_MAX = 145
V_CRUISE_UNSET = 255
V_CRUISE_INITIAL = 40
V_CRUISE_INITIAL_EXPERIMENTAL_MODE = 105

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


class VCruiseHelper(VCruiseHelperSP):
  def __init__(self, CP, CP_SP):
    VCruiseHelperSP.__init__(self, CP, CP_SP)
    self.CP = CP
    self.CP_SP = CP_SP
    self.params = Params()

    self.v_cruise_kph = V_CRUISE_UNSET
    self.v_cruise_cluster_kph = V_CRUISE_UNSET
    self.v_cruise_kph_last = 0
    self.button_timers = {ButtonType.decelCruise: 0, ButtonType.accelCruise: 0}
    self.button_change_states = {btn: {"standstill": False, "enabled": False} for btn in self.button_timers}

  @property
  def v_cruise_initialized(self):
    return self.v_cruise_kph != V_CRUISE_UNSET

  def update_v_cruise(self, CS, enabled, is_metric):
    self.v_cruise_kph_last = self.v_cruise_kph

    self.get_minimum_set_speed(is_metric)

    if CS.cruiseState.available:
      _enabled = self.update_enabled_state(CS, enabled)
      if not self.CP.pcmCruise or (not self.CP_SP.pcmCruiseSpeed and _enabled):
        # if stock cruise is completely disabled, then we can use our own set speed logic
        self._update_v_cruise_non_pcm(CS, _enabled, is_metric)
        self.update_speed_limit_assist_v_cruise_non_pcm()
        self.v_cruise_cluster_kph = self.v_cruise_kph
        self.update_button_timers(CS, enabled)
      else:
        # PCM-based set speed (this comes from the car; don't quantize here)
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
    # handle button presses. TODO: this should be in state_control, but a decelCruise press
    # would have the effect of both enabling and changing speed is checked after the state transition
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

    # Don't adjust speed when pressing resume to exit standstill
    cruise_standstill = self.button_change_states[button_type]["standstill"] or CS.cruiseState.standstill
    if button_type == ButtonType.accelCruise and cruise_standstill:
      return

    # Don't adjust speed if we've enabled since the button was depressed (some ports enable on rising edge)
    if not self.button_change_states[button_type]["enabled"]:
      return

    # Speed Limit Assist for Non PCM long cars.
    # True: Disallow set speed changes when user confirmed the target set speed during preActive state
    # False: Allow set speed changes as SLA is not requesting user confirmation
    if self.update_speed_limit_assist_pre_active_confirmed(button_type):
      return

    # -------------------------------------------------------------------------
    # KEY CHANGE:
    # Work in DISPLAY UNITS:
    # - metric: integer kph
    # - imperial: integer mph (always), then convert back to kph for storage
    # This prevents fractional mph (e.g., 53.7 mph) from ever being produced.
    # -------------------------------------------------------------------------
    if is_metric:
      v_disp = float(self.v_cruise_kph)                 # kph
      disp_min = float(self.v_cruise_min)               # kph
      disp_max = float(V_CRUISE_MAX)                    # kph
      base_delta = 1.0                                  # 1 kph steps
    else:
      v_disp = float(self.v_cruise_kph) * CV.KPH_TO_MPH  # mph
      disp_min = float(self.v_cruise_min) * CV.KPH_TO_MPH
      disp_max = float(V_CRUISE_MAX) * CV.KPH_TO_MPH
      base_delta = 1.0                                   # 1 mph steps

    # Allow VCruiseHelperSP to modify delta for long-press behavior
    long_press, disp_delta = VCruiseHelperSP.update_v_cruise_delta(self, long_press, base_delta)

    # Snap to nearest interval on long-press if we're on a partial step
    if long_press and (v_disp % disp_delta) != 0:
      v_disp = CRUISE_NEAREST_FUNC[button_type](v_disp / disp_delta) * disp_delta
    else:
      v_disp += disp_delta * CRUISE_INTERVAL_SIGN[button_type]

    # If set is pressed while overriding, clip cruise speed to minimum of vEgo
    if CS.gasPressed and button_type in (ButtonType.decelCruise, ButtonType.setCruise):
      v_ego_disp = CS.vEgo * (CV.MS_TO_KPH if is_metric else CV.MS_TO_MPH)
      v_disp = max(v_disp, v_ego_disp)

    # Enforce whole-number display speeds
    if is_metric:
      v_disp = float(int(round(v_disp)))  # whole kph
      v_disp = float(np.clip(v_disp, disp_min, disp_max))
      self.v_cruise_kph = v_disp
    else:
      v_disp = float(int(round(v_disp)))  # whole mph, forever
      v_disp = float(np.clip(v_disp, disp_min, disp_max))
      self.v_cruise_kph = v_disp * CV.MPH_TO_KPH

    # Safety clip (no 0.1 kph rounding anymore)
    self.v_cruise_kph = float(np.clip(self.v_cruise_kph, self.v_cruise_min, V_CRUISE_MAX))

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
    # initializing is handled by the PCM
    if self.CP.pcmCruise:
      return

    initial_experimental_mode = experimental_mode and not dynamic_experimental_control
    initial = V_CRUISE_INITIAL_EXPERIMENTAL_MODE if initial_experimental_mode else V_CRUISE_INITIAL

    is_metric = self.params.get_bool("IsMetric")

    if any(b.type in (ButtonType.accelCruise, ButtonType.resumeCruise) for b in CS.buttonEvents) and self.v_cruise_initialized:
      self.v_cruise_kph = self.v_cruise_kph_last
    else:
      # Start from current speed, but:
      # - Metric: floor to whole kph
      # - Imperial: floor to whole mph (round down), then convert back to kph
      v_kph = float(np.clip(CS.vEgo * CV.MS_TO_KPH, initial, V_CRUISE_MAX))

      if is_metric:
        self.v_cruise_kph = float(int(math.floor(v_kph)))
      else:
        v_mph = v_kph * CV.KPH_TO_MPH
        v_mph_floor = float(int(math.floor(v_mph)))  # <-- round DOWN in mph
        self.v_cruise_kph = v_mph_floor * CV.MPH_TO_KPH

    self.v_cruise_cluster_kph = self.v_cruise_kph