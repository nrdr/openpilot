#!/usr/bin/env python3
"""
nrdr_steer_ratio_curve.py — live steer-ratio gap-filler + guided SR Calibrate.

Measures effective SR from IMU yaw vs wheel angle (same physics as steerratio_by_angle):

    SR = |radians(SWA)| / |atan(wheelbase * yaw / v)|

Bins by |SWA|, promotes confident means into a device curve, applies:
  device promoted → fingerprint seed / Clarity twopoint → nearest trusted → scalar.

Gates match the author protocol: hold-still (rate), ≥~7 mph, turning, sanity clamp.
Default Auto gap-fill also requires latActive + !steeringPressed.
SR Calibrate relaxes lat/pressed for lot bootstrap and coaches the next incomplete bin.
"""
from __future__ import annotations

import json
import math
import time

from openpilot.common.params import Params, UnknownKeyName

# Shared |SWA| grid (deg). Matches offline 25° binning; lock target ~250°.
ANGLE_BP = [0.0, 25.0, 50.0, 75.0, 100.0, 125.0, 150.0, 175.0, 200.0, 225.0, 250.0]
BIN_HALF = 12.5  # ±deg around bin center for guided in-band

MIN_V_MS = 7.0 * 0.44704          # ~7 mph
MIN_ABS_SWA_DEG = 5.0
MIN_YAW_RAD_S = 0.03
RATE_GATE_DEG_S = 20.0            # hold still
SR_MIN, SR_MAX = 5.0, 40.0
STD_MAX = 2.5                     # promote only if bin std is sane
# Stickiness: don't let a thin new slice yank a well-proven bin (see Standing Decision).
MAX_PROMOTE_STEP = 0.25           # max |ΔSR| per promote event at 100% rate
N_TRUST_MULT = 5                  # device fully overrides seed once n >= N_min * this

PARAM_REFRESH_FRAMES = 300        # ~3 s
SAVE_FRAMES = 3000                # ~30 s
CALIBRATE_TIMEOUT_S = 45.0 * 60.0

DATA_VERSION = 2


def _n_min(abs_swa: float) -> int:
  # Outer angles have better yaw/SWA SNR — promote faster (mountain-pass mitigation).
  if abs_swa < 40.0:
    return 80
  if abs_swa < 100.0:
    return 50
  return 30


def _n_trust(abs_swa: float) -> int:
  """Samples needed before device fully overrides a fingerprint seed at this angle."""
  return _n_min(abs_swa) * N_TRUST_MULT


