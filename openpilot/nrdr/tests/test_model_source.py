"""Where the model's steering comes from, and the command delay the Firmware Controller takes from it."""
import ast
import re
from pathlib import Path
from types import SimpleNamespace as NS

import numpy as np
import pytest

from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from opendbc.car.structs import car as car_structs
from opendbc.car.vehicle_model import VehicleModel
from openpilot.nrdr.features.lateral import model_source as ms
from openpilot.nrdr.features.lateral.latcontrol_fw import LatControlFirmware
from openpilot.nrdr.features.lateral.yaw_control_timing import command_delay

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("output,mlsim,source", [
  ({"action": np.zeros((1, 2)), "plan": np.zeros((1, 33, 15))}, True, ms.ACTION_HEAD),
  ({"plan": np.zeros((1, 33, 15))}, True, ms.PLAN),                                     # Pop v2, TCP v3
  ({"plan": np.zeros((1, 33, 15)), "desired_curvature": np.zeros((1, 1))}, True, ms.PLAN),
  ({"plan": np.zeros((1, 33, 15)), "desired_curvature": np.zeros((1, 1))}, False, ms.PLAN),
  ({"plan": np.zeros((1, 33, 15)), "desired_curvature": np.ones((1, 1))}, False, ms.CURVATURE_HEAD),
])
def test_the_source_is_the_one_get_action_from_model_steers_with(output, mlsim, source):
  assert ms.lateral_source(output, mlsim) == source


@pytest.mark.parametrize("curvature", [None, 0.0, 0.002, -0.002])
@pytest.mark.parametrize("mlsim", [False, True])
def test_source_matches_the_actual_curvature_branch_even_at_zero(curvature, mlsim, monkeypatch):
  from openpilot.sunnypilot.modeld_v2 import fill_model_msg as publisher

  plan_curvature = 0.019
  monkeypatch.setattr(publisher, "get_curvature_from_plan", lambda *args: plan_curvature)
  output = {"plan": np.zeros((1, 33, 15))}
  if curvature is not None:
    output["desired_curvature"] = np.array([[curvature]])
  actual = publisher.get_curvature_from_output(output, output["plan"][0], 20., .275, mlsim)
  source = ms.lateral_source(output, mlsim)
  assert source == (ms.PLAN if actual == plan_curvature else ms.CURVATURE_HEAD)
  assert actual == (plan_curvature if mlsim or not curvature else curvature)


@pytest.mark.parametrize("source", [ms.PLAN, ms.CURVATURE_HEAD, ms.ACTION_HEAD])
def test_sunny_companion_action_keeps_provenance_after_serialization(source):
  from openpilot.cereal import log, messaging

  publisher = ROOT / "sunnypilot/modeld_v2/modeld.py"
  tree = ast.parse(publisher.read_text(encoding="utf-8"))
  mirror, = [node for node in ast.walk(tree) if isinstance(node, ast.Assign) and
             any(ast.unparse(target) == "drivingdata_send.drivingModelData.action" for target in node.targets)]
  model = messaging.new_message("modelV2")
  model.modelV2.action = log.ModelDataV2.Action.new_message(
    desiredCurvature=-.0125, desiredAcceleration=.625, shouldStop=True,
    lateralActionTime=.275, lateralSource=source, delayInput="actionT")
  driving = messaging.new_message("drivingModelData")
  exec(compile(ast.Module(body=[mirror], type_ignores=[]), str(publisher), "exec"),
       {"drivingdata_send": driving, "modelv2_send": model})
  with log.Event.from_bytes(driving.to_bytes()) as restored:
    assert restored.drivingModelData.action.to_dict() == model.modelV2.action.to_dict()


def test_the_delay_input_names_how_the_told_delay_reaches_the_model():
  assert ms.delay_input({"action_t": 0, "desire_pulse": 0}) == "actionT"
  assert ms.delay_input({"lateral_control_params": 0}) == "lateralControlParams"
  assert ms.delay_input({"desire_pulse": 0, "traffic_convention": 0}) == "none"


@pytest.mark.parametrize("action_time,delay", [(0.0, None), (-1.0, None), (0.155, 0.145), (0.275, 0.025), (0.3, 0.0), (0.45, 0.0)])
def test_the_plan_floor_command_delay_lands_the_plan_at_the_told_time(action_time, delay):
  assert ms.plan_floor_command_delay(action_time) == (None if delay is None else pytest.approx(delay))


