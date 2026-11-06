"""Production profile hooks with atomic Params files and no native services.

Execute the actual native callback and settings-thread body. These tests cover
host synchronization, not the native messaging transport or longitudinal math.
"""
import ast
import base64
import gzip
import multiprocessing
import os
from collections.abc import Callable
from contextlib import contextmanager
from pathlib import Path
from threading import Event, Lock, Thread
from types import SimpleNamespace as NS
from typing import Union

import pytest

from openpilot.nrdr.features.longitudinal.personality import personality_lock_path, personality_write_lock, write_personality


ROOT = Path(__file__).resolve().parents[3]
KEY = "LongitudinalPersonality"
MVL_FLAG = 131072
BUTTON = NS(gapAdjustCruise=3)
RELEASE = NS(buttonEvents=[NS(type=BUTTON.gapAdjustCruise, pressed=False)])


def definitions(relative, env, *, cls=None, method=None):
  path = ROOT / relative
  tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
  if cls is not None:
    owner = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == cls)
    nodes = [node for node in owner.body if isinstance(node, ast.FunctionDef) and node.name == method]
  else:
    nodes = [node for node in tree.body if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.Assign, ast.AnnAssign))]
  exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), env)
  return env


@pytest.fixture
def runtime():
  env = {"os": os, "Lock": Lock, "time": NS(sleep=lambda _: None, monotonic=lambda: 100.),
         "car": NS(CarState=NS(ButtonEvent=NS(Type=BUTTON))),
         "log": NS(LongitudinalPersonality=NS(schema=NS(enumerants=dict.fromkeys(range(4))))),
         "StockCmbsAlerts": lambda: object(), "consume_button_press": lambda _: True,
         "personality_write_lock": personality_write_lock, "write_personality": write_personality}
  definitions("openpilot/nrdr/features/longitudinal/policy.py", env)
  # Only the opendbc enum import is unavailable on this host. The real policy
  # gate is independently covered by test_mvl_policy_boundary.py.
  env["mvl_longitudinal_enabled"] = lambda cp: (
    cp.brand == "honda" and cp.openpilotLongitudinalControl and bool(cp.flags & MVL_FLAG)
  )
  definitions("openpilot/nrdr/hooks/selfdrived.py", env)
  definitions("openpilot/selfdrive/selfdrived/selfdrived.py", env, cls="SelfdriveD", method="params_thread")
  definitions("openpilot/selfdrive/ui/layouts/settings/toggles.py", env,
              cls="TogglesLayout", method="_set_longitudinal_personality")
  return env


class AtomicParams:
  def __init__(self, directory, initial):
    self.path = directory / KEY
    self.writes = []
    self.other = {"IsOffroad": True}
    self.on_put = lambda: None
    self.after_put = lambda: None
    self.external(initial)

  def external(self, value):
    temporary = self.path.with_suffix(".new")
    temporary.write_text(str(value), encoding="ascii")
    temporary.replace(self.path)

  def get_param_path(self, key):
    assert key == KEY
    return str(self.path)

  def get(self, key, **_):
    return int(self.path.read_text()) if key == KEY else self.other.get(key)

  def get_bool(self, key):
    return bool(self.other.get(key))

  def put(self, key, value, *, block=False):
    if key != KEY:
      self.other[key] = value
      return
    assert block, "MVL must not enqueue intermediate wheel profiles in Params' async FIFO"
    self.writes.append(value)
    self.on_put()
    self.external(value)
    self.after_put()


def state(runtime, tmp_path, initial=1, *, flags=MVL_FLAG, openlong=True):
  params = AtomicParams(tmp_path, initial)
  cp = NS(brand="honda", carFingerprint="HONDA_CIVIC", flags=flags, openpilotLongitudinalControl=openlong)
  selfdrive = NS(CP=cp, params=params, personality=initial, experimental_mode_switched=False,
                 mads=NS(read_params=lambda: None))
  selfdrive.nrdr = runtime["NrdrSelfdrive"](cp)
  selfdrive.nrdr.initialize_personality(selfdrive)
  return selfdrive


