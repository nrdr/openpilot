"""Shared lookups for the offline EPS measuring tools (eps_*.py): VSA yaw decode, Table A, calibrations.

Offline only: nothing here runs on the car. Ported from JamesL787 ns-bosch-radar-testing tools/lateral, where these
tools measured every calibration in vfn_eps_core (rows, R6, column load, command delay, rack maps, yaw scales).
"""
from types import SimpleNamespace

import numpy as np

from openpilot.nrdr.features.lateral import vfn_eps_core as core
from openpilot.nrdr.features.lateral.honda_vgr import HONDA_VGR_PROFILES, get_honda_vgr_profile, normalize_honda_eps_firmware

# VSA yaw rate, 0x94 KINEMATICS YAW_RATE (top 10 bits, clockwise-positive). Per car: deg/s per count, standstill zero
# in counts (each drive's own standstill mean replaces it), clockwise under-read in deg/s ramped in over RIGHT_LOSS_BP
# counts. Scales are fitted against GPS heading on straight-to-straight pairs (eps_fit_yaw_scale.py):
# - Clarity: 1670 pairs on 9 routes, 0.2468 +/- 0.0008 with the clockwise correction (zero 512 since its VSA yaw-bias
#   recalibration of 2026-10-02, 508 before).
# - Civic Bosch: 0.2446 / 0.2412 on two routes, zero 513, clockwise not checked.
# - CR-V 5G: 217 windows on route 00000013--da43527a2c, 0.24455 + 0.49 clockwise, zero 509.5.
# - Insight: 70k pairs on route 0000001e, 0.2428 + 0.157 clockwise.
# - Civic (Nidec) TEG-A010: 359k pairs on routes 0000012d-00000139, 0.2414 + 0.098 clockwise.
YAW_RATE_CALIBRATION = {
  "HONDA_CLARITY": (0.246, 512.0, 0.24),
  "HONDA_CIVIC_BOSCH": (0.244, 513.0, 0.0),
  "HONDA_CRV_5G": (0.245, 509.5, 0.49),
  "HONDA_INSIGHT": (0.243, 512.0, 0.16),
  "HONDA_CIVIC": (0.241, 512.0, 0.10),
}
DEFAULT_YAW_RATE_CALIBRATION = (0.25, 512.0, 0.0)  # the DBC's own scale and zero
# Event names that changed upstream: newer logs (this tree) carry vehicleParameters / deviceMotion, older ones
# liveParameters / livePose, with the same fields. The tools accept either.
VEHICLE_PARAMETERS = ("vehicleParameters", "liveParameters")
DEVICE_POSE = ("deviceMotion", "livePose")
RIGHT_LOSS_BP = (3.0, 5.0)  # counts from zero over which the clockwise under-read comes in
VSA_ADDR = 0x94


def vsa_counts(dat) -> int:
  return (dat[0] << 2) | (dat[1] >> 6)


def yaw_rate_deg_s(counts_from_zero, scale: float, right_loss: float = 0.0):
  """Yaw rate in deg/s, clockwise-positive, from counts relative to the zero (scalar or array)."""
  lo, hi = RIGHT_LOSS_BP
  return counts_from_zero * scale + right_loss * np.clip((np.asarray(counts_from_zero) - lo) / (hi - lo), 0.0, 1.0)


def vgr_profile(fingerprint: str, eps_fw: str | None):
  if not eps_fw:
    return None
  cp = SimpleNamespace(brand="honda", carFingerprint=str(fingerprint), carFw=[SimpleNamespace(ecu="eps", fwVersion=eps_fw)])
  return get_honda_vgr_profile(cp)


def vgr_profile_by_name(name: str):
  return next((p for p in HONDA_VGR_PROFILES if p.name == name), None)


def vgr_inverse(profile, steps: int = 4001):
  """(linear_bp, angle_bp) for np.interp, sampled finely from the profile's exact Table A conversion."""
  angles = np.unique(np.r_[np.asarray(profile.physical_knots, float), np.linspace(0.0, profile.physical_knots[-1], steps)])
  return np.array([profile.physical_to_linear(a) for a in angles]), angles


def _own_calibrations():
  # Imported here: the controller module pulls in the control stack, which only some tools need.
  from openpilot.nrdr.features.lateral.latcontrol_fw import _OWN_CALIBRATIONS
  table = {name: entry[:2] for name, entry in _OWN_CALIBRATIONS.items()}
  table.setdefault("clarity_a020", (core.CLARITY_A020, core.CLARITY_EPS_LOAD))
  return table


def calibration(name: str):
  """(EpsFirmwareCalibration, column-load tuple) by calibration name."""
  table = _own_calibrations()
  if name not in table:
    raise SystemExit(f"unknown calibration {name!r}; known: {', '.join(sorted(table))}")
  return table[name]


def firmware_profile(fingerprint: str, eps_fw: str | None):
  """The Firmware Controller profile this car/EPS is admitted with, or None."""
  from openpilot.nrdr.features.lateral.controller_selection import _PROFILES
  return _PROFILES.get((str(fingerprint), normalize_honda_eps_firmware(eps_fw))) if eps_fw else None


def prediction_schedule(profile):
  """The measured delay schedule told to the model, or None where the live/manual delay is used."""
  if profile is None or not profile.prediction_schedule:
    return None
  from openpilot.nrdr.features.lateral.yaw_control_timing import DELAY_SCHEDULE_BP, DELAY_SCHEDULE_V  # reads Params
  return DELAY_SCHEDULE_BP, DELAY_SCHEDULE_V


def rack_map(fingerprint: str, eps_fw: str | None, cp_ratio: float):
  """The car's rack map (yaw-measured or spec-predicted), when this tree has rack maps (honda_rack_map) and one for it."""
  try:
    from openpilot.nrdr.features.lateral.honda_rack_map import rack_map_geometry
  except ImportError:  # a tree without rack maps
    return None
  cp = SimpleNamespace(brand="honda", carFingerprint=str(fingerprint), carFw=[SimpleNamespace(ecu="eps", fwVersion=eps_fw)])
  return rack_map_geometry(cp, vgr_profile(fingerprint, eps_fw), cp_ratio)
