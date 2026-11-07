"""Execute production button/constraint code with no device or native services."""

import ast
import bisect
from abc import abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from threading import Lock
from types import SimpleNamespace as NS

import pytest
from openpilot.nrdr.tests.test_mvl_cruise import MVL_FLAG, load_policy


ROOT = Path(__file__).resolve().parents[3]
PREFERENCES = ("ExperimentalMode", "DynamicExperimentalControl", "CustomAccIncrementsEnabled",
               "SmartCruiseControlVision", "SmartCruiseControlMap")


def load_definitions(relative, names, namespace):
  source = ROOT / relative
  tree = ast.parse(source.read_text(encoding="utf-8"))
  nodes = [n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name in names]
  exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), "exec"), namespace)


class RecordingParams:
  def __init__(self, values=None):
    self.values = dict(values or {})
    self.queue = []
    self.actions = []
    self.on_remove = lambda _: None

  def get(self, key):
    return self.values.get(key)

  def get_bool(self, key):
    return bool(self.get(key))

  def put(self, key, value, block=False):
    self.actions.append(("put", key, value))
    if block:
      self.values[key] = value
    else:
      self.queue.append((key, value))

  put_bool = put

  def remove(self, key):
    self.actions.append(("remove", key))
    self.values.pop(key, None)
    self.on_remove(key)

  def flush(self):
    for key, value in self.queue:
      self.values[key] = value
    self.queue.clear()


def constraints(params, *, has_long=True, cp=True, steer_control_type=1, has_bsm=True):
  namespace = {"UI_CONSTRAINT_PARAMS": PREFERENCES}
  load_definitions("openpilot/nrdr/ui/settings_policy.py", {"snapshot_params", "restore_params", "_restore_params"}, namespace)
  source = ROOT / "openpilot/selfdrive/ui/sunnypilot/ui_state.py"
  tree = ast.parse(source.read_text(encoding="utf-8"))
  cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "UIStateSP")
  method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_enforce_constraints")
  namespace["car"] = NS(CarParams=NS(SteerControlType=NS(angle=2)))
  exec(compile(ast.Module(body=[method], type_ignores=[]), str(source), "exec"), namespace)
  state = NS(params=params, has_longitudinal_control=has_long, has_icbm=False,
             CP=NS(steerControlType=steer_control_type, alphaLongitudinalAvailable=False, enableBsm=has_bsm) if cp else None,
             CP_SP=NS(intelligentCruiseButtonManagementAvailable=False))
  namespace["_enforce_constraints"](state)
  return state


@pytest.mark.parametrize("key", PREFERENCES)
@pytest.mark.parametrize("initial", (False, True))
@pytest.mark.parametrize("when", ("during_refresh", "after_refresh"))
def test_ui_refresh_cannot_restore_stale_preference(key, initial, when):
  params = RecordingParams(dict.fromkeys(PREFERENCES, initial))
  if when == "during_refresh":
    params.on_remove = lambda removed: params.values.update({key: not initial}) if removed == "AlphaLongitudinalEnabled" else None
  constraints(params)
  if when == "after_refresh":
    params.values[key] = not initial  # A committed button/remote write before queued UI writes drain.
  params.flush()
  assert params.values[key] is not initial
  assert not any(action[1] in PREFERENCES for action in params.actions)


@pytest.mark.parametrize("has_long,cp", ((False, False), (False, True), (True, True)))
def test_ui_preserves_preferences_without_delete_restore_cycle(has_long, cp):
  params = RecordingParams(dict.fromkeys(PREFERENCES, True))
  constraints(params, has_long=has_long, cp=cp)
  params.flush()
  assert all(params.values[key] is True for key in PREFERENCES)
  assert not any(action[1] in PREFERENCES for action in params.actions)
  assert ("remove", "AlphaLongitudinalEnabled") in params.actions
  assert ("remove", "IntelligentCruiseButtonManagement") in params.actions


def test_unrelated_vehicle_constraints_are_still_enforced():
  forbidden = ("EnforceTorqueControl", "LateralJerkTorqueController",
               "AlphaLongitudinalEnabled", "AutoLaneChangeBsmDelay", "IntelligentCruiseButtonManagement")
  params = RecordingParams(dict.fromkeys((*PREFERENCES, *forbidden), True))
  constraints(params, steer_control_type=2, has_bsm=False)
  params.flush()
  assert all(key not in params.values for key in forbidden)
  assert all(params.values[key] is True for key in PREFERENCES)


