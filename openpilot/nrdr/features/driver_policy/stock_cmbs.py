"""Read-only CMBS setting feedback; never changes Honda messages or controls."""

from opendbc.car import Bus


STATUS_MAX_AGE_NS = 500_000_000
CONFIRM_TIME_NS = 200_000_000


def publish_stock_cmbs_status(CI, CS_SP, now_nanos: int) -> None:
  # FCM_OFF_2's button-setting meaning is verified in this Civic's camera logs.
  # Do not infer the same meaning for other Honda platforms without evidence.
  if CI.CP.brand != "honda" or CI.CP.carFingerprint != "HONDA_CIVIC":
    return
  camera = CI.can_parsers.get(Bus.cam)
  if camera is None:
    return
  hud = camera.vl.get("ACC_HUD", {})
  stamp = camera.ts_nanos.get("ACC_HUD", {}).get("FCM_OFF_2", 0)
  if not stamp or not 0 <= now_nanos - stamp <= STATUS_MAX_AGE_NS or "FCM_OFF_2" not in hud:
    return

  # Use the checksum/counter-validated camera input, not our fault-masked HUD output.
  # FCM_OFF can stay asserted even when the user setting is enabled.
  CS_SP.stockCmbsStatus = "disabled" if hud["FCM_OFF_2"] else "enabled"
  CS_SP.stockCmbsStatusMonoTime = stamp
  CS_SP.stockCmbsOffOrProblem = bool(hud.get("FCM_OFF", 0) or hud.get("FCM_PROBLEM", 0))


class StockCmbsAlerts:
  def __init__(self):
    self.confirmed = None
    self.candidate = None
    self.candidate_since = 0
    self.last_stamp = 0

  def update(self, status: str, stamp: int, valid: bool) -> bool:
    """Announce stable setting changes, never startup defaults or stale messages."""
    if not valid or status not in ("enabled", "disabled") or not stamp or stamp < self.last_stamp:
      self.__init__()
      return False
    if stamp == self.last_stamp:
      return False
    if self.last_stamp and stamp - self.last_stamp > STATUS_MAX_AGE_NS:
      self.__init__()
    self.last_stamp = stamp
    if status != self.candidate:
      self.candidate, self.candidate_since = status, stamp
      return False
    if stamp - self.candidate_since < CONFIRM_TIME_NS:
      return False
    changed = self.confirmed is not None and self.confirmed != status
    self.confirmed = status
    return changed
