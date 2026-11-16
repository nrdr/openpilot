"""Run controlsd's measurement prefix without importing device/model/UI services."""
import ast
import copy
import math
import struct
from pathlib import Path
from types import SimpleNamespace

import pytest
from opendbc.car.vehicle_model import VehicleModel

from openpilot.nrdr.features.lateral.honda_rack_map import RACK_MAP_TABLES
from openpilot.nrdr.features.lateral.steer_ratio_tuning import (
  SteerRatioMode,
  SteerRatioModeLatch,
  SteerRatioSelection,
  resolve_steer_ratio_selection,
)
from openpilot.nrdr.hooks.controlsd import vehicle_model_state
from openpilot.nrdr.params import ParamSnapshot
from openpilot.sunnypilot.livedelay.helpers import get_lat_delay

POSES = ((-135.0, 5.0, 1.7, 0.035), (47.5, 22.0, -1.2, -0.025),
         (0.75, 40.0, 1.7, 0.035), (12.0, 0.0, 0.0, 0.0))
NON_RACK = ("manual", "comma", "raw", "legacy-firmware", "fallback", "hybrid")


@pytest.fixture(scope="module")
def measure_controlsd():
  # Execute the unchanged source statements through self.curvature, including
  # the real hook and VM update. No copied/reimplemented production expression.
  path = Path(__file__).resolve().parents[2] / "selfdrive/controls/controlsd.py"
  control_class = next(node for node in ast.parse(path.read_text(encoding="utf-8")).body
                       if isinstance(node, ast.ClassDef) and node.name == "Controls")
  method = copy.deepcopy(next(node for node in control_class.body
                              if isinstance(node, ast.FunctionDef) and node.name == "state_control"))
  end, = [index for index, node in enumerate(method.body) if isinstance(node, ast.Assign)
          and any(isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name)
                  and target.value.id == "self" and target.attr == "curvature" for target in node.targets)]
  method.body = method.body[:end + 1] + [ast.Return(value=ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()),
                                                                     attr="curvature", ctx=ast.Load()))]
  namespace = {"math": math, "vehicle_model_state": vehicle_model_state, "get_lat_delay": get_lat_delay}
  tree = ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[]))
  # Execute only repository-owned source statements.
  exec(compile(tree, str(path), "exec"), namespace)
  return namespace["state_control"]


class Services(dict):
  def __init__(self, **values):
    super().__init__(values)
    self.valid = {"vehicleParameters": True}


class CaptureController:
  def __init__(self, events):
    self.events = events

  def set_live_tuning_snapshot(self, snapshot):
    self.snapshot = snapshot

  def set_steer_ratio_selection(self, selection):
    self.events.append("selection")
    self.steer_ratio_selection = selection


class RecordingVehicleModel(VehicleModel):
  def __init__(self, CP, events):
    self.events = events
    super().__init__(CP)

  def update_params(self, stiffness_factor, steer_ratio):
    self.events.append("vm-update")
    super().update_params(stiffness_factor, steer_ratio)


def car_params(fingerprint="HONDA_CIVIC", firmware=b"39990-TEG-A010", wheelbase=2.7):
  return SimpleNamespace(brand="honda", carFingerprint=fingerprint, carFw=[SimpleNamespace(ecu="eps", fwVersion=firmware)],
                         steerRatio=15.38, steerRatioRear=0.0, mass=1462.0, rotationalInertia=2500.0,
                         wheelbase=wheelbase, centerToFront=0.4 * wheelbase,
                         tireStiffnessFront=192150.0, tireStiffnessRear=202500.0,
                         minSteerSpeed=0.0, steerAtStandstill=True, steerActuatorDelay=0.1)


def settings(mode, **extra):
  return {"NrdrSteerRatioMode": int(mode), "NrdrSteerRatioManualCenter": 15.38,
          "NrdrSteerRatioManualFinal": 10.93, "NrdrLearnStiffness": True, "NrdrLearnAngleOffset": True,
          "LagdToggle": True, **extra}


