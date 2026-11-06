# NRDR longitudinal vehicle isolation

## Honda MVL priority (November 6, 2026)

With **Live Learning Gas** selected, Honda openpilot longitudinal uses the
pinned MVL controller and planner, not the custom controller with default
slider values. Selection is latched at startup; change it while parked and
restart. It applies to Nidec PCM, Bosch, and gas-interceptor control.

- Source: MVL root `376c44b5731b2655e5c2f301b73c9729eb499e91` and its
  opendbc pin `3fec9a418a659de31d7b1f494193161697a35071`.
- Aggressive, Standard, and Relaxed copy MVL's complete profiles, including
  following distances. Only Econ retains the fixed nrdr longer-following,
  gentler acceleration/jerk profile.
- Conflicting custom longitudinal settings are locked and ignored, not erased.
  Custom tune files, PCM shaping, wind-brake overrides, PID scaling, brake-authority
  overrides, and optional Sunny acceleration/target shaping cannot change this mode.
- Saved learning remains intact. The mode includes MVL's gas, wind, PCM response,
  brake feedback and platform-specific command paths; it is not just a gas learner.
- Experimental Engine Braking and Set-Speed Overshoot Allowance are retired in
  both modes, including their parameter registrations and active controller code.
- MVL cruise defaults also apply: the software ceiling is 145 km/h and initial
  software SET has the donor's 40 km/h floor. Hardware-owned PCM cruise targets
  and engagement guards remain hardware-owned; this is not the custom 0-mph SET
  experiment.
- The donor's model/e2e candidate participates in longitudinal planning regardless
  of the saved Experimental Mode toggle. That toggle is locked in MVL mode;
  retaining the same driving model does not disable its longitudinal candidate.
- Lateral tuning, selected driving model, vehicle safety and driver overrides are
  unchanged. Qualified Clarity interceptor hardware retains its existing calibrated
  brake/hold protection; that is an explicit hardware exception, not donor parity.

See `opendbc_repo/opendbc/car/honda/MVL_LONGITUDINAL.md` and
`openpilot/selfdrive/controls/lib/longitudinal_mpc_lib/mvl_manifest.json` for
source hashes, exact scope, integration differences and test contracts.
Parity tests establish software behavior against those pins, not road safety,
successful convergence of a particular car's learning, or the author's private
settings. The unchanged driving model and retained learned values still affect
the result. Do not infer that the reported braking issue is resolved from these
tests alone.

## Non-Honda isolation

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
