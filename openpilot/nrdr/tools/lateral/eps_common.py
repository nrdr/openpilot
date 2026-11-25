"""Shared lookups for the offline EPS measuring tools (eps_*.py): VSA yaw decode, Table A, calibrations.

Offline only: nothing here runs in vehicle control. Lookups follow Biscuit-Labs Honda-PTM-Testing 45e5b91fae;
nrdr's existing parameter and log-format adapters are retained.
"""
from types import SimpleNamespace
import os
import re

import numpy as np

from openpilot.nrdr.features.lateral import vfn_eps_core as core
from openpilot.nrdr.features.lateral.honda_vgr import HONDA_VGR_PROFILES, get_honda_vgr_profile, normalize_honda_eps_firmware, ptm_inverse

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
  "ACURA_RDX_3G": (0.2511, 512.3, -0.20),
}
DEFAULT_YAW_RATE_CALIBRATION = (0.25, 512.0, 0.0)  # the DBC's own scale and zero
# Event names that changed upstream: newer logs (this tree) carry vehicleParameters / deviceMotion, older ones
# liveParameters / livePose, with the same fields. The tools accept either.
VEHICLE_PARAMETERS = ("vehicleParameters", "liveParameters")
DEVICE_POSE = ("deviceMotion", "livePose")
RIGHT_LOSS_BP = (3.0, 5.0)  # counts from zero over which the clockwise under-read comes in
VSA_ADDR = 0x94


def log_segment_number(path) -> int:
  """Route folders and flat downloads, with either Windows or POSIX separators."""
  normalized = os.fspath(path).replace('\\', '/')
  match = re.search(r'(?:rlog_|--|/)(\d+)(?:\.zst|\.bz2|/rlog|--rlog)', normalized)
  return int(match.group(1)) if match else 0


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


def vgr_inverse(profile):
  """(linear_bp, angle_bp) using the same sampled Table A inverse as the PTM baseline."""
  return tuple(np.asarray(axis, float) for axis in ptm_inverse(profile))


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
  """The PTM Controller profile this car/EPS is admitted with, or None."""
  from openpilot.nrdr.features.lateral.controller_selection import _PROFILES
  return _PROFILES.get((str(fingerprint), normalize_honda_eps_firmware(eps_fw))) if eps_fw else None


def prediction_schedule(profile):
  """The selected calibration's prediction schedule, not a shared Clarity fallback."""
  from openpilot.nrdr.features.lateral.yaw_control_timing import prediction_delay_schedule
  return prediction_delay_schedule(profile)


def rack_map(fingerprint: str, eps_fw: str | None, cp_ratio: float):
  """The car's rack map (yaw-measured or spec-predicted), when this tree has rack maps (honda_rack_map) and one for it."""
  try:
    from openpilot.nrdr.features.lateral.honda_rack_map import rack_map_geometry
  except ImportError:  # a tree without rack maps
    return None
  cp = SimpleNamespace(brand="honda", carFingerprint=str(fingerprint), carFw=[SimpleNamespace(ecu="eps", fwVersion=eps_fw)])
  return rack_map_geometry(cp, vgr_profile(fingerprint, eps_fw), cp_ratio, ptm_baseline=True)
