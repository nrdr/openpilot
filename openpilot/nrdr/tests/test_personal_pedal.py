"""Offline controller math, mode isolation and shared selector contracts."""
import ast
import base64
from collections import deque
from dataclasses import MISSING, fields, replace
import math
import gzip
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace as NS

import numpy as np
import pytest

from opendbc.car.honda.values import CAR, HondaFlags, HONDA_BOSCH_A
from openpilot.common.pid import PIDController
from openpilot.nrdr.params.generated.keys import NrdrParamKey
from openpilot.nrdr.params.longitudinal_controller import CONTROLLER_KEY, decode_controller, saved_controller
from openpilot.nrdr.tests.test_honda_pcm_ui import Params, Widget, state, native_layout
from openpilot.nrdr.tests.test_mvl_host_parity import STATE, definitions, environment
from openpilot.nrdr.tests.test_mvl_settings import rpc as rpc, encoded
from openpilot.nrdr.tests.test_sunnylink_model_catalog import load_function, ParamType
from openpilot.nrdr.ui.honda_pcm import longitudinal_controller_choices, save_longitudinal_controller, store_controller_choice
from openpilot.sunnypilot.sunnylink.tools.compile_settings_ui import compile_schema, DEFAULT_SRC


ROOT = Path(__file__).resolve().parents[3]
CORE = "openpilot/nrdr/features/longitudinal/"


def controller_modules():
  live = NS(snapshot=NS(generation=0), generation=0)
  env = dict(np=np, math=math, deque=deque, DT_CTRL=.01, DT_MDL=.05, HondaFlags=HondaFlags,
             car=NS(CarControl=NS(Actuators=NS(LongControlState=STATE))), PIDController=PIDController,
             NrdrParamKey=NrdrParamKey, get_live_params=lambda: live,
             read_bool=lambda snap, key, default: default,
             read_float=lambda snap, key, default, *args, **kw: default,
             LongTune=lambda: NS(stopping={"l2_enable": 0}, refresh=lambda: None))
  normal = definitions((ROOT / CORE / "longcontrol.py").read_text(), env)
  personal = definitions((ROOT / CORE / "personal_pedal.py").read_text(), normal)
  return normal, personal


def cp(flag=True):
  return NS(brand="honda", carFingerprint=CAR.HONDA_CLARITY, openpilotLongitudinalControl=True,
            flags=HondaFlags.NIDEC | (HondaFlags.PERSONAL_PEDAL if flag else 0),
            stopAccel=-2., longitudinalTuning=NS(deprecated=NS(kpBP=[0.], kpV=[0.]), kiBP=[0.], kiV=[.3]),
            deprecated=NS(stoppingDecelRate=.3, vEgoStarting=.5, vEgoStopping=.5, startingState=False, startAccel=1.))


@pytest.mark.parametrize("index,kp,ki", [
  (0, (3.6, 2.4, 1.5), (.54, .36)), (1, (2.4, 1.6, 1.), (.36, .24)),
  (2, (1.2, .8, .5), (.18, .12)), (3, (.6, .4, .25), (.09, .06)),
])
@pytest.mark.parametrize("speed", [0., 2.5, 5., 9., 20., 35., 45.])
def test_exact_historical_gains_and_speed_feedback(index, kp, ki, speed):
  _, module = controller_modules()
  ctl = module["PersonalPedalControl"](cp(), NS(enableGasInterceptor=True))
  ctl._update_pid_scale(index, False)
  ctl.set_plan(NS(speeds=[speed + .2, 99.], aTarget=.4), True)
  cs = NS(vEgo=speed, aEgo=-8.)  # Acceleration error must not enter this PI.
  expected_p = np.interp(speed, [0., 5., 35.], kp) * .2
  expected_i = np.interp(speed, [0., 35.], ki) * .2 * .01
  assert ctl._pid_accel(cs, .4) == pytest.approx(.4 + expected_p + expected_i)
  assert ctl.pid.p == pytest.approx(expected_p)
  assert ctl.pid.i == pytest.approx(expected_i)
  assert ctl.pid.f == .4


def test_feedback_integrates_speed_error_not_acceleration_error():
  _, module = controller_modules()
  ctl = module["PersonalPedalControl"](cp(), NS(enableGasInterceptor=True))
  ctl._update_pid_scale(2, False)
  ctl.set_plan(NS(speeds=[20.2], aTarget=0.), True)
  for _ in range(100):
    ctl._pid_accel(NS(vEgo=20., aEgo=0.), 0.)
  assert ctl.pid.i == pytest.approx(np.interp(20., [0., 35.], [.18, .12]) * .2)
  ctl.reset()
  assert ctl.pid.i == 0.


