"""MVL cruise preferences with real source/vehicle gates and in-memory Params.

Exercises button events and received SLA plans, not planner generation or CAN.
"""
import ast
import math
from pathlib import Path
from types import SimpleNamespace as NS

import numpy as np
import pytest

from opendbc.car.honda.pcm_test_modes import FIXED_CRUISE_MPS, qualified
from opendbc.car.honda.values import CAR, HondaFlags
from opendbc.car.structs import car
from opendbc.sunnypilot.car.honda.icbm_eligibility import civic_icbm_available
from openpilot.cereal import custom
from openpilot.common.constants import CV
from openpilot.nrdr.features.driver_policy.speed_limit import compare_cluster_target, quantize_set_speed
from openpilot.nrdr.features.longitudinal.policy import mvl_longitudinal_enabled

ROOT = Path(__file__).resolve().parents[3]
BUTTON = car.CarState.ButtonEvent.Type
SLA = custom.LongitudinalPlanSP.SpeedLimit.AssistState
PREFERENCES = {"CustomAccIncrementsEnabled": True, "CustomAccShortPressIncrement": 5, "CustomAccLongPressIncrement": 1}


class Params:
  def __init__(self, values):
    self.values = dict(values)
    self.reads = []

  def get(self, key, **_):
    self.reads.append(key)
    return self.values[key]

  def get_bool(self, key):
    return bool(self.get(key))


def definitions(relative, env):
  path = ROOT / relative
  tree = ast.parse(path.read_text(encoding="utf-8"))
  tree.body = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.Assign, ast.AnnAssign))]
  tree.body.insert(0, ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0))
  namespace = dict(env)
  exec(compile(ast.fix_missing_locations(tree), str(path), "exec"), namespace)
  return namespace


def helper(*, mvl=True, fixed=False, legacy=False, pcm=False, pcm_speed=False, stock=False, values=None):
  params = Params(PREFERENCES | (values or {}))
  env = {
    "np": np, "math": math, "CV": CV, "car": car, "custom": custom, "HondaFlags": HondaFlags,
    "Params": lambda: params, "pcm_mode_qualified": qualified, "FIXED_CRUISE_MPS": FIXED_CRUISE_MPS,
    "mvl_longitudinal_enabled": mvl_longitudinal_enabled, "civic_icbm_available": civic_icbm_available,
    "compare_cluster_target": compare_cluster_target, "quantize_set_speed": quantize_set_speed,
    "SLA_ACTIVE_STATES": (SLA.active, SLA.adapting), "consume_button_press": lambda _: True,
  }
  minimum = definitions("openpilot/sunnypilot/selfdrive/car/intelligent_cruise_button_management/helpers.py", env)
  env["get_minimum_set_speed"] = minimum["get_minimum_set_speed"]
  ext = definitions("openpilot/sunnypilot/selfdrive/car/cruise_ext.py", env)
  env["VCruiseHelperSP"] = ext["VCruiseHelperSP"]
  env["NrdrCruise"] = definitions("openpilot/nrdr/features/driver_policy/cruise.py", env)["NrdrCruise"]
  core = definitions("openpilot/selfdrive/car/cruise.py", env)
  flags = (HondaFlags.NIDEC | (HondaFlags.MVL_LONGITUDINAL if mvl else 0) |
           (HondaFlags.NIDEC_PCM_FIXED_CRUISE if fixed else 0) | (HondaFlags.NIDEC_PCM_LEGACY if legacy else 0))
  cp = NS(flags=flags, brand="honda", carFingerprint=CAR.HONDA_CIVIC, pcmCruise=pcm,
          openpilotLongitudinalControl=not stock, passive=False, dashcamOnly=False)
  sp = NS(pcmCruiseSpeed=pcm_speed, flags=0, enableGasInterceptor=False, intelligentCruiseButtonManagementAvailable=stock)
  result = core["VCruiseHelper"](cp, sp)
  result.v_cruise_kph = result.v_cruise_cluster_kph = result.fixed_cruise_kph = 80.
  result.enabled_prev = True
  return result, params


def state(button=None, pressed=False, *, pcm_speed=25., available=True):
  return car.CarState.new_message(vEgo=20.,
                                 buttonEvents=[] if button is None else [{"type": button, "pressed": pressed}],
                                 cruiseState={"available": available, "speed": pcm_speed, "speedCluster": pcm_speed + .2})


def press(cruise, button, *, long=False, metric=True):
  cruise.update_v_cruise(state(button, True), True, metric)
  if long:
    for _ in range(50):
      cruise.update_v_cruise(state(), True, metric)
  cruise.update_v_cruise(state(button, False), True, metric)


def plan(target, assist=SLA.active, *, valid=True, last_valid=False):
  return NS(speedLimit=NS(resolver=NS(speedLimitValid=valid, speedLimitLastValid=last_valid,
                                    speedLimitFinalLast=target * CV.KPH_TO_MS), assist=NS(state=assist)))


