import hashlib
from pathlib import Path

from opendbc.car.car_helpers import interfaces
from opendbc.car.honda.values import CAR as HONDA
from opendbc.car.hyundai.values import CAR as HYUNDAI
from opendbc.car.toyota.values import CAR as TOYOTA
from openpilot.common.parameterized import parameterized
from openpilot.common.params import Params
from openpilot.common.realtime import DT_CTRL
from openpilot.selfdrive.car.helpers import convert_to_capnp
from openpilot.selfdrive.controls.lib.latcontrol_torque import LatControlTorque
from openpilot.sunnypilot.selfdrive.car import interfaces as sunnypilot_interfaces
from openpilot.sunnypilot.selfdrive.controls.controlsd_ext import ControlsExt
from openpilot.sunnypilot.selfdrive.controls.lib.latcontrol_torque_v0 import LatControlTorque as LatControlTorqueV0
from openpilot.sunnypilot.selfdrive.controls.lib.nnlc.helpers import NRDR_TORQUE_NN_MODEL_PATH


CLARITY_MODEL_SHA256 = "4f2e92c085c5eeebb7c6714e4733ea7b71c1e69c7de7776a2bff6def12ce0134"


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
    previous = {key: params.get(key) for key in ("EnforceTorqueControl", "NeuralNetworkLateralControl")}
    try:
      params.put_bool("EnforceTorqueControl", False, block=True)
      params.put_bool("NeuralNetworkLateralControl", False, block=True)

      CarInterface = interfaces[HONDA.HONDA_CLARITY]
      CP = CarInterface.get_non_essential_params(HONDA.HONDA_CLARITY)
      CP_SP = CarInterface.get_non_essential_params_sp(CP, HONDA.HONDA_CLARITY)
      CI = CarInterface(CP, CP_SP)
      sunnypilot_interfaces.setup_interfaces(CI, params)

      assert CP.lateralTuning.which() == "torque"
      assert CP_SP.neuralNetworkLateralControl.model.name == "HONDA_CLARITY"
      assert not CP_SP.neuralNetworkLateralControl.fuzzyFingerprint
      model_path = Path(CP_SP.neuralNetworkLateralControl.model.path)
      assert model_path == Path(NRDR_TORQUE_NN_MODEL_PATH) / "HONDA_CLARITY.json"
      assert hashlib.sha256(model_path.read_bytes()).hexdigest() == CLARITY_MODEL_SHA256

      controls_ext = ControlsExt.__new__(ControlsExt)
      controls_ext.CP = CP.as_reader()
      controls_ext.CP_SP = convert_to_capnp(CP_SP).as_reader()
      controls_ext.params = params
      controller = controls_ext.initialize_lateral_control(object(), CI, DT_CTRL)

      assert isinstance(controller, LatControlTorqueV0)
      assert controller.extension.enabled
      assert controller.extension.has_nn_model
      controller.extension.model_valid = True
      assert controller.extension._nnlc_enabled
    finally:
      for key, value in previous.items():
        if value is None:
          params.remove(key)
        else:
          params.put(key, value, block=True)

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