def test_reference_follows_final_arbitration_not_future_mpc_or_dashboard():
  _, module = controller_modules()
  plan = NS(speeds=[20., 40., 60.], aTarget=-2.)
  assert module["speed_reference"](plan, .04) == pytest.approx(19.92)
  assert module["speed_reference"](plan, 10.) == pytest.approx(19.9)
  assert module["speed_reference"](NS(speeds=[.01], aTarget=-2.), .05) == 0.
  for speeds in ([], [math.nan], [math.inf]):
    assert module["speed_reference"](NS(speeds=speeds, aTarget=0.), .01) is None


@pytest.mark.parametrize("active,stop,expected", [(False, False, STATE.off), (True, True, STATE.stopping),
                                                 (True, False, STATE.pid)])
def test_states_limits_and_saved_standard_scales(active, stop, expected):
  _, module = controller_modules()
  ctl = module["PersonalPedalControl"](cp(), NS(enableGasInterceptor=True))
  ctl.pid_scales = (5., 5., 5., 5.)
  ctl.static_feedforward = False
  ctl.roen_acceleration_limits = True
  ctl.set_plan(NS(speeds=[30.], aTarget=.5), True)
  cs = NS(vEgo=10., aEgo=0., brakePressed=False, cruiseState=NS(standstill=False))
  out = ctl.update(active, cs, .5, stop, (-3.5, 1.5), personality=3)
  assert ctl.long_control_state == expected
  assert -3.5 <= out <= 1.5
  if not active:
    assert out == 0.
  if stop:
    assert out < 0. and ctl.pid.i == 0.
  assert ctl.pid_scale == 1.
  assert ctl._accel_limits((-3.5, 1.5), 0.) == (-3.5, 1.5)


@pytest.mark.parametrize("brand,nidec,pedal,longitudinal,selected,mvl", [
  ("honda", True, True, True, True, False), ("honda", True, True, True, False, False),
  ("honda", True, False, True, True, False), ("honda", False, True, True, True, False),
  ("honda", True, True, False, True, False), ("toyota", True, True, True, True, False),
  ("honda", True, True, True, True, True),
])
def test_runtime_admission(brand, nidec, pedal, longitudinal, selected, mvl):
  _, module = controller_modules()
  flags = (HondaFlags.NIDEC if nidec else 0) | (HondaFlags.PERSONAL_PEDAL if selected else 0) | (HondaFlags.MVL_LONGITUDINAL if mvl else 0)
  car_params = NS(brand=brand, flags=flags, openpilotLongitudinalControl=longitudinal)
  assert module["personal_pedal_enabled"](car_params, NS(enableGasInterceptor=pedal)) is bool(
    brand == "honda" and nidec and pedal and longitudinal and selected and not mvl)


@pytest.mark.parametrize("profile", range(4))
def test_standard_controller_is_identical_to_parent(profile):
  normal, personal = controller_modules()
  env = environment(NrdrLongControl=normal["NrdrLongControl"], **{
    name: personal[name] for name in ("PersonalPedalControl", "personal_pedal_enabled")})
  path = "openpilot/selfdrive/controls/lib/longcontrol.py"
  parent = subprocess.check_output(["git", "show", f"3fe02ea468:{path}"], cwd=ROOT, text=True)
  old = definitions(parent, env)["LongControl"](cp(False), NS(enableGasInterceptor=True))
  new = definitions((ROOT / path).read_text(), env)["LongControl"](cp(False), NS(enableGasInterceptor=True))
  for i in range(500):
    cs = NS(vEgo=15. + math.sin(i / 100), aEgo=.3 * math.sin(i / 30), brakePressed=False, cruiseState=NS(standstill=False))
    args = (i > 5, cs, math.sin(i / 50), i > 450, (-3.5, 2.))
    new.set_plan(NS(speeds=[100.], aTarget=10.), i % 5 == 0)
    assert new.update(*args, personality=profile) == old.update(*args, personality=profile)
    assert (new.pid.p, new.pid.i, new.pid.f) == (old.pid.p, old.pid.i, old.pid.f)


