from opendbc.car.honda.civic_pcm import WindCreditTrial
from opendbc.car.honda.tests.test_civic_pcm import interface
from opendbc.car.honda.tests.test_civic_pcm_speed_control import apply
from opendbc.car.honda.values import CAR
import pytest


def test_recovery_requires_sustained_missing_deceleration_and_real_request():
  trial = WindCreditTrial()
  for i in range(251):
    # A brief bump followed by coast matching the request.
    assert not trial.update(i * 20_000_000, True, -.8, 0. if i < 18 else -.8, 30, 0)
  samples = [trial.update(i * 20_000_000, True, -.8, -.02, 30, 0) for i in range(251, 501)]
  assert not any(samples[:25]) and 0 < samples[-1] < 12
  # No wind-credit headroom, no request, and stale data all veto any held trial output.
  assert trial.update(501 * 20_000_000, True, -.8, -.02, 10, 10) == 0
  assert trial.update(502 * 20_000_000, True, .1, .4, 30, 0) == 0
  assert trial.update(800 * 20_000_000, True, -.8, -.02, 30, 0) == 0
  assert trial.update(801 * 20_000_000, False, -.8, -.02, 30, 0) == 0


def test_wire_trial_recovers_some_discarded_brake_only_on_opt_in():
  def run(opt_in, achieved):
    ci, _ = interface(wind_bench=opt_in)
    ci.CC.windfactor = 2.986
    ci.CS.out.vEgo, ci.CS.out.aEgo, ci.CS.out.canValid = 25., achieved, True
    brakes = []
    for tick in range(500):
      _, messages = apply(ci, -.78, tick, speed=24.)
      for addr, data, _ in messages:
        if addr == 0x1fa:
          brakes.append(int.from_bytes(data[:2], 'big') >> 6)
        elif addr == 0x30c:
          assert not data[2]
    return brakes
  assert max(run(False, -.04)) == 0
  assert max(run(True, -.78)) == 0
  commands = run(True, -.04)
  assert not any(commands[:25]) and 0 < max(commands) <= 12
  assert max(y - x for x, y in zip(commands, commands[1:], strict=False)) <= 1


def test_no_bench_hook_for_other_command_paths():
  for car, interceptor in [(CAR.HONDA_CLARITY, False), (CAR.HONDA_CIVIC, True), (CAR.HONDA_CIVIC_BOSCH, False)]:
    ci, _ = interface(car, interceptor=interceptor, wind_bench=True)
    assert ci.CC.civic_wind_trial is None


@pytest.mark.parametrize("veto", ["stockAeb", "gasPressed", "brakePressed", "canValid", "accFaulted", "positive_speed_lead"])
def test_trial_never_recovers_brake_during_a_veto(veto):
  ci, _ = interface(wind_bench=True)
  ci.CC.windfactor = 2.986
  cs = ci.CS.out
  cs.vEgo, cs.aEgo, cs.canValid = 25., -.04, True
  if veto != "positive_speed_lead":
    setattr(cs, veto, veto != "canValid")
  for tick in range(200):
    apply(ci, -.78, tick, speed=30. if veto == "positive_speed_lead" else 24.)
    assert ci.CC.civic_wind_trial.extra == 0
