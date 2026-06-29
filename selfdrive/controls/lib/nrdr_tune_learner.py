#!/usr/bin/env python3
"""
nrdr_tune_learner.py - 2D online lateral tune learner.

Learns a per-(speed, |steering angle|) feedforward TRIM that cancels the car's systematic,
direction-dependent steering bias -- the over/under-turn surface that tune_grid.py measures.
It is a gain-scheduled, persistent integrator: each cell slowly accumulates the steady-state
tracking error seen there until that cell's error goes to zero, and the learned surface is
saved across drives. Offline companion: tune_learn_tool.py (seed from grids, view/diff the map).

SAFETY -- this moves the wheel, so every lever is deliberately conservative:
  * the output is a SEPARATE additive trim, hard-clamped to +-TRIM_HARD_FRAC * steer_max. The PID
    always does the driving; the trim can only ever nudge within a tight bound, in front of the
    same steer_max clamp the rest of the output already passes through.
  * learning is SLOW (LEARN_RATE_REF, scaled by a <=100% user rate) -- far below the control
    rate, so it cannot chase noise into the loop.
  * learning is GATED to clean, quasi-steady, hands-off, lat-active driving: low steering rate
    (so it learns the steady bias, not transient slew lag), sane speed, bounded error, and
    paramsd settled (its own valid flags) -- so it never chases the kinematic estimator (steer
    ratio / offset / stiffness) while that is still adapting. Different layer, no turf war.
  * bilinear apply + bilinear-weighted learn -> smooth output, no torque steps at bin edges.
  * defaults OFF (NrdrTuneLearner). Viewable, resettable (NrdrTuneLearnerReset), and seedable
    offline. The learned surface persists in NrdrTuneLearnerMap.
"""
import numpy as np

from openpilot.common.params import Params

MS_TO_MPH = 2.23694

# Grid geometry -- MUST match tune_grid.py so the offline seed/view tools map cell-for-cell.
SPEED_MAX_MPH = 85.0
SPEED_BIN_MPH = 5.0
ANGLE_MAX_DEG = 500.0
ANGLE_BIN_DEG = 20.0
N_SPEED = int(SPEED_MAX_MPH / SPEED_BIN_MPH)   # 17 speed rows
N_ANGLE = int(ANGLE_MAX_DEG / ANGLE_BIN_DEG)   # 25 angle columns

MIN_ABS_DES = 1.0          # deg: dead-ahead band -- no trim, no learning (center boost owns center)

# --- safety / learning constants ---
TRIM_HARD_FRAC = 1.0       # hard cap on any stored cell, as a fraction of steer_max (still bounded by the final steer_max clamp)
LEARN_RATE_REF = 2.0e-5    # torque per (deg of error) per frame at 100% user rate
LEARN_MIN_SPEED_MS = 5.0 / MS_TO_MPH   # ~5 mph: below this the steering signal is transient junk
RATE_GATE_DEG_S = 25.0     # only learn when the wheel is quasi-steady (filters turn-in / unwind lag)
ERR_REJECT_DEG = 30.0      # ignore outlier frames (glitches / large transients)

PARAM_REFRESH_FRAMES = 300   # ~3 s: refresh toggles/sliders, honor reset (matches latcontrol cadence)
SAVE_FRAMES = 3000           # ~30 s: persist the learned map while it's still changing


def _get_float(params, key, default, lo, hi, scale=1.0):
  # Mirror of latcontrol_pid.get_param_float, duplicated here to avoid a circular import.
  v = params.get(key)
  if v is None:
    return default
  try:
    if isinstance(v, bytes):
      v = v.decode("utf-8")
    r = float(v) / scale
  except (TypeError, ValueError):
    return default
  return min(max(r, lo), hi)


