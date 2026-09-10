import math
from dataclasses import dataclass

import numpy as np

from openpilot.nrdr.features.longitudinal.long_tune import LOW_SPEED_JERK_BP, LongTune
from openpilot.selfdrive.modeld.constants import ModelConstants


CROSSFADE_FRAMES = 5
LEAD_ACCEL_FILTER_TAU = 0.4
LEAD_ACCEL_TAU_MAX = 1.0
MAX_EFFECTIVE_BRAKE = 4.5
BRAKE_PERSISTENCE = 0.8
BRAKE_ENGAGE_DELAY = 0.3
BRAKE_RELEASE_TIME = 0.5
MIN_TRACK_AGE = 0.5
LEAD_ACCEL_TAU_NORMALIZER = 1.5
BOSCH_RAW_MLT_MIN_DISTANCE = 12.0
BOSCH_RAW_MLT_MAX_TTC = 5.0
BOSCH_FCW_MIN_MODEL_PROB = 0.9
BOSCH_FCW_MIN_CLOSING_SPEED = 0.5
BOSCH_FCW_MAX_TTC = 4.0

PERSONALITY_NAMES = {
  0: "aggressive",
  1: "standard",
  2: "relaxed",
  3: "econ",
}

PERSONALITY_JERK = {
  "aggressive": 0.4,
  "standard": 1.0,
  "relaxed": 1.0,
  "econ": 1.5,
}

PERSONALITY_T_FOLLOW = {
  "aggressive": 0.75,
  "standard": 1.45,
  "relaxed": 1.75,
  "econ": 2.25,
}

CRUISE_MAX_ACCEL = 2.0


@dataclass(frozen=True)
class MpcPolicyResult:
  lead_0: np.ndarray
  lead_1: np.ndarray
  obstacles: np.ndarray
  t_follow: float
  lead_probability: float
  status: bool


def _personality_name(personality) -> str | None:
  value = personality.raw if hasattr(personality, "raw") else int(personality)
  return PERSONALITY_NAMES.get(value)


def _brake_gate(accel: float, accel_tau: float, threshold: float) -> tuple[bool, float]:
  if not (math.isfinite(accel) and math.isfinite(accel_tau)):
    return False, 0.0
  discounted_accel = accel * (1.0 - np.clip(accel_tau, 0.0, LEAD_ACCEL_TAU_NORMALIZER) / LEAD_ACCEL_TAU_NORMALIZER)
  return discounted_accel < threshold, discounted_accel


