# Lane change tuning — first iteration (2026-09-20)

Location: Sunnylink **Steering → Lane Change**, still immediately above NRDR.
The native SunnyPilot Lane Change settings screen exposes the same new controls.
All NRDR-owned additions have **NRDR** in the title. Existing SunnyPilot start
delay, blind-spot delay, and road-edge controls retain their location and names.

## Settings and when they apply

| Setting | Default | Meaning / application |
| --- | --- | --- |
| Auto Lane Change by Blinker | Existing saved setting | SunnyPilot delay before starting; not maneuver duration. Existing refresh is about 2.5 seconds. |
| NRDR Minimum Lane-Change State Time | 0.5 s | Minimum starting-state time before the model may finish. Also requires lane-change probability below 0.02. Captured at the next start. |
| NRDR Lane Change Entry SR Reduction | 0.0 (disabled) | Command-side reduction of 0–5 SR points. 3.0 is a proposed experiment, not a road-validated default. Captured at the next start; zero cancels an active effect. |
| NRDR Lane Change Entry SR Return Time | 1.0 s | Time to remove the reduction after a 0.15-second entry ramp. Captured at the next start. |
| NRDR Legacy Lane Change Torque Factor | 2.0x | Existing v1 torque path multiplies its acceleration factor in any non-off lane-change state, including waiting. Honda edits apply after refresh. 1.0 removes this factor. |
| NRDR Legacy Lane Change Friction | 0% | Existing v1 torque path suppresses friction during those states. Retain 0–100% instead. Honda edits apply after refresh. |

NRDR background refresh is normally within 0.5 seconds. Neither a reboot nor an
LKAS cycle is needed. Entry settings are intentionally captured per maneuver;
editing them does not restart or retime an already-running entry envelope.
Configure while parked. Existing one-second live-tuning output transitions apply
to legacy torque/friction edits, but not to settings waiting for the next maneuver.

The legacy factor/friction controls do **not** tune Honda PID, its interpolated
PIF/Torque blend, or replacement NNLC/v0/jerk-aware output paths. Their existing
default behavior is preserved. Non-Honda cars ignore these new torque/SR settings.

## SR semantics

This is a temporary steering **request** adjustment, not a claim that mechanical
geometry changes during a lane change. Measured curvature, saved SR sources and
learner state are not modified. The accepted SR source is resolved first, including
Hybrid's A/B transition, then the current effective ratio determines the request
reduction. For a constant 16.5 ratio, a 3-point peak reduction is equivalent to
requesting with 13.5, before blending back to the normal request.

The implementation maps the normal desired curvature into physical steering angle,
reduces its displacement from the zero-curvature steering angle, and maps it back
through the same source. This preserves the zero-curvature/roll-compensation point.
The resulting curvature is bounded between zero and the original request, and goes
through the existing curvature limiter and actuator/safety limits afterward.
Effective ratio reduction is capped at a floor of 8.0.

The envelope is time-based, **not** a measurement of how far across the lane the car
has traveled. It ramps in over 0.15 seconds, then smoothly returns over the chosen
time. Completion, cancellation, direction reversal or driver steering returns it
within 0.2 seconds. Disengagement or invalid/stale model data clears it. Driver
steering at initiation suppresses it for that maneuver. Waiting for a nudge does
not activate it. It does not re-trigger continuously while the state stays starting.

## Unchanged policies

- 20 mph lane-change admission floor and existing 10-second timeout.
- Blind-spot, road-edge and auto-lane-change brake/continuous-change admission checks.
- Model completion threshold (0.02), driver-nudge detection and steering safety limits.
- Clarity NNLC-to-PID selection during lane changes and stiction-helper suppression.
- Existing lane-centering signal/lane-change suppression and driver-override behavior.

These are documented rather than exposed as bypass controls.

## Validation and scope

Source-level and native bench tests are distinct from road validation. Compare the
disabled baseline against any experimental setting with the same model, SR sources
and other tuning. A larger reduction can make a lane change weaker; it is not a
guarantee of smoother or more accurate lane changes.

Applied-settings logs include the captured entry settings, current reduction,
resolved geometry, and curvature request before/after shaping. During the entry
effect, samples are queued at 10 Hz plus state changes. These are controller-side
values, not merely the saved UI setting; final actuator output still passes through
the existing downstream limits.

No release publication or device installation is part of this first implementation.
The `350` branch remains frozen. Native validation uses a separate offroad checkout
and private Params; it must not alter installed software or vehicle settings.
