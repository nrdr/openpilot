import os
import time
from threading import Lock

from openpilot.cereal import log, custom
from opendbc.car.structs import car
from openpilot.nrdr.features.driver_policy.hud_submode import consume_button_press
from openpilot.nrdr.features.driver_policy.stock_cmbs import StockCmbsAlerts
from openpilot.nrdr.features.longitudinal.personality import personality_write_lock
from openpilot.nrdr.features.longitudinal.policy import longitudinal_personality, mvl_longitudinal_enabled, nrdr_longitudinal_enabled


ButtonType = car.CarState.ButtonEvent.Type


class MvlPersonalitySync:
  """One coalesced wheel request, persisted only by the settings thread.

  Params' async FIFO has no completion token. Do not put MVL wheel requests in
  it: intermediate writes could otherwise look like fresh native UI choices.
  File identity distinguishes even a UI rewrite of the previous saved value.
  The lock protects memory only; neither reads nor fsync hold up the 100 Hz loop.
  """

  def __init__(self, selfdrive):
    self.params = selfdrive.params
    self._lock = Lock()
    self._version = 0
    self._pending = None  # (wheel generation, personality); bounded, latest wins
    self._written = None  # write awaiting a successful observation
    self._observed = self._read()
    if self._observed is not None and self._observed[1] is not None:
      selfdrive.personality = self._observed[1]

  def _read(self):
    try:
      # Params replaces this file atomically. Read identity and value from the
      # same descriptor, never a value paired with another writer's stat().
      with open(self.params.get_param_path("LongitudinalPersonality"), "rb") as f:
        stat = os.fstat(f.fileno())
        raw = f.read(16)
    except FileNotFoundError:
      return (None, None)
    except OSError:
      return None  # Keep the active choice and retry after a storage error.
    identity = (stat.st_dev, stat.st_ino, stat.st_mtime_ns, stat.st_ctime_ns, stat.st_size)
    try:
      value = int(raw) if stat.st_size <= 16 else None
    except ValueError:
      value = None
    return identity, value if value in range(4) else None

  def cycle(self, selfdrive, count):
    with self._lock:
      selfdrive.personality = (longitudinal_personality(selfdrive.personality, True) - 1) % count
      self._version += 1
      self._pending = self._version, selfdrive.personality

  def poll(self, selfdrive):
    # UI/RPC writes cannot slip between this fresh read and the wheel commit.
    # Only this settings thread waits on disk/other processes; cycle() never does.
    try:
      with personality_write_lock(self.params):
        self._poll_locked(selfdrive)
    except (OSError, RuntimeError):
      return  # Lock/storage failure: retain the active choice and retry later.

  def _poll_locked(self, selfdrive):
    with self._lock:
      version = self._version
    observed = self._read()
    if observed is None:
      return

    with self._lock:
      if version != self._version:
        # A wheel press during this read takes precedence. Remember this disk
        # version so the same stale observation cannot replay on the next poll.
        self._observed, self._written = observed, None
        return
      if self._written is not None:
        job, before = self._written
        if observed[0] != before[0] and observed[1] == job[1]:
          self._observed = observed
          if self._pending == job:
            self._pending = None
        self._written = None
      if (observed != self._observed and observed[1] is not None and
          (self._observed is not None or self._pending is None)):
        # A native settings write observed while wheel persistence is pending
        # supersedes it, including a rewrite of the old saved personality.
        selfdrive.personality = observed[1]
        self._version += 1
        self._pending = None
      self._observed = observed
      job = self._pending
      if job is None:
        return
      self._written = job, observed

    try:
      self.params.put("LongitudinalPersonality", job[1], block=True)
    except (OSError, RuntimeError):
      # An error need not mean the atomic rename failed. Keep the completion
      # marker until a read proves whether this job reached disk.
      return
    persisted = self._read()
    with self._lock:
      if persisted is None:
        return  # A later poll must acknowledge this write, not replay it.
      self._written = None
      if persisted[0] != observed[0] and persisted[1] == job[1]:
        self._observed = persisted
        if self._pending == job:
          self._pending = None
      # A different external write remains unobserved until the next poll;
      # an unchanged file means persistence failed and the latest job retries.