class NrdrLongitudinalMpc:
  def __init__(self, dt: float, time_indices: np.ndarray, time_diffs: np.ndarray,
               cruise_min_accel: float, cruise_max_accel: float, min_lead_factor: float,
               accel_min: float, log_fn=None, honda_bosch_a_radar: bool = False):
    self.dt = dt
    self.time_indices = time_indices
    self.time_diffs = time_diffs
    self.cruise_min_accel = cruise_min_accel
    self.cruise_max_accel = cruise_max_accel
    self.min_lead_factor = min_lead_factor
    self.accel_min = accel_min
    self.honda_bosch_a_radar = bool(honda_bosch_a_radar)
    self.lead_time_indices = np.asarray(ModelConstants.LEAD_T_IDXS)
    self.tune = LongTune(log_fn=log_fn)
    self.reset()

  def reset(self) -> None:
    self.track_ids = [None, None]
    self.track_frames = [0, 0]
    self.filtered_accels = [0.0, 0.0]
    self.brake_track_ids = [None, None]
    self.brake_durations = [0.0, 0.0]
    self.effective_brakes = [0.0, 0.0]
    self.track_ages = [0.0, 0.0]

  def jerk_factors(self, personality, default: float, v_ego: float) -> tuple[float, float]:
    default = PERSONALITY_JERK.get(_personality_name(personality), default)
    factors = self.tune.jerk_factors(_personality_name(personality), (default, default))
    if self.tune.low_speed_jerk_scale <= 1.0:
      return factors
    scale = float(np.interp(v_ego, LOW_SPEED_JERK_BP, [self.tune.low_speed_jerk_scale, 1.0]))
    return factors[0] * scale, factors[1] * scale

  def base_jerk(self, personality, fallback) -> float:
    name = _personality_name(personality)
    return PERSONALITY_JERK[name] if name in PERSONALITY_JERK else fallback(personality)

  def t_follow(self, personality, default: float) -> float:
    return PERSONALITY_T_FOLLOW.get(_personality_name(personality), default)

  def _bosch_raw_mlt_fallback(self, radar_lead, v_ego: float) -> bool:
    if not (self.honda_bosch_a_radar and radar_lead.present and getattr(radar_lead, "radar", False)):
      return False
    distance = float(radar_lead.dRel)
    raw_velocity = float(radar_lead.vLead)
    if not (math.isfinite(distance) and math.isfinite(raw_velocity)):
      return True
    closing_speed = max(0.0, float(v_ego) - raw_velocity)
    ttc = distance / max(closing_speed, 1e-3) if closing_speed > 0.1 else math.inf
    return distance <= BOSCH_RAW_MLT_MIN_DISTANCE or ttc <= BOSCH_RAW_MLT_MAX_TTC

  def _bosch_model_horizon_valid(self, model_lead, radar_lead, v_ego: float) -> bool:
    try:
      probability = float(model_lead.prob)
      distance = float(radar_lead.dRel)
      raw_velocity = float(radar_lead.vLead)
      model_x = np.asarray(model_lead.x, dtype=np.float64)
      model_v = np.asarray(model_lead.v, dtype=np.float64)
      v_ego = float(v_ego)
    except (AttributeError, TypeError, ValueError):
      return False
    return (math.isfinite(probability) and probability > 0.5 and
            math.isfinite(distance) and math.isfinite(raw_velocity) and math.isfinite(v_ego) and
            model_x.shape == self.lead_time_indices.shape and model_v.shape == self.lead_time_indices.shape and
            np.all(np.isfinite(model_x)) and np.all(np.isfinite(model_v)))

  def _finite_raw_fallback(self, raw_fallback, radar_lead, v_ego: float) -> np.ndarray:
    if raw_fallback is not None:
      try:
        candidate = np.asarray(raw_fallback, dtype=np.float64)
      except (TypeError, ValueError):
        candidate = np.empty((0, 2), dtype=np.float64)
      if candidate.shape == (len(self.time_indices), 2) and np.all(np.isfinite(candidate)):
        return candidate

    try:
      distance = float(getattr(radar_lead, "dRel", 0.0))
      raw_velocity = float(getattr(radar_lead, "vLead", 0.0))
      v_ego = float(v_ego)
    except (TypeError, ValueError):
      distance, raw_velocity, v_ego = 0.0, 0.0, 0.0
    distance = max(0.0, distance) if math.isfinite(distance) else 0.0
    raw_velocity = max(0.0, raw_velocity) if math.isfinite(raw_velocity) else 0.0
    v_ego = max(0.0, v_ego) if math.isfinite(v_ego) else 0.0
    lead_x = distance + raw_velocity * self.lead_time_indices
    lead_v = np.full_like(self.lead_time_indices, raw_velocity)
    return self._to_mpc_trajectory(lead_x, lead_v, v_ego)

  def fcw_authorized(self, lead, v_ego: float) -> bool:
    if not self.honda_bosch_a_radar:
      return True
    if lead is None or not getattr(lead, "present", False) or not getattr(lead, "radar", False):
      return False
    try:
      model_probability = float(getattr(lead, "modelProb", 0.0))
      distance = float(getattr(lead, "dRel", 0.0))
      raw_velocity = float(getattr(lead, "vLead", 0.0))
      v_ego = float(v_ego)
    except (TypeError, ValueError):
      return False
    if (not all(math.isfinite(value) for value in (model_probability, distance, raw_velocity, v_ego)) or
        model_probability <= BOSCH_FCW_MIN_MODEL_PROB):
      return False
    deprecated = getattr(lead, "deprecated", None)
    if not bool(getattr(deprecated, "fcw", False)):
      return False
    closing_speed = max(0.0, v_ego - raw_velocity)
    if closing_speed < BOSCH_FCW_MIN_CLOSING_SPEED:
      return False
    ttc = max(0.0, distance) / max(closing_speed, 1e-3)
    return ttc < BOSCH_FCW_MAX_TTC

  def _lead_trajectory(self, model_lead, radar_lead, slot: int, v_ego: float,
                       raw_fallback: np.ndarray | None = None) -> np.ndarray:
    if not radar_lead.present:
      lead_x = 50.0 + (v_ego + 10.0) * self.lead_time_indices
      lead_v = np.full_like(self.lead_time_indices, v_ego + 10.0)
      return self._to_mpc_trajectory(lead_x, lead_v, v_ego)

    if self.honda_bosch_a_radar and getattr(radar_lead, "radar", False):
      if (not self._bosch_model_horizon_valid(model_lead, radar_lead, v_ego) or
          self._bosch_raw_mlt_fallback(radar_lead, v_ego)):
        return self._finite_raw_fallback(raw_fallback, radar_lead, v_ego)

    settings = self.tune.lead_consumption
    distance = float(radar_lead.dRel)
    raw_velocity = float(radar_lead.vLead)
    model_x = np.asarray(model_lead.x, dtype=np.float64)
    model_v = np.asarray(model_lead.v, dtype=np.float64)
    model_x = model_x - model_x[0]
    model_v = model_v - model_v[0]

    filtered_velocity = float(getattr(radar_lead, "vLeadK", raw_velocity))
    filtered_accel = float(getattr(radar_lead, "aLeadK", 0.0))
    accel_tau = float(getattr(radar_lead, "aLeadTau", 1.0))
    track_id = getattr(radar_lead, "radarTrackId", -1)

    if track_id != self.track_ids[slot]:
      self.track_ids[slot] = track_id
      self.track_frames[slot] = 0
    else:
      self.track_frames[slot] = min(self.track_frames[slot] + 1, CROSSFADE_FRAMES)

    finite = all(math.isfinite(value) for value in (filtered_velocity, filtered_accel, accel_tau))
    anchor_velocity = raw_velocity
    if settings["m1_anchor"] >= 0.5 and finite:
      escape = settings["m1_alead_escape"]
      escape_weight = np.clip((abs(filtered_accel) - escape) / max(escape, 1e-3), 0.0, 1.0)
      filter_weight = self.track_frames[slot] / CROSSFADE_FRAMES * (1.0 - escape_weight)
      anchor_velocity = filter_weight * filtered_velocity + (1.0 - filter_weight) * raw_velocity

    blend = 0.0
    accel_x = np.zeros_like(self.lead_time_indices)
    accel_v = np.zeros_like(self.lead_time_indices)
    if settings["m2_w_max"] > 0.0 and finite:
      alpha = self.dt / (LEAD_ACCEL_FILTER_TAU + self.dt)
      self.filtered_accels[slot] += alpha * (filtered_accel - self.filtered_accels[slot])
      accel = self.filtered_accels[slot]
      braking, _ = _brake_gate(accel, accel_tau, -settings["m2_alead_deadband"])
      if ((braking or accel > settings["m2_alead_deadband"]) and
          accel_tau < LEAD_ACCEL_TAU_MAX and distance < settings["m2_drel_gate"]):
        blend = settings["m2_w_max"]
        tau = max(accel_tau, 1e-3)
        decay = 1.0 - np.exp(-self.lead_time_indices / tau)
        accel_v = accel * tau * decay
        accel_x = accel * tau * (self.lead_time_indices - tau * decay)
    else:
      self.filtered_accels[slot] = filtered_accel if finite else 0.0

    lead_v = anchor_velocity + model_v * (1.0 - blend) + blend * accel_v
    lead_x = distance + model_x * (1.0 - blend) + blend * accel_x
    return self._to_mpc_trajectory(lead_x, lead_v, v_ego)

  def _to_mpc_trajectory(self, lead_x: np.ndarray, lead_v: np.ndarray, v_ego: float) -> np.ndarray:
    lead_v_0 = lead_v[0]
    minimum_x = self.min_lead_factor * (v_ego + lead_v_0) * (v_ego - lead_v_0) / (-self.accel_min * 2)
    lead_x[0] = max(lead_x[0], minimum_x)
    lead_v = np.clip(lead_v, 0.0, 1e8)
    x_mpc = np.maximum.accumulate(np.interp(self.time_indices, self.lead_time_indices, lead_x))
    v_mpc = np.interp(self.time_indices, self.lead_time_indices, lead_v)
    return np.column_stack((x_mpc, v_mpc))

  def _effective_brake(self, radar_lead, comfort_brake: float, slot: int) -> float:
    settings = self.tune.lead_consumption
    maximum = settings["m3_b_eff_max"]
    if maximum <= comfort_brake or not getattr(radar_lead, "present", False):
      self.brake_durations[slot] = 0.0
      self.effective_brakes[slot] = 0.0
      self.track_ages[slot] = 0.0
      return comfort_brake

    accel = float(getattr(radar_lead, "aLeadK", 0.0))
    accel_tau = float(getattr(radar_lead, "aLeadTau", 1.0))
    track_id = getattr(radar_lead, "radarTrackId", -1)
    if track_id == self.brake_track_ids[slot] and track_id not in (None, -1):
      self.track_ages[slot] = min(self.track_ages[slot] + self.dt, 1e6)
    else:
      self.brake_track_ids[slot] = track_id
      self.track_ages[slot] = 0.0

    active, discounted_accel = _brake_gate(accel, accel_tau, settings["m3_alead_gate"])
    if active and self.track_ages[slot] >= MIN_TRACK_AGE:
      self.brake_durations[slot] = min(self.brake_durations[slot] + self.dt, 1e6)
    else:
      self.brake_durations[slot] = 0.0

    if self.brake_durations[slot] >= BRAKE_PERSISTENCE + BRAKE_ENGAGE_DELAY:
      target = min(max(comfort_brake, -discounted_accel), maximum, MAX_EFFECTIVE_BRAKE)
      self.effective_brakes[slot] = max(self.effective_brakes[slot], target)
    elif self.effective_brakes[slot] > comfort_brake:
      step = (maximum - comfort_brake) * self.dt / BRAKE_RELEASE_TIME
      self.effective_brakes[slot] = max(comfort_brake, self.effective_brakes[slot] - step)
    else:
      self.effective_brakes[slot] = 0.0
    return max(comfort_brake, self.effective_brakes[slot])

  def prepare(self, v_cruise: float, model, radar_state, personality, v_ego: float,
              base_t_follow: float, raw_lead_trajectories=None) -> MpcPolicyResult:
    self.tune.refresh()
    t_follow = max(0.9, base_t_follow + self.tune.t_follow_offset(_personality_name(personality)))
    model_leads = model.leadsV3
    raw_lead_trajectories = (None, None) if raw_lead_trajectories is None else raw_lead_trajectories
    lead_0 = self._lead_trajectory(model_leads[0], radar_state.leadOne, 0, v_ego, raw_lead_trajectories[0])
    lead_1 = self._lead_trajectory(model_leads[1], radar_state.leadTwo, 1, v_ego, raw_lead_trajectories[1])
    comfort_brake = self.tune.comfort_brake

    brake_0 = self._effective_brake(radar_state.leadOne, comfort_brake, 0)
    brake_1 = self._effective_brake(radar_state.leadTwo, comfort_brake, 1)
    obstacle_0 = lead_0[:, 0] + lead_0[:, 1] ** 2 / (2 * brake_0)
    obstacle_1 = lead_1[:, 0] + lead_1[:, 1] ** 2 / (2 * brake_1)

    lower_velocity = v_ego + self.time_indices * self.cruise_min_accel * 1.05
    upper_velocity = v_ego + self.time_indices * self.cruise_max_accel * 1.05
    cruise_velocity = np.clip(np.full(len(self.time_indices), v_cruise), lower_velocity, upper_velocity)
    cruise_distance = (cruise_velocity ** 2 / (2 * comfort_brake) + t_follow * cruise_velocity +
                       self.tune.stop_distance)
    cruise_obstacle = np.cumsum(self.time_diffs * cruise_velocity) + cruise_distance

    return MpcPolicyResult(
      lead_0,
      lead_1,
      np.column_stack((obstacle_0, obstacle_1, cruise_obstacle)),
      t_follow,
      float(model_leads[0].prob),
      bool(model_leads[0].prob > 0.5 or model_leads[1].prob > 0.5),
    )