class Button(IntEnum):
  gapAdjustCruise = 3
  other = 4

  @property
  def raw(self):
    return int(self)


def button_stack(*, long_enabled=True, brand="honda", initial_mode=True, mvl=False, saved_mvl=False):
  params = RecordingParams({"ExperimentalMode": initial_mode, "HondaLiveLearningGas": saved_mvl})
  namespace = {"ButtonType": Button, "Params": lambda: params, "structs": NS(CarParams=object),
               "DISTANCE_LONG_PRESS": 50, "EventNameSP": NS(experimentalModeSwitched="switched"),
               "consume_button_press": lambda _: True,
                "StockCmbsAlerts": lambda: object(), "time": NS(monotonic=lambda: 100.),
               "nrdr_longitudinal_enabled": lambda cp: cp.brand == "honda",
               "longitudinal_personality": lambda value, _: value,
               "log": NS(LongitudinalPersonality=NS(schema=NS(enumerants=dict.fromkeys(range(4)))))}
  load_policy(namespace)
  load_definitions("openpilot/sunnypilot/selfdrive/car/cruise_helpers.py", {"CruiseHelper"}, namespace)
  load_definitions("openpilot/nrdr/hooks/selfdrived.py", {"NrdrSelfdrive", "MvlPersonalitySync"}, namespace)
  helper = namespace["CruiseHelper"](NS(openpilotLongitudinalControl=long_enabled, brand=brand,
                                       flags=MVL_FLAG if mvl else 0))
  helper.personality = 1
  helper.nrdr = namespace["NrdrSelfdrive"](helper.CP)
  if namespace["mvl_longitudinal_enabled"](helper.CP):
    # Exercise the real MVL cycle/latches without disk-backed initialization.
    # Atomic persistence is covered by test_mvl_personality_sync.py.
    sync = namespace["MvlPersonalitySync"].__new__(namespace["MvlPersonalitySync"])
    sync._lock, sync._version, sync._pending = Lock(), 0, None
    helper.nrdr.personality_sync = sync
  events = []

  def tick(pressed=None, *, reserved=False, available=True, flush_writes=True):
    cs = NS(cruiseState=NS(available=available), buttonEvents=[] if pressed is None else [NS(type=Button.gapAdjustCruise, pressed=pressed)])
    helper.update(cs, NS(add=events.append), params.get_bool("ExperimentalMode"), distance_button_reserved=reserved)
    changed = namespace["NrdrSelfdrive"].update_personality(helper, cs, reserved)
    if flush_writes:
      params.flush()
    return changed

  return helper, params, events, tick


def hold(tick, **kwargs):
  tick(True, **kwargs)
  for _ in range(49):
    tick(**kwargs)


@pytest.mark.parametrize("mvl", (False, True))
def test_repeated_holds_toggle_once_each_without_personality_change(mvl):
  helper, params, events, tick = button_stack(mvl=mvl)
  for expected in (False, True, False):
    hold(tick)
    assert params.get_bool("ExperimentalMode") is expected
    for _ in range(100):
      tick()
    assert params.get_bool("ExperimentalMode") is expected
    assert not tick(False)
    assert not helper.experimental_mode_switched
  assert events == ["switched"] * 3
  assert helper.personality == 1


@pytest.mark.parametrize("release_reserved", (False, True))
def test_reserved_release_resets_latch_and_next_hold_works(release_reserved):
  helper, params, events, tick = button_stack()
  hold(tick)
  tick(reserved=True)
  assert not tick(False, reserved=release_reserved)
  assert helper.button_frame_counts[Button.gapAdjustCruise] == 0
  assert not helper.experimental_mode_switched
  hold(tick)
  assert params.get_bool("ExperimentalMode") is True
  assert events == ["switched", "switched"]
  assert helper.personality == 1


