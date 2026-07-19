"""
nrdr Show Footage sub-panel.

Pick a drive, get a QR code that points your phone at the copyparty file server
for that drive's video files. Built for the roadside "can I see the footage?"
moment: no laptop, no SSH, no cloud - phone joins the device hotspot, scans the
code, plays qcamera.ts (or grabs fcamera.hevc for full res, VLC plays it).
"""
import datetime
import os
import re
import socket
import subprocess

import numpy as np
import pyray as rl
import qrcode

from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.hardware.hw import Paths
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.lib.wrap_text import wrap_text
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.button import IconButton
from openpilot.system.ui.widgets.list_view import button_item, ListItem
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, LineSeparatorSP

COPYPARTY_PORT = 8080      # matches -p in process_config copyparty args
ROUTES_MOUNT = "/routes"   # copyparty -v mount of Paths.log_root()
MAX_ROUTES = 15
SEGMENT_RE = re.compile(r"^(.+)--(\d+)$")


def _device_ip() -> str:
  """Best address for a PHONE to reach this device. Prefer the hotspot subnet
  (192.168.43.x), then any wlan address; the default-route trick is only a
  fallback because with LTE up it returns an address no phone can reach."""
  try:
    out = subprocess.check_output(["ip", "-4", "-o", "addr"], encoding="utf8", timeout=2)
    addrs: list[tuple[str, str]] = []
    for line in out.splitlines():
      parts = line.split()
      if len(parts) >= 4 and parts[2] == "inet":
        addrs.append((parts[1], parts[3].split("/")[0]))
    for _ifname, ip in addrs:
      if ip.startswith("192.168.43."):
        return ip
    for ifname, ip in addrs:
      if ifname.startswith("wlan"):
        return ip
  except Exception:
    pass
  try:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
      s.connect(("8.8.8.8", 80))
      return s.getsockname()[0]
  except Exception:
    return "--"


def _list_routes() -> list[dict]:
  """Group realdata segment dirs into routes, newest first."""
  routes: dict[str, dict] = {}
  try:
    with os.scandir(Paths.log_root()) as it:
      for entry in it:
        if not entry.is_dir():
          continue
        m = SEGMENT_RE.match(entry.name)
        if m is None:
          continue
        route_id, seg = m.group(1), int(m.group(2))
        try:
          mtime = entry.stat().st_mtime
        except OSError:
          mtime = 0.0
        rec = routes.setdefault(route_id, {"route": route_id, "segments": 0, "mtime": 0.0,
                                           "newest_seg_dir": entry.name, "newest_seg": -1})
        rec["segments"] += 1
        rec["mtime"] = max(rec["mtime"], mtime)
        if seg > rec["newest_seg"]:
          rec["newest_seg"] = seg
          rec["newest_seg_dir"] = entry.name
  except OSError:
    return []
  return sorted(routes.values(), key=lambda r: r["mtime"], reverse=True)[:MAX_ROUTES]


