# NRDR Clarity — Pre-Reset Tune Snapshot & Re-Tune Plan
*Captured 2026-06-25, immediately before factory reset.*

This is the handoff note for picking the lateral work back up after the reset + relearn.
Raw param dump: `/tmp/nrdr_tune_snapshot.txt` on the device (copy off before reboot) + your PC log archive.

---

## 1. The "before" tune (what produced the −417° roundabout runaway)

**Base PID (from the car, `NrdrCarTuneInfo`):** kp `0.03` · ki `0.01` · kf `1.2e-5`
Learned `steerRatio ≈ 17.3` (Clarity nominal 16.5 → **+5%, normal, not a factor**).

| Band | P | I | F |
|---|---|---|---|
| Low (<25 mph) | **60%** | **60%** | **20%** |
| Standard (25–50) | 80% | 80% | 30% |
| Highway (50+) | 100% | 100% | 50% |

- **LPF tau:** 0.05 / 0.07 / 0.10 · **Notch:** 6.9 Hz, Q 1.5
- **Unwind:** boost duration **3.0 s** · ff multiplier **4.0×** · lookahead on · freeze off
- **Center boost:** 0.5 @ 3°, min-speed 50 mph
- **Override:** threshold 2400 · center-boost 1200 · pass-through assist on
- **Learned params:** steer ratio / stiffness / angle offset all **on**
- **Min steer speed:** 0 (steers below the Clarity's stock 12 mph floor)

---

## 2. Diagnosis (settled — confirmed in `tune_trace.py` event 1)

The Nidec EPS is **torque-commanded**, so the plant openpilot closes the loop around is *torque → angle* — a **double integrator**. Pure proportional feedback on a double integrator is an **undamped oscillator**.

At highway speed two things hide this: tire self-aligning torque (natural damping, rises with speed) and the feedforward (`kf·angle·v²`). **Below ~10 mph both go to zero**, and the integrator is frozen below 4.5 mph — so the wheel steers on **P alone**. Result: it rings. Raising P made it worse; lowering it (the 60%) made it softer but still rang. As the car ran wide, the model wound `desired` up to **±400°** (near lock) and P railed to saturation (−5.9 wanted, ±1.0 available).

**The missing ingredient is damping (D).** The tune had `kd = 0`. P / I / F are all gain knobs — none of them add damping, which is why no combination ever fixed it. *(Feedforward / unwind boost were red herrings: F is negligible at low speed because of the v² term.)*

---

## 3. What's now in the repo (built + verified, NOT yet flashed)

A real **rate-damping "D" term**, in **PID/F Tuning Ground** (device + Sunnylink), defaulted **off**:

- **Rate Damping (D) Strength** — 0–300%, default **0%**
- **Rate Damping Fade-Out Speed** — 0–60 mph, default **30**

Math (in `latcontrol_pid.py`, applied after the output scale, before the clamp):
```
output += −(strength × 0.010) × steeringRateDeg × speed_fade
speed_fade = clip((fade_speed − vEgo) / fade_speed, 0, 1)   # full at standstill, 0 by fade_speed
```
Files touched: `latcontrol_pid.py`, `nrdr_sub_layouts/pidf_ground.py`, `settings_ui_src/pages/steering.yaml` (settings_ui.json recompiled, 174→176 keys), `common/params_keys.h`.

---

## 4. Re-tune plan (after reset + `scons` + flash)

The reset wipes params to **defaults** — use that as a feature. **Do NOT restore the old 60/60/20 low band**; defaults give 100% low-band P, which is what you want now that D will damp it.

1. **Flash** the build (D term + latest UI).
2. **Re-apply the keepers** (good, unrelated to the bug): LPF tau 0.05 / 0.07 / 0.10 · Notch 6.9 Hz · Override 2400 / 1200 · Standard band 80/80/30 · Highway band 100/100/50 · learned params on.
3. **Leave Low band at default 100/100/100.** Set **Unwind back to default 2.0× / 1.0 s** (4×/3 s was overcooked and is downstream of the real bug).
4. **Add D:** Strength **30%**, Fade **30 mph**. Drive the worst roundabout.
5. **Iterate:**
   - still ringing → D **up** (50–80%) and/or fade **up** (→40 mph for the 13–18 mph turns)
   - turn-in feels heavy/laggy → D **down**
   - once stable → push **Low-band P toward / past 100%** for crisp tracking (PD lets you run the stiffer P without the ring)
6. **Re-run `tune_trace.py`.** Event-1 success = `desired` stays bounded (no ±400° runaway), `actual` tracks it, rms collapses from ~75°.

---

## 5. Backlog (unrelated, still open)
- Merge nrdr/openpilot PRs #4 & #5 (EPS tooling) — *done earlier; verify on the post-reset branch.*
- Honda Dashboard Variant A/B backend rounding (placeholder toggle wired; needs logs).
- "StarPilot PID Additions" toggle — gate the borrowed `_pid_output_scale` (Civic-Bosch constants, never tuned for Clarity) behind one switch; keep your unwind + lookahead/freeze and the new D term as core.
