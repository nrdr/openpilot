"""Blue/black radial gradient — paints the BP screen backdrop.

Approximates the mockup's `radial-gradient(120% 140% at 0% 0%, ...)` using
raylib's 4-corner rectangle gradient. Top-left = blue glow, others = deep navy
fading to near-black bottom-right. Cheap to draw every frame.
"""
import pyray as rl

from openpilot.system.ui.widgets import Widget
from openpilot.selfdrive.ui.bp.mici.widgets import bp_palette as P


class BPRadialBackground(Widget):
  def __init__(self):
    super().__init__()

  def _render(self, _):
    r = self._rect
    # 4-corner gradient: top-left blue glow, fade to deep navy/black on the
    # other corners. This is a close visual match for the radial used in the
    # mockup at the size of a 536x240 panel.
    rl.draw_rectangle_gradient_ex(
      r,
      P.BG_TOPLEFT,                               # top-left
      rl.Color(0x06, 0x0E, 0x22, 0xFF),           # bottom-left
      P.BG_DEEP,                                  # bottom-right
      rl.Color(0x08, 0x12, 0x28, 0xFF),           # top-right
    )
