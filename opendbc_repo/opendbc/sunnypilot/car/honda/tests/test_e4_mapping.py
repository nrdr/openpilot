"""Host-output -> signed Honda E4 regressions; no vehicle, Params or safety-limit edits."""
from dataclasses import replace

import numpy as np
import pytest

from opendbc.car import gen_empty_fingerprint, structs
from opendbc.car.honda.interface import CarInterface
from opendbc.car.honda.values import CAR, CarControllerParams
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from opendbc.sunnypilot.car.tests.runtime_config import make_test_car_config


PLATFORMS = [
  pytest.param(CAR.HONDA_CIVIC_BOSCH, b"39990-TBA-C020", 3840, id="civic-c020"),
  pytest.param(CAR.HONDA_CIVIC_BOSCH, b"39990-TBA-C120", 3840, id="civic-c120"),
  pytest.param(CAR.HONDA_CIVIC_BOSCH, b"39990-TGG-A120", 3840, id="civic-tgg-a120"),
  pytest.param(CAR.HONDA_INSIGHT, b"39990-TXM-A040", 3840, id="insight"),
  pytest.param(CAR.HONDA_CIVIC, b"39990-TEG-A010", 3840, id="unchanged-teg"),
  pytest.param(CAR.HONDA_CLARITY, b"39990-TRW-A020", 3840, id="unchanged-clarity"),
  pytest.param(CAR.HONDA_CRV_5G, b"39990-TLA-A040", 4096, id="unchanged-crv"),
  pytest.param(CAR.HONDA_CIVIC_BOSCH_DIESEL, b"39990-TFK-G020", 4096, id="unchanged-diesel"),
]


def car_params(car, firmware, modified):
  config = make_test_car_config()
  # Isolate mapping from the independently tested override ramps/delta limiter.
  config.honda.provider.live_tuning = replace(config.honda.provider.live_tuning,
                                            override_fade_up_s=0.0, steer_delta_limiter_enabled=False,
                                            live_learning_gas=False)
  version = firmware.rsplit(b"-", 1)
  firmware = (b",".join(version) if modified else firmware) + b"\x00\x00"
  car_fw = [structs.CarParams.CarFw(ecu="eps", fwVersion=firmware)]
  fingerprint = gen_empty_fingerprint()
  cp = CarInterface.get_params(car, fingerprint, car_fw, alpha_long=False, is_release=False,
                              docs=False, interface_config=config)
  sp = CarInterface.get_params_sp(cp, car, fingerprint, car_fw, alpha_long=False, is_release_sp=False, docs=False)
  assert bool(sp.flags & HondaFlagsSP.EPS_MODIFIED) is modified
  return cp, sp, config


def interface(car, firmware, modified):
  cp, sp, config = car_params(car, firmware, modified)
  ci = CarInterface(cp, sp, config)
  ci.update([])
  ci.CS.out.vEgo = 20.0
  ci.CS.out.aEgo = 0.0
  ci.CS.out.cruiseState.speed = 30.0
  ci.CS.out.cruiseState.available = True
  ci.CS.out.standstill = False
  ci.CS.out.steeringPressed = False
  ci.CS.out.steeringTorque = 0.0
  ci.CS.steer_control_active = True
  return ci


def command(ci, output, tick, active=True):
  cc = structs.CarControl(enabled=active, latActive=active)
  cc.actuators.torque = output
  returned, messages = ci.apply(cc.as_reader(), structs.CarControlSP(), tick * 10_000_000)
  steering = [data for address, data, _ in messages if address == 0xE4]
  assert len(steering) == 1
  return returned, int.from_bytes(steering[0][:2], "big", signed=True)


@pytest.mark.parametrize("car,firmware,limit", PLATFORMS)
@pytest.mark.parametrize("modified", [False, True], ids=["stock", "modified"])
def test_stock_and_modified_images_have_the_intended_identity_mapping(car, firmware, limit, modified):
  cp, _, _ = car_params(car, firmware, modified)
  assert list(cp.lateralParams.torqueBP) == [0, limit]
  assert list(cp.lateralParams.torqueV) == [0, limit]
  params = CarControllerParams(cp)
  assert params.STEER_MAX == limit
  assert params.STEER_LOOKUP_BP == params.STEER_LOOKUP_V == [-limit, 0, limit]


@pytest.mark.parametrize("car,firmware,limit", PLATFORMS)
@pytest.mark.parametrize("modified", [False, True], ids=["stock", "modified"])
def test_real_controller_packs_signed_e4_and_reports_the_same_wire_command(car, firmware, limit, modified):
  ci = interface(car, firmware, modified)
  outputs = (-1.25, -1.0, -0.9375, -0.9, -0.5, -0.1, -0.0001, 0.0,
             0.0001, 0.1, 0.5, 0.9, 0.9375, 1.0, 1.25)
  for tick, output in enumerate(outputs):
    returned, wire = command(ci, output, tick)
    # The actuator field is Float32 on the message boundary (e.g. 0.9 is
    # slightly below 0.9 there); the controller then truncates to CAN counts.
    expected = int(np.clip(-float(np.float32(output)) * limit, -limit, limit))
    assert wire == returned.torqueOutputCan == expected
    assert abs(wire) <= limit
    if abs(output) <= 1.0:
      # This is not double-normalized or silently reshaped in CarController.
      assert returned.torque == pytest.approx(output, abs=1e-6)
    if wire:
      assert np.sign(wire) == -np.sign(output)


@pytest.mark.parametrize("car,firmware,limit", PLATFORMS)
@pytest.mark.parametrize("modified", [False, True], ids=["stock", "modified"])
def test_disengaged_controller_never_sends_nonzero_e4(car, firmware, limit, modified):
  ci = interface(car, firmware, modified)
  command(ci, 0.75, 0)
  for tick, output in enumerate((-1.0, 1.0), 1):
    returned, wire = command(ci, output, tick, active=False)
    assert wire == returned.torqueOutputCan == 0
    assert returned.torque == 0.0


@pytest.mark.parametrize("car,firmware", [
  (CAR.HONDA_CIVIC_BOSCH, b"39990-TBA-C020"),
  (CAR.HONDA_INSIGHT, b"39990-TXM-A040"),
])
@pytest.mark.parametrize("modified", [False, True], ids=["stock", "modified"])
def test_same_pid_fraction_shrinks_counts_but_rescaled_physical_ff_stays_the_same(car, firmware, modified):
  ci = interface(car, firmware, modified)
  # Avoid integer rounding in the fixed-fraction comparison: exactly 6.25% fewer
  # counts throughout the range, not just removal of the old saturated tail.
  for tick, output in enumerate((-1.0, -0.75, -0.5, -0.25, 0.25, 0.5, 0.75, 1.0)):
    returned, wire = command(ci, output, tick)
    assert wire == -output * 4096 * (3840 / 4096)
    assert returned.torque == pytest.approx(output)

  # The Firmware Controller must pair its inverse divisor with the host scale:
  # one physical E4 can use a different normalized fraction without changing CAN.
  for tick, physical_e4 in enumerate((-3000, -1536, -384, 384, 1536, 3000), 10):
    fraction = -physical_e4 / 3840
    _, wire = command(ci, fraction, tick)
    assert wire == pytest.approx(physical_e4, abs=1)
    assert fraction == pytest.approx((-physical_e4 / 4096) * (4096 / 3840))
