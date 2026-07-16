# nrdr Cascade Lateral Control — Design Spec (pre-implementation)

**Goal:** PID lateral where the precise angle sensor does the driving and the IMU audits the
geometry — so no steer ratio value (curve, scalar, spec sheet, learned) can bias steady-state
tracking for more than a few seconds. Answers the owner's ask: "latcontrol_pid that functions
like latcontrol_angle, bypassing reliance on steerRatio."

**Status:** IMPLEMENTED, SHIPS DORMANT (NrdrCurvatureTrim default OFF). Unit suite green (7/7: convergence, measured-noise jitter, clamp, watchdog disarm, all freeze gates, leak, sign symmetry). ROAD USE STILL GATED on the offline log replay below. Constants below are derived from
~7.7 h of HONDA_CLARITY log data (analysis/cache.pkl), 2026-07-15.

---

## Architecture

```
desired_curvature (model)
        │
        ▼
  θ_ff = VM.get_steer_from_curvature(κ_des)      ← SR map = FIRST GUESS only (v2 curve)
        │
        + θ_trim  ◄─── OUTER LOOP (new): slow integrator on (κ_des − yaw/v)
        │               true curvature error from IMU — no steer ratio anywhere in it
        ▼
  angle setpoint ──► INNER LOOP (existing latcontrol_pid): PID on (θ_des − θ_meas) → torque
```

- Inner loop: unchanged. It is already an angle servo closed on the 100Hz high-resolution sensor.
- Outer loop: `θ_trim += Kc · (κ_des − κ_meas) · dt − θ_trim · dt/T_leak`, output in degrees,
  added to the setpoint before FF computation (FF sees the corrected angle).
- κ_meas = roll-compensated yaw_rate / v (livePose z, same convention as sr_fit).

## Constants (data-derived)

| Parameter | Value | Basis |
|---|---|---|
| Trim time constant T | 2.5 s (≈ Kc·SR·L scaling) | κ-noise: 1.9–5.0e-4 1/m std (speed-dependent). T=2–3 s ⇒ setpoint jitter 0.12–0.15° 1σ ≈ sensor resolution. T<1 s ⇒ >0.2° jitter (felt). |
| Optional speed schedule | T = 2 s @ >25 m/s, 4 s @ <10 m/s | noise std doubles at low speed |
| Trim clamp | ±2.5° | v1-map error worst case ≈ 2° equivalent; spec-scalar errors similar scale |
| Leak T_leak | 30 s | trim decays when error signal is gated off; prevents stale bias |
| Enable gate | v > 4.5 m/s (10 mph) | κ = yaw/v degenerates at low speed (noise ×2.7 below 10 m/s) |

## Freeze / reset conditions (trim held, not integrated)

- steeringPressed (driver override) — freeze; resume on release
- not latActive — freeze + leak
- v below gate — freeze + leak
- |θ_rate| > 25 °/s (aggressive transient) — freeze (don't learn geometry mid-slew)
- livePose invalid / posenet bad — freeze
- lane change in progress (laneChangeState != off) — freeze (κ_des intentionally ≠ path)

## Anti-windup

Integrate only when the inner loop is not torque-saturated (pid_log.saturated false);
clamp-and-back-calculate otherwise. Trim is pre-FF, so FF cannot fight it.

## Interactions

- **Model outer loop (vision):** corrects lateral *position* on ~1 s+ horizon; trim corrects
  curvature *tracking*. Stack benignly iff trim is slow (T ≥ 2 s) and bounded. Watch for
  breathing on long constant curves during tuning.
- **Tune learner:** its steady-state angle-error correction is subsumed by a superior signal
  (angle error is blind to rack-model error; κ error is not). SHIP RULE: when
  `NrdrCurvatureTrim` is enabled, tune-learner apply() is disabled (map retained, frozen).
  Revisit whether the learner survives at all after road data.
- **SR map (v2 curve / scalar):** determines transient quality only (how far trim travels).
  Keep v2. Curve debates become tuning nuance, not correctness.
- **Column twist:** lives between sensor and rack; the outer loop sees its effect on true yaw
  and trims through it. This is where twist is handled — never in the geometry map (v1 lesson).

## Rollout plan

0. **Extractor v2:** add `controlsState.desiredCurvature` + `steeringAngleDesiredDeg` +
   `saturated` columns; owner reruns on device (resumable, reprocesses with new columns —
   delete /data/media/0/sr_extract first or use a new out dir).
1. **Offline replay gate:** feed logged κ_des / yaw / v through the trim law; verify on real
   routes: |trim| bounded, convergence < 5 s after map-error steps, zero oscillation,
   jitter ≤ 0.15° on straights. No road testing until this passes.
2. **Ship dormant:** `NrdrCurvatureTrim` param, default OFF. UI toggle under Lateral Tuning
   with trim value displayed live (devUI) for the first drives.
3. **Road:** owner enables, city + highway loop, hands ready. Success = corners hold line with
   ZERO retune when swapping SR map between v2 curve and flat 16.0 (the whole point).

## Non-goals (this feature)

- No torque-domain twist compensation (future; possibly folded into inner-loop FF)
- No changes to torque-mode latcontrol
- No paramsd changes (its scalar is already ignored on curve cars; freeze task #5 separate)