def test_sla_confirmation_cannot_turn_into_a_delayed_toggle_or_personality_change():
  helper, params, events, tick = button_stack()
  hold(tick, reserved=True)
  for _ in range(100):
    tick()  # Planner reservation expires while the same physical press continues.
  assert not tick(False)
  assert events == []
  assert helper.personality == 1
  hold(tick)
  assert params.get_bool("ExperimentalMode") is False
  assert events == ["switched"]


@pytest.mark.parametrize("mvl", (False, True))
def test_release_while_cruise_unavailable_does_not_stick(mvl):
  helper, params, events, tick = button_stack(mvl=mvl)
  hold(tick)
  tick(False, available=False)
  for _ in range(100):
    tick()
  assert events == ["switched"]
  assert helper.button_frame_counts[Button.gapAdjustCruise] == 0
  hold(tick)
  assert params.get_bool("ExperimentalMode") is True
  assert events == ["switched", "switched"]


@pytest.mark.parametrize("mvl", (False, True))
def test_unavailable_press_requires_fresh_press_after_cruise_returns(mvl):
  _, _, events, tick = button_stack(mvl=mvl)
  hold(tick, available=False)
  for _ in range(100):
    tick()
  assert not tick(False)
  assert not events
  hold(tick)
  assert events == ["switched"]


@pytest.mark.parametrize("brand,expected", (("honda", 3), ("toyota", 2)))
@pytest.mark.parametrize("mvl", (False, True))
def test_short_press_keeps_existing_personality_count(brand, expected, mvl):
  helper, _, events, tick = button_stack(brand=brand, mvl=mvl)
  helper.personality = 0
  tick(True)
  for _ in range(10):
    tick()
  assert tick(False)
  assert helper.personality == expected
  assert not events


def test_stock_longitudinal_cannot_toggle_experimental_mode():
  _, params, events, tick = button_stack(long_enabled=False)
  hold(tick)
  assert not tick(False)
  assert not params.actions
  assert not events


@pytest.mark.parametrize("saved_mvl", (False, True))
@pytest.mark.parametrize("initial_mode", (False, True))
def test_mvl_hold_toggles_once_without_personality_change_regardless_of_saved_choice(saved_mvl, initial_mode):
  helper, params, events, tick = button_stack(mvl=True, saved_mvl=saved_mvl, initial_mode=initial_mode)
  for expected in (not initial_mode, initial_mode, not initial_mode):
    hold(tick)
    for _ in range(80):
      tick()
    assert params.get_bool("ExperimentalMode") is expected
    assert helper.experimental_mode_switched
    assert not tick(False)
    assert not helper.experimental_mode_switched
    params.values["HondaLiveLearningGas"] = not params.values["HondaLiveLearningGas"]
  assert helper.mvl_enabled is True
  assert helper.personality == 1 and helper.nrdr.personality_sync._pending is None
  assert events == ["switched"] * 3
  assert params.actions == [("put", "ExperimentalMode", value) for value in (not initial_mode, initial_mode, not initial_mode)]


def test_mvl_stale_sla_cannot_block_hold_or_four_personality_short_presses():
  helper, params, events, tick = button_stack(mvl=True)
  helper.nrdr.sla_button_reserved_until = 1000.
  reserved = helper.nrdr.reserve_distance_button(object())
  assert not reserved and helper.nrdr.sla_button_reserved_until == 0.
  hold(tick, reserved=reserved)
  assert not tick(False)
  assert events == ["switched"] and not params.get_bool("ExperimentalMode")
  for generation, expected in enumerate((0, 3, 2, 1), 1):
    tick(True)
    assert tick(False)
    assert helper.personality == expected
    assert helper.nrdr.personality_sync._pending == (generation, expected)
  assert params.actions == [("put", "ExperimentalMode", False)]


@pytest.mark.parametrize("mvl", (False, True))
def test_cruise_loss_mid_hold_blocks_both_actions_until_fresh_press(mvl):
  helper, params, events, tick = button_stack(mvl=mvl)
  tick(True)
  for _ in range(10):
    tick()
  tick(available=False)
  for _ in range(100):
    tick()
  assert not tick(False)
  assert not events and not params.actions and helper.personality == 1
  hold(tick)
  assert not tick(False)
  assert events == ["switched"] and not params.get_bool("ExperimentalMode")


