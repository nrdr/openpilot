"""BP-styled QR dialog for the BluePilot web server.

Replaces selfdrive/ui/bp/mici/widgets/web_server_qr_dialog.py with a layout
that matches the new BP design language: radial backdrop, BP topbar with
chevron back, QR centered on the left, URL + caption + a BP toggle on the
right. The QR generation, IP detection, and toggle behavior are reused
verbatim from the existing dialog.
"""
import pyray as rl
from collections.abc import Callable

from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets.label import UnifiedLabel
from openpilot.system.ui.widgets.nav_widget import NavWidget

from openpilot.selfdrive.ui.bp.mici.widgets.bg_radial import BPRadialBackground
from openpilot.selfdrive.ui.bp.mici.widgets.bp_topbar import BPTopbar, TOPBAR_HEIGHT
from openpilot.selfdrive.ui.bp.mici.widgets.cards import BigToggleCard, _fit_single_line
from openpilot.selfdrive.ui.bp.mici.widgets import bp_palette as P

# Reuse the URL / IP / QR-image helpers from the existing dialog so we don't
# fork that logic. Only the rendering layer is reimplemented here.
from openpilot.selfdrive.ui.bp.mici.widgets.web_server_qr_dialog import (
  WebServerQRDialog as _LegacyQRDialog,
)


class BPWebServerQRDialog(NavWidget):
  """BP-styled QR display + disable toggle."""

  PADDING = 14

  def __init__(self, back_callback: Callable | None = None):
    super().__init__()
    if back_callback is not None:
      self.set_back_callback(back_callback)
    self.set_rect(rl.Rectangle(0, 0, gui_app.width, gui_app.height))
    self._params = Params()

    # Borrow the legacy QR generation logic by composition.
    self._gen = _LegacyQRDialog(back_callback=back_callback or (lambda: None))
    # We don't render the legacy widget — only call its helpers — so detach
    # its callbacks to avoid surprising side effects.
    self._gen._handle_toggle = lambda *_a, **_k: None

    self._bg = self._child(BPRadialBackground())
    self._topbar = self._child(BPTopbar(title="Web Server", on_back=self._on_back))

    self._url_label = UnifiedLabel(
      "", font_size=22, font_weight=FontWeight.BOLD, text_color=P.ACCENT2,
      letter_spacing=0.02, max_width=380, wrap_text=False, elide=False,
    )
    self._scan_label = UnifiedLabel(
      "scan to open", font_size=20, font_weight=FontWeight.MEDIUM,
      text_color=P.MUTED, letter_spacing=0.04,
      max_width=380, wrap_text=False,
    )
    self._error_label = UnifiedLabel(
      "no Wi-Fi connection", font_size=24, font_weight=FontWeight.BOLD,
      text_color=P.DANGER, max_width=380, wrap_text=False,
    )

    # BP toggle for the disable action — same Params key as the legacy widget.
    self._disable_toggle = self._child(BigToggleCard(
      "Web Server", "Tap to disable.", param_key="EnableWebRoutesServer",
      on_change=self._on_toggle_change,
    ))

  # ---- handlers ----
  def _on_back(self):
    gui_app.pop_widget()

  def _on_toggle_change(self, enabled: bool):
    if not enabled:
      self._on_back()

  # ---- render ----
  def _render(self, _):
    r = self._rect
    self._bg.render(r)

    # Topbar
    self._topbar.render(rl.Rectangle(r.x, r.y, r.width, TOPBAR_HEIGHT))

    # Body area
    body_y = r.y + TOPBAR_HEIGHT
    body_h = r.height - TOPBAR_HEIGHT - 8

    # ---- Left column: QR + URL/caption ----
    try:
      self._gen._generate_qr_code()
      url = self._gen._get_server_url()
    except Exception as e:
      cloudlog.warning(f"BPQRDialog: gen failed: {e}")
      url = ""

    # QR sizing — fit a square inside the body height with caption underneath.
    caption_h = 22 + 4 + 20 + 8  # url + gap + scan caption + bottom margin
    qr_max = body_h - caption_h - 8
    qr_size = max(60, min(qr_max, 160))
    qr_x = r.x + self.PADDING
    qr_y = body_y + (body_h - (qr_size + caption_h)) / 2

    if self._gen._qr_texture is not None and self._gen._qr_texture.id != 0:
      scale = qr_size / max(1, self._gen._qr_texture.height)
      rl.draw_texture_ex(self._gen._qr_texture, rl.Vector2(qr_x, qr_y), 0.0, scale, rl.WHITE)
    else:
      # No connection — show error in QR area
      err_x = qr_x + (qr_size - 200) / 2
      err_y = qr_y + (qr_size - 24) / 2
      self._error_label.set_position(err_x, err_y)
      self._error_label.render()

    # URL + caption under the QR
    if url:
      _fit_single_line(self._url_label, 22, qr_size + 60, min_size=14)
      self._url_label.set_text(url)
      self._url_label.set_position(qr_x, qr_y + qr_size + 6)
      self._url_label.render()

      self._scan_label.set_position(qr_x, qr_y + qr_size + 30)
      self._scan_label.render()

    # ---- Right column: BP-styled disable toggle ----
    right_x = qr_x + qr_size + 20
    right_w = r.width - right_x - self.PADDING
    self._disable_toggle.render(rl.Rectangle(right_x, body_y + 6, right_w, body_h - 12))
