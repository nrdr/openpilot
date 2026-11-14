"""Command timing for the Civic's non-interceptor Nidec PCM path."""
import math

from opendbc.car.honda.values import CAR, HondaFlags
from opendbc.car.honda.nidec_pcm_constraints import taper_positive_accel
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP


PCM_GAS_TICKS = 10  # ACC_HUD is transmitted at 10 Hz, from a 100 Hz controller.
REFERENCE_MAX_AGE_NS = 250_000_000
# Candidate preview for gentle slowdowns, not a learned inverse of engine drag.
# The positive-acceleration servo gain can be >10 s. Reusing it below zero
# turned a -0.1 m/s2 request into a multi-mph reduction of the PCM target.
SLOWDOWN_PREVIEW_SECONDS = 1.0


def coast_blend(requested: float, hill: float, speed: float, cruise: float, eligible: bool) -> tuple[float, float]:
  """Free-cruise road-load credit (m/s2) and positive speed-feedforward fraction.

  Candidate lower-envelope credit, not measured brake authority or a wind learner:
  Nov 8 Civic coast samples (no pedals/brake/reported gas, zero PCM target, >.5s
  settling) had -aEgo-g*sin(pitch) mostly above this 0.10--0.30 m/s2 curve.
  The recorded trajectory is NOT a closed-loop validation of this approximation.

  Credit fades out for overspeed or material slowdown. Leads, stops, invalid
  observations and overrides veto it at both producer and controller. No timer
  holds propulsion, no minimum speed target, no simultaneous gas/brake exception.
  The same credit reduces positive feedforward BEFORE friction is required, so
  gas cannot keep asking for full speed lead while the brake path enters coast.
  """
  if (not eligible or not all(math.isfinite(x) for x in (requested, hill, speed, cruise))
      or requested <= -.5 or not 5.0 < speed < 50.0 or not 5.0 < cruise <= 100.0):
    return 0.0, 1.0
  # Deliberately below the observed coast resistance; never apply the saved
  # Wind Brake factor (nearly 3 in the source drive, ~1.7 m/s2 at highway speed).
  points = ((5.0, .10), (13.0, .15), (22.0, .25), (35.0, .30))
  drag = points[-1][1]
  for (v0, d0), (v1, d1) in zip(points, points[1:]):
    if speed <= v1:
      drag = d0 + (d1 - d0) * (speed - v0) / (v1 - v0)
      break
  rolling = min((speed - 5.0) / 4.0, 1.0)
  # Full credit only through +0.25 m/s overspeed, none by +0.75 (~1.7 mph).
  speed_weight = min(max((.75 - (speed - cruise)) / .5, 0.0), 1.0)
  # A >=0.5 m/s2 slowdown retains the original brake path in full.
  demand_weight = min(max((requested + .5) / .35, 0.0), 1.0)
  credit = drag * rolling * min(speed_weight, demand_weight)
  # Do not restore positive feedforward at the zero-credit overspeed endpoint.
  # For negative wheel demand its limit as credit -> 0 is zero, not one.
  fraction = (min(max((requested + hill + credit) / credit, 0.0), 1.0) if credit > 0.0
              else float(requested + hill >= 0.0))
  return credit, fraction


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


def speed_deadzone_target(target: float, speed: float, maximum: float) -> float:
  """Continuous target-speed deadband: zero width at 0 m/s, full width at 9 m/s.

  Inside the band request current speed, never a zero PCM target. This is a
  setpoint transform for the factory speed servo, not a replacement PID.
  """
  if (type(maximum) not in (int, float) or not math.isfinite(maximum) or not 0.0 <= maximum <= 0.2
      or not math.isfinite(target) or not math.isfinite(speed) or speed < 0.0):
    return target
  if maximum == 0.0:
    return target
  width = maximum * min(speed / 9.0, 1.0)
  error = target - speed
  return speed + math.copysign(max(abs(error) - width, 0.0), error)


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


def speed_learning_observable(reference: float | None, speed: float, shaped_accel: float,
                              requested_accel: float, gas_wire: float, maximum: float) -> bool:
  """MVL's gain fit is valid only when the speed lead is effectively sf * accel.

  The planner-reference offset and comfort ramp can otherwise look like ECU lag.
  A full gas allowance leaves authority to the speed servo; a reduced allowance
  cannot distinguish servo response from the gas ceiling. Launch learning has
  its own measured-response gates and is independent of this steady-state fit.
  """
  return bool(reference is not None and all(math.isfinite(v) for v in (reference, speed, shaped_accel, requested_accel, gas_wire, maximum))
              and abs(reference - speed) <= 0.1 and shaped_accel > 0.05
              and abs(shaped_accel - taper_positive_accel(requested_accel, speed)) <= 0.005 and maximum > 0 and gas_wire >= maximum)


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
