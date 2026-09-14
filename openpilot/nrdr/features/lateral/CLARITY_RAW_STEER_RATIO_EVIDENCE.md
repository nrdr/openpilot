# Clarity raw steer-ratio evidence

This file records the immutable inputs behind `CLARITY_RAW_STEER_RATIO`. It is
evidence for the shipped constants, not a runtime input or a claim that the
curve learns while driving.

## Original angle bins

- Source commit: `54f74ae3e5973aa681904780f8cac140870a2b5f`
- Source path: `sr-capture/clarity-sr-angle-5deg-HONDA_CLARITY.csv`
- Source blob: `8a96cab2b8d5fcfa055709e997bea38e3f5724b0`
- Synchronized CSV SHA-256: `861D8E00B286D5412C6C6D3908564789270A2026EC824EB6F49BD11793D96672`
- Extractor SHA-256: `5CE250872F7607409E3562FECC323CC1FF69F3F20351F46BA72FA5887A7185C6`

Every original angle and ratio literal is retained unchanged. Those ratios are
in the archived `abs(theta) / atan(wheel_angle)` domain; they are not directly
the small-angle ratio consumed by openpilot's `VehicleModel`.

## Bilateral near-lock anchor

- `cache.pkl` SHA-256: `1A633B31B91EDFFF9CE9D4F83B240566F21476B028D02960E7B14E44839E725B`
- `cache_meta` SHA-256: `FAC9AB6F9C4E4DDACDBFC43911F7694DD8E7B07759C8C150F6F4DA12DBAF1CAE`
- Cohort: 425–440 degrees, 825 samples, 598 left / 227 right, four routes and five segments
- Retained anchor: 435.7 degrees, raw-domain ratio `15.435171905851`
- Raw-domain IQR: `15.376501675`–`15.491261584`; maximum observed angle: 438.9 degrees
- Direct VehicleModel-domain median: `14.161368890`

Segments:

- `0000007e--d4a413c4c4--296`
- `00000080--ddc219bb73--4`
- `00000081--49da42be4e--18`
- `0000008a--91b97700bb--5`
- `0000008a--91b97700bb--6`

The extractor used calibrated yaw (calibration roll/pitch) and computed
`abs(theta_rad) / atan(2.75 * abs(yaw_rate / speed))`. General gates were speed
3–25 m/s, `pose_ok`, at least 5 degrees steering angle, at least 0.03 rad/s yaw
rate, and a sane raw ratio of 5–40. The near-lock cohort relaxes only the
`latActive` and hands-off gates because lock frames are reported as driver
pressed.

The cache does not contain pair age, `calibrationValid`, or `posenetOK`, so the
anchor is deliberately one robust bilateral cohort rather than a detailed
sparse-bin tail. Runtime linearly bridges 247.5 to 435.7 degrees and clamps at
the anchor beyond that point.

Historical commit `7a9ad65863b713a525bebd932ee87e41448ccf57` is a consistency
cross-check only: its original VehicleModel-domain fit was 14.95 at 234 degrees,
14.35 at 362 degrees, and 14.02 at 450 degrees. It is not treated as raw
physical-rack evidence and none of its sparse 25-degree wiggles are imported.
