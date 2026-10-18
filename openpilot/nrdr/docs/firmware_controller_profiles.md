# Firmware Controller profiles

This is steering-angle feedback plus an EPS-firmware-inversion feedforward, not
real-time yaw feedback. `NrdrLateralController = 1` is latched at drive startup;
changing it requires offroad confirmation. PIF's Device Yaw Correction is separate.

| Detected vehicle / EPS family | Calibration | Prediction delay |
| --- | --- | --- |
| HONDA_CLARITY / 39990-TRW-A020, modified EPS | Existing Clarity A020 | Measured speed schedule |
| HONDA_CIVIC_BOSCH / 39990-TBA-C020, modified EPS | Civic C020 TargetMapD / Tracker4500 / Norm1650 / P117to265 / D737 / KFF45 | Normal live/manual path |
| HONDA_CIVIC / 39990-TEG-A010, modified EPS | TEG-A010 corrected PTM build, command row 3 (driven on that build) | Normal live/manual path |
| HONDA_INSIGHT / 39990-TXM-A040, modified EPS | Insight TXM-A040 corrected PTM build (the Clarity's own command map and P table, 3840 E4 per unit, measured load, R6 from its A table) | Clarity's measured speed schedule |
| HONDA_CIVIC_BOSCH / 39990-TBA-C120, modified EPS | C120 corrected PTM starting calibration: rows 0-4 the Clarity's R5 per key (3840 E4 per unit, its image's key clamp 1663), R6 from its A table, the C020's load and trims | Normal live/manual path |
| HONDA_CIVIC_BOSCH / 39990-TGG-A120, modified EPS | TGG-A120 corrected PTM starting calibration: row 0, built for 4096 E4 per unit but sent 3840 (its key clamp 1663), R6 from its A table (the C020's), the C020's load and trims | Normal live/manual path |
| HONDA_CIVIC / 39990-TBA-A030, modified EPS | A030 corrected PTM starting calibration: the TEG-A010's row 3 on every row, R6 from its A table (the TEG's), the TEG's measured load | Normal live/manual path |
| HONDA_CRV_5G / 39990-TLA-A040, modified EPS | CR-V A040 corrected PTM starting calibration: row 0, key clamp 1774, R6 from its A table, the owner's measured load, untrimmed | Normal live/manual path |
| HONDA_CRV_5G / 39990-TLA-A220, modified EPS | CR-V A220 corrected PTM starting calibration: rows 0-5 Clarity-equivalent, its own envelope, the A040's A table, R6, load and trims | Normal live/manual path |

PID CarParams and a matching firmware steer-ratio profile are also required. No
other Civic, firmware version, diesel, CR-V, or generic Honda inherits a calibration.
The five starting calibrations are provisional: their firmware fields are read from
each corrected image, while load, trims and command delay are carried from the
nearest measured car until the owner's drives measure them.

## Required corrected firmware

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
build separately before selecting Firmware Controller; do not pair these
calibrations with the older images. This software update does not flash the EPS
or change safety limits.

## Timing

The temporary fixed 0.30-second prediction override is removed. Clarity uses
0.15 / 0.08 / 0.10 / 0.20 / 0.30 seconds at 3.5 / 7 / 12 / 20 / 30 m/s,
interpolated every frame, with endpoints held. Both model runtimes and controlsd
use the same profile. Saved live/manual settings are preserved but unavailable
while that schedule is selected. Civic has no measured prediction schedule in the
source and therefore keeps live/manual delay normally, subject to Suggested locks.
Model-specific smoothing remains separate, as in the source implementation.

Command delay is a separate interpolated curvature history buffer, not a blocking
sleep. It fades between 10 and 15 m/s. Clarity retains its saved endpoints, default
0.145 / 0.025 seconds. Civic (and the Insight) uses fixed 0.175 / 0.025 seconds (source 0.150 / 0.000
plus the existing port's 0.025-second model-action compensation); saved Clarity
command-delay settings do not retune Civic. These are model-dependent calibrations,
not a guarantee for every driving model.

## Calibration and unchanged behavior

C020 has its own nonlinear command map, speed envelope, rate scale (-173), column
load fit, fixed P trims (115 / 125 / 115%) and I trims (75 / 95 / 100%). Its firmware
law inversion includes both the command-map and P-map knots. Clarity keeps its
newer angle-dependent R6 conversion and all existing core numerical behavior.

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
inactive reset/history behavior and single output LPF are preserved. Optimized
lane changes suppress feedforward (including modeled EPS damping) for either
controller and fade it back in afterward. No extra rate damping or device-yaw
blend is added to Firmware Controller.

## Source audit and verification boundary

Sources: JamesL787 `honda-eps-controller-update` ab868ea15561 (Clarity prediction
refit); `civic-command-delay` 59eb99e3183e (C020 calibration, load/P-I trims and
command delay); `c020-crawl-gate-civic-load` 74938539173c. The later
`crv-eps-calibration-fix` 898a319842cd was checked: its relevant C020 calibration
and load remain the same. Its CR-V/radar/model updates are outside this change.

The Civic crawl gate/friction-width schedule is included. The older Clarity
constant-R6 model from the Civic branch is not imported. No unmeasured TEG yaw
calibration is added, and neither controller is converted to live car-yaw feedback.
The C020 high-speed envelope is firmware-derived; the original source drive did
not validate its high-speed rail. PRs #21 (`a8aa41534e50`) and #22
(`5f54846231dd`) supply the corrected TEG and Insight calibrations described
above. PRs #19/#20 were withdrawn/superseded; their older multi-image
calibrations and universal Clarity delay schedule are not included.

Host checks validate numerical parity, profile admission, shared schedule wiring,
lane-change bypass and generated Sunnylink definitions. They do not replace native
C4 tests, recorded-drive replay or progressive road validation. Do not promote
this patch to release branches or call the provisional TEG calibration validated
on this basis.
