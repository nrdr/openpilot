"""Display order is independent of the persisted lane-guidance enum values."""

from openpilot.nrdr.features.lateral.lane_guidance import LaneGuidanceMode


LANE_GUIDANCE_LABELS = ("Off", "Blendful", "Star")
LANE_GUIDANCE_MODES = (LaneGuidanceMode.MODEL_ONLY, LaneGuidanceMode.BLENDFUL, LaneGuidanceMode.NRDR)
