"""Pinned-donor cruise helper parity, button safety and isolated settings.

No device I/O. Source fixtures are blob-verified by test_mvl_host_parity.
Low-speed SET (<40 kph), including standstill, restores donor's fixed floor40.
Native PCM-owned targets/sentinels and engagement guards are never overridden.
"""
import ast
import math
from enum import IntEnum
from types import SimpleNamespace as NS

import numpy as np
import pytest

from openpilot.common.constants import CV
from openpilot.nrdr.tests.test_mvl_host_parity import DONOR, LEGACY, definitions, git_source, source

CORE = "openpilot/selfdrive/car/cruise.py"
EXT = "openpilot/sunnypilot/selfdrive/car/cruise_ext.py"
HELPERS = "openpilot/sunnypilot/selfdrive/car/cruise_helpers.py"
MVL_FLAG = 131072


def load_policy(namespace):
  """Execute the real policy expression; replace only the unavailable DBC import."""
  class NoEnumImport(ast.NodeTransformer):
    def visit_ImportFrom(self, node):
      assert node.module == "opendbc.car.honda.values"
      return None

  tree = NoEnumImport().visit(ast.parse(source("openpilot/nrdr/features/longitudinal/policy.py")))
  namespace["HondaFlags"] = NS(MVL_LONGITUDINAL=MVL_FLAG)
  exec(compile(ast.fix_missing_locations(tree), "<real MVL gate, injected enum>", "exec"), namespace)
  return namespace


class Button(IntEnum):
  accelCruise = 1
  decelCruise = 2
  setCruise = 3
  resumeCruise = 4
  cancel = 5
  mainCruise = 6
  gapAdjustCruise = 7

  @property
  def raw(self):
    return int(self)


SLA = NS(disabled=0, preActive=1, active=2, adapting=3)
DEFAULTS = {"CustomAccIncrementsEnabled": False, "CustomAccShortPressIncrement": 1, "CustomAccLongPressIncrement": 5}
POLLUTED = DEFAULTS | {"CustomAccIncrementsEnabled": True, "CustomAccShortPressIncrement": 10,
                      "CustomAccLongPressIncrement": 10, "NrdrCruiseButtonSubMode": True, "NrdrHudSubModeUntil": 0,
                      "NrdrCruiseButtonSubModeSecs": 60, "InitialCruiseSpeedKph": 140, "HondaLiveLearningGas": False}


class Params:
  def __init__(self, values):
    self.values = values.copy()
    self.calls = []

  def get(self, key, **_):
    self.calls.append(("get", key))
    return self.values.get(key)

  def get_bool(self, key):
    return bool(self.get(key))

  def put(self, key, value, **_):
    self.calls.append(("put", key))
    self.values[key] = value

  put_bool = put


def forbidden(*_args, **_kwargs):
  raise AssertionError("MVL touched custom cruise settings/HUD/SLA")


def namespace(values=None):
  params = Params(DEFAULTS if values is None else values)
  env = {
    "np": np, "math": math, "CV": CV, "Params": lambda: params,
    "car": NS(CarState=NS(ButtonEvent=NS(Type=Button)), CarParams=object),
    "structs": NS(CarParams=object, CarParamsSP=object),
    "custom": NS(LongitudinalPlanSP=NS(SpeedLimit=NS(AssistState=SLA)), OnroadEventSP=NS(EventName=NS(experimentalModeSwitched=1))),
    "get_minimum_set_speed": lambda metric: 30 if metric else 20, "SLA_ACTIVE_STATES": (2, 3),
    "compare_cluster_target": lambda *_: (False, False), "quantize_set_speed": lambda speed, *_: round(speed, 1),
    "consume_button_press": lambda _: True,
  }
  load_policy(env)
  return env, params


def module(revision=None, values=None, *, forbid_nrdr=False):
  env, params = namespace(values)
  text = source if revision is None else lambda path: git_source(path, revision)
  ext = definitions(text(EXT), env)
  env["VCruiseHelperSP"] = ext["VCruiseHelperSP"]
  nrdr = definitions(source("openpilot/nrdr/features/driver_policy/cruise.py"), env)["NrdrCruise"]
  env["NrdrCruise"] = forbidden if forbid_nrdr else nrdr
  return definitions(text(CORE), env), params


def cp(*, mvl=True, pcm=False, brand="honda", openlong=True):
  return NS(flags=MVL_FLAG if mvl else 0, brand=brand, pcmCruise=pcm, openpilotLongitudinalControl=openlong)


def state(speed=20., *, button=None, pressed=False, available=True, standstill=False, gas=False, pcm_speed=25.):
  return NS(vEgo=speed, gasPressed=gas,
            buttonEvents=[] if button is None else [NS(type=button, pressed=pressed)],
            cruiseState=NS(available=available, standstill=standstill, speed=pcm_speed, speedCluster=pcm_speed + .2))


