"""Offline-only A/B on retained *.raw.npz and sibling *.metadata.json (deep_scan_extract schema).

A = logged host bus-0 0x1FA COMPUTER_BRAKE, in counts (not pressure or acceleration).
B = A plus a bounded release tail. Never reduce an onset, initiate a brake from coasting,
or shape gas. Inspired by the *time* component of https://github.com/Biscuit-Labs/openpilot/pull/43, merged at
723755ee9b074ee6520eb7ac2dadc14a0e970d64. Its Bosch thresholds, force/gas maps, stop
gap and radar policies do NOT transfer. The 3-count ceiling and rolling <=5 m/s band
are deliberately small experimental choices, not measured Nidec calibrations.

Reads local files, writes JSON only to stdout. No CAN sender, controller or device imports.
Usage: python -B -m openpilot.nrdr.tools.civic_pcm_brake_shadow SEGMENTS_DIR [SEGMENTS_DIR ...]
       [--window FULL_ROUTE@START:END] [--all-rolling-speeds]

Retained 2026-11-04 A/B reference (v3 + v2 + evening extraction roots): 748 unique
segments, 7,082 primary in-scope frames, zero changed. Six of seven releases had no
witnessed qualified onset; the remaining pulse lasted 6.6893 s. No evidence for a
stop-and-go cycling benefit. Removing only the speed ceiling changed 59/344,864
frames (21 releases; 105 -> 104 onsets). These are frozen packet histories, not a
prediction of pressure, following distance, jerk or driver response.
"""
import argparse
from collections import Counter
import json
from pathlib import Path

import numpy as np


HOLD_S, MAX_GAP_S, CAP = 1.5, .045, 3


def civic_pcm(config):
  cp, sp = config.get("carParams", {}), config.get("carParamsSP", {})
  flags, sp_flags = cp.get("flags"), sp.get("flags")
  safety = cp.get("safetyConfigs", [])
  return (cp.get("carFingerprint") == "HONDA_CIVIC" and cp.get("openpilotLongitudinalControl") is True
          and cp.get("pcmCruise") is True and isinstance(flags, int) and flags & 16 and not flags & (4 | 2048)
          and len(safety) == 1 and safety[0].get("safetyModel") == "hondaNidec" and safety[0].get("safetyParam") == 0
          and sp.get("enableGasInterceptor") is False and isinstance(sp_flags, int) and not sp_flags & (1 | 16)
          and sp.get("safetyParam") == 0)


def brake_shadow(t, a, scope, demand, hud_off, *, releases=None):
  """Reset at missing/invalid records and segment boundaries. First positive run is left-censored.

  Only a witnessed 0 -> positive -> 0 physical command can start a tail. Duration is
  measured from the observed rising edge, not extended by synthesized counts. Abort on
  release of decel demand, HUD authority, or scope. Never raise a subsequent positive command.
  """
  b = a.copy()
  stats = Counter()
  previous = -2
  onset = None
  tail = 0
  for i in np.flatnonzero(scope):
    if previous != i - 1 or not 0 < t[i] - t[previous] <= MAX_GAP_S:
      onset, tail = None, 0
    elif a[i] > 0:
      if a[previous] == 0:
        stats["observed_onsets_A"] += 1
        onset = t[i]
        if b[previous] == 0:
          stats["observed_onsets_B"] += 1
      tail = 0
    elif a[previous] > 0:
      stats["observed_releases_A"] += 1
      age = None if onset is None else t[i] - onset
      if releases is not None:
        releases.append((i, age))
      if age is None:
        stats["left_censored_releases"] += 1
      elif age >= HOLD_S:
        stats["long_pulse_releases"] += 1
      if onset is not None and t[i] - onset < HOLD_S:
        stats["early_releases"] += 1
        if not demand[i]:
          stats["release_veto_demand"] += 1
        elif not hud_off[i]:
          stats["release_veto_hud"] += 1
        else:
          tail = min(CAP, a[previous])
          stats["changed_releases"] += 1
    if onset is None or t[i] - onset >= HOLD_S or not demand[i] or not hud_off[i]:
      tail = 0
    if tail:
      b[i] = tail
    previous = i
  return b, stats


def past(z, fields, stream, cols, t, max_age):
  """Latest valid packet at or before the command (never reach past an invalid packet)."""
  result = np.full((len(cols), len(t)), np.nan)
  names = fields.get(stream, [])
  if stream not in z or not all(k in names for k in ("mono", "valid", *cols)):
    return result
  rows = z[stream]
  if not len(rows):
    return result
  stamps = rows[:, names.index("mono")]
  idx = np.searchsorted(stamps, t, side="right") - 1
  age = t - stamps[idx]
  ok = (idx >= 0) & (age >= 0) & (age <= max_age) & (rows[idx, names.index("valid")] == 1)
  result[:, ok] = rows[idx[ok]][:, [names.index(k) for k in cols]].T
  return result