def poll(runtime, selfdrive):
  iterations = iter((False, True))
  runtime["params_thread"](selfdrive, NS(is_set=lambda: next(iterations)))


def press(runtime, selfdrive):
  assert runtime["NrdrSelfdrive"].update_personality(selfdrive, RELEASE, False)


def native_select(runtime, selfdrive, selected):
  runtime["ui_state"] = NS(CP=selfdrive.CP)
  runtime["_set_longitudinal_personality"](NS(_params=selfdrive.params), selected)


@pytest.mark.parametrize("initial,selected", [(1, 3), (3, 0), (3, 1), (3, 2)])
@pytest.mark.parametrize("string_value", [False, True])
def test_native_selection_reaches_active_profile_and_exits_econ(runtime, tmp_path, initial, selected, string_value):
  selfdrive = state(runtime, tmp_path, initial)
  native_select(runtime, selfdrive, str(selected) if string_value else selected)
  poll(runtime, selfdrive)
  assert selfdrive.personality == selfdrive.params.get(KEY) == selected
  assert selfdrive.nrdr.personality_sync._pending is None
  assert selfdrive.params.writes == [selected]  # no echo write from the poller


@pytest.mark.parametrize("flags,openlong", [(0, True), (MVL_FLAG, False)])
def test_legacy_honda_still_never_polls_personality(runtime, tmp_path, flags, openlong):
  selfdrive = state(runtime, tmp_path, flags=flags, openlong=openlong)
  assert selfdrive.nrdr.personality_sync is None

  def forbidden(*_, **__):
    raise AssertionError("legacy Honda polled personality")

  selfdrive.params.get = selfdrive.params.get_param_path = forbidden
  poll(runtime, selfdrive)
  assert selfdrive.personality == 1


def test_multiple_wheel_presses_coalesce_without_reading_stale_disk(runtime, tmp_path):
  selfdrive = state(runtime, tmp_path)
  for expected in (0, 3, 2):
    press(runtime, selfdrive)
    assert selfdrive.personality == expected
    assert selfdrive.params.get(KEY) == 1
    assert selfdrive.params.writes == []
  poll(runtime, selfdrive)
  assert selfdrive.personality == selfdrive.params.get(KEY) == 2
  assert selfdrive.params.writes == [2]
  for _ in range(3):
    poll(runtime, selfdrive)
    assert selfdrive.personality == 2


def test_wheel_cycle_back_to_saved_value_is_not_an_early_ack(runtime, tmp_path):
  selfdrive = state(runtime, tmp_path)
  for _ in range(8):
    press(runtime, selfdrive)
  assert selfdrive.personality == 1
  assert selfdrive.nrdr.personality_sync._pending == (8, 1)
  poll(runtime, selfdrive)
  assert selfdrive.nrdr.personality_sync._pending is None
  assert selfdrive.params.writes == [1]


def test_slow_persistence_never_blocks_wheel_or_replays_intermediate_profile(runtime, tmp_path):
  selfdrive = state(runtime, tmp_path)
  entered, release = Event(), Event()
  errors = []

  def slow_write():
    entered.set()
    assert release.wait(3), "test did not release persistence"

  def worker():
    try:
      poll(runtime, selfdrive)
    except BaseException as error:
      errors.append(error)

  press(runtime, selfdrive)  # 1 -> 0; writer will hold this request
  selfdrive.params.on_put = slow_write
  thread = Thread(target=worker)
  thread.start()
  try:
    assert entered.wait(3)
    for expected in (3, 2, 1, 0, 3):
      press(runtime, selfdrive)
      assert selfdrive.personality == expected
  finally:
    release.set()
    thread.join(3)
  assert not thread.is_alive() and not errors
  assert selfdrive.params.get(KEY) == 0  # old completion cannot activate 0
  assert selfdrive.personality == 3
  selfdrive.params.on_put = lambda: None
  poll(runtime, selfdrive)
  assert selfdrive.personality == selfdrive.params.get(KEY) == 3
  assert selfdrive.params.writes == [0, 3]


