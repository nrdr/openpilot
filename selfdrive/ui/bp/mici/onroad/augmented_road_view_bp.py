import time
import pyray as rl
from cereal import messaging, car
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.params import Params
from openpilot.system.ui.lib.application import gui_app
from openpilot.selfdrive.ui.mici.onroad import SIDE_PANEL_WIDTH
from openpilot.selfdrive.ui.mici.onroad.augmented_road_view import AugmentedRoadView
from openpilot.selfdrive.ui.mici.onroad.cameraview import CameraView
from openpilot.selfdrive.ui.bp.mici.onroad.model_renderer_bp import ModelRendererBP
from openpilot.selfdrive.ui.bp.onroad.blindspot_renderer import BlindspotRendererMixin
from openpilot.selfdrive.ui.bp.mici.onroad.hud_renderer_bp import MiciHudRendererBP
from openpilot.selfdrive.ui.bp.mici.onroad.complication import MiciComplication
from openpilot.selfdrive.ui.bp.mici.onroad.confidence_ball_bp import ConfidenceBallMiciBP
from openpilot.selfdrive.ui.ui_state import ui_state, UIStatus
from openpilot.selfdrive.ui.bp.lib.ui_debug_logger import bp_ui_log

# BluePilot: Margin to keep confidence ball inside the MICI rounded border
MICI_BALL_BORDER_MARGIN = 25  # half of 50px MICI border thickness


class MiciAugmentedRoadViewBP(AugmentedRoadView, BlindspotRendererMixin):
  """BluePilot MICI AugmentedRoadView with blindspot indicators, BP HUD, and complication."""

  BLIND_SPOT_WIDTH = 125  # Narrower for MICI's smaller screen

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._init_blindspot()
    self._bp_params = Params()

    # BluePilot: Replace HUD renderer with BP version (brake coloring + powerflow)
    self._hud_renderer = MiciHudRendererBP()

    # BluePilot: Replace confidence ball with BP version on the left (MADS beam + enhanced coloring)
    self._confidence_ball = ConfidenceBallMiciBP()

    # BluePilot: Add lead car complication widget
    self._complication = MiciComplication()

    self._model_renderer = ModelRendererBP()

    # BluePilot: TICI uses AugmentedRoadViewSP for this; upstream MICI no longer does — BP _render still fades the overlay.
    self._fade_alpha_filter = FirstOrderFilter(0, 0.1, 1 / gui_app.target_fps)

  def _render(self, _):
    """Override render to place confidence ball on left, offset driver state, and conditionally hide border."""
    self._switch_stream_if_needed(ui_state.sm)
    self._update_calibration()

    # Create inner content area (camera view, excluding side panel)
    self._content_rect = rl.Rectangle(
      self.rect.x,
      self.rect.y,
      self.rect.width - SIDE_PANEL_WIDTH,
      self.rect.height,
    )

    bp_ui_log.scissor("MiciAugRoadView", "begin",
                       x=int(self._content_rect.x), y=int(self._content_rect.y),
                       w=int(self._content_rect.width), h=int(self._content_rect.height))
    rl.begin_scissor_mode(
      int(self._content_rect.x),
      int(self._content_rect.y),
      int(self._content_rect.width),
      int(self._content_rect.height)
    )

    # Render the base camera view
    CameraView._render(self, self._content_rect)

    # Model overlays
    self._model_renderer.render(self._content_rect)

    # Fade out bottom overlay (only when engaged)
    fade_alpha = self._fade_alpha_filter.update(ui_state.status != UIStatus.DISENGAGED)
    if fade_alpha > 1e-2:
      rl.draw_texture_ex(self._fade_texture, rl.Vector2(self._content_rect.x, self._content_rect.y), 0.0, 1.0,
                         rl.Color(255, 255, 255, int(255 * fade_alpha)))

    alert_to_render, not_animating_out = self._alert_renderer.will_render()

    # BluePilot: Driver monitor pushed right by ball width
    should_draw_dmoji = (not self._hud_renderer.drawing_top_icons() and ui_state.is_onroad() and
                         (ui_state.status != UIStatus.DISENGAGED or ui_state.always_on_dm))
    self._driver_state_renderer.set_should_draw(should_draw_dmoji)
    self._driver_state_renderer.set_position(self._rect.x + 16, self._rect.y + 10)
    self._driver_state_renderer.render()

    # HUD and alerts
    self._hud_renderer.set_can_draw_top_icons(alert_to_render is None)
    self._hud_renderer.set_wheel_critical_icon(alert_to_render is not None and not not_animating_out and
                                               alert_to_render.visual_alert == car.CarControl.HUDControl.VisualAlert.steerRequired)
    if ui_state.started:
      self._alert_renderer.render(self._content_rect)
    self._hud_renderer.render(self._content_rect)

    bp_ui_log.scissor("MiciAugRoadView", "end")
    rl.end_scissor_mode()

    # BluePilot: Conditionally draw MICI rounded border
    if not self._bp_params.get_bool("BPHideOnroadBorder"):
      rl.draw_rectangle_rounded_lines_ex(self._content_rect, 0.2 * 1.02, 10, 50, rl.BLACK)

    # BluePilot: Blindspot indicators (outside scissor, on screen edges)
    self._draw_blindspot_screen_edges(self.rect, self.BLIND_SPOT_WIDTH)

    # BluePilot: Lead car complication widget
    self._complication.render(self._content_rect)

    ball_rect = rl.Rectangle(
      self._rect.x + self._rect.width - SIDE_PANEL_WIDTH,
      self._content_rect.y,
      SIDE_PANEL_WIDTH,
      self._content_rect.height,
    )
    self._confidence_ball.render(ball_rect)

    # Bookmark icon
    self._bookmark_icon.render(self.rect)

    # Offroad label
    if not ui_state.started:
      rl.draw_rectangle(int(self.rect.x), int(self.rect.y), int(self.rect.width), int(self.rect.height), rl.Color(0, 0, 0, 175))
      self._offroad_label.render(self._content_rect)