def runs(mask):
  edges = np.flatnonzero(np.diff(np.r_[False, mask, False].astype(int)))
  return zip(edges[::2], edges[1::2], strict=True)


def stable_tx(z, fields, t):
  """safetyTxBlocked is cumulative. Require two fresh, consecutive, unchanged reports,
  not a lifetime total of zero. This is a veto, not proof a particular TX passed.
  """
  name = "pandaStates"
  names = fields.get(name, [])
  if name not in z or "tx_blocked" not in names:
    return np.zeros(len(t), bool)
  rows = z[name]
  ts, valid, count = (rows[:, names.index(k)] for k in ("mono", "valid", "tx_blocked"))
  stable = ((np.diff(ts) > 0) & (np.diff(ts) <= .25) & (np.diff(count) == 0) & (count[1:] >= 0)
            & (valid[:-1] == 1) & (valid[1:] == 1))
  idx = np.searchsorted(ts, t, side="right") - 1
  ok = idx >= 1
  ok[ok] = stable[idx[ok] - 1] & (t[ok] - ts[idx[ok]] <= .25)
  return ok


def analyze(path, meta, windows, *, all_rolling_speeds=False):
  stats, examples, watched = Counter(), [], {}
  fields = meta["fields"]
  stream = "sendcan_0_506"
  with np.load(path, allow_pickle=False) as z:
    if stream not in z:
      return Counter(no_host_brake_stream_segments=1), [], [], {}
    rows, names = z[stream], fields[stream]
    t, valid, a, cancel, override, rq = (rows[:, names.index(k)] for k in ("mono", "valid", "brake", "cancel", "override", "brake_request"))
    v, actual, gas, pedal, aeb, can_ok, fault, stand = past(
      z, fields, "carState", ("v", "a", "pedal_gas", "pedal_brake", "stock_aeb", "can_valid", "acc_fault", "standstill"), t, .05)
    active, enabled, request, state = past(z, fields, "carControl", ("active", "enabled", "request", "long_state"), t, .05)
    pcm, ref = past(z, fields, "carControlSP", ("pcm_enabled", "ref_mono"), t, .05)
    allowed, allowed_long, rx_bad = past(z, fields, "pandaStates", ("controls_allowed", "controls_long", "rx_checks_invalid"), t, .25)
    tx_ok = stable_tx(z, fields, t)
    speed, allowance = past(z, fields, "can_128_780", ("pcm_speed", "pcm_gas"), t, .15)
    pressure, = past(z, fields, "can_0_487", ("pressure1_raw",), t, .05)
    echo_name = "can_128_506"
    echo_fall = np.empty(0)
    if echo_name in z:
      echo = z[echo_name]
      et, ev, eb = (echo[:, fields[echo_name].index(k)] for k in ("mono", "valid", "brake"))
      gap = np.diff(et)
      echo_fall = et[1:][(ev[1:] == 1) & (ev[:-1] == 1) & (gap >= 0) & (gap <= MAX_GAP_S) & (eb[:-1] > 0) & (eb[1:] == 0)]
  runtime = ((valid == 1) & (override == 1) & (cancel == 0) & (rq == (a > 0)) & (a >= 0) & (a <= 255) & (a == np.floor(a))
             & (enabled == 1) & (active == 1) & np.isin(state, [1, 2]) & (pcm == 1) & (t >= ref) & (t - ref <= .25)
             & (allowed == 1) & (allowed_long == 1) & tx_ok & (rx_bad == 0) & (can_ok == 1) & (fault == 0)
             & (gas == 0) & (pedal == 0) & (aeb == 0) & np.isfinite(request) & np.isfinite(v))
  scope = runtime & (stand == 0) & (v > 0) & np.isfinite(speed) & np.isfinite(allowance)
  if not all_rolling_speeds:
    scope &= v <= 5
  release_rows = []
  b, edges = brake_shadow(t, a, scope, request < 0, (speed == 0) & (allowance == 0), releases=release_rows)
  changed = scope & (b != a)
  stats.update(edges)
  stats.update(host_frames=len(t), runtime_frames=int(runtime.sum()), rolling_scope_frames=int(scope.sum()), changed_frames=int(changed.sum()),
               rolling_positive_A=int((scope & (a > 0)).sum()), rolling_positive_B=int((scope & (b > 0)).sum()),
               scope_2_to_4_mps=int((scope & (v >= 2) & (v <= 4)).sum()), changed_2_to_4_mps=int((changed & (v >= 2) & (v <= 4)).sum()),
               added_count_frames=int(np.sum((b - a)[changed])))
  rel = t - meta["init"]["mono"]
  releases = []
  for i, age in release_rows:
    j = np.searchsorted(echo_fall, t[i])
    lag = echo_fall[j] - t[i] if j < len(echo_fall) else np.inf
    releases.append({"segment": meta["segment"], "release_s": round(rel[i], 4), "on_duration_s": None if age is None else round(age, 4),
                     "prior_count": int(a[i-1]), "B_count": int(b[i]), "v_mps": round(v[i], 3), "request_mps2": round(request[i], 3),
                     "pcm_speed_mps": round(speed[i], 3), "pcm_gas": int(allowance[i]),
                     "observed_echo_fall_ms": round(lag * 1000, 1) if lag <= .08 else None})
  for start, end in runs(changed):
    examples.append({"segment": meta["segment"], "first_s": round(rel[start], 4), "last_s": round(rel[end-1], 4), "frames": int(end-start),
                     "prior_brake": int(a[start-1]), "shadow_brake": int(b[start]), "speed_mps": round(v[start], 3),
                     "request_mps2": round(request[start], 3), "logged_accel_mps2": round(actual[start], 3) if np.isfinite(actual[start]) else None,
                     "logged_pressure_raw": int(pressure[start]) if np.isfinite(pressure[start]) else None})
  for label, lo, hi in windows:
    sel = (rel >= lo) & (rel < hi) & runtime
    if np.any(sel):
      watched[label] = Counter(runtime_frames=int(sel.sum()), positive_A=int((sel & (a > 0)).sum()),
                               positive_B=int((sel & (b > 0)).sum()), rolling_scope=int((sel & scope).sum()), changed=int((sel & changed).sum()))
  return stats, examples, releases, watched


