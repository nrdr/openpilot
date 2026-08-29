from types import SimpleNamespace

import pytest

from opendbc.car import Bus, structs
from opendbc.car.honda.values import CAR, HONDA_GAS_INTERCEPTOR_THRESHOLD_512
from opendbc.sunnypilot.car.honda.carstate_ext import CarStateExt


@pytest.mark.parametrize("state", [0, 1, 5, 15])
def test_gas_interceptor_state_is_forwarded_exactly(state):
  CP = SimpleNamespace(carFingerprint="HONDA_CLARITY")
  CP_SP = SimpleNamespace(flags=0, enableGasInterceptor=True)
  parser = SimpleNamespace(vl={"GAS_SENSOR": {
    "INTERCEPTOR_GAS": 300,
    "INTERCEPTOR_GAS2": 300,
    "STATE": state,
  }})
  can_parsers = {Bus.pt: parser, Bus.cam: SimpleNamespace(vl={})}
  ret = structs.CarState()
  ret_sp = structs.CarStateSP()

  CarStateExt(CP, CP_SP).update(ret, ret_sp, can_parsers)

  assert ret_sp.gasInterceptorState == state
  assert not ret.gasPressed


@pytest.mark.parametrize("car_fingerprint", HONDA_GAS_INTERCEPTOR_THRESHOLD_512)
@pytest.mark.parametrize("gas,gas_pressed", [(492, False), (493, False), (512, False), (513, True)])
def test_noisy_vehicle_gas_pressed_threshold_is_512(car_fingerprint, gas, gas_pressed):
  CP = SimpleNamespace(carFingerprint=car_fingerprint)
  CP_SP = SimpleNamespace(flags=0, enableGasInterceptor=True)
  parser = SimpleNamespace(vl={"GAS_SENSOR": {
    "INTERCEPTOR_GAS": gas,
    "INTERCEPTOR_GAS2": gas,
    "STATE": 0,
  }})
  can_parsers = {Bus.pt: parser, Bus.cam: SimpleNamespace(vl={})}
  ret = structs.CarState()

  CarStateExt(CP, CP_SP).update(ret, structs.CarStateSP(), can_parsers)

  assert ret.gasPressed is gas_pressed


@pytest.mark.parametrize("gas,gas_pressed", [(492, False), (493, True), (512, True)])
def test_other_hondas_keep_standard_gas_pressed_threshold(gas, gas_pressed):
  CP = SimpleNamespace(carFingerprint=CAR.HONDA_CLARITY)
  CP_SP = SimpleNamespace(flags=0, enableGasInterceptor=True)
  parser = SimpleNamespace(vl={"GAS_SENSOR": {
    "INTERCEPTOR_GAS": gas,
    "INTERCEPTOR_GAS2": gas,
    "STATE": 0,
  }})
  can_parsers = {Bus.pt: parser, Bus.cam: SimpleNamespace(vl={})}
  ret = structs.CarState()

  CarStateExt(CP, CP_SP).update(ret, structs.CarStateSP(), can_parsers)

  assert ret.gasPressed is gas_pressed
