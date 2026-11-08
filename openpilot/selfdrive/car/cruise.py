import math
import numpy as np

from opendbc.car.structs import car
from opendbc.car.honda.pcm_test_modes import FIXED_CRUISE_MPS
from openpilot.common.constants import CV
from openpilot.nrdr.features.driver_policy.cruise import NrdrCruise
from openpilot.sunnypilot.selfdrive.car.cruise_ext import VCruiseHelperSP


# WARNING: this value was determined based on the model's training distribution,
#          model predictions above this speed can be unpredictable
# V_CRUISE's are in kph
V_CRUISE_MIN = 0
V_CRUISE_MAX = 169
V_CRUISE_UNSET = 255
V_CRUISE_INITIAL = 0
MVL_V_CRUISE_MAX = 145  # Pinned 376c44b; do not change non-MVL/global limits.
MVL_V_CRUISE_INITIAL = 40
FIXED_V_CRUISE_MAX = FIXED_CRUISE_MPS * CV.MS_TO_KPH  # Car-side ceiling, not additional control headroom.
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


class VCruiseHelper(VCruiseHelperSP):
  def __init__(self, CP, CP_SP):
    VCruiseHelperSP.__init__(self, CP, CP_SP)
    self.CP = CP
    self.v_cruise_kph = V_CRUISE_UNSET
    self.v_cruise_cluster_kph = V_CRUISE_UNSET
    self.v_cruise_kph_last = 0
    self.button_timers = {ButtonType.decelCruise: 0, ButtonType.accelCruise: 0}
    self.button_change_states = {btn: {"standstill": False, "enabled": False} for btn in self.button_timers}
    self.nrdr = None if self.mvl_enabled else NrdrCruise(CP)
    self.v_cruise_max = MVL_V_CRUISE_MAX if self.mvl_enabled else V_CRUISE_MAX
    if self.fixed_cruise_enabled:
      self.v_cruise_max = FIXED_V_CRUISE_MAX
    # Separate from the published availability sentinel and from PCM readback.
    self.fixed_cruise_kph = V_CRUISE_UNSET
    self.fixed_cruise_button = None

  @property
  def v_cruise_initialized(self):
    return self.v_cruise_kph != V_CRUISE_UNSET

  def update_v_cruise(self, CS, enabled, is_metric):
    if self.nrdr is not None:
      self.nrdr.begin_update(is_metric)
    self.v_cruise_kph_last = self.v_cruise_kph

    self.get_minimum_set_speed(is_metric)

    if self.fixed_cruise_enabled:
      if not CS.cruiseState.available:
        self.fixed_cruise_button = None
      elif not enabled:
        # PCM engagement can arrive after the button edge has left CS_prev.
        for b in CS.buttonEvents:
          if b.type in (ButtonType.accelCruise, ButtonType.resumeCruise, ButtonType.decelCruise, ButtonType.setCruise):
            self.fixed_cruise_button = b.type
          elif b.type in (ButtonType.cancel, ButtonType.mainCruise):
            self.fixed_cruise_button = None

    _enabled = self.update_enabled_state(CS, enabled)

    if CS.cruiseState.available:
      if self.fixed_cruise_enabled:
        self.v_cruise_kph = self.fixed_cruise_kph
        if self.v_cruise_initialized and _enabled:
          self._update_v_cruise_non_pcm(CS, _enabled, is_metric)
          self.update_speed_limit_assist_v_cruise_non_pcm()
          self.v_cruise_kph = np.clip(self.v_cruise_kph, 0, self.v_cruise_max)
          self.fixed_cruise_kph = self.v_cruise_kph
        self.v_cruise_cluster_kph = self.v_cruise_kph
      elif not self.CP.pcmCruise or (not self.CP_SP.pcmCruiseSpeed and _enabled):
        # if stock cruise is completely disabled, then we can use our own set speed logic
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

    if self.fixed_cruise_enabled or not self.CP.pcmCruise or not self.CP_SP.pcmCruiseSpeed:
      self.update_button_timers(CS, enabled)

  def _update_v_cruise_non_pcm(self, CS, enabled, is_metric):
    # handle button presses. TODO: this should be in state_control, but a decelCruise press
    # would have the effect of both enabling and changing speed is checked after the state transition
    if not enabled:
      return

    long_press = False
    button_type = None

    v_cruise_delta = 1. if is_metric else IMPERIAL_INCREMENT

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

    if self.nrdr is not None:
      if not self.nrdr.allow_speed_change():
        return
      honda_speed = self.nrdr.update_honda_imperial(self, CS, button_type, long_press, self.v_cruise_max)
      if honda_speed is not None:
        self.v_cruise_kph = honda_speed
        self.v_cruise_cluster_kph = honda_speed
        return
    # MVL also uses NRDR's DISTANCE-only SLA confirmation; +/- stays manual.
    elif not self.mvl_enabled and self.update_speed_limit_assist_pre_active_confirmed(button_type):
      return

    long_press, v_cruise_delta = VCruiseHelperSP.update_v_cruise_delta(self, long_press, v_cruise_delta)
    if long_press and self.v_cruise_kph % v_cruise_delta != 0:  # partial interval
      self.v_cruise_kph = CRUISE_NEAREST_FUNC[button_type](self.v_cruise_kph / v_cruise_delta) * v_cruise_delta
    else:
      self.v_cruise_kph += v_cruise_delta * CRUISE_INTERVAL_SIGN[button_type]

    # If set is pressed while overriding, clip cruise speed to minimum of vEgo
    if CS.gasPressed and button_type in (ButtonType.decelCruise, ButtonType.setCruise):
      self.v_cruise_kph = max(self.v_cruise_kph, CS.vEgo * CV.MS_TO_KPH)

    self.v_cruise_kph = np.clip(round(self.v_cruise_kph, 1), self.v_cruise_min, self.v_cruise_max)

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

  def initialize_v_cruise(self, CS, experimental_mode: bool) -> None:
    if self.fixed_cruise_enabled:
      button = next((b.type for b in CS.buttonEvents if b.type in
                     (ButtonType.accelCruise, ButtonType.resumeCruise, ButtonType.decelCruise, ButtonType.setCruise)),
                    self.fixed_cruise_button)
      resume = button in (ButtonType.accelCruise, ButtonType.resumeCruise)
      if resume and self.fixed_cruise_kph != V_CRUISE_UNSET:
        initial_speed = self.fixed_cruise_kph
      else:
        initial_speed = CS.vEgo * CV.MS_TO_KPH
        initial_speed = self.nrdr.initial_speed(initial_speed) if self.nrdr is not None else round(initial_speed, 1)
      # Clamp after Honda imperial quantization, whose zero maps just below 0 kph.
      self.v_cruise_kph = float(np.clip(initial_speed, 0, self.v_cruise_max))
      self.fixed_cruise_kph = self.v_cruise_cluster_kph = self.v_cruise_kph
      self.fixed_cruise_button = None
      return

    # initializing is handled by the PCM
    if self.CP.pcmCruise:
      return


    if any(b.type in (ButtonType.accelCruise, ButtonType.resumeCruise) for b in CS.buttonEvents) and self.v_cruise_initialized:
      self.v_cruise_kph = self.v_cruise_kph_last
    elif getattr(self, "mvl_enabled", False):
      # card.py passes an ExperimentalMode bool, NOT the donor's integer
      # InitialCruiseSpeedKph (default 40). Ignore it; never reinterpret True
      # as a requested speed. Restore the donor's checked-in default, including
      # its 40 kph SET floor at standstill; engagement remains hardware-gated.
      self.v_cruise_kph = int(round(np.clip(max(CS.vEgo * CV.MS_TO_KPH, MVL_V_CRUISE_INITIAL),
                                          MVL_V_CRUISE_INITIAL, MVL_V_CRUISE_MAX)))
    else:
      # SET uses current speed in every driving mode. Experimental Mode must
      # not silently select a highway target on a residential street.
      initial_speed = np.clip(CS.vEgo * CV.MS_TO_KPH, V_CRUISE_INITIAL, V_CRUISE_MAX)
      self.v_cruise_kph = self.nrdr.initial_speed(initial_speed)

    self.v_cruise_cluster_kph = self.v_cruise_kph
