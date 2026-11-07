"""Behavior changes intentionally brought in with the October MVL sync."""
import pytest

from opendbc.car import structs
from opendbc.car.honda.tests.test_civic_pcm import interface, control
from opendbc.car.honda.values import CAR, HondaSafetyFlags


@pytest.mark.parametrize("car", [CAR.HONDA_CIVIC, CAR.HONDA_CLARITY, CAR.ACURA_ILX])
def test_only_interceptor_uses_the_new_integral_gain(car):
  pcm, _ = interface(car, interceptor=False)
  pedal, _ = interface(car, interceptor=True)
  assert list(pcm.CP.longitudinalTuning.kiV) == pytest.approx([0.0])
  assert list(pedal.CP.longitudinalTuning.kiBP) == pytest.approx([0.0])
  assert list(pedal.CP.longitudinalTuning.kiV) == pytest.approx([0.3])


def test_civic_positive_plan_keeps_speed_lead_with_poisoned_alpha():
  ci, _ = interface(learning=False)
  ci.CC.speed_alphas = {key: -5.0 for key in ci.CC.speed_alphas}
  ci.CS.out.aEgo = 0.8
  ci.CC.nidec_pid.i = -0.5
  cc = control(0.4)
  ci.apply(cc.as_reader(), structs.CarControlSP(), 0)
  assert ci.CC.accel < 0.0
  assert ci.CC.pcm_speed_sent - ci.CS.out.vEgo == pytest.approx(0.35, abs=0.01)


@pytest.mark.parametrize("car,uses_abs", [(CAR.ACURA_INTEGRA, True), (CAR.HONDA_CIVIC_BOSCH, False), (CAR.HONDA_CIVIC, False)])
def test_abs_only_safety_flag_is_limited_to_integra(car, uses_abs):
  ci, _ = interface(car)
  assert bool(ci.CP.safetyConfigs[-1].safetyParam & HondaSafetyFlags.NO_ENGINE_DATA_MSG) is uses_abs
