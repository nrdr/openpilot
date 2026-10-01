"""VFN's f837ca86 core regression tests, adapted to NRDR's isolated port."""
import math
import numpy as np
import pytest
from openpilot.nrdr.features.lateral import vfn_eps_core as eps_ff
from openpilot.common.filter_simple import FirstOrderFilter

DT_CTRL = 0.01
KP_BP, KP_V, KI_V = [0.0, 11.175, 11.176, 22.352], [0.018, 0.024, 0.048, 0.060], [0.006, 0.008, 0.016, 0.020]


def _lat_pid_scale_banded(speed, low, standard, highway):
  return low if speed < 25 * 0.44704 else standard if speed < 50 * 0.44704 else highway


# --- firmware model and feedforward -------------------------------------------------------------

@pytest.mark.parametrize("output", [-1.0, -0.4, -0.05, 0.0, 0.02, 0.3, 0.9])
def test_command_map_round_trips(output):
  r5 = eps_ff.r5_from_output(output, 20.0)
  assert eps_ff.output_from_r5(r5) == pytest.approx(output, abs=2e-3)


def test_command_map_matches_the_measured_gain():
  # route 00000352: R5 = 7.7 * E4 and E4 = -3840 * output
  assert eps_ff.r5_from_output(0.1, 20.0) == pytest.approx(-0.1 * 3840 * 7.7, rel=0.03)


@pytest.mark.parametrize("load,rate", [(500, 0), (-1500, 0), (800, 40), (-800, -40), (300, -60), (-4000, 120),
                                       (100, -216), (-6000, 0), (0, 0)])
@pytest.mark.parametrize("guess", [0.0, 15000.0, -15000.0])
def test_inversion_reproduces_the_requested_load(load, rate, guess):
  r5 = eps_ff.r5_for_motion(load, rate, guess)
  assert eps_ff.firmware_output(r5, rate) == pytest.approx(load, abs=1e-6)


@pytest.mark.parametrize("angle", [0.0, 45.0, 150.0, -300.0])
@pytest.mark.parametrize("load,rate", [(800, 40), (-4000, 120), (300, -60)])
def test_inversion_reproduces_the_requested_load_at_an_angle(load, rate, angle):
  r5 = eps_ff.r5_for_motion(load, rate, 0.0, angle)
  assert eps_ff.firmware_output(r5, rate, angle) == pytest.approx(load, abs=1e-6)


def test_firmware_damping_grows_with_angle_like_its_table():
  # R6 is taken before the firmware's angle table: per deg/s of the published rate it is -119 near centre
  # and -141..-146 past 60 deg on routes 363/365/366/369, flat per count of the pre-table 0x18F rate
  assert eps_ff.firmware_r6(10.0, 0.0) == pytest.approx(-1220.0, rel=0.01)
  assert eps_ff.firmware_r6(10.0, 5.0) == pytest.approx(-1220.0, rel=0.02)
  assert eps_ff.firmware_r6(10.0, 200.0) == pytest.approx(-1220.0 * 1.19, rel=0.02)
  assert eps_ff.firmware_r6(10.0, -200.0) == eps_ff.firmware_r6(10.0, 200.0)
  assert eps_ff.firmware_r6(-10.0, 200.0) == -eps_ff.firmware_r6(10.0, 200.0)


def test_turn_in_asks_more_than_a_hold_and_an_exit_less():
  # left turn (positive angle and output) at 60 deg, 8 m/s
  def out(rate):
    return eps_ff.output_from_r5(eps_ff.r5_for_motion(eps_ff.column_load(60.0, rate, 8.0, 0.0), rate))
  turn_in, hold, unwind = out(40.0), out(0.0), out(-40.0)
  assert turn_in > hold > unwind
  assert hold > 0.0


@pytest.mark.parametrize("v_kph,cap", [(40.0, eps_ff.R5_CAP), (130.0, 0.9 * 24000)])
def test_target_stays_clear_of_the_rail_and_the_speed_ceiling(v_kph, cap):
  ff = eps_ff.HondaEpsFirmwareFeedforward(DT_CTRL)
  for k in range(200):
    ff.update(400.0 + k, v_kph / 3.6, 0.0)
  assert abs(ff.r5) <= cap + 1e-6


