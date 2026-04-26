#!/usr/bin/env python3
"""Drive the BP MICI UI for a few frames and dump screenshots to /tmp.

Used during development of the new BP home (mockups/mici_home.html port) to
verify the runtime render matches the mockup. Mocks ui_state where it would
otherwise hang waiting on cereal services.

Usage:
  python3 mockups/capture_bp_home.py
  open /tmp/bp_home_*.png
"""
import os
import sys
import time
from unittest.mock import MagicMock

import pyray as rl

# --- 1. Stub cereal SubMaster so ui_state.update() doesn't hang on services
import cereal.messaging as messaging
_orig_SubMaster = messaging.SubMaster

class _FakeMsg:
  __slots__ = ('valid', 'updated', '_attrs')
  def __init__(self, **kw):
    self.valid = True
    self.updated = True
    self._attrs = kw
  def __getattr__(self, k):
    if k in self._attrs:
      return self._attrs[k]
    return _FakeMsg()

class _FakeSubMaster:
  def __init__(self, *a, **kw):
    self._frame = 0
    self._messages: dict[str, _FakeMsg] = {}
  def update(self, _t=0):
    self._frame += 1
  def updated(self, *_):
    return False
  def __getitem__(self, k):
    return self._messages.get(k, _FakeMsg())
  def __contains__(self, k):
    return True
  @property
  def frame(self):
    return self._frame
  @property
  def all_alive_and_valid(self):
    return True
  def all_checks(self, *a, **kw):
    return True
  def all_alive(self, *a, **kw):
    return True
  def all_valid(self, *a, **kw):
    return True
  def alive(self, _):
    return True
  def valid(self, _):
    return True
  def recv_frame(self, _):
    return self._frame
  def rcv_time(self, _):
    return time.monotonic()

messaging.SubMaster = _FakeSubMaster
messaging.PubMaster = MagicMock

# --- 2. Now we can import the rest of the UI stack
from cereal import log
from openpilot.system.ui.lib.application import gui_app
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.selfdrive.ui.mici.layouts.main import MiciMainLayout
from openpilot.selfdrive.ui.mici.layouts.home import NETWORK_TYPES  # for sanity

NetworkType = log.DeviceState.NetworkType

OUT_DIR = "/tmp"


def _set_state(net_type, experimental: bool, started: bool = False):
  """Inject state into the global UI state object so the home renders the
  desired mode."""
  ds = _FakeMsg(
    networkType=net_type,
    networkStrength=_FakeMsg(raw=3),
    started=False,
  )
  cs = _FakeMsg(standstill=True)
  ss = _FakeMsg(enabled=False)
  sssp = _FakeMsg(mads=_FakeMsg(enabled=False))
  ui_state.sm._messages.update({
    "deviceState": ds,
    "carState": cs,
    "selfdriveState": ss,
    "selfdriveStateSP": sssp,
  })
  ui_state.started = started
  ui_state.has_longitudinal_control = True
  ui_state.params.put_bool("ExperimentalMode", experimental)


def _capture(name: str, frames: int = 30):
  """Run N frames so animations stabilize, then write a screenshot.

  KNOWN LIMITATION: rl.take_screenshot captures from a buffer that lags
  behind newly-pushed full-screen widgets like dialogs. Captures of
  panel/home content work fine; freshly-pushed dialogs may show the
  underlying screen. Verify dialogs by running ./selfdrive/ui/ui.py
  directly on a real device.
  """
  iterations = 0
  next_break = False
  for should_render in gui_app.render():
    if next_break:
      break
    if should_render:
      iterations += 1
      if iterations >= frames:
        next_break = True
  out_path = f"{OUT_DIR}/bp_home_{name}.png"
  rl.take_screenshot(out_path)
  print(f"[capture] wrote {out_path}")
  return out_path


