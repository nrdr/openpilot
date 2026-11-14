"""Exercise the merged controller with real packing, without any vehicle I/O."""
from copy import deepcopy
from dataclasses import replace

import pytest

from opendbc.can import CANPacker, CANParser
from opendbc.car import Bus, structs
from opendbc.car.honda.interface import CarInterface
from opendbc.car.honda.values import CAR, DBC
from opendbc.sunnypilot.car.tests.runtime_config import make_test_car_config


def interface(*, interceptor=False, learning=False):
  config = make_test_car_config()
  config.honda.provider.live_tuning = replace(config.honda.provider.live_tuning, live_learning_gas=learning)
  fingerprint = {i: {} for i in range(7)}
  if interceptor:
    fingerprint[0][0x201] = 6
  cp = CarInterface.get_params(CAR.HONDA_CLARITY, fingerprint, [], alpha_long=True, is_release=False, docs=False, interface_config=config)
  sp = CarInterface.get_params_sp(cp, CAR.HONDA_CLARITY, fingerprint, [], alpha_long=True, is_release_sp=False, docs=False)
  ci = CarInterface(cp, sp, config)
  ci.update([])
  ci.CS.out.vEgo = 12.0
  ci.CS.out.aEgo = 0.0
  ci.CS.out.cruiseState.speed = 25.0
  ci.CS.out.cruiseState.available = True
  ci.CS.out.standstill = False
  ci.CS.steer_control_active = True
  return ci, config.honda.provider


def learned_state(controller):
  return deepcopy({name: getattr(controller, name) for name in (
    "gas_factors", "gas_alphas", "speed_factors", "speed_alphas", "windfactor",
    "average_factor", "car_gas_per_pcm_gas", "sat_accel", "dv_launch", "gas_launch", "dv_break",
  )})


@pytest.mark.parametrize("interceptor", [False, True])
def test_merged_controller_emits_brake_and_correct_gas_channel(interceptor):
  ci, _ = interface(interceptor=interceptor)
  assert ci.CP_SP.enableGasInterceptor == interceptor
  cc = structs.CarControl(enabled=True, longActive=True, latActive=True)
  cc.actuators.accel = 0.5
  cc.actuators.torque = 0.2
  cc.actuators.longControlState = structs.CarControl.Actuators.LongControlState.pid
  emitted = set()
  for tick in range(100):
    out, messages = ci.apply(cc.as_reader(), structs.CarControlSP(), tick * 10_000_000)
    emitted.update(addr for addr, _, _ in messages)
    assert abs(out.torque) <= 1
    assert out.torqueOutputCan != ci.CC.average_factor
  assert 0x1FA in emitted  # BRAKE_COMMAND must survive the interceptor merge too
  assert (0x200 in emitted) == interceptor
  assert 0x30C in emitted  # ACC_HUD / wire gas path


@pytest.mark.parametrize("learning", [False, True])
def test_wire_gas_learning_obeys_switch(learning):
  ci, provider = interface(learning=learning)
  before = learned_state(ci.CC)
  cc = structs.CarControl(enabled=True, longActive=True)
  cc.actuators.accel = 0.8
  cc.actuators.longControlState = structs.CarControl.Actuators.LongControlState.pid
  for tick in range(500):
    ci.apply(cc.as_reader(), structs.CarControlSP(), tick * 10_000_000)
  assert (learned_state(ci.CC) != before) == learning
  if not learning:
    assert not any(isinstance(item, dict) and "gas_factor" in item for item in provider.persisted)


def test_clarity_yaw_signal_decodes_vfn_units():
  dbc = DBC[CAR.HONDA_CLARITY][Bus.pt]
  packer = CANPacker(dbc)
  parser = CANParser(dbc, [("KINEMATICS", 100)], 0)
  for tick in range(5):
    msg = packer.make_can_msg("KINEMATICS", 0, {"YAW_RATE": -1.0})
    parser.update([(tick * 10_000_000, [msg])])
  assert parser.vl["KINEMATICS"]["YAW_RATE"] == -1.0
