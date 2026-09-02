import datetime
import subprocess
import time
from zoneinfo import ZoneInfo

import pyray as rl

from openpilot.selfdrive.ui.mici.layouts.home import HOME_PADDING
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app


try:
  LOCAL_TIMEZONE: datetime.tzinfo = ZoneInfo("America/New_York")
except Exception:
  LOCAL_TIMEZONE = datetime.UTC


def _local_ip() -> str:
  try:
    output = subprocess.check_output(["ip", "-4", "-o", "addr"], encoding="utf8", timeout=2)
    addresses = []
    for line in output.splitlines():
      fields = line.split()
      if len(fields) >= 4 and fields[2] == "inet" and fields[1] != "lo":
        addresses.append((fields[1], fields[3].split("/")[0]))
    for prefix in ("192.168.43.", "192.168.", "10.", "172."):
      for _, address in addresses:
        if address.startswith(prefix):
          return address
    return addresses[0][1] if addresses else ""
  except Exception:
    return ""


def _time_ago(value) -> str:
  if value is None:
    return "never updated"
  if value.tzinfo is None:
    value = value.replace(tzinfo=datetime.UTC)
  minutes = max(0, int((datetime.datetime.now(datetime.UTC) - value).total_seconds())) // 60
  if minutes == 0:
    return "Last updated just now"
  if minutes < 60:
    return f"Last updated {minutes} minute{'' if minutes == 1 else 's'} ago"
  hours, minutes = divmod(minutes, 60)
  if hours < 24:
    return f"Last updated {hours} hour{'' if hours == 1 else 's'} {minutes} minute{'' if minutes == 1 else 's'} ago"
  days, hours = divmod(hours, 24)
  return f"Last updated {days} day{'' if days == 1 else 's'} {hours} hour{'' if hours == 1 else 's'} ago"


class NrdrMiciHome:
  def __init__(self, layout):
    self.layout = layout
    self.ip = _local_ip()
    self.last_check = time.monotonic()
    self.last_update = self._last_update_time()
    layout._version_text = self.version_text()

  @staticmethod
  def _last_update_time():
    try:
      return ui_state.params.get("LastUpdateTime")
    except Exception:
      return None

  @staticmethod
  def version_text() -> tuple[str, str, str, str] | None:
    version = ui_state.params.get("Version")
    branch = ui_state.params.get("GitBranch")
    commit = ui_state.params.get("GitCommit")
    if not all((version, branch, commit)):
      return None
    try:
      raw_date = ui_state.params.get("GitCommitDate")
      timestamp = int(raw_date.strip("'").split()[0])
      date = datetime.datetime.fromtimestamp(timestamp, LOCAL_TIMEZONE).strftime("%b %d")
    except (ValueError, IndexError, TypeError, AttributeError):
      date = ""
    return version, f"{branch} {commit[:7]}", "", date

  def update(self) -> None:
    now = time.monotonic()
    if now - self.last_check > 5.0:
      self.last_check = now
      self.ip = _local_ip()
      self.last_update = self._last_update_time()

  def render(self) -> None:
    home = self.layout
    position = rl.Vector2(home.rect.x - 2 + HOME_PADDING, home.rect.y - 16)
    home._openpilot_label.set_position(position.x, position.y)
    home._openpilot_label.render()

    if home._version_text is not None:
      version_position = rl.Rectangle(position.x, position.y + home._openpilot_label.font_size + 16, 100, 44)
      home._version_label.set_text("stable.konik.ai")
      home._version_label.set_position(version_position.x, version_position.y)
      home._version_label.render()

      home._branch_label.set_max_width(gui_app.width - home._version_label.text_width - 32)
      home._branch_label.set_text("   " + _time_ago(self.last_update))
      home._branch_label.set_position(version_position.x + home._version_label.text_width + 12, version_position.y)
      home._branch_label.render()

      home._version_commit_label.set_text("Device IP: " + (self.ip or "obtaining..."))
      home._version_commit_label.set_position(version_position.x, version_position.y + home._version_label.font_size + 7)
      home._version_commit_label.render()

      if home._version_text[3]:
        home._date_label.set_text(home._version_text[3])
        home._date_label.set_position(home.rect.x + home.rect.width - home._date_label.text_width - HOME_PADDING,
                                      home.rect.y + home.rect.height - 48 - home._date_label.font_size - 4)
        home._date_label.render()

    home._experimental_icon.set_visible(ui_state.experimental_mode)
    home._set_chestnut_visibility()
    home._mic_icon.set_visible(ui_state.recording_audio)
    home._body_icon.set_visible(bool(ui_state.is_body))

    footer = rl.Rectangle(home.rect.x + HOME_PADDING, home.rect.y + home.rect.height - 48, home.rect.width - HOME_PADDING, 48)
    home._status_bar_layout.render(footer)
    home._alerts_pill.set_position(home.rect.x + home.rect.width - home._alerts_pill.rect.width - HOME_PADDING,
                                   home.rect.y + home.rect.height - home._alerts_pill.rect.height)
    home._alerts_pill.render()