class FootageQrDialog(Widget):
  """Full-screen QR pointing the phone at this drive's files on copyparty."""

  def __init__(self, route_label: str, seg_dir: str):
    super().__init__()
    self._route_label = route_label
    self._seg_dir = seg_dir
    self._url = f"http://{_device_ip()}:{COPYPARTY_PORT}{ROUTES_MOUNT}/{seg_dir}/"
    self.qr_texture: rl.Texture | None = None
    self._generate_qr_code()
    self._close_btn = IconButton(gui_app.texture("icons/close.png", 80, 80))
    self._close_btn.set_click_callback(gui_app.pop_widget)

  def _generate_qr_code(self) -> None:
    try:
      qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
      qr.add_data(self._url)
      qr.make(fit=True)

      pil_img = qr.make_image(fill_color="black", back_color="white").convert('RGBA')
      img_array = np.array(pil_img, dtype=np.uint8)

      if self.qr_texture and self.qr_texture.id != 0:
        rl.unload_texture(self.qr_texture)

      rl_image = rl.Image()
      rl_image.data = rl.ffi.cast("void *", img_array.ctypes.data)
      rl_image.width = pil_img.width
      rl_image.height = pil_img.height
      rl_image.mipmaps = 1
      rl_image.format = rl.PixelFormat.PIXELFORMAT_UNCOMPRESSED_R8G8B8A8

      self.qr_texture = rl.load_texture_from_image(rl_image)
    except Exception:
      cloudlog.exception("footage QR generation failed")
      self.qr_texture = None

  def _render(self, rect: rl.Rectangle) -> int:
    rl.clear_background(rl.Color(224, 224, 224, 255))

    margin = 70
    content_rect = rl.Rectangle(rect.x + margin, rect.y + margin, rect.width - 2 * margin, rect.height - 2 * margin)
    y = content_rect.y

    close_size = 80
    pad = 20
    close_rect = rl.Rectangle(content_rect.x - pad, y - pad, close_size + pad * 2, close_size + pad * 2)
    self._close_btn.render(close_rect)
    y += close_size + 40

    title_font = gui_app.font(FontWeight.NORMAL)
    left_width = int(content_rect.width * 0.5 - 15)

    title_wrapped = wrap_text(title_font, tr("Show Footage: ") + self._route_label, 70, left_width)
    rl.draw_text_ex(title_font, "\n".join(title_wrapped), rl.Vector2(content_rect.x, y), 70, 0.0, rl.BLACK)
    y += len(title_wrapped) * 70 + 50

    self._render_instructions(rl.Rectangle(content_rect.x, y, left_width,
                                           content_rect.height - (y - content_rect.y)))

    right_width = content_rect.width // 2 - 20
    qr_size = min(right_width, content_rect.height) - 40
    qr_x = content_rect.x + left_width + 40 + (right_width - qr_size) // 2
    self._render_qr_code(rl.Rectangle(qr_x, content_rect.y, qr_size, qr_size))

    return -1

  def _render_instructions(self, rect: rl.Rectangle) -> None:
    instructions = [
      tr("Join this device's hotspot (or the same Wi-Fi) on your phone"),
      tr("Scan the QR code, or type the address below"),
      tr("Tap qcamera.ts to play. fcamera.hevc is the full-resolution file (VLC plays it)."),
    ]

    font = gui_app.font(FontWeight.BOLD)
    y = rect.y

    for i, text in enumerate(instructions):
      circle_radius = 25
      circle_x = rect.x + circle_radius + 15
      text_x = rect.x + circle_radius * 2 + 40
      text_width = rect.width - (circle_radius * 2 + 40)

      wrapped = wrap_text(font, text, 44, int(text_width))
      text_height = len(wrapped) * 44
      circle_y = y + text_height // 2

      rl.draw_circle(int(circle_x), int(circle_y), circle_radius, rl.Color(70, 70, 70, 255))
      number = str(i + 1)
      number_size = measure_text_cached(font, number, 30)
      rl.draw_text_ex(font, number, (int(circle_x - number_size.x // 2), int(circle_y - number_size.y // 2)), 30, 0, rl.WHITE)

      rl.draw_text_ex(font, "\n".join(wrapped), rl.Vector2(text_x, y), 44, 0.0, rl.BLACK)
      y += text_height + 40

    url_font = gui_app.font(FontWeight.MEDIUM)
    url_wrapped = wrap_text(url_font, self._url, 40, int(rect.width))
    rl.draw_text_ex(url_font, "\n".join(url_wrapped), rl.Vector2(rect.x, y + 10), 40, 0.0, rl.Color(30, 90, 200, 255))

  def _render_qr_code(self, rect: rl.Rectangle) -> None:
    if not self.qr_texture:
      rl.draw_rectangle_rounded(rect, 0.1, 20, rl.Color(240, 240, 240, 255))
      rl.draw_text_ex(gui_app.font(FontWeight.BOLD), tr("QR Code Error"),
                      rl.Vector2(rect.x + 20, rect.y + rect.height // 2 - 15), 30, 0.0, rl.RED)
      return
    source = rl.Rectangle(0, 0, self.qr_texture.width, self.qr_texture.height)
    rl.draw_texture_pro(self.qr_texture, source, rect, rl.Vector2(0, 0), 0, rl.WHITE)

  def __del__(self):
    if self.qr_texture and self.qr_texture.id != 0:
      rl.unload_texture(self.qr_texture)


class FootageLayout(Widget):
  def __init__(self, back_btn_callback):
    super().__init__()
    self._back_button = NavButton(tr("Back"))
    self._back_button.set_click_callback(back_btn_callback)

    self._server_toggle = toggle_item_sp(
      param="EnableCopyparty",
      title=lambda: tr("File Server (Default: ON)"),
      description=lambda: tr("The QR links below are served by the copyparty file server. It must be ON, and it only runs while the car is off (ignition off). Same toggle as in Developer."),
    )

    self._scroller = Scroller([self._server_toggle], line_separator=False, spacing=0)

  def _open_route_qr(self, route_label: str, seg_dir: str):
    gui_app.push_widget(FootageQrDialog(route_label, seg_dir))

  def _build_route_items(self) -> list:
    items: list = []
    for rec in _list_routes():
      when = datetime.datetime.fromtimestamp(rec["mtime"]).strftime("%b %d, %I:%M %p")
      label = f"{when}  (~{rec['segments']} min)"
      seg_dir = rec["newest_seg_dir"]
      items.append(button_item(
        label,
        lambda: tr("QR"),
        rec["route"],
        callback=(lambda rl_=label, sd_=seg_dir: self._open_route_qr(rl_, sd_)),
      ))
    if not items:
      items.append(ListItem(title=lambda: tr("No drives recorded yet.")))
    return items

  def show_event(self):
    # Rebuild the drive list every time the panel is opened.
    self._scroller = Scroller([self._server_toggle, LineSeparatorSP(40), *self._build_route_items()],
                              line_separator=False, spacing=0)
    self._scroller.show_event()

  def _update_state(self):
    super()._update_state()
    # Dim the list while the file server is off and the car is on.
    self._server_toggle.action_item.set_enabled(ui_state.is_offroad())

  def _render(self, rect):
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40, rect.width,
                                rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)
