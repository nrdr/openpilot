import math
from types import SimpleNamespace

import numpy as np

from openpilot.common.test import OpenpilotTestCase
from openpilot.common.parameterized import parameterized

from openpilot.cereal import log
from opendbc.car.structs import car
from opendbc.car.car_helpers import interfaces
from opendbc.car.honda.values import CAR as HONDA
from opendbc.car.toyota.values import CAR as TOYOTA
from opendbc.car.nissan.values import CAR as NISSAN
from opendbc.car.gm.values import CAR as GM
from opendbc.car.vehicle_model import VehicleModel
from openpilot.common.realtime import DT_CTRL
from openpilot.selfdrive.controls.lib.latcontrol_pid import LatControlPID, _CIVIC_C020, _CIVIC_C120, _CURVES, _LatStiction
from openpilot.selfdrive.controls.lib.latcontrol_torque import LatControlTorque
from openpilot.selfdrive.controls.lib.latcontrol_angle import LatControlAngle


class TestLatControl(OpenpilotTestCase):

  @staticmethod
  def pid_controller(car_name=HONDA.HONDA_CLARITY, modified=True, fw=b"39990-TRW-A020"):
    tune = SimpleNamespace(pid=SimpleNamespace(kpBP=[0.], kpV=[0.1], kiBP=[0.], kiV=[0.], kf=0.01))
    car_fw = [SimpleNamespace(ecu="eps", fwVersion=fw.replace(b"-", b",", 1) if modified else fw)]
    CP = SimpleNamespace(steerLimitTimer=0.8, lateralTuning=tune, steerRatio=16.5,
                         carFingerprint=car_name, carFw=car_fw)
    CI = SimpleNamespace(get_steer_feedforward_function=lambda: lambda angle, speed: 1.0)
    return LatControlPID(CP, CI, DT_CTRL)

  @staticmethod
  def pid_inputs(v_ego=30.0, steering_angle=-1.0):
    CS = SimpleNamespace(vEgo=v_ego, steeringAngleDeg=steering_angle, steeringRateDeg=0.0, steeringPressed=False,
                         steeringTorque=0.0, leftBlinker=False, rightBlinker=False,
                         steerFaultTemporary=False, steerFaultPermanent=False)
    VM = SimpleNamespace(sR=18.5, get_steer_from_curvature=lambda curvature, speed, roll: curvature)
    params = SimpleNamespace(roll=0.0, angleOffsetDeg=0.0)
    return CS, VM, params

  @parameterized.expand([(HONDA.HONDA_CIVIC, LatControlPID), (TOYOTA.TOYOTA_RAV4, LatControlTorque),
                         (NISSAN.NISSAN_LEAF, LatControlAngle), (GM.CHEVROLET_BOLT_EUV, LatControlTorque)])
  def test_saturation(self, car_name, controller):
    CarInterface = interfaces[car_name]
    CP = CarInterface.get_non_essential_params(car_name)
    CI = CarInterface(CP)
    VM = VehicleModel(CP)

    controller = controller(CP.as_reader(), CI, DT_CTRL)

    CS = car.CarState.new_message()
    CS.vEgo = 30
    CS.steeringPressed = False

    params = log.VehicleParameters.new_message()

    # Saturate for curvature limited and controller limited
    for _ in range(1000):
      _, _, lac_log = controller.update(True, CS, VM, params, False, 0, True, 0.2)
    assert lac_log.saturated

    for _ in range(1000):
      _, _, lac_log = controller.update(True, CS, VM, params, False, 0, False, 0.2)
    assert not lac_log.saturated

    for _ in range(1000):
      _, _, lac_log = controller.update(True, CS, VM, params, False, 1, False, 0.2)
    assert lac_log.saturated

  def test_honda_fixed_steering_curves(self):
    curves = [
      (_CURVES[HONDA.HONDA_CLARITY], (59.570751, 76.770346, 82.599905, 104.350769)),
      (_CIVIC_C120, (59.684930, 76.546436, 81.663266, 100.779317)),
      (_CIVIC_C020, (58.875419, 76.102489, 81.495405, 100.779317)),
      (_CURVES[HONDA.HONDA_CRV_5G], (58.270013, 75.745112, 82.018583, 103.616196)),
      (_CURVES[HONDA.HONDA_INSIGHT], (57.911805, 75.628947, 83.301413, 107.642051)),
      (_CURVES[HONDA.HONDA_ACCORD], (55.089501, 71.502052, 79.385722, 101.843927)),
      (_CURVES[HONDA.HONDA_CIVIC_BOSCH_DIESEL], (54.776499, 70.975658, 78.737376, 100.779317)),
    ]
    for (x, y), expected in curves:
      assert len(x) == len(y)
      assert np.all(np.diff(x) > 0.0) and np.all(np.diff(y) > 0.0)
      np.testing.assert_allclose(np.interp((60, 80, 90, 120), x, y), expected, atol=0.02)
      np.testing.assert_allclose(-np.interp((60, 80, 90, 120), x, y), -np.asarray(expected), atol=0.02)

  def test_honda_curve_selection_and_lane_change(self):
    c120 = self.pid_controller(HONDA.HONDA_CIVIC_BOSCH, fw=b"39990-TBA-C120")
    c020 = self.pid_controller(HONDA.HONDA_CIVIC_BOSCH, fw=b"39990-TBA-C020")
    assert c120.angle_curve is _CIVIC_C120
    assert c020.angle_curve is _CIVIC_C020

    controller = self.pid_controller()
    CS, VM, params = self.pid_inputs(steering_angle=400.0)
    _, mapped, _ = controller.update(False, CS, VM, params, False, -math.radians(120.0), False, 0.1)
    CS.steeringAngleDeg = -400.0
    _, mapped_again, _ = controller.update(False, CS, VM, params, False, -math.radians(120.0), False, 0.1)
    assert mapped == mapped_again
    assert np.isclose(mapped, np.interp(120.0, *_CURVES[HONDA.HONDA_CLARITY]))
    controller.lane_changing = True
    _, lane_change, _ = controller.update(False, CS, VM, params, False, -math.radians(120.0), False, 0.1)
    assert np.isclose(lane_change, 120.0 * 12.72 / 18.5)

  def test_center_boost_and_feedforward(self):
    controller = self.pid_controller()
    CS, VM, params = self.pid_inputs()
    output, _, log = controller.update(True, CS, VM, params, False, 0.0, False, 0.1)
    assert np.isclose(output, 2.0 * log.p + log.f)
    assert np.isclose(log.f, np.interp(CS.vEgo, (0.0, 11.175, 11.176, 22.352), (2.4e-6, 1.8e-6, 3.6e-6, 6e-6)))

    controller = self.pid_controller()
    CS.leftBlinker = True
    output, _, log = controller.update(True, CS, VM, params, False, 0.0, False, 0.1)
    assert np.isclose(output, log.p + log.f)

  def test_predictive_stiction_capture_hold_and_release(self):
    stiction = _LatStiction(DT_CTRL)
    first = stiction.update(True, 0.0, 1.0, 0.0, 30.0, 0.5, False, False, False)
    assert stiction.state == stiction.CAPTURE and first == 0.5
    for _ in range(8):
      captured = stiction.update(True, 0.0, 1.0, 0.0, 30.0, 0.5, False, False, False)
    assert 0.25 <= captured < 0.5

    for _ in range(80):
      held = stiction.update(True, 0.0, 0.1, 0.0, 0.0, 0.3, False, False, False)
      if stiction.state == stiction.HOLD:
        break
    assert stiction.state == stiction.HOLD
    assert stiction.update(True, 0.0, 0.1, 0.0, 0.0, 0.7, False, False, False) == held
    assert stiction.update(True, 0.0, -0.1, 0.0, 0.0, -0.1, False, False, False) == -0.1
    assert stiction.state == stiction.TRACK

  def test_predictive_stiction_gates_and_zero_speed(self):
    for gate in ((False, False, True), (False, True, False), (True, False, False)):
      stiction = _LatStiction(DT_CTRL)
      output = stiction.update(True, 0.0, 1.0, 0.0, 30.0, 0.5, *gate)
      assert output == 0.5 and stiction.state == stiction.TRACK

    stiction = _LatStiction(DT_CTRL)
    stiction._enter(stiction.REACQUIRE, 0.2)
    assert stiction.update(True, 0.0, 0.1, 0.0, 0.0, -0.3, False, False, False) == -0.3
    assert stiction.state == stiction.TRACK
