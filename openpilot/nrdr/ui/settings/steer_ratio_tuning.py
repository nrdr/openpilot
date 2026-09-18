from collections.abc import Callable

import pyray as rl

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.nrdr.features.lateral.honda_vgr import get_honda_vgr_profile
from openpilot.nrdr.features.lateral.steer_ratio_tuning import (
  SteerRatioMode, get_raw_steer_ratio_profile, get_steer_ratio_metadata, resolve_steer_ratio_selection,
)
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.sunnypilot.widgets.list_view import (
  LineSeparatorSP, ListItemSP, multiple_button_item_sp, option_item_sp, toggle_item_sp,
)


class SteerRatioTuningLayout(Widget):
  def __init__(self, back_btn_callback: Callable):
    super().__init__()
    self._back_button = NavButton(tr("Back"))
    self._back_button.set_click_callback(back_btn_callback)
    self._hybrid = toggle_item_sp(
      title=lambda: tr("Enable Hybrid Steer Ratio"), param="NrdrSteerRatioHybrid",
      description=lambda: tr("Experimental: configure while parked. Blend A into B across 5 degrees. " +
                             "OFF keeps your existing single-source selection. No speed-based switch."),
    )
    self._source_a = self._source_item("NrdrSteerRatioMode", "Ratio A — Near Center / Single Source")
    self._blend_start = option_item_sp(
      title=lambda: tr("Blend Starts At"), param="NrdrSteerRatioBlendStart", min_value=0, max_value=180,
      value_change_step=1, label_callback=lambda value: f"{value}–{value + 5}°",
      description=lambda: tr("Angle from straight ahead, in either direction. Source B takes over fully 5 degrees later. " +
                             "The same transition is followed in reverse when unwinding."),
    )
    self._source_b = self._source_item("NrdrSteerRatioSourceB", "Ratio B — Beyond the Blend")
    self._manual_center = option_item_sp(
      param="NrdrSteerRatioManualCenter", title=lambda: tr("Manual Override On-Center Ratio (Default: 15.38)"),
      min_value=800, max_value=2500, value_change_step=1, use_float_scaling=True,
      label_callback=lambda value: f"{value / 100:.2f}",
      description=lambda: tr("The manual ratio with the wheel straight ahead. Used only when A or enabled B is Manual."),
    )
    self._manual_final = option_item_sp(
      param="NrdrSteerRatioManualFinal", title=lambda: tr("Manual Override Final Ratio (Default: 10.93)"),
      min_value=800, max_value=2500, value_change_step=1, use_float_scaling=True,
      label_callback=lambda value: f"{value / 100:.2f}",
      description=lambda: tr("The manual outer-angle ratio. Both Manual sources share these two saved values."),
    )
    self._status = ListItemSP(title=lambda: tr("Configured steer-ratio result"), description=self._status_details)
    self._status.set_right_value(self._status_text)
    self._scroller = Scroller([
      self._hybrid, self._source_a, self._blend_start, self._source_b,
      self._status, LineSeparatorSP(40), self._manual_center, self._manual_final,
    ], line_separator=False, spacing=0)

  @staticmethod
  def _source_item(param: str, title: str) -> ListItemSP:
    return multiple_button_item_sp(
      title=lambda: tr(title), param=param, button_width=215,
      buttons=[lambda: tr("Manual"), lambda: tr("Comma"), lambda: tr("Measured"), lambda: tr("Firmware")],
      description=lambda: tr("Measured uses fixed logged data, not on-road learning. Firmware requires a recognized EPS. " +
                             "Unavailable sources and invalid hybrid blends are rejected."),
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
    is_honda = str(ui_state.CP.brand).lower() == "honda"
    return (
      is_honda and get_steer_ratio_metadata(str(ui_state.CP.carFingerprint)) is not None,
      get_raw_steer_ratio_profile(ui_state.CP) is not None,
      get_honda_vgr_profile(ui_state.CP) is not None,
    )

  def _status_text(self) -> str:
    if ui_state.CP is None:
      return tr("Waiting for car")
    selection = resolve_steer_ratio_selection(ui_state.CP, ui_state.params)
    if not selection.available:
      return tr("Unavailable — see details")
    if selection.hybrid is not None:
      return tr(f"Hybrid · {selection.hybrid.start:g}–{selection.hybrid.end:g}°")
    return tr(selection.effective_label)

  def _status_details(self) -> str:
    if ui_state.CP is None:
      return tr("Waiting for car")
    selection = resolve_steer_ratio_selection(ui_state.CP, ui_state.params)
    detail = selection.effective_label if selection.available else selection.unavailable_reason
    return tr(detail + ". Configured preview, not proof of live controller consumption. " +
              "Comma preview uses the stock anchor; runtime uses its last valid learned ratio. " +
              "Invalid hybrid edits hold the last accepted geometry while active; startup uses stock fallback.")

  def _update_state(self):
    super()._update_state()
    manual_available, raw_available, firmware_available = self._capabilities()
    hybrid = ui_state.params.get_bool("NrdrSteerRatioHybrid")
    allowed = {int(SteerRatioMode.COMMA)}
    allowed.update(int(mode) for mode, available in (
      (SteerRatioMode.MANUAL, manual_available), (SteerRatioMode.NRDR_RAW, raw_available),
      (SteerRatioMode.FIRMWARE, firmware_available),
    ) if available)
    self._hybrid.action_item.set_enabled(manual_available or hybrid)
    self._hybrid.action_item.set_state(hybrid)
    for item, key in ((self._source_a, "NrdrSteerRatioMode"), (self._source_b, "NrdrSteerRatioSourceB")):
      try:
        item.action_item.selected_button = int(ui_state.params.get(key, return_default=True))
      except (TypeError, ValueError):
        item.action_item.selected_button = -1
      item.action_item.set_enabled_buttons(allowed)
    self._source_b.action_item.set_enabled(hybrid)
    self._blend_start.action_item.set_enabled(hybrid)
    manual_enabled = manual_available and (
      self._current_mode() is SteerRatioMode.MANUAL or (hybrid and self._source_b.action_item.selected_button == 0)
    )
    self._manual_center.action_item.set_enabled(manual_enabled)
    self._manual_final.action_item.set_enabled(manual_enabled)

  def _render(self, rect):
    self._back_button.set_position(self._rect.x + 20, self._rect.y + 20)
    self._back_button.render()
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40,
                                rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    self._scroller.show_event()


__all__ = ("SteerRatioTuningLayout",)
