"""Command timing for the Civic's non-interceptor Nidec PCM path."""
import math

from opendbc.car.honda.values import CAR, HondaFlags
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP


PCM_GAS_TICKS = 10  # ACC_HUD is transmitted at 10 Hz, from a 100 Hz controller.
REFERENCE_MAX_AGE_NS = 250_000_000
# Candidate preview for gentle slowdowns, not a learned inverse of engine drag.
# The positive-acceleration servo gain can be >10 s. Reusing it below zero
# turned a -0.1 m/s2 request into a multi-mph reduction of the PCM target.
SLOWDOWN_PREVIEW_SECONDS = 1.0


class WindCreditTrial:
  """Bench-only: return some discarded brake demand when coasting isn't delivering it.

  Output is an additional wire count, not a pressure estimate. The limits are
  experiment bounds, not a measured Civic brake calibration.
  """
  def __init__(self):
    self.last_ns = 0
    self.seconds = 0.
    self.extra = 0.

  def update(self, now_ns, eligible, demand, measured, pre_wind_counts, base_counts):
    dt = (now_ns - self.last_ns) * 1e-9
    self.last_ns = now_ns
    if (not eligible or not 0. < dt <= .05 or not all(math.isfinite(x) for x in
        (demand, measured, pre_wind_counts, base_counts)) or demand >= 0.):
      self.seconds = self.extra = 0.
      return 0
    # Act only on a sustained tracking deficit, not merely a negative plan.
    deficit = measured - demand
    self.seconds = min(1., self.seconds + dt) if deficit > .20 else 0.
    headroom = max(0., pre_wind_counts - base_counts)
    target = min(12., 12. * max(0., deficit - .20), headroom) if self.seconds >= .5 else 0.
    self.extra = min(headroom, max(self.extra - 8. * dt, min(self.extra + 4. * dt, target)))
    return int(self.extra)


def reference_speed(CC_SP, now_nanos: int, requested_accel: float) -> float | None:
  """Extrapolate a fresh planner speed reference; never reuse stale targets."""
  age = now_nanos - CC_SP.civicPcmReferenceMonoTime
  speed = CC_SP.civicPcmReferenceSpeed
  if (CC_SP.civicPcmReferenceMonoTime <= 0 or not 0 <= age <= REFERENCE_MAX_AGE_NS or
      not math.isfinite(speed) or not 0.0 <= speed <= 100.0 or not math.isfinite(requested_accel)):
    return None
  return min(max(speed + requested_accel * (age / 1e9), 0.0), 100.0)


def speed_target(reference: float, requested_accel: float, acceleration_gain: float) -> float:
  """Keep acceleration authority without extrapolating its gain into coasting.

  Positive requests retain the previous feedforward exactly. A negative request
  previews at most one second of speed loss instead of using the learned
  propulsion gain as an inverse model of the PCM's very different torque-off
  response. This is a static, continuous map: no held target, release timer,
  current-speed floor, or delay of a falling planner reference. Gas/brake and
  freshness interlocks remain outside this helper and take precedence.
  """
  gain = acceleration_gain if requested_accel >= 0.0 else min(acceleration_gain, SLOWDOWN_PREVIEW_SECONDS)
  return min(max(reference + gain * requested_accel, 0.0), 100.0)


def gas_allowance(requested_accel: float, actual_accel: float, speed_lead: float, maximum: int) -> float:
  """Legacy-style PCM authority ceiling, not an inverse pedal-position target.

  Leave full authority available while below the speed target. Close to the
  target, taper only for measured acceleration overshoot; below current speed,
  taper for speed overshoot too. These are the old override law's 0.3/1.1 m/s2
  and 0.5/1.0 m/s breakpoints, without its reduced low-speed authority ceiling.
  Braking/disengagement still zero the command outside this helper.
  """
  if not all(math.isfinite(v) for v in (requested_accel, actual_accel, speed_lead)) or requested_accel <= -0.5:
    # A material slowdown must release propulsion even before brake hysteresis
    # has ramped far enough to produce its first nonzero brake packet.
    return 0.0
  accel_error = actual_accel - requested_accel
  accel_limiter = 1.0 - 0.9 * min(max((accel_error - 0.3) / 0.8, 0.0), 1.0)
  # Acceleration overshoot should not starve a car still well below its target.
  accel_limiter = max(accel_limiter, min(max(speed_lead, 0.0), 1.0))
  speed_limiter = 1.0 - 0.9 * min(max(-speed_lead / 0.5, 0.0), 1.0)
  return float(maximum * min(speed_limiter, accel_limiter))


def allowance_command(target: float, previous_command: int, recovery: bool, maximum: int) -> int:
  """Keep the existing rise envelope, without inverse-model undershoot on release."""
  rise = 7 if recovery and previous_command < target else 2
  return int(min(max(target, 0.0), min(previous_command + rise, maximum)))


def uses_civic_pcm(CP, CP_SP) -> bool:
  return bool(CP.carFingerprint == CAR.HONDA_CIVIC and CP.openpilotLongitudinalControl and
              not (CP.flags & HondaFlags.BOSCH) and not CP_SP.enableGasInterceptor and
              not (CP_SP.flags & HondaFlagsSP.STOCK_LONGITUDINAL))


def response_per_tick(alpha: float) -> float:
  # A persisted value must not produce a singular/unstable inverse. This is the
  # same learner range, not a reset of stored tuning or a lower authority limit.
  return min(max(alpha, 0.02), 1.0) if math.isfinite(alpha) else 0.5


def gas_command(target: float, average: float, previous_command: int, alpha: float,
                recovery: bool, maximum: int) -> int:
  """Invert one complete sent-command interval, preserving existing rise limits.

  Inverting a 10 ms response and then holding that result for 100 ms magnified
  tiny reductions into zero-gas pulses. At alpha=.02 a 100->98 target produced
  0 followed by a half-second rise-limited recovery. The equivalent 100 ms
  response is ~.183, not .02. Keep the fractional target until final packing.
  """
  alpha_send = 1.0 - (1.0 - response_per_tick(alpha)) ** PCM_GAS_TICKS
  command = (target - average * (1.0 - alpha_send)) / alpha_send
  # Prepare at 100 Hz with exactly the old per-tick rise envelope. Only the
  # inverse horizon is 100 ms; multiplying the rise limit here would make the
  # first engage/override-release packet more aggressive than before.
  rise = 7 if recovery and previous_command < target else 2
  return int(min(max(command, 0.0), min(previous_command + rise, maximum)))


def advance_model(average: float, sensitivity: float, held_wire: int, alpha: float) -> tuple[float, float]:
  """Advance only the command actually on the wire, including between sends."""
  alpha = response_per_tick(alpha)
  return (average * (1.0 - alpha) + held_wire * alpha,
          (held_wire - average) + (1.0 - alpha) * sensitivity)
