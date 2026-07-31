import pytest

from openpilot.cereal import car, custom, log
from openpilot.selfdrive.selfdrived.events import ET, Events
from openpilot.sunnypilot.selfdrive.car.car_specific import CarSpecificEventsSP


EventName = log.OnroadEvent.EventName


@pytest.mark.parametrize("interceptor_enabled,state,fault_expected", [
  (True, 0, False),
  (True, 1, True),
  (True, 5, True),
  (False, 5, False),
])
def test_gas_interceptor_fault_is_a_standard_controls_event(interceptor_enabled, state, fault_expected):
  CP = car.CarParams(brand="honda", carFingerprint="HONDA_CLARITY")
  CP_SP = custom.CarParamsSP(enableGasInterceptor=interceptor_enabled)
  CS = car.CarState()
  CS_SP = custom.CarStateSP(gasInterceptorState=state)
  events = Events()

  CarSpecificEventsSP(CP, CP_SP).update(CS, CS_SP, events)

  assert events.has(EventName.gasInterceptorFault) is fault_expected
  assert events.contains(ET.IMMEDIATE_DISABLE) is fault_expected
  assert events.contains(ET.NO_ENTRY) is fault_expected
  assert events.contains(ET.PERMANENT) is fault_expected