@pytest.mark.parametrize("selected", [0, 1, 2, 3])
def test_native_choice_supersedes_pending_wheel_even_same_saved_value(runtime, tmp_path, selected):
  selfdrive = state(runtime, tmp_path)
  press(runtime, selfdrive)
  press(runtime, selfdrive)
  native_select(runtime, selfdrive, selected)
  poll(runtime, selfdrive)
  assert selfdrive.personality == selfdrive.params.get(KEY) == selected
  assert selfdrive.params.writes == [selected]
  assert selfdrive.nrdr.personality_sync._pending is None


def test_native_choice_during_inflight_write_is_eventually_applied(runtime, tmp_path):
  selfdrive = state(runtime, tmp_path)
  press(runtime, selfdrive)  # request 0

  def after_put():
    press(runtime, selfdrive)  # newer wheel request 3 while 0 is in flight
    selfdrive.params.external(2)

  selfdrive.params.after_put = after_put
  poll(runtime, selfdrive)
  assert selfdrive.personality == 3
  selfdrive.params.after_put = lambda: None
  poll(runtime, selfdrive)
  assert selfdrive.personality == selfdrive.params.get(KEY) == 2
  assert selfdrive.params.writes == [0]
  assert selfdrive.nrdr.personality_sync._pending is None


def test_wheel_during_poll_read_discards_that_version_not_just_one_iteration(runtime, tmp_path):
  selfdrive = state(runtime, tmp_path)
  native_select(runtime, selfdrive, 3)
  sync = selfdrive.nrdr.personality_sync
  read = sync._read

  def raced_read():
    snapshot = read()
    press(runtime, selfdrive)  # 1 -> 0, after this external version was read
    sync._read = read
    return snapshot

  sync._read = raced_read
  poll(runtime, selfdrive)
  assert selfdrive.personality == 0
  poll(runtime, selfdrive)
  assert selfdrive.personality == selfdrive.params.get(KEY) == 0
  assert selfdrive.params.writes == [3, 0]


def test_failed_post_write_read_does_not_replay_old_completion(runtime, tmp_path):
  selfdrive = state(runtime, tmp_path)
  sync = selfdrive.nrdr.personality_sync
  read = sync._read
  press(runtime, selfdrive)

  def after_put():
    press(runtime, selfdrive)
    sync._read = lambda: None

  selfdrive.params.after_put = after_put
  poll(runtime, selfdrive)
  assert selfdrive.personality == 3 and selfdrive.params.get(KEY) == 0
  sync._read = read
  selfdrive.params.after_put = lambda: None
  poll(runtime, selfdrive)
  assert selfdrive.personality == selfdrive.params.get(KEY) == 3
  assert selfdrive.params.writes == [0, 3]


def test_storage_failure_retries_latest_request_without_resetting_active(runtime, tmp_path):
  selfdrive = state(runtime, tmp_path)
  press(runtime, selfdrive)

  def fail():
    raise OSError("storage unavailable")

  selfdrive.params.on_put = fail
  poll(runtime, selfdrive)
  assert selfdrive.personality == 0 and selfdrive.params.get(KEY) == 1
  press(runtime, selfdrive)
  selfdrive.params.on_put = lambda: None
  poll(runtime, selfdrive)
  assert selfdrive.personality == selfdrive.params.get(KEY) == 3


def test_unreported_write_failure_does_not_acknowledge_pending_profile(runtime, tmp_path):
  selfdrive = state(runtime, tmp_path)
  press(runtime, selfdrive)
  put = selfdrive.params.put
  selfdrive.params.put = lambda *_args, **_kwargs: None
  poll(runtime, selfdrive)
  assert selfdrive.personality == 0 and selfdrive.params.get(KEY) == 1
  assert selfdrive.nrdr.personality_sync._pending is not None
  press(runtime, selfdrive)
  selfdrive.params.put = put
  poll(runtime, selfdrive)
  assert selfdrive.personality == selfdrive.params.get(KEY) == 3


