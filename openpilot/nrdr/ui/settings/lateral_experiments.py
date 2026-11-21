"""Shared entries for the compact and full Lateral Tuning screens."""
from openpilot.nrdr.params import confirmed_vehicle_identity, get_selected_car_identity


LATERAL_EXPERIMENTS = (
  ("NrdrLateralSpeedBound", "Lateral Speed Bound",
   "Experimental. Can reduce requested steering when you control speed and the model expects a faster turn. "
   "Not used by PTM torque controllers. Takes effect next drive."),
  ("NrdrTurnDesireRefresh", "Turn Desire Refresh",
   "Experimental. Repeats a signaled turn request while waiting to turn. Requires Lane Turn Desire; "
   "does not keep the request after the signal cancels."),
)


def confirmed_honda_tuning(state):
  present, fingerprint, brand = get_selected_car_identity(state.params)
  identity = confirmed_vehicle_identity(state.CP, fingerprint, brand, selection_present=present)
  return identity is not None and identity[1] == "honda"
