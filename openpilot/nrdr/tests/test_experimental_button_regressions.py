"""Execute production button/constraint code with no device or native services."""

import ast
from enum import IntEnum
from pathlib import Path
from types import SimpleNamespace as NS

import pytest


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
  forbidden = ("EnforceTorqueControl", "NeuralNetworkLateralControl", "LateralJerkTorqueController",
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


def button_stack(*, long_enabled=True, brand="honda"):
  params = RecordingParams({"ExperimentalMode": True})
  namespace = {"ButtonType": Button, "Params": lambda: params, "structs": NS(CarParams=object),
               "DISTANCE_LONG_PRESS": 50, "EventNameSP": NS(experimentalModeSwitched="switched"),
               "consume_button_press": lambda _: True,
               "nrdr_longitudinal_enabled": lambda cp: cp.brand == "honda",
               "longitudinal_personality": lambda value, _: value,
               "log": NS(LongitudinalPersonality=NS(schema=NS(enumerants=dict.fromkeys(range(4)))))}
  load_definitions("openpilot/sunnypilot/selfdrive/car/cruise_helpers.py", {"CruiseHelper"}, namespace)
  load_definitions("openpilot/nrdr/hooks/selfdrived.py", {"NrdrSelfdrive"}, namespace)
  helper = namespace["CruiseHelper"](NS(openpilotLongitudinalControl=long_enabled, brand=brand))
  helper.personality = 1
  events = []

  def tick(pressed=None, *, reserved=False, available=True):
    cs = NS(cruiseState=NS(available=available), buttonEvents=[] if pressed is None else [NS(type=Button.gapAdjustCruise, pressed=pressed)])
    helper.update(cs, NS(add=events.append), params.get_bool("ExperimentalMode"), distance_button_reserved=reserved)
    changed = namespace["NrdrSelfdrive"].update_personality(helper, cs, reserved)
    params.flush()
    return changed

  return helper, params, events, tick


def hold(tick, **kwargs):
  tick(True, **kwargs)
  for _ in range(49):
    tick(**kwargs)


def test_repeated_holds_toggle_once_each_without_personality_change():
  helper, params, events, tick = button_stack()
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


def test_release_while_cruise_unavailable_does_not_stick():
  helper, params, events, tick = button_stack()
  hold(tick)
  tick(False, available=False)
  for _ in range(100):
    tick()
  assert events == ["switched"]
  assert helper.button_frame_counts[Button.gapAdjustCruise] == 0
  hold(tick)
  assert params.get_bool("ExperimentalMode") is True
  assert events == ["switched", "switched"]


def test_unavailable_press_requires_fresh_press_after_cruise_returns():
  _, _, events, tick = button_stack()
  hold(tick, available=False)
  for _ in range(100):
    tick()
  assert not tick(False)
  assert not events
  hold(tick)
  assert events == ["switched"]


@pytest.mark.parametrize("brand,expected", (("honda", 3), ("toyota", 2)))
def test_short_press_keeps_existing_personality_count(brand, expected):
  helper, _, events, tick = button_stack(brand=brand)
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