def test_error_after_atomic_replace_cannot_replay_the_old_wheel_job(runtime, tmp_path):
  selfdrive = state(runtime, tmp_path)
  press(runtime, selfdrive)

  def after_put():
    press(runtime, selfdrive)
    raise OSError("directory sync failed after replace")

  selfdrive.params.after_put = after_put
  poll(runtime, selfdrive)
  assert selfdrive.personality == 3 and selfdrive.params.get(KEY) == 0
  selfdrive.params.after_put = lambda: None
  poll(runtime, selfdrive)
  assert selfdrive.personality == selfdrive.params.get(KEY) == 3
  assert selfdrive.params.writes == [0, 3]


def test_unknown_startup_disk_version_cannot_revert_a_pending_wheel_choice(runtime, tmp_path):
  selfdrive = state(runtime, tmp_path)
  sync = selfdrive.nrdr.personality_sync
  sync._observed = None  # Startup read failed; the existing active choice survived.
  press(runtime, selfdrive)
  poll(runtime, selfdrive)
  assert selfdrive.personality == selfdrive.params.get(KEY) == 0


def test_later_ui_rewrite_of_an_acknowledged_wheel_value_is_not_ignored(runtime, tmp_path):
  selfdrive = state(runtime, tmp_path)
  press(runtime, selfdrive)
  poll(runtime, selfdrive)  # observed/persisted 0
  press(runtime, selfdrive)  # active 3, pending
  native_select(runtime, selfdrive, 0)  # same value, different disk version
  poll(runtime, selfdrive)
  assert selfdrive.personality == selfdrive.params.get(KEY) == 0
  assert selfdrive.params.writes == [0, 0]


@pytest.mark.parametrize("invalid", [-1, 4, "garbage", "9999999999999999999999999999"])
def test_invalid_disk_profile_does_not_replace_active_econ(runtime, tmp_path, invalid):
  selfdrive = state(runtime, tmp_path, 3)
  selfdrive.params.external(invalid)
  poll(runtime, selfdrive)
  assert selfdrive.personality == 3
  native_select(runtime, selfdrive, 1)
  poll(runtime, selfdrive)
  assert selfdrive.personality == 1


@pytest.mark.parametrize("mvl", [True, False])
@pytest.mark.parametrize("blocked", ["reserved", "consumed", "experimental"])
def test_mvl_bypasses_stale_sla_latches_but_not_experimental_hold(runtime, tmp_path, blocked, mvl):
  selfdrive = state(runtime, tmp_path, flags=MVL_FLAG if mvl else 0)
  selfdrive.distance_button_consumed = blocked == "consumed"
  selfdrive.experimental_mode_switched = blocked == "experimental"
  changed = mvl and blocked != "experimental"
  assert runtime["NrdrSelfdrive"].update_personality(selfdrive, RELEASE, blocked == "reserved") is changed
  assert selfdrive.personality == (0 if changed else 1)
  if mvl:
    assert selfdrive.nrdr.personality_sync._pending == ((1, 0) if changed else None)
    assert not selfdrive.distance_button_consumed and not selfdrive.experimental_mode_switched
  assert not selfdrive.params.writes


def test_mvl_ignores_stale_sla_publication_and_reservation(runtime, tmp_path):
  selfdrive = state(runtime, tmp_path)
  selfdrive.nrdr.sla_button_reserved_until = 1000.
  # No SLA enum is provided: MVL must return before interpreting the message.
  assert not selfdrive.nrdr.reserve_distance_button(object())
  assert selfdrive.nrdr.sla_button_reserved_until == 0.


@pytest.mark.parametrize("unavailable_on_press", [True, False])
def test_mvl_preserves_unavailable_press_guard_until_fresh_press(runtime, tmp_path, unavailable_on_press):
  selfdrive = state(runtime, tmp_path)

  def tick(pressed=None, available=True):
    cs = NS(cruiseState=NS(available=available), buttonEvents=[] if pressed is None else
            [NS(type=BUTTON.gapAdjustCruise, pressed=pressed)])
    return runtime["NrdrSelfdrive"].update_personality(selfdrive, cs, False)

  assert not tick(True, not unavailable_on_press)
  assert not tick(available=False)  # unavailable initially or partway through hold
  assert not tick(available=True)
  assert not tick(False)
  assert selfdrive.personality == 1 and not selfdrive.params.writes
  assert not tick(True)
  assert tick(False)
  assert selfdrive.personality == 0


