"""Execute ICBM host definitions with real car messages and no native Params/UI.

Windows regression coverage, not CAN transmission or vehicle acceptance.
"""
import ast
from enum import IntEnum
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

import pytest

from opendbc.car import apply_hysteresis
from opendbc.car.honda.values import CAR, HondaFlags
from opendbc.car.structs import car
from openpilot.nrdr.ui.icbm import icbm_available
from openpilot.common.constants import CV


ROOT = Path(__file__).resolve().parents[3]
CONTROLLER = "openpilot/sunnypilot/selfdrive/car/intelligent_cruise_button_management/controller.py"
CRUISE = "openpilot/sunnypilot/selfdrive/car/cruise_ext.py"
INTERFACES = "openpilot/sunnypilot/selfdrive/car/interfaces.py"
UI = "openpilot/selfdrive/ui/sunnypilot/ui_state.py"
KEY = "IntelligentCruiseButtonManagement"
ButtonType = car.CarState.ButtonEvent.Type
BUTTONS = (ButtonType.accelCruise, ButtonType.decelCruise, ButtonType.cancel, ButtonType.mainCruise,
           ButtonType.setCruise, ButtonType.resumeCruise, ButtonType.gapAdjustCruise, ButtonType.lkas)


class State(IntEnum):
  inactive, preActive, increasing, decreasing, holding = range(5)


class SendButtonState(IntEnum):
  none, increase, decrease = range(3)


def definitions(relative, names, env, *, class_name=None):
  path = ROOT / relative
  tree = ast.parse(path.read_text(encoding="utf-8"))
  body = tree.body if class_name is None else next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name).body
  selected = [n for n in body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names or
              isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in n.targets)]
  assert selected
  future = ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)
  exec(compile(ast.fix_missing_locations(ast.Module(body=[future, *selected], type_ignores=[])), str(path), "exec"), env)
  return env


def car_params(*, bosch=False, op_long=False, available=True, pcm_speed=False, interceptor=False):
  cp = NS(carFingerprint=CAR.HONDA_CIVIC_BOSCH if bosch else CAR.HONDA_CIVIC,
          flags=HondaFlags.BOSCH if bosch else HondaFlags.NIDEC, brand="honda",
          openpilotLongitudinalControl=op_long, pcmCruise=True, steerControlType=0,
          alphaLongitudinalAvailable=False, enableBsm=True)
  sp = NS(pcmCruiseSpeed=pcm_speed, intelligentCruiseButtonManagementAvailable=available, enableGasInterceptor=interceptor)
  return cp, sp


def controller(*, bosch=False, **kwargs):
  env = {"State": State, "SendButtonState": SendButtonState, "ButtonType": ButtonType,
         "CV": CV, "DT_CTRL": .01, "apply_hysteresis": apply_hysteresis,
         "icbm_available": icbm_available}
  definitions(CRUISE, {"CRUISE_BUTTON_TIMER", "update_manual_button_timers"}, env)
  definitions("openpilot/sunnypilot/selfdrive/car/intelligent_cruise_button_management/helpers.py", {"get_minimum_set_speed"}, env)
  definitions(CONTROLLER, {"HYST_GAP", "INACTIVE_TIMER", "SEND_BUTTONS", "IntelligentCruiseButtonManagement"}, env)
  cp, sp = car_params(bosch=bosch, **kwargs)
  return env["IntelligentCruiseButtonManagement"](cp, sp), env


def inputs():
  cs = car.CarState.new_message(vEgo=20., cruiseState={"enabled": True, "available": True, "speedCluster": 20.})
  cc = car.CarControl.new_message(enabled=True)
  return cs, cc, NS(vTarget=25.)


def run_ticks(icbm, cs, cc, plan, count, metric=True):
  for _ in range(count):
    icbm.run(cs, cc, plan, metric)


def assert_restart_delay(icbm, cs, cc, plan):
  icbm.run(cs, cc, plan, True)
  assert icbm.state == State.preActive and icbm.pre_active_timer == 40
  run_ticks(icbm, cs, cc, plan, 39)
  assert icbm.cruise_button == SendButtonState.none
  icbm.run(cs, cc, plan, True)
  assert icbm.cruise_button == SendButtonState.increase


