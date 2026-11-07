"""Live mici controls for confidence-gated lane centering."""

from openpilot.cereal import custom
from openpilot.nrdr.features.lateral.lane_guidance import (
  LaneGuidanceMode,
  lane_guidance_mode_from_params,
  set_lane_guidance_mode,
)
from openpilot.selfdrive.ui.layouts.settings.common import (
  LANE_CENTER_OFFSET_LABELS,
  LANE_CENTER_OFFSET_VALUES,
  LANE_CENTERING_E2E_AUTHORITY_LABELS,
  LANE_CENTERING_E2E_AUTHORITY_VALUES,
  LANE_CENTERING_MIN_SPEED_LABELS,
  LANE_CENTERING_MIN_SPEED_VALUES,
  LANE_CENTERING_STRENGTH_LABELS,
  LANE_CENTERING_STRENGTH_VALUES,
  closest_value_index,
)
from openpilot.selfdrive.controls.lib.lane_centering import lane_centering_min_speed_mph, lane_centering_strength
from openpilot.selfdrive.ui.mici.widgets.button import BigMultiToggle, BigToggle
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.nrdr.params.tuning_policy import tuning_write_allowed
from openpilot.nrdr.ui.lane_guidance import LANE_GUIDANCE_LABELS, LANE_GUIDANCE_MODES
from openpilot.system.ui.widgets.scroller import NavScroller


