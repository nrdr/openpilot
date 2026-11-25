"""Opt-in PTM Testing admission, baseline parity and independent controller state."""
import ast
import math
from pathlib import Path
import sys
import time
from types import SimpleNamespace as NS

import pytest

from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP, PTM_EPS_REVISIONS
from openpilot.nrdr.features.lateral.controller_selection import (
  _PROFILES, firmware_controller_selected, firmware_controller_testing_selected, firmware_controller_profile_for_model,
)
from openpilot.nrdr.tests.test_rdx_route_a import rdx, simulate_receipt


@pytest.fixture(params=list(_PROFILES))
def admitted_car(request, monkeypatch):
  fingerprint, firmware = request.param
  if fingerprint.startswith("ACURA_RDX"):
    cp = rdx(fingerprint)
    simulate_receipt(monkeypatch, cp)
  else:
    cp = NS(brand="honda", carFingerprint=fingerprint, steerRatio=16.5, wheelbase=2.75, steerLimitTimer=.8,
            lateralTuning=NS(which=lambda: "pid"),
            carFw=[NS(ecu="eps", fwVersion=PTM_EPS_REVISIONS.get(fingerprint, firmware.encode()))])
  return cp, NS(flags=HondaFlagsSP.EPS_MODIFIED.value)


def test_testing_is_explicit_and_shares_exact_admission(admitted_car):
  cp, sp = admitted_car
  for value in (None, 0, "0", b"0", 1, "1", b"1", 2, "2", b"2", 3, "invalid"):
    params = {"NrdrLateralController": value}
    assert firmware_controller_selected(params, cp, sp) == (value in (1, "1", b"1", 2, "2", b"2"))
    assert firmware_controller_testing_selected(params, cp, sp) == (value in (2, "2", b"2"))
    assert not firmware_controller_selected(params, cp, NS(flags=0))
    assert not firmware_controller_testing_selected(params, cp, NS(flags=0))
  cp.carFw = []
  assert not firmware_controller_testing_selected({"NrdrLateralController": 2}, cp, sp)


def test_non_honda_testing_selection_does_not_wait_for_carparams():
  class NoReads:
    def get(self, *args, **kwargs):
      pytest.fail("unsupported car must not read or wait for Honda settings")
  assert firmware_controller_profile_for_model(NoReads(), NS(brand="toyota")) is None


@pytest.mark.skipif(sys.platform == "win32", reason="native controller dependencies")
def test_native_testing_is_identical_but_has_separate_state(admitted_car):
  from openpilot.nrdr.features.lateral.latcontrol_fw import LatControlFirmware
  from openpilot.nrdr.features.lateral.latcontrol_ptm_testing import LatControlPtmTesting, PtmTestingCore, PtmTestingFeedforward
  from openpilot.nrdr.features.lateral.vfn_eps_core import HondaEpsLateralCore, HondaEpsFirmwareFeedforward
  cp, sp = admitted_car
  baseline, testing = (cls(cp, sp, None, .01) for cls in (LatControlFirmware, LatControlPtmTesting))
  assert type(baseline.core) is HondaEpsLateralCore
  assert type(baseline.core.ff) is HondaEpsFirmwareFeedforward
  assert type(testing.core) is PtmTestingCore
  assert type(testing.core.ff) is PtmTestingFeedforward
  assert baseline.core.pid is not testing.core.pid
  assert baseline.core.ff is not testing.core.ff
  for controller in (baseline, testing):
    # Supply already converted angles to isolate the wrapper/core, not vehicle geometry.
    controller.steer_ratio_selection = NS(desired_angle_no_offset=lambda vm, angle, speed, roll, desired: desired)
  for frame in range(450):
    angle = 140. * math.sin(frame / 80.)
    state = NS(vEgo=8. + frame / 30., steeringAngleDeg=angle, steeringRateDeg=1.,
               steeringPressed=200 <= frame < 220, steeringTorque=-3. if 200 <= frame < 220 else 0.)
    model = NS(meta=NS(laneChangeState=NS(raw=0)),
               action=NS(lateralSource="plan" if frame < 300 else "actionHead", ptmTimingRestored=True))
    outputs = []
    for controller in (baseline, testing):
      controller.update_model_v2(model)
      active = 10 <= frame < 400
      if not active:
        controller.reset()
      output, target, telemetry = controller.update(active, state, None, NS(roll=.01, angleOffsetDeg=.5),
        225 <= frame < 230, angle + 15. * math.sin(frame / 17.), None, False, .2)
      assert abs(output) <= min(controller.steer_max, controller.core.ff.cal.output_ceiling())
      if not active:
        assert output == 0.
      fields = telemetry.to_dict()
      if controller is testing:
        trace = fields.pop("ptmTesting")
        assert trace["version"] == 1
        assert trace["entryMonoTime"] > 0
        assert trace["intervalValid"] == (frame != 0)
        assert trace["nominalDt"] == .01
        assert trace["rawPressed"] == state.steeringPressed
        if trace["coreUpdated"]:
          assert trace["after"]["output"] == controller.core.output
          if active:
            assert trace["effectivePressed"] == controller.pressed_prev
          assert trace["desiredAngleNoOffset"] == controller.prev_angle
        else:
          assert not telemetry.ptmTesting._has("before")
          assert not telemetry.ptmTesting._has("after")
      else:
        assert not telemetry._has("ptmTesting")
      outputs.append((output, target, fields))
    assert outputs[0] == outputs[1]
  original = baseline.core.output_lpf_enabled
  testing.core.output_lpf_enabled = not original
  assert baseline.core.output_lpf_enabled == original


