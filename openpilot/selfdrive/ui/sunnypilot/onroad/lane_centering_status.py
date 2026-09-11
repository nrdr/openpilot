from openpilot.cereal import custom


LaneCenteringReason = custom.LaneCenteringStateSP.Reason

LANE_CENTERING_REASON_LABELS = {
  int(LaneCenteringReason.unavailable): "--",
  int(LaneCenteringReason.disabled): "OFF",
  int(LaneCenteringReason.lateralInactive): "LAT",
  int(LaneCenteringReason.invalidInput): "BAD",
  int(LaneCenteringReason.modelInvalid): "MOD",
  int(LaneCenteringReason.driverOverride): "OVR",
  int(LaneCenteringReason.laneChange): "LCHG",
  int(LaneCenteringReason.belowSpeed): "SPD",
  int(LaneCenteringReason.turnSignalFade): "SIG",
  int(LaneCenteringReason.laneDataInvalid): "DATA",
  int(LaneCenteringReason.laneConfidenceLow): "CONF",
  int(LaneCenteringReason.laneGeometryInvalid): "GEOM",
  int(LaneCenteringReason.centered): "CTR",
  int(LaneCenteringReason.modelAuthority): "E2E",
  int(LaneCenteringReason.correcting): "ACT",
  int(LaneCenteringReason.zeroStrength): "ZERO",
  int(LaneCenteringReason.timingUnavailable): "TIME",
  int(LaneCenteringReason.previewTooShort): "SHORT",
}

LANE_CENTERING_SUSPENDED_REASONS = {
  int(LaneCenteringReason.driverOverride),
  int(LaneCenteringReason.laneChange),
  int(LaneCenteringReason.turnSignalFade),
}


def lane_centering_reason_code(reason) -> int:
  """Normalize pycapnp's decoded enum before hashed lookup."""
  return int(getattr(reason, "raw", reason))