def _promote_delta(abs_swa: float) -> int:
  """New samples required since last promote before another update is allowed."""
  return max(20, _n_min(abs_swa) // 2)


def _get_bool(params: Params, key: str, default: bool = False) -> bool:
  try:
    v = params.get(key, return_default=True)
  except (UnknownKeyName, TypeError):
    try:
      return bool(params.get_bool(key))
    except Exception:
      return default
  if v is None:
    return default
  if isinstance(v, (bytes, str)):
    s = v.decode("utf-8") if isinstance(v, bytes) else v
    return s not in ("0", "false", "False", "")
  return bool(v)


def _get_float(params: Params, key: str, default: float, lo: float, hi: float, scale: float = 1.0) -> float:
  try:
    v = params.get(key)
  except UnknownKeyName:
    v = None
  if v is None:
    return default
  try:
    if isinstance(v, bytes):
      v = v.decode("utf-8")
    r = float(v) / scale
  except (TypeError, ValueError):
    return default
  return min(max(r, lo), hi)


def _bin_index(abs_swa: float) -> int:
  # Floor bin matching offline tool: int(a // 25) * 25 → index
  if abs_swa <= ANGLE_BP[0]:
    return 0
  if abs_swa >= ANGLE_BP[-1]:
    return len(ANGLE_BP) - 1
  edge = int(abs_swa // 25.0) * 25.0
  try:
    return ANGLE_BP.index(edge)
  except ValueError:
    best_i, best_d = 0, abs(abs_swa - ANGLE_BP[0])
    for i, a in enumerate(ANGLE_BP):
      d = abs(abs_swa - a)
      if d < best_d:
        best_i, best_d = i, d
    return best_i


def _lerp(x: float, xs: list[float], ys: list[float]) -> float:
  if not xs:
    return 15.0
  if len(xs) == 1 or x <= xs[0]:
    return float(ys[0])
  if x >= xs[-1]:
    return float(ys[-1])
  for i in range(1, len(xs)):
    if x <= xs[i]:
      t = (x - xs[i - 1]) / (xs[i] - xs[i - 1])
      return float(ys[i - 1] + t * (ys[i] - ys[i - 1]))
  return float(ys[-1])


def _empty_bin() -> dict:
  return {"n": 0, "sum": 0.0, "sumsq": 0.0, "nPos": 0, "nNeg": 0}


class SteerRatioCurveLearner:
  def __init__(self, wheelbase: float, max_angle_deg: float = 250.0):
    self.params = Params()
    self.wheelbase = float(wheelbase) if wheelbase else 2.7
    self.max_angle_deg = float(max_angle_deg)
    self.enabled = True
    self.rate = 0.5
    self.calibrate = False
    self.promoted: dict[str, float] = {}   # str(angle) -> SR
    self.promoted_n: dict[str, int] = {}   # str(angle) -> n locked at last promote (stickiness)
    self.bins: dict[str, dict] = {}        # str(angle) -> accum
    self._dirty = False
    self._calibrate_started_mono: float | None = None
    self._target_idx = 0
    self._target_sign = 1  # +1 left/CW convention by SWA sign; coach + then -
    # Live status for snapshot / UI
    self.status = "idle"
    self.target_deg = 0.0
    self.target_sign = 1
    self.in_band = False
    self.hold_ok = False
    self.speed_ok = False
    self.bin_n = 0
    self.bin_n_min = 0
    self.bins_ready = 0
    self.bins_total = 0
    self.last_sample_sr = 0.0
    self._load()
    self._refresh_params(force=True)
    self._refresh_fast_params()
    self._update_guide()

  # --- persistence ---
  def _load(self):
    raw = None
    try:
      raw = self.params.get("NrdrSteerRatioCurveData")
    except UnknownKeyName:
      return
    if raw is None:
      return
    try:
      if isinstance(raw, bytes):
        raw = json.loads(raw.decode("utf-8"))
      elif isinstance(raw, str):
        raw = json.loads(raw)
      if not isinstance(raw, dict):
        return
      self.promoted = {str(k): float(v) for k, v in (raw.get("promoted") or {}).items()}
      self.promoted_n = {str(k): int(v) for k, v in (raw.get("promotedN") or {}).items()}
      bins_in = raw.get("bins") or {}
      self.bins = {}
      for k, b in bins_in.items():
        if isinstance(b, dict):
          self.bins[str(k)] = {
            "n": int(b.get("n", 0)),
            "sum": float(b.get("sum", 0.0)),
            "sumsq": float(b.get("sumsq", 0.0)),
            "nPos": int(b.get("nPos", 0)),
            "nNeg": int(b.get("nNeg", 0)),
          }
      # Migrate v1: infer promoted_n from bin n when missing
      for k in self.promoted:
        if k not in self.promoted_n:
          bn = int((self.bins.get(k) or {}).get("n", 0))
          self.promoted_n[k] = bn if bn > 0 else _n_min(float(k))
    except (TypeError, ValueError, json.JSONDecodeError):
      self.promoted = {}
      self.promoted_n = {}
      self.bins = {}

  def _save(self):
    payload = {
      "version": DATA_VERSION,
      "promoted": self.promoted,
      "promotedN": self.promoted_n,
      "bins": self.bins,
    }
    try:
      self.params.put("NrdrSteerRatioCurveData", payload, block=False)
      self._dirty = False
    except Exception:
      pass

  def _refresh_params(self, force: bool = False):
    self.enabled = _get_bool(self.params, "NrdrSteerRatioCurve", True)
    self.rate = _get_float(self.params, "NrdrSteerRatioCurveRate", 0.5, 0.0, 1.0, scale=100.0)
    # Calibrate/reset handled in _refresh_fast_params every frame.

  # --- apply merge ---
  def apply(self, abs_swa: float, scalar_sr: float,
            seed_bp: list[float] | None, seed_v: list[float] | None,
            twopoint: tuple[float, float] | None) -> tuple[float, str]:
    """Return (sr, mode). Only call when Learn SR is off.

    Device never fully replaces a fingerprint seed until promoted_n earns N_trust —
    thin new drives cannot yank a graduate seed (or a large live pool) overnight.
    """
    seed_pts = self._seed_points(seed_bp, seed_v, twopoint)
    if not self.enabled:
      if seed_pts:
        sr = self._interp_or_nearest(abs_swa, seed_pts)
        mode = "clarity_twopoint" if twopoint and not seed_bp else "seed_curve"
        return sr, mode
      return float(scalar_sr), "scalar_cp"

    seed_sr = self._interp_or_nearest(abs_swa, seed_pts) if seed_pts else None
    device_sr, device_n, device_angle = self._nearest_device(abs_swa)

    if device_sr is not None:
      if seed_sr is not None:
        w = min(1.0, float(device_n) / float(_n_trust(device_angle)))
        sr = float((1.0 - w) * seed_sr + w * device_sr)
        if w >= 0.999:
          return sr, "device_curve"
        if w <= 0.001:
          mode = "clarity_twopoint" if twopoint and not seed_bp else "seed_curve"
          return float(seed_sr), mode
        return sr, "device_seed_blend"
      return float(device_sr), "device_curve"

    if seed_pts:
      sr = self._interp_or_nearest(abs_swa, seed_pts)
      mode = "clarity_twopoint" if twopoint and not seed_bp else "seed_curve"
      # Hold outer via nearest when past seed end
      if abs_swa > seed_pts[-1][0] + BIN_HALF:
        return sr, "nearest_bin"
      return sr, mode

    return float(scalar_sr), "scalar_cp"

  @staticmethod
  def _seed_points(seed_bp, seed_v, twopoint):
    if seed_bp and seed_v and len(seed_bp) == len(seed_v) and len(seed_bp) >= 2:
      return list(zip([float(x) for x in seed_bp], [float(y) for y in seed_v]))
    if twopoint is not None:
      return [(0.0, float(twopoint[0])), (250.0, float(twopoint[1]))]
    return []

  def _device_points(self):
    pts = []
    for k, v in self.promoted.items():
      try:
        pts.append((float(k), float(v)))
      except (TypeError, ValueError):
        continue
    pts.sort(key=lambda p: p[0])
    return pts

  def _nearest_device(self, abs_swa: float) -> tuple[float | None, int, float]:
    """Return (sr, promoted_n, angle) for nearest device bin within tolerance, else (None,0,0)."""
    best = None
    best_d = None
    for k, sr in self.promoted.items():
      try:
        a = float(k)
      except (TypeError, ValueError):
        continue
      d = abs(abs_swa - a)
      if d <= BIN_HALF + 5.0 and (best_d is None or d < best_d):
        best_d = d
        best = (float(sr), int(self.promoted_n.get(k, 0)), a)
    if best is None:
      return None, 0, 0.0
    return best

  @staticmethod
  def _interp_or_nearest(abs_swa: float, pts: list[tuple[float, float]]) -> float:
    if not pts:
      return 15.0
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return _lerp(abs_swa, xs, ys)

  # --- learning ---
  def update(self, frame: int, v_ego: float, steering_angle_deg: float, steering_rate_deg: float,
             yaw_rate: float | None, lat_active: bool, steering_pressed: bool):
    # Calibrate + Reset are safety-sensitive (CLEAR_ON_IGNITION / momentary) — poll every frame.
    self._refresh_fast_params()
    if frame % PARAM_REFRESH_FRAMES == 0:
      self._refresh_params()
      self._check_calibrate_timeout()
      self._update_guide()

    if self._dirty and frame % SAVE_FRAMES == 0:
      self._save()

    if (not self.enabled and not self.calibrate) or (self.rate <= 0.0 and not self.calibrate):
      self.status = "frozen" if self.enabled else "off"
      return

    if yaw_rate is None or self.wheelbase <= 0.0:
      self.status = "no_yaw"
      return

    abs_swa = abs(steering_angle_deg)
    self.speed_ok = v_ego >= MIN_V_MS
    self.hold_ok = abs(steering_rate_deg) <= RATE_GATE_DEG_S
    self.in_band = self._is_in_target_band(steering_angle_deg) if self.calibrate else True

    # Default gap-fill gates
    if not self.calibrate:
      if not lat_active:
        self.status = "need_lat"
        return
      if steering_pressed:
        self.status = "steering_pressed"
        return
    # Calibrate: lat/pressed optional; still need physics gates

    if not self.speed_ok:
      self.status = "too_slow"
      return
    if not self.hold_ok:
      self.status = "hold_still"
      return
    if abs_swa < MIN_ABS_SWA_DEG or abs(yaw_rate) < MIN_YAW_RAD_S:
      self.status = "not_turning"
      return

    # During guided calibrate, only credit the coached bin/sign (keeps wizard focused).
    if self.calibrate and not self.in_band:
      self.status = "aim_target"
      return

    curv = yaw_rate / v_ego
    road_wheel = math.atan(self.wheelbase * curv)
    if abs(road_wheel) < 1e-4:
      self.status = "not_turning"
      return
    sr = abs(math.radians(steering_angle_deg) / road_wheel)
    if not (SR_MIN < sr < SR_MAX):
      self.status = "sr_clamp"
      return

    self.last_sample_sr = float(sr)
    idx = _bin_index(abs_swa)
    angle_key = str(ANGLE_BP[idx])
    b = self.bins.get(angle_key) or _empty_bin()
    b["n"] = int(b["n"]) + 1
    b["sum"] = float(b["sum"]) + sr
    b["sumsq"] = float(b["sumsq"]) + sr * sr
    if steering_angle_deg >= 0.0:
      b["nPos"] = int(b["nPos"]) + 1
    else:
      b["nNeg"] = int(b["nNeg"]) + 1
    self.bins[angle_key] = b
    self._dirty = True
    self.bin_n = int(b["n"])
    self.bin_n_min = _n_min(ANGLE_BP[idx])
    self.status = "accumulating"

    if self._bin_ready(angle_key, ANGLE_BP[idx], require_both_signs=False):
      self._promote_bin(angle_key, ANGLE_BP[idx])

    if self.calibrate:
      self._advance_guide_if_needed()
      if self._lock_coverage_met():
        self._finish_calibrate(reason="complete")

  def _refresh_fast_params(self):
    """Every-frame poll for calibrate clear (ignition) and momentary reset."""
    was_cal = self.calibrate
    self.calibrate = _get_bool(self.params, "NrdrSteerRatioCalibrate", False)
    if self.calibrate and not was_cal:
      self._calibrate_started_mono = time.monotonic()
      self._target_idx = 0
      self._target_sign = 1
      self._update_guide()
    if not self.calibrate:
      self._calibrate_started_mono = None
    if _get_bool(self.params, "NrdrSteerRatioCurveReset", False):
      self.promoted = {}
      self.promoted_n = {}
      self.bins = {}
      self._dirty = True
      self._save()
      try:
        self.params.put_bool("NrdrSteerRatioCurveReset", False)
      except Exception:
        pass
      self._update_guide()

  def _bin_stats(self, b: dict) -> tuple[float, float, int]:
    n = int(b.get("n", 0))
    if n <= 0:
      return 0.0, 0.0, 0
    mean = float(b["sum"]) / n
    var = max(float(b["sumsq"]) / n - mean * mean, 0.0)
    return mean, math.sqrt(var), n

  def _bin_ready(self, key: str, angle: float, require_both_signs: bool) -> bool:
    b = self.bins.get(key)
    if not b:
      return False
    mean, std, n = self._bin_stats(b)
    if n < _n_min(angle) or std > STD_MAX:
      return False
    if require_both_signs and (int(b.get("nPos", 0)) < 1 or int(b.get("nNeg", 0)) < 1):
      return False
    return True

  def _promote_bin(self, key: str, angle: float):
    """Update promoted SR only after enough *new* evidence; step-clamp toward cumulative mean.

    Cumulative bin stats are the long-term pool (never discarded except Reset). Promoted
    values move slowly toward that mean so 1–2 thin drives cannot yank a large history.
    Rate scales the max step (0 = freeze promoted; calibrate still allows first fill).
    """
    b = self.bins.get(key)
    if not b:
      return
    mean, std, n = self._bin_stats(b)
    if n < _n_min(angle) or std > STD_MAX:
      return

    old = self.promoted.get(key)
    old_n = int(self.promoted_n.get(key, 0))

    # First fill: accept cumulative mean once ready (calibrate / cold start).
    if old is None:
      self.promoted[key] = float(mean)
      self.promoted_n[key] = int(n)
      self._dirty = True
      return

    # Need a milestone of new samples since last promote (prevents per-frame yank).
    if (n - old_n) < _promote_delta(angle):
      return

    if self.rate <= 0.0 and not self.calibrate:
      # Freeze applied curve; keep accumulating bin stats for later.
      self.promoted_n[key] = int(n)
      return

    # Step toward cumulative mean; rate scales aggressiveness.
    # Calibrate: larger steps so a deliberate lot session can land, still not unbounded.
    if self.calibrate:
      max_step = MAX_PROMOTE_STEP * 4.0
    else:
      max_step = MAX_PROMOTE_STEP * self.rate
    target = float(mean)
    delta = target - float(old)
    if delta > max_step:
      delta = max_step
    elif delta < -max_step:
      delta = -max_step
    self.promoted[key] = float(old) + delta
    self.promoted_n[key] = int(n)
    self._dirty = True

  def _lock_bins(self) -> list[float]:
    # Consecutive bins from first useful angle through near lock.
    lock = min(self.max_angle_deg, ANGLE_BP[-1])
    return [a for a in ANGLE_BP if MIN_ABS_SWA_DEG <= a <= lock + 1e-6]

  def _lock_coverage_met(self) -> bool:
    for a in self._lock_bins():
      key = str(a)
      # Calibrate complete wants both signs for bias cancel.
      if not self._bin_ready(key, a, require_both_signs=True):
        # Also accept if already promoted with both signs seen historically
        b = self.bins.get(key) or _empty_bin()
        if key in self.promoted and int(b.get("nPos", 0)) >= 1 and int(b.get("nNeg", 0)) >= 1:
          continue
        return False
    return True

  def _coverage_counts(self) -> tuple[int, int]:
    total = len(self._lock_bins())
    ready = 0
    for a in self._lock_bins():
      key = str(a)
      if self._bin_ready(key, a, require_both_signs=False) or key in self.promoted:
        ready += 1
    return ready, total

  # --- guided calibrate ---
  def _update_guide(self):
    ready, total = self._coverage_counts()
    self.bins_ready = ready
    self.bins_total = total
    targets = self._lock_bins()
    if not targets:
      self.target_deg = 0.0
      return
    # Find first incomplete (needs samples or missing a sign)
    for i, a in enumerate(targets):
      key = str(a)
      b = self.bins.get(key) or _empty_bin()
      need_n = not self._bin_ready(key, a, require_both_signs=False)
      need_pos = int(b.get("nPos", 0)) < max(1, _n_min(a) // 4)
      need_neg = int(b.get("nNeg", 0)) < max(1, _n_min(a) // 4)
      if need_n or need_pos or need_neg:
        self._target_idx = i
        self.target_deg = float(a)
        if need_pos:
          self._target_sign = 1
        elif need_neg:
          self._target_sign = -1
        else:
          self._target_sign = 1 if int(b.get("nPos", 0)) <= int(b.get("nNeg", 0)) else -1
        self.target_sign = self._target_sign
        self.bin_n = int(b.get("n", 0))
        self.bin_n_min = _n_min(a)
        return
    self._target_idx = len(targets) - 1
    self.target_deg = float(targets[-1])
    self.target_sign = self._target_sign

  def _is_in_target_band(self, steering_angle_deg: float) -> bool:
    desired = self.target_deg * float(self._target_sign)
    return abs(steering_angle_deg - desired) <= BIN_HALF

  def _advance_guide_if_needed(self):
    self._update_guide()

  def _check_calibrate_timeout(self):
    if not self.calibrate or self._calibrate_started_mono is None:
      return
    if time.monotonic() - self._calibrate_started_mono > CALIBRATE_TIMEOUT_S:
      self._finish_calibrate(reason="timeout")

  def _finish_calibrate(self, reason: str):
    # Promote any ready bins, then clear calibrate toggle.
    for a in self._lock_bins():
      key = str(a)
      if self._bin_ready(key, a, require_both_signs=False):
        self._promote_bin(key, a)
    if self._dirty:
      self._save()
    self.calibrate = False
    self._calibrate_started_mono = None
    try:
      self.params.put_bool("NrdrSteerRatioCalibrate", False)
    except Exception:
      pass
    self.status = f"calibrate_{reason}"
    self._update_guide()

  def snapshot_fields(self) -> dict:
    side = "L" if self.target_sign > 0 else "R"
    return {
      "curveAuto": bool(self.enabled),
      "calibrate": bool(self.calibrate),
      "curveStatus": self.status,
      "curveTargetDeg": round(float(self.target_deg), 1),
      "curveTargetSide": side,
      "curveInBand": bool(self.in_band),
      "curveHoldOk": bool(self.hold_ok),
      "curveSpeedOk": bool(self.speed_ok),
      "curveBinN": int(self.bin_n),
      "curveBinNMin": int(self.bin_n_min),
      "curveBinsReady": int(self.bins_ready),
      "curveBinsTotal": int(self.bins_total),
      "curvePromotedCount": len(self.promoted),
      "curveLastSampleSr": round(float(self.last_sample_sr), 2),
    }