@pytest.mark.parametrize("mvl", [False, True])
@pytest.mark.parametrize("button,direction", [(BUTTON.accelCruise, 1), (BUTTON.decelCruise, -1)])
@pytest.mark.parametrize("long,increment", [(False, 5), (True, 1)])
def test_reversed_saved_increments_change_actual_button_target(mvl, button, direction, long, increment):
  cruise, params = helper(mvl=mvl)
  assert cruise.params is params
  assert params.reads == list(PREFERENCES)
  press(cruise, button, long=long)
  assert cruise.v_cruise_kph == cruise.v_cruise_cluster_kph == 80. + direction * increment
  assert params.values == PREFERENCES


@pytest.mark.parametrize("button,direction", [(BUTTON.accelCruise, 1), (BUTTON.decelCruise, -1)])
@pytest.mark.parametrize("long,delta", [(False, 8.), (True, 1.6)])
def test_mvl_reversed_imperial_increments_change_actual_button_target(button, direction, long, delta):
  cruise, _ = helper()
  press(cruise, button, long=long, metric=False)
  assert cruise.v_cruise_kph == cruise.v_cruise_cluster_kph == round(80. + direction * delta, 1)


@pytest.mark.parametrize("metric,base", [(True, 1.), (False, 1.6)])
def test_mvl_reloads_saved_increments_and_disabled_choice_keeps_normal_defaults(metric, base):
  cruise, params = helper()
  for long, expected in ((False, (True, 5 * base)), (True, (False, base))):
    assert cruise.update_v_cruise_delta(long, base) == expected
  params.values.update(CustomAccShortPressIncrement=10, CustomAccLongPressIncrement=5)
  cruise.read_custom_set_speed_params()
  assert cruise.update_v_cruise_delta(False, base) == (True, 10 * base)
  assert cruise.update_v_cruise_delta(True, base) == (True, 5 * base)
  params.values["CustomAccIncrementsEnabled"] = False
  cruise.read_custom_set_speed_params()
  assert cruise.update_v_cruise_delta(False, base) == (False, base)
  assert cruise.update_v_cruise_delta(True, base) == (True, 5 * base)
  assert params.reads == list(PREFERENCES) * 3
  press(cruise, BUTTON.accelCruise, metric=metric)
  assert cruise.v_cruise_kph == round(80. + base, 1)


@pytest.mark.parametrize("metric", [False, True])
@pytest.mark.parametrize("assist", [SLA.active, SLA.adapting])
@pytest.mark.parametrize("valid,last_valid", [(True, False), (False, True)])
def test_mvl_consumes_sla_plan_and_tracks_changed_limit(metric, assist, valid, last_valid):
  cruise, _ = helper()
  cruise.update_speed_limit_assist(metric, plan(63., assist, valid=valid, last_valid=last_valid))
  assert cruise.has_speed_limit and cruise.req_minus and not cruise.req_plus
  assert cruise.sla_state == assist
  assert cruise.update_speed_limit_final_last_changed
  cruise.update_v_cruise(state(), True, metric)
  assert cruise.v_cruise_kph == cruise.v_cruise_cluster_kph == quantize_set_speed(63., metric, cruise.CP)
  assert cruise.prev_sla_state == assist
  assert not cruise.update_speed_limit_final_last_changed
  # An unchanged active plan must not undo the driver's next manual increment.
  cruise.v_cruise_kph = 70.
  cruise.update_v_cruise(state(), True, metric)
  assert cruise.v_cruise_kph == 70.
  cruise.update_speed_limit_assist(metric, plan(88., assist))
  cruise.update_v_cruise(state(), True, metric)
  assert cruise.v_cruise_kph == quantize_set_speed(88., metric, cruise.CP)


@pytest.mark.parametrize("previous", [False, True])
@pytest.mark.parametrize("target,button,direction", [(60., BUTTON.decelCruise, -1), (100., BUTTON.accelCruise, 1)])
def test_mvl_sla_current_or_previous_preactive_keeps_manual_increment(previous, target, button, direction):
  cruise, _ = helper()
  cruise.update_speed_limit_assist(True, plan(target, SLA.preActive))
  if previous:
    cruise.prev_sla_state = SLA.preActive
    cruise.sla_state = SLA.disabled
  assert (cruise.req_plus, cruise.req_minus) == (direction > 0, direction < 0)
  # Release through the core handler, before the next plan advances prev_sla_state.
  cruise.button_timers[button] = 1
  cruise.button_change_states[button] = {"enabled": True, "standstill": False}
  cruise._update_v_cruise_non_pcm(state(button), True, True)
  assert cruise.v_cruise_kph == 80. + 5 * direction


