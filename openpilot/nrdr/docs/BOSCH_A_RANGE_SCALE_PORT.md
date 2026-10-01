# Bosch-A range-scale port — September 13, 2026

Ported from [JamesL787/openpilot commit 753fe43726f5d3d69a4b40fcd20fb97bb68f44d5](https://github.com/JamesL787/openpilot/commit/753fe43726f5d3d69a4b40fcd20fb97bb68f44d5),
"honda: set Bosch-A range scale from firmware, not a single tape point".
The user authorized this radar-specific rollout separately from the earlier
lateral changes.

## Scope

- Bosch-A raw range now uses `raw_range / 16 - 3.0` meters, replacing the
  previous scale of `0.05712` with `0.0625` meters/count.
- The source commit derives the scale by composing its firmware observations
  `q16 = 8 * raw_range` and `(q16 - n) / 128`. Its supporting firmware analysis
  and route statistics are the contributor's evidence, not a new independent
  firmware or road validation performed for this port.
- The existing `-3.0` offset remains. This does not implement reading a radar's
  per-unit calibration word or establish that the retained offset is exact for
  every radar.
- All 16 DBC range aliases use the same scale and offset. Runtime still consumes
  raw fields, so this does not apply the conversion twice.
- Donor tests retain NRDR's current `deprecated.measured` schema access. A
  redundant donor assertion is consolidated, and additional tests pin all 16
  DBC aliases at representative near/far raw values.

No parser enablement, bus assignment, track-validity or velocity-authority
policy is changed. Nidec radar, lateral control, steering tuning, low-pass
settings, actuator-delay settings, model selection, and EPS firmware are outside
this change. Distance-derived lateral projection and range-ratio fallback
velocity naturally reflect the corrected range; native relative velocity's
scale is unchanged.

## Release boundaries

The root gitlink and opendbc source must be deployed together. The intended
targets are the C4, `nrdr-nightly`, and `nrdr-staging-09.13.2026`, with their source
development branches synchronized. `350` is explicitly frozen unless the user
names it in a separate change request; this rollout must not move it. `nrdr-clean`
and older staging refs are also excluded.

Preserve existing settings and validate under an offroad/no-output guard.
Native synthetic radar/decoder and integration tests verify software behavior;
they are not a substitute for a Bosch-A-equipped vehicle's controlled validation.
The currently connected Nidec Civic cannot physically validate Bosch-A radar.
