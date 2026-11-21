"""HumanFollowing: the MPC lead path follows the model's lead trajectory instead of the aLeadK extrapolation.

Ported from openpilot-radar (ns-bosch-radar-testing, STATUS 62/63/118/120), which follows FrogPilot-Testing
728f65472 `process_lead`. NRDR port: the planner calls `upstream_lead_paths()` when `gate.human_following_enabled(CP)` and MVL is off, and hands
the result to LongitudinalMpc.update(lead_paths=...). The SOURCE `install()` and `enabled_for(CP, toggle)` are dropped:
the toggle is permanently on and the nrdr MPC takes the paths as an argument.

Differences from StarPilot's builder:
- The model lead counts above LEAD_DETECTION_PROBABILITY (0.35) rather than 0.5.
- No aLeadK < -0.5 or 7 s TTC hand-back. Those guards produced the felt -3.5 m/s^2 peaks on route 24f
  (STATUS 62/63). Only a 2.0 s closing-TTC hand-back to the raw extrapolation is kept (owner, 2026-09-28,
  after a 3.0/2.5/2.0/1.5/1.0 s replay sweep).
- Forward movement is bounded by the distance the lead's speed can cover (x_lead_max).

Kept from StarPilot: the model-horizon freshness check (`lead_horizon_matches` geometry, model_t equality).
A failed check returns None, so the raw extrapolation is used, which is never softer.

Known cost (STATUS 120, replay): later than stock ACC on 0262 379.4 (+1.05 s) and 25e 1002.0 (+0.35 s), where
the model has the lead speeding up while radar aLeadK reads -1 to -2. Replay evidence only; not road-validated.
"""
import math

import numpy as np
from opendbc.car.interfaces import ACCEL_MIN

from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import T_DIFFS, T_IDXS
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.selfdrive.controls.radard import RADAR_TO_CAMERA

LEAD_DETECTION_PROBABILITY = 0.35
LEAD_T_IDXS_MODEL = np.asarray(ModelConstants.LEAD_T_IDXS, dtype=np.float64)
MAX_CLOSING_TTC = 2.0
MIN_CLOSING_SPEED = 0.75
def _horizon_matches(model_lead, lead, v_ego, model_v_ego) -> bool:
  """StarPilot's lead_horizon_matches with the 0.35 detection threshold in place of 0.5."""
  try:
    values = tuple(float(value) for value in (model_lead.prob, lead.modelProb, model_lead.x[0], model_lead.y[0],
      model_lead.v[0], lead.dRel, lead.yRel, lead.vLead, v_ego, model_v_ego))
    if not all(math.isfinite(value) for value in values):
      return False
    probability, matched_probability, model_x, model_y, model_v, distance, lateral, speed, ego, model_ego = values
    p_min = LEAD_DETECTION_PROBABILITY
    if not p_min < probability <= 1. or not p_min < matched_probability <= 1. or distance <= 0. or speed < 0.:
      return False
    expected_distance = model_x - RADAR_TO_CAMERA
    expected_speed = ego + model_v - model_ego
    if type(lead.radar) is not bool or type(lead.radarTrackId) is not int:
      return False
    if lead.radar:
      return bool(lead.radarTrackId >= 0 and
        abs(distance - expected_distance) < max(5., .25 * expected_distance) and
        abs(lateral + model_y) < 1. and abs(speed - expected_speed) < 2.)
    return bool(lead.radarTrackId == -1 and abs(distance - expected_distance) <= .001 and
      abs(lateral + model_y) <= .001 and math.isfinite(float(lead.vRel)) and
      abs(float(lead.vRel) - (model_v - model_ego)) <= .001)
  except (AttributeError, IndexError, TypeError, ValueError, OverflowError):
    return False


