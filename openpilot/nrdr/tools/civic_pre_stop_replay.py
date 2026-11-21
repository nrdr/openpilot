"""Nov 4 Civic diagnostics. Local extracted packets only; no control, Params, or CAN writer.

Run with the evening archive and earlier deep-scan-v2/v3 segments directories.
Outputs JSON to stdout. All B arms are independent command-space sensitivities, not
vehicle simulations. Never feed a hypothetical outcome into a later recorded sample.
"""
import argparse
from collections import Counter
import json
import math
from pathlib import Path

import numpy as np

from openpilot.nrdr.tools.civic_pcm_brake_shadow import civic_pcm, past, runs, stable_tx


DT, MPH = .02, .44704
C, D, B = "0000018c--563c5ee60c", "0000018d--d59b49fe33", "0000018b--451da3eb4a"
EVENING_BUILD = "76bced854eedd316dae9f24c08e4256a69af2821"
STOCK = {"147": 32, "148": 11, "14c": 12, "188": 46, "189": 107, "18a": 10}
WINDOWS = {
  C: [(451., 453.24, "rolling stop 1"), (526.08, 527.48, "stationary activation into creep"),
      (527.9, 532.22, "rolling stop 2"), (963., 967.95, "PID approach"), (585.03, 590.45, "closing lead")],
  D: [(740.70, 742.80, "successful rolling stop"), (750., 775., "successful hold plateau"), (789.2, 791., "departure")],
  B: [(225., 233., "high-speed dead zone"), (63.03, 88.77, "other hill")],
}
HUD_WINDOWS = {C: [(450.993, 453.446605, "P07 stopping"), (526.065, 532.427987, "P08 entire activation"),
                   (526.065, 527.062, "P08 still stationary"), (527.062, 527.483, "P08 first motion"),
                   (957., 968.159476, "P09 PID")],
               D: [(740.683, 742.973, "successful stopping"), (743.004, 788.169, "held until stop clears"),
                   (788.181, 791., "valid PID departure")]}


def hud_veto(raw, meta, result):
  """fc8b77b51 gate, paired at real HUD packet cadence. No extra request/lead/standstill gates.

  Controller inputs are causal log joins, not a claim to know the exact receive tick.
  Use the send timestamp for the state; bin paired bus-128 echoes by their OWN wire times.
  No simulation of later launch/governor state or physical brake response.
  """
  fields = meta["fields"]
  h, e = "sendcan_0_780", "can_128_780"
  if h not in raw or e not in raw:
    result["coverage"]["missing_stream_segments"] += 1
    return
  sent, echo = raw[h], raw[e]
  st, valid, speed, gas = (sent[:, fields[h].index(k)] for k in ("mono", "valid", "pcm_speed", "pcm_gas"))
  et, ev, es, eg = (echo[:, fields[e].index(k)] for k in ("mono", "valid", "pcm_speed", "pcm_gas"))
  active, state = past(raw, fields, "carControl", ("active", "long_state"), st, .05)
  sp = raw["carControlSP"]
  seen = sp[(sp[:, 1] == 1) & (sp[:, fields["carControlSP"].index("pcm_enabled")] == 1), 0]
  # Conservative segment-start censoring until first witnessed speed-led confirmation.
  known = (valid == 1) & np.isin(state, [0, 1, 2, 3]) & np.isin(active, [0, 1]) & (st >= (seen[0] if len(seen) else np.inf))
  veto = known & (active == 1) & ~np.isin(state, [1, 3])
  i = np.searchsorted(st, et, side="right")-1
  if not len(st):
    result["coverage"]["unpaired_echo"] += len(et)
    return
  paired = (i >= 0) & (et-st[i] <= .05) & (ev == 1) & (valid[i] == 1) & (eg == gas[i]) & (es == speed[i])
  # Ambiguous batched echoes are not counted as multiple confirmations of one send.
  unique = np.bincount(i[paired], minlength=len(st)) == 1
  paired &= unique[i]
  coverage = result["coverage"]
  coverage.update(echo=len(et), sent=len(st), paired=int(paired.sum()), unpaired_echo=int((~paired).sum()),
                  active_unpaired_sends=int(((active == 1) & ~unique).sum()))
  rel = et - meta["init"]["mono"]
  for lo, hi, name in [(-np.inf, np.inf, "all"), *HUD_WINDOWS[meta["route"]]]:
    where = (rel >= lo) & (rel < hi)
    if not np.any(where):
      continue
    p = paired & known[i] & where
    mask = p & (active[i] == 1)
    cut = mask & veto[i]
    changed = cut & ((eg > 0) | (es > 0))
    c = result["windows"].setdefault(name, Counter())
    c.update(wire=int(where.sum()), paired_known=int(p.sum()), active=int(mask.sum()), veto=int(cut.sum()),
             changed=int(changed.sum()), gas_to_zero=int((cut & (eg > 0)).sum()), speed_to_zero=int((cut & (es > 0)).sum()),
             positive_unchanged=int((mask & ~cut & ((eg > 0) | (es > 0))).sum()))
    if name == "all":
      for j in np.flatnonzero(changed):
        result["changed_packets"].append([int(meta["segment"]), round(rel[j], 5), int(state[i[j]]), es[j], int(eg[j])])


