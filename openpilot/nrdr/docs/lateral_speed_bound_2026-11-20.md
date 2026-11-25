# Lateral speed bound (opt-in, unvalidated on the road)

Parameter `NrdrLateralSpeedBound`, default off. Read once when modeld starts. Never active with the PTM torque controllers or while openpilot controls speed.

On the C4: **Settings → Device → Lateral Tuning → Lateral Speed Bound**. Also available in Sunnylink under **Steering → nrdr → Lateral Tuning**. Change while parked. Missing or stale vehicle/control data skips the experiment.

## Problem

modeld turns the model's lateral output into a curvature by dividing by the measured speed: plan yaw rate / v for plan models, lateral acceleration / v² for action-head models. The model produced that output for the speed it expected. When the driver controls speed and the car is slower than the model expects, the same output becomes a tighter curvature than the model's path, and slowing further makes it tighter still.

Measured on the Clarity, 2026-11-20, lateral-only driving, EPS build 0x09 (analysis in `C:\Openpilot Workspace\analysis\ptm-angle-2026-11-20`):

| Case | Car / plan speed at the peak request | Effect |
|---|---|---|
| OPM10V3, four rolling 90° turns | 1.7-5.1 / 6.4-7.1 m/s | Peak target 282-408° against 137-171° driven manually |
| TSFDOM, NO OUTLET corner | braked 6.5 to 3.9 m/s | Model output flat to falling (2.4 to 1.6 m/s²); wheel 137° to 274° |

## What the option does

`LateralSpeedBound` (`features/lateral/lateral_speed_bound.py`) learns the usual ratio between the model's planned speed and the car's speed in steady driving (above 8 m/s, |a| below 0.5 m/s², 20 s minimum). When the planned speed over the 0.3 s action horizon exceeds that ratio by more than 8%, the planned speed divided by (ratio x 1.08) is used for the conversion instead of the measured speed. The speed used is never below the measured speed and never more than 1.5 times it, so the option can only reduce a curvature request, by at most 1.5x (plan) or 2.25x (action head).

## Command-level replay of the shipped module on the recorded plans

Same plans and wheel history; not a prediction of the car's path.

| Drive | Peak target, shipped to bounded (deg) | Acts on ordinary driving |
|---|---|---|
| Route 06, OPM10V3 | turn 4: 308 to 276; turn 7: 281 to 252; turn 8: 385 to 279; from-stop turns within 12° | 1.2% of straight and gentle-curve time, 4.9% of ordinary-curve time |
| Route 09, TSFDOM | turn 4: 262 to 220; others within 4° | 0.3% and 0.1% |

## Known limits

- It removes between a fifth and a half of the excess over the manual wheel angle at the measured rolling turns, not all of it. For action-head models the model's planned speed follows the car down under braking, so this bound is weak there; a stronger one needs the model's speed lag measured by model replay.
- The request still collapses toward zero when the car stops mid-turn (the conversion's own 1 m/s floor). Not addressed here.
- Reducing the request can make the car turn too little. Recorded-plan replay does not establish closed-loop safety or correct lane placement.

## Rollback

Set the parameter to 0 and restart, or revert the commit. Stored value is harmless when the code is absent.
