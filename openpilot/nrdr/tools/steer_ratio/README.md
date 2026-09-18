# Steer-ratio investigation

Read-only analysis of recorded drives. The tools never apply ratios, alter device
settings, or start control processes. Run resource-intensive scans on a workstation
or with the device continuously verified offroad. Do not tune while driving.

## Which tool?

- `by_angle`: quick yaw/speed/angle coverage and logged scalar-learner inspection.
- `correction`: full-log, vehicle-model-aware investigation with independent
  mapping, command tracking, matched-angle speed comparisons, and rejection reports.
- `draft`: explicit offline provisional curve builder from `sr_samples.csv.gz`.
  Uses broader command-conditioned steady observations with per-anchor coverage,
  route/configuration balancing, explicit interpolation and unmeasured endpoint
  holds. This is not a live learner, independent rack calibration or installer.
  Requires an exact fingerprint/EPS pair and one known vehicle-model geometry;
  the current draft bounds are 8-25 effective SR, not universal car support.
  See `features/lateral/CIVIC_TEG_PROVISIONAL_STEER_RATIO_EVIDENCE.md` for v0's
  evidence and limitations. Future profiles require their own review and tests.

Example, using a new output directory outside the checkout:

```sh
python -m openpilot.nrdr.tools.steer_ratio.correction \
  '/path/to/route-prefix--*/rlog.zst' \
  --output-dir /path/to/new-analysis \
  --mapping-max-speed 33 --angle-bin 5 --speed-bin 5
```

Speeds are **m/s**; 33 m/s is about 74 mph. The default independent-mapping
ceiling remains 15 m/s (about 34 mph). Raising that ceiling is an explicit highway
analysis choice, not a relaxation of yaw uncertainty, steering rate, acceleration,
roll, parameter validity, or steady-turn dwell requirements. It does not request
driving at a particular speed. Reuse existing safely collected logs.

## Questions the results answer

1. **Does measured angle produce the curvature the vehicle model predicts?**
   `sr_angle_speed.csv` separates angle, speed and turn direction. It includes
   effective SR with the logged tire/roll model, simple kinematic SR, zero-roll and
   unit-stiffness variants, and the result before the optional center-bias fit.
   Manual steering is allowed in this cohort; requested angles are not used.
2. **Does the remaining mismatch change with speed at comparable angles?**
   `sr_matched_speed.csv` pairs the same route, direction, vehicle/configuration
   and 1-degree angle cell across observed speed bands. Median angles must differ
   by no more than 0.25 degrees. Each side needs at least three occupied seconds.
   Two routes with bilateral matches are required for a supported comparison.
   Empty output means insufficient overlap, **not** speed independence.
3. **Is the wheel falling short of its request, or is the request itself too small?**
   `sr_tracking_vs_mapping.csv` keeps actual/requested angle tracking separate from
   the tracking-cancelled curvature mapping factor. It also reports sensitivity to
   +/-100 ms of command pairing delay. Large timing sensitivity or missing paired
   evidence limits interpretation; these are observational signatures, not diagnoses.

No speed correction is fitted or recommended automatically. A repeatable residual
can still come from tire stiffness, roll, sensor calibration, timing, compliance,
or another missing part of the model. Existing speed-dependent tire dynamics must
not be counted a second time as a speed-dependent rack ratio.

## Cross-car safeguards

- No Honda/Civic ratio table or tuning preset is hard-coded into the analysis.
  It uses geometry and tire parameters recorded in each car's `carParams`.
- Ratio and response summaries separate fingerprint, EPS firmware identifier,
  vehicle-model geometry hash, software revision and selected saved tuning values.
  Missing firmware is explicitly `unknown`; it cannot distinguish unreported
  firmware changes. For modified EPS firmware, keep external flash/build records.
- Settings are **recorded snapshots**, not proof that a historical controller
  consumed them live. Unlogged setting changes cannot be reconstructed. Compare
  controlled, stable-setting runs before acting on a suggested association.
- Invalid pose/state and rejected mapping observations break steady dwell.
  Required log streams are sorted by event timestamp before pairing; logger
  arrival order is not assumed to be chronological.
  Repeated frames do not increase independent support: aggregation balances
  occupied seconds first, then route/direction medians. Occupied seconds and dwells
  are coverage measures, not independent experiments or formal confidence intervals.
- Center-bias fits never cross route/configuration boundaries; weak or boundary
  fits are not applied. The unadjusted estimate remains available for comparison.
- Rear-steering geometry is currently rejected, not silently approximated.
  Missing/invalid geometry is also rejected. This implementation expects the
  current openpilot event schema and standard steering-angle/yaw conventions.
  Other log schemas need an explicit adapter and tests.
- Steering faults remain excluded by default. `--include-faulted-mapping` retains
  otherwise-valid angle/yaw measurements in **separate, diagnostic-only cohorts**.
  This allows investigating manually driven circles after an LKAS fault without
  labeling motion sensors invalid or mixing these observations with fault-free
  evidence. Command-response analysis still excludes steering faults.
- The inherited model inversion accepts effective ratios between 5 and 40.
  Vehicles outside that range need explicitly validated model/gate extensions;
  the tool does not claim universal vehicle compatibility.
- Controllers that do not log a meaningful requested steering angle cannot support
  the tracking comparison. They may still support independent yaw/angle mapping.
- High-angle results remain effective, model-dependent ratios. The dynamic
  bicycle model is not an exact rack-geometry measurement at large road-wheel angles.

## Reproducibility and existing outputs

`sr_summary.json` (schema 2) stores selected thresholds, source manifests, read
failures and all summary rows. Per-sample compressed diagnostic files preserve
route/time provenance. Failed segments produce a nonzero exit status; partial
controller samples from that segment are discarded. Coverage attrition can still
include observations seen before a read error, so an incomplete scan must be
investigated before comparing results. Existing files are protected unless the
operator explicitly passes `--force`.

The original strict, manual, transient and stage/rejection outputs remain available.
Strict command-conditioned samples are **not** independent geometry evidence.
The broad angle-only speed-strata warning is a screening check; use the finer
matched-speed report for the angle-versus-speed question.

`--delay` is an explicitly selected command-response alignment, not an estimate of
EPS actuator delay. It does not time-shift the independent steady-state mapping
cohort. +/-100 ms sensitivity is a robustness check, not a fitted delay confidence
interval. Abrupt/transient turns remain outside steady mapping recommendations.

Tests include fixed-SR dynamics across several vehicle geometries, injected speed
residuals, tracking-only errors, angle/speed confounding, mixed firmware/settings,
invalid telemetry, dwell interruption, frame-density imbalance and lag sensitivity.
No result is a road-safety validation or permission to apply a new tune.