@pytest.mark.parametrize("saved_mvl", (False, True))
def test_unlatched_honda_hold_keeps_legacy_behavior_even_with_saved_choice(saved_mvl):
  helper, params, events, tick = button_stack(mvl=False, saved_mvl=saved_mvl)
  hold(tick)
  assert helper.mvl_enabled is False
  assert params.get_bool("ExperimentalMode") is False
  assert events == ["switched"]


def test_selfdrived_always_passes_reservation_to_button_tracker():
  source = ROOT / "openpilot/selfdrive/selfdrived/selfdrived.py"
  tree = ast.parse(source.read_text(encoding="utf-8"))
  cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "SelfdriveD")
  method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "update_events")
  calls = [n.value for n in method.body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
           and ast.unparse(n.value.func) == "CruiseHelper.update"]
  assert len(calls) == 1
  assert any(k.arg == "distance_button_reserved" and ast.unparse(k.value) == "button_reserved" for k in calls[0].keywords)


def test_runtime_longitudinal_gate_is_still_required():
  source = (ROOT / "openpilot/selfdrive/selfdrived/selfdrived.py").read_text(encoding="utf-8")
  assert 'self.params.get_bool("ExperimentalMode") and self.CP.openpilotLongitudinalControl' in source


def alert_stack(helper):
  """Run the production event factory, dispatcher and alert manager without cereal."""
  status = NS(normal=0)
  size = NS(none=0, small=1, mid=2)
  visual = audible = NS(none=0)
  namespace = {"bisect": bisect, "IntEnum": IntEnum, "abstractmethod": abstractmethod, "DT_CTRL": 0.01,
               "AlertCallbackType": object, "AlertStatus": status, "AlertSize": size, "VisualAlert": visual, "AudibleAlert": audible,
               "log": NS(SelfdriveState=NS(AlertStatus=object, AlertSize=object, AudibleAlert=object)),
               "car": NS(CarControl=NS(HUDControl=NS(VisualAlert=object))),
               "defaultdict": defaultdict, "dataclass": dataclass,
               "custom": NS(OnroadEventSP=NS(EventName=NS(experimentalModeSwitched="switched"))),
               "LONGITUDINAL_PERSONALITY_MAP": {1: "standard"}}
  load_definitions("openpilot/sunnypilot/selfdrive/selfdrived/events_base.py",
                   {"Priority", "ET", "Alert", "NormalPermanentAlert", "EventsBase"}, namespace)
  load_definitions("openpilot/sunnypilot/selfdrive/selfdrived/events.py", {"experimental_mode_switched_alert", "EventsSP"}, namespace)

  # Evaluate the real mapping entry, so an unwired callback cannot pass these tests.
  source = ROOT / "openpilot/sunnypilot/selfdrive/selfdrived/events.py"
  tree = ast.parse(source.read_text(encoding="utf-8"))
  mapping = next(n.value for n in tree.body if isinstance(n, ast.AnnAssign) and ast.unparse(n.target) == "EVENTS_SP")
  entry = next(v for k, v in zip(mapping.keys, mapping.values, strict=True) if ast.unparse(k) == "EventNameSP.experimentalModeSwitched")
  namespace["EVENTS_SP"] = {"switched": eval(compile(ast.Expression(entry), str(source), "eval"), namespace)}
  namespace["EVENT_NAME_SP"] = {"switched": "experimentalModeSwitched"}
  namespace["EmptyAlert"] = namespace["NormalPermanentAlert"]("", duration=0.)
  load_definitions("openpilot/selfdrive/selfdrived/alertmanager.py", {"AlertEntry", "AlertManager"}, namespace)

  source = ROOT / "openpilot/selfdrive/selfdrived/selfdrived.py"
  tree = ast.parse(source.read_text(encoding="utf-8"))
  cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "SelfdriveD")
  method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "update_alerts")
  exec(compile(ast.Module(body=[method], type_ignores=[]), str(source), "exec"), namespace)

  helper.events = NS(create_alerts=lambda *_: [])
  helper.events_sp = namespace["EventsSP"]()
  helper.AM = namespace["AlertManager"]()
  helper.sm = NS(frame=1)
  helper.enabled = True
  helper.is_metric = False
  helper.state_machine = NS(current_alert_types=[namespace["ET"].WARNING], soft_disable_timer=0)
  return NS(**namespace)


