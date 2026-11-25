"""Compatibility exports for the canonical NRDR PID lateral controller."""

from openpilot.nrdr.features.lateral.latcontrol_pid import (
  CENTER_BOOST_SPEED_FADE,
  CENTER_TAPER_FADE_TAU,
  CIVIC_TEG_CENTER_BOOST_FADE_DEG,
  LOW_SPEED_MAX,
  MPH_TO_MS,
  RATE_DAMPING_REFERENCE,
  RATE_DAMPING_UNWIND_ANGLE,
  STANDARD_SPEED_MAX,
  NrdrLatControlPID,
)


__all__ = (
  "CENTER_BOOST_SPEED_FADE",
  "CENTER_TAPER_FADE_TAU",
  "CIVIC_TEG_CENTER_BOOST_FADE_DEG",
  "LOW_SPEED_MAX",
  "MPH_TO_MS",
  "RATE_DAMPING_REFERENCE",
  "RATE_DAMPING_UNWIND_ANGLE",
  "STANDARD_SPEED_MAX",
  "NrdrLatControlPID",
)