@pytest.mark.parametrize("pcm_speed", [False, True])
@pytest.mark.parametrize("pcm", [False, True])
@pytest.mark.parametrize("metric", [False, True])
def test_entire_button_update_matches_donor_defaults_with_polluted_settings(pcm_speed, pcm, metric):
  current, params = module(values=POLLUTED, forbid_nrdr=True)
  donor, _ = module(DONOR)
  car_params, car_sp = cp(pcm=pcm), NS(pcmCruiseSpeed=pcm_speed)
  actual, expected = (m["VCruiseHelper"](car_params, car_sp) for m in (current, donor))
  assert actual.nrdr is None and actual.params is None
  for helper in (actual, expected):
    helper.v_cruise_kph = helper.v_cruise_cluster_kph = 70.
  # Even old in-memory settings/SLA targets cannot leak into the mode.
  actual.custom_acc_enabled, actual.short_increment, actual.long_increment = True, 10, 10
  actual.sla_state, actual.prev_sla_state = SLA.active, SLA.preActive
  actual.has_speed_limit, actual.speed_limit_final_last_kph = True, 169.
  actual.req_plus = actual.req_minus = True
  for frame in range(420):
    button = Button.accelCruise if frame < 210 else Button.decelCruise
    event = frame % 210 in (5, 8, 20, 75, 100, 160)
    pressed = frame % 210 in (5, 20, 100)
    cs = state(button=button if event else None, pressed=pressed, gas=frame % 31 == 0,
               standstill=110 < frame % 210 < 135, available=frame % 80 != 0)
    actual.read_custom_set_speed_params()
    actual.update_speed_limit_assist(metric, object())  # no access to sidecar fields
    for helper in (actual, expected):
      helper.update_v_cruise(cs, frame % 200 > 2, metric)
    for key in ("v_cruise_kph", "v_cruise_cluster_kph", "v_cruise_kph_last", "v_cruise_min", "enabled_prev"):
      assert getattr(actual, key) == getattr(expected, key), (frame, key)
    assert actual.button_timers == expected.button_timers
    assert actual.button_change_states == expected.button_change_states
  assert not params.calls


@pytest.mark.parametrize("metric", [False, True])
def test_button_targets_never_exceed_donor_maximum(metric):
  current, _ = module(forbid_nrdr=True)
  helper = current["VCruiseHelper"](cp(), NS(pcmCruiseSpeed=True))
  helper.v_cruise_kph = helper.v_cruise_cluster_kph = 144.
  for frame in range(600):
    helper.update_v_cruise(state(button=Button.accelCruise if frame == 0 else None, pressed=True), True, metric)
    assert helper.v_cruise_kph <= 145
  assert helper.v_cruise_kph == 145
  assert current["V_CRUISE_MAX"] == 169


@pytest.mark.parametrize("pcm_speed", [False, True])
@pytest.mark.parametrize("metric", [False, True])
def test_standstill_set_then_decrement_uses_exact_donor_sp_minimum(pcm_speed, metric):
  current, _ = module(forbid_nrdr=True)
  donor, _ = module(DONOR)
  actual, expected = (m["VCruiseHelper"](cp(), NS(pcmCruiseSpeed=pcm_speed)) for m in (current, donor))
  actual.initialize_v_cruise(state(0.), True)
  expected.initialize_v_cruise(state(0.), 40)
  assert actual.v_cruise_kph == expected.v_cruise_kph == 40
  for frame in range(700):
    cs = state(0., button=Button.decelCruise if frame == 3 else None, pressed=True, standstill=True)
    for helper in (actual, expected):
      helper.update_v_cruise(cs, True, metric)
    assert actual.v_cruise_kph == expected.v_cruise_kph
    assert actual.button_timers == expected.button_timers
  assert actual.v_cruise_kph == (8 if pcm_speed else 30 if metric else 20)


@pytest.mark.parametrize("speed", [40., 40.4, 72., 100.7, 145., 160.])
@pytest.mark.parametrize("experimental", [False, True])
def test_initialization_at_or_above_40_matches_donor_default(speed, experimental):
  current, _ = module(forbid_nrdr=True)
  donor, _ = module(DONOR)
  helpers = [m["VCruiseHelper"](cp(), NS(pcmCruiseSpeed=True)) for m in (current, donor)]
  cs = state(speed / 3.6, button=Button.decelCruise)
  helpers[0].initialize_v_cruise(cs, experimental)
  helpers[1].initialize_v_cruise(cs, 40)
  assert helpers[0].v_cruise_kph == helpers[1].v_cruise_kph
  assert helpers[0].v_cruise_cluster_kph == helpers[1].v_cruise_cluster_kph