def test_mvl_current_unavailability_blocks_untracked_release(runtime, tmp_path):
  selfdrive = state(runtime, tmp_path)
  cs = NS(cruiseState=NS(available=False), buttonEvents=RELEASE.buttonEvents)
  assert not runtime["NrdrSelfdrive"].update_personality(selfdrive, cs, True)
  assert selfdrive.personality == 1 and selfdrive.nrdr.personality_sync._pending is None


def start_thread(callback):
  errors = []

  def run():
    try:
      callback()
    except BaseException as error:
      errors.append(error)

  thread = Thread(target=run)
  thread.start()
  return thread, errors


def join_thread(worker):
  thread, errors = worker
  thread.join(5)
  assert not thread.is_alive() and not errors


def test_ui_commit_before_wheel_lock_is_reread_not_overwritten(runtime, tmp_path):
  selfdrive = state(runtime, tmp_path)
  press(runtime, selfdrive)  # old wheel choice 0
  entered, release, poll_waiting = Event(), Event(), Event()

  def pause_ui_commit():
    entered.set()
    assert release.wait(5)

  @contextmanager
  def observe_lock_wait(params):
    poll_waiting.set()
    with personality_write_lock(params):
      yield

  runtime["personality_write_lock"] = observe_lock_wait
  selfdrive.params.on_put = pause_ui_commit
  ui = start_thread(lambda: native_select(runtime, selfdrive, 2))
  wheel = None
  try:
    assert entered.wait(5)
    wheel = start_thread(lambda: poll(runtime, selfdrive))
    assert poll_waiting.wait(5)
    # Control-loop memory changes are not blocked by the cross-process lock.
    for _ in range(4):
      press(runtime, selfdrive)
    assert selfdrive.personality == 0
  finally:
    release.set()
    join_thread(ui)
    if wheel is not None:
      join_thread(wheel)
  assert selfdrive.personality == selfdrive.params.get(KEY) == 2
  assert selfdrive.params.writes == [2]
  assert selfdrive.nrdr.personality_sync._pending is None


def test_ui_attempt_before_wheel_commit_waits_then_exits_econ(runtime, tmp_path):
  selfdrive = state(runtime, tmp_path, 0)
  press(runtime, selfdrive)  # pending Econ
  entered, release, ui_waiting = Event(), Event(), Event()

  def pause_wheel_commit():
    if len(selfdrive.params.writes) == 1:
      entered.set()
      assert release.wait(5)

  def select():
    ui_waiting.set()
    native_select(runtime, selfdrive, 1)

  selfdrive.params.on_put = pause_wheel_commit
  wheel = start_thread(lambda: poll(runtime, selfdrive))
  ui = None
  try:
    assert entered.wait(5)
    ui = start_thread(select)
    assert ui_waiting.wait(5)
    for _ in range(4):
      press(runtime, selfdrive)
    assert selfdrive.personality == 3
    assert selfdrive.params.writes == [3]  # UI cannot enter Params.put yet.
  finally:
    release.set()
    join_thread(wheel)
    if ui is not None:
      join_thread(ui)
  poll(runtime, selfdrive)
  assert selfdrive.personality == selfdrive.params.get(KEY) == 1
  assert selfdrive.params.writes == [3, 1]
  assert selfdrive.nrdr.personality_sync._pending is None


def test_lock_failure_keeps_latest_wheel_request(runtime, tmp_path):
  selfdrive = state(runtime, tmp_path)

  @contextmanager
  def failed_lock(_):
    raise OSError("lock unavailable")
    yield

  runtime["personality_write_lock"] = failed_lock
  for expected in (0, 3, 2):
    press(runtime, selfdrive)
    poll(runtime, selfdrive)
    assert selfdrive.personality == expected
  assert selfdrive.params.writes == []
  runtime["personality_write_lock"] = personality_write_lock
  poll(runtime, selfdrive)
  assert selfdrive.personality == selfdrive.params.get(KEY) == 2