def build_trajectory(model_lead, radar_lead, v_ego, model_v_ego=None):
  """Radar (or vision) dRel/vLead anchor plus the model's future deltas; None selects the raw extrapolation."""
  if model_lead is None or radar_lead is None or not bool(getattr(radar_lead, "present", False)):
    return None
  try:
    model_x = np.asarray(model_lead.x, dtype=np.float64)
    model_v = np.asarray(model_lead.v, dtype=np.float64)
    model_y = np.asarray(model_lead.y, dtype=np.float64)
    model_t = np.asarray(model_lead.t, dtype=np.float64)
  except (AttributeError, TypeError, ValueError):
    return None

  expected_len = len(LEAD_T_IDXS_MODEL)
  if any(value.shape != (expected_len,) for value in (model_x, model_v, model_y, model_t)):
    return None
  if (any(not np.all(np.isfinite(value)) for value in (model_x, model_v, model_y, model_t)) or
      not np.array_equal(model_t, LEAD_T_IDXS_MODEL) or not _horizon_matches(model_lead, radar_lead, v_ego, model_v_ego)):
    return None

  raw_d_rel = float(getattr(radar_lead, "dRel", float("nan")))
  raw_v_lead = float(getattr(radar_lead, "vLead", float("nan")))
  if not np.isfinite(raw_d_rel) or not np.isfinite(raw_v_lead) or not np.isfinite(v_ego):
    return None

  # Urgent closing: hand the lead back to the raw aLeadK extrapolation.
  v_ego = float(v_ego)
  closing = v_ego - raw_v_lead
  if closing > MIN_CLOSING_SPEED and raw_d_rel / closing < MAX_CLOSING_TTC:
    return None

  # The model contributes future deltas only; the current lead distance and speed stay the anchor.
  x_lead_traj = raw_d_rel + (model_x - model_x[0])
  v_lead_traj = raw_v_lead + (model_v - model_v[0])

  # MPC will not converge if an immediate crash is expected: clip to what is still possible to brake for.
  v_lead_0 = v_lead_traj[0]
  min_x_lead = ((v_ego + v_lead_0) / 2.0) * (v_ego - v_lead_0) / (-ACCEL_MIN * 2.0)
  x_lead_traj[0] = max(x_lead_traj[0], min_x_lead)
  v_lead_traj = np.clip(v_lead_traj, 0.0, 1e8)

  x_lead_mpc = np.maximum.accumulate(np.interp(T_IDXS, LEAD_T_IDXS_MODEL, x_lead_traj))
  v_lead_mpc = np.interp(T_IDXS, LEAD_T_IDXS_MODEL, v_lead_traj)

  # Forward movement cannot exceed the distance covered by the corrected speed.
  x_lead_max = x_lead_mpc[0] + np.cumsum(T_DIFFS[1:] * (v_lead_mpc[:-1] + v_lead_mpc[1:]) / 2)
  x_lead_mpc[1:] = np.minimum(x_lead_mpc[1:], x_lead_max)
  return np.column_stack((x_lead_mpc, v_lead_mpc))


def upstream_lead_paths(model, radar_state, v_ego):
  """(path for leadOne, path for leadTwo) for the upstream MPC; None for a lead keeps its raw aLeadK extrapolation.

  `model` is the live modelV2 message (nrdr has no StarPilot qualified_model_leads frame-age history, so no freshness
  check is made here beyond the horizon match in build_trajectory); None gives (None, None).
  Mirrors StarPilot's long_mpc.update pairing: model leadsV3[0] with leadOne, [1] with leadTwo, and
  model_v_ego = model.velocity.x[0]."""
  if model is None:
    return None, None
  try:
    model_leads = getattr(model, 'leadsV3', ())
    velocity = getattr(getattr(model, 'velocity', None), 'x', ())
    model_v_ego = velocity[0] if len(velocity) else None
    return tuple(build_trajectory(model_leads[i] if len(model_leads) > i else None, lead, v_ego, model_v_ego)
                 for i, lead in enumerate((radar_state.leadOne, radar_state.leadTwo)))
  except (AttributeError, IndexError, TypeError, ValueError):
    return None, None