@pytest.mark.parametrize("mvl", [False, True])
@pytest.mark.parametrize("fixed", [False, True])
@pytest.mark.parametrize("metric", [False, True])
@pytest.mark.parametrize("long,increment", [(False, 5), (True, 1)])
@pytest.mark.parametrize("target,button,direction", [(60., BUTTON.decelCruise, -1), (100., BUTTON.accelCruise, 1)])
def test_preactive_core_button_presses_remain_manual_with_distance_only_confirmation(mvl, fixed, metric, long, increment,
                                                                                  target, button, direction):
  cruise, _ = helper(mvl=mvl, fixed=fixed, pcm=fixed, pcm_speed=fixed)
  baseline, _ = helper(mvl=mvl, fixed=fixed, pcm=fixed, pcm_speed=fixed)
  cruise.update_speed_limit_assist(metric, plan(target, SLA.preActive))
  for item in (cruise, baseline):
    press(item, button, long=long, metric=metric)
  assert cruise.v_cruise_kph == cruise.v_cruise_cluster_kph == baseline.v_cruise_kph
  assert direction * (cruise.v_cruise_kph - 80.) > 0
  assert cruise.sla_state == SLA.preActive  # +/- is not an SLA confirmation.
  if mvl or metric:
    assert cruise.v_cruise_kph == round(80. + direction * increment * (1. if metric else 1.6), 1)
  if fixed:
    assert cruise.fixed_cruise_kph == cruise.v_cruise_kph


@pytest.mark.parametrize("guard", ["disabled", "enabled_since_press", "standstill_at_press", "standstill_at_release"])
def test_mvl_preactive_manual_increment_retains_engagement_and_standstill_guards(guard):
  cruise, _ = helper()
  cruise.update_speed_limit_assist(True, plan(100., SLA.preActive))
  down, up = state(BUTTON.accelCruise, True), state(BUTTON.accelCruise, False)
  down.cruiseState.standstill = guard == "standstill_at_press"
  up.cruiseState.standstill = guard == "standstill_at_release"
  cruise.update_v_cruise(down, guard not in ("disabled", "enabled_since_press"), True)
  cruise.update_v_cruise(up, guard != "disabled", True)
  assert cruise.v_cruise_kph == 80.


@pytest.mark.parametrize("button,target", [(BUTTON.accelCruise, 100.), (BUTTON.decelCruise, 60.)])
def test_mvl_preactive_button_press_does_not_take_native_pcm_authority(button, target):
  cruise, _ = helper(pcm=True, pcm_speed=True)
  cruise.update_speed_limit_assist(True, plan(target, SLA.preActive))
  press(cruise, button)
  cs = state()
  assert cruise.v_cruise_kph == cs.cruiseState.speed * CV.MS_TO_KPH
  assert cruise.v_cruise_cluster_kph == cs.cruiseState.speedCluster * CV.MS_TO_KPH


@pytest.mark.parametrize("assist", [SLA.disabled, SLA.preActive, SLA.pending])
def test_mvl_does_not_apply_unconfirmed_or_disabled_sla_target(assist):
  cruise, _ = helper()
  cruise.update_speed_limit_assist(True, plan(60., assist))
  cruise.update_v_cruise(state(), True, True)
  assert cruise.v_cruise_kph == 80.
  assert cruise.prev_sla_state == assist


@pytest.mark.parametrize("metric", [False, True])
@pytest.mark.parametrize("pcm_speed", [False, True])
@pytest.mark.parametrize("fixed", [False, True])
@pytest.mark.parametrize("target", [0., 200.])
def test_sla_keeps_mvl_minimum_and_fixed_pcm_ceiling(metric, pcm_speed, fixed, target):
  cruise, _ = helper(fixed=fixed, pcm_speed=pcm_speed)
  cruise.update_speed_limit_assist(metric, plan(target))
  cruise.update_v_cruise(state(), True, metric)
  minimum = 0 if fixed else 8 if pcm_speed else 30 if metric else 20
  maximum = FIXED_CRUISE_MPS * CV.MS_TO_KPH if fixed else 145
  assert cruise.v_cruise_min == minimum
  assert cruise.v_cruise_kph == (minimum if target == 0 else maximum)
  if fixed:
    assert cruise.fixed_cruise_kph == cruise.v_cruise_kph


@pytest.mark.parametrize("mvl,legacy,stock", [(True, False, False), (False, True, False), (False, False, True)])
@pytest.mark.parametrize("reported", [0., -1., 25.])
def test_sla_and_custom_preferences_do_not_take_native_pcm_speed_authority(mvl, legacy, stock, reported):
  cruise, _ = helper(mvl=mvl, legacy=legacy, stock=stock, pcm=True, pcm_speed=True)
  cruise.update_speed_limit_assist(True, plan(60.))
  cs = state(pcm_speed=reported)
  cruise.update_v_cruise(cs, True, True)
  assert not cruise.fixed_cruise_enabled
  assert cruise.v_cruise_kph == (255 if reported == 0 else -1 if reported == -1 else reported * CV.MS_TO_KPH)
  assert cruise.v_cruise_cluster_kph == (cruise.v_cruise_kph if reported <= 0 else cs.cruiseState.speedCluster * CV.MS_TO_KPH)


@pytest.mark.parametrize("metric,minimum", [(True, 40.), (False, 25 * CV.MPH_TO_KPH)])
def test_factory_acc_icbm_minimum_is_unchanged(metric, minimum):
  cruise, _ = helper(mvl=False, stock=True, pcm=True)
  cruise.update_speed_limit_assist(metric, plan(0.))
  cruise.update_v_cruise(state(), True, metric)
  assert not cruise.mvl_enabled and not cruise.fixed_cruise_enabled
  assert cruise.v_cruise_min == cruise.v_cruise_kph == minimum