@pytest.mark.parametrize("flags,expected", [(MVL_FLAG, 0), (0, 1)])
def test_real_hud_submode_consumption_is_bypassed_only_in_mvl(runtime, tmp_path, flags, expected):
  definitions("openpilot/nrdr/features/driver_policy/hud_submode.py", runtime)
  selfdrive = state(runtime, tmp_path, flags=flags)
  selfdrive.params.other.update(NrdrCruiseButtonSubMode=True, NrdrHudSubModeUntil=0)
  changed = runtime["NrdrSelfdrive"].update_personality(selfdrive, RELEASE, False)
  assert changed is (flags == MVL_FLAG)
  assert selfdrive.personality == expected
  assert selfdrive.params.other["NrdrHudSubModeUntil"] == (0 if flags else 115.)
  assert selfdrive.params.writes == []  # No profile disk write on the wheel tick.


def test_startup_sanitize_is_locked_and_not_queued(runtime, tmp_path):
  selfdrive = state(runtime, tmp_path, initial=3, flags=0)
  selfdrive.CP.brand = "toyota"
  tree = ast.parse((ROOT / "openpilot/sunnypilot/__init__.py").read_text())
  sanitize = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "get_sanitize_int_param")
  tree = ast.parse((ROOT / "openpilot/selfdrive/selfdrived/selfdrived.py").read_text())
  cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "SelfdriveD")
  init = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "__init__")
  block = next(n for n in init.body if isinstance(n, ast.With) and
               ast.unparse(n.items[0].context_expr) == "personality_write_lock(self.params)")
  runtime["self"] = selfdrive
  runtime["log"].LongitudinalPersonality.schema.enumerants = {str(i): i for i in range(4)}
  exec(compile(ast.Module(body=[sanitize, block], type_ignores=[]), "<startup profile>", "exec"), runtime)
  assert selfdrive.personality == selfdrive.params.get(KEY) == 2
  assert selfdrive.params.writes == [2]


class ProfilePath:
  def __init__(self, path):
    self.path = path

  def get_param_path(self, key):
    assert key == KEY
    return self.path


def acquire_in_process(path, attempted, acquired):
  attempted.set()
  with personality_write_lock(ProfilePath(path)):
    acquired.set()


def test_profile_lock_excludes_other_process_and_survives_key_cleanup(tmp_path):
  path = str(tmp_path / KEY)
  params = ProfilePath(path)
  ctx = multiprocessing.get_context("spawn")
  attempted, acquired = ctx.Event(), ctx.Event()
  process = ctx.Process(target=acquire_in_process, args=(path, attempted, acquired))
  with personality_write_lock(params):
    lock_path = personality_lock_path(params)
    assert lock_path.parent != tmp_path
    # Param cleanup cannot unlink/replace the separate lock inode.
    (tmp_path / KEY).write_text("1")
    (tmp_path / KEY).unlink()
    process.start()
    assert attempted.wait(5)
    assert not acquired.wait(.2)
  process.join(5)
  if process.is_alive():
    process.terminate()
    process.join(5)
  assert process.exitcode == 0 and acquired.is_set()
  assert personality_lock_path(ProfilePath(str(tmp_path / "other-prefix" / KEY))) != lock_path


def test_failed_native_write_releases_profile_lock(tmp_path):
  params = AtomicParams(tmp_path, 1)

  def fail():
    raise OSError("failed before rename")

  params.on_put = fail
  with pytest.raises(OSError):
    write_personality(params, 3)
  params.on_put = lambda: None
  write_personality(params, 2)
  assert params.get(KEY) == 2


class MultiToggle:
  enabled = True

  def __init__(self, _text, options, *_args, **_kwargs):
    self._options = options

  def set_value(self, value):
    self.value = value

  def _handle_mouse_release(self, _pos):
    self.value = self._options[(self._options.index(self.value) + 1) % len(self._options)]


