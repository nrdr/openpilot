# Civic TEG-A010 measured curve: provisional v0

Version: 2026-09-13. This is a fixed offline draft, **not a live learner and not
road-validated**. It is a starting hypothesis for comparison, not a diagnosis or
a demonstrated fix for highway oscillations, understeer, or actuator delay.

## Scope and source

- Fingerprint: `HONDA_CIVIC`; reported EPS: `39990-TEG-A010` only.
- Vehicle: the owner's 2018 Civic Touring with modified EPS firmware.
- Full-log inputs: `00000059--23041ba9e2`, `0000005a--8cecadb216`,
  `0000005b--b351e105bb` (124 rlog segments, no reported read failures).
- Export: `sr_samples.csv.gz` from the September 13 correction/surface scan.
- Export SHA256:
  `15c8c34551eb6dd9d31e09a9959225dbe1c0e2dbdff5522e62dc1ac9daedec5a`.
- Builder: `openpilot.nrdr.tools.steer_ratio.draft`, schema 1.

EPS identification is a reported part/version string, not a hash of the flashed
binary. It cannot distinguish different custom firmware that reports the same
identifier. Keep the external firmware build/flash record with future tests.
This draft must not be borrowed for Civic Bosch, TGG-A120, A030, or another car.
Runtime and both settings interfaces require the matching reported EPS for Civic.

## Curve and uncertainty

The stored domain is **vehicle-model** effective SR: the angle/yaw inversion
already accounts for the logged tire stiffness, roll and vehicle geometry.
Do not run it through Clarity's raw-angle-to-VM conversion again. No firmware
Table-A shape, manual endpoint, speed correction, or new delay fit is used.

| Absolute steering angle | VM ratio | Origin |
| ---: | ---: | --- |
| 0.000 degrees | 15.8207 | Held from the nearest anchor; unmeasured at zero |
| 3.292 degrees | 15.8207 | Provisional data-derived anchor, 0-5 degree bin |
| 8.783 degrees | 15.6557 | Provisional data-derived anchor, 5-15 degree bin |
| 19.289 degrees | 15.5427 | Provisional data-derived anchor, 15-30 degree bin |
| 35.669 degrees | 15.1964 | Provisional data-derived anchor, 30-50 degree bin |
| 58.671 degrees | 14.7617 | Provisional data-derived anchor, 50-75 degree bin |
| Beyond 58.671 degrees | 14.7617 | Nearest-anchor hold; unmeasured extrapolation |

Ratios interpolate linearly between anchors and are symmetric left/right.
The builder and runtime reject a model-domain table that would reverse the
angle-to-curvature mapping between anchors.
Holding the last anchor makes the undefined tail explicit; it does **not** imply
that the physical rack becomes constant-ratio. High-angle circle data did not
pass the strict steady-mapping gates, so no high-angle measured anchor is claimed.

## Evidence admitted for a rough draft

The independent steady-mapping report remains sparse: 67 accepted samples and no
supported matched-angle speed comparison. This draft deliberately uses the
broader **command-conditioned** steady cohort (strict and relaxed quality), not
that independent calibration cohort. It requires command output available and
no reported safety limiting. Ratio estimates come from measured angle/yaw and
the logged model, not from multiplying the requested angle by its tracking error.

Aggregation balances frames into occupied-second medians, then configurations
within each route/direction, then route/direction medians. Each admitted bin
needs at least five occupied route/direction seconds, two routes, one route with
both directions, and no more than 15% max/min spread among route/direction
medians. These are provisional screening rules, not a calibration guarantee.

| Angle bin | Occupied route/direction seconds | Routes | Bilateral routes | Ratio spread | Used |
| --- | ---: | ---: | ---: | ---: | --- |
| 0-5 degrees | 949 | 3 | 3 | 11.96% | Yes |
| 5-15 degrees | 648 | 3 | 3 | 7.78% | Yes |
| 15-30 degrees | 313 | 3 | 3 | 3.29% | Yes |
| 30-50 degrees | 52 | 3 | 3 | 2.47% | Yes |
| 50-75 degrees | 26 | 3 | 2 | 1.47% | Yes |
| 100-150 degrees | 1 | 1 | 0 | 0% | No |

Coverage seconds are correlated, not independent trials. The small-angle
estimate is particularly sensitive to angle offset, roll, noise, tire-model
error and selection bias. Configuration balancing cannot undo unlogged live
setting changes. Lack of supported speed comparisons is not proof that no
speed-dependent residual exists; none is fitted in v0.

Near-center v0 is about 2.9% above the stock 15.38 firmware center anchor, but
about 20.9% below the owner's saved manual center of 20.0. Raising SR asks for
more steering angle at the same curvature; this is not a blanket increase in
steering authority and must not be presented as a cure for tracking undershoot.

## Reproduction and future revisions

```sh
python -m openpilot.nrdr.tools.steer_ratio.draft /path/to/sr_samples.csv.gz \
  --fingerprint HONDA_CIVIC --eps-firmware 39990-TEG-A010 \
  --output /path/to/new-civic-draft.json
```

The output preserves source hash, per-anchor coverage, route/direction/configuration
summaries, rejected bins, ratio domain and limitations. It refuses overwrites and
does not read/write device settings or install a profile. The analyzer is
vehicle-parameter-based; this particular runtime table remains Civic-specific.

For a future revision, use additional safely collected logs with recorded firmware
and settings, review independent mapping and tracking separately, and compare
like angles across speeds before fitting a speed term. Replace held/interpolated
sections with supported anchors and version the evidence and literal table
together. Do not silently pool different EPS identifiers or vehicle-model geometry.
Adding a profile never changes the selected mode or the saved manual endpoints.
Choose any experimental mode only while parked; offline tests are not road validation.