@pytest.mark.parametrize("mvl,radar,expected", [(False, False, 0), (False, True, 2), (True, False, 1), (True, True, 1)])
def test_legacy_selection_is_read_only(mvl, radar, expected):
  params = Params(HondaLiveLearningGas=mvl, HondaBoschARadar=radar)
  assert saved_controller(params, bosch_radar_available=True) == expected
  assert params.writes == []
  assert decode_controller(-1) is None


def test_selector_supports_all_nidec_pedals_and_bosch_radar_without_duplication():
  for car in (CAR.HONDA_CIVIC, CAR.HONDA_CLARITY, CAR.ACURA_ILX):
    ui = state(carFingerprint=car, enableGasInterceptor=True)
    assert longitudinal_controller_choices(ui.CP, ui.CP_SP, ui.params) == (0, 1, 3)
  ui = state(carFingerprint=next(iter(HONDA_BOSCH_A)), enableGasInterceptor=False)
  assert longitudinal_controller_choices(ui.CP, ui.CP_SP, ui.params) == (0, 1, 2)
  ui = state(enableGasInterceptor=False)
  assert longitudinal_controller_choices(ui.CP, ui.CP_SP, ui.params) == (0, 1)
  schema = compile_schema(DEFAULT_SRC)
  items = []
  def walk(value):
    if isinstance(value, dict):
      if "key" in value and "widget" in value:
        items.append(value)
      for child in value.values():
        walk(child)
    elif isinstance(value, list):
      for child in value:
        walk(child)
  walk(schema)
  selector = [x for x in items if x["key"] == CONTROLLER_KEY]
  assert len(selector) == 1
  assert [x["value"] for x in selector[0]["options"]] == [0, 1, 2, 3]
  assert not [x for x in items if x["key"] in ("HondaLiveLearningGas", "HondaBoschARadar")]
  layout = native_layout(state(enableGasInterceptor=True))
  assert layout._tuning_items[0] is layout._longitudinal_controller
  assert not hasattr(layout, "_radar_tryout")


def test_explicit_selection_only_resets_on_entering_personal_and_preserves_tuning(monkeypatch):
  requests = []
  monkeypatch.setitem(sys.modules, "openpilot.nrdr.car.live_gas_reset", NS(request_reset=lambda p, cp: requests.append(cp)))
  ui = state(enableGasInterceptor=True)
  ui.params.values.update(IsOffroad=True, HondaLiveLearningGas=True, HondaGasFactorParams="1.4",
                          LongPidTuneScaleEcon=175, StaticFeedforwardLong=False, ModelManager_ActiveBundle="Cheddar")
  assert save_longitudinal_controller(ui, 3)
  assert len(requests) == 1 and ui.params.get(CONTROLLER_KEY) == 3
  assert ui.params.get_bool("HondaLiveLearningGas") is False
  assert save_longitudinal_controller(ui, 3) and len(requests) == 1
  assert ui.params.get("HondaGasFactorParams") == "1.4"  # queued reset, not an uncontrolled UI deletion
  assert ui.params.get("LongPidTuneScaleEcon") == 175
  assert ui.params.get("StaticFeedforwardLong") is False
  assert ui.params.get("ModelManager_ActiveBundle") == "Cheddar"
  assert save_longitudinal_controller(ui, 1) and len(requests) == 1
  ui.params.values["IsOffroad"] = False
  before = list(ui.params.writes)
  assert not save_longitudinal_controller(ui, 3)
  assert ui.params.writes == before


def test_bosch_selector_uses_existing_radar_setting():
  params = Params(IsOffroad=True, HondaLiveLearningGas=True, HondaBoschARadar=False)
  assert store_controller_choice(params, 2, (0, 1, 2))
  assert params.get_bool("HondaBoschARadar") and not params.get_bool("HondaLiveLearningGas")
  assert store_controller_choice(params, 1, (0, 1, 2))
  assert params.get_bool("HondaBoschARadar") and params.get_bool("HondaLiveLearningGas")
  assert store_controller_choice(params, 0, (0, 1, 2))
  assert not params.get_bool("HondaBoschARadar")
  assert not store_controller_choice(params, 3, (0, 1, 2))


