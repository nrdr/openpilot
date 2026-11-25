"""Opt-in re-issue of the turn-desire pulse.

The model is told about a turn desire only on the frame it switches on and remembers it for about five
seconds (measured 2026-11-20: 5.04-5.06 s for OPM10V3, 5.5-8.8 s for TSFDOM). The pulse fires when speed
first drops below the turn-desire speed with the blinker on, so a turn that takes longer than that, or
starts from a stop, runs with no desire left in the model's memory.

While one turn request stays up and the turn has not started, this drops the request for a single model
frame to produce a fresh pulse:
  - when the car moves off after a stop, and
  - every REFRESH_S while it keeps moving,
at most MAX_REFRESHES times per request. Once the wheel is turned toward the request the model is already
acting on it, so nothing is re-issued during or after the turn. With the option off the request passes
through unchanged.
See openpilot/nrdr/docs/turn_desire_refresh_2026-11-20.md.
"""
PARAM = "NrdrTurnDesireRefresh"

REFRESH_S = 5.0          # the model's pulse memory; a new pulse arrives as the old one leaves
LAUNCH_MIN_AGE_S = 2.5   # moving off re-issues the pulse only if the last one is at least this old
STOP_SPEED = 0.5         # m/s
MOVING_SPEED = 1.0       # m/s
NOT_STARTED_DEG = 20.0   # wheel angle toward the request below which the turn has not started
TURNED_DEG = 90.0        # once the wheel has been this far toward the request, the turn is under way or done
MAX_REFRESHES = 3


def enabled(params) -> bool:
  """A missing key reads as off."""
  try:
    return bool(params.get_bool(PARAM))
  except Exception:
    return False


class TurnDesireRefresh:
  def __init__(self, none, dt: float):
    self.none = none
    self.refresh_frames = round(REFRESH_S / dt)
    self.launch_min_frames = round(LAUNCH_MIN_AGE_S / dt)
    self.direction = none
    self.frames_since_pulse = 0
    self.refreshes = 0
    self.stopped = False
    self.turned = False
    self.blank = False

  def update(self, requested, v_ego: float, wheel_toward_deg: float, enabled: bool):
    """Call once per model frame. `wheel_toward_deg` is the wheel angle signed toward the requested turn.
    Returns the direction to publish for this frame."""
    if requested == self.none or requested != self.direction:
      # no request, or a new one: pass it through and start counting from its own pulse
      self.direction = requested
      self.frames_since_pulse, self.refreshes, self.blank = 0, 0, False
      self.turned = requested != self.none and wheel_toward_deg >= TURNED_DEG
      self.stopped = v_ego < STOP_SPEED
      return requested
    if wheel_toward_deg >= TURNED_DEG:
      self.turned = True
    if self.blank:
      # the frame after a dropped one: publishing the request again is the fresh pulse
      self.blank = False
      self.frames_since_pulse = 0
      return requested
    self.frames_since_pulse += 1
    moving_off = self.stopped and v_ego > MOVING_SPEED
    if v_ego < STOP_SPEED:
      self.stopped = True
    elif v_ego > MOVING_SPEED:
      self.stopped = False
    due = (moving_off and self.frames_since_pulse >= self.launch_min_frames) or \
          (v_ego > MOVING_SPEED and self.frames_since_pulse >= self.refresh_frames)
    not_started = not self.turned and wheel_toward_deg < NOT_STARTED_DEG
    if enabled and due and not_started and self.refreshes < MAX_REFRESHES:
      self.refreshes += 1
      self.blank = True
      return self.none
    return requested