@pytest.mark.parametrize("bosch", [False, True])
def test_stock_acc_delay_and_target_direction_preserved(bosch):
  icbm, _ = controller(bosch=bosch)
  cs, cc, plan = inputs()
  assert_restart_delay(icbm, cs, cc, plan)
  cs.cruiseState.speedCluster = 25.
  icbm.run(cs, cc, plan, True)
  assert icbm.state == State.holding and icbm.cruise_button == SendButtonState.none
  plan.vTarget = 20.
  run_ticks(icbm, cs, cc, plan, 2)
  assert icbm.cruise_button == SendButtonState.decrease


@pytest.mark.parametrize("bosch", [False, True])
@pytest.mark.parametrize("blocked", ["op_long", "fixed_pcm", "legacy_pcm", "mvl", "unavailable", "pcm_speed", "cp_missing", "sp_missing"])
def test_ineligible_state_clears_pending_button_and_fixed_pcm_cannot_bypass(bosch, blocked):
  icbm, _ = controller(bosch=bosch)
  cs, cc, plan = inputs()
  run_ticks(icbm, cs, cc, plan, 41)
  assert icbm.cruise_button == SendButtonState.increase
  cp, sp = icbm.CP, icbm.CP_SP
  if blocked in ("op_long", "fixed_pcm", "legacy_pcm", "mvl"):
    cp.openpilotLongitudinalControl = True
    cp.flags |= {"op_long": 0, "fixed_pcm": 262144,
                 "legacy_pcm": 524288, "mvl": HondaFlags.MVL_LONGITUDINAL}[blocked]
    # Explicitly preserve False: Fixed's target ownership is NOT ICBM admission.
    sp.pcmCruiseSpeed = False
  elif blocked == "unavailable":
    sp.intelligentCruiseButtonManagementAvailable = False
  elif blocked == "pcm_speed":
    sp.pcmCruiseSpeed = True
  elif blocked == "cp_missing":
    icbm.CP = None
  else:
    icbm.CP_SP = None
  run_ticks(icbm, cs, cc, plan, 100)
  assert icbm.state == State.inactive and icbm.cruise_button == SendButtonState.none
  assert not icbm.is_ready and not icbm.is_ready_prev and icbm.pre_active_timer == 0
  icbm.CP, icbm.CP_SP = car_params(bosch=bosch)
  assert_restart_delay(icbm, cs, cc, plan)


@pytest.mark.parametrize("bosch", [False, True])
@pytest.mark.parametrize("group,field,value", [
  ("cc", "enabled", False), ("stock", "enabled", False),
  ("cs", "gasPressed", True), ("cs", "brakePressed", True),
  ("cs", "standstill", True), ("stock", "standstill", True),
  ("cruise", "override", True), ("cruise", "cancel", True), ("cruise", "resume", True),
])
def test_readiness_interrupts_immediately_and_restarts_delay(bosch, group, field, value):
  icbm, _ = controller(bosch=bosch)
  cs, cc, plan = inputs()
  run_ticks(icbm, cs, cc, plan, 41)
  obj = {"cc": cc, "cs": cs, "stock": cs.cruiseState, "cruise": cc.cruiseControl}[group]
  before = getattr(obj, field)
  setattr(obj, field, value)
  run_ticks(icbm, cs, cc, plan, 60)
  assert icbm.state == State.inactive and icbm.cruise_button == SendButtonState.none
  assert icbm.pre_active_timer == 0
  setattr(obj, field, before)
  assert_restart_delay(icbm, cs, cc, plan)