class NrdrSelfdrive:
  def __init__(self, CP=None):
    self.longitudinal_enabled = nrdr_longitudinal_enabled(CP)
    self.personality_sync = None
    self.personality_button_held = False
    self.personality_safety_consumed = False
    self.sla_button_reserved_until = 0.0
    self.stock_cmbs_alerts = StockCmbsAlerts()

  def initialize_personality(self, selfdrive):
    if mvl_longitudinal_enabled(selfdrive.CP):
      self.personality_sync = MvlPersonalitySync(selfdrive)

  def update_stock_cmbs(self, CS, sm, events_sp) -> None:
    state = sm['carStateSP']
    valid = CS.canValid and sm.all_checks(['carStateSP'])
    if self.stock_cmbs_alerts.update(str(state.stockCmbsStatus), state.stockCmbsStatusMonoTime, valid):
      events_sp.add(custom.OnroadEventSP.EventName.stockCmbsStatusChanged)

  def reserve_distance_button(self, sla_state) -> bool:
    if self.personality_sync is not None:
      # SLA is disabled in startup-latched MVL, including stale publications.
      self.sla_button_reserved_until = 0.0
      return False
    if not self.longitudinal_enabled:
      return False
    now = time.monotonic()
    if sla_state == custom.LongitudinalPlanSP.SpeedLimit.AssistState.preActive:
      self.sla_button_reserved_until = now + 0.75
    if now <= self.sla_button_reserved_until:
      return True
    self.sla_button_reserved_until = 0.0
    return False

  @staticmethod
  def update_personality(selfdrive, CS, button_reserved: bool) -> bool:
    distance_released = any(not event.pressed and event.type == ButtonType.gapAdjustCruise for event in CS.buttonEvents)
    nrdr = getattr(selfdrive, "nrdr", None)
    sync = getattr(nrdr, "personality_sync", None)
    experimental_mode_switched = selfdrive.experimental_mode_switched
    if distance_released:
      selfdrive.experimental_mode_switched = False

    blocked = button_reserved or getattr(selfdrive, "distance_button_consumed", False)
    if sync is not None:
      # Ignore stale disabled-SLA consumption for personality selection, but
      # retain cruise-unavailable protection until a fresh available press.
      # Experimental holds share the normal latch: keep it through the hold
      # and suppress personality cycling on that hold's release.
      available = getattr(getattr(CS, "cruiseState", None), "available", True)
      if any(event.pressed and event.type == ButtonType.gapAdjustCruise for event in CS.buttonEvents):
        if not nrdr.personality_button_held:
          nrdr.personality_safety_consumed = False
        nrdr.personality_button_held = True
      if nrdr.personality_button_held and not available:
        nrdr.personality_safety_consumed = True
      blocked = not available or nrdr.personality_safety_consumed
      if distance_released:
        # CruiseHelper also needs this latch while held: availability returning
        # must not turn the tail of an unavailable press into a mode toggle.
        selfdrive.distance_button_consumed = False
        nrdr.personality_button_held = False
        nrdr.personality_safety_consumed = False

    if not selfdrive.CP.openpilotLongitudinalControl or blocked:
      return False

    changed = False
    enabled = nrdr_longitudinal_enabled(selfdrive.CP)
    if sync is None:
      selfdrive.personality = longitudinal_personality(selfdrive.personality, enabled)
    if (distance_released and not experimental_mode_switched and
        (sync is not None or not enabled or consume_button_press(selfdrive.params))):
      count = len(log.LongitudinalPersonality.schema.enumerants) if enabled else 3
      if sync is not None:
        sync.cycle(selfdrive, count)
      else:
        selfdrive.personality = (selfdrive.personality - 1) % count
        selfdrive.params.put("LongitudinalPersonality", selfdrive.personality)
      changed = True

    return changed
