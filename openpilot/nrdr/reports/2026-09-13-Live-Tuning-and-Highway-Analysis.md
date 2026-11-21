# September 13: live tuning and Civic highway oscillations

## Pre-deployment status and scope

This report records the isolated validation completed before C4 deployment.
At that point, live-tuning fixes were implemented locally on
`nrdr-architecture-development`, but not installed in `/data/openpilot`,
published, or road-validated.
Highway oscillation analysis has identified a strong tuning lead, not a proven
vehicle-level fix. No preset, stored vehicle setting, steering limit, override
policy, or steer-ratio calibration was changed. The owner's original report is
unchanged. Longitudinal issues and Sunnylink text layout remain outside this pass.

## Live-tuning changes

- Controller, P/I/F–torque blend, steer-ratio selection, vehicle-model learning
  switches, live delay, and lane-centering settings now use background snapshots
  with a target full polling cycle of 0.5 seconds, instead of engagement latches
  or the previous multi-second refresh intervals.
- A control frame captures one snapshot for geometry, controller settings and
  lane centering. The complete blend tuple is published together. Separate UI
  writes are not a storage transaction; polling latency is not a hard deadline.
- A torque-command edit transition removes the first-frame command step and
  retires the offset over one second. Unchanged settings do not add filtering.
  Driver takeover, disengagement and invalid output clear the transition.
- Local lane-centering controls and their Sunnylink schema permit live edits;
  the feature-dependent controls and runtime confidence/override gates remain.
  Drivers should not operate settings while driving.
- Sunnylink's server-side save policy now also admits the six live lane-centering
  settings onroad. The previous server restriction could reject an edit even
  after its UI allowed it. Longitudinal-personality, handcrafted-preset apply,
  vehicle-compatibility and protected-parameter restrictions are unchanged.
- Invalid minimum-speed settings still fall back to 50 mph. Nonfinite offset
  and model-authority values remain visible to the controller's rejection gate.
- Honda's separate parameter provider also refreshes its regular settings on a
  0.5-second target cycle. No filter coefficients or override thresholds changed.
- The PID consumer queues a `nrdr_live_settings_consumed` event when the resolved
  blend settings or engagement state change. It includes the snapshot generation,
  consumption time, all six blend settings and yaw-feedback validity. Logging
  runs in the background worker, never as storage/logging I/O in the control loop.
  This is best-effort consumption telemetry, not proof that the one-second
  transition has finished or that the EPS physically delivered the command.
- Native and Sunnylink blend help now describes live application consistently;
  stale "next engagement" instructions were removed. Numeric ranges, defaults
  and handcrafted preset values are unchanged.

### Highway-friction end-to-end check

`test_live_friction_pipeline.py` exercises a saved highway-friction change through
the production background reader, actual PID/legacy-yaw blend, one-second edit
transition and Honda steering low-pass filter. Three write paths are covered:
the native widget's production setter, Sunnylink's production save handler with
base64 decoding and typed storage, and a direct typed storage write.

With simulated highway motion and continuous lateral engagement, each test
changes highway friction from 1.0 to 0.3 and back to 1.0. It checks that the
controller consumes the new value, the first-frame step is removed, the
transition finishes and the post-filter command changes. Torque share, LAF,
low/standard friction and the other initialized settings remain unchanged.
The corresponding consumption event must be emitted once for each edit by
the background worker. Separate tests check that failed logging cannot stop
parameter refresh and that friction edits preserve normal integral evolution.

Only temporary Params are written. The Sunnylink test supplies confirmed-Honda
capability data without opening a socket; the native setter runs without starting
graphics. These tests do not measure internet delivery latency, render either UI,
send CAN, emulate EPS firmware or establish vehicle-level stability.

### Verification

Tests use an isolated source overlay and private Params directory on the parked
C4, guarded by fresh offroad, not-started, ignition-off and no-output checks.
The installed driving source and its Params were not modified. The isolated
validation directory is `/data/nrdr-live-validation-20260913-w8a_j2mh`.

The final native regression suite passed **509 tests and 179 subtests in 44.18
seconds**, including all three end-to-end live-friction write paths. Covered
behavior includes continuous-engagement edits, captured snapshot consistency,
blend disable/re-enable, steer-ratio selection, lane centering, transitions,
invalid inputs, UI callbacks, parameter ownership, Sunnylink save policy and
compiled-settings consistency. The pure local suite separately passed 34 tests
and 51 subtests, including metadata translation extraction.

One existing full-UI alias identity test is excluded: it initializes real UI
messaging and cannot find `deviceState` inside the private test namespace.
Direct tests of the production Tici and Mici setting callbacks pass with onroad
and engaged state. One optional JSON Schema validator test is skipped because
`jsonschema` is not installed; compiled-source parity and standalone compiler
checks pass. This is not a complete native UI startup or road test.

