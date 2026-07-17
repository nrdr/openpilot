# nrdr openpilot — Architecture & Flow Maps

Paired with `AGENT_LOG.md`. Update matching maps when flows change.

---

## 1. Lateral steer-ratio apply path (today + Phase A)

```mermaid
flowchart TD
  controlsd[controlsd sets VM from learn toggle]
  controlsd --> vmScalar["VM.sR scalar: paramsd or CP.steerRatio"]
  lac[LatControlPID.update]
  vmScalar --> lac
  lac --> clear["VM.sr_curve = None"]
  clear --> gate{Learn SR off?}
  gate -->|no| keepScalar[keep controlsd scalar]
  gate -->|yes| fp{fingerprint}
  fp -->|HONDA_CRV_5G| seed[interp NRDR_STEER_RATIO_CURVES]
  fp -->|HONDA_CLARITY| twopt[interp Min/Max twopoint]
  fp -->|other| keepScalar
  seed --> des[get_steer_from_curvature]
  twopt --> des
  keepScalar --> des
  lac --> snap[NrdrAppliedTuneSnapshot Params]
  snap --> ui[Car and Tune Info / Learned Parameters]
```

**Key files:** `selfdrive/controls/controlsd.py`, `sunnypilot/selfdrive/controls/controlsd_ext.py`, `selfdrive/controls/lib/latcontrol_pid.py`, `opendbc_repo/opendbc/car/vehicle_model.py`.

---

## 2. NRDR settings tree

```text
NRDR
├── Learned Parameters     # scalar Auto toggles + applied SR readout (Phase A)
├── Lateral Tuning
│   ├── Car & Tune Info    # VIEW: static CP + currently applied stack
│   ├── PID/F Tuning Ground  # Min/Max (Clarity), banded scales, 2D Auto-Tuner
│   ├── Unwind / Override / Filters / Ford
├── Longitudinal Tuning
└── Special
```

---

## 3. TuneLearner (2D Auto-Tuner)

```mermaid
flowchart LR
  map[NrdrTuneLearnerMap L/R grids]
  err[angle error]
  map --> apply[error-gated trim]
  err --> apply
  apply --> torque[output_torque += trim]
  learn[accumulate when hands-off quasi-steady]
  err --> learn
  learn --> map
```

Only runs on **EPS-modified** Hondas inside `LatControlPID`. UI knobs: Enable / Strength / Rate / Reset. Phase A surfaces **applied trim** + map cell in VIEW.

**Key file:** `selfdrive/controls/lib/nrdr_tune_learner.py`.

---

## 4. Gap-filler (Phase B)

```mermaid
flowchart TD
  sample[yaw / SWA / v gated sample] --> accum[Per-bin stats]
  accum --> promote[Promote when n/std OK]
  promote --> data[NrdrSteerRatioCurveData]
  data --> apply
  seed[Fingerprint seed / Clarity twopoint] --> apply
  apply["blend device↔seed until trust → nearest → scalar"] --> VM[VM.sR]
  calib[SR Calibrate guided] --> sample
  auto[Curve Auto gap-fill hands-off] --> sample
```

**Key file:** `selfdrive/controls/lib/nrdr_steer_ratio_curve.py` (wired from `latcontrol_pid.py`).

**SR Calibrate:** guided step-through — UI names next incomplete `|SWA|` bin target (“Hold ~100° L/R”), live in-band / hold-still / speed feedback, advance on `N_min`; complete = lock coverage then normal hands-off gap-fill.

**Calibrate driving protocol (author):** hold constant SWA for 2–3 laps per radius → adjust → repeat wide/medium/tight/near-lock; ≥7 mph (~10 mph wide); both CW and CCW. Gates: discard moving-wheel frames (`|steeringRate|` high) and slow frames. Bins still `|SWA|`; both directions recommended for bias/stats.

**Stickiness:** bin stats accumulate forever (until Reset). Promote only on sample milestones with step-clamp. Apply blends device with fingerprint seed until `promoted_n ≥ 5×N_min`.

**UI:** Learned Parameters — Curve Auto / Rate / Calibrate / Reset + **Fit from Logs SCAN/VIEW** + live guide line.

---

## 5. Seed graduation (Phase C)

```mermaid
flowchart LR
  logs[rlogs] --> fit[sr_curve_fit.py fit]
  fit --> data[NrdrSteerRatioCurveData]
  data --> export[sr_curve_fit.py export]
  export --> pr["PR into NRDR_STEER_RATIO_CURVES"]
  live[Live gap-filler / Calibrate] --> data
```

**CLI:** `sr_curve_fit.py` — `view` / `fit [--apply] [--replace] [--calibrate] [--force]` / `export [--fingerprint]`. Same gates as live learner; yaw from **calibrated** pose. `--apply` **merges** into existing pool by default; `--replace` wipes. Refuses empty apply without `--force`. Human-reviewed paste into `NRDR_STEER_RATIO_CURVES`.

**Read-only diagnostic:** `steerratio_by_angle.py` (aligned ≥7 mph + rate gate; points at fit tool for writes).
