# PTM Controller profiles

This is steering-angle feedback plus an EPS-firmware-inversion feedforward, not
real-time yaw feedback. `NrdrLateralController = 1` is latched at drive startup;
changing it requires offroad confirmation. PIF's Device Yaw Correction is separate.

## November 2026 donor update

Audited against [Biscuit-Labs Honda-PTM-Testing `45e5b91fae`](https://github.com/Biscuit-Labs/openpilot/tree/45e5b91fae934e4f423ee39055efb84d2150c575).
The public name is **PTM Controller**; internal identifiers and saved value `1` are unchanged.
The target is a shared PTM baseline with the StarPilot port: identical core output for identical inputs,
calibrations and tuning. nrdr's optional geometry, lane guidance and Optimized Lane Changes remain fork-specific.
Do not silently retune PTM calibrations when adapting them to sunnypilot.

| Donor change | nrdr integration |
| --- | --- |
| Ridgeline T6Z-A110 rev b5 (`2200525cb9`) | Exact hybrid-comma revision, linear 4096 E4 transport, V850 output scale/P clamp, measured load and rack, and the donor's default prediction/command timing. Earlier comma-only builds are not admitted to this controller. |
| Odyssey THR-A020 (`2eba17325c`) | Exact modified revision, 4096 E4 transport, its own P knots, identity angle geometry and donor spec rack/load. Vehicle calibration and timing remain provisional; no donor road validation yet. |
| CR-V A040/A220 (`3282629883`, `d8ccb1866a`) | Firmware geometry uses the measured A040 rack; A220 reuses that map with inferred provenance. Other steer-ratio modes are unchanged. |
| CR-V A040 town delay (`a08d164a2b`) | Exact donor 0.18/0 s; A220 0.12/0 s. Both use the donor's default prediction schedule. |
| RDX prediction delay (`5fcb966386`) | Staged schedule 0.15/0.40/0.40/0.22/0.30 s. Existing RDX identity/transport restrictions remain; not newly enabled. |

C020 now uses corrected rev-b command/P tables (RWD prefix `df67bf6f`), not the old TargetMapD image.
Clarity uses the donor's hardcoded 0.20/0.10 s command delay (`542ed36dfe`); saved legacy endpoints are
preserved but ignored. C120 uses the donor's exact spec-predicted rack table; Insight uses its piecewise map.
RDX/Odyssey retain internal state for dropouts up to 100 ms, with I frozen and zero steering output;
longer dropouts reset. Other cars still reset on every inactive frame.
Donor AOL/engagement, radar and longitudinal changes are outside this controller update.

New firmware requirements: Ridgeline `39990-T6Z,A110-REVB5.rwd` (SHA-256 prefix `e7e2d909`),
Odyssey `39990-THR,A020-20261110-PTM.rwd` (`b89d20f0`). The reported part string is not a firmware hash.
No EPS firmware is flashed; Panda limits, driver override, disengagement and saved controller/geometry choices are unchanged.

| Detected vehicle / EPS family | Calibration | Prediction delay |
| --- | --- | --- |
| HONDA_CLARITY / 39990-TRW-A020, modified EPS | Existing Clarity A020 | Measured speed schedule |
| HONDA_CIVIC_BOSCH / 39990-TBA-C020, modified EPS | Corrected PTM rev b, Clarity-equivalent command/P tables, RWD `df67bf6f` | Its own speed schedule (provisional) |
| HONDA_CIVIC / 39990-TEG-A010, modified EPS | TEG-A010 corrected PTM build, command row 3 (driven on that build) | Its own measured schedule |
| HONDA_INSIGHT / 39990-TXM-A040, modified EPS | Insight TXM-A040 corrected PTM build (the Clarity's own command map and P table, 3840 E4 per unit, measured load, R6 from its A table) | Clarity's measured speed schedule |
| HONDA_CIVIC_BOSCH / 39990-TBA-C120, modified EPS | C120 corrected PTM starting calibration: rows 0-4 the Clarity's R5 per key (3840 E4 per unit, its image's key clamp 1663), R6 from its A table, the C020's load and trims | The C020's speed schedule |
| HONDA_CIVIC_BOSCH / 39990-TGG-A120, modified EPS | Corrected row 0, built for 4096 E4 but sent 3840. Own measured column load and rack (owner routes 0b–10 on an earlier image); retains C020 trims and A table. No change to C020. | The C020's speed schedule |
| HONDA_CIVIC / 39990-TBA-A030, modified EPS | A030 corrected PTM starting calibration: the TEG-A010's row 3 on every row, R6 from its A table (the TEG's), the TEG's measured load | The TEG-A010's speed schedule |
| HONDA_CRV_5G / 39990-TLA-A040, modified EPS | CR-V A040 corrected PTM: row 0, key clamp 1774, measured load/rack, untrimmed | Donor default (Clarity schedule) |
| HONDA_CRV_5G / 39990-TLA-A220, modified EPS | CR-V A220 corrected PTM: rows 0-5 Clarity-equivalent, its own envelope, A040 load/rack/trims | Donor default (Clarity schedule) |
| ACURA_RDX_3G or ACURA_RDX_3G_MMR / 39990-TJB,A220 | Route-A Trk1641 RomCRC only. **Unavailable while its full trusted RWD digest is missing.** The MMR shares the 2019 vehicle measurements; no separate MMR fit. | RDX measured schedule, staged only |
| HONDA_RIDGELINE / 39990-T6Z,A110 | PTM rev b5 only, measured load/rack, provisional timing | Donor default (Clarity schedule) |
| HONDA_ODYSSEY / 39990-THR,A020 | 2026-11-10 PTM, spec vehicle calibration | Donor default (Clarity schedule) |

