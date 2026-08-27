# Honda Bosch-A radar decoder

NRDR includes an experimental decoder for the factory radar used by supported plain Honda
Bosch-A platforms. The feature is controlled by `HondaBoschARadar` and is enabled by default.

The receive-only decoder remains active with either stock Honda longitudinal control or openpilot
Alpha Long. With stock longitudinal, the decoded objects are perception only. With Alpha Long,
they feed openpilot's lead tracking and therefore its braking and acceleration decisions. Honda's
normal Alpha Long initialization still silences the factory ACC command path and disables factory
AEB/CMBS; the camera-side Bosch-A object stream remains available to this decoder.

The radar object format is reverse-engineered. Its range, relative speed, azimuth, slot
assembly, validity, and stale-track behavior are covered by offline tests, but every supported
vehicle has not yet been road-validated. If displayed tracks do not agree with real traffic,
turn `HondaBoschARadar` off before driving again and preserve the route logs for analysis.

The historical Civic-only decoder and its incompatible DBC are retained in the
`nrdr-development-archive-08.24.2026` archive, not in this branch.

