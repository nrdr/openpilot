# Steer-ratio mode reference

This is the technical provenance and fallback contract behind the four user-facing steer-ratio choices.

## Persistent contract

- `NrdrSteerRatioMode`: `0` Manual, `1` Comma, `2` NRDR raw, `3` Firmware.
- `NrdrSteerRatioManualCenter`: global manual center value, default `15.38`.
- `NrdrSteerRatioManualFinal`: global manual final value, default `10.93`.
- `NrdrSteerRatioHybrid`: opt-in angle-based hybrid, default OFF. Existing mode becomes source A; no migration changes it.
- `NrdrSteerRatioSourceB`: source beyond the blend; same 0–3 enumeration, default Firmware (`3`).
- `NrdrSteerRatioBlendStart`: absolute steering-wheel angle where the fixed 5-degree blend begins, 0–180 degrees, default 25. This default is a configuration placeholder, not a recommended tuning point.

The six values are published as one background snapshot and captured once per control frame. Measured-curvature and desired-angle paths use the same selection. The background polling cycle is 0.5 seconds; this is not proof of end-to-end Sunnylink delivery or consumption while driving. Separately saved edits are not a storage transaction. Torque-controlled cars retain the existing one-second tuning-edit transition and all existing override/curvature/jerk/torque limits. Configure experimental hybrid settings while parked. No road validation is claimed.

## Hybrid geometry

UI order is Enable Hybrid, source A, blend-start slider, source B. Sunnylink uses the same dropdown widget for both sources; the device uses its native source selectors. Both Manual sources share the existing manual endpoint values. Missing car/EPS profiles are not substituted from another car.

Hybrid converts both sources into equivalent linear steering angle at the immutable CP ratio. It blends those mappings, not raw firmware divisors or torque outputs. The 5-degree transition is a strictly increasing piecewise-linear table with 101 nodes weighted by smoothstep. Node monotonicity guarantees that the shipped transition itself is invertible. Outside the transition, each source's exact forward map and inverse are used. Left/right are symmetric; unwind follows the same mapping. No speed correction is introduced.

For measured sources, this uses a self-consistent inverse of the complete angle-dependent curve. It is not the legacy single-source desired-angle approximation that holds ratio at the current measured angle. Existing single-source behavior remains unchanged when Hybrid is OFF.

Comma sources capture the last valid learner ratio once per control-frame selection. New values rebuild and revalidate the blend; unchanged configurations reuse cached geometry. Learned ratio is not implicitly used when neither source is Comma. Firmware in either source retains the existing firmware/NNLC incompatibility guard for the entire hybrid mode.

Invalid source choices, invalid angles, and blends that reverse/flatten the mapping are rejected. While active, the last accepted geometry is retained. At startup or when inactive, an invalid hybrid resolves to stock fallback. This avoids installing a non-invertible map, but monotonicity alone is NOT evidence of stable vehicle control: even an increasing 5-degree blend may have a steep local gain.

`nrdr_live_settings_consumed` events with component `steer_ratio_geometry` distinguish requested source settings, effective selection, and rejection reason. UI descriptions are configured previews, not live-consumption acknowledgements. A Comma-based UI preview uses CP as its anchor; runtime uses the held learner value and can therefore accept/reject differently. Full saved/consumed frontend acknowledgement remains separate work.

## Mode semantics

- **Manual** linearly interpolates the two global values against absolute measured steering-wheel angle only for exact supported Honda endpoint-metadata fingerprints. Unsupported Hondas and non-Hondas resolve to CP-static fallback and the sliders are disabled. There is no lane-change fade.
- **Comma** uses the last valid, finite `vehicleParameters.steerRatio` as one scalar. It uses immutable `CP.steerRatio` before the first valid sample and holds its last valid sample across transient message invalidity.
- **NRDR Measured Curve** uses a fixed matching car/EPS profile, not live learning. `HONDA_CLARITY` preserves every original non-monotonic logged median through `247.5` degrees and adds one separately audited bilateral near-lock anchor at `435.7` degrees. It interpolates the raw-domain evidence, converts it into the small-angle ratio expected by `VehicleModel`, and clamps beyond `435.7` degrees. `HONDA_CIVIC` with exact TEG-A010 EPS uses the provisional September 13 vehicle-model-domain curve, with data-derived anchors at 3.292–58.671 degrees and endpoint holds outside that range. Unsupported car/EPS combinations resolve to CP-static fallback; no related-car curve is borrowed.
- **Firmware** requires an exact recognized `HondaVgrProfile`. EPS Table A supplies relative shape only, so immutable `CP.steerRatio` is the absolute center anchor. Unsupported firmware resolves once to CP-static fallback; no family match is borrowed.

## Raw Clarity provenance

- Source commit: `54f74ae3e5973aa681904780f8cac140870a2b5f`
- Path: `sr-capture/clarity-sr-angle-5deg-HONDA_CLARITY.csv`
- Blob: `8a96cab2b8d5fcfa055709e997bea38e3f5724b0`

Bin centers are `2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5, 52.5, 57.5, 62.5, 67.5, 72.5, 77.5, 82.5, 87.5, 92.5, 107.5, 182.5, 217.5, 247.5` degrees. Their raw-domain medians are `19.679678, 20.665984, 19.948804, 19.330348, 19.362985, 19.307147, 19.150893, 18.394874, 18.300584, 18.578655, 18.087309, 17.979249, 18.036352, 17.710230, 17.497041, 17.279111, 17.025118, 17.088272, 16.797072, 16.530043, 15.739778, 15.319622, 15.279368`. Runtime prepends angle zero with the first median, then appends the separately audited `435.7` / `15.435171905851` near-lock anchor.

The archived medians use `theta / atan(wheel_angle)`, while openpilot's vehicle model expects a small-angle ratio. At the clamped absolute query angle `theta`, runtime therefore returns `theta / tan(theta / raw_ratio)` (radians), with the raw ratio as the zero-angle limit. This yields `14.8701034355` at `247.5` degrees, `14.1656734608` at `435.7` degrees, and about `14.1751986062` at the Clarity's `433.8`-degree half-lock. Full hashes, extraction gates, segment IDs, limitations, and the independent historical fit cross-check are recorded in [`CLARITY_RAW_STEER_RATIO_EVIDENCE.md`](../features/lateral/CLARITY_RAW_STEER_RATIO_EVIDENCE.md).