@pytest.mark.parametrize("button", BUTTONS)
def test_all_manual_cruise_gap_lkas_buttons_hold_and_release(button):
  icbm, env = controller()
  cs, cc, plan = inputs()
  run_ticks(icbm, cs, cc, plan, 41)
  cs.buttonEvents = [car.CarState.ButtonEvent(type=button, pressed=True)]
  icbm.run(cs, cc, plan, True)
  cs.buttonEvents = []
  run_ticks(icbm, cs, cc, plan, 80)
  assert icbm.cruise_button == SendButtonState.none and not icbm.is_ready
  assert all(value == 0 for value in env["CRUISE_BUTTON_TIMER"].values())
  cs.buttonEvents = [car.CarState.ButtonEvent(type=button, pressed=False)]
  icbm.run(cs, cc, plan, True)
  assert icbm.state == State.inactive
  cs.buttonEvents = []
  assert_restart_delay(icbm, cs, cc, plan)


def test_manual_pulse_and_ineligible_hold_are_not_lost_and_timers_are_private():
  icbm, env = controller()
  second = env["IntelligentCruiseButtonManagement"](icbm.CP, icbm.CP_SP)
  assert icbm.cruise_button_timers is not second.cruise_button_timers
  assert icbm.cruise_button_timers is not env["CRUISE_BUTTON_TIMER"]
  cs, cc, plan = inputs()
  run_ticks(icbm, cs, cc, plan, 41)
  cs.buttonEvents = [car.CarState.ButtonEvent(type=ButtonType.lkas, pressed=p) for p in (True, False)]
  icbm.run(cs, cc, plan, True)
  assert icbm.cruise_button == SendButtonState.none
  icbm.CP_SP.intelligentCruiseButtonManagementAvailable = False
  cs.buttonEvents = [car.CarState.ButtonEvent(type=ButtonType.gapAdjustCruise, pressed=True)]
  icbm.run(cs, cc, plan, True)
  cs.buttonEvents = []
  icbm.CP_SP.intelligentCruiseButtonManagementAvailable = True
  run_ticks(icbm, cs, cc, plan, 60)
  assert icbm.cruise_button == SendButtonState.none
  assert all(value == 0 for value in second.cruise_button_timers.values())


@pytest.mark.parametrize("metric", [False, True])
@pytest.mark.parametrize("bosch", [False, True])
def test_factory_minimum_clamps_target_and_reaches_terminal_holding(metric, bosch):
  icbm, _ = controller(bosch=bosch)
  cs, cc, plan = inputs()
  floor = 30 if metric else 20
  conversion = CV.KPH_TO_MS if metric else CV.MPH_TO_MS
  cs.cruiseState.speedCluster = (floor + 1) * conversion
  plan.vTarget = 0.
  run_ticks(icbm, cs, cc, plan, 41, metric)
  assert icbm.v_cruise_min == icbm.v_target == floor
  assert icbm.cruise_button == SendButtonState.decrease
  cs.cruiseState.speedCluster = floor * conversion
  run_ticks(icbm, cs, cc, plan, 100, metric)
  assert icbm.state == State.holding and icbm.cruise_button == SendButtonState.none


@pytest.mark.parametrize("metric", [False, True])
@pytest.mark.parametrize("variant", ["stock_icbm", "bosch", "op_long", "unavailable", "stock_off", "interceptor", "fixed", "mvl", "mvl_stock"])
def test_cruise_helper_civic_minimum_is_kph_and_other_branches_unchanged(metric, variant):
  cp, sp = car_params(bosch=variant == "bosch", op_long=variant in ("op_long", "fixed", "mvl", "mvl_stock"),
                      available=variant != "unavailable", pcm_speed=variant in ("stock_off", "mvl_stock"),
                      interceptor=variant == "interceptor")
  obj = NS(CP=cp, CP_SP=sp, fixed_cruise_enabled=variant == "fixed", mvl_enabled=variant in ("mvl", "mvl_stock"))
  env = {"CV": CV, "icbm_available": icbm_available, "V_CRUISE_MIN": 0, "MVL_V_CRUISE_MIN": 8}
  definitions("openpilot/sunnypilot/selfdrive/car/intelligent_cruise_button_management/helpers.py", {"get_minimum_set_speed"}, env)
  definitions(CRUISE, {"get_minimum_set_speed"}, env, class_name="VCruiseHelperSP")
  # The class method has the same name as its module-level helper.
  method = env.pop("get_minimum_set_speed")
  definitions("openpilot/sunnypilot/selfdrive/car/intelligent_cruise_button_management/helpers.py", {"get_minimum_set_speed"}, env)
  method(obj, metric)
  expected = 30 if metric else 20
  if variant == "stock_off":
    expected = 0
  elif variant == "mvl_stock":
    expected = 8
  assert obj.v_cruise_min == expected


