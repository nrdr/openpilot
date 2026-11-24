"""
Ported from zoompilot's jetlink_adapter (Zeph Leggett, MIT License) for nrdr's openpilot.

jetlink on this fork: the adapter jetlink runs over, and the hooks manager,
modeld, hardwared, selfdrived and the UI call.

jetlink (jetlink_repo, vendored comma-side only, linked as /jetlink by
launch_chffrplus.sh) runs the large driving model on an attached Jetson, Mac or
iPhone. Its stock adapter (jetlink.openpilot.stock) knows stock openpilot's
paths; Adapter below is that with this fork's param names, its modeld_v2 and
MADS. The hooks (jetlink.openpilot.hooks) never raise and answer as if the link
were off when jetlink is not present, or speaks another API.

Off by default: the JetlinkLink param is 0 until the user turns it on, and
with it 0 every hook answers as if jetlink were not there.

comma's chestnut board keeps working as before: modeld asks prepare(CHESTNUT)
and jetlink never takes the big model while a chestnut is fitted.

manager imports this module to build the process list, and runs it as
jetlinkd, the resident gadget owner. So the top level is the standard library
only; everything else is imported where it is used. tests/test_adapter.py holds
the line.
"""
from __future__ import annotations

import functools
import os
import threading
from collections import namedtuple
from pathlib import Path

# the version of jetlink.openpilot's API this adapter is written to; any other
# is treated as jetlink being absent, with the reason as the offroad alert
API = 4

# the gadget owner, as manager names the process and selfdrived lists it
OWNER = 'jetlinkd'

# the Jetlink setting, stored as an index: jetlink.openpilot.MODES,
# written out so the panels build the setting without a jetlink checkout
MODES = ('off', 'usb', 'ios')

# the params jetlink reads and writes, all declared in params_keys.h. big_model,
# catalog and select are the model manager's slots, which this port does not
# wire: jetlink then runs its own default or the server's pick
_Keys = namedtuple('_Keys', 'link offroad progress spec big_model catalog charge_phone select')
KEYS = _Keys(link='JetlinkLink', offroad='IsOffroad', progress='JetlinkProgress', spec='JetlinkSpec',
             big_model=None, catalog=None, charge_phone='JetlinkChargePhone', select=None)

_AGNOS = os.path.isfile('/AGNOS')


def _params_dir() -> Path:
  """The params store's directory, by params.cc and hw.h's rule: PARAMS_ROOT,
  else /data/params on a device and $HOME/.comma<OPENPILOT_PREFIX>/params
  elsewhere, then /<OPENPILOT_PREFIX, or d>. Per call, so it follows a prefix
  as Params does; the environment only, so it never raises."""
  prefix = os.environ.get('OPENPILOT_PREFIX', '')
  root = os.environ.get('PARAMS_ROOT')
  if root is None:
    root = '/data/params' if _AGNOS else os.environ.get('HOME', '') + '/.comma' + prefix + '/params'
  return Path(root) / os.environ.get('OPENPILOT_PREFIX', 'd')


def link_on() -> bool:
  """Is the Jetlink setting on? As jetlink reads it, a file, so that a jetlink
  this build cannot use tells only someone who turned the link on."""
  try:
    return 0 < int((_params_dir() / KEYS.link).read_bytes()) < len(MODES)
  except (OSError, ValueError):
    return False


def model_uses_plan(model) -> bool:
  """Does the model drive from the plan (no action head)? JetlinkModelState has
  no uses_plan, so read its output slices, as modeld's own models decide it."""
  try:
    return bool(model.uses_plan)
  except AttributeError:
    return 'action' not in model.output_slices


def model_mlsim(model) -> bool:
  """modeld_v2's mlsim of the model it runs; the joined big model is
  a supercombo with the plan, so True."""
  try:
    return bool(model.mlsim)
  except AttributeError:
    return True


def with_blendful(get_action_from_model, min_lat_control_speed: float):
  """The stock action function taking modeld_v2's extra argument: Blendful's
  correction as a callback on the raw curvature, applied above the minimum
  lateral control speed. ptm_controller and lateral_speed pass through."""
  def action(model_output, prev_action, lat_action_t, long_action_t, v_ego, blendful=None,
             ptm_controller=False, lateral_speed=None):
    result = get_action_from_model(model_output, prev_action, lat_action_t, long_action_t, v_ego,
                                   ptm_controller=ptm_controller, lateral_speed=lateral_speed)
    if blendful is not None:
      correction = blendful(result.desiredCurvature)
      if v_ego > min_lat_control_speed:
        result.desiredCurvature += correction
    return result
  return action


