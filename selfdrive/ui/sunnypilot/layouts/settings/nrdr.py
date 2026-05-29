"""
nrdr experimental settings panel.
"""

from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, option_item_sp, LineSeparatorSP
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.widgets import Widget
from openpilot.selfdrive.ui.ui_state import ui_state


class NrdrLayout(Widget):
  def __init__(self):
    super().__init__()

    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=False, spacing=0)

  def _initialize_items(self):
    self._lat_pid_tune_scale = option_item_sp(
      param="LatPidTuneScale",
      title=lambda: tr("Lateral PID Tune Scale"),
      min_value=0,
      max_value=500,
      value_change_step=5,
      description=lambda: tr("Scales lateral PID controller values from their configured base tune."),
      label_callback=lambda value: f"{value}%",
    )

    self._long_pid_tune_scale = option_item_sp(
      param="LongPidTuneScale",
      title=lambda: tr("Longitudinal PID Tune Scale"),
      min_value=0,
      max_value=500,
      value_change_step=5,
      description=lambda: tr("Scales longitudinal PID controller values from their configured base tune."),
      label_callback=lambda value: f"{value}%",
    )

    self._increase_override_tolerance = toggle_item_sp(
      param="NrdrIncreaseOverrideTolerance",
      title=lambda: tr("Increase Driver Override Tolerance"),
      description=lambda: tr("Reduces the likelihood of false driver override detections on sensitive Honda EPS platforms."),
    )

    self._lkas_active_during_override = toggle_item_sp(
      param="HondaLkasActiveDuringOverride",
      title=lambda: tr("Tell EPS LKAS=Active During Override "),
      description=lambda: tr("When fully overriding, should the EPS feel like driving normally or be more resistant?"),
    )

    self._override_torque_scale = option_item_sp(
      param="HondaOverrideTorqueScale",
      title=lambda: tr("Override Torque Retain"),
      min_value=0,
      max_value=100,
      value_change_step=1,
      description=lambda: tr("Controls how much openpilot steering torque remains while the driver is overriding."),
      label_callback=lambda value: f"{value}%",
    )

    self._override_fade_down = option_item_sp(
      param="HondaOverrideFadeDownSecs",
      title=lambda: tr("Override Torque Fade Down"),
      min_value=0,
      max_value=1000,
      value_change_step=10,
      description=lambda: tr("Controls how quickly steering torque fades out when driver override begins."),
      label_callback=lambda value: f"{value / 100:.1f} s",
      use_float_scaling=True,
    )

    self._override_fade_up = option_item_sp(
      param="HondaOverrideFadeUpSecs",
      title=lambda: tr("Override Torque Fade Up"),
      min_value=0,
      max_value=1000,
      value_change_step=10,
      description=lambda: tr("Controls how quickly steering torque fades back in after driver override ends."),
      label_callback=lambda value: f"{value / 100:.1f} s",
      use_float_scaling=True,
    )

    self._live_learning_gas = toggle_item_sp(
      param="HondaLiveLearningGas",
      title=lambda: tr("Live Learning Gas"),
      description=lambda: tr("Allows Honda gas and wind compensation factors to learn live while driving."),
    )

    self._low_pass_filter = toggle_item_sp(
      param="HondaTorqueLowPassFilter",
      title=lambda: tr("Low Pass Filter"),
      description=lambda: tr("Applies smoothing to requested steering torque."),
    )

    self._steer_delta_limiter = toggle_item_sp(
      param="HondaSteerDeltaLimiter",
      title=lambda: tr("Steer Delta Rate Limiter"),
      description=lambda: tr("Limits how quickly requested steering torque can rise or fall."),
    )

    self._steer_delta_up = option_item_sp(
      param="HondaSteerDeltaUp",
      title=lambda: tr("Steer Delta Up"),
      min_value=0,
      max_value=10000,
      value_change_step=10,
      description=lambda: tr("Controls the maximum upward steering torque rate when the rate limiter is enabled."),
      label_callback=lambda value: f"{value / 100:.1f}",
      use_float_scaling=True,
    )

    self._steer_delta_down = option_item_sp(
      param="HondaSteerDeltaDown",
      title=lambda: tr("Steer Delta Down"),
      min_value=0,
      max_value=10000,
      value_change_step=10,
      description=lambda: tr("Controls the maximum downward steering torque rate when the rate limiter is enabled."),
      label_callback=lambda value: f"{value / 100:.1f}",
      use_float_scaling=True,
    )

    self._stopping_decel_rate = option_item_sp(
      param="HondaStoppingDecelRate",
      title=lambda: tr("Stopping Decel Rate"),
      min_value=0,
      max_value=100,
      value_change_step=1,
      description=lambda: tr("Controls the deceleration rate used while stopping."),
      label_callback=lambda value: f"{value / 100:.2f}",
    )

    return [
      self._increase_override_tolerance,
      LineSeparatorSP(40),
      self._override_fade_down,
      self._override_fade_up,
      self._lkas_active_during_override,
      self._override_torque_scale,
      LineSeparatorSP(40),
      self._live_learning_gas,
      self._low_pass_filter,
      LineSeparatorSP(40),
      self._steer_delta_limiter,
      self._steer_delta_up,
      self._steer_delta_down,
      LineSeparatorSP(40),
      self._lat_pid_tune_scale,
      self._long_pid_tune_scale,
      self._stopping_decel_rate,
    ]

  def _update_state(self):
    super()._update_state()

    steer_delta_limiter_enabled = self._steer_delta_limiter.action_item.get_state()

    self._increase_override_tolerance.action_item.set_enabled(True)
    self._lat_pid_tune_scale.action_item.set_enabled(True)
    self._long_pid_tune_scale.action_item.set_enabled(True)
    self._override_torque_scale.action_item.set_enabled(True)
    self._steer_delta_limiter.action_item.set_enabled(True)
    self._steer_delta_up.action_item.set_enabled(True)
    self._steer_delta_down.action_item.set_enabled(True)

    self._steer_delta_up.set_visible(steer_delta_limiter_enabled)
    self._steer_delta_down.set_visible(steer_delta_limiter_enabled)

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()
