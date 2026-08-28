# Steer-ratio mode reference

This is the technical provenance and fallback contract behind the four user-facing steer-ratio choices.

## Persistent contract

- `NrdrSteerRatioMode`: `0` Manual, `1` Comma, `2` NRDR raw, `3` Firmware.
- `NrdrSteerRatioManualCenter`: global manual center value, default `15.38`.
- `NrdrSteerRatioManualFinal`: global manual final value, default `10.93`.

The three values are read in one snapshot. Controls latch the complete resolved selection while lateral control is active, so measured-curvature and PID desired-angle paths cannot observe different modes or endpoints in one active interval.

## Mode semantics

- **Manual** linearly interpolates the two global values against absolute measured steering-wheel angle only for exact supported Honda endpoint-metadata fingerprints. Unsupported Hondas and non-Hondas resolve to CP-static fallback and the sliders are disabled. There is no lane-change fade.
- **Comma** uses the last valid, finite `vehicleParameters.steerRatio` as one scalar. It uses immutable `CP.steerRatio` before the first valid sample and holds its last valid sample across transient message invalidity.
- **NRDR raw** is available only for exact `HONDA_CLARITY`. It preserves the non-monotonic logged medians and linearly interpolates between retained bin centers, including unevidenced gaps. It endpoint-clamps at `15.279368` after `247.5` degrees. Unsupported fingerprints resolve once to CP-static fallback; no related-car curve is borrowed.
- **Firmware** requires an exact recognized `HondaVgrProfile`. EPS Table A supplies relative shape only, so immutable `CP.steerRatio` is the absolute center anchor. Unsupported firmware resolves once to CP-static fallback; no family match is borrowed.

## Raw Clarity provenance

- Source commit: `54f74ae3e5973aa681904780f8cac140870a2b5f`
- Path: `sr-capture/clarity-sr-angle-5deg-HONDA_CLARITY.csv`
- Blob: `8a96cab2b8d5fcfa055709e997bea38e3f5724b0`

Bin centers are `2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5, 52.5, 57.5, 62.5, 67.5, 72.5, 77.5, 82.5, 87.5, 92.5, 107.5, 182.5, 217.5, 247.5` degrees. Their medians are `19.679678, 20.665984, 19.948804, 19.330348, 19.362985, 19.307147, 19.150893, 18.394874, 18.300584, 18.578655, 18.087309, 17.979249, 18.036352, 17.710230, 17.497041, 17.279111, 17.025118, 17.088272, 16.797072, 16.530043, 15.739778, 15.319622, 15.279368`. Runtime prepends angle zero with the first median.
