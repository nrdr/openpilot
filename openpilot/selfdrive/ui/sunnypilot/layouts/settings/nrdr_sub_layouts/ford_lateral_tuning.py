from collections.abc import Callable
import pyray as rl

from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, option_item_sp


class FordLateralTuningLayout(Widget):
  def __init__(self, back_btn_callback: Callable):
    super().__init__()
    self._back_button = NavButton(tr("Back"))
    self._back_button.set_click_callback(back_btn_callback)

    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=False, spacing=0)

  def _initialize_items(self):
    self._ford_oem_lateral = toggle_item_sp(
      param="NrdrFordOemLateral",
      title=lambda: tr("Ford: OEM-Style Lateral (Default: OFF)"),
      description=lambda: tr(
        "Ford only. Replaces stock curvature-only steering with Ford's full four-signal command (adds curvature-rate plus a "
        + "lane-centering path-angle), the way the factory system actually drives. Targets the two stock complaints: the wheel "
        + "fighting you after you grab it, and running out of steering authority in vigorous turns. OFF = stock curvature-only "
        + "path, completely unchanged. BETA - first test on an empty road with your hands ready. No effect on non-Ford cars."
      ),
    )

    self._ford_human_turn = toggle_item_sp(
      param="NrdrFordHumanTurn",
      title=lambda: tr("Ford: Human Turn Detection (Default: ON)"),
      description=lambda: tr(
        "When you hold the wheel into a turn past 45 degrees, openpilot stops commanding steering so it isn't fighting you, then "
        + "ramps smoothly back in when you let go instead of snapping. This is the fix for 'the wheel tries to throw me off the "
        + "road' after you touch it. Only active when OEM-Style Lateral is on."
      ),
    )

    self._ford_lane_positioning = toggle_item_sp(
      param="NrdrFordLanePositioning",
      title=lambda: tr("Ford: Lane Positioning (Default: ON)"),
      description=lambda: tr(
        "Drives the path-angle signal with a lane-centering PID for extra steering authority and tighter in-lane position - the "
        + "main lever against 'runs out of torque'. Engages at highway speed and steps aside during auto lane changes. Only "
        + "active when OEM-Style Lateral is on."
      ),
    )

    self._ford_lane_pos_gain = option_item_sp(
      param="NrdrFordLanePosGain",
      title=lambda: tr("Ford: Lane Positioning Strength (Default: 100%)"),
      min_value=0,
      max_value=300,
      value_change_step=5,
      description=lambda: tr(
        "How hard the lane-centering path-angle pulls toward lane center. 100% = baseline. Raise for stronger centering, lower if "
        + "it feels busy. Only used when Lane Positioning is on."
      ),
      label_callback=lambda value: f"{value}%",
    )

    self._ford_max_lat_accel = option_item_sp(
      param="NrdrFordMaxLatAccel",
      title=lambda: tr("Ford: Max Lateral Accel (Default: 2.40)"),
      min_value=200,
      max_value=350,
      value_change_step=5,
      description=lambda: tr(
        "Raises the lateral-acceleration ceiling that caps how hard the car will corner - the most direct knob for 'runs out of "
        + "torque'. Stock is ~2.4 m/s^2, set low on purpose because the safety model can't see road banking. Raising it gives more "
        + "cornering authority but removes that conservative margin; increase in small steps and validate on-road. Only used when "
        + "OEM-Style Lateral is on."
      ),
      label_callback=lambda value: f"{value / 100:.2f} m/s2",
      use_float_scaling=True,
    )

    return [
      self._ford_oem_lateral,
      self._ford_human_turn,
      self._ford_lane_positioning,
      self._ford_lane_pos_gain,
      self._ford_max_lat_accel,
    ]

  def _update_state(self):
    super()._update_state()
    ford_oem_enabled = self._ford_oem_lateral.action_item.get_state()
    self._ford_human_turn.set_visible(ford_oem_enabled)
    self._ford_lane_positioning.set_visible(ford_oem_enabled)
    self._ford_max_lat_accel.set_visible(ford_oem_enabled)
    self._ford_lane_pos_gain.set_visible(ford_oem_enabled and self._ford_lane_positioning.action_item.get_state())

  def _render(self, rect):
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40, rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    self._scroller.show_event()