def test_desired_rate_tracks_a_ramp_and_resets():
  ff = eps_ff.HondaEpsFirmwareFeedforward(DT_CTRL)
  for k in range(150):
    ff.update(50.0 * k * DT_CTRL, 10.0, 0.0)
  assert ff.rate == pytest.approx(50.0, abs=1.0)
  ff.reset()
  assert ff.rate == 0.0 and ff.output == 0.0 and ff.prev_angle is None


def test_feedforward_output_is_smoothed():
  raw = eps_ff.HondaEpsFirmwareFeedforward(DT_CTRL, output_tau=0.0)
  smooth = eps_ff.HondaEpsFirmwareFeedforward(DT_CTRL)
  for ff in (raw, smooth):
    ff.update(0.0, 10.0, 0.0)
    ff.update(30.0, 10.0, 0.0)   # a step in the target
  assert abs(smooth.output) < 0.2 * abs(raw.output)


# --- control core ---------------------------------------------------------------------------------

def _core():
  return eps_ff.HondaEpsLateralCore(KP_BP, KP_V, KP_BP, KI_V, DT_CTRL)


def _hold(core, frames, des=20.0, angle=20.0, v=10.0, pressed=False):
  for _ in range(frames):
    core.update(des, 0.0, angle, v, 0.0, pressed, False)


def test_feedforward_waits_for_the_wheel_to_join_the_path():
  core = _core()
  _hold(core, 100, des=60.0, angle=20.0)   # engaged 40 deg off the path
  assert core.ff_weight == 0.0
  _hold(core, 25, des=60.0, angle=58.0)    # on the path: fades in over FF_FADE_IN_S
  assert 0.0 < core.ff_weight < 1.0
  _hold(core, 40, des=60.0, angle=58.0)
  assert core.ff_weight == 1.0
  _hold(core, 10, des=60.0, angle=20.0)    # once in, a later error does not throw it out
  assert core.ff_weight == 1.0


def test_driver_press_and_standstill_take_the_feedforward_out():
  core = _core()
  _hold(core, 80)
  assert core.ff_weight == 1.0
  _hold(core, 1, pressed=True)
  assert core.ff_weight == 0.0
  _hold(core, 80)
  _hold(core, 1, v=1.0)
  assert core.ff_weight == 0.0
  _hold(core, 80, v=3.0)
  assert core.ff_weight == pytest.approx(0.5)   # faded in with speed between 2 and 4 m/s


@pytest.mark.parametrize("v, des, weight", [
  (3.0, 2.0, 0.0),     # crawling near straight: the model's wiggles do not reach the wheel through the feedforward
  (3.0, -12.5, 0.25),  # joins with |desired angle| between 5 and 20 deg (0.5 from the 2-4 m/s speed fade)
  (4.5, 12.5, 0.5),
  (4.5, -30.0, 1.0),   # every real crawl turn gets all of it
  (6.5, 2.0, 0.5),     # the crawl gate fades out of effect between 5 and 8 m/s
  (8.0, 0.0, 1.0),
  (20.0, 0.5, 1.0),    # at speed it never applies
])
def test_crawl_gate_holds_the_feedforward_off_near_straight(v, des, weight):
  core = _core()
  _hold(core, 80, des=des, angle=des, v=v)
  assert core.ff_weight == pytest.approx(weight)


