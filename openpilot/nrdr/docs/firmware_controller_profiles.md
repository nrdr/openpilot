# Firmware Controller profiles

This is steering-angle feedback plus an EPS-firmware-inversion feedforward, not
real-time yaw feedback. `NrdrLateralController = 1` is latched at drive startup;
changing it requires offroad confirmation. PIF's Device Yaw Correction is separate.

| Detected vehicle / EPS family | Calibration | Prediction delay |
| --- | --- | --- |
| HONDA_CLARITY / 39990-TRW-A020, modified EPS | Existing Clarity A020 | Measured speed schedule |
| HONDA_CIVIC_BOSCH / 39990-TBA-C020, modified EPS | Civic C020 TargetMapD / Tracker4500 / Norm1650 / P117to265 / D737 / KFF45 | Normal live/manual path |
| HONDA_CIVIC / 39990-TEG-A010, modified EPS | TEG-A010 corrected PTM build, command row 3 (provisional until driven on that build) | Normal live/manual path |
| HONDA_INSIGHT / 39990-TXM-A040, modified EPS | Insight TXM-A040 corrected PTM build (the Clarity's own command map and P table, 4096 E4 per unit, measured load, R6 from its A table) | Clarity's measured speed schedule |

PID CarParams and a matching firmware steer-ratio profile are also required. No
other Civic, firmware version, diesel, CR-V, or generic Honda inherits the fallback.

## Required corrected firmware

The Civic TEG-A010 calibration requires
`39990-TEG,A010-20261016b-PTMFix-ClarityEquivMap-ClarityPKnots-Row6Stock-A280FlatRows023`
(RWD SHA-256 starts `04147917`). It replaces the Bosch placeholder, but remains
provisional: it has not yet been road-validated on this corrected build.

The Insight TXM-A040 calibration requires `39990-TXM,A040-PTM-20261016b`
(RWD SHA-256 starts `7ba37432`). Its source configuration has been driven on the
corrected build; that is not independent validation of this port.

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
3840-count transport and user-selected geometry are unchanged. It remains
provisional, especially at crawl speeds not covered by the source telemetry.

Insight TXM-A040 uses the corrected firmware's Clarity command map and P table,
its own load and angle-dependent R6, the C020 base gains/P-I trims, Civic command
delay, and Clarity prediction schedule. Its 4096-count transport is accounted
for in the inversion; no transport or safety limit is increased.

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
