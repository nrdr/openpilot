import hashlib
from pathlib import Path

import pytest

from openpilot.cereal import log
from opendbc.car.car_helpers import interfaces
from opendbc.car.structs import CarParams, car
from opendbc.car.honda.values import CAR as HONDA
from opendbc.car.hyundai.values import CAR as HYUNDAI
from opendbc.car.toyota.values import CAR as TOYOTA
from opendbc.car.vehicle_model import VehicleModel
from openpilot.common.constants import CV
from openpilot.common.parameterized import parameterized
from openpilot.common.params import Params
from openpilot.common.realtime import DT_CTRL
from openpilot.selfdrive.car.helpers import convert_to_capnp
from openpilot.selfdrive.controls.lib.latcontrol_torque import LatControlTorque
from openpilot.sunnypilot.selfdrive.car import interfaces as sunnypilot_interfaces
from openpilot.sunnypilot.selfdrive.controls.controlsd_ext import ControlsExt
from openpilot.sunnypilot.nrdr.latcontrol_clarity_hybrid import LatControlClarityHybrid, clarity_nnlc_blend_target
from openpilot.sunnypilot.nrdr.live_params import reset_live_params_for_tests
from openpilot.sunnypilot.nrdr.nnlc_model import get_forced_nnlc_model
from openpilot.sunnypilot.selfdrive.controls.lib.latcontrol_torque_v0 import LatControlTorque as LatControlTorqueV0


CLARITY_MODEL_SHA256 = "4f2e92c085c5eeebb7c6714e4733ea7b71c1e69c7de7776a2bff6def12ce0134"


@pytest.fixture(autouse=True)
def reset_live_params():
  reset_live_params_for_tests()
  yield
  reset_live_params_for_tests()


