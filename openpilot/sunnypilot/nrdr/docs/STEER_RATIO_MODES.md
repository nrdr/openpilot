# Steer-ratio mode reference

This is the technical provenance and fallback contract behind the four user-facing steer-ratio choices.

## Persistent contract

- `NrdrSteerRatioMode`: `0` Manual, `1` Comma, `2` NRDR Raw, `3` Firmware.
- `NrdrSteerRatioManualCenter`: global manual center value, default `15.38`.
- `NrdrSteerRatioManualFinal`: global manual final value, default `10.93`.

The three values are read as one snapshot. Controls latch the complete selection while lateral control is active, so the
measured-curvature and desired-angle paths cannot observe different modes or endpoints in one active interval.

## Mode semantics

- **Manual** linearly interpolates the two global values against absolute measured steering-wheel angle only for exact supported
  Honda endpoint-metadata fingerprints. Unsupported cars use the immutable stock `CarParams.steerRatio`.
- **Comma** uses the last finite, validated `vehicleParameters.steerRatio` scalar. It starts from the immutable stock ratio and
  holds the last valid learned value through brief service or learner invalidity.
- **NRDR Raw** is available only for exact `HONDA_CLARITY`. It preserves every published `54f74ae3` atan-domain median and adds
  one bilateral near-lock anchor at `435.7°`. Runtime interpolates those raw estimator values, converts them to the effective
  scalar expected by `VehicleModel`, and endpoint-clamps only after `435.7°`. Unsupported cars use the stock ratio; no sibling
  car curve is borrowed.
- **Firmware** requires an exact recognized Honda EPS profile. The firmware map supplies relative shape only; the immutable stock
  ratio remains its absolute center anchor. Unsupported firmware uses the stock ratio.

## Raw Clarity base provenance

- Source commit: `54f74ae3e5973aa681904780f8cac140870a2b5f`
- Source path: `sr-capture/clarity-sr-angle-5deg-HONDA_CLARITY.csv`
- Git blob: `8a96cab2b8d5fcfa055709e997bea38e3f5724b0`
- Audited synchronized CSV SHA-256: `861D8E00B286D5412C6C6D3908564789270A2026EC824EB6F49BD11793D96672`
- Extractor SHA-256: `5CE250872F7607409E3562FECC323CC1FF69F3F20351F46BA72FA5887A7185C6`

The retained angle knots before the new endpoint are `0, 2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5,
52.5, 57.5, 62.5, 67.5, 72.5, 77.5, 82.5, 87.5, 92.5, 107.5, 182.5, 217.5, 247.5` degrees. Their literal atan-domain
values remain `19.679678, 19.679678, 20.665984, 19.948804, 19.330348, 19.362985, 19.307147, 19.150893, 18.394874,
18.300584, 18.578655, 18.087309, 17.979249, 18.036352, 17.710230, 17.497041, 17.279111, 17.025118, 17.088272,
16.797072, 16.530043, 15.739778, 15.319622, 15.279368`. No original literal was replaced, rounded, or smoothed.

## Bilateral near-lock anchor

The appended endpoint is angle `435.7°`, raw atan-domain value `15.435171905851`, with `825` accepted samples: `598` left and
`227` right across four routes and five segments. Its raw-domain IQR is `15.376501675–15.491261584`, the maximum observed angle
is `438.9°`, and the direct VehicleModel-domain median is `14.161368890`. It comes from these synchronized-cache segments:

- `0000007e--d4a413c4c4--296`
- `00000080--ddc219bb73--4`
- `00000081--49da42be4e--18`
- `0000008a--91b97700bb--5`
- `0000008a--91b97700bb--6`

The cache SHA-256 is `1A633B31B91EDFFF9CE9D4F83B240566F21476B028D02960E7B14E44839E725B`; its metadata SHA-256 is
`FAC9AB6F9C4E4DDACDBFC43911F7694DD8E7B07759C8C150F6F4DA12DBAF1CAE`.

The endpoint uses calibrated yaw from calibration roll/pitch and the same estimator as the original capture:

`raw = abs(theta_rad) / atan(2.75 * abs(yaw_rate / speed))`

Accepted samples use `3–25 m/s`, `pose_ok`, at least `5°` steering, at least `0.03 rad/s` yaw, and a sane raw range of
`5–40`. Near lock, only the lateral-active and hands-off gates are relaxed because those frames report the driver-pressed state.
The cache does not carry pair-age, `calibrationValid`, or `posenetOK`, so those checks cannot be reconstructed and this limitation
is intentionally recorded here.

## Runtime conversion

For an absolute measured angle `theta_deg`, runtime:

1. clamps `theta_deg` to `0–435.7°`;
2. linearly interpolates the raw atan-domain values, including the gap from `247.5°` to the bilateral endpoint;
3. returns the zero-angle limit (`raw`) at zero, otherwise computes
   `theta_rad / tan(theta_rad / raw)` for the scalar expected by `VehicleModel`.

This yields `14.8701034355` at `247.5°`, approximately `14.1751986062` at the Clarity's `433.8°` half-lock, and
`14.1656734608` at and beyond `435.7°`. The old behavior of holding the `247.5°` result through lock is gone.

The `7a9ad65863b713a525bebd932ee87e41448ccf57` fitted curve is only an external magnitude/direction cross-check; none of its fitted
knots are runtime inputs. No `12.72` tail, direct `14.07` fitted endpoint, or sparsely supported intermediate-bin wiggles are used.

The concise immutable evidence record is colocated with the implementation in
[`CLARITY_RAW_STEER_RATIO_EVIDENCE.md`](../CLARITY_RAW_STEER_RATIO_EVIDENCE.md).