def measurement_core_type():
  # Exercise the real pure Testing subclass even on hosts without native messaging.
  from openpilot.nrdr.features.lateral.vfn_eps_core import HondaEpsLateralCore
  source = Path(__file__).resolve().parents[1] / "features/lateral/latcontrol_ptm_testing.py"
  node, = [n for n in ast.parse(source.read_text()).body if isinstance(n, ast.ClassDef) and n.name == "PtmTestingCore"]
  env = {"HondaEpsLateralCore": HondaEpsLateralCore, "math": math}
  exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), "exec"), env)
  return env["PtmTestingCore"]


def test_measurements_preserve_math_and_reproduce_each_consumed_update():
  from openpilot.cereal import log
  from openpilot.nrdr.features.lateral.vfn_eps_core import HondaEpsLateralCore
  args = ([0., 11.175, 11.176, 22.352], [.018, .024, .048, .060],
          [0., 11.175, 11.176, 22.352], [.006, .008, .016, .020], .01)
  testing = measurement_core_type()(*args)
  baseline = HondaEpsLateralCore(*args)
  reconstruction = measurement_core_type()(*args)
  for frame in range(1200):
    if frame % 301 == 0:
      baseline.reset()
      testing.reset()
      assert testing.trace is None
    desired = 260. * math.sin(frame / 60.)
    speed = (1.5, 4., 11.175, 11.176, 22.351, 22.352, 30.)[(frame // 50) % 7]
    inputs = (desired, .432198765, desired - 90. * math.sin(frame / 80.), speed, .018765432,
              30 <= frame % 100 < 40, frame % 7 < 3)
    options = {"optimized_lane_change": frame % 100 > 90, "override_fade_up_s": 1.0}
    assert testing.update(*inputs, **options) == baseline.update(*inputs, **options)
    message = log.ControlsState.PtmTestingTrace.new_message(**testing.trace)
    with log.ControlsState.PtmTestingTrace.from_bytes(message.to_bytes()) as decoded:
      trace = decoded.to_dict()
    assert trace["passedSteerLimited"] == inputs[-1]
    assert trace["effectivePressed"] == inputs[-2]
    assert trace["speed"] == speed
    assert trace["after"]["integral"] == baseline.pid.i
    assert trace["after"]["p"] == baseline.pid.p
    assert trace["after"]["weightedFf"] == baseline.pid.f
    # Restore only the recorded pre-state, then rerun the production arithmetic.
    before = trace["before"]
    reconstruction.pid.i = before["integral"]
    reconstruction.ff.prev_angle = before["ffAngle"] if before["ffAngleValid"] else None
    reconstruction.ff.rate = before["ffRate"]
    reconstruction.ff.r5 = before["ffR5"]
    reconstruction.ff.output = before["ffOutput"]
    reconstruction.ff_ramp = before["ffRamp"]
    reconstruction.since_press_s = before["sincePress"] if before["sincePressValid"] else math.inf
    reconstruction.output_lpf.x = before["filterState"]
    consumed = tuple(trace[key] for key in ("desiredAngleNoOffset", "angleOffset", "measuredAngle", "speed", "roll",
                                            "effectivePressed", "passedSteerLimited"))
    assert reconstruction.update(*consumed, optimized_lane_change=trace["optimizedLaneChange"],
                                 override_fade_up_s=trace["overrideFadeUp"]) == baseline.output
    assert reconstruction.trace["after"] == trace["after"]
    assert testing.output_lpf_tau == baseline.output_lpf_tau


def test_optional_measurement_schema_round_trip():
  from openpilot.cereal import log
  # A historical/default PID payload has no measurement pointer.
  old = log.Event.new_message()
  old.init("controlsState").lateralControlState.init("pidState").p = .125
  with log.Event.from_bytes(old.to_bytes()) as decoded:
    assert not decoded.controlsState.lateralControlState.pidState._has("ptmTesting")
  old.clear_write_flag()
  sample = old.controlsState.lateralControlState.pidState
  core = measurement_core_type()([0], [.02], [0], [.006], .01)
  core.update(40., .123456789, 35., 5., .01, False, True)
  sample.ptmTesting = dict(core.trace, version=1, entryMonoTime=time.monotonic_ns(), nominalDt=.01)
  with log.Event.from_bytes(old.to_bytes()) as decoded:
    trace = decoded.controlsState.lateralControlState.pidState.ptmTesting.to_dict()
    for key, value in core.trace.items():
      assert trace[key] == value
    assert trace["angleOffset"] == .123456789


def test_publish_measurements_only_touch_testing_log():
  from openpilot.cereal import log
  source = Path(__file__).resolve().parents[2] / "selfdrive/controls/controlsd.py"
  tree = ast.parse(source.read_text())
  nodes = [node for node in ast.walk(tree) if isinstance(node, ast.If)
           and ast.unparse(node.test) == "lac_log._has('ptmTesting')"]
  assert len(nodes) == 1
  publish, = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == 'publish']
  call_sites = [node for node in ast.walk(publish) if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute) and node.func.attr == 'get_lat_active']
  assert len(call_sites) == 1  # This method advances blinker-pause state; never call again for logging.
  bind, = [node for node in publish.body if isinstance(node, ast.Assign)
           and any(isinstance(t, ast.Name) and t.id == 'lat_active_for_mismatch' for t in node.targets)]
  mismatch, = [node for node in publish.body if isinstance(node, ast.If)
               and ast.unparse(node.test) == 'lat_active_for_mismatch']
  code = compile(ast.Module(body=[bind, mismatch, *nodes], type_ignores=[]), str(source), "exec")
  from opendbc.car.structs import car
  class Messages(dict):
    logMonoTime = {"carState": 11, "carOutput": 12, "vehicleParameters": 13, "modelV2": 14}
  messages = Messages(carOutput=NS(actuatorsOutput=NS(torque=.234567891)))
  command = NS(actuators=NS(torque=.123456789))
  for testing, active in ((False, False), (False, True), (True, False), (True, True)):
    calls = []
    def lat_active(sm):
      calls.append(sm)
      return active
    owner = NS(sm=messages, steer_limited_by_safety=False, get_lat_active=lat_active,
               CP=NS(steerControlType=car.CarParams.SteerControlType.torque))
    logged = log.ControlsState.LateralPIDState.new_message(p=.25)
    if testing:
      logged.init("ptmTesting").version = 1
    exec(code, {"self": owner, "CC": command, "lac_log": logged, "car": car})
    assert calls == [messages]
    assert logged.p == .25 and command.actuators.torque == .123456789
    assert owner.steer_limited_by_safety == active
    if testing:
      trace = logged.ptmTesting
      assert trace.carStateMonoTime == 11 and trace.carOutputMonoTime == 12
      assert trace.vehicleParametersMonoTime == 13 and trace.modelMonoTime == 14
      assert trace.comparedCommand == .123456789 and trace.comparedApplied == .234567891
      assert trace.mismatchEvaluated == active and trace.nextSteerLimited == active
    else:
      assert not logged._has("ptmTesting")


@pytest.mark.skipif(sys.platform == "win32", reason="native controller dependencies")
def test_native_factory_keeps_existing_ids_and_requires_opt_in(admitted_car):
  from openpilot.nrdr.features.lateral.latcontrol_fw import LatControlFirmware
  from openpilot.nrdr.features.lateral.latcontrol_ptm_testing import LatControlPtmTesting
  cp, sp = admitted_car
  source = Path(__file__).resolve().parents[2] / "sunnypilot/selfdrive/controls/controlsd_ext.py"
  method, = [n for n in ast.walk(ast.parse(source.read_text()))
             if isinstance(n, ast.FunctionDef) and n.name == "initialize_lateral_control"]
  env = {}
  exec(compile(ast.Module(body=[method], type_ignores=[]), str(source), "exec"), env)
  class Settings(dict):
    def get_bool(self, key):
      return bool(self.get(key, False))
  fallback = object()
  for value, expected in ((0, None), (1, LatControlFirmware), (2, LatControlPtmTesting)):
    owner = NS(CP=cp, CP_SP=sp, params=Settings(NrdrLateralController=value))
    controller = env["initialize_lateral_control"](owner, fallback, None, .01)
    assert (controller is fallback) if expected is None else (type(controller) is expected)
