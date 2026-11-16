"""
Ported from zoompilot's accelerator_events (Zeph Leggett, MIT License), cut down to the events nrdr has.

Onroad events for a JetLink big model that joins mid-drive: jetlink's swap
events (jetlink/openpilot/events.py) read off this fork's messages, and their
flags raised as events nrdr already has: bigModelLoading for the no-entry
second and bigModelReady for the chime. nrdr has no events of its own for the
offer or a lost link, so those two flags are not raised. With no jetlink on the
device, or the link off, the tracker is inert and nothing is added.

The tracker reads modeld's runtime record (jetlink_adapter.runtime()), as nrdr
carries no accelerator state on modelDataV2SP.
"""
import openpilot.cereal.messaging as messaging
from openpilot.cereal import custom
from openpilot.common.realtime import DT_CTRL
from openpilot.selfdrive.selfdrived.events import Events, EventName
from openpilot.sunnypilot import jetlink_adapter
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP

EventNameSP = custom.OnroadEventSP.EventName


class AcceleratorEvents:
  # JetLink is optional: its daemon exiting costs the big model, never
  # engagement. manager does not restart a process that died, so without this
  # a dead link owner would be processNotRunning, NO_ENTRY until a reboot
  OPTIONAL_PROCESSES = frozenset({jetlink_adapter.OWNER})

  def __init__(self):
    # jetlink's tracker, behind the hooks' net; None without jetlink
    self.swap = jetlink_adapter.swap_events(DT_CTRL)

  @property
  def settling(self) -> bool:
    """Within a second of the big model swapping in or handing back."""
    return self.swap is not None and self.swap.settling

  def update(self, sm: messaging.SubMaster, in_control: bool, events: Events, events_sp: EventsSP) -> None:
    """`in_control`: openpilot or MADS is engaged, MADS even while its lateral
    is paused, the rule the adapter's swap gate waits on (Adapter.engaged)."""
    if self.swap is None:
      return
    fresh = sm.seen['modelV2'] and sm.alive['modelV2'] and sm.valid['modelV2']
    big = sm.alive['modelV2'] and sm.valid['modelV2'] and sm['modelV2'].big
    flags = self.swap.update(fresh, big, in_control)   # state None: modeld's runtime record
    if flags.no_entry or flags.chime:
      # the native block's chime on the swap waits for the end of the second,
      # when it means the driver can engage
      events_sp.remove(EventNameSP.bigModelReady)
    if flags.no_entry:
      events.add(EventName.bigModelLoading)
    if flags.chime:
      events_sp.add(EventNameSP.bigModelReady)
