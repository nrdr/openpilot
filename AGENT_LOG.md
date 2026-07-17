# nrdr openpilot — Agent Log

**Shared memory for every agent working on this nrdr fork. Read before you start; update before you finish.**

---

## How to use this log

1. Read **Standing Decisions** — treat as constraints.
2. Skim the latest **Change Log** entries.
3. After work: prepend a Change Log entry (newest first) with a **Check** line; update Standing Decisions / `ARCHITECTURE.md` when flows or rules change.

**Precedence:** Standing Decisions > code comments > older change-log entries.

**Do not confuse** with stock `docs/contributing/architecture.md`. This log covers **nrdr lateral / steer-ratio / tune** systems.

---

## Authoritative references

- **`ARCHITECTURE.md`** — topology and flow maps for SR apply, gap-filler (planned), NRDR settings, TuneLearner.
- Plan: `~/.cursor/plans/steer_ratio_auto-tune_875a0b78.plan.md` (gap-filler Phases A–C).

---

## Standing Decisions (newest wins)

### Steer ratio
- **Apply priority (per |SWA|):** device promoted bins **blend with** fingerprint seed until `promoted_n ≥ 5×N_min`, then device; else nearest trusted → scalar. Thin new data cannot yank a graduated seed overnight.
- **Scalar Learn SR** (`NrdrLearnSteerRatio`) is separate from the curve Auto toggle. When scalar Learn is ON, it wins for `VM.sR`.
- **Clarity Min/Max** only apply on `HONDA_CLARITY`. **CR-V 5G** uses the measured multi-point seed table in `latcontrol_pid.py`.
- **Gap-filler (Phase B):** one Curve Auto toggle (`NrdrSteerRatioCurve`); guided **SR Calibrate**; Rate / Reset; device curve in `NrdrSteerRatioCurveData`. Default drive: hands-off + latActive + rate/speed gates.
- **Offline fit / graduation (Phase C):** `sr_curve_fit.py` + Learned Parameters **SCAN** / `NrdrRemoteSrCurveFit`. `--apply` merges by default. Human PR for `NRDR_STEER_RATIO_CURVES` only.

### SR data collection (author protocol — drives calibrate + offline fit)
Canonical way to fill bins (from `sr_extract` / steerratio author). **SR Calibrate UI copy and Phase B gates must match this:**

1. **Hold a constant wheel angle** — set it, do 2–3 smooth laps, then change radius. Frames where the wheel is *moving* are discarded → need a **steering-rate gate** (hold still). Continuous winding is worse than “hold, lap, adjust.”
2. **Stay above ~7 mph** the whole time (slower frames discarded). ~10 mph on wider circles is ideal. Phase B: `MIN_V ≈ 7 mph` (not 3 m/s crawl).
3. **Cover 3–4 radii:** wide → medium → tight → a couple laps at/near **full lock** (matches calibrate-complete = to lock).
4. **Both directions** (CW and CCW). Bins remain `|SWA|` (shared L/R), but both directions cancel mount/offset bias and improve stats — **coach both in Calibrate UI**; optional soft “seen both signs” for complete later.

Daily Auto gap-fill can still use opportunistic hands-off turns; Calibrate is for intentional lot/circle bootstrap.

**Why these gates exist (measurement physics):**  
`SR = |δ_sw| / |atan(L · yaw / v)|`. That only equals the rack ratio in **quasi-steady** turning. Moving wheel → yaw lags SWA (plant delay / slip buildup) → junk SR. Slow `v` → `yaw/v` noise blows up. One radius → one `|δ|` bin only; VGR needs many angles to lock. One direction → mount/offset bias can skew absolute SR; CW+CCW averages odd errors. Same math for Calibrate, Auto gap-fill, and offline fit — Calibrate is just the mode that makes following the protocol easy.

### Guided SR Calibrate (locked UX)
Manual calibrate is a **step-through wizard**, not a vague “drive circles until done”:

1. **Targets = incomplete bin centers** from the shared `|SWA|` grid (e.g. 0 / 50 / 100 / 150 / 175 / 200… up to near lock / `CP` max). Skip bins already at `N_min`.
2. **One active target:** UI shows e.g. `Hold ~100°  (±15°)` + live `|SWA|` with in-band / hold-still / speed status (green when accumulating).
3. **Dwell → credit:** samples only while in band + rate gate + ≥7 mph; when that bin hits `N_min` (and optional std), advance to next incomplete.
4. **Direction coaching:** after a bin fills (or at start of each target), prompt **left then right** (or CW then CCW) for bias; bins stay `|SWA|` shared — both signs feed the same bin.
5. **Progress:** `Step 3/6 · 100° · n=42/80 · bins to lock 4/6`; milestone at mid-angle optional.
6. **Complete:** consecutive bins through near-lock meet `N_min` → auto-off + promote. Partial exit still promotes what was filled.
7. **Safety:** timeout / ignition / manual off; never leave calibrate stuck.

Auto gap-fill stays unguided opportunistic; only Calibrate is the guided path.

### SR curve evolution / stickiness (locked)
Thin new data must **not** yank a well-proven curve (fingerprint seed from large pool X, or a device bin with huge cumulative `n`).