def test_personal_actuator_uses_neutral_factors_and_disables_learning():
  path = ROOT / "opendbc_repo/opendbc/sunnypilot/car/honda/controller_features.py"
  class Learner:
    def __init__(self, gas, wind, car, alpha):
      self.gasfactor, self.windfactor, self.gasalpha = gas, wind, alpha
  from opendbc.sunnypilot.car.runtime_config import HondaLiveTuning
  env = dict(HondaFlags=HondaFlags, HondaFlagsSP=NS(STOCK_LONGITUDINAL=1),
             HondaCarConfig=object, HondaLiveTuning=HondaLiveTuning, LongGasLearner=Learner,
             replace=replace, math=math)
  cls = definitions(path.read_text(), env)["HondaControllerFeatures"]
  live = HondaLiveTuning(**{field.name: 0 for field in fields(HondaLiveTuning) if field.default is MISSING})
  provider = NS(initialize_live_learning_gas=lambda _: None, get_live_tuning=lambda: live)
  obj = cls(cp(), NS(enableGasInterceptor=True, flags=0), NS(provider=provider))
  assert obj.longitudinal_factors == (1., 1.) and obj.gas_alpha == 0.
  assert not obj.live_tuning().live_learning_gas and not obj.live_tuning().roen_acceleration_limits


@pytest.mark.parametrize("pedal,stock,nidec,selected", [(True, False, True, True), (False, False, True, True),
                                                       (True, True, True, True), (True, False, False, True),
                                                       (True, False, True, False)])
def test_startup_flag_is_hardware_qualified_without_extra_safety_authority(pedal, stock, nidec, selected):
  from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP, HondaSafetyFlagsSP
  from opendbc.car.honda.values import HondaSafetyFlags
  path = ROOT / "opendbc_repo/opendbc/sunnypilot/car/interfaces.py"
  node = next(n for n in ast.parse(path.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == "_initialize_honda")
  env = dict(HondaFlags=HondaFlags, HondaFlagsSP=HondaFlagsSP, HondaSafetyFlagsSP=HondaSafetyFlagsSP,
             HondaSafetyFlags=HondaSafetyFlags, structs=NS(CarParams=object, CarParamsSP=object), HondaCarConfig=object)
  exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), "exec"), env)
  params = cp(False)
  params.flags = HondaFlags.NIDEC if nidec else HondaFlags.BOSCH
  params.safetyConfigs = [NS(safetyParam=0)]
  sp = NS(enableGasInterceptor=pedal, flags=0, safetyParam=0)
  config = NS(personal_pedal=selected, enforce_stock_longitudinal=stock, clarity_interceptor_brake_bench=False)
  env["_initialize_honda"](params, sp, config)
  assert bool(params.flags & HondaFlags.PERSONAL_PEDAL) is (pedal and not stock and nidec and selected)
  if not stock:
    assert params.safetyConfigs[0].safetyParam == sp.safetyParam == 0


@pytest.mark.parametrize("compressed", [False, True])
@pytest.mark.parametrize("legacy,selected,expected", [(True, -1, 1), (False, -1, 0), (False, 3, 3)])
def test_remote_read_resolves_legacy_without_migration(compressed, legacy, selected, expected):
  params = Params(HondaLiveLearningGas=legacy, NrdrLongitudinalController=selected)
  params.all_keys = lambda: [CONTROLLER_KEY.encode()]
  params.get_type = lambda _: ParamType.INT
  read = load_function("openpilot/sunnypilot/sunnylink/athena/sunnylinkd.py", "getParams", {
    "Params": lambda: params, "ParamKeyType": ParamType, "json": json, "gzip": gzip, "base64": base64,
    "_vehicle_tuning_capabilities": lambda: {}, "get_param_as_byte": lambda key: str(params.get(key)).encode(),
  })
  value = base64.b64decode(read([CONTROLLER_KEY], compressed)[CONTROLLER_KEY])
  assert int(gzip.decompress(value) if compressed else value) == expected
  assert params.writes == []


