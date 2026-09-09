"""Offroad-only mici controls for confidence-gated lane centering."""

from openpilot.selfdrive.ui.layouts.settings.common import (
  LANE_CENTER_OFFSET_LABELS,
  LANE_CENTER_OFFSET_VALUES,
  LANE_CENTERING_E2E_AUTHORITY_LABELS,
  LANE_CENTERING_E2E_AUTHORITY_VALUES,
  closest_value_index,
)
from openpilot.selfdrive.ui.mici.widgets.button import BigMultiToggle, BigToggle
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.widgets.scroller import NavScroller


class LaneCenteringLayoutMici(NavScroller):
  def __init__(self):
    super().__init__()

    self._lane_centering_toggle = BigToggle(
      "lane centering",
      "offroad only",
      initial_state=ui_state.params.get_bool("LaneCentering"),
      toggle_callback=self._on_lane_centering,
    )
    self._pause_on_signal_toggle = BigToggle(
      "pause on turn signal",
      initial_state=bool(ui_state.params.get("LaneCenteringPauseOnSignal", return_default=True)),
      toggle_callback=self._on_pause_on_signal,
    )
    self._center_offset_toggle = BigMultiToggle(
      "center offset",
      list(LANE_CENTER_OFFSET_LABELS),
      select_callback=self._on_center_offset,
      font_size=40,
    )
    self._model_authority_toggle = BigMultiToggle(
      "model path authority",
      list(LANE_CENTERING_E2E_AUTHORITY_LABELS),
      select_callback=self._on_model_authority,
      font_size=40,
    )

    self._lane_centering_toggle.set_enabled(self._write_allowed)
    for item in (self._pause_on_signal_toggle, self._center_offset_toggle, self._model_authority_toggle):
      item.set_enabled(self._settings_writable)

    self._scroller.add_widgets([
      self._lane_centering_toggle,
      self._pause_on_signal_toggle,
      self._center_offset_toggle,
      self._model_authority_toggle,
    ])
    ui_state.add_offroad_transition_callback(self._refresh)

  @staticmethod
  def _write_allowed() -> bool:
    return ui_state.is_offroad() and not ui_state.engaged

  def _settings_writable(self) -> bool:
    return self._write_allowed() and ui_state.params.get_bool("LaneCentering")

  def _on_lane_centering(self, state: bool) -> None:
    if not self._write_allowed():
      self._lane_centering_toggle.set_checked(ui_state.params.get_bool("LaneCentering"))
      return
    ui_state.params.put_bool("LaneCentering", state, block=True)

  def _on_pause_on_signal(self, state: bool) -> None:
    if not self._settings_writable():
      self._refresh()
      return
    ui_state.params.put_bool("LaneCenteringPauseOnSignal", state, block=True)

  def _on_center_offset(self, value: str) -> None:
    if not self._settings_writable():
      self._refresh()
      return
    ui_state.params.put("LaneCenterOffset", LANE_CENTER_OFFSET_VALUES[LANE_CENTER_OFFSET_LABELS.index(value)], block=True)

  def _on_model_authority(self, value: str) -> None:
    if not self._settings_writable():
      self._refresh()
      return
    index = LANE_CENTERING_E2E_AUTHORITY_LABELS.index(value)
    ui_state.params.put("LaneCenteringE2EAuthority", LANE_CENTERING_E2E_AUTHORITY_VALUES[index], block=True)

  def _refresh(self) -> None:
    self._lane_centering_toggle.set_checked(ui_state.params.get_bool("LaneCentering"))
    self._pause_on_signal_toggle.set_checked(
      bool(ui_state.params.get("LaneCenteringPauseOnSignal", return_default=True)))
    self._center_offset_toggle.set_value(
      LANE_CENTER_OFFSET_LABELS[closest_value_index(
        LANE_CENTER_OFFSET_VALUES, ui_state.params.get("LaneCenterOffset", return_default=True))])
    self._model_authority_toggle.set_value(
      LANE_CENTERING_E2E_AUTHORITY_LABELS[closest_value_index(
        LANE_CENTERING_E2E_AUTHORITY_VALUES, ui_state.params.get("LaneCenteringE2EAuthority", return_default=True))])

  def show_event(self):
    super().show_event()
    self._refresh()
