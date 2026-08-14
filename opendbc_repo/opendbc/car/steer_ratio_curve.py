"""
nrdr: angle-dependent steer ratio.

The old multi-knot offline fit is scrapped. Steer ratio is now a two-point linear
taper between live-tunable endpoints (NrdrSteerRatioMin at center, NrdrSteerRatioMax
at ~lock), consumed in latcontrol_pid and applied only when Learn Steer Ratio is off.

This map is intentionally left empty so VehicleModel.steer_ratio_at falls back to the
scalar self.sR everywhere; latcontrol drives that scalar per frame from the endpoints.
"""

# {carFingerprint: (|steering wheel angle| breakpoints [deg], steer ratio values)}
SR_ANGLE_CURVES: dict[str, tuple[list[float], list[float]]] = {}
