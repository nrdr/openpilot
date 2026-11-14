"""Civic Experimental adapter: MVL learning, wind isolation, brake priority."""
from copy import deepcopy

import pytest

from opendbc.car.honda import civic_pcm
from opendbc.car.honda.nidec_pcm_constraints import taper_positive_accel
from opendbc.car.honda.tests.test_civic_pcm import interface, control
from opendbc.car.honda.tests.test_civic_pcm_speed_control import START, reference, apply
from opendbc.car.honda.values import CAR, HondaFlags


@pytest.mark.parametrize("mvl", [False, True])
def test_wind_choice_is_saved_but_has_no_control_effect_with_experimental(mvl):
  on, on_config = interface(mvl=mvl, wind_brake=True, wind_bench=True)
  off, off_config = interface(mvl=mvl, wind_brake=False)
  assert on_config.honda.nidec_wind_brake and not off_config.honda.nidec_wind_brake
  assert not on.CC.nidec_wind_brake and not off.CC.nidec_wind_brake
  assert on.CC.civic_wind_trial is None
  for tick in range(220):
    accel = .6 if tick < 100 else (-.1 if tick < 150 else -1.)
    assert apply(on, accel, tick)[1] == apply(off, accel, tick)[1]
  assert on.CC.apply_brake_last > 0


def test_mvl_and_experimental_admitted_together_and_speed_learning_remains_live():
  ci, config = interface(mvl=True, learning=True)
  assert ci.CP.flags & HondaFlags.MVL_LONGITUDINAL and ci.CP.flags & HondaFlags.NIDEC_PCM_EXPERIMENTAL
  assert ci.CC.mvl_longitudinal and ci.CC.civic_pcm
  assert ci.CC.nrdr.live_tuning().live_learning_gas
  before = deepcopy(ci.CC.speed_factors)
  gas_before = deepcopy(ci.CC.gas_factors)
  for tick in range(650):
    apply(ci, .5, tick)
  assert ci.CC.speed_factors != before
  assert ci.CC.gas_factors == gas_before
  assert any("speed_factor" in snapshot for snapshot in config.honda.provider.persisted)


@pytest.mark.parametrize("reason", ["inactive", "brake", "aeb", "stale"])
def test_combined_mode_releases_propulsion_without_a_comfort_delay(reason):
  ci, _ = interface(mvl=True, learning=True)
  for tick in range(110):
    apply(ci, .6, tick)
  before = deepcopy(ci.CC.speed_factors)
  cc, now = control(.6), START + 1_100_000_000
  sp = reference(20., now)
  if reason == "inactive":
    cc.enabled = cc.longActive = False
  elif reason == "brake":
    ci.CS.out.brakePressed = True
  elif reason == "aeb":
    ci.CS.out.stockAeb = True
  else:
    sp.civicPcmReferenceMonoTime = START
  ci.apply(cc.as_reader(), sp, now)
  assert ci.CC.new_accel == ci.CC.pcm_gas_sent == 0
  assert ci.CC.speed_factors == before


@pytest.mark.parametrize("car,interceptor", [(CAR.HONDA_CIVIC, True), (CAR.HONDA_CLARITY, False), (CAR.HONDA_CIVIC_BOSCH, False)])
def test_combined_selection_does_not_change_other_powertrain_modes(car, interceptor):
  ci, _ = interface(car, interceptor=interceptor, mvl=True, pcm_mode=2)
  assert ci.CC.mvl_longitudinal and not ci.CC.civic_pcm


def test_speed_fit_excludes_reference_offsets_ramps_and_limited_authority():
  shaped = taper_positive_accel(.5, 20.)
  assert civic_pcm.speed_learning_observable(20., 20., shaped, .5, 198, 198)
  assert not civic_pcm.speed_learning_observable(21., 20., shaped, .5, 198, 198)
  assert not civic_pcm.speed_learning_observable(20., 20., .05, .5, 198, 198)
  assert not civic_pcm.speed_learning_observable(20., 20., shaped, .5, 190, 198)
  assert not civic_pcm.speed_learning_observable(None, 20., shaped, .5, 198, 198)