class Params(dict):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.actions = []

  def get_bool(self, key):
    return bool(self.get(key))

  def remove(self, key):
    self.actions.append(("remove", key))
    self.pop(key, None)

  def put_bool(self, key, value, **kwargs):
    self.actions.append(("put", key, value))
    self[key] = value


@pytest.mark.parametrize("saved", [None, False, True])
@pytest.mark.parametrize("available", [False, True])
@pytest.mark.parametrize("op_long", [False, True])
def test_interface_admission_and_cleanup_preserve_saved_choice(saved, available, op_long):
  cp, sp = car_params(available=available, op_long=op_long, pcm_speed=True)
  params = Params({} if saved is None else {KEY: saved})
  env = {"Params": lambda: pytest.fail("Injected Params was not forwarded"), "cloudlog": Mock(),
         "set_speed_limit_assist_availability": Mock(), "STATSLOGSP": Mock(),
         "structs": NS(CarParams=NS(SteerControlType=NS(angle=2)))}
  definitions(INTERFACES, {"_enforce_torque_lateral_control", "_initialize_intelligent_cruise_button_management",
                         "_initialize_torque_lateral_control", "_cleanup_unsupported_params", "setup_interfaces"}, env)
  cp.to_dict = dict
  ci = NS(CP=cp, CP_SP=sp)
  for _ in range(3):
    env["setup_interfaces"](ci, params)
  assert params.get(KEY) is saved and (KEY in params) is (saved is not None)
  assert not any(action[1] == KEY for action in params.actions)
  assert sp.pcmCruiseSpeed is not bool(saved and available and not op_long)
  assert cp.pcmCruise is True and cp.openpilotLongitudinalControl is op_long
  env["set_speed_limit_assist_availability"].assert_called_with(cp, sp, params)


@pytest.mark.parametrize("saved", [None, False, True])
@pytest.mark.parametrize("mode", ["missing_cp", "missing_sp", "unavailable", "op_long", "pending_on", "active"])
def test_ui_preserves_choice_and_uses_admitted_state_not_saved_preference(saved, mode):
  cp, sp = car_params(available=mode != "unavailable", op_long=mode == "op_long", pcm_speed=mode == "pending_on")
  ui = NS(CP=None if mode == "missing_cp" else cp, CP_SP=None if mode == "missing_sp" else sp,
          params=Params({} if saved is None else {KEY: saved}), has_longitudinal_control=mode == "op_long", has_icbm=True)
  env = {"car": car, "icbm_available": icbm_available}
  definitions(UI, {"_enforce_constraints"}, env, class_name="UIStateSP")
  for _ in range(3):
    env["_enforce_constraints"](ui)
  assert ui.params.get(KEY) is saved and (KEY in ui.params) is (saved is not None)
  assert not any(action[1] == KEY for action in ui.params.actions)
  assert not ui.has_icbm  # Civic support is retired, including stale availability.


def test_ui_missing_persistent_sp_does_not_keep_previous_active_capability():
  class StopAfterAdmission(Exception):
    pass

  cp, sp = car_params()
  ui = NS(CP=cp, CP_SP=sp, params=Params({KEY: True}), has_icbm=True, has_longitudinal_control=False)
  env = {"car": car, "icbm_available": icbm_available, "messaging": Mock(), "custom": NS(CarParamsSP=object)}
  definitions(UI, {"update_params", "_enforce_constraints"}, env, class_name="UIStateSP")

  def enforce():
    env["_enforce_constraints"](ui)
    raise StopAfterAdmission

  ui._enforce_constraints = enforce
  with pytest.raises(StopAfterAdmission):
    env["update_params"](ui)
  assert ui.CP_SP is None and not ui.has_icbm and ui.params[KEY] is True
  env["messaging"].log_from_bytes.assert_not_called()
