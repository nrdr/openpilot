"""
nrdr: measured angle-dependent steer ratio curves (variable-gear-ratio racks).

openpilot models steerRatio as one scalar; a VGR rack isn't one number. These
curves were fit offline from on-road logs (yaw-rate ground truth, bank + tire-slip
compensated, robust PWL fit). HONDA_CLARITY: holdout yaw-rate RMSE 0.0061 rad/s
vs 0.0099 with the 16.5 scalar (~8h of driving incl. a full-lock cul-de-sac sweep).

Notes:
- Ratios below ~60deg intentionally include the average LKAS-torque column twist
  present during op driving (the angle sensor sits upstream of the torsion bar),
  so the angle<->curvature mapping matches runtime conditions. Explicit
  torque-based twist correction is a possible v2.
- VehicleModel.sr_trim is the hook for a live global multiplier (tires/alignment
  drift); it ships fixed at 1.0 until curve-relative residuals justify wiring
  paramsd into it.
"""

# {carFingerprint: (|steering wheel angle| breakpoints [deg], steer ratio values)}
SR_ANGLE_CURVES: dict[str, tuple[list[float], list[float]]] = {
  "HONDA_CLARITY": (
    [3., 4., 5., 6., 7., 9., 11., 14., 17., 21., 26., 33., 41., 51., 63., 79., 98., 122., 188., 234., 362., 450.],
    [16.60, 17.10, 17.55, 17.05, 17.12, 18.04, 18.17, 19.02, 17.80, 17.89, 18.02, 18.01,
     17.68, 17.04, 17.09, 16.88, 16.28, 15.81, 15.12, 14.95, 14.35, 14.02],
  ),
}
