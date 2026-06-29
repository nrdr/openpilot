#!/usr/bin/env python3
"""
tune_trace.py - frame-by-frame trace of low-speed tight-turn events.

Companion to tune_report.py. The report tells you WHERE the tune is off (it found
your low-speed turns oscillating); this dumps the actual time series of the worst
low-speed turn events - desired vs actual steering angle, the error, and the
P / I / F / output breakdown - so you can SEE the limit cycle and which term drives it.

Gate (same spirit as tune_report): lateral active, hands off the wheel. Saturated
frames are kept here on purpose - the catch-up-and-overshoot is what we want to see.

Usage:
  python3 tune_trace.py <rlog> [<rlog> ...]
  python3 tune_trace.py /data/media/0/realdata/*/rlog.zst | tee /data/nrdr_tune_trace.txt

Read-only. Touches nothing on the device, changes no params.
"""
import sys
import math

from openpilot.tools.lib.logreader import LogReader

MS_TO_MPH = 2.23694
MAX_MPH = 25           # the controller's whole low-speed band (< 25 mph). captures
                       # roundabouts + tight turns; matches _LAT_SCALE_LOW_MAX exactly.
MIN_ABS_DES = 6.0      # deg (wheel): a real turn, not straight-line micro-corrections
GAP_S = 0.4            # a gap longer than this ends an event
MIN_EVENT_S = 0.4      # ignore events shorter than this
TOP_EVENTS = 4         # print this many worst events
MAX_ROWS = 45          # cap rows printed per event (downsample if longer)


def collect(paths):
  samples = []  # (t_s, mph, des, act, err, p, i, f, out, sat)
  v_ego = 0.0
  steering_pressed = False
  lat_active = False
  for path in paths:
    try:
      lr = LogReader(path)
    except Exception as e:
      print(f"!! could not open {path}: {e}", file=sys.stderr)
      continue
    for msg in lr:
      w = msg.which()
      if w == "carState":
        v_ego = msg.carState.vEgo
        steering_pressed = msg.carState.steeringPressed
      elif w == "carControl":
        lat_active = msg.carControl.latActive
      elif w == "controlsState":
        lcs = msg.controlsState.lateralControlState
        if lcs.which() != "pidState":
          continue
        pid = lcs.pidState
        if not pid.active or not lat_active or steering_pressed:
          continue
        samples.append((
          msg.logMonoTime / 1e9,
          v_ego * MS_TO_MPH,
          float(pid.steeringAngleDesiredDeg),
          float(pid.steeringAngleDeg),
          float(pid.steeringAngleDesiredDeg) - float(pid.steeringAngleDeg),
          float(pid.p), float(pid.i), float(pid.f), float(pid.output), bool(pid.saturated),
          float(pid.steeringRateDeg),
        ))
  # NOTE: don't globally sort - logMonoTime resets each boot, so read order (per file,
  # in glob order) is the correct ordering; event splitting handles the per-boot resets.
  return samples


def find_events(samples):
  qual = [s for s in samples if s[1] <= MAX_MPH and abs(s[2]) >= MIN_ABS_DES]
  events, cur = [], []
  for s in qual:
    # split on a forward gap > GAP_S OR a backward jump (new boot / new route file)
    if cur and not (0.0 <= s[0] - cur[-1][0] <= GAP_S):
      events.append(cur)
      cur = []
    cur.append(s)
  if cur:
    events.append(cur)
  return [e for e in events if e[-1][0] - e[0][0] >= MIN_EVENT_S and len(e) >= 10]


def event_stats(ev):
  errs = [s[4] for s in ev]
  n = len(errs)
  mean = sum(errs) / n
  rms = math.sqrt(max(sum(e * e for e in errs) / n - mean * mean, 0.0))
  flips, prev = 0, 0
  for e in errs:
    s = 1 if e > 0 else (-1 if e < 0 else 0)
    if s and prev and s != prev:
      flips += 1
    if s:
      prev = s
  dur = ev[-1][0] - ev[0][0]
  freq = (flips / 2.0) / dur if dur > 0 else 0.0
  peak = max(abs(e) for e in errs)
  return mean, rms, peak, freq, dur


def main(paths):
  samples = collect(paths)
  print(f"\nCollected {len(samples)} active hands-off pid frames.")
  events = find_events(samples)
  print(f"Found {len(events)} low-speed (<= {MAX_MPH:.0f} mph) turn events (|desired| >= {MIN_ABS_DES:.0f} deg).\n")
  if not events:
    print("No qualifying low-speed turn events found. The logs need slow tight turns")
    print("(roundabouts / slow corners) driven hands-off with lateral engaged.")
    return

  ranked = sorted(events, key=lambda e: event_stats(e)[1], reverse=True)
  for idx, ev in enumerate(ranked[:TOP_EVENTS], 1):
    mean, rms, peak, freq, dur = event_stats(ev)
    mph_lo = min(s[1] for s in ev)
    mph_hi = max(s[1] for s in ev)
    side = "left" if sum(s[2] for s in ev) > 0 else "right"
    print("=" * 96)
    print(f"EVENT {idx}: {side} turn, {mph_lo:.0f}-{mph_hi:.0f} mph, {dur:.1f}s | "
          f"err mean {mean:+.1f}  rms {rms:.1f}  peak {peak:.0f} deg | error swings ~{freq:.1f} Hz")
    print("=" * 96)
    print(f"{'t(s)':>6} {'mph':>4} {'desired':>8} {'actual':>8} {'rate':>7} {'error':>7} "
          f"{'P':>7} {'I':>7} {'F':>7} {'out':>7} sat")
    step = max(1, len(ev) // MAX_ROWS)
    t0 = ev[0][0]
    for s in ev[::step]:
      t, mph, des, act, err, p, i, f, out, sat, rate = s
      print(f"{t - t0:>6.2f} {mph:>4.0f} {des:>8.1f} {act:>8.1f} {rate:>7.0f} {err:>7.1f} "
            f"{p:>7.3f} {i:>7.3f} {f:>7.3f} {out:>7.3f} {'S' if sat else ''}")
    print()

  print("Reading guide:")
  print("  desired vs actual : the gap is the tracking error - watch 'actual' chase 'desired'.")
  print("  error crossing zero with big swings = limit-cycle oscillation (loop gain/lag, not authority).")
  print("  which term dominates 'out' tells us what drives the swing:")
  print("    F leads the overshoot  -> feedforward too hot at low speed / high angle.")
  print("    P big and flips sign with the error -> proportional/lag-driven oscillation.")
  print("    I keeps growing one way -> integrator wind-up overshoot.")
  print("  'out' hitting ~+/-1.0 (sat=S) in bursts = slamming to catch up, then overshooting.")
  print("  rate = steering-wheel deg/s, the signal a derivative/rate-damping term feeds on.")
  print("    smooth rate = clean enough to damp; jagged/quantized rate would limit a D term.")


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(1)
  main(sys.argv[1:])
