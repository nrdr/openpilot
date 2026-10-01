"""Explicit controller selection, admitted only for the validated EPS family."""
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP

from openpilot.nrdr.features.lateral.honda_vgr import get_honda_vgr_profile


def yaw_controller_available(CP, CP_SP) -> bool:
  return bool(CP is not None and str(CP.brand) == "honda" and str(CP.carFingerprint) == "HONDA_CLARITY"
              and getattr(CP_SP, "flags", 0) & HondaFlagsSP.EPS_MODIFIED.value
              and get_honda_vgr_profile(CP) is not None and CP.lateralTuning.which() == "pid")