1. **Bin stats are the long-term pool** — accumulate forever in `NrdrSteerRatioCurveData` until explicit Reset (never drop old samples when promoting).
2. **Promote only on milestones** — need `_promote_delta` new samples since last promote (not every frame).
3. **Step-clamp** — each promote moves at most `MAX_PROMOTE_STEP * rate` toward the cumulative mean (Rate=0 freezes applied curve).
4. **Seed stickiness on apply** — device blends with fingerprint seed until `promoted_n ≥ N_min * 5`; mode `device_seed_blend` while earning trust.
5. **Offline `--apply` merges by default** — `--replace` required to wipe; refuse empty apply without `--force`.
6. **Hardcoded seeds** (`NRDR_STEER_RATIO_CURVES`) are the durable “large pool X” after human graduation — devices refine, they don’t silently erase that prior.

### Effective tune visibility (Phase A)
- **Car & Tune Info VIEW** and Learned Parameters show **currently applied** values via Params snapshot `NrdrAppliedTuneSnapshot` (JSON) — not a live cereal stream.
- Snapshot includes applied SR + mode, banded P/I/F scales, TuneLearner trim applied / map cell.

### UI placement
- Curve knobs (when added) → **Learned Parameters**.
- Min/Max → **PID/F Tuning Ground** (Clarity-only copy).
- Effective stack → **Car & Tune Info VIEW**.

### Verification
- `py_compile` touched Python; Bugbot on non-trivial control changes when skills require it.

---

## Change Log

### 2026-07-17 — Device Fit-from-logs SCAN + remoted
- **What:** Learned Parameters SCAN/VIEW for `sr_curve_fit.py fit --apply`; `NrdrRemoteSrCurveFit` + summary in remoted/params/yaml.
- **Why:** Phase C usable on-device without SSH; website can trigger the same merge fit.
- **Check:** Offroad → Learned Parameters → SCAN; result modal + `/data/nrdr_sr_curve_fit.txt`. Remote toggle clears when remoted finishes.

### 2026-07-17 — SR curve stickiness (thin-data protection)
- **What:** Promote only on sample milestones + step-clamp; `promotedN` trust weight; apply blends device↔seed until n≥5×Nmin (`device_seed_blend`); offline `--apply` merges by default (`--replace` to wipe).
- **Why:** User concern — small new drives must not dramatically yank bins built from a large historical pool / graduated seed.
- **Check:** With CR-V seed + fresh device bin at n=Nmin, applied mode is `device_seed_blend` near seed. After n reaches ~5×Nmin, mode becomes `device_curve`. Rate 0 freezes promoted while bins still accumulate.

### 2026-07-17 — Phase C: sr_curve_fit + export graduation
- **What:** Added `sr_curve_fit.py` (view/fit/export into `NrdrSteerRatioCurveData` + paste-ready seed snippets). Aligned `steerratio_by_angle.py` to ≥7 mph + rate gate. steering.yaml + Learned Parameters CLI hint for fit/export.
- **Why:** Offline backfill and human-reviewed seed graduation (Phase C).
- **Check:** `python3 sr_curve_fit.py fit <rlogs>` prints promoted table; `--apply` writes CurveData (refuses empty without `--force`); `--export --fingerprint HONDA_CRV_5G` prints snippet. Fit uses calibrated yaw (liveCalibration) to match on-road learner.

### 2026-07-17 — Phase B: SR curve gap-filler + guided Calibrate
- **What:** Added `nrdr_steer_ratio_curve.py` (sample→bin→promote→apply merge). Params: Curve Auto / Rate / Calibrate / Reset / CurveData. LatControlPID wires apply + live update + snapshot guide fields. Learned Parameters UI + Car & Tune Info VIEW show curve/calibrate progress.
- **Why:** Continue Phase B — live gap-fill and guided lot calibration through lock.
- **Check:** With Learn SR OFF + Curve Auto ON, applied mode is seed/device/nearest as expected. Enable SR Calibrate in a lot ≥7 mph — guide shows Hold ~25° L then R through bins; Completes or clears on ignition. `py_compile`/AST + unit apply/promote checks passed.

### 2026-07-17 — Why SR collection gates exist + improve path
- **What:** Documented physics behind hold-still / ≥7 mph / multi-radius / both-directions; Phase B improvement ideas (rate gate, dwell, dual-mode N_min, CW+CCW progress).
- **Why:** User asked whether author params apply and how to improve.
- **Check:** Phase B should not treat author notes as optional folklore — they are the validity conditions for the SR estimator.

### 2026-07-17 — Guided Calibrate UX locked
- **What:** SR Calibrate = step-through wizard: next incomplete bin target angle, live in-band/hold/speed feedback, L then R coaching, advance on N_min, complete to lock.
- **Why:** User asked for guided hold-angle prompts through completion (not freeform circles only).
- **Check:** Phase B UI must implement target angle + status, not only a progress fraction.

### 2026-07-17 — Phase A start: agent docs + applied-tune snapshot plumbing
- **What:** Added `AGENT_LOG.md` / `ARCHITECTURE.md`. LatControlPID writes `NrdrAppliedTuneSnapshot`. Car & Tune Info + Learned Parameters show applied SR / scales / TuneLearner trim. Stale Learn SR / Min-Max copy clarified.
- **Why:** Users were blind to effective tune vs static knobs; prep for gap-filler.
- **Check:** On device after engage, open Car & Tune Info VIEW and Learned Parameters — applied SR/mode and scales should match last drive state. `NrdrAppliedTuneSnapshot` param should exist after ~3s onroad.

---

## Open / Recent Issues

_(none tracked yet)_
