"""Exercise the production VFN wrapper, without CAN or device settings writes."""
import math
from types import SimpleNamespace

import pytest

from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.nrdr.features.lateral.latcontrol_vfn_eps import LatControlVfnEps
from openpilot.nrdr.params.snapshots import ParamSnapshot


def car(fingerprint="HONDA_CLARITY", firmware=b"39990-TRW-A020", modified=True):
  cp = SimpleNamespace(brand="honda", carFingerprint=fingerprint, steerRatio=16.5,
                       wheelbase=2.75, steerLimitTimer=.8,
                       carFw=[SimpleNamespace(ecu="eps", fwVersion=firmware)],
                       lateralTuning=SimpleNamespace(which=lambda: "pid"))
  return cp, SimpleNamespace(flags=HondaFlagsSP.EPS_MODIFIED.value if modified else 0)


def controller(**changes):
  cp, sp = car(**changes)
  return LatControlVfnEps(cp, sp, None, .01)


def tick(control, *, active=True, state=0, angle=20., speed=15., desired=20.):
  control.update_model_v2(SimpleNamespace(meta=SimpleNamespace(laneChangeState=SimpleNamespace(raw=state))))
  cs = SimpleNamespace(vEgo=speed, steeringAngleDeg=angle, steeringRateDeg=0.,
                       steeringPressed=False, steeringTorque=0.)
  curvature = control.rack_map.curvature_from_angle(desired, speed, 0.)
  return control.update(active, cs, None, SimpleNamespace(roll=0., angleOffsetDeg=0.),
                        False, curvature, None, False, .2)


@pytest.mark.parametrize("changes", [dict(fingerprint="HONDA_CIVIC"), dict(firmware=b"39990-TRW-A010"), dict(modified=False)])
def test_wrong_platform_or_eps_cannot_select_vfn(changes):
  with pytest.raises(ValueError):
    controller(**changes)


@pytest.mark.parametrize("state", [2, 3])
def test_lane_change_suppresses_wrapper_feedforward_and_rejoins(state):
  control = controller()
  for _ in range(100):
    tick(control)
  assert control.core.ff_weight == 1.
  for _ in range(60):
    output, _, logged = tick(control, state=state)
    assert control.core.ff_weight == 0.
    assert logged.f == 0.
    assert math.isfinite(output) and abs(output) <= 1.
  tick(control)
  assert 0. < control.core.ff_weight < .1


def test_disabled_optimization_and_waiting_for_nudge_keep_feedforward():
  control = controller()
  control.set_live_tuning_snapshot(ParamSnapshot(1, {"NrdrOptimizedLaneChanges": False}))
  for _ in range(100):
    tick(control, state=2)
  assert control.core.ff_weight == 1.
  control.set_live_tuning_snapshot(ParamSnapshot(2, {"NrdrOptimizedLaneChanges": True}))
  tick(control, state=1)
  assert control.core.ff_weight == 1.


def test_custom_pif_geometry_and_filter_settings_do_not_retune_vfn():
  baseline, custom = controller(), controller()
  custom.set_live_tuning_snapshot(ParamSnapshot(1, {
    "LatPScale": 500, "LatIScale": 0, "LatFScale": 0,
    "NrdrLatRateDampingStandard": 300, "NrdrTorqueOutputLowPass": False,
    "NrdrSteerRatioMode": 0, "NrdrSteerRatioManualCenter": 25.,
  }))
  for frame in range(150):
    desired = 20. + math.sin(frame / 20.)
    assert tick(custom, desired=desired)[0] == pytest.approx(tick(baseline, desired=desired)[0])


def test_inactive_control_resets_and_reengagement_limits_requested_angle_rate():
  control = controller()
  for _ in range(100):
    tick(control)
  output, previous, logged = tick(control, active=False)
  assert output == 0. and not logged.active
  assert control.core.pid.i == 0. and control.core.output == 0.
  _, requested, _ = tick(control, desired=100.)
  assert requested - previous == pytest.approx(3.)


@pytest.mark.parametrize("curvature", [-.01, -.001, .001, .01])
def test_lane_change_shaping_reduces_request_without_reversing_it(curvature):
  control = controller()
  shaped = control.shape_lane_change_request(15., 15., .01, curvature, 5.)
  assert min(0., curvature) <= shaped <= max(0., curvature)
  assert abs(shaped) < abs(curvature)
