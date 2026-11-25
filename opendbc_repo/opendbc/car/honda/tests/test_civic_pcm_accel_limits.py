"""Experimental-only removal of the historical near-cruise windup ceiling."""
from types import SimpleNamespace

import numpy as np
import pytest

from opendbc.car.honda.interface import CarInterface
from opendbc.car.honda.tests.test_civic_pcm import interface
from opendbc.car.honda.values import CAR, CarControllerParams, HondaFlags
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP


@pytest.mark.parametrize("mvl", [False, True])
@pytest.mark.parametrize("speed", [0., 10., 27., 28.5, 29.8, 30., 32.])
def test_experimental_keeps_absolute_limits_without_near_cruise_ceiling(mvl, speed):
  ci, _ = interface(pcm_mode=2, mvl=mvl)
  assert ci.CP.flags & HondaFlags.NIDEC_PCM_EXPERIMENTAL
  assert CarInterface.get_pid_accel_limits(ci.CP, ci.CP_SP, speed, 30.) == (
    CarControllerParams.NIDEC_ACCEL_MIN, CarControllerParams.NIDEC_ACCEL_MAX)


@pytest.mark.parametrize("mode,mvl", [(0, False), (0, True), (1, False), (1, True)])
@pytest.mark.parametrize("speed", [27., 28.5, 29.8, 30., 32.])
def test_other_pcm_modes_keep_their_existing_ceiling(mode, mvl, speed):
  ci, _ = interface(pcm_mode=mode, mvl=mvl)
  ecu = mode == 1 and not mvl
  expected = np.interp(speed, [30. - (1.5 if ecu else 2.), 29.8],
                       [CarControllerParams.NIDEC_ACCEL_MAX, .4 if ecu else .2])
  assert CarInterface.get_pid_accel_limits(ci.CP, ci.CP_SP, speed, 30.) == (
    CarControllerParams.NIDEC_ACCEL_MIN, expected)


@pytest.mark.parametrize("car,interceptor", [(CAR.HONDA_CIVIC_BOSCH, False), (CAR.HONDA_CIVIC, True)])
def test_bosch_and_pedal_limits_are_unchanged(car, interceptor):
  ci, _ = interface(car, pcm_mode=2, interceptor=interceptor)
  baseline, _ = interface(car, pcm_mode=0, interceptor=interceptor)
  for speed in (28., 30., 32.):
    assert CarInterface.get_pid_accel_limits(ci.CP, ci.CP_SP, speed, 30.) == (
      CarInterface.get_pid_accel_limits(baseline.CP, baseline.CP_SP, speed, 30.))


@pytest.mark.parametrize("car,open_long,stock,bosch", [
  (CAR.HONDA_CLARITY, True, False, False),
  (CAR.HONDA_CIVIC, False, False, False),
  (CAR.HONDA_CIVIC, True, True, False),
  (CAR.HONDA_CIVIC, True, False, True),
])
def test_experimental_flag_alone_cannot_bypass_platform_or_control_scope(car, open_long, stock, bosch):
  cp = SimpleNamespace(carFingerprint=car, openpilotLongitudinalControl=open_long,
                       flags=HondaFlags.NIDEC_PCM_EXPERIMENTAL | (HondaFlags.BOSCH if bosch else 0))
  sp = SimpleNamespace(enableGasInterceptor=False, flags=HondaFlagsSP.STOCK_LONGITUDINAL if stock else 0)
  assert CarInterface.get_pid_accel_limits(cp, sp, 30., 30.) == (CarControllerParams.NIDEC_ACCEL_MIN, .2)