def replay(roots, windows=(), *, all_rolling_speeds=False):
  # Same source may appear in two completed extraction roots; never count it twice or silently pick a conflict.
  seen, routes, watched = {}, {}, {}
  duplicates = 0
  for root in roots:
    markers = sorted(root.glob("*/*.metadata.json"))
    if not markers:
      raise ValueError(f"no segment metadata under {root}")
    for marker in markers:
      meta = json.loads(marker.read_text(encoding="utf-8"))
      route, segment = meta["route"], meta["segment"]
      key, sha = (route, segment), meta["source_sha256"]
      if len(sha) != 64:
        raise ValueError(f"missing source hash: {marker}")
      if key in seen:
        if seen[key] != sha:
          raise ValueError(f"conflicting sources for {key}")
        duplicates += 1
        continue
      seen[key] = sha
      out = routes.setdefault(route, {"commits": [], "counts": Counter(), "changes": [], "releases": []})
      commit = (meta.get("init") or {}).get("gitCommit")
      if commit not in out["commits"]:
        out["commits"].append(commit)
      out["counts"]["segments"] += 1
      if meta.get("config_inherited_from_segment"):
        out["counts"]["inherited_configuration_segments"] += 1
      if not civic_pcm(meta.get("config", {})):
        out["counts"]["configuration_excluded_segments"] += 1
        continue
      raw = marker.with_suffix("").with_suffix(".raw.npz")
      applicable = [(label, lo, hi) for label, name, lo, hi in windows if name == route]
      stats, examples, releases, samples = analyze(raw, meta, applicable, all_rolling_speeds=all_rolling_speeds)
      out["counts"].update(stats)
      out["changes"].extend(examples)
      out["releases"].extend(releases)
      for label, values in samples.items():
        watched.setdefault(label, Counter()).update(values)
  total = Counter()
  for out in routes.values():
    total.update(out["counts"])
  return {"arm": "all-rolling-speed sensitivity" if all_rolling_speeds else "primary: rolling <=5 m/s",
          "duplicate_segments_skipped": duplicates, "totals": total, "routes": routes,
          "windows": {label: watched.get(label, {"runtime_frames": 0}) for label, *_ in windows}}


def window_arg(arg):
  try:
    route, bounds = arg.split("@")
    lo, hi = map(float, bounds.split(":"))
    if not (0 <= lo < hi and np.isfinite(hi)):
      raise ValueError
    return arg, route, lo, hi
  except ValueError as exc:
    raise argparse.ArgumentTypeError("use FULL_ROUTE@START:END (seconds since route init)") from exc


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("roots", nargs="+", type=Path, help="local segments directory/directories")
  parser.add_argument("--window", action="append", type=window_arg, default=[])
  parser.add_argument("--all-rolling-speeds", action="store_true", help="separate sensitivity: remove only the 5 m/s ceiling")
  args = parser.parse_args()
  print(json.dumps(replay(args.roots, args.window, all_rolling_speeds=args.all_rolling_speeds), indent=2, allow_nan=False))