PID CarParams and a matching firmware steer-ratio profile are also required. No
other Civic, firmware version, diesel, CR-V, or generic Honda inherits a calibration.
The five starting calibrations are provisional: their firmware fields are read from
each corrected image, while load, trims and command delay are carried from the
nearest measured car until the owner's drives measure them.

## Required corrected firmware

### Acura RDX: staged, not enabled

The [donor calibration](https://github.com/Biscuit-Labs/openpilot/blob/01e5a3b8ce2cd7876f03adb03d72c0ec55663dd7/openpilot/selfdrive/controls/lib/honda_eps_calibrations.py#L342-L399)
names `RDX-PTM-101526-RomCRC.rwd` and publishes only SHA-256 prefix `3dd8b91b`.
The prefix is **not** an allowlist entry. The trusted full SHA-256 is unset, so even an exact rack with a saved
controller selection cannot offer or run this profile or use its rack map. No RWD is distributed or flashed.

To unlock a future reviewed build: obtain the original Route-A **RWD container** and an independently trusted full
SHA-256 from the builder. Hash the container, not the decrypted payload, verify the full match, and review a change
pinning that digest in `rdx_identity.py`. Confirm that specific build was flashed to the actual rack; diagnostics
cannot prove it. The private, non-backed-up `NrdrRdxRouteAConfirmation` state binds that confirmation to the exact
fingerprint and SHA-256 of the 17-character VIN as well as the full image digest. Nothing creates it automatically;
there is no public confirmation toggle. Revoke it on any reflash/rack swap, even with an unchanged version string.
Receipt changes require an offroad process restart. The pinned production transport remains at 4095 on 3G and
4076 on MMR; neither is the required linear 4096 map. A separate no-CAN bench configuration is not production
admission. Before enabling a real car, the transport and controller must use the same verified authorization,
and inactive and fallback PIF wire output must be checked against the baseline. Pinning a hash alone cannot do this.

The admitted profile still needs the explicit controller selection. Firmware geometry remains separately selectable.
The donor's measured pinion-rate curve is not a firmware Table A. Rack/load came from a 2019 RDX; angle geometry
past 169 degrees is extrapolated. TJB's own P knots/values and E4 scale 4096 are used, R6 is -120.1 per deg/s
at centre, high-speed P trim is 0.7 and the friction knee is 15 deg/s. Command delay is 0.12/0 s with its own
staged prediction schedule. The donor's 100 ms state retention never authorizes inactive steering output.
No Panda change or road validation is implied.

The Civic TEG-A010 calibration requires
`39990-TEG,A010-20261016b-PTMFix-ClarityEquivMap-ClarityPKnots-Row6Stock-A280FlatRows023`
(RWD SHA-256 starts `04147917`). It replaces the Bosch placeholder. It has been
driven on this corrected build (owner's route `0000013d`, 2026-10-17): the car runs
the corrected map (median R5 residual 35 counts over 104k frames, against 822 for the
earlier build's), the column load
holds out at R^2 0.810 (the same as a refit), and its telemetry R6 word agrees with the R6 computed from its Table A
(-156.16 at centre) within 0.8% on unrailed frames.

The Insight TXM-A040 calibration requires `39990-TXM,A040-PTM-20261016b`
(RWD SHA-256 starts `7ba37432`). Its source configuration has been driven on the
corrected build; that is not independent validation of this port.

The starting calibrations require, by RWD SHA-256 prefix: Civic Bosch TBA-C120
`9261b8db`, Civic TGG-A120 `6640806d`, Civic TBA-A030 `55c37266`, CR-V TLA-A040
`2e6a8802`, CR-V TLA-A220 `2c992997` (each `...-20261016b-PTMFix-ClarityEquivMap-...`).
The controller logs the required build at start and shows it in its description.

Older builds report the same EPS version strings as these corrected builds.
Family admission cannot verify the actual flashed image. Confirm the flashed
build separately before selecting PTM Controller; do not pair these
calibrations with the older images. This software update does not flash the EPS
or change safety limits.

## Timing

All admitted PTM profiles use the donor's fixed prediction schedule. Clarity uses
0.15 / 0.08 / 0.10 / 0.20 / 0.30 seconds at 3.5 / 7 / 12 / 20 / 30 m/s,
interpolated every frame, with endpoints held. Both model runtimes and controlsd
use the same profile. Saved live/manual settings are preserved but unavailable
while that schedule is selected. The Civics have their own schedules (2026-10-18):
TEG-A010 0.20 seconds at every speed, measured on its owner's drives, and C020 0.28 /
0.28 / 0.28 / 0.26 / 0.26 seconds, provisional (from a drive on an older controller).
RDX uses 0.15 / 0.40 / 0.40 / 0.22 / 0.30 seconds at those same speeds.
Insight, CR-V, Ridgeline and Odyssey use the donor default (Clarity schedule).

Command delay is a separate interpolated history buffer, not a blocking sleep.
Hardcoded endpoints interpolate from 10 to 15 m/s:

| Calibration | Below 10 m/s | Above 15 m/s |
| --- | --- | --- |
| Clarity | 0.20 s | 0.10 s |
| All Civics | 0.15 s | 0.15 s |
| Insight | 0.15 s | 0 s |
| CR-V A040 | 0.18 s | 0 s |
| CR-V A220, RDX, Ridgeline, Odyssey | 0.12 s | 0 s |

Both model runners use the donor's 0.1 s PTM curvature filter and add its delay to the
prediction horizon. Controlsd interpolates model actions between frames. PTM plan
models use the actual prediction horizon without the 0.3 s floor and no additional
command delay. Action/curvature heads and unknown sources use the table above; the
delay multiplier transitions over one second when the source changes.
Non-PTM model processing retains its existing timing. No saved settings are rewritten.

## Calibration and unchanged behavior

C020 has its own nonlinear command map, speed envelope, angle-dependent rate scale (-153.74 at centre), column
load fit, fixed P trims (115 / 125 / 115%) and I trims (75 / 95 / 100%). Its firmware
law inversion includes both the command-map and P-map knots. Clarity keeps its
angle-dependent R6 conversion, sampled exactly as in the donor's calibration calculation.

TEG-A010 now uses its corrected firmware's command row 3 and shared Clarity P
knots, with its own telemetry-derived column load and angle-dependent R6. It
retains the C020 base gains, P/I trims and Civic command delay. Its existing
3840-count transport and user-selected geometry are unchanged. Crawl speeds
are still thinly covered by its owner's drives (few turns below 9 m/s).

Insight TXM-A040 uses the corrected firmware's Clarity command map and P table,
its own load and angle-dependent R6, the C020 base gains/P-I trims, Civic command
delay, and Clarity prediction schedule. It is sent 3840 counts per unit, the
image's own command clamp (as the Clarity); no transport or safety limit is increased.

Shared steer-ratio selection, driver override, torque clipping, safety checks,
zero inactive output and single output LPF are preserved. The RDX/Odyssey state-retention window is described above. Optimized
lane changes suppress feedforward (including modeled EPS damping) for either
controller and fade it back in afterward. No extra rate damping or device-yaw
blend is added to PTM Controller.

## Source audit and verification boundary

The baseline is Biscuit-Labs `45e5b91fae`, especially `honda_eps_calibrations.py`,
`honda_eps_firmware_ff.py`, `honda_eps_rack_map.py` and `latcontrol_honda_eps.py`.
Calibration provenance distinguishes measured values from defaults and spec estimates.
The C020 high-speed envelope is firmware-derived, not validated at its high-speed rail.

Verification: 335 focused host tests pass (7 native-only skips); 9 in-memory C4 tests
cover timings, model gates, dropout transitions and offline CAN packing. Direct donor
comparisons match all 12 cores over 18,000 frames and all 12 rack maps. Non-PTM model
processing matches parent `14d3f1b0af` in 180 cases. Generated Sunnylink definitions agree.
These checks do not establish road performance or authorize release promotion.
