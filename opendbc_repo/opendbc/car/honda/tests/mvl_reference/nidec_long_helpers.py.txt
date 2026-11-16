"""Pure Nidec longitudinal helpers (importable without openpilot)."""

# Keep in sync with opendbc/car/honda/carcontroller.py
NIDEC_MIN_ACCEL_SPEED_LEAD = 0.35
# m/s of lead below which the servo is never treated as saturated (see NIDEC_DV_SAT_MIN in carcontroller)
NIDEC_DV_SAT_MIN = 2.5
# m/s below the displayed set speed where the PCM's own set-speed governor takes over (see
# nidec_set_speed_governed); the gas-channel learners have always used this margin
NIDEC_SET_SPEED_MARGIN = 2.0


def nidec_speed_lead_mps(sf_eff: float, accel: float, alpha_eff: float) -> float:
  """PCM_SPEED lead (m/s) from the speed-channel blend."""
  speed_lead = sf_eff * accel + alpha_eff
  if accel > 0.05:
    speed_lead = sf_eff * accel + max(alpha_eff, -sf_eff * accel + NIDEC_MIN_ACCEL_SPEED_LEAD)
  return speed_lead


def nidec_speed_channel_pinned(dv_lead: float, dv_sat: float, dv_coast: float = NIDEC_DV_SAT_MIN) -> bool:
  """True when the lead the servo is answering is past its responsive band in either direction.

  Above dv_sat the servo is at its acceleration ceiling, below -dv_coast it is at its coast floor
  (fuel cut; the PCM has no brake authority through PCM_SPEED). In both regions
  d(response)/d(speed factor) = 0, so tracking error there is not speed-factor information and
  the speed-channel learners may only reduce. The negative side matters on cars whose coast
  floor is shallow: CR-V 2015 (route a6354c3dcf16e7cf/25) coasts at -0.4 m/s2 for every lead
  from -1 to -40 m/s, so a -0.5 m/s2 plan undershoots forever and err*accel (both negative) was
  the dominant growth fuel that took the highway speed factor from 4 to 23-43.
  """
  return dv_lead > dv_sat or dv_lead < -dv_coast


def nidec_set_speed_governed(v_ego: float, v_cruise: float, margin: float = NIDEC_SET_SPEED_MARGIN) -> bool:
  """True when the PCM's own set-speed governor, not our wire, decides the acceleration.

  The Nidec PCM stops accelerating ~3% below the CRUISE_SPEED it displays regardless of PCM_SPEED
  and PCM_GAS (CR-V 2015 route a6354c3dcf16e7cf/25: 20 s of PCM_SPEED = vEgo + 11 m/s, gas 198,
  plan +0.7, car held at 116-117 kph with the display at 120; aEgo +0.5 at 95-113 kph, +0.02 at
  115-117, -0.05 at 117-119 under the same wire). Undershoot there is not plant information for
  any longitudinal learner: it collapsed sat_accel 0.69 -> 0.37 and pinned the speed alpha at its
  cap on that route. Uses the same 2 m/s margin the gas-channel learners already apply.
  """
  return v_ego >= v_cruise - margin