def q(x, f=np.mean):
  x = np.asarray(x)
  x = x[np.isfinite(x)]
  return round(float(f(x)), 4) if len(x) else None


def valid(d, name, age):
  return (d[name+"_valid"] == 1) & (d[name+"_age"] >= 0) & (d[name+"_age"] <= age)


def consumed(raw, fields, mono, wanted):
  """Match the plan named by controlsState, not the most recent radar/plan publication."""
  plan, cols = raw["longitudinalPlan"], fields["longitudinalPlan"]
  out = np.full((3, len(mono)), np.nan)
  if not len(plan):
    return out
  ts = np.rint(plan[:, 0]*1e9).astype(np.int64)
  key = np.rint(np.nan_to_num(wanted, nan=-1.)*1e9).astype(np.int64)
  idx = np.minimum(np.searchsorted(ts, key), len(ts)-1)
  ok = (ts[idx] == key) & (plan[idx, 1] == 1) & (mono >= wanted) & (mono-wanted <= .25)
  out[:, ok] = plan[idx[ok]][:, [cols.index(k) for k in ("plan_stop", "plan_source", "allow_brake")]].T
  return out


def aged(mask, t):
  """Elapsed observed time in this uninterrupted run. No segment carry, missing-frame holds or future samples."""
  age = np.zeros(len(t))
  for i in np.flatnonzero(mask):
    if i and mask[i-1] and 0 < t[i]-t[i-1] <= .031:
      age[i] = age[i-1]+t[i]-t[i-1]
  return age


