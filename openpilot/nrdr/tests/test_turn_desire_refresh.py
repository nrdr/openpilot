from openpilot.nrdr.features.lateral import turn_desire_refresh as tdr
from openpilot.nrdr.features.lateral.turn_desire_refresh import TurnDesireRefresh

NONE, LEFT, RIGHT = 0, 1, 2
DT = 0.05


def run(speeds, requested, wheel=None, enabled=True):
  refresh = TurnDesireRefresh(NONE, DT)
  wheel = [0.0] * len(speeds) if wheel is None else wheel
  return [refresh.update(r, v, w, enabled) for r, v, w in zip(requested, speeds, wheel, strict=True)]


def pulses(out):
  """Frames where the model would see a rising edge."""
  return [i for i in range(len(out)) if out[i] != NONE and (i == 0 or out[i - 1] != out[i])]


def test_off_is_a_pure_pass_through():
  requested = [NONE] * 5 + [LEFT] * 400 + [NONE] * 3 + [RIGHT] * 50 + [LEFT] * 50
  speeds = [8.0] * 5 + [max(0.0, 8.0 - 0.1 * i) for i in range(100)] + [0.0] * 100 + [0.05 * i for i in range(200)] + [5.0] * 103
  assert run(speeds, requested, enabled=False) == requested


def test_long_approach_is_refreshed_every_five_seconds_up_to_the_limit():
  n = 600
  out = run([5.0] * n, [LEFT] * n)
  assert pulses(out) == [0, 101, 202, 303]          # one dropped frame, then the fresh pulse
  assert out.count(NONE) == tdr.MAX_REFRESHES
  assert all(out[i] == LEFT for i in range(n) if i not in (100, 201, 302))


def test_moving_off_after_a_stop_re_issues_the_pulse_once_it_is_old_enough():
  # pulse on the approach, 4 s stopped, then launch: the model's 5 s memory would otherwise be nearly spent
  speeds = [6.0 - 0.1 * i for i in range(60)] + [0.0] * 80 + [0.2 * i for i in range(60)]
  out = run(speeds, [RIGHT] * len(speeds))
  launch = 140 + 6                                   # first frame above MOVING_SPEED
  assert out[launch] == NONE and out[launch + 1] == RIGHT
  assert pulses(out)[:2] == [0, launch + 1]
  # nothing is re-issued while standing still, however long
  assert run([0.0] * 2000, [LEFT] * 2000) == [LEFT] * 2000


def test_a_quick_stop_and_go_does_not_double_the_pulse():
  speeds = [3.0 - 0.3 * i for i in range(10)] + [0.0] * 10 + [0.3 * i for i in range(20)]
  out = run(speeds, [LEFT] * len(speeds))
  assert pulses(out) == [0]                          # last pulse younger than LAUNCH_MIN_AGE_S


def test_nothing_is_re_issued_during_or_after_the_turn():
  n = 500
  # rolling turn: wheel already turned toward the request when the 5 s mark passes
  wheel = [0.0] * 40 + [min(140.0, 4.0 * i) for i in range(80)] + [140.0] * 380
  assert pulses(run([5.0] * n, [LEFT] * n, wheel)) == [0]
  # the turn is over and the wheel is straight again, but the blinker never cancelled: still nothing
  wheel = [0.0] * 20 + [150.0] * 60 + [0.0] * 420
  assert pulses(run([5.0] * n, [RIGHT] * n, wheel)) == [0]
  # wheel turned the other way (negative toward the request) counts as not started
  assert pulses(run([5.0] * 250, [LEFT] * 250, [-60.0] * 250)) == [0, 101, 202]


def test_a_new_or_changed_request_restarts_the_count():
  requested = [LEFT] * 250 + [NONE] * 2 + [LEFT] * 250 + [RIGHT] * 120
  out = run([5.0] * len(requested), requested)
  assert pulses(out) == [0, 101, 202, 252, 353, 454, 502, 603]
  assert out[250:252] == [NONE, NONE]


def test_request_first_seen_mid_turn_does_not_refresh_on_exit():
  assert pulses(run([5.0] * 250, [LEFT] * 250, [95.0] + [0.0] * 249)) == [0]


def test_option_reads_as_off_when_the_key_is_missing():
  class Missing:
    def get_bool(self, key):
      raise KeyError(key)
  assert tdr.enabled(Missing()) is False
