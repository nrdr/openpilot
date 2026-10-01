# NRDR longitudinal vehicle isolation

Non-Honda cars use the existing Sunnypilot/MVL longitudinal baseline, not the
NRDR controller with nominal/default slider values. This does not force factory
ACC, change platform safety limits, or change lateral control.

The behavioral reference is the parent of the NRDR architecture port:
`66ad9fac65f577940a9cbbe269104fb8177f2f76`.

The shared policy in `features/longitudinal/policy.py` enables Honda behavior and
otherwise fails closed. `TUNED_NON_HONDA_CARS` is intentionally empty. A future
non-Honda tune must explicitly approve an exact `(brand, carFingerprint)` pair
in code, with its own tuning and regression tests. There is no global opt-in
parameter, and old settings or `/data/nrdr_long_tune.json` cannot authorize a car.

## Bypassed on baseline cars

- NRDR PID gains/scales, feedforward changes, stop/launch state machine and tune file.
- NRDR acceleration ceilings, overspeed/mismatch corrections, stop thresholds,
  launch boost, and global turn/coast output limiting/smoothing.
- NRDR MPC weights, following gaps, lead/model shaping and extra FCW gate.
- NRDR DEC hysteresis/dwell changes and speed-limit assist/map extensions.
- The fourth Econ personality and NRDR distance-button reservation/submode.

Baseline Smart Cruise Control, Speed Limit Assist, Experimental/DEC features,
platform longitudinal enablement, and existing safety/engagement restrictions
remain intact. They still follow their normal settings.

Honda behavior remains enabled. Missing/unknown vehicle identity selects the
baseline. The policy is chosen at process initialization; this is not a live
vehicle-mode switch.

## Three-personality handling

Baseline cars use Aggressive, Standard, and Relaxed. A stale saved Econ value is
interpreted as Relaxed (the longest baseline gap), not wrapped to Aggressive.
The distance button cycles three settings and HUD requests stay within 1-3 bars.
NRDR tuning controls and Econ are unavailable for unsupported vehicles.

## Release boundary

Source changes alone do not update an installed release. The frozen `350` branch
and vehicles using it must not be updated without explicit authorization.
Offline parity checks are not device, simulator, or road validation.

## Local verification (2026-09-18)

- 143 tests and 3 subtests passed across non-Honda baseline parity, NRDR MPC,
  tune-file handling, DEC, and Sunnylink source checks.
- Changed Python files passed Ruff and bytecode compilation; generated
  Sunnylink JSON matches its source.
- Native controller/personality and full Sunnylink runtime tests remain pending:
  this Windows environment lacks the working Cap'n Proto/native runtime.
- No device was modified. Remote `350` was read-only verified at
  `aeac2c6bf6e56ac91433997c0a25aed6edf6d51f`.
