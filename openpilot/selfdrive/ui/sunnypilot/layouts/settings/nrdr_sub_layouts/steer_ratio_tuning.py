from collections.abc import Callable

import pyray as rl

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.sunnypilot.nrdr.honda_vgr import get_honda_vgr_profile
from openpilot.sunnypilot.nrdr.steer_ratio_tuning import (
  SteerRatioMode,
  get_steer_ratio_metadata,
  parse_steer_ratio_mode,
)
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.sunnypilot.widgets.list_view import LineSeparatorSP, option_item_sp, toggle_item_sp


class SteerRatioTuningLayout(Widget):
  def __init__(self, back_btn_callback: Callable):
    super().__init__()
    self._back_button = NavButton(tr("Back"))
    self._back_button.set_click_callback(back_btn_callback)
    self._mode = SteerRatioMode.MANUAL
    self._comma = toggle_item_sp(
      title=lambda: tr("Use Comma Steer Ratio Learner"),
      description=lambda: tr("Uses comma's one learned steering ratio. It starts from the car's stock number, then holds the " +
                             "last good learned number if the learner briefly becomes unavailable.") + " " + self._latch_notice(),
      callback=lambda enabled: self._set_mode(SteerRatioMode.COMMA, enabled),
    )
    self._nrdr_raw = toggle_item_sp(
      title=lambda: tr("Use nrdr Steer Ratio Learner"),
      description=self._raw_description,
      callback=lambda enabled: self._set_mode(SteerRatioMode.NRDR_RAW, enabled),
    )
    self._firmware = toggle_item_sp(
      title=lambda: tr("Use Firmware Steer Ratio"),
      description=self._firmware_description,
      callback=lambda enabled: self._set_mode(SteerRatioMode.FIRMWARE, enabled),
    )
    self._manual_center = option_item_sp(
      param="NrdrSteerRatioManualCenter",
      title=lambda: tr("Manual Override On-Center Ratio"),
      min_value=800,
      max_value=2500,
      value_change_step=1,
      description=self._manual_center_description,
      label_callback=lambda value: f"{value / 100:.2f}",
      use_float_scaling=True,
    )
    self._manual_final = option_item_sp(
      param="NrdrSteerRatioManualFinal",
      title=lambda: tr("Manual Override Final Ratio"),
      min_value=800,
      max_value=2500,
      value_change_step=1,
      description=self._manual_final_description,
      label_callback=lambda value: f"{value / 100:.2f}",
      use_float_scaling=True,
    )
    self._mode_items = {
      SteerRatioMode.COMMA: self._comma,
      SteerRatioMode.NRDR_RAW: self._nrdr_raw,
      SteerRatioMode.FIRMWARE: self._firmware,
    }
    self._scroller = Scroller([
      self._comma,
      self._nrdr_raw,
      self._firmware,
      LineSeparatorSP(40),
      self._manual_center,
      self._manual_final,
    ], line_separator=False, spacing=0)

  def _set_mode(self, selected: SteerRatioMode, enabled: bool) -> None:
    current = parse_steer_ratio_mode(ui_state.params.get("NrdrSteerRatioMode", return_default=True))
    mode = selected if enabled else SteerRatioMode.MANUAL if current is selected else current
    ui_state.params.put("NrdrSteerRatioMode", int(mode))
    self._mode = mode
    self._sync_switches()

  @staticmethod
  def _raw_available() -> bool:
    return ui_state.CP is not None and str(ui_state.CP.brand).lower() == "honda" and \
      str(ui_state.CP.carFingerprint) == "HONDA_CLARITY"

  @staticmethod
  def _firmware_available() -> bool:
    return ui_state.CP is not None and get_honda_vgr_profile(ui_state.CP) is not None

  @staticmethod
  def _manual_available() -> bool:
    return ui_state.CP is not None and str(ui_state.CP.brand).lower() == "honda" and \
      get_steer_ratio_metadata(ui_state.CP.carFingerprint) is not None

  @staticmethod
  def _latch_notice() -> str:
    return tr("Changes made while engaged activate on the next disengage/re-engage. If already disengaged, wait up to 10 seconds " +
              "for settings to sync before engaging.")

  def _manual_center_description(self) -> str:
    if not self._manual_available():
      return tr("Unavailable for this car. Its stock steer ratio stays unchanged.")
    return tr(
      "Controls steering near the middle. A bigger number asks for more steering-wheel movement; a smaller number asks for less."
    ) + " " + self._latch_notice()

  def _manual_final_description(self) -> str:
    if not self._manual_available():
      return tr("Unavailable for this car. Its stock steer ratio stays unchanged.")
    return tr(
      "Controls steering farther into a turn. NRDR smoothly moves from the on-center number to this final number."
    ) + " " + self._latch_notice()

  def _raw_description(self) -> str:
    if not self._raw_available():
      return tr("Unavailable for this car. NRDR's raw road-learned values currently exist only for the Honda Clarity.")
    return tr(" ".join((
      "Uses NRDR's fixed curve made directly from logged Clarity steering angles. It does not learn while you drive.",
      "The audited curve now reaches its 435.7° near-lock point instead of holding the 247.5° point through the rest of the rack.",
    ))) + " " + self._latch_notice()

  def _firmware_description(self) -> str:
    if not self._firmware_available():
      return tr("Unavailable because this car's exact EPS firmware map was not recognized. Stock geometry is used safely instead.")
    return tr(
      "Uses the variable steering shape read from this car's exact EPS firmware. The car's normal steer ratio stays as the anchor."
    ) + " " + self._latch_notice()

  def _sync_switches(self) -> None:
    for mode, item in self._mode_items.items():
      item.action_item.set_state(self._mode is mode)

  def _update_state(self):
    super()._update_state()
    self._mode = parse_steer_ratio_mode(ui_state.params.get("NrdrSteerRatioMode", return_default=True))
    self._sync_switches()

    availability = {
      SteerRatioMode.COMMA: True,
      SteerRatioMode.NRDR_RAW: self._raw_available(),
      SteerRatioMode.FIRMWARE: self._firmware_available(),
    }
    for mode, item in self._mode_items.items():
      selected = self._mode is mode
      # Keep an unavailable selected switch usable so the user
      # can always turn it back off.
      enabled = selected or (self._mode is SteerRatioMode.MANUAL and availability[mode])
      item.action_item.set_enabled(enabled)

    manual_enabled = self._mode is SteerRatioMode.MANUAL and self._manual_available()
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
