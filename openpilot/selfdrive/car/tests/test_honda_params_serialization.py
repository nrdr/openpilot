"""Exercise Honda startup across the opendbc-to-cereal boundary used by card."""
from dataclasses import replace

import pytest

from opendbc.car import gen_empty_fingerprint, structs
from opendbc.car.honda.interface import CarInterface
from opendbc.car.honda.values import CAR
from opendbc.sunnypilot.car.interfaces import setup_interfaces
from opendbc.sunnypilot.car.tests.runtime_config import make_test_car_config
from openpilot.cereal import custom
from openpilot.selfdrive.car.helpers import convert_to_capnp


@pytest.mark.parametrize("car", [CAR.HONDA_CLARITY, CAR.HONDA_CIVIC])
@pytest.mark.parametrize("hybrid", [False, True])
@pytest.mark.parametrize("pedal_bytes", [None, 6, 8])
@pytest.mark.parametrize("stock_long", [False, True])
@pytest.mark.parametrize("live_gas", [False, True])
@pytest.mark.parametrize("clarity_brake", [False, True])
def test_honda_startup_parameters_serialize(car, hybrid, pedal_bytes, stock_long, live_gas, clarity_brake):
  config = make_test_car_config(honda_stock_longitudinal=stock_long)
  config = replace(config, honda=replace(config.honda, clarity_interceptor_brake_bench=clarity_brake,
                                        mvl_longitudinal=live_gas))
  config.honda.provider.live_tuning = replace(config.honda.provider.live_tuning, live_learning_gas=live_gas)
  fingerprint = gen_empty_fingerprint()
  if hybrid:
    fingerprint[0][0x184] = 8
  if pedal_bytes is not None:
    fingerprint[0][0x201] = pedal_bytes
  cp = CarInterface.get_params(car, fingerprint, [], True, False, False, config)
  cp_sp = CarInterface.get_params_sp(cp, car, fingerprint, [], True, False, False)
  setup_interfaces(CarInterface, cp, cp_sp, config)

  # IntFlag compares equal to int, so equality-only tests miss this startup
  # failure. The production message encoder requires the plain wire type.
  assert type(cp_sp.flags) is int
  message = convert_to_capnp(cp_sp)
  with custom.CarParamsSP.from_bytes(message.to_bytes()) as restored:
    assert restored.flags == cp_sp.flags
    assert restored.safetyParam == cp_sp.safetyParam
    assert restored.enableGasInterceptor == cp_sp.enableGasInterceptor


@pytest.mark.parametrize("alpha_long", [False, True])
@pytest.mark.parametrize("release", [False, True])
def test_modified_clarity_interceptor_camera_flags_round_trip(alpha_long, release):
  # Hardware/configuration combination from the reported startup failure.
  fingerprint = gen_empty_fingerprint()
  fingerprint[0].update({0x184: 8, 0x201: 6, 0x223: 8, 0x35E: 8})
  firmware = [structs.CarParams.CarFw(ecu="eps", fwVersion=b"39990-TRW,A020")]
  config = make_test_car_config(honda_stock_longitudinal=False)
  config = replace(config, honda=replace(config.honda, mvl_longitudinal=True, nidec_pcm_mode=0,
                                        nidec_wind_brake=True, clarity_interceptor_brake_bench=False))
  cp = CarInterface.get_params(CAR.HONDA_CLARITY, fingerprint, firmware, alpha_long, release, False, config)
  cp_sp = CarInterface.get_params_sp(cp, CAR.HONDA_CLARITY, fingerprint, firmware, alpha_long, release, False)
  setup_interfaces(CarInterface, cp, cp_sp, config)
  assert cp.openpilotLongitudinalControl and not cp.pcmCruise
  assert cp_sp.enableGasInterceptor and cp_sp.safetyParam == 3
  assert type(cp_sp.flags) is int and cp_sp.flags == 47
  with custom.CarParamsSP.from_bytes(convert_to_capnp(cp_sp).to_bytes()) as restored:
    assert restored.flags == 47 and restored.safetyParam == 3
