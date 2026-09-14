"""Bumpless live torque-tuning edits; no storage I/O or changed steady-state tune."""

from dataclasses import dataclass
import math

from openpilot.nrdr.params.snapshots import LIVE_LATERAL_KEYS


LIVE_TUNING_TRANSITION_SECONDS = 1.0


@dataclass
class LiveTorqueTransition:
  previous_values: tuple | None = None
  previous_output: float = 0.0
  offset: float = 0.0
  remaining: float = 0.0
  was_active: bool = False

  def update(self, output: float, snapshot, active: bool, steering_pressed: bool, dt: float) -> float:
    values = tuple(snapshot.get(key) for key in LIVE_LATERAL_KEYS)
    changed = self.previous_values is not None and values != self.previous_values
    self.previous_values = values
    if not active or steering_pressed or not math.isfinite(output):
      self.offset = self.remaining = 0.0
      self.was_active = False
      self.previous_output = output if math.isfinite(output) else 0.0
      return output

    if changed and self.was_active:
      # Remove the edit's first-frame step. Subsequent road-driven command
      # changes still pass through; only this offset is retired over one second.
      self.offset = self.previous_output - output
      self.remaining = LIVE_TUNING_TRANSITION_SECONDS
    elif self.remaining > 0.0:
      remaining = max(0.0, self.remaining - max(0.0, dt))
      self.offset *= remaining / self.remaining
      self.remaining = remaining

    result = max(-1.0, min(1.0, output + self.offset)) if self.remaining > 0.0 else output
    self.previous_output = result
    self.was_active = True
    return result
