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
- **Firmware** requires an exact recognized `HondaVgrProfile`. EPS Table A supplies relative shape only. Where the exact car and EPS have a rack map (`honda_rack_map.py`), that map is the absolute anchor: yaw-measured for the Clarity TRW-A020, Civic Bosch TBA-C020, Civic TEG-A010 (and the TBA-A030, the same car) and Insight TXM-A040, predicted from the car's published specs for the Civic Bosch TBA-C120, Civic hatch TGG-A120 and CR-V TLA-A040 (see below). Otherwise immutable `CP.steerRatio` is. Unsupported firmware resolves once to CP-static fallback; no family match is borrowed, and a map applies only to the car/EPS images it lists (one image covers another only when it is the same car).

## Raw Clarity provenance

- Source commit: `54f74ae3e5973aa681904780f8cac140870a2b5f`
- Path: `sr-capture/clarity-sr-angle-5deg-HONDA_CLARITY.csv`
- Blob: `8a96cab2b8d5fcfa055709e997bea38e3f5724b0`

Bin centers are `2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5, 52.5, 57.5, 62.5, 67.5, 72.5, 77.5, 82.5, 87.5, 92.5, 107.5, 182.5, 217.5, 247.5` degrees. Their raw-domain medians are `19.679678, 20.665984, 19.948804, 19.330348, 19.362985, 19.307147, 19.150893, 18.394874, 18.300584, 18.578655, 18.087309, 17.979249, 18.036352, 17.710230, 17.497041, 17.279111, 17.025118, 17.088272, 16.797072, 16.530043, 15.739778, 15.319622, 15.279368`. Runtime prepends angle zero with the first median, then appends the separately audited `435.7` / `15.435171905851` near-lock anchor.

The archived medians use `theta / atan(wheel_angle)`, while openpilot's vehicle model expects a small-angle ratio. At the clamped absolute query angle `theta`, runtime therefore returns `theta / tan(theta / raw_ratio)` (radians), with the raw ratio as the zero-angle limit. This yields `14.8701034355` at `247.5` degrees, `14.1656734608` at `435.7` degrees, and about `14.1751986062` at the Clarity's `433.8`-degree half-lock. Full hashes, extraction gates, segment IDs, limitations, and the independent historical fit cross-check are recorded in [`CLARITY_RAW_STEER_RATIO_EVIDENCE.md`](../features/lateral/CLARITY_RAW_STEER_RATIO_EVIDENCE.md).

## Measured rack maps (Firmware)

A rack map is fitted against the car's own VSA yaw sensor (0x94, scale checked against GPS heading) with
JamesL787 `tools/lateral/fit_rack_map.py`, in VehicleModel's form with both of its constants measured:
`lin = R(angle) * L * [k (1 - sf v^2) - g sf roll]`, where `lin` is Table A's linear angle of the physical wheel
angle. `R` is the effective rack ratio by wheel angle after Table A (the mean of left- and right-turn medians, so an
angle offset cancels) and `sf` the slip factor, fitted from how `R` changes with speed inside one angle band.

| Car / EPS | Ratio near centre -> largest angle | Slip factor | CP ratio it replaces | Routes |
| --- | --- | --- | --- | --- |
| Clarity TRW-A020 | 17.34 -> 16.02 (400 deg) | -0.0005 | 16.5 | 341-36b |
| Civic Bosch TBA-C020 | 14.93 -> 14.27 (283 deg) | -0.00065 | 15.38 | 294/289/2b7/2c6/2d4/1b8/251 |
| Civic TEG-A010, TBA-A030 (the same 2016-18 sedan, same Table A) | 14.16 -> 13.78 (293 deg) | -0.00067 | 15.38 | 0000012d-00000139 (0000013d agrees) |
| Insight TXM-A040 | 17.86 -> 17.17 (221 deg) | -0.00066 | 15.0 | 0000001e |

With a single-source Firmware rack map selected, the Firmware controller, curvature-measuring controllers and
controlsd's current-curvature measurement use the full map (`angle_from_curvature`, `curvature_from_angle`), including
its slip factor. Controlsd first updates VehicleModel from the frame's accepted snapshot, then passes the raw wheel
angle, separate angle offset, speed and roll through that same selection; other modes retain their VehicleModel
formula. Speed-free paths (lane-change shaping and a hybrid's Firmware source) still use the same ratio by angle
without the measured slip factor, through VehicleModel at the CP ratio.
On the TEG, CP's 15.38 delivered 6-11% more curvature than asked on the owner's drives, most in slow turns past
150 deg; the map holds the measured curvature within ~1-3%.

## Spec-predicted rack maps (Firmware)

Every measured map above is Table A, then a tan, then one centre ratio R0: `k L (1 - sf v^2) = tan(lin / R0)`, within
2% from 15 to 230 deg on all four cars. For an image nobody has measured, `honda_spec_plant.py` predicts R0 from the
road-wheel angle at lock that Honda publishes (lock-to-lock turns and Honda's steering ratio, which is the ratio at
lock) through that image's own Table A, `R0 = 1.149 * lin(lock) / road angle at lock`, and the slip factor from the
axle loads, `sf = -0.0055454 * (m_front^0.2 - m_rear^0.2) / L`. Both constants are the mean over the four measured cars.
The driver's 80 kg is added once: 50 kg on the front axle and 30 kg on the rear. The slip coefficient was refitted
to the same four measured maps after correcting the original fallback formula's duplicate front-axle allocation;
the measured maps themselves are unchanged.
Held out one car at a time, R0 lands within 1.6% rms (2.5% worst) and the slip factor within 10%. The Insight and the
TEG share published geometry yet measure 4.4% apart, so published specs cannot do better than ~2.5%; a car's own
measurement replaces its spec map. The tables' provenance says `spec`.

| Car / EPS | Specs (lock turns, Honda ratio) | Ratio near centre -> lock | Slip factor |
| --- | --- | --- | --- |
| Civic Bosch TBA-C120 (2019-21 sedan) | 2.22, 10.94 | 14.47 -> 12.96 (400 deg) | -0.000675 |
| Civic hatch TGG-A120 (Sport) | 2.11, 11.12 | 14.88 -> 13.52 (380 deg) | -0.000624 |
| CR-V TLA-A040 (2017-19) | 2.30, 12.3 | 16.82 -> 15.33 (414 deg) | -0.000589 |
