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
# v2 (pure rack): torque-corrected fit - column-twist effects excluded, so this is the
# geometry map the PID setpoint path wants. Near-flat ~16.6 through normal driving,
# tapering only past ~100 deg (parking/lock). v1 (twist-baked) measured effective
# ratio including average LKAS column flex; that belongs in the torque domain, not here.
# Low-torque holdout yaw RMSE: v2 0.0046 vs v1 0.0053 vs best flat scalar 0.0045.
SR_ANGLE_CURVES: dict[str, tuple[list[float], list[float]]] = {
  "HONDA_CLARITY": (
    [0., 6., 12., 20., 32., 48., 70., 100., 140., 200., 300., 450.],
    # v2.1: tail bent to the owner's proven lock ratio (12.74, from the original on-car
    # measurement; preferred by road feel over the v2 fit's 13.95). <=140 deg unchanged.
    # v2.2: center anchored to the owner's months-validated 17.00 (inside the fit's
    # uncertainty band; also removes the 6-deg fit-noise dip and makes the curve
    # monotone from center). 20 deg onward unchanged from v2.1.
    [17.00, 17.00, 16.90, 16.84, 16.84, 16.72, 16.40, 15.94, 15.40, 14.30, 13.40, 12.74],
  ),
}