def candidate(d, ok, stop, source, allow, set_mps, stable_set):
  v, a, req, brake = (d[k] for k in ("v", "a", "request", "wire_brake"))
  hud_off = (d["wire_pcm_gas"] == 0) & (d["wire_pcm_speed"] == 0)
  near_lead = valid(d, "radarState", .15) & (d["radar_lead"] == 1) & (d["radar_lead_dist"] > 0) & (d["radar_lead_dist"] <= 10)
  stopping = ok & (stop == 1) & (allow == 1) & (d["long_state"] == 2) & near_lead
  # Hypothesis 1: suppress an opposing *propulsion request* while stopped/re-engaging.
  # Record the contradicting fields; do not guess a stationary brake/pressure setpoint.
  inhibit = stopping & (v < 1.) & (req <= 0) & ((d["wire_pcm_speed"] > 0) | (d["wire_pcm_gas"] > 0))
  # Upper envelope if the STOPPING rise cap were doubled and pre-limit demand allowed
  # it. Require observed build at roughly the original 5.376 counts/s over 0.6 s.
  # Cannot observe uncapped demand; lower bound is always the recorded command.
  track = stopping & (d["standstill"] == 0) & (v > 0) & (v <= 1.5) & (a-req > .25) & (req < 0) & (brake > 0) & hud_off
  building = (aged(track, d["t"]) >= .599) & (brake-np.roll(brake, 30) >= 2) & (brake-np.roll(brake, 30) <= 5)
  build_extra = np.minimum(8, np.floor(5.376 * aged(building, d["t"])))
  # Diagnostic masks for independently owned bench work, NOT alternative commands.
  # A positive speed target BELOW ego is not the same as positive gas authority.
  dead = (ok & valid(d, "can_0_487", .06) & (allow == 1) & (d["long_state"] == 1) & (v > 5) & (req < -.15) & (a-req > .25)
          & (brake == 0) & (d["wire_pump"] == 0) & (d["hyd_pressure1_raw"] <= 106) & (d["hyd_pressure2_raw"] <= 107))
  strict = aged(dead & hud_off, d["t"]) >= .5
  no_positive_lead = aged(dead & (d["wire_pcm_gas"] == 0) & (d["wire_pcm_speed"] <= v), d["t"]) >= .5
  # Independent near-set probe: cap only the positive PCM speed target at the driver
  # setpoint when observed acceleration would close the remaining deficit in one second.
  # Gas allowance, planner, friction and measured torque are NEVER modified.
  deficit = set_mps-v
  near = (ok & stable_set & (source == 0) & (d["long_state"] == 1) & (d["vision_active"] == 0) & (d["map_active"] == 0)
          & valid(d, "longitudinalPlanSP", .16) & (v > 5) & (brake == 0) & (req > 0) & (a > .1)
          & (deficit >= 0) & (deficit <= 2*MPH) & (deficit <= a * 1.0))
  trim = np.where(near, np.maximum(0., d["wire_pcm_speed"]-set_mps), 0.)
  return inhibit, build_extra, strict, no_positive_lead, trim


def historical_slice(t, mask, req, actual, pitch):
  """Restricted negative rolling PID branch of rejected d5485d618. No lift/launch/stopping.

  Cold-start at each authorized slice, 50 Hz approximation to 100 Hz brake hysteresis.
  Base = grade-compensated /4.8, NO wind or learned gain. Compare only observed zero-brake
  slices (zero seed); prolonged frozen error overstates closed-loop integral build.
  """
  counts = np.full(len(t), np.nan)
  integral = previous = steady = base = 0.
  braking = False
  last = -2
  for i in np.flatnonzero(mask):
    if i != last+1 or not 0 < t[i]-t[last] < .031:
      integral = previous = steady = base = 0.
      braking = False
    raw = min(1., max(0., -(req[i]+9.81*math.sin(pitch[i]))/4.8))
    braking = raw >= (.005 if braking else .02)
    steady = min(max(steady, raw-.01), raw+.01) if braking else 0.
    base = min(steady, base+.06)
    error = actual[i]-req[i]
    error = math.copysign(max(0., abs(error)-.03), error)
    maximum = 255/256
    integral = min(max(integral, -base), maximum-base)
    p = .15*error
    proposed = min(max(integral+.20*error*DT, -base), maximum-base)
    trial = base+p+proposed
    if error > 0 and (previous >= maximum or trial > maximum):
      if integral < 0:
        integral = min(proposed, 0.)
    elif error < 0 and trial < 0:
      if integral > 0:
        integral = max(proposed, 0.)
    else:
      integral = proposed
    previous = min(max(base+p+integral, 0.), maximum, max(base, previous)+.5*DT)
    counts[i] = int(256*previous)
    last = i
  return counts


def context(d, mask):
  """Fixed joint cells: 2 m/s speed, 1 degree pitch, 10 m range, 2 m/s relative speed."""
  for row in zip(*(np.floor(d[k][mask]/width).astype(int) for k, width in
                   (("v", 2), ("pitch_deg", 1), ("radar_lead_dist", 10), ("radar_lead_vrel", 2))), strict=True):
    yield tuple(row)


