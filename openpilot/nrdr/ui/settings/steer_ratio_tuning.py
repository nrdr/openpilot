from collections.abc import Callable

import pyray as rl

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.nrdr.features.lateral.honda_vgr import get_honda_vgr_profile
from openpilot.nrdr.features.lateral.steer_ratio_tuning import (
  RAW_STEER_RATIO_PROFILES,
  SteerRatioMode,
  get_steer_ratio_metadata,
  resolve_steer_ratio_selection,
)
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.sunnypilot.widgets.list_view import (
  LineSeparatorSP,
  ListItemSP,
  ToggleActionSP,
  option_item_sp,
)


class SteerRatioTuningLayout(Widget):
  def __init__(self, back_btn_callback: Callable):
    super().__init__()
    self._back_button = NavButton(tr("Back"))
    self._back_button.set_click_callback(back_btn_callback)
    self._mode_items = {
      SteerRatioMode.COMMA: self._mode_item(
          SteerRatioMode.COMMA,
          "Use Comma Steer Ratio Learner",
          "Uses Comma's last valid learned steer ratio as one number at every wheel angle. "
          "It holds the last good value through brief message dropouts.",  # noqa: ISC002
      ),
      SteerRatioMode.NRDR_RAW: self._mode_item(
          SteerRatioMode.NRDR_RAW,
          "Use nrdr Steer Ratio Learner",
          "Uses NRDR's fixed curve made directly from logged steering angles. It does not learn while you drive. "
          "The Clarity raw data ends at 247.5 degrees and then holds 15.279368. "
          "This is available only when NRDR has an exact audited curve for your car.",  # noqa: ISC002
      ),
      SteerRatioMode.FIRMWARE: self._mode_item(
        SteerRatioMode.FIRMWARE,
        "Use Firmware Steer Ratio",
        "Uses the exact shape stored in a recognized EPS firmware file, anchored to your car's stock center ratio.",
      ),
    }

    self._manual_center = option_item_sp(
      param="NrdrSteerRatioManualCenter",
      title=lambda: tr("Manual Override On-Center Ratio (Default: 15.38)"),
      min_value=800,
      max_value=2500,
      value_change_step=1,
      description=lambda: tr("The ratio used with the wheel straight ahead. A bigger number asks for more steering-wheel movement "
                             "for the same planned curve; a smaller number asks for less."),  # noqa: ISC002
      label_callback=lambda value: f"{value / 100:.2f}",
      use_float_scaling=True,
    )
    self._manual_final = option_item_sp(
      param="NrdrSteerRatioManualFinal",
      title=lambda: tr("Manual Override Final Ratio (Default: 10.93)"),
      min_value=800,
      max_value=2500,
      value_change_step=1,
      description=lambda: tr("The ratio used near the end of the steering wheel's travel. NRDR blends smoothly between the two manual numbers."),
      label_callback=lambda value: f"{value / 100:.2f}",
      use_float_scaling=True,
    )
    self._status = ListItemSP(title=lambda: tr("Current steer-ratio result"))
    self._status.set_right_value(self._status_text)
    self._scroller = Scroller([
      self._status,
      LineSeparatorSP(40),
      self._mode_items[SteerRatioMode.COMMA],
      self._mode_items[SteerRatioMode.NRDR_RAW],
      self._mode_items[SteerRatioMode.FIRMWARE],
      LineSeparatorSP(40),
      self._manual_center,
      self._manual_final,
    ], line_separator=False, spacing=0)

  def _mode_item(self, mode: SteerRatioMode, title: str, description: str) -> ListItemSP:
    action = ToggleActionSP(
      initial_state=False,
      callback=lambda state, mode=mode: self._set_mode(mode, state),
      param=None,
    )
    return ListItemSP(
      title=lambda title=title: tr(title),
      description=lambda description=description: tr(description),
      action_item=action,
    )

  @staticmethod
  def _current_mode() -> SteerRatioMode:
    try:
      return SteerRatioMode(int(ui_state.params.get("NrdrSteerRatioMode")))
    except (TypeError, ValueError):
      return SteerRatioMode.MANUAL

  @staticmethod
  def _capabilities() -> tuple[bool, bool, bool]:
    if ui_state.CP is None:
      return False, False, False
    fingerprint = str(ui_state.CP.carFingerprint)
    is_honda = str(ui_state.CP.brand).lower() == "honda"
    return (
      is_honda and get_steer_ratio_metadata(fingerprint) is not None,
      is_honda and fingerprint in RAW_STEER_RATIO_PROFILES,
      get_honda_vgr_profile(ui_state.CP) is not None,
    )

  def _set_mode(self, mode: SteerRatioMode, state: bool) -> None:
    if ui_state.engaged:
      return
    current = self._current_mode()
    new_mode = mode if state else SteerRatioMode.MANUAL if current is mode else current
    ui_state.params.put("NrdrSteerRatioMode", int(new_mode))

  def _status_text(self) -> str:
    if ui_state.CP is None:
      return tr("Waiting for car")
    selection = resolve_steer_ratio_selection(ui_state.CP, ui_state.params)
    if selection.available:
      return tr(selection.effective_label)
    return tr("Stock fallback — selected mode unavailable")

  def _update_state(self):
    super()._update_state()
    mode = self._current_mode()
    manual_available, raw_available, firmware_available = self._capabilities()
    available = {
      SteerRatioMode.COMMA: True,
      SteerRatioMode.NRDR_RAW: raw_available,
      SteerRatioMode.FIRMWARE: firmware_available,
    }
    for item_mode, item in self._mode_items.items():
      selected = mode is item_mode
      item.action_item.set_state(selected)
      # With a mode selected, only its own switch remains clickable so turning
      # it off returns to Manual. Geometry writes are locked while engaged.
      item.action_item.set_enabled(not ui_state.engaged and (selected or (mode is SteerRatioMode.MANUAL and available[item_mode])))

    manual_enabled = not ui_state.engaged and mode is SteerRatioMode.MANUAL and manual_available
    self._manual_center.action_item.set_enabled(manual_enabled)
    self._manual_final.action_item.set_enabled(manual_enabled)

  def _render(self, rect):
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    content_rect = rl.Rectangle(
      rect.x,
      rect.y + self._back_button.rect.height + 40,
      rect.width,
      rect.height - self._back_button.rect.height - 40,
    )
    self._scroller.render(content_rect)

  def show_event(self):
    self._scroller.show_event()


__all__ = ("SteerRatioTuningLayout",)