def test_the_slew_starts_at_its_first_target_and_moves_at_its_rate():
  slew = ms.CommandDelaySlew(0.01)
  assert slew.update(0.175) == 0.175
  out = [slew.update(0.025) for _ in range(60)]
  assert out[0] == pytest.approx(0.175 - 0.003) and out[-1] == pytest.approx(0.025)


def _controller(fingerprint, firmware):
  cp = NS(brand="honda", carFingerprint=fingerprint, steerRatio=16.5, wheelbase=2.75, steerLimitTimer=.8,
          carFw=[NS(ecu="eps", fwVersion=firmware)], lateralTuning=NS(which=lambda: "pid"))
  return LatControlFirmware(cp, NS(flags=HondaFlagsSP.EPS_MODIFIED.value), None, .01)


def _delays(control, source, action_time, frames, speed=8.):
  vm = VehicleModel(car_structs.CarParams.new_message(
    mass=1840, rotationalInertia=3000, wheelbase=2.75, centerToFront=1.08,
    steerRatioRear=0, steerRatio=16.5, tireStiffnessFront=200000, tireStiffnessRear=200000))
  cs = NS(vEgo=speed, steeringAngleDeg=0., steeringRateDeg=0., steeringPressed=False, steeringTorque=0.)
  model = NS(meta=NS(laneChangeState=NS(raw=0)), action=NS(lateralSource=source, lateralActionTime=action_time))
  out = []
  for _ in range(frames):
    control.update_model_v2(model)
    out.append(control.update(True, cs, vm, NS(roll=0., angleOffsetDeg=0.), False, .001, None, False, .2)[2].commandDelay)
  return out


@pytest.mark.parametrize("fingerprint,firmware,calibration,action_time", [
  ("HONDA_CLARITY", b"39990-TRW-A020", "clarity_a020", 0.155),        # 0.08 told at 7 m/s
  ("HONDA_CIVIC", b"39990-TEG-A010", "civic_teg_a010", 0.275),         # 0.20 told
  ("HONDA_CIVIC_BOSCH", b"39990-TBA-C020", "civic_bosch_c020", 0.355),  # 0.28 told: above the floor
])
def test_a_plan_model_on_a_scheduled_profile_only_undoes_the_floor(fingerprint, firmware, calibration, action_time):
  control = _controller(fingerprint, firmware)
  head = _delays(control, "actionHead", action_time, 5)
  assert head[-1] == pytest.approx(command_delay(None, 8., calibration=calibration), abs=1e-6)
  plan = _delays(control, "plan", action_time, 300)
  assert plan[-1] == pytest.approx(max(0.3 - action_time, 0.), abs=1e-6)
  assert max(abs(a - b) for a, b in zip([head[-1], *plan], plan, strict=False)) <= 0.003 + 1e-6  # slewed, no step


def test_an_unknown_source_or_an_older_model_message_keeps_the_calibrations_delay():
  control = _controller("HONDA_CIVIC", b"39990-TEG-A010")
  assert _delays(control, "unknown", 0.275, 3)[-1] == pytest.approx(0.175)
  control.update_model_v2(NS(meta=NS(laneChangeState=NS(raw=0))))  # no action field (an older publisher)
  assert control._command_delay(8.) == pytest.approx(0.175)


def test_the_schema_names_every_source_and_delay_input():
  schema = (ROOT / "cereal" / "log.capnp").read_text(encoding="utf-8")
  action = re.search(r"\n  struct Action \{(?P<body>.*?)\n  \}", schema[schema.index("struct ModelDataV2 {"):], re.DOTALL)
  body = action.group("body")
  assert "lateralSource @4 :LateralSource;" in body and "delayInput @5 :DelayInput;" in body
  for name in ("unknown", ms.PLAN, ms.ACTION_HEAD, ms.CURVATURE_HEAD, "none", "actionT", "lateralControlParams"):
    assert re.search(rf"\b{name} @\d+;", body), name


@pytest.mark.parametrize("publisher", ["selfdrive/modeld/modeld.py", "sunnypilot/modeld_v2/modeld.py"])
def test_both_publishers_attach_the_source_and_delay_input(publisher):
  tree = ast.parse((ROOT / publisher).read_text(encoding="utf-8"))
  call, = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "set_lateral_action_timing"]
  keywords = {k.arg: k.value for k in call.keywords}
  assert keywords["lateral_source"].func.id == "lateral_source" and keywords["delay_input"].func.id == "delay_input"