def good_car(d):
  return (valid(d, "carState", .04) & (d["can_valid"] == 1) & (d["acc_fault"] == 0) & (d["stock_aeb"] == 0)
          & (d["pedal_brake"] == 0) & (d["pedal_gas"] == 0))


def good_context(d):
  return (valid(d, "radarState", .15) & (d["radar_lead"] == 1) & (d["radar_lead_dist"] > 0)
          & np.isfinite(d["pitch_deg"]) & np.isfinite(d["radar_lead_vrel"]) & np.isfinite(d["v"]) & valid(d, "carControl", .05))


def load_aligned(path, keys):
  with np.load(path, allow_pickle=False) as z:
    n = len(z["t"])
    return {k: z[k] if k in z else np.full(n, np.nan) for k in keys}


BASE_KEYS = """mono t carState_valid carState_age can_valid acc_fault stock_aeb pedal_brake pedal_gas v a pitch_deg
               carControl_valid carControl_age radarState_valid radarState_age radar_lead radar_lead_dist radar_lead_v radar_lead_vrel
               cruise can_128_506_valid can_128_506_age wire_brake can_0_487_valid can_0_487_age hyd_pressure1_raw hyd_pressure2_raw""".split()
OP_KEYS = BASE_KEYS + """active enabled controls_allowed controls_long rx_checks_invalid sp_pcm_enabled sp_ref_mono carControlSP_valid carControlSP_age
                         plan_mono controlsState_age controlsState_valid request long_state standstill wire_pcm_speed wire_pcm_gas wire_pump pitch
                         can_128_780_valid can_128_780_age wire_cancel wire_override vision_active map_active
                         longitudinalPlanSP_age longitudinalPlanSP_valid""".split()


def approach_set(path, d):
  with np.load(path, allow_pickle=False) as z:
    rows = z["set_kph"]
  t = d["mono"]
  idx = np.searchsorted(rows[:, 0], t, side="right")-1
  values = rows[idx, 1]/3.6
  fresh = ((idx >= 0) & (values > 0) & (values < 56) & (abs(t-rows[idx, 0]-d["carState_age"]) < 1.e-6))
  same = np.r_[False, np.all(rows[idx[1:], 1:3] == rows[idx[:-1], 1:3], axis=1)]
  return values, fresh & same