def test_friction_knee_is_wide_in_the_city_and_sharp_at_speed():
  assert eps_ff.friction_width(0.0) == eps_ff.friction_width(8.0) == 20.0
  assert eps_ff.friction_width(15.0) == eps_ff.friction_width(30.0) == eps_ff.FRICTION_WIDTH_DEG_S == 5.0
  # a slow desired rate asks for less friction in the city than at speed; a turn-in rate gets it all either way
  city = eps_ff.column_load(0.0, 5.0, 8.0, 0.0, eps_ff.friction_width(8.0)) - eps_ff.column_load(0.0, 5.0, 8.0, 0.0, 1e9)
  fast = eps_ff.column_load(0.0, 5.0, 8.0, 0.0, eps_ff.friction_width(20.0)) - eps_ff.column_load(0.0, 5.0, 8.0, 0.0, 1e9)
  assert abs(city) < 0.4 * abs(fast)
  turn = [eps_ff.column_load(0.0, 100.0, 8.0, 0.0, w) - eps_ff.column_load(0.0, 100.0, 8.0, 0.0, 1e9) for w in (20.0, 5.0)]
  assert turn[0] == pytest.approx(turn[1], rel=0.01)


def test_without_the_feedforward_the_core_is_the_banded_pid():
  core = _core()
  eps_ff.FF_JOIN_ERROR_DEG, saved = -1.0, eps_ff.FF_JOIN_ERROR_DEG
  try:
    out = core.update(10.0, 0.0, 5.0, 15.0, 0.0, False, False)
  finally:
    eps_ff.FF_JOIN_ERROR_DEG = saved
  p = float(np.interp(15.0, KP_BP, KP_V)) * 5.0 * 1.00    # 15 m/s is the standard band: LatPScale 100
  i = float(np.interp(15.0, KP_BP, KI_V)) * 0.95 * DT_CTRL * 5.0
  assert out == pytest.approx((p + i) * DT_CTRL / (0.05 + DT_CTRL))


MPH = 0.44704
SPEEDS = [0.0, 3.0, 25 * MPH - 1e-6, 25 * MPH, 25 * MPH + 1e-6, 15.0, 50 * MPH - 1e-6, 50 * MPH, 50 * MPH + 1e-6, 30.0]


@pytest.mark.parametrize("v", SPEEDS)
def test_output_lpf_bands_switch_exactly_where_latcontrol_pids_do(v):
  taus = (0.07, 0.05, 0.01)
  assert eps_ff.speed_band(v, taus) == _lat_pid_scale_banded(v, *taus)


def test_output_lpf_is_latcontrol_pids_filter():
  # The car controller does not filter (see carcontroller.py), so this LPF must be exactly the one
  # LatControlPID runs: FirstOrderFilter from 0, update_alpha with the banded tau every frame, then clip.
  taus = (0.07, 0.05, 0.01)
  filtered, raw = _core(), _core()
  filtered.output_lpf_tau = raw.output_lpf_tau = taus
  raw.output_lpf_enabled = False
  reference = FirstOrderFilter(0.0, 0.1, DT_CTRL)
  speeds = np.concatenate([np.linspace(3.0, 30.0, 300), np.linspace(30.0, 3.0, 300)])
  for k, v in enumerate(speeds):
    args = (40.0 * math.sin(k * 0.05), 0.5, 38.0 * math.sin(k * 0.05 - 0.1), float(v), 0.0, False, False)
    out = filtered.update(*args)
    u = raw.update(*args)
    reference.update_alpha(_lat_pid_scale_banded(float(v), *taus))
    assert out == max(min(reference.update(u), 1.0), -1.0)
  filtered.reset()
  assert filtered.output_lpf.x == 0.0 and filtered.output == 0.0


def test_output_lpf_setting_is_honoured():
  core = _core()
  core.output_lpf_enabled = False
  out = core.update(10.0, 0.0, 5.0, 15.0, 0.0, False, False)
  assert out == pytest.approx(core.pid.p + core.pid.i + core.pid.f)




def test_optimized_lane_change_suppresses_ff_and_rejoins_gradually():
  core = _core()
  _hold(core, 80)
  assert core.ff_weight == 1.0
  for _ in range(100):
    core.update(20.0, 0.0, 20.0, 10.0, 0.0, False, False, optimized_lane_change=True)
    assert core.ff_weight == 0.0
    assert core.pid.f == 0.0
  core.update(20.0, 0.0, 20.0, 10.0, 0.0, False, False)
  assert 0.0 < core.ff_weight < 0.1