@pytest.mark.parametrize("speed", [0., 1., 8., 15., 25., 39.])
@pytest.mark.parametrize("caller_argument", [False, True, 40, 140])
def test_low_speed_set_restores_donor_40_floor_ignoring_host_boolean_or_saved_target(speed, caller_argument):
  current, _ = module(forbid_nrdr=True)
  helper = current["VCruiseHelper"](cp(), NS(pcmCruiseSpeed=True))
  helper.initialize_v_cruise(state(speed / 3.6, button=Button.decelCruise), caller_argument)
  assert helper.v_cruise_kph == 40
  assert helper.v_cruise_cluster_kph == helper.v_cruise_kph


@pytest.mark.parametrize("last", [8., 30., 100., 145.])
def test_resume_restores_only_initialized_speed(last):
  current, _ = module(forbid_nrdr=True)
  helper = current["VCruiseHelper"](cp(), NS(pcmCruiseSpeed=True))
  helper.v_cruise_kph, helper.v_cruise_kph_last = last, last
  helper.initialize_v_cruise(state(0., button=Button.resumeCruise), True)
  assert helper.v_cruise_kph == last
  fresh = current["VCruiseHelper"](cp(), NS(pcmCruiseSpeed=True))
  fresh.v_cruise_kph_last = 120.
  fresh.initialize_v_cruise(state(0., button=Button.resumeCruise), True)
  assert fresh.v_cruise_kph == 40.


@pytest.mark.parametrize("speed", [-1., 0., 25., 44.5])
def test_native_pcm_ownership_and_sentinels_match_donor(speed):
  modules = [module(forbid_nrdr=True)[0], module(DONOR)[0]]
  helpers = [m["VCruiseHelper"](cp(pcm=True), NS(pcmCruiseSpeed=True)) for m in modules]
  for helper in helpers:
    helper.update_v_cruise(state(pcm_speed=speed), True, True)
    previous = (helper.v_cruise_kph, helper.v_cruise_cluster_kph)
    helper.initialize_v_cruise(state(0.), False)
    assert (helper.v_cruise_kph, helper.v_cruise_cluster_kph) == previous
  assert helpers[0].v_cruise_kph == helpers[1].v_cruise_kph
  assert helpers[0].v_cruise_cluster_kph == helpers[1].v_cruise_cluster_kph


@pytest.mark.parametrize("brand,openlong,mvl", [("toyota", True, True), ("honda", True, False), ("honda", False, True)])
@pytest.mark.parametrize("metric", [False, True])
def test_non_mvl_matches_pre_change_helper(brand, openlong, mvl, metric):
  modules = [module(values=POLLUTED)[0], module(LEGACY, values=POLLUTED)[0]]
  helpers = [m["VCruiseHelper"](cp(brand=brand, openlong=openlong, mvl=mvl), NS(pcmCruiseSpeed=True)) for m in modules]
  for helper in helpers:
    helper.initialize_v_cruise(state(7.3, button=Button.decelCruise), True)
  for frame in range(130):
    cs = state(button=Button.accelCruise if frame in (0, 100) else None, pressed=frame == 0)
    for helper in helpers:
      helper.update_v_cruise(cs, True, metric)
    assert helpers[0].v_cruise_kph == helpers[1].v_cruise_kph
    assert helpers[0].v_cruise_cluster_kph == helpers[1].v_cruise_cluster_kph


def test_pinned_caller_and_defaults_explain_boolean_adapter():
  donor_card = git_source("openpilot/selfdrive/car/card.py")
  host_card = source("openpilot/selfdrive/car/card.py")
  assert "initialize_v_cruise(self.CS_prev, self.initial_cruise_speed)" in donor_card
  assert "initialize_v_cruise(self.CS_prev, self.experimental_mode)" in host_card
  keys = git_source("openpilot/common/params_keys.h")
  for text in ('{"InitialCruiseSpeedKph", {PERSISTENT, INT, "40"}}',
               '{"CustomAccIncrementsEnabled", {PERSISTENT | BACKUP, BOOL, "0"}}'):
    assert text in keys
  minimum = git_source("openpilot/sunnypilot/selfdrive/car/intelligent_cruise_button_management/helpers.py")
  assert "return 30 if is_metric else 20" in minimum


@pytest.mark.parametrize("mvl", [False, True])
@pytest.mark.parametrize("saved_mvl", [False, True])
def test_experimental_wheel_hold_obeys_startup_flag_not_saved_choice(mvl, saved_mvl):
  env, params = namespace(POLLUTED | {"HondaLiveLearningGas": saved_mvl, "ExperimentalMode": False})
  cls = definitions(source(HELPERS), env)["CruiseHelper"]
  helper = cls(cp(mvl=mvl))
  events = []
  for frame in range(150):
    helper.update(state(button=Button.gapAdjustCruise if frame == 0 else None, pressed=True),
                  NS(add=events.append), False)
  assert params.values["ExperimentalMode"] is (not mvl)
  assert helper.experimental_mode_switched is (not mvl)
  assert events == ([] if mvl else [1])