def op_segment(stem, meta, sidecar, approaches, totals, windows, cells, approach_rows, hud):
  d = load_aligned(stem.with_suffix(".aligned.npz"), OP_KEYS)
  t, mono = d["t"], d["mono"]
  with np.load(stem.with_suffix(".raw.npz"), allow_pickle=False) as raw:
    stop, source, allow = consumed(raw, meta["fields"], mono, d["plan_mono"])
    ok = good_car(d) & stable_tx(raw, meta["fields"], mono)
    if hud is not None:
      hud_veto(raw, meta, hud)
  for key, age in (("carControl", .05), ("controlsState", .05), ("carControlSP", .05), ("can_128_506", .06), ("can_128_780", .16)):
    ok &= valid(d, key, age)
  ok &= ((d["active"] == 1) & (d["enabled"] == 1) & (d["controls_allowed"] == 1) & (d["controls_long"] == 1) & (d["rx_checks_invalid"] == 0)
         & (d["sp_pcm_enabled"] == 1) & (mono >= d["sp_ref_mono"]) & (mono-d["sp_ref_mono"] <= .25) & (d["wire_override"] == 1)
         & (d["wire_cancel"] == 0) & np.isfinite(stop) & np.isfinite(d["request"]) & np.isfinite(d["a"]))
  set_mps, unchanged = approach_set(sidecar, d) if sidecar else (np.full(len(t), np.nan), np.zeros(len(t), bool))
  stable_set = aged(ok & unchanged, t) >= 3
  inhibit, build, strict, no_lead, trim = candidate(d, ok, stop, source, allow, set_mps, stable_set)
  brake = d["wire_brake"]
  pressure_ok = valid(d, "can_0_487", .06)
  pid = ok & (d["long_state"] == 1) & (d["v"] > 5) & (d["request"] < 0) & (brake == 0) & np.isfinite(d["pitch"])
  old = historical_slice(t, pid, d["request"], d["a"], d["pitch"])
  tracking = pid & (d["request"] < -.15) & (abs(d["a"]-d["request"]) < .1)
  totals.update(samples=int(ok.sum()), inhibit=int(inhibit.sum()), build_upper=int((build > 0).sum()),
                strict_dead=int(strict.sum()), no_positive_speed_lead_dead=int(no_lead.sum()), trim=int((trim > 0).sum()),
                already_tracking=int(tracking.sum()), historical_positive_tracking=int((tracking & (old > 0)).sum()))
  for lo, hi, name in WINDOWS[meta["route"]]:
    take = ok & (t >= lo) & (t < hi)
    if not take.any():
      continue
    if name in windows:
      raise ValueError(f"reference window crosses a segment: {name}")
    found = np.flatnonzero(take)
    windows[name] = {"n": len(found), "first_last_brake": brake[found[[0,-1]]].tolist(), "zero": int((brake[take] == 0).sum()),
                     "request": q(d["request"][take]), "actual": q(d["a"][take]), "pressure": q(d["hyd_pressure1_raw"][take & pressure_ok]),
                     "inhibit": int(inhibit[take].sum()), "build_upper_frames": int((build[take] > 0).sum()), "build_upper_max": q(build[take], max),
                     "strict_dead": int(strict[take].sum()), "no_positive_speed_lead_dead": int(no_lead[take].sum()),
                     "old_slice_n": int(np.isfinite(old[take]).sum()), "old_slice_mean": q(old[take]), "old_slice_max": q(old[take], max)}
    if name == "closing lead":
      cells.update(context(d, take & good_context(d)))
  for item in approaches:
    take = ok & (t >= item["t"]-1.e-4) & (t <= item["end"]+1.e-4)
    approach_rows.append({"route": meta["route"], "segment": meta["segment"], "start": item["t"], "n": int(take.sum()),
                          "trim_frames": int((trim[take] > 0).sum()), "max_target_reduction_mps": q(trim[take], max),
                          "crossed": item["phases"].get("cross") is not None, "observed_peak_mph": item["phases"]["max_speed"]["error_mph"]})