@functools.cache
def _adapter_class():
  from jetlink.openpilot.interface import Keys
  from jetlink.openpilot.stock import Stock

  class Adapter(Stock):
    """jetlink.openpilot.interface.Openpilot over this fork: stock openpilot
    but for what follows."""
    KEYS = Keys(**KEYS._asdict())
    # MADS's state rides on carControlSP
    IN_CONTROL_SERVICES = ('carState', 'carControl', 'carControlSP')

    def chestnut_present(self) -> bool:
      # modeld's own test: a chestnut whose firmware names itself
      from openpilot.selfdrive.modeld.helpers import chestnut_present
      return chestnut_present()

    def model_constants(self):
      from openpilot.sunnypilot.modeld_v2.constants import ModelConstants
      return ModelConstants

    def action_function(self):
      # modeld_v2 passes Blendful's correction as a callback and the PTM controller flag
      from openpilot.selfdrive.modeld.modeld import MIN_LAT_CONTROL_SPEED, get_action_from_model
      return with_blendful(get_action_from_model, MIN_LAT_CONTROL_SPEED)

    def engaged(self, sm) -> bool:
      # selfdrived's enabled or mads.enabled, as controlsd republishes them
      return bool(sm['carControl'].enabled or sm['carControlSP'].mads.enabled)

  return Adapter


def adapter():
  """The adapter, for jetlink's entry points that run as their own process:
  the provisioning run."""
  return _adapter_class()()


def owner_config():
  """What jetlinkd needs: data only, so the owner imports nothing heavy."""
  return _adapter_class().owner_config()


def main() -> None:
  """jetlinkd: hold the USB gadget until manager stops this process."""
  _adapter_class().main()


# -- the hooks ----------------------------------------------------------------

# this process's hooks, made on first use and kept, the link off included:
# Python does not cache a failed import. One per process, so that prepare()
# and attach() reach the same jetlink
_hooks = None
_making = threading.Lock()


def hooks():
  """jetlink.openpilot.hooks.Hooks over this adapter, or the link off."""
  global _hooks
  with _making:
    if _hooks is None:
      _hooks = _guard()
    return _hooks


def _guard():
  # inside a function, so a jetlink that fails to import lands here too
  try:
    import jetlink
    if getattr(jetlink, '__file__', None) is None:
      return _Off()   # an empty jetlink dir, which Python takes for a namespace package
    from jetlink.openpilot.hooks import Hooks
  except ModuleNotFoundError as e:
    if e.name == 'jetlink':
      return _Off()   # no checkout: the link does not exist on this device
    if (e.name or '').startswith('jetlink.'):
      return _unusable("jetlink package too old for this build", e)
    return _unusable(f"jetlink failed to load: {e}", e)
  except Exception as e:
    return _unusable(f"jetlink failed to load: {type(e).__name__}: {e}", e)
  try:
    return Hooks(API, adapter, link_on=link_on, log=_cloudlog)
  except Exception as e:
    return _unusable(str(e), e)   # another API, which it names


def _cloudlog():
  from openpilot.common.swaglog import cloudlog
  return cloudlog


def _unusable(why: str, error: Exception) -> _Off:
  try:
    _cloudlog().error("jetlink: %s", why, exc_info=error)
  except Exception:
    pass
  return _Off(why)


class _Off:
  """Every hook with the link off; reason() says why, to someone who turned
  the link on. jetlink's own Off cannot answer for a jetlink that is missing or
  too old to have it, and one answer for every case keeps them alike."""
  # by hook; a callable is handed the hook's arguments. A wanted power-off goes
  # ahead: no jetlink must keep a comma on to drain the car's battery
  ANSWERS = {'should_run': False, 'status': None, 'prepare': False, 'attach': lambda model, *_: model,
             'handed_over': False, 'state': 'none', 'shutdown_step': lambda wanted, reason='': wanted,
             'request_shutdown': False, 'shutdown_pending': False, 'runtime': None, 'swap_events': None}

  def __init__(self, why: str = ''):
    self.why = why

  def reason(self) -> str | None:
    return self.why if self.why and link_on() else None

  def __getattr__(self, name: str):
    if name not in self.ANSWERS:
      raise AttributeError(name)
    answer = self.ANSWERS[name]
    return answer if callable(answer) else lambda *args: answer


def _hook(name: str):
  def call(*args):
    return getattr(hooks(), name)(*args)
  call.__name__ = call.__qualname__ = name
  return call


# the hooks by the names the hook lines call, each this process's hooks() at
# the call: jetlink.openpilot.hooks says what each does and answers
HOOK_NAMES = (*_Off.ANSWERS, 'reason')
(should_run, status, prepare, attach, handed_over, state, shutdown_step, request_shutdown, shutdown_pending,
 runtime, swap_events, reason) = map(_hook, HOOK_NAMES)
