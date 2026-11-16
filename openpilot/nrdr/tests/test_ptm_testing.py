"""Opt-in PTM Testing admission, baseline parity and independent controller state."""
import ast
import math
from pathlib import Path
import sys
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
      outputs.append((output, target, telemetry.to_dict()))
    assert outputs[0] == outputs[1]
  original = baseline.core.output_lpf_enabled
  testing.core.output_lpf_enabled = not original
  assert baseline.core.output_lpf_enabled == original


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