A read-only 30-cycle device benchmark of all 56 keys in 12 groups measured
6.869 ms mean and 11.701 ms maximum storage-read time per full cycle. Reads stay
in the background worker, not the steering-output loop. Python syntax, schema
consistency and whitespace checks also pass (34 changed Python files parsed).
The installed C4 source still reports commit `0db9efcd7e` after validation.

## Highway evidence

Source logs: high-rate `rlog.zst` files, route 5a segments 13–14 and route 5b
segment 16. Times below are seconds since route start, not wall-clock time.
Both selected windows contain active PID control above 50 mph, no recorded
driver steering override, no turn signals and no recorded steering fault.
Every selected sample passed freshness checks for car state, calibrated yaw,
vehicle roll and lane-centering diagnostics.

| Measurement | `0000005a--8cecadb216` | `0000005b--b351e105bb` |
| --- | ---: | ---: |
| Window | 14:03–14:15 | 16:22–16:34 |
| Samples | 1,195 | 1,194 |
| Speed | 61.83–62.94 mph | 50.91–55.61 mph |
| Largest sample gap | 16.5 ms | 16.3 ms |
| Recorded lane-centering strength at route start | 1.0 | 0.3 |
| Best-fit torque share | 10% | 10% |
| Reconstructed-command correlation | 0.99683 | 0.99921 |
| Reconstructed-command RMS error | 0.004176 | 0.002216 |
| Observed command fluctuation RMS, 0.1–1 Hz | 0.019662 | 0.051117 |
| Weighted P/I/F fluctuation RMS | 0.005308 | 0.015642 |
| Inferred torque-branch contribution fluctuation RMS | 0.016152 | 0.036540 |

These are normalized command units, not measured physical EPS motor torque.
Component RMS values do not add directly because the components are correlated.
The fit assumes an unknown but constant torque-controller integral over each
short window; it is not direct telemetry of the blend's internal state.

Both route-start records contain a 10% torque share, lateral-acceleration factor
10 and highway friction 1.0. The September 12 handcrafted preset explicitly
sets low, standard and highway blend friction to 1.0. This is separate from
the native torque-controller override friction. The generic blend resolver's
highway default is 0.06; neither default nor preset was changed in this pass.

Within the friction ramp, the legacy branch applies friction proportional to
lateral-acceleration error, saturating at an error magnitude of 0.3 m/s².
Consequently even a 10% branch weight can produce substantial fluctuating
correction when its friction value is 1.0. The logs support that mechanism.
They do not exclude interacting delay, model-path or P/I/F effects.

## Recorded-input candidate comparison

The production `ClassicTorqueCandidate` was run with recorded desired curvature,
speed, calibrated yaw and roll, with only highway friction changed. It retained
the actual speed-band handoff, integral evolution and internal anti-windup.
Initial integral was fitted, not logged. Both frozen and evolving integral
assumptions were checked because the external safety-limited flag was not
reconstructed. Their results were very close. The table uses evolving integral.

| Highway friction | 5a fluctuation RMS | 5a mean command | 5b fluctuation RMS | 5b mean command |
| --- | ---: | ---: | ---: | ---: |
| 1.0, recorded baseline | 0.019496 | -0.13903 | 0.051098 | 0.09185 |
| 0.3, candidate | 0.009611 | -0.11988 | 0.027365 | 0.08096 |
| 0.1, comparison | 0.007221 | -0.11402 | 0.020800 | 0.07776 |
| 0.06, comparison | 0.006806 | -0.11285 | 0.019526 | 0.07712 |

At 0.3, modeled command fluctuation falls approximately 51% and 46%, while
mean command magnitude falls approximately 14% and 12%. This tradeoff matters:
reducing fluctuation alone is not success if curve tracking gets weaker.
The existing controller's output is reconstructed closely, but recorded-input
counterfactuals keep vehicle motion fixed. They cannot predict the car's new
response, prove closed-loop stability, or establish a safe road tune.

## Next validation boundary

The isolated comparison supports testing highway friction independently of the
overall 10% blend share. It does not justify raising all gains, changing steer
ratio, weakening driver override, or shipping a new global preset. A highway
friction value of 0.3 is an initial candidate for controlled vehicle validation,
not a recommended public-road setting or an applied change.

First validate the live-only build without changing the tune. Any subsequent
vehicle comparison must hold the other settings constant, verify the applied
value, and evaluate curve tracking, command/yaw oscillation, angle error and
required interventions together. Use a qualified driver and controlled test
conditions; do not reproduce violent takeovers or adjust settings as the driver.
No onroad test, installation or release publication was performed in this analysis phase.

Reproduction script: `C:\Openpilot Workspace\Build Reports\2026-09-13\civic_highway_blend_trace.py`.
It reads logs under an offroad guard and does not publish controls or write Params.
