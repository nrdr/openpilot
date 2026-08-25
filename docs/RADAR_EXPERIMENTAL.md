# Honda Bosch-A radar decoder

NRDR includes an experimental decoder for the factory radar used by supported plain Honda
Bosch-A platforms. The feature is controlled by `HondaBoschARadar` and is enabled by default.

The decoder is active only while the vehicle retains stock Honda longitudinal control. When
openpilot longitudinal control is enabled, the normal Honda initialization path silences the
radar ECU, reports radar unavailable, and does not construct this decoder. This feature must
not be presented as an openpilot-longitudinal radar source or as preserving factory AEB while
openpilot longitudinal control is active.

The radar object format is reverse-engineered. Its range, relative speed, azimuth, slot
assembly, validity, and stale-track behavior are covered by offline tests, but every supported
vehicle has not yet been road-validated. If displayed tracks do not agree with real traffic,
turn `HondaBoschARadar` off before driving again and preserve the route logs for analysis.

The historical Civic-only decoder and its incompatible DBC are retained in the
`nrdr-development-archive-08.24.2026` archive, not in this branch.