def stock_screen(roots, cells):
  seen, per_route, contrasts = {}, {}, {}
  support, positive = Counter(), Counter()
  coarse = {cell[:2] for cell in cells}
  for root in roots:
    for p in sorted(root.glob("*/*.metadata.json")):
      code = p.parent.name[:8].lstrip("0")
      if code not in STOCK:
        continue
      m = json.loads(p.read_text())
      key = m["route"], m["segment"]
      if key in seen:
        if seen[key] != m["source_sha256"]:
          raise ValueError(f"source conflict {key}")
        continue
      seen[key] = m["source_sha256"]
      cp, sp = m["config"].get("carParams", {}), m["config"].get("carParamsSP", {})
      r = per_route.setdefault(code, Counter())
      r["segments"] += 1
      if (cp.get("carFingerprint") != "HONDA_CIVIC" or cp.get("openpilotLongitudinalControl") is not False
          or sp.get("enableGasInterceptor") is not False or not sp.get("flags", 0) & 16):
        r["config_excluded"] += 1
        continue
      d = load_aligned(p.with_suffix("").with_suffix(".aligned.npz"), BASE_KEYS+["can_2_506_valid", "can_2_506_age", "stock_brake"])
      active = good_car(d) & (d["cruise"] == 1) & valid(d, "can_2_506", .06)
      lead = valid(d, "radarState", .15) & (d["radar_lead"] == 1)
      close = active & lead & (d["v"] < 4) & (d["radar_lead_dist"] > 0) & (d["radar_lead_dist"] < 22) & (abs(d["radar_lead_v"]) < 1)
      r["active_frames"] += int(active.sum())
      r["close_half_second_runs"] += sum(e-s >= 25 for s, e in runs(close))
      matched = active & good_context(d)
      r["context_available"] += int(matched.sum())
      for cell, cmd in zip(context(d, matched), d["stock_brake"][matched], strict=True):
        if cell[:2] in coarse:
          r["speed_pitch_lead_present"] += 1
          r["speed_pitch_lead_present_positive"] += int(cmd > 0)
        if cell in cells:
          support[cell] += 1
          positive[cell] += int(cmd > 0)
          r["same_cell_frames"] += 1
      if code in ("147", "189"):
        lo, hi = (1156.38, 1161.62) if code == "147" else (1659.814, 1666.694)
        check = active & (d["t"] >= lo) & (d["t"] < hi) & valid(d, "can_128_506", .06)
        if check.any():
          contrasts[code] = {"n": int(check.sum()), "echo_mean": q(d["wire_brake"][check]), "stock_mean": q(d["stock_brake"][check]),
                             "pressure1_max": q(d["hyd_pressure1_raw"][check & valid(d, "can_0_487", .06)], max), "actual": q(d["a"][check])}
  if {k: v["segments"] for k, v in per_route.items()} != STOCK:
    raise ValueError("incomplete stock marker inventory")
  return {"routes": per_route, "unmatched_positive_controls": contrasts, "op_window_context_frames": sum(cells.values()), "op_frames_with_5s_stock_cell":
          sum(n for cell,n in cells.items() if support[cell] >= 250), "stock_frames_in_cells": sum(support.values()),
          "stock_positive_in_cells": sum(positive.values())}


def main(evening, roots):
  manifest = json.loads((evening/"manifest.json").read_text())
  primary = json.loads((evening/"near_setpoint_results.json").read_text())["routes"]
  windows, approaches, totals, cells = {}, [], {}, Counter()
  hud = {name: {"coverage": Counter(), "windows": {}, "changed_packets": []} for name in (C, D)}
  for name, size in ((C, 22), (D, 31), (B, 9)):
    dirs = [r/name for r in [evening/"segments", *roots] if (r/name).is_dir()]
    if len(dirs) != 1:
      raise ValueError(f"ambiguous/missing route directory: {name}")
    markers = sorted(dirs[0].glob("*.metadata.json"))
    if [int(p.name.split(".")[0]) for p in markers] != list(range(size)):
      raise ValueError(f"incomplete route {name}")
    stats = totals[name] = Counter()
    for p in markers:
      m = json.loads(p.read_text())
      if not civic_pcm(m["config"]) or m["route"] != name or m["segment"] != int(p.name.split(".")[0]):
        raise ValueError(f"not the target Civic configuration: {p}")
      stem = p.with_suffix("").with_suffix("")
      sidecar, items = None, []
      if name != B:
        if m["source_sha256"] != manifest[f"{name}--{m['segment']}/rlog.zst"] or m["init"]["gitCommit"] != EVENING_BUILD:
          raise ValueError(f"source/build mismatch: {p}")
        sidecar = evening/"powertrain"/name/(stem.name+".npz")
        items = [i for i in primary[name]["approaches"] if i["seg"] == m["segment"]]
      elif not m["init"]["gitCommit"].startswith("a4b41ccac6"):
        raise ValueError(f"unexpected rollback build: {p}")
      op_segment(stem, m, sidecar, items, stats, windows, cells, approaches, hud.get(name))
  return {"hud": hud, "route_totals": totals, "windows": windows, "approaches": approaches, "stock": stock_screen(roots, cells)}


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("evening", type=Path)
  parser.add_argument("older_segments", nargs="+", type=Path)
  args = parser.parse_args()
  print(json.dumps(main(args.evening, args.older_segments), indent=2, allow_nan=False))