def controls_for(CP, values, pose, stiffness=1.0):
  angle, speed, offset, roll = pose
  live = SimpleNamespace(steerRatio=18.2, steerRatioValid=True, stiffnessFactor=stiffness, angleOffsetDeg=offset, roll=roll)
  CS = SimpleNamespace(steeringAngleDeg=angle, vEgo=speed, standstill=speed == 0.0,
                       steerFaultTemporary=False, steerFaultPermanent=False)
  snapshot = ParamSnapshot(1, values)
  events = []
  controls = SimpleNamespace(CP=CP, nrdr_live_params=SimpleNamespace(snapshot=snapshot),
                             LaC=CaptureController(events), VM=RecordingVehicleModel(CP, events),
                             get_lat_active=lambda _sm: True,
                             sm=Services(carState=CS, vehicleParameters=live,
                                         lateralDelay=SimpleNamespace(lateralDelay=0.3)))
  controls.steer_ratio_latch = SteerRatioModeLatch(resolve_steer_ratio_selection(CP, snapshot))
  events.clear()  # Construction's VM update is not part of a control frame.
  return controls


def old_measurement(controls):
  """The pre-fix pipeline, with raw-angle ratio evaluation kept before offset."""
  CS, live = controls.sm["carState"], controls.sm["vehicleParameters"]
  selection = controls.steer_ratio_latch.selection
  vm = VehicleModel(controls.CP)
  stiffness = live.stiffnessFactor if controls.learn_stiffness else 1.0
  ratio = selection.ratio_at(CS.steeringAngleDeg, controls.nrdr_last_valid_comma_ratio)
  offset = live.angleOffsetDeg if controls.learn_angle_offset else 0.0
  vm.update_params(max(stiffness, 0.1), max(ratio, 0.1))
  angle = selection.linearize_measured_angle(CS.steeringAngleDeg - offset)
  return -vm.calc_curvature(math.radians(angle), CS.vEgo, live.roll)


def assert_same_bits(actual, expected):
  assert struct.pack("!d", actual) == struct.pack("!d", expected)


@pytest.mark.parametrize("kind", NON_RACK)
@pytest.mark.parametrize("pose", POSES)
@pytest.mark.parametrize("stiffness", (0.65, 1.0, 1.25))
def test_non_rack_measurement_is_bit_identical(measure_controlsd, kind, pose, stiffness):
  CP = car_params()
  if kind == "legacy-firmware":
    CP = car_params("HONDA_CRV_5G", b"39990-TLA-A220")  # Table A exists; no rack map is borrowed.
  elif kind == "raw":
    CP = car_params("HONDA_CLARITY", b"39990-TRW-A020")
  elif kind == "fallback":
    CP = car_params(firmware=b"UNKNOWN")
  mode = {"manual": 0, "comma": 1, "raw": 2, "legacy-firmware": 3, "fallback": 3, "hybrid": 0}[kind]
  values = settings(mode)
  if kind == "hybrid":
    values.update(NrdrSteerRatioHybrid=True, NrdrSteerRatioSourceB=3, NrdrSteerRatioBlendStart=25.0)
  controls = controls_for(CP, values, pose, stiffness)
  actual = measure_controlsd(controls)
  selection = controls.LaC.steer_ratio_selection
  assert selection.rack_map is None
  if kind == "legacy-firmware":
    assert selection.firmware_vgr_selected
  if kind == "hybrid":
    assert selection.hybrid is not None
  assert_same_bits(actual, old_measurement(controls))


@pytest.mark.parametrize("table", RACK_MAP_TABLES, ids=lambda table: table.name)
@pytest.mark.parametrize("pose", POSES)
@pytest.mark.parametrize("stiffness", (0.65, 1.25))
def test_controlsd_uses_full_rack_inverse(measure_controlsd, table, pose, stiffness):
  CP = car_params(table.fingerprint, table.firmware[0].encode(), table.wheelbase)
  controls = controls_for(CP, settings(SteerRatioMode.FIRMWARE), pose, stiffness)
  actual = measure_controlsd(controls)
  selection = controls.LaC.steer_ratio_selection
  angle, speed, offset, roll = pose
  assert selection.rack_map is not None
  expected = -selection.rack_map.curvature_from_angle(angle - offset, speed, roll)
  assert_same_bits(actual, expected)
  restored_angle = selection.desired_angle_no_offset(controls.VM, angle, speed, roll, actual) + offset
  assert restored_angle == pytest.approx(angle, abs=1e-7)
  # VM still receives the same live tire stiffness and CP ratio; the rack map
  # owns only this conversion, not a rewrite of the other VM consumers.
  assert controls.VM.cF == stiffness * CP.tireStiffnessFront
  assert controls.VM.cR == stiffness * CP.tireStiffnessRear
  assert controls.VM.sR == CP.steerRatio


