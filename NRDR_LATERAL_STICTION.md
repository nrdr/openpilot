# Lateral Stiction

Final-stage torque state machine emulating the breakaway friction of high-torque
EPS units (Toyota, Lexus, HKG). Param `NrdrLatStiction`, default off.
Implementation: `selfdrive/controls/lib/nrdr_lat_stiction.py`.

## Why

Those platforms hold precise lines in every controller era because the EPS blocks
noise in the amplitude domain: commands below the breakaway threshold move nothing,
the wheel parks solid between corrections, and only persistently integrated error
produces motion. A low-pass filter pays lag on everything; a threshold pays lag on
nothing that matters. The Honda EPS (particularly with modified firmware) is a
near-transparent pass-through, so every noise sample becomes wheel motion. This
stage rebuilds the threshold in software.

## Operation

HOLD: output frozen at a captured hold torque; a slow integrator (KI_HOLD) winds
against standing error. Zero dither reaches the EPS.
MOVE: live PID+FF output passes through unmodified.

Breakaway (HOLD to MOVE): |error| > E_HI, or |desired-angle rate| > DES_RATE_MOVE
(feedforward-led; never waits for error), or accumulated drift > DRIFT_BUDGET_DEGS.
Park (MOVE to HOLD): |error| < E_LO with plan and wheel quiet, sustained DWELL_S.
Transitions crossfade over XFADE_S; minimum state times prevent chatter.
Exact passthrough when disengaged, overridden, lane changing, saturated, or below
MIN_SPEED.

## Constants

| Constant | Value | Basis |
|---|---|---|
| E_HI | 0.9 to 0.4 deg over 8 to 30 m/s | ES350 hold span p75-p90 (city); highway end estimated |
| E_LO | 0.35 to 0.20 deg | ES350 holds begin with 0.3-0.5 deg wander |
| DES_RATE_MOVE / QUIET | 2.0 / 0.8 deg/s | plan-led breakaway; quiet gate for parking |
| DRIFT_BUDGET_DEGS | 0.35 deg*s | escapes sub-threshold creep in 1-2 s |
| DWELL_S / MIN_MOVE_S / MIN_HOLD_S | 0.15 / 0.25 / 0.20 s | ES350 moves p50 0.33 s; holds from 0.4 s |
| XFADE_S | 0.08 s | bumpless transitions |
| KI_HOLD | 0.10 torque/(deg*s) | stiction winding rate |
| MIN_SPEED | 3.0 m/s | parking bypass |

## Measured reference - Lexus ES350, city 8-15 m/s, 63 s engaged, hands-off

Hold fraction 53% of drive time. Hold durations p50 0.76 s. Wheel span within a
hold p50 0.51 / p90 1.16 deg. Move durations p50 0.33 s; step amplitude p50 0.54 /
p75 1.78 deg; peak move rate p50 6.5 deg/s. Commanded curvature flat to four
decimals during holds. Highway (25+ m/s) remains uncalibrated pending logs.

## Notes

With standing dither removed, the in-MOVE low-pass filter can be reduced (target
0.05-0.10). The auto-tuner is compatible: held error is persistent error. Visible
move-pause-move stepping is the intended behavior.