@pytest.mark.parametrize("initial_mode", (False, True))
@pytest.mark.parametrize("write_flushed", (False, True))
@pytest.mark.parametrize("mvl", (False, True))
def test_experimental_alert_uses_button_result_before_param_poller_catches_up(initial_mode, write_flushed, mvl):
  helper, params, events, tick = button_stack(initial_mode=initial_mode, mvl=mvl)
  runtime = alert_stack(helper)
  helper.experimental_mode = initial_mode  # params_thread has not observed the toggle yet.
  hold(tick, flush_writes=False)
  assert events == ["switched"]
  assert params.get_bool("ExperimentalMode") is initial_mode
  assert params.queue == [("ExperimentalMode", not initial_mode)]
  if write_flushed:
    params.flush()  # The disk writer and params_thread can catch up independently.
  helper.events_sp.add(events[0])
  runtime.update_alerts(helper, NS())

  alert = helper.AM.current_alert
  assert alert.alert_text_1 == ("Experimental Mode Off" if initial_mode else "Experimental Mode On")
  assert alert.alert_text_2 == ""
  assert alert.alert_type == "experimentalModeSwitched/warning"
  assert alert.event_type == runtime.ET.WARNING
  assert alert.duration == 150  # Preserve the existing 1.5-second warning.
  assert alert.priority == runtime.Priority.LOWER
  assert alert.alert_size == runtime.AlertSize.small
  assert alert.alert_status == runtime.AlertStatus.normal
  assert alert.visual_alert == runtime.VisualAlert.none
  assert alert.audible_alert == runtime.AudibleAlert.none
  assert params.actions == [("put", "ExperimentalMode", not initial_mode)]

  # Once queued, the displayed message must not track later param/thread changes.
  helper.events_sp.clear()
  params.flush()
  helper.experimental_mode = not initial_mode
  helper.sm.frame += 1
  runtime.update_alerts(helper, NS())
  assert helper.AM.current_alert is alert


@pytest.mark.parametrize("mvl", (False, True))
def test_repeated_toggles_get_independent_alert_snapshots(mvl):
  helper, _, events, tick = button_stack(mvl=mvl)
  runtime = alert_stack(helper)
  snapshots = []
  for expected in ("Experimental Mode Off", "Experimental Mode On", "Experimental Mode Off"):
    hold(tick)
    helper.events_sp.add(events[-1])
    runtime.update_alerts(helper, NS())
    snapshots.append(helper.AM.current_alert)
    assert snapshots[-1].alert_text_1 == expected
    helper.events_sp.clear()
    tick(False)
    helper.sm.frame += 50

  assert [alert.alert_text_1 for alert in snapshots] == ["Experimental Mode Off", "Experimental Mode On", "Experimental Mode Off"]
  assert len({id(alert) for alert in snapshots}) == 3


def test_event_specific_state_preserves_other_callbacks_and_warning_filter():
  helper, _, _, _ = button_stack()
  runtime = alert_stack(helper)
  seen = []

  def other_callback(*args):
    seen.append(args)
    return runtime.NormalPermanentAlert("Other warning")

  runtime.EVENTS_SP["other"] = {runtime.ET.WARNING: other_callback}
  runtime.EVENT_NAME_SP["other"] = "other"
  helper.events_sp.event_counters["other"] = 0
  helper.events_sp.add("other")
  helper.events_sp.add("switched")
  helper._experimental_mode = True
  cs = NS()
  runtime.update_alerts(helper, cs)
  assert seen == [(helper.CP, cs, helper.sm, False, 0, "standard")]
  assert helper.AM.alerts["experimentalModeSwitched/warning"].alert.alert_text_1 == "Experimental Mode On"

  helper.state_machine.current_alert_types = [runtime.ET.PERMANENT]
  runtime.update_alerts(helper, cs)
  assert len(seen) == 1
  assert helper.AM.current_alert is runtime.EmptyAlert

  # Legacy callers still pass their original callback arguments unchanged.
  helper.events_sp.remove("switched")
  alerts = helper.events_sp.create_alerts([runtime.ET.WARNING], ["legacy"])
  assert alerts[0].alert_text_1 == "Other warning"
  assert seen[-1] == ("legacy",)
