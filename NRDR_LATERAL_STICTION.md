# Predictive Lateral Stiction

`NrdrLatStiction` is a default-off final-stage steering overlay implemented in
`openpilot/nrdr/features/lateral/lat_stiction.py`. Normal PID output provides the
throw; the overlay only removes torque while the wheel closes on a stable
target, freezes the captured output briefly, and returns smoothly to PID when
another correction is required.

## States

- `TRACK`: exact PID passthrough.
- `CAPTURE`: predicts the target crossing from steering-angle error and relative
  wheel/target rate. Torque that is still driving the closing motion is tapered
  over 80 ms. Capture never increases or reverses torque.
- `HOLD`: freezes the settled capture output.
- `REACQUIRE`: blends back to current PID output over 80 ms.

Capture and hold use relative motion, so a slowly moving intersection target can
produce the intended move-pause-move response. There is no minimum-speed
bypass. Driver input, a real model lane change, steering faults, curvature
limiting, and controller saturation immediately restore normal control. The
base PID integrator and tune learner are frozen while capture, hold, or
reacquisition owns the output.

## Initial prototype limits

The prototype is one-sided: it can reduce a throw but cannot add boost or apply
counter-torque. It targets dynamic angle overshoot, not an incorrect steady
steer-ratio map. Calibrated yaw is intentionally not allowed to command torque
in this version; a later yaw-authoritative mode requires delay validation and a
latched physical-angle target first.

| Setting | Value |
|---|---:|
| Prediction horizon | 0.12 s |
| Relative-rate filter | 0.05 s |
| Capture damping | 0.008 normalized torque/(deg/s) |
| Maximum torque removal | 0.25 |
| Capture authority ramp | 0.08 s |
| Hold direction-change release | 0.03 normalized torque |
| Hold entry error | 0.35° low speed to 0.20° high speed |
| Hold release error | 0.90° low speed to 0.40° high speed |
| Hold dwell | 0.15 s |
| Reacquisition blend | 0.08 s |
