"""Bare admission, real wrapper, geometry, timing, and dependency-boundary checks."""
import ast
import hashlib
import json
import math
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from opendbc.car import gen_empty_fingerprint, structs
from opendbc.car.honda.interface import CarInterface
from opendbc.car.honda.values import CAR
from opendbc.car.vehicle_model import VehicleModel
from openpilot.nrdr.params import PARAMS, read_settings, registry_lines
from openpilot.nrdr.features.lateral.controller_selection import PROFILES, firmware_controller_profile
from openpilot.nrdr.features.lateral.steer_ratio_tuning import SteerRatioMode
from openpilot.nrdr.features.lateral.hybrid_steer_ratio import AngleSource, build_hybrid
from openpilot.nrdr.features.lateral.latcontrol_fw import LatControlFirmware
from openpilot.nrdr.features.lateral import vfn_eps_core as core
from openpilot.nrdr.features.lateral.yaw_control_timing import CommandDelay, command_delay, prediction_delay
from openpilot.nrdr.hooks.lateral import apply_startup_policy, create_firmware_controller


ROOT = Path(__file__).resolve().parents[3]
CASES = list(PROFILES.items())


def cp_for(fingerprint, version):
  fw = [structs.CarParams.CarFw(ecu="eps", fwVersion=version.encode() + b"\0\0")]
  cp = CarInterface.get_params(CAR[fingerprint], gen_empty_fingerprint(), fw, False, False, False)
  cp.carFw = fw  # get_car sets these after get_params, before constructing the interface.
  return cp


def settings_for(profile, **extra):
  return read_settings({"NrdrLateralController": 1, "NrdrFirmwareImage": profile.firmware_image, **extra})


@pytest.mark.parametrize("family,profile", CASES)
def test_exact_modified_family_and_image_are_both_required(family, profile):
  fingerprint, version = family
  cp = cp_for(fingerprint, version.replace("-", ",", 1))
  assert firmware_controller_profile(cp, settings_for(profile)) is profile
  for image in ("", "1", "04147917", profile.firmware_image + "x"):
    assert firmware_controller_profile(cp, settings_for(profile, NrdrFirmwareImage=image)) is None
  for controller in (0, 2, None, "oops"):
    assert firmware_controller_profile(cp, settings_for(profile, NrdrLateralController=controller)) is None
  assert firmware_controller_profile(cp_for(fingerprint, version), settings_for(profile)) is None
  cp.carFw = [*cp.carFw, structs.CarParams.CarFw(ecu="eps", fwVersion=b"39990-XXX,XXXX")]
  assert firmware_controller_profile(cp, settings_for(profile)) is None


@pytest.mark.parametrize("family,profile", CASES)
@pytest.mark.parametrize("wrong_car", ["HONDA_ACCORD", "HONDA_CRV_5G", "HONDA_CIVIC_BOSCH_DIESEL", "TOYOTA_RAV4"])
def test_no_generic_honda_or_cross_car_fallback(family, profile, wrong_car):
  cp = SimpleNamespace(brand="honda", carFingerprint=wrong_car, steerRatio=16.5,
                       lateralTuning=SimpleNamespace(which=lambda: "pid"),
                       carFw=[SimpleNamespace(ecu="eps", fwVersion=family[1].replace("-", ",", 1).encode())])
  assert create_firmware_controller(cp, None, .01, settings_for(profile)) is None


@pytest.mark.parametrize("family,profile", CASES)
def test_modified_car_without_acknowledged_controller_cannot_actuate(family, profile):
  fp, version = family
  cp = cp_for(fp, version.replace("-", ",", 1))
  apply_startup_policy(cp, settings_for(profile))
  assert not cp.dashcamOnly
  apply_startup_policy(cp, read_settings({}))
  assert cp.dashcamOnly


def test_stock_car_is_not_modified_by_startup_policy():
  cp = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
  before = cp.to_dict()
  apply_startup_policy(cp, read_settings({}))
  assert cp.to_dict() == before
  assert create_firmware_controller(cp, None, .01, read_settings({})) is None