def test_snapshot_then_vm_update_then_measurement_with_raw_angle(measure_controlsd, monkeypatch):
  controls = controls_for(car_params(), settings(0), POSES[0], 0.65)
  events = controls.VM.events
  original = SteerRatioSelection.measured_curvature

  def capture(selection, VM, measured_angle_deg, speed, roll, angle_offset_deg=0.0):
    events.append("measurement")
    assert events == ["selection", "vm-update", "measurement"]
    assert selection is controls.steer_ratio_latch.selection
    assert measured_angle_deg == POSES[0][0] and angle_offset_deg == POSES[0][2]
    assert speed == POSES[0][1] and roll == POSES[0][3]
    assert VM.cF == 0.65 * controls.CP.tireStiffnessFront
    return original(selection, VM, measured_angle_deg, speed, roll, angle_offset_deg)

  monkeypatch.setattr(SteerRatioSelection, "measured_curvature", capture)
  assert_same_bits(measure_controlsd(controls), old_measurement(controls))
  assert events == ["selection", "vm-update", "measurement"]


def test_held_geometry_and_comma_ratio_transitions(measure_controlsd):
  controls = controls_for(car_params(), settings(3), POSES[1], 1.25)
  initial = measure_controlsd(controls)
  accepted = controls.LaC.steer_ratio_selection
  assert accepted.rack_map is not None
  rejected = settings(3, NrdrSteerRatioHybrid=True, NrdrSteerRatioSourceB=99)
  controls.nrdr_live_params.snapshot = ParamSnapshot(2, rejected)
  assert_same_bits(measure_controlsd(controls), initial)
  assert controls.LaC.steer_ratio_selection is accepted  # Same held geometry, not the rejected candidate.
  assert controls.steer_ratio_latch.rejected_reason

  controls.get_lat_active = lambda _sm: False
  fallback = measure_controlsd(controls)
  assert controls.LaC.steer_ratio_selection.effective_mode is None
  assert_same_bits(fallback, old_measurement(controls))

  controls.get_lat_active = lambda _sm: True
  for generation, mode in ((3, 0), (4, 1)):
    controls.nrdr_live_params.snapshot = ParamSnapshot(generation, settings(mode))
    assert_same_bits(measure_controlsd(controls), old_measurement(controls))
    assert controls.LaC.steer_ratio_selection.effective_mode == mode

  controls.sm["vehicleParameters"].steerRatio = math.nan
  controls.sm.valid["vehicleParameters"] = False
  held_comma = measure_controlsd(controls)
  assert controls.VM.sR == 18.2
  assert_same_bits(held_comma, old_measurement(controls))


@pytest.mark.parametrize("mode", tuple(SteerRatioMode))
@pytest.mark.parametrize("active", (False, True))
@pytest.mark.parametrize("stale_controller_selection", (False, True))
def test_measurement_does_not_require_controller_geometry(measure_controlsd, mode, active, stale_controller_selection):
  CP = car_params("TOYOTA_RAV4", b"UNKNOWN")
  CP.brand = "toyota"
  controls = controls_for(CP, settings(mode), POSES[1], 0.65)

  def forbidden(*args, **kwargs):
    raise AssertionError("controlsd must use the accepted latch, not optional controller geometry")

  # Legacy/extension controllers need neither a setter nor a geometry attribute.
  # A stale optional attribute must not override the frame's accepted selection.
  controls.LaC = (SimpleNamespace(steer_ratio_selection=SimpleNamespace(measured_curvature=forbidden))
                  if stale_controller_selection else object())
  controls.get_lat_active = lambda _sm: active
  assert not hasattr(controls.LaC, "set_steer_ratio_selection")
  actual = measure_controlsd(controls)
  assert controls.steer_ratio_latch.selection.rack_map is None
  assert_same_bits(actual, old_measurement(controls))