@pytest.mark.parametrize("compressed", [False, True])
def test_remote_controller_writes_and_rejections(rpc, monkeypatch, compressed):
  save, params, caps = rpc
  reset_requests = []
  monkeypatch.setitem(sys.modules, "openpilot.nrdr.car.live_gas_reset", NS(
    REQUEST="NrdrResetLiveGas", request_reset=lambda p, cp: reset_requests.append(cp), stored_cp=lambda p: None))
  caps["nrdr_personal_pedal_available"] = True
  params.values.update(ModelManager_ActiveBundle="Cheddar", LongPidTuneScaleEcon=175)
  save({CONTROLLER_KEY: encoded(3, compressed)}, compressed)
  assert params.get(CONTROLLER_KEY) == 3 and not params.get_bool("HondaLiveLearningGas")
  assert len(reset_requests) == 1
  save({CONTROLLER_KEY: encoded(1, compressed)}, compressed)
  assert params.get_bool("HondaLiveLearningGas")
  assert params.get("LongPidTuneScaleEcon") == 175 and params.get("ModelManager_ActiveBundle") == "Cheddar"
  for update in ({CONTROLLER_KEY: encoded(2, compressed)}, {CONTROLLER_KEY: encoded(9, compressed)},
                 {CONTROLLER_KEY: encoded(0, compressed), "HondaLiveLearningGas": encoded(0, compressed)}):
    before = list(params.writes)
    with pytest.raises(ValueError):
      save(update, compressed)
    assert params.writes == before
  params.values["IsOffroad"] = False
  with pytest.raises(ValueError):
    save({CONTROLLER_KEY: encoded(3, compressed)}, compressed)


@pytest.mark.parametrize("roen", [False, True])
def test_pedal_output_unchanged_without_selection_and_historical_scale_when_selected(roen):
  path = "opendbc/sunnypilot/car/honda/gas_interceptor.py"
  source = ROOT / "opendbc_repo" / path
  old = subprocess.check_output(["git", "show", f"ff99a28e5:{path}"], cwd=ROOT / "opendbc_repo", text=True)
  env = dict(np=np, HondaFlags=HondaFlags, structs=NS(CarParams=object, CarParamsSP=object, CarControl=object, CarState=object),
             CanData=object, create_gas_interceptor_command=lambda *args: args)
  old_class = definitions(old, env)["GasInterceptorCarController"]
  new_class = definitions(source.read_text(), env)["GasInterceptorCarController"]
  for flag in (False, True):
    old_ctl = old_class(cp(False), NS(enableGasInterceptor=True))
    new_ctl = new_class(cp(flag), NS(enableGasInterceptor=True))
    for frame in range(150):
      cs = NS(out=NS(vEgo=frame / 5))
      cc = NS(longActive=frame > 10)
      args = (cc, cs, .2, 0., 0., None, frame, roen)
      # Use the same CAN packing stub: compare signal values, not fake physical motion.
      old_result = old_ctl.update(*args)
      new_result = new_ctl.update(*args)
      if not flag:
        assert new_result == old_result and new_ctl.gas == old_ctl.gas
      elif cc.longActive and frame % 2 == 0:
        assert new_ctl.gas <= np.interp(cs.out.vEgo, [0., 10.], [.4, 1.]) * .2 + 1e-12


@pytest.mark.parametrize("onroad_at_click", [False, True])
def test_c4_selector_uses_shared_choices_and_rechecks_selection(onroad_at_click, monkeypatch):
  from openpilot.nrdr.ui import honda_pcm
  from openpilot.nrdr.params.longitudinal_controller import BOSCH_RADAR_WARNING
  ui = state(enableGasInterceptor=True)
  ui.params.values["HondaLiveLearningGas"] = True
  panels, buttons, resets = [], [], []
  monkeypatch.setitem(sys.modules, "openpilot.nrdr.car.live_gas_reset", NS(request_reset=lambda p, cp: resets.append(cp)))
  path = "openpilot/nrdr/ui/settings/pcm_modes_mici.py"
  node = next(n for n in ast.parse((ROOT / path).read_text()).body if isinstance(n, ast.ClassDef)
              and n.name == "LongitudinalControllerControl")
  env = dict(vars(honda_pcm), BigButton=Widget, ui_state=ui, tr=lambda s: s, BOSCH_RADAR_WARNING=BOSCH_RADAR_WARNING,
             NavScroller=lambda: NS(_scroller=NS(add_widgets=buttons.extend)),
             gui_app=NS(push_widget=panels.append, pop_widget=lambda: panels.pop()))
  exec(compile(ast.Module(body=[node], type_ignores=[]), path, "exec"), env)
  ctl = env["LongitudinalControllerControl"]()
  assert ctl.value == "MVL Live Learning Gas"
  ctl.click_callback()
  assert [button.text for button in buttons] == ["Standard", "MVL Live Learning Gas", "Aragon's Personal Pedal"]
  ui.params.values["IsOffroad"] = not onroad_at_click
  buttons[-1].click_callback()
  if onroad_at_click:
    assert not ui.params.writes and not resets
  else:
    assert ctl.value == "Aragon's Personal Pedal" and ui.params.get(CONTROLLER_KEY) == 3
    assert len(resets) == 1 and not panels
