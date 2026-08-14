from types import SimpleNamespace

import pytest

from opendbc.car import Bus, structs
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