class TuneLearner:
  def __init__(self, dt: float, steer_max: float):
    self.dt = float(dt)
    self.steer_max = float(steer_max) if steer_max else 1.0
    self.params = Params()
    self.map_l = np.zeros((N_SPEED, N_ANGLE), dtype=np.float32)
    self.map_r = np.zeros((N_SPEED, N_ANGLE), dtype=np.float32)
    self.enabled = False
    self.max_trim = 0.10 * self.steer_max
    self.rate = 0.30
    self.dirty = False
    self._load()
    self._refresh_params()

  # --- bilinear grid helpers over (speed mph, |angle| deg) ---
  def _grid_pos(self, v_ego, abs_des):
    sf = (v_ego * MS_TO_MPH) / SPEED_BIN_MPH - 0.5   # -0.5 -> sample at bin centers
    af = abs_des / ANGLE_BIN_DEG - 0.5
    sf = min(max(sf, 0.0), N_SPEED - 1.0)
    af = min(max(af, 0.0), N_ANGLE - 1.0)
    s0 = int(sf)
    a0 = int(af)
    s1 = min(s0 + 1, N_SPEED - 1)
    a1 = min(a0 + 1, N_ANGLE - 1)
    return s0, s1, a0, a1, sf - s0, af - a0

  def _bilinear(self, m, v_ego, abs_des):
    s0, s1, a0, a1, ws, wa = self._grid_pos(v_ego, abs_des)
    return float(m[s0, a0] * (1.0 - ws) * (1.0 - wa) + m[s1, a0] * ws * (1.0 - wa)
                 + m[s0, a1] * (1.0 - ws) * wa + m[s1, a1] * ws * wa)

  def _accumulate(self, m, v_ego, abs_des, delta):
    hard = TRIM_HARD_FRAC * self.steer_max
    s0, s1, a0, a1, ws, wa = self._grid_pos(v_ego, abs_des)
    for s, a, w in ((s0, a0, (1.0 - ws) * (1.0 - wa)), (s1, a0, ws * (1.0 - wa)),
                    (s0, a1, (1.0 - ws) * wa), (s1, a1, ws * wa)):
      m[s, a] = min(max(float(m[s, a]) + delta * w, -hard), hard)

  # --- runtime: bounded learned trim, added to the output every active frame ---
  def apply(self, v_ego, desired_deg):
    if not self.enabled:
      return 0.0
    abs_des = abs(desired_deg)
    if abs_des < MIN_ABS_DES:
      return 0.0
    m = self.map_l if desired_deg > 0.0 else self.map_r
    trim_norm = self._bilinear(m, v_ego, abs_des)
    trim_norm = min(max(trim_norm, -self.max_trim), self.max_trim)
    return trim_norm if desired_deg > 0.0 else -trim_norm

  # --- learning: nudge the map from this frame's steady-state error (map only; never the output) ---
  def learn(self, v_ego, desired_deg, error, steering_rate_deg, steering_pressed, paramsd_ok, frame):
    if frame % PARAM_REFRESH_FRAMES == 0:
      self._refresh_params()
    if self.dirty and self.enabled and frame % SAVE_FRAMES == 0:
      self._save()
    if not self.enabled:
      return
    abs_des = abs(desired_deg)
    # paramsd_ok gates out frames where the kinematic estimator (steer ratio / offset / stiffness)
    # isn't vouching for itself -- don't learn a tracking trim against a target that's still moving.
    if (steering_pressed or not paramsd_ok or abs_des < MIN_ABS_DES or v_ego < LEARN_MIN_SPEED_MS
        or abs(steering_rate_deg) > RATE_GATE_DEG_S or abs(error) > ERR_REJECT_DEG):
      return
    # Direction-normalize so +error = under-turn = needs more turn (tune_grid's convention);
    # the stored trim is then "extra turn in the commanded direction".
    norm_err = error if desired_deg > 0.0 else -error
    m = self.map_l if desired_deg > 0.0 else self.map_r
    self._accumulate(m, v_ego, abs_des, self.rate * LEARN_RATE_REF * norm_err)
    self.dirty = True

  # --- params + persistence ---
  def _refresh_params(self):
    self.enabled = self.params.get_bool("NrdrTuneLearner")
    self.max_trim = _get_float(self.params, "NrdrTuneLearnerStrength", 0.10, 0.0, TRIM_HARD_FRAC, 100.0) * self.steer_max
    self.rate = _get_float(self.params, "NrdrTuneLearnerRate", 0.30, 0.0, 1.0, 100.0)
    if self.params.get_bool("NrdrTuneLearnerReset"):
      self.map_l[:] = 0.0
      self.map_r[:] = 0.0
      self.dirty = True
      self._save()
      self.params.put_bool("NrdrTuneLearnerReset", False)

  def _load(self):
    raw = self.params.get("NrdrTuneLearnerMap")
    n = N_SPEED * N_ANGLE
    if raw and len(raw) == 2 * n * 4:
      arr = np.frombuffer(raw, dtype=np.float32)
      self.map_l = arr[:n].reshape(N_SPEED, N_ANGLE).copy()
      self.map_r = arr[n:].reshape(N_SPEED, N_ANGLE).copy()

  def _save(self):
    blob = np.concatenate([self.map_l.ravel(), self.map_r.ravel()]).astype(np.float32).tobytes()
    self.params.put("NrdrTuneLearnerMap", blob)
    self.dirty = False