class TestNNTorqueModel:

  @parameterized.expand([HONDA.HONDA_CIVIC, TOYOTA.TOYOTA_RAV4, HYUNDAI.HYUNDAI_SANTA_CRUZ_1ST_GEN])
  def test_load_model(self, car_name):
    params = Params()
    params.put_bool("NeuralNetworkLateralControl", True, block=True)

    CarInterface = interfaces[car_name]
    CP = CarInterface.get_non_essential_params(car_name)
    CP_SP = CarInterface.get_non_essential_params_sp(CP, car_name)
    CI = CarInterface(CP, CP_SP)

    sunnypilot_interfaces.setup_interfaces(CI, params)

    CP_SP = convert_to_capnp(CP_SP)

    controller = LatControlTorque(CP.as_reader(), CP_SP.as_reader(), CI, DT_CTRL)

    assert controller.extension.has_nn_model

  def test_clarity_forces_torque_and_exact_nnlc_model_with_global_toggles_off(self):
    params = Params()
    keys = ("EnforceTorqueControl", "NeuralNetworkLateralControl", "NrdrNnlcEnabled",
            "NrdrNnlcActivationSpeed", "NrdrNnlcKpGain", "NrdrNnlcKfGain", "NrdrNnlcKiGain",
            "NrdrLegacyDualBpSteerRatio")
    previous = {key: params.get(key) for key in keys}
    try:
      params.put_bool("EnforceTorqueControl", False, block=True)
      params.put_bool("NeuralNetworkLateralControl", False, block=True)
      params.put_bool("NrdrNnlcEnabled", True, block=True)
      params.put("NrdrNnlcActivationSpeed", 30, block=True)
      params.put("NrdrNnlcKpGain", 100, block=True)
      params.put("NrdrNnlcKfGain", 50, block=True)
      params.put("NrdrNnlcKiGain", 10, block=True)
      params.put_bool("NrdrLegacyDualBpSteerRatio", True, block=True)

      CarInterface = interfaces[HONDA.HONDA_CLARITY]
      CP = CarInterface.get_non_essential_params(HONDA.HONDA_CLARITY)
      CP.carFw = [CarParams.CarFw(ecu=CarParams.Ecu.eps, fwVersion=b"39990-TRW-A020")]
      CP_SP = CarInterface.get_non_essential_params_sp(CP, HONDA.HONDA_CLARITY)
      CI = CarInterface(CP, CP_SP)
      sunnypilot_interfaces.setup_interfaces(CI, params)

      assert CP.lateralTuning.which() == "torque"
      assert CP_SP.neuralNetworkLateralControl.model.name == "HONDA_CLARITY"
      assert not CP_SP.neuralNetworkLateralControl.fuzzyFingerprint
      model_path = Path(CP_SP.neuralNetworkLateralControl.model.path)
      assert model_path == Path(get_forced_nnlc_model(CP))
      assert hashlib.sha256(model_path.read_bytes()).hexdigest() == CLARITY_MODEL_SHA256

      controls_ext = ControlsExt.__new__(ControlsExt)
      controls_ext.CP = CP.as_reader()
      controls_ext.CP_SP = convert_to_capnp(CP_SP).as_reader()
      controls_ext.params = params
      controller = controls_ext.initialize_lateral_control(object(), CI, DT_CTRL)

      assert isinstance(controller, LatControlClarityHybrid)
      assert isinstance(controller.torque_controller, LatControlTorqueV0)
      pid_controller = controller.pid_controller.nrdr_controller
      assert pid_controller is not None
      assert pid_controller.sr_profile is not None
      assert pid_controller.vgr_profile is not None
      assert pid_controller.vgr_profile.name == "Clarity TRW-A020"
      assert len(pid_controller.pid._k_p[0]) == len(pid_controller.pid._k_p[1]) == 4
      assert len(pid_controller.pid._k_i[0]) == len(pid_controller.pid._k_i[1]) == 4
      low_max = 25.0 * CV.MPH_TO_MS
      assert all(abs(a - b) < 1e-6 for a, b in zip(pid_controller.pid._k_p[0],
                                                     [0.0, low_max - 1e-3, low_max, 50.0 * CV.MPH_TO_MS], strict=True))
      assert all(abs(a - b) < 1e-6 for a, b in zip(pid_controller.pid._k_p[1],
                                                     [0.018, 0.024, 0.048, 0.060], strict=True))
      assert all(abs(a - b) < 1e-6 for a, b in zip(pid_controller.pid._k_i[0],
                                                     [0.0, low_max - 1e-3, low_max, 50.0 * CV.MPH_TO_MS], strict=True))
      assert all(abs(a - b) < 1e-6 for a, b in zip(pid_controller.pid._k_i[1],
                                                     [0.006, 0.008, 0.016, 0.020], strict=True))
      assert all(abs(a - b) < 1e-6 for a, b in zip(pid_controller.kf_bp,
                                                     [0.0, low_max - 1e-3, low_max, 50.0 * CV.MPH_TO_MS], strict=True))
      assert all(abs(a - b) < 1e-12 for a, b in zip(pid_controller.kf_v,
                                                      [2.4e-6, 1.8e-6, 3.6e-6, 6.0e-6], strict=True))
      assert controller.extension.enabled
      assert controller.extension.has_nn_model
      assert abs(controller.extension.activation_speed_mps - 30.0 * CV.MPH_TO_MS) < 1e-6
      assert controller.extension._pid.k_p == 1.0
      assert controller.extension._pid.k_f == 0.5
      assert controller.extension._pid.k_i == 0.1
      controller.torque_controller.extension.model_valid = True
      assert controller.extension._nnlc_enabled

      # All new Sunnylink/device controls are live; refreshing them must not require
      # reconstructing the controller or resetting either integrator.
      params.put("NrdrNnlcActivationSpeed", 50, block=True)
      params.put("NrdrNnlcKpGain", 125, block=True)
      params.put("NrdrNnlcKfGain", 60, block=True)
      params.put("NrdrNnlcKiGain", 15, block=True)
      controller.extension.nrdr.params.refresh_all()
      controller.extension.nrdr.refresh()
      assert abs(controller.extension.activation_speed_mps - 50.0 * CV.MPH_TO_MS) < 1e-6
      assert controller.extension._pid.k_p == 1.25
      assert controller.extension._pid.k_f == 0.6
      assert controller.extension._pid.k_i == 0.15
      controller.extension._pid.i = 0.2
      params.put_bool("NrdrNnlcEnabled", False, block=True)
      controller.extension.nrdr.params.refresh_all()
      controller.extension.nrdr.refresh()
      assert not controller.extension.enabled
      assert controller.extension._pid.i == 0.0
      params.put_bool("NrdrNnlcEnabled", True, block=True)
      controller.extension.nrdr.params.refresh_all()
      controller.extension.nrdr.refresh()
      assert controller.extension.enabled

      # PID runs first even while Torque/NNLC is the serialized tuning type, so
      # its Clarity endpoint curve is also used for NNLC's actual-curvature measurement.
      CS = car.CarState.new_message()
      CS.steeringAngleDeg = 100.0
      VM = VehicleModel(CP)
      vehicle_params = log.VehicleParameters.new_message()
      controller.update(False, CS, VM, vehicle_params, False, 0.0, None, False, 0.2)
      assert abs(VM.sR - 16.188) < 1e-6

      # Exercise the real PID interpolation while active. The hybrid previously
      # passed this test only because inactive control never called PIDController.update().
      controller.torque_controller.extension.model_valid = False
      controller.torque_controller.update = lambda *_args, **_kwargs: (_ for _ in ()).throw(
        AssertionError("disabled NNLC ran the torque controller")
      )
      CS.vEgo = 10.0 * CV.MPH_TO_MS
      controller.update(True, CS, VM, vehicle_params, False, 0.0, None, False, 0.2)

      # Firmware EPS mode is PID-only until NNLC can dewarp both position and rate coordinates.
      params.put_bool("NrdrLegacyDualBpSteerRatio", False, block=True)
      pid_controller.params.refresh_all()
      pid_controller._refresh_settings()
      assert pid_controller.firmware_vgr_selected
      controller.nnlc_blend = 1.0
      controller.extension._pid.i = 0.2
      VM.sR = 17.123
      controller.update(True, CS, VM, vehicle_params, False, 0.0, None, False, 0.2)
      assert controller.nnlc_blend == 0.0
      assert controller.extension._pid.i == 0.0
      assert VM.sR == 17.123
    finally:
      for key, value in previous.items():
        if value is None:
          params.remove(key)
        else:
          params.put(key, value, block=True)
  def test_clarity_hybrid_speed_and_lane_change_policy(self):
    assert clarity_nnlc_blend_target(26.0 * CV.MPH_TO_MS, log.LaneChangeState.off) == 0.0
    assert abs(clarity_nnlc_blend_target(30.0 * CV.MPH_TO_MS, log.LaneChangeState.off) - 0.5) < 1e-6
    assert clarity_nnlc_blend_target(34.0 * CV.MPH_TO_MS, log.LaneChangeState.off) == 1.0
    assert clarity_nnlc_blend_target(46.0 * CV.MPH_TO_MS, log.LaneChangeState.off, 50.0 * CV.MPH_TO_MS) == 0.0
    assert abs(clarity_nnlc_blend_target(50.0 * CV.MPH_TO_MS, log.LaneChangeState.off,
                                         50.0 * CV.MPH_TO_MS) - 0.5) < 1e-6
    assert clarity_nnlc_blend_target(54.0 * CV.MPH_TO_MS, log.LaneChangeState.off, 50.0 * CV.MPH_TO_MS) == 1.0

    for lane_change_state in (log.LaneChangeState.preLaneChange, log.LaneChangeState.laneChangeStarting,
                              log.LaneChangeState.laneChangeFinishing):
      assert clarity_nnlc_blend_target(70.0 * CV.MPH_TO_MS, lane_change_state) == 0.0

    controller = LatControlClarityHybrid.__new__(LatControlClarityHybrid)
    controller.dt = DT_CTRL
    controller.nnlc_blend = 1.0
    assert controller._update_blend(True, 0.0, log.LaneChangeState.preLaneChange) == 0.0

  def test_hidden_global_toggles_do_not_force_other_hondas(self):
    params = Params()
    previous = {key: params.get(key) for key in ("EnforceTorqueControl", "NeuralNetworkLateralControl")}
    try:
      params.put_bool("EnforceTorqueControl", False, block=True)
      params.put_bool("NeuralNetworkLateralControl", False, block=True)

      CarInterface = interfaces[HONDA.HONDA_CIVIC]
      CP = CarInterface.get_non_essential_params(HONDA.HONDA_CIVIC)
      CP_SP = CarInterface.get_non_essential_params_sp(CP, HONDA.HONDA_CIVIC)
      CI = CarInterface(CP, CP_SP)
      sunnypilot_interfaces.setup_interfaces(CI, params)

      assert CP.lateralTuning.which() == "pid"
    finally:
      for key, value in previous.items():
        if value is None:
          params.remove(key)
        else:
          params.put(key, value, block=True)