@pytest.mark.parametrize("family,profile", CASES)
@pytest.mark.parametrize("mode", [0, 1, 2, 3])
def test_runtime_uses_selected_geometry_without_mutating_carparams(family, profile, mode):
  fp, version = family
  cp = cp_for(fp, version.replace("-", ",", 1))
  before = cp.to_dict()
  settings = settings_for(profile, NrdrSteerRatioMode=mode)
  controller = create_firmware_controller(cp, None, .01, settings)
  assert isinstance(controller, LatControlFirmware)
  vm = VehicleModel(cp)
  vm.update_params(1., 18.)
  controller.prepare_geometry(18.)
  selection = controller.selection
  assert selection.requested_mode == mode
  if mode == 2 and fp not in ("HONDA_CLARITY", "HONDA_CIVIC"):
    assert selection.effective_mode is SteerRatioMode.COMMA
  cs = SimpleNamespace(vEgo=20., steeringAngleDeg=10., steeringRateDeg=0., steeringPressed=False, steeringTorque=0.)
  params = SimpleNamespace(roll=.01, angleOffsetDeg=.3)
  curvature = selection.measured_curvature(vm, cs.steeringAngleDeg, cs.vEgo, params.roll, params.angleOffsetDeg)
  for _ in range(50):
    output, target, logged = controller.update(False, cs, vm, params, False, curvature, False, .2)
  assert output == 0. and not logged.active
  assert target == pytest.approx(cs.steeringAngleDeg, abs=1e-6)
  for _ in range(100):
    output, target, logged = controller.update(True, cs, vm, params, False, curvature, False, .2)
    assert math.isfinite(output) and abs(output) <= 1.
    assert logged.epsFfActive and logged.commandDelay == pytest.approx(.025)
  assert cp.to_dict() == before


@pytest.mark.parametrize("family,profile", CASES)
def test_wrapper_matches_unmodified_development_core_for_identical_inputs(family, profile):
  fp, version = family
  cp = cp_for(fp, version.replace("-", ",", 1))
  controller = create_firmware_controller(cp, None, .01, settings_for(profile, NrdrSteerRatioMode=1))
  # A fresh core with the copied calibration must produce the same command for
  # the wrapper's delayed, rate-limited target and the stock override signal.
  from copy import deepcopy
  expected = deepcopy(controller.core)
  vm = VehicleModel(cp)
  params = SimpleNamespace(roll=0., angleOffsetDeg=.2)
  cs = SimpleNamespace(vEgo=20., steeringAngleDeg=0., steeringRateDeg=0., steeringPressed=False, steeringTorque=0.)
  for frame in range(1000):
    cs.steeringAngleDeg = 15. * math.sin(frame / 71.)
    cs.steeringPressed = frame % 503 > 490
    controller.lane_change_state = 2 if 300 < frame < 400 else 0
    requested = controller.selection.measured_curvature(vm, 20. * math.sin(frame / 71.), cs.vEgo, 0.)
    out, target, logged = controller.update(True, cs, vm, params, False, requested, False, .2)
    reference = expected.update(target - params.angleOffsetDeg, params.angleOffsetDeg, cs.steeringAngleDeg,
                                cs.vEgo, params.roll, cs.steeringPressed, False,
                                optimized_lane_change=controller.lane_change_state in (2, 3))
    assert out == pytest.approx(reference, abs=1e-13)
    if 300 < frame < 400:
      assert logged.f == 0. and logged.epsFfWeight == 0.


@pytest.mark.parametrize("family,profile", CASES)
@pytest.mark.parametrize("speed", [0., 3.5, 7., 12., 20., 30., 40.])
def test_timing_is_profile_specific_and_manual_delay_never_replaces_it(family, profile, speed):
  expected = float(np.interp(speed, (3.5, 7., 12., 20., 30.), (.15, .08, .10, .20, .30)))
  assert prediction_delay(profile, speed, .83) == (expected if profile.prediction_schedule else .83)
  low = .145 if profile.calibration == "clarity_a020" else .175
  assert command_delay({}, speed, calibration=profile.calibration) == pytest.approx(np.interp(speed, (10., 15.), (low, .025)))
  assert prediction_delay(None, speed, .83) == .83


def test_delay_line_interpolation_and_history_survive_inactive_updates():
  line = CommandDelay(.01)
  for value in range(100):
    delayed = line.update(value, .025)
  assert delayed == pytest.approx(96.5)
  assert len(line.buf) == 32
  assert line.update(100., 0.) == 100.


@pytest.mark.parametrize("family,profile", CASES)
def test_lane_change_suppression_and_stock_override_integrator_behavior(family, profile):
  cp = cp_for(family[0], family[1].replace("-", ",", 1))
  controller = create_firmware_controller(cp, None, .01, settings_for(profile))
  vm = VehicleModel(cp)
  cs = SimpleNamespace(vEgo=15., steeringAngleDeg=0., steeringRateDeg=0., steeringPressed=False, steeringTorque=0.)
  params = SimpleNamespace(roll=0., angleOffsetDeg=0.)
  curvature = controller.selection.measured_curvature(vm, 10., 15., 0.)
  for _ in range(100):
    controller.update(True, cs, vm, params, False, curvature, False, .2)
  assert controller.core.ff_weight == 1.
  for state in (2, 3):
    controller.lane_change_state = state
    _, _, logged = controller.update(True, cs, vm, params, False, curvature, False, .2)
    assert logged.f == 0. and logged.epsFfWeight == 0.
  controller.lane_change_state = 0
  cs.steeringAngleDeg = controller.prev_angle  # Rejoin only once the wheel is on the path.
  controller.update(True, cs, vm, params, False, curvature, False, .2)
  assert 0. < controller.core.ff_weight < .1
  cs.steeringPressed = True
  old_i = controller.core.pid.i
  controller.update(True, cs, vm, params, False, curvature, False, .2)
  assert controller.core.pid.i == old_i
  controller.update(False, cs, vm, params, False, curvature, False, .2)
  assert controller.core.output == 0. and controller.core.pid.i == 0.