def test_mici_actual_profile_handler_uses_shared_writer_and_exits_econ(runtime, tmp_path):
  selfdrive = state(runtime, tmp_path, 3)
  env = {"Params": lambda: selfdrive.params, "tuning_write_allowed": lambda *_: True,
         "write_personality": write_personality, "BigMultiToggle": MultiToggle,
         "Callable": Callable, "Union": Union, "rl": NS(Texture=object), "MousePos": object}
  path = ROOT / "openpilot/selfdrive/ui/mici/widgets/button.py"
  tree = ast.parse(path.read_text())
  nodes = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name in ("_ParamWritePolicy", "BigMultiParamToggle")]
  exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), env)
  control = env["BigMultiParamToggle"]("profile", KEY, ["aggressive", "standard", "relaxed", "econ"])
  control._handle_mouse_release(None)
  poll(runtime, selfdrive)
  assert selfdrive.personality == selfdrive.params.get(KEY) == 0
  assert selfdrive.params.writes == [0]


def remote_writer(params):
  # Execute saveParams and its real admission policy; omit only local imports
  # of native dependencies that are irrelevant to the personality branch.
  env = {"params": params, "base64": base64, "gzip": gzip, "Path": Path,
         "REQUEST": "NrdrResetLiveGas", "MVL_LOCK_KEYS": frozenset(), "mvl_tuning_locked": lambda _: False,
         "tuning_write_allowed": lambda *_args, **_kw: True, "BLOCKED_PARAMS": frozenset(),
         "cloudlog": NS(warning=lambda *_: None, error=lambda *_: None), "write_personality": write_personality}
  definitions("openpilot/nrdr/features/services/sunnylink.py", env)
  path = ROOT / "openpilot/sunnypilot/sunnylink/athena/sunnylinkd.py"
  tree = ast.parse(path.read_text())
  node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "saveParams")
  node.decorator_list = []
  node.body = [n for n in node.body if not isinstance(n, (ast.Import, ast.ImportFrom))]
  exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), "exec"), env)
  return env["saveParams"]


@pytest.mark.parametrize("compressed", [False, True])
@pytest.mark.parametrize("selected", [0, 1, 2, 3])
def test_remote_actual_profile_handler_uses_shared_writer(runtime, tmp_path, compressed, selected):
  selfdrive = state(runtime, tmp_path, 3)
  raw = str(selected).encode()
  encoded = base64.b64encode(gzip.compress(raw) if compressed else raw).decode()
  remote_writer(selfdrive.params)({KEY: encoded}, compressed)
  poll(runtime, selfdrive)
  assert selfdrive.personality == selfdrive.params.get(KEY) == selected
  assert selfdrive.params.writes == [selected]


def test_remote_profile_policy_still_blocks_onroad(runtime, tmp_path):
  selfdrive = state(runtime, tmp_path, 3)
  selfdrive.params.other["IsOffroad"] = False
  remote_writer(selfdrive.params)({KEY: base64.b64encode(b"1").decode()})
  poll(runtime, selfdrive)
  assert selfdrive.personality == 3
  assert not selfdrive.params.writes


@pytest.mark.parametrize("value", [b"4", b"-1", b"true", b"garbage"])
def test_remote_invalid_profile_is_reported_without_writing(runtime, tmp_path, value):
  selfdrive = state(runtime, tmp_path, 3)
  with pytest.raises(ValueError, match="could not be saved"):
    remote_writer(selfdrive.params)({KEY: base64.b64encode(value).decode()})
  assert selfdrive.params.get(KEY) == 3 and not selfdrive.params.writes


def test_remote_profile_storage_failure_is_not_reported_as_success(runtime, tmp_path):
  selfdrive = state(runtime, tmp_path, 3)

  def fail():
    raise OSError("storage unavailable")

  selfdrive.params.on_put = fail
  with pytest.raises(ValueError, match="could not be saved"):
    remote_writer(selfdrive.params)({KEY: base64.b64encode(b"1").decode()})
  assert selfdrive.params.get(KEY) == 3
