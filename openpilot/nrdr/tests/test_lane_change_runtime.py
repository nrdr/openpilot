"""Native-message integration tests for lane-change settings and command hooks."""
from types import SimpleNamespace

import pytest

from opendbc.car.structs import car
from opendbc.car.vehicle_model import VehicleModel as NativeVehicleModel
from openpilot.cereal import log
from openpilot.nrdr.features.driver_policy.lane_change import torque_from_lateral_accel
from openpilot.nrdr.features.lateral.lane_change_tuning import LaneChangeEntry, shape_lane_change_curvature
from openpilot.nrdr.features.lateral.steer_ratio_tuning import SteerRatioModeLatch, resolve_steer_ratio_selection
from openpilot.nrdr.hooks.controlsd import lane_change_request
from openpilot.nrdr.tests.test_lane_change_tuning import VehicleModel, selection
from openpilot.selfdrive.controls.lib import desire_helper


def test_native_enums_and_hook_vehicle_admission():
  model = log.ModelDataV2.new_message()
  model.meta.laneChangeState = 'laneChangeStarting'
  model.meta.laneChangeDirection = 'left'
  cs = car.CarState.new_message(steeringAngleDeg=15, vEgo=25)
  reports = []
  for brand in ('honda', 'toyota'):
    cp = SimpleNamespace(brand=brand, carFingerprint='HONDA_CLARITY' if brand == 'honda' else 'LEXUS_ES', steerRatio=16.5, carFw=[])
    snapshot = {'NrdrSteerRatioMode': 1, 'NrdrLaneChangeEntrySrReduction': 3.0}
    controls = SimpleNamespace(
      CP=cp, VM=VehicleModel(), nrdr_lateral_snapshot=snapshot, nrdr_lane_change_entry=LaneChangeEntry(),
      steer_ratio_latch=SteerRatioModeLatch(resolve_steer_ratio_selection(cp, snapshot)),
      sm=SimpleNamespace(valid={'lateralManeuverPlan': False}, all_checks=lambda services: True),
      nrdr_live_params=SimpleNamespace(record_applied_settings=lambda *args, **kw: reports.append(kw)),
    )
    outputs = [lane_change_request(controls, cs, model, SimpleNamespace(roll=0.0), 0.01, True, 0.01) for _ in range(15)]
    assert (outputs[-1] < 0.01) if brand == 'honda' else outputs == [0.01] * 15
    assert reports[-1]['supported'] == (brand == 'honda')
    assert reports[-1]['shaped_curvature'] <= reports[-1]['requested_curvature']
    controls.sm.all_checks = lambda services: False
    assert lane_change_request(controls, cs, model, SimpleNamespace(roll=0.0), 0.01, True, 0.01) == 0.01


@pytest.mark.parametrize('mode,hybrid', [(0, False), (1, False), (2, False), (3, False), (2, True), (1, True)])
@pytest.mark.parametrize('speed', (10.0, 25.0, 35.0))
@pytest.mark.parametrize('roll', (-0.06, 0.0, 0.06))
def test_native_vehicle_model_preserves_feedback_and_shapes_selected_geometry(mode, hybrid, speed, roll):
  cp = car.CarParams.new_message(mass=1840, rotationalInertia=3000, wheelbase=2.75,
                               centerToFront=1.08, steerRatioRear=0, steerRatio=19 if mode == 1 else 16.5,
                               tireStiffnessFront=200000, tireStiffnessRear=200000)
  vm = NativeVehicleModel(cp)
  selected = selection(mode, hybrid)
  for angle in (-30, -27.5, 0, 27.5, 30):
    before = selected.measured_curvature(vm, angle, speed, roll)
    ratio = vm.sR
    for curvature in (-0.005, -0.001, 0.0, 0.001, 0.005):
      assert shape_lane_change_curvature(selected, vm, angle, speed, roll, curvature, 0) == curvature
      shaped = shape_lane_change_curvature(selected, vm, angle, speed, roll, curvature, 3)
      assert min(0, curvature) <= shaped <= max(0, curvature)
      if curvature:
        assert abs(shaped) < abs(curvature)
      if mode == 1 and not hybrid:
        assert shaped == pytest.approx(curvature * 16 / 19)
      assert vm.sR == ratio
      assert selected.measured_curvature(vm, angle, speed, roll) == pytest.approx(before)


@pytest.mark.parametrize('duration', (0.5, 1.0, 2.0))
def test_minimum_state_time_uses_next_start_snapshot_and_preserves_model_completion_gate(monkeypatch, duration):
  reports = []
  live = SimpleNamespace(snapshot={'NrdrLaneChangeMinTime': duration}, generation=2,
                         record_applied_settings=lambda *args, **kw: reports.append(kw))
  monkeypatch.setattr(desire_helper, 'get_live_params', lambda profile: live)
  dh = desire_helper.DesireHelper()
  dh.alc.update_params = lambda: None
  dh.alc.lane_change_set_timer = 0
  dh.lane_turn_controller.update_params = lambda: None
  cs = car.CarState.new_message(vEgo=25, leftBlinker=True, steeringPressed=True, steeringTorque=1)
  dh.update(cs, True, 1.0)
  assert dh.lane_change_state == log.LaneChangeState.preLaneChange
  dh.update(cs, True, 1.0)
  assert dh.lane_change_state == log.LaneChangeState.laneChangeStarting
  assert reports[-1]['minimum_start_time'] == duration
  live.snapshot = {'NrdrLaneChangeMinTime': 0.5}
  # A saved edit cannot shorten a maneuver already in progress.
  for _ in range(round(duration / desire_helper.DT_MDL) - 1):
    dh.update(cs, True, 0.0)
    assert dh.lane_change_state == log.LaneChangeState.laneChangeStarting
  assert dh.lane_change_min_time == duration
  for _ in range(3):
    dh.update(cs, True, 1.0)
    assert dh.lane_change_state == log.LaneChangeState.laneChangeStarting
  dh.update(cs, True, 0.0)
  assert dh.lane_change_state == log.LaneChangeState.preLaneChange


def test_legacy_torque_factor_preserves_defaults_and_restores_params_even_on_failure():
  params = SimpleNamespace(latAccelFactor=4.0)
  def torque(accel, p):
    return accel / p.latAccelFactor
  assert torque_from_lateral_accel(torque, 2, params, False, {'NrdrLaneChangeTorqueFactor': 3}) == 0.5
  assert torque_from_lateral_accel(torque, 2, params, True) == 0.25
  assert torque_from_lateral_accel(torque, 2, params, True, {'NrdrLaneChangeTorqueFactor': 1}) == 0.5
  assert params.latAccelFactor == 4.0

  def fail(accel, p):
    raise ValueError('test failure')

  with pytest.raises(ValueError):
    torque_from_lateral_accel(fail, 2, params, True)
  assert params.latAccelFactor == 4.0