class LaneCenteringLayoutMici(NavScroller):
  def __init__(self):
    super().__init__()

    self._lane_guidance_mode = BigMultiToggle(
      "Lane Centering Method",
      list(LANE_GUIDANCE_LABELS),
      select_callback=self._on_lane_guidance_mode,
      font_size=40,
      description="choose one method; Sunny needs a custom model; tuning below applies to Star",
    )
    self._pause_on_signal_toggle = BigToggle(
      "fade on turn signal",
      initial_state=bool(ui_state.params.get("LaneCenteringPauseOnSignal", return_default=True)),
      toggle_callback=self._on_pause_on_signal,
    )
    self._minimum_speed_toggle = BigMultiToggle(
      "minimum speed",
      list(LANE_CENTERING_MIN_SPEED_LABELS),
      select_callback=self._on_minimum_speed,
      font_size=40,
    )
    self._center_offset_toggle = BigMultiToggle(
      "center offset",
      list(LANE_CENTER_OFFSET_LABELS),
      select_callback=self._on_center_offset,
      font_size=40,
    )
    self._strength_toggle = BigMultiToggle(
      "lane-centering strength",
      list(LANE_CENTERING_STRENGTH_LABELS),
      select_callback=self._on_strength,
      font_size=40,
    )
    self._model_authority_toggle = BigMultiToggle(
      "model break-in",
      list(LANE_CENTERING_E2E_AUTHORITY_LABELS),
      select_callback=self._on_model_authority,
      font_size=40,
    )

    self._lane_guidance_mode.set_enabled(self._write_allowed)
    for item in (self._minimum_speed_toggle, self._pause_on_signal_toggle, self._center_offset_toggle,
                 self._strength_toggle, self._model_authority_toggle):
      item.set_enabled(self._settings_writable)

    self._scroller.add_widgets([
      self._lane_guidance_mode,
      self._minimum_speed_toggle,
      self._pause_on_signal_toggle,
      self._center_offset_toggle,
      self._strength_toggle,
      self._model_authority_toggle,
    ])
    ui_state.add_offroad_transition_callback(self._refresh)

  @staticmethod
  def _write_allowed() -> bool:
    return tuning_write_allowed(ui_state.params, "LaneGuidanceMode", is_offroad=ui_state.is_offroad())

  @staticmethod
  def _custom_model_active() -> bool | None:
    runner = ui_state.params.get("ModelRunnerTypeCache")
    if runner is None:
      # This derived cache is cleared during the onroad transition. Missing is
      # temporarily unknown, not proof that the active runner is stock.
      return None
    return runner == custom.ModelManagerSP.Runner.tinygrad

  def _settings_writable(self) -> bool:
    return self._write_allowed() and lane_guidance_mode_from_params(ui_state.params) == LaneGuidanceMode.NRDR

  def _on_lane_guidance_mode(self, value: str) -> None:
    if not self._write_allowed():
      self._refresh()
      return
    mode = LANE_GUIDANCE_MODES[LANE_GUIDANCE_LABELS.index(value)]
    custom_model_active = self._custom_model_active()
    if mode == LaneGuidanceMode.BLENDFUL and custom_model_active is not True:
      # BigMultiToggle cycles instead of exposing individually disabled
      # buttons. Skip Sunny when unavailable OR temporarily unknown, so the
      # Off -> Sunny -> Star display order cannot trap the user at Off.
      mode = LaneGuidanceMode.NRDR
    set_lane_guidance_mode(ui_state.params, mode)
    self._refresh()

  def _on_pause_on_signal(self, state: bool) -> None:
    if not self._settings_writable():
      self._refresh()
      return
    ui_state.params.put_bool("LaneCenteringPauseOnSignal", state, block=True)

  def _on_minimum_speed(self, value: str) -> None:
    if not self._settings_writable():
      self._refresh()
      return
    ui_state.params.put("LaneCenteringMinSpeed", LANE_CENTERING_MIN_SPEED_VALUES[LANE_CENTERING_MIN_SPEED_LABELS.index(value)], block=True)

  def _on_center_offset(self, value: str) -> None:
    if not self._settings_writable():
      self._refresh()
      return
    ui_state.params.put("LaneCenterOffset", LANE_CENTER_OFFSET_VALUES[LANE_CENTER_OFFSET_LABELS.index(value)], block=True)

  def _on_strength(self, value: str) -> None:
    if not self._settings_writable():
      self._refresh()
      return
    index = LANE_CENTERING_STRENGTH_LABELS.index(value)
    ui_state.params.put("LaneCenteringStrength", LANE_CENTERING_STRENGTH_VALUES[index], block=True)

  def _on_model_authority(self, value: str) -> None:
    if not self._settings_writable():
      self._refresh()
      return
    index = LANE_CENTERING_E2E_AUTHORITY_LABELS.index(value)
    ui_state.params.put("LaneCenteringE2EAuthority", LANE_CENTERING_E2E_AUTHORITY_VALUES[index], block=True)

  def _refresh(self) -> None:
    mode = lane_guidance_mode_from_params(ui_state.params)
    if mode == LaneGuidanceMode.BLENDFUL and self._custom_model_active() is False:
      # Do not merely disguise an unavailable saved mode. Persist the safe
      # state once a non-tinygrad runner is confirmed. A missing transition
      # cache is left untouched until the manager republishes it.
      set_lane_guidance_mode(ui_state.params, LaneGuidanceMode.MODEL_ONLY)
      mode = LaneGuidanceMode.MODEL_ONLY
    self._lane_guidance_mode.set_value(LANE_GUIDANCE_LABELS[LANE_GUIDANCE_MODES.index(mode)])
    self._pause_on_signal_toggle.set_checked(
      bool(ui_state.params.get("LaneCenteringPauseOnSignal", return_default=True)))
    self._minimum_speed_toggle.set_value(
      LANE_CENTERING_MIN_SPEED_LABELS[closest_value_index(
        LANE_CENTERING_MIN_SPEED_VALUES,
        lane_centering_min_speed_mph(ui_state.params.get("LaneCenteringMinSpeed", return_default=True)))])
    self._center_offset_toggle.set_value(
      LANE_CENTER_OFFSET_LABELS[closest_value_index(
        LANE_CENTER_OFFSET_VALUES, ui_state.params.get("LaneCenterOffset", return_default=True))])
    self._strength_toggle.set_value(
      LANE_CENTERING_STRENGTH_LABELS[closest_value_index(
        LANE_CENTERING_STRENGTH_VALUES,
        lane_centering_strength(ui_state.params.get("LaneCenteringStrength", return_default=True)))])
    self._model_authority_toggle.set_value(
      LANE_CENTERING_E2E_AUTHORITY_LABELS[closest_value_index(
        LANE_CENTERING_E2E_AUTHORITY_VALUES, ui_state.params.get("LaneCenteringE2EAuthority", return_default=True))])

  def show_event(self):
    super().show_event()
    self._refresh()
