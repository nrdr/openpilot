#!/usr/bin/env python3
import os
import time

from openpilot.system.hardware import HARDWARE, TICI
from openpilot.common.realtime import config_realtime_process, set_core_affinity
from openpilot.system.ui.lib.application import gui_app
from openpilot.selfdrive.ui.layouts.main import MainLayout
from openpilot.selfdrive.ui.mici.layouts.main import MiciMainLayout
from openpilot.selfdrive.ui.ui_state import ui_state

BIG_UI = gui_app.big_ui()


def main():
  cores = {5, }
  config_realtime_process(0, 51)

  gui_app.init_window("UI")
  if BIG_UI:
    MainLayout()
  else:
    MiciMainLayout()

  _started_seen = False
  _offroad_since = None
  for should_render in gui_app.render():
    ui_state.update()

    # nrdr: health reboot while parked/remote - full device reboot 2h after going offroad, but
    # only once we've actually been onroad since boot, so a parked device reboots a single time
    # (post-drive) instead of looping every 2h. Clears the UI memory leak and anything else stale.
    if ui_state.started:
      _started_seen = True
      _offroad_since = None
    elif _started_seen:
      if _offroad_since is None:
        _offroad_since = time.monotonic()
      elif time.monotonic() - _offroad_since > 7200:
        HARDWARE.reboot()

    if should_render:
      # reaffine after power save offlines our core
      if TICI and os.sched_getaffinity(0) != cores:
        try:
          set_core_affinity(list(cores))
        except OSError:
          pass


if __name__ == "__main__":
  main()
