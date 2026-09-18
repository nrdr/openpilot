import pytest

from openpilot.cereal import custom, log
from opendbc.car.structs import car
from openpilot.selfdrive.selfdrived.events import ET, Events
from openpilot.sunnypilot.selfdrive.car.car_specific import CarSpecificEventsSP, GAS_INTERCEPTOR_STARTUP_GRACE_FRAMES


EventName = log.OnroadEvent.EventName


@pytest.mark.parametrize("interceptor_enabled,state,fault_expected", [
  (True, 0, False),
  (True, 1, True),
  (True, 2, True),
  (True, 3, True),
  (True, 6, True),
  (True, 15, True),
  (False, 5, False),
])
def test_gas_interceptor_fault_is_a_standard_controls_event(interceptor_enabled, state, fault_expected):
  CP = car.CarParams(brand="honda", carFingerprint="HONDA_CLARITY")
  CP_SP = custom.CarParamsSP(enableGasInterceptor=interceptor_enabled)
  CS = car.CarState(canValid=True)
  CS_SP = custom.CarStateSP(gasInterceptorState=state)
  events = Events()

  CarSpecificEventsSP(CP, CP_SP).update(CS, CS_SP, events)

  assert events.has(EventName.gasInterceptorFault) is fault_expected
  assert events.contains(ET.IMMEDIATE_DISABLE) is fault_expected
  assert events.contains(ET.NO_ENTRY) is fault_expected
  assert events.contains(ET.PERMANENT) is fault_expected


@pytest.mark.parametrize("state", [4, 5])
def test_gas_interceptor_bootstrap_allows_zero_command_without_visible_fault(state):
  CP = car.CarParams(brand="honda", carFingerprint="HONDA_CLARITY")
  CP_SP = custom.CarParamsSP(enableGasInterceptor=True)
  CS = car.CarState(canValid=True)
  CS_SP = custom.CarStateSP(gasInterceptorState=state)
  events = Events()

  CarSpecificEventsSP(CP, CP_SP).update(CS, CS_SP, events)

  assert not events.has(EventName.gasInterceptorFault)
  assert not events.has(EventName.selfdriveInitializing)
  assert not events.contains(ET.NO_ENTRY)
  assert not events.contains(ET.PERMANENT)


def test_gas_interceptor_observed_boot_timing_then_healthy_and_later_fault():
  CP = car.CarParams(brand="honda", carFingerprint="HONDA_CLARITY")
  CP_SP = custom.CarParamsSP(enableGasInterceptor=True)
  CS = car.CarState(canValid=True)
  events = Events()
  car_events = CarSpecificEventsSP(CP, CP_SP)

  # Longest observed boot took 5.31 seconds before the first healthy state.
  for _ in range(531):
    events.clear()
    car_events.update(CS, custom.CarStateSP(gasInterceptorState=5), events)
    assert not events.has(EventName.gasInterceptorFault)

  events.clear()
  car_events.update(CS, custom.CarStateSP(gasInterceptorState=0), events)
  assert not events.has(EventName.gasInterceptorFault)
  assert not events.has(EventName.selfdriveInitializing)

  events.clear()
  car_events.update(CS, custom.CarStateSP(gasInterceptorState=5), events)
  assert events.has(EventName.gasInterceptorFault)


def test_gas_interceptor_bootstrap_faults_on_early_enable_request():
  CP = car.CarParams(brand="honda", carFingerprint="HONDA_CLARITY")
  CP_SP = custom.CarParamsSP(enableGasInterceptor=True)
  CS = car.CarState(canValid=True)
  events = Events()
  events.add(EventName.buttonEnable)

  CarSpecificEventsSP(CP, CP_SP).update(CS, custom.CarStateSP(gasInterceptorState=5), events)

  assert events.has(EventName.gasInterceptorFault)


def test_gas_interceptor_invalid_default_zero_does_not_latch_healthy():
  CP = car.CarParams(brand="honda", carFingerprint="HONDA_CLARITY")
  CP_SP = custom.CarParamsSP(enableGasInterceptor=True)
  events = Events()
  car_events = CarSpecificEventsSP(CP, CP_SP)

  car_events.update(car.CarState(canValid=False), custom.CarStateSP(gasInterceptorState=0), events)
  assert not car_events.gas_interceptor_healthy

  events.clear()
  car_events.update(car.CarState(canValid=True), custom.CarStateSP(gasInterceptorState=5), events)
  assert not events.has(EventName.gasInterceptorFault)

  events.clear()
  car_events.update(car.CarState(canValid=True), custom.CarStateSP(gasInterceptorState=0), events)
  assert car_events.gas_interceptor_healthy

  events.clear()
  car_events.update(car.CarState(canValid=True), custom.CarStateSP(gasInterceptorState=5), events)
  assert events.has(EventName.gasInterceptorFault)


def test_gas_interceptor_bootstrap_faults_after_bounded_grace():
  CP = car.CarParams(brand="honda", carFingerprint="HONDA_CLARITY")
  CP_SP = custom.CarParamsSP(enableGasInterceptor=True)
  CS = car.CarState(canValid=True)
  CS_SP = custom.CarStateSP(gasInterceptorState=5)
  events = Events()
  car_events = CarSpecificEventsSP(CP, CP_SP)

  for _ in range(GAS_INTERCEPTOR_STARTUP_GRACE_FRAMES):
    events.clear()
    car_events.update(CS, CS_SP, events)
    assert not events.has(EventName.gasInterceptorFault)

  events.clear()
  car_events.update(CS, CS_SP, events)
  assert events.has(EventName.gasInterceptorFault)
