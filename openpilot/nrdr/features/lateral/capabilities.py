"""Controller eligibility shared by tuning UI, presets and control code.

Keep this module independent of native Params and messaging so a preset can be
validated before those libraries are built.
"""

from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP


def supports_interpolated_torque_pif(CP, CP_SP) -> bool:
  """Limit the experiment to modified-EPS Honda PID and Clarity-hybrid paths."""
  if str(getattr(CP, "brand", "")).lower() != "honda":
    return False
  if not bool(getattr(CP_SP, "flags", 0) & HondaFlagsSP.EPS_MODIFIED.value):
    return False
  fingerprint = str(getattr(CP, "carFingerprint", ""))
  try:
    lateral_kind = CP.lateralTuning.which()
  except (AttributeError, TypeError):
    lateral_kind = ""
  return lateral_kind == "pid" or (fingerprint == "HONDA_CLARITY" and lateral_kind == "torque")
