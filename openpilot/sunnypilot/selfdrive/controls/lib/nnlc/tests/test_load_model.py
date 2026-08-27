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
from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.selfdrive.car.opendbc_config import build_sunnypilot_car_config


class TestNNTorqueModel(OpenpilotTestCase):

  @parameterized.expand([HONDA.HONDA_CIVIC, TOYOTA.TOYOTA_RAV4, HYUNDAI.HYUNDAI_SANTA_CRUZ_1ST_GEN])
  def test_load_model(self, car_name):
    params = Params()
    params.put_bool("NeuralNetworkLateralControl", True, block=True)

    CarInterface = interfaces[car_name]
    interface_config = build_sunnypilot_car_config(params, start_worker=False)
    CP = CarInterface.get_non_essential_params(car_name, interface_config)
    CP_SP = CarInterface.get_non_essential_params_sp(CP, car_name)
    CI = CarInterface(CP, CP_SP, interface_config)

    sunnypilot_interfaces.setup_interfaces(CI, params)

    CP_SP = convert_to_capnp(CP_SP)

    controller = LatControlTorque(CP.as_reader(), CP_SP.as_reader(), CI, DT_CTRL)

    assert controller.extension.has_nn_model
