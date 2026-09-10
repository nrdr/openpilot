"""Offroad-only controls for confidence-gated lane centering."""

from collections.abc import Callable

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.selfdrive.controls.lib.lane_centering import (
  LANE_CENTERING_MIN_SPEED_MAX_MPH,
  LANE_CENTERING_MIN_SPEED_MIN_MPH,
  lane_centering_min_speed_mph,
)
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.lib.styles import style
from openpilot.system.ui.sunnypilot.widgets.list_view import ListItemSP, toggle_item_sp
from openpilot.system.ui.sunnypilot.widgets.option_control import OptionControlSP
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.scroller_tici import Scroller


class _GuardedOptionControlSP(OptionControlSP):
  """Option control that rechecks its write gate at the mutation boundary."""

  def __init__(self, *args, write_allowed: Callable[[], bool], value_normalizer: Callable[[object], float] | None = None, **kwargs):
    self._write_allowed = write_allowed
    self._value_normalizer = value_normalizer
    super().__init__(*args, **kwargs)

  def set_value(self, value: int):
    if self._write_allowed():
      super().set_value(value)

  def refresh_from_param(self) -> None:
    try:
      value = self.params.get(self.param_key, return_default=True)
      if self._value_normalizer is not None:
        value = self._value_normalizer(value)
      candidate = int(float(value) * 100.0) if self.use_float_scaling else int(value)
    except (TypeError, ValueError):
      return
    self.current_value = min(self.max_value, max(self.min_value, candidate))


class LaneCenteringLayout(Widget):
  def __init__(self):
    super().__init__()

    self._lane_centering_toggle = toggle_item_sp(
      title=tr("Enable Lane Centering"),
      description=tr("Bias the model curvature toward the center of two confident lane lines. The correction remains subject to the normal " +
                     "curvature and jerk limits."),
      initial_state=ui_state.params.get_bool("LaneCentering"),
      enabled=self._write_allowed,
      callback=self._on_lane_centering,
    )
    self._pause_on_signal_toggle = toggle_item_sp(
      title=tr("Pause on Turn Signal"),
      description=tr("Smoothly release the lane-centering correction while either turn signal is active."),
      initial_state=bool(ui_state.params.get("LaneCenteringPauseOnSignal", return_default=True)),
      enabled=self._settings_writable,
      callback=self._on_pause_on_signal,
    )
    self._minimum_speed_control = self._option_item(
      title=tr("Minimum Lane Centering Speed"),
      description=tr("Arm lane centering at this speed. Once active, it releases smoothly 3 mph below the selected speed, bounded by the " +
                     "5 m/s controller floor."),
      param="LaneCenteringMinSpeed",
      min_value=LANE_CENTERING_MIN_SPEED_MIN_MPH,
      max_value=LANE_CENTERING_MIN_SPEED_MAX_MPH,
      label_callback=lambda value: f"{value} mph",
      value_normalizer=lane_centering_min_speed_mph,
    )
    self._center_offset_control = self._option_item(
      title=tr("Center Offset"),
      description=tr("Shift the target left or right of the detected lane center. The controller reduces the offset in a narrow lane."),
      param="LaneCenterOffset",
      min_value=-30,
      max_value=30,
      use_float_scaling=True,
      label_callback=lambda value: f"{value / 100:.2f} m",
    )
    self._model_authority_control = self._option_item(
      title=tr("Model Path Authority"),
      description=tr("Allow a confident model path to reduce the lane-line correction when the two paths disagree. 100% gives the model full " +
                     "authority; 0% retains the full lane-line correction."),
      param="LaneCenteringE2EAuthority",
      min_value=0,
      max_value=100,
      value_change_step=5,
      use_float_scaling=True,
      label_callback=lambda value: f"{value}%",
    )

    self._scroller = Scroller([
      self._lane_centering_toggle,
      self._minimum_speed_control,
      self._pause_on_signal_toggle,
      self._center_offset_control,
      self._model_authority_control,
    ], line_separator=True, spacing=0)

  @staticmethod
  def _write_allowed() -> bool:
    return ui_state.is_offroad() and not ui_state.engaged

  def _settings_writable(self) -> bool:
    return self._write_allowed() and ui_state.params.get_bool("LaneCentering")

  def _option_item(self, title: str, description: str, param: str, min_value: int, max_value: int,
                   value_change_step: int = 1, use_float_scaling: bool = False,
                   label_callback: Callable[[int], str] | None = None,
                   value_normalizer: Callable[[object], float] | None = None) -> ListItemSP:
    action = _GuardedOptionControlSP(
      param,
      min_value,
      max_value,
      value_change_step=value_change_step,
      enabled=self._settings_writable,
      use_float_scaling=use_float_scaling,
      label_width=style.BUTTON_ACTION_WIDTH,
      label_callback=label_callback,
      write_allowed=self._settings_writable,
      value_normalizer=value_normalizer,
    )
    return ListItemSP(title=title, description=description, action_item=action)

  def _on_lane_centering(self, state: bool) -> None:
    if not self._write_allowed():
      self._lane_centering_toggle.action_item.set_state(ui_state.params.get_bool("LaneCentering"))
      return
    ui_state.params.put_bool("LaneCentering", state, block=True)

  def _on_pause_on_signal(self, state: bool) -> None:
    if not self._settings_writable():
      current = bool(ui_state.params.get("LaneCenteringPauseOnSignal", return_default=True))
      self._pause_on_signal_toggle.action_item.set_state(current)
      return
    ui_state.params.put_bool("LaneCenteringPauseOnSignal", state, block=True)

  def _refresh(self) -> None:
    self._lane_centering_toggle.action_item.set_state(ui_state.params.get_bool("LaneCentering"))
    self._pause_on_signal_toggle.action_item.set_state(
      bool(ui_state.params.get("LaneCenteringPauseOnSignal", return_default=True)))
    self._minimum_speed_control.action_item.refresh_from_param()
    self._center_offset_control.action_item.refresh_from_param()
    self._model_authority_control.action_item.refresh_from_param()

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._refresh()
    self._scroller.show_event()