def main():
  # Allow STOCK_REGRESSION=1 to verify the BP override is gated correctly:
  # in that mode we never instantiate any BP class (sub-panels, panels list).
  stock = bool(int(os.getenv("STOCK_REGRESSION", "0")))

  gui_app.init_window("BP UI Capture")
  main_layout = MiciMainLayout()

  # Disable the interactive timeout so MainLayout._on_interactive_timeout
  # doesn't pop our pushed widgets ~30s into the run.
  from openpilot.selfdrive.ui.ui_state import device as _device
  _device.set_override_interactive_timeout(10**9)
  if stock:
    # Just capture the home + settings landing in stock mode and exit.
    _set_state(NetworkType.wifi, experimental=False)
    _capture("99-stock-home", frames=20)
    gui_app.push_widget(main_layout._settings_layout)
    _capture("99-stock-settings", frames=30)
    return

  # ---- Home states ----
  _set_state(NetworkType.wifi, experimental=False)
  _capture("01-standard-ready", frames=20)

  _set_state(NetworkType.wifi, experimental=True)
  _capture("02-experimental", frames=20)

  _set_state(NetworkType.none, experimental=False)
  _capture("03-offline", frames=20)

  # ---- Alerts pane (swipe-left from home in MainLayout's scroller) ----
  _set_state(NetworkType.wifi, experimental=False)
  main_layout._scroller.scroll_to(int(main_layout._alerts_layout.rect.x), smooth=False)
  _capture("04-alerts", frames=20)
  # Scroll back to home before settings tests
  main_layout._scroller.scroll_to(int(main_layout._home_layout.rect.x), smooth=False)

  # ---- Settings landing + every sub-panel ----
  _set_state(NetworkType.wifi, experimental=False)
  gui_app.push_widget(main_layout._settings_layout)
  _capture("10-settings-landing", frames=30)

  tiles = main_layout._settings_layout._scroller._items
  panel_specs = [
    # (tile_index, capture_prefix, [pages_to_screenshot])
    (0, "11-toggles",   [(0, "page1"), (1, "page2"), (7, "last")]),
    (1, "12-network",   [(0, "wifi"),  (1, "metered"), (3, "tether-pw")]),
    (2, "13-device",    [(0, "paired"), (2, "pair"), (10, "power-off")]),
    (3, "14-firehose",  [(0, "segments"), (1, "status")]),
    (4, "15-developer", [(0, "dongle"), (4, "ssh-keys"), (9, "debug")]),
    (5, "16-vehicle",   [(0, "current"), (1, "clear"), (2, "select")]),
    (6, "17-bluepilot", [(0, "first"), (4, "lower-right"), (15, "lane-pos"), (28, "uninstall-cache")]),
  ]

  # ---- Capture BP dialogs (in isolation on top of settings) ----
  # NB: rl.take_screenshot can lag for newly-pushed full-screen widgets;
  #     these dialog captures may show settings underneath. Verify dialogs
  #     by running ./selfdrive/ui/ui.py directly.
  from openpilot.selfdrive.ui.bp.mici.widgets.bp_dialogs import BPInfoDialog, BPConfirmDialog, BPInputDialog
  d = BPInfoDialog("Disengage first", "Disengage to power off.")
  gui_app.push_widget(d)
  _capture("20-dialog-info", frames=20)
  print(f"[dbg] info dialog rect=(x={d.rect.x},y={d.rect.y},w={d.rect.width},h={d.rect.height}) "
        f"dismissing={d.is_dismissing}")
  if gui_app._nav_stack and gui_app._nav_stack[-1] is d:
    gui_app.pop_widget()

  gui_app.push_widget(BPConfirmDialog(
    "slide to\npower off",
    gui_app.texture("icons_mici/settings/device/power.png", 64, 64),
    confirm_callback=lambda: None, exit_on_confirm=False, red=True,
  ))
  _capture("21-dialog-confirm", frames=20)
  gui_app.pop_widget()

  gui_app.push_widget(BPInputDialog("enter APN...", "comma.ai", minimum_length=0))
  _capture("22-dialog-input", frames=20)
  gui_app.pop_widget()

  # ---- BP QR dialog ----
  from openpilot.selfdrive.ui.bp.mici.widgets.web_server_qr_dialog_bp import BPWebServerQRDialog
  gui_app.push_widget(BPWebServerQRDialog(back_callback=gui_app.pop_widget))
  _capture("23-dialog-qr", frames=30)
  if gui_app._nav_stack[-1].__class__.__name__ == "BPWebServerQRDialog":
    gui_app.pop_widget()

  # Cycle the lower-right complication through each option so the multi-toggle
  # captures show the longest text path through the auto-shrink logic.
  ui_state.params.put("mici_complication", 4)  # "time to lead car"

  for tile_idx, prefix, pages in panel_specs:
    # Pop back to settings landing (in case we're inside a panel)
    while len(gui_app._nav_stack) > 2:
      gui_app.pop_widget()

    tile = tiles[tile_idx]
    if tile._click_callback:
      tile._click_callback()
    panel = gui_app._nav_stack[-1]
    if hasattr(panel, "_pager"):
      for page_idx, page_name in pages:
        panel._pager.set_page(page_idx, smooth=False)
        _capture(f"{prefix}-{page_name}", frames=20)


if __name__ == "__main__":
  main()