def test_registry_is_generated_from_one_bare_contract_and_settings_are_immutable():
  header = (ROOT / "openpilot/common/params_keys.h").read_text()
  generated = header.split("// NRDR_BARE_PARAMS_BEGIN (generated from openpilot.nrdr.params)\n", 1)[1].split("    // NRDR_BARE_PARAMS_END", 1)[0]
  assert generated.rstrip() == registry_lines()
  settings = read_settings({})
  assert set(settings) == set(PARAMS)
  with pytest.raises(TypeError):
    settings["NrdrLateralController"] = 1


def test_stock_runtime_seams_match_and_no_sunnypilot_or_frame_params_dependency():
  controls = (ROOT / "openpilot/selfdrive/controls/controlsd.py").read_text()
  model = (ROOT / "openpilot/selfdrive/modeld/modeld.py").read_text()
  assert "prediction_delay(self.LaC.profile, CS.vEgo, lat_delay)" in controls
  assert "prediction_delay(firmware_profile, v_ego, lat_delay)" in model
  assert "getattr(self.LaC, \"tuned\"" not in controls
  for source in (ROOT / "openpilot/nrdr").rglob("*.py"):
    if "tests" in source.parts:
      continue
    tree = ast.parse(source.read_text())
    for node in ast.walk(tree):
      if isinstance(node, ast.ImportFrom):
        assert "sunnypilot" not in (node.module or "")
      if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        assert node.func.id != "Params"


@pytest.mark.parametrize("mode", [0, 1, 2, 3])
def test_hybrid_geometry_is_monotonic_invertible_and_symmetric(mode):
  from openpilot.nrdr.features.lateral.steer_ratio_tuning import CLARITY_RAW_STEER_RATIO
  from openpilot.nrdr.features.lateral.honda_vgr import HONDA_VGR_PROFILES
  def source(value):
    return AngleSource(value, str(value), 16.5, 15.38, 10.93, 250., 18., CLARITY_RAW_STEER_RATIO, HONDA_VGR_PROFILES[0])
  hybrid = build_hybrid(source(mode), source(3), 10.)
  inputs = np.linspace(0., 500., 2001)
  outputs = [hybrid.forward(x) for x in inputs]
  assert np.all(np.diff(outputs) > 0.)
  for angle in inputs[::10]:
    assert hybrid.inverse(hybrid.forward(angle)) == pytest.approx(angle, abs=1e-8)
    assert hybrid.forward(-angle) == pytest.approx(-hybrid.forward(angle))


def test_corrected_tegs_and_insight_use_distinct_transports_and_measured_r6():
  assert core.CIVIC_TEG_A010.e4_per_output == 3840
  assert core.INSIGHT_TXM_A040.e4_per_output == 4096
  assert core.CIVIC_TEG_A010 is not core.CIVIC_BOSCH_C020
  assert core.CIVIC_TEG_EPS_LOAD != core.CIVIC_EPS_LOAD


def test_copied_math_and_stock_pid_match_the_pinned_source_blobs():
  manifest = json.loads((ROOT / "openpilot/nrdr/PORT_MANIFEST.json").read_text())
  for path, expected in {**manifest["source_blobs"], **manifest["stock_blobs"]}.items():
    data = (ROOT / path).read_bytes().replace(b"\r\n", b"\n")
    digest = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    assert digest == expected, path


def test_comma_geometry_holds_last_valid_learner_ratio():
  family, profile = CASES[2]
  cp = cp_for(family[0], family[1].replace("-", ",", 1))
  controller = create_firmware_controller(cp, None, .01, settings_for(profile))
  controller.prepare_geometry(0., valid=False)
  assert controller.comma_ratio == cp.steerRatio
  controller.prepare_geometry(18., valid=True)
  for invalid in (0., -1., math.nan, math.inf):
    controller.prepare_geometry(invalid)
    assert controller.comma_ratio == 18.
  controller.prepare_geometry(19., valid=False)
  assert controller.comma_ratio == 18.
  assert controller.selection.ratio_at(0., controller.comma_ratio) == 18.
