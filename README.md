# Night Rider Linear EPS Fork (nrdr)

## Overview

This fork supports the Linear EPS firmware modification available for select Honda platforms.

Linearized EPS firmware alters the steering torque response characteristics. As a result, stock lateral tuning is not appropriate. This fork applies the required adjustments to support linear torque curves, along with additional refinements/QOL developed within the Honda Openpilot/Sunnypilot community.

---

## Recent Changes

- **Custom P/I/F Lateral Scaling** — Optional Low / Standard / Highway multipliers can scale Proportional, Integral, and Feedforward independently. Every multiplier defaults to a neutral 100%, leaving the static base tune unchanged.
- **Comma 4 (C4) support** — full C4 UI day-one: redesigned home screen (nrdr branding, live Device IP, "last updated" feed, NY-time stamp) and a fix for the personality toggle that was crash-looping the C4 on boot.
- **Ford OEM-Style Lateral** — optional four-signal Ford lateral control (curvature + curvature-rate + lane-centering path-angle) for the Expedition, with human-turn detection, lane positioning, and a lateral-accel ceiling. Behind a master toggle, default OFF — Honda is untouched.
- **Car & Tune Info** — on-device and Sunnylink readout of the detected car: fingerprint, EPS/camera firmware, gas interceptor, radar, and the live kp/ki/kf in use.
- **Cruise Mismatch Correction + ECU-Matched Longitudinal** — Honda Nidec longitudinal accuracy: corrects set-speed vs. actual mismatch and matches the factory ECU's gas/brake response.

---

## Branches

- **`nrdr-development`** — the main dev branch; all work lands here first (source, not pre-compiled).
- **`nrdr-staging-<DATE>`** — pre-compiled snapshots cut from `nrdr-development`. Dated so you can pin a known-good build.
- **`nrdr-nightly`** — always tracks the latest `nrdr-staging`. Run this if you just want the newest pre-compiled build.
- **`nrdr-clean`** — compliance build that follows all the rules needed for valid standing with comma and their servers.

> **Factory reset whenever you switch between a non-clean and a clean branch** — otherwise old logs can carry over and defeat the entire point of the clean branch. Also factory reset if you leave the nrdr fork family completely.

---

## Supported Platforms

- Honda Civic (Nidec)
- Honda Civic (Bosch)
- Honda Clarity (Nidec)
- Ford Expedition (OEM-style lateral, optional)

Additional EPS firmware variants may be supported as they are validated.

---

## Installation

```
installer.comma.ai/nrdr/mvl-staging-03.03.2026
```

---

## Recommended Device Configuration

- **Force Torque Controller:** OFF
- **NNLC:** OFF
- **Model:** PopV2
- **Live Learning Delay:** ON

---

## Steering Assist Activation Behavior

Configure steering assist activation according to preference:

### Activate on Every Startup
```
STEERING → CUSTOMIZE MADS → TOGGLE MADS WITH CRUISE MAIN: ON
```

### Activate Only After LKAS Button Press
```
STEERING → CUSTOMIZE MADS → TOGGLE MADS WITH CRUISE MAIN: OFF
```

---

# Settings Reference

## Aragon's Important Setting TLDRs

The short version — if you only read one part, read this. Full per-setting detail is in the sections below.

- **Low Pass Filter (tau):** Reduces stutter, adds lag. Adds even more lag if tuned above defaults.
- **Notch Filter (+ Notch Q):** Aims to remove stutter with no additional lag. Targets the specific frequencies stutter occurs at, but may not be useful if the exact frequency is unknown. Lower Notch Q to expand the removal to nearby neighbors; raise it to be more strict.
- **Lateral P / I / F Scales:** Raise if the car is permanently too lazy in that band; lower if it's twitchy. P sharpens reaction to error, I pulls harder out of persistent error, F pre-applies curvature torque. To mimic the old single PID scale, raise P and I together and leave F at 100%. [Watch this](https://youtu.be/4Y7zG48uHRo)
- **Longitudinal PID Personality Scales:** Each distance/personality has its own longitudinal PID scale. These scales are active only with a gas pedal interceptor and Live Learning Gas OFF; all other cases stay at 100%.
- **Center Boost:** Created because Comma's models love to be lazy. Boosts the lateral tune (gives it a multiplier) for rock-solid straight-line performance, but only when the car is within the limits of Center Boost Threshold (deg).
- **Increase Driver Override Hysteresis:** Adds some time before a detected override is applied to prevent false positives, but might cause grinding.
- **Driver Override Threshold:** Start with 1200 as a baseline and raise to a max of 2400 until huge torque drops no longer happen.
- **Override Fade Down/Up:** Too long of a fade down might cause grinding. Tune how you like.
- **Override Torque Retain:** 0% is the healthiest for the EPS, but 50% or 100% for cars with less torque might be more ideal for co-assistance.

---

## Learned Parameters

openpilot continuously estimates a few vehicle parameters from how the car actually responds, instead of trusting fixed book values. Each one here has an **Auto** toggle: ON feeds the live-learned value into the controller, OFF pins it to a static base. The panel also shows the current learned numbers live (read-only) so you can watch them settle.

- **Learn Steer Ratio (Auto)** — the ratio between steering-wheel angle and road-wheel angle. On ordinary cars, ON uses openpilot's live estimate and OFF uses the static base. Mapped Hondas instead follow the selected model artifact's reviewed policy: Pop and Off-Policy artifacts use the road-tested legacy dual-BP curve, while reviewed Deep-RL artifacts use the raw firmware VGR at every steering angle. An unknown model receives no guessed model correction; it uses raw firmware geometry only when the exact EPS firmware is mapped, otherwise it leaves openpilot's stock VehicleModel untouched.
- **Learn Tire Stiffness (Auto)** — how strongly the tires generate cornering force. ON uses the live factor; OFF pins it to 1.0. It affects how much curvature the model expects from a given steering command.
- **Learn Angle Offset (Auto)** — the steering angle that actually corresponds to "straight" (sensors are rarely perfectly zeroed). ON uses the learned offset; OFF forces 0.0. If a bad offset gets learned (e.g. after a long crab-walk or a sensor glitch) it pulls the car to one side — turning OFF is the quick fix while it re-learns.

---

## Lateral Tuning

### 1/4 — Low Pass Filter

**Low Pass Filter (tau)** — a low-pass on the steering-torque command. It smooths out high-frequency jitter/stutter, at the cost of phase lag: the bigger the time constant (tau, in seconds), the smoother and the laggier. The goal is the smallest tau that kills the stutter — past about 0.1s, the added lag itself starts causing the slow oscillations it was meant to prevent. The filter is speed-banded so you can stay sharp where you need response and smooth more where you don't:

- **Low Pass Filter Tau (<25mph)** — tau below 25 mph.
- **Standard Tau (25–50mph)** — tau between 25 and 50 mph.
- **Highway Tau (50mph+)** — tau at 50 mph and up.

All three only do anything while the **Low Pass Filter** toggle is ON. Higher speeds usually tolerate (and benefit from) a touch more smoothing; low speed wants the least lag so parking-lot maneuvers stay crisp.

### 2/4 — P / I / F scales

The lateral controller is a PID: **P** reacts to the current path error, **I** accumulates stubborn error over time, and a feedforward (**kf**) term pre-applies torque for the curvature the model already knows is coming. On NRDR's torque-mod Honda platforms, the base tune is static at every speed: `kp = 0.03`, `ki = 0.01`, and `kf = 1.2e-5`. The controls below are optional percentage multipliers evaluated independently in the Low Speed (<25mph), Standard (25–50mph), and Highway (50mph+) bands; they are not a baked-in gain schedule.

- **Proportional Scale** — percentage multiplier on the P term. Higher = sharper reaction to error (tighter tracking and corner-cutting, but more twitch and possible weaving); lower = softer (wider swings on curves, fewer corrections).
- **Integral Scale** — multiplier on the I term. Higher = harder pull out of persistent error (holds a corner, but can wind up and weave); lower lets small steady errors stand.
- **Feedforward Scale** — multiplier on kf, the pre-applied curvature torque. Higher shoves the car into curves earlier (can over-corner); **100% leaves it at the tuned value.** Holding F at 100% while you raise P/I is the new equivalent of the old "Keep Feedforward Static" — you gain correction authority without inflating the feedforward.

100% is neutral for every term in every band and preserves the same static base tune across all speeds. Change a band only when you intentionally want a speed-specific live multiplier. *(Longitudinal uses four personality-specific combined scales plus its own Keep Feedforward Static toggle — see Longitudinal Tuning.)*

### 3/4 — center boost & unwind

- **Center Boost** — comma's model tends to under-correct on dead-straight roads, letting the car drift lazily within the lane. This adds an extra multiplier on top of the normal output, but only near center, so you get a rock-solid straight line without making the whole tune twitchy (0.50 = +50% boost). One static value across all speed ranges.
- **Center Boost Threshold (deg)** — how close to center, in steering degrees, the wheel must be for the boost to be active. Outside this band you're cornering, so the boost backs off and lets your normal curve tune do the work.
- **Unwind Integrator Freeze** — as the wheel returns toward center after a curve, a wound-up I term can keep pushing torque and overshoot past center. This freezes the integrator during the unwind so it stops holding torque through the return.
- **Unwind Lookahead** — instead of waiting for the instantaneous desired curvature to drop, this reads the model's planned path and starts unwinding earlier, for a smoother, more natural exit out of curves.

### 4/4 — notch, delta limiter, min speed

- **Notch Filter** — some EPS racks have a fixed resonance (often a ~7Hz growl) that shows up as steering chatter. A notch (band-reject) filter removes a narrow band right at that frequency while leaving everything else untouched — so unlike a low-pass, it adds almost no broadband lag. Best paired with a well-tuned LPF.
- **Notch Frequency (Hz)** — the center frequency to remove. Set it to whatever your EPS actually growls at (listen for it, or read it off logs). The wrong frequency does nothing useful.
- **Notch Q / Width** — how wide the cut is. Higher Q = a narrow, surgical notch; lower Q = wider, also pulling down neighboring frequencies. Lower it if you're unsure of the exact frequency, raise it to be precise once you've found it.
- **Legacy Steer Delta Rate Limiter** — an older method that caps how fast requested torque can rise or fall. Mostly superseded by the LPF + notch; left in for those who still want it.
- **Steer Delta Up / Down** — the max upward/downward torque change per step when the limiter is ON. Too low adds lag.
- **Minimum Steer Speed (mph)** — below this speed, no steering torque is commanded at all. 0 = steer at any speed, including standstill (stock). Raise it if you don't want the wheel moving in parking lots or at a dead stop.

---

## Ford Lateral Tuning (Expedition)

OEM-style four-signal Ford lateral control, ported from BluePilot, one level under Lateral Tuning. **Ford only** — these have no effect on other makes. Everything here is gated behind the master toggle, which defaults OFF (stock curvature-only steering).

- **Ford: OEM-Style Lateral (Default: OFF)** — replaces stock curvature-only steering with Ford's full four-signal command (adds curvature-rate plus a lane-centering path-angle), the way the factory system actually drives. Targets the two stock complaints: the wheel fighting you after you grab it, and running out of steering authority in vigorous turns. OFF = stock curvature-only path, completely unchanged. BETA — first test on an empty road with your hands ready.
- **Ford: Human Turn Detection (Default: ON)** — when you hold the wheel into a turn past 45°, openpilot stops commanding steering so it isn't fighting you, then ramps smoothly back in when you let go instead of snapping. This is the fix for "the wheel tries to throw me off the road" after you touch it.
- **Ford: Lane Positioning (Default: ON)** — drives the path-angle signal with a lane-centering PID for extra steering authority and tighter in-lane position — the main lever against "runs out of torque." Engages at highway speed and steps aside during auto lane changes.
- **Ford: Lane Positioning Strength (Default: 100%)** — how hard the lane-centering path-angle pulls toward lane center. 100% = baseline. Raise for stronger centering, lower if it feels busy.
- **Ford: Max Lateral Accel (Default: 2.40 m/s²)** — raises the lateral-acceleration ceiling that caps how hard the car will corner — the most direct knob for "runs out of torque." Stock is ~2.4 m/s², set low on purpose because the safety model can't see road banking. Raising it gives more cornering authority but removes that conservative margin; increase in small steps and validate on-road.

---

## Override Tuning

"Override" = the EPS deciding you are steering, so openpilot should back off. On sensitive Honda racks this can false-trigger and cause a sudden torque drop mid-corner. These settings tune how that hand-off is detected and how it feels.

- **Increase Driver Override Hysteresis** — doubles the override threshold below, adding a margin so brief torque spikes aren't misread as you grabbing the wheel. Fewer false drops, but a genuine override is recognized slightly later.
- **Driver Override Threshold** — the raw steering-torque-sensor reading above which you're considered to be steering. 1200 is Honda's stock value; on the few cars with a different stock threshold your number is applied proportionally, so 1200 always means "stock." Higher = openpilot holds on through more of your input before letting go.
- **Pass-through assist torque on override** — ON resets the EPS's internal lane-assist state during override, so once the fade completes the wheel feels exactly like normal manual driving; OFF can leave a heavier, more resistive feel in the rack through the override.
- **Override Torque Fade Down (s)** — how quickly openpilot torque ramps out once override begins.
- **Override Torque Fade Up (s)** — how quickly it ramps back in after you let go.
- **Override Torque Retain (%)** — how much openpilot torque stays applied after the fade-down completes. 0% fully releases (easiest on the EPS); 50–100% keeps co-assisting, which can help on lower-torque cars where you still want help while nudging the wheel.

---

## Longitudinal Tuning

- **Distance 1–4 / Personality PID Scales (%)** — separate multipliers for Aggressive, Standard, Relaxed, and Econ, defaulting to 200%, 100%, 80%, and 50%. They apply only on a gas-interceptor car while Live Learning Gas is OFF. PCM-controlled cars and Live Learning Gas always use 100%.
- **Keep Feedforward Static** — the active personality scale multiplies only the feedback (P+I) terms, leaving the longitudinal feedforward (kf) at its tuned value. Use it when you want more correction authority without also inflating the feedforward.
- **Live Learning Gas** — Honda gas response and wind-resistance compensation differ car to car, so this learns them live while you drive. Samples are lag-aligned (~0.5s, to match pedal-to-response delay) and only taken in quasi-steady conditions, the result is clamped to a safe band around nominal, and it's persisted across drives. While enabled, every longitudinal PID personality scale is held at 100%. Offroad toggle.
- **Try Honda Bosch Radar (experimental)** — reads the factory Bosch radar's fine-range objects (CAN 0x280) and feeds them to the longitudinal controller. Honda Bosch only, and the decode is reverse-engineered (cross-validated across Civic Bosch radars, but still) — confirm the lead distance/closing rate look right before trusting it for following.
- **Stopping Decel Rate** — brake-rate limiter used as the car settles into a stop (carcontroller side).
- **Stop Accel** — the target acceleration once fully stopped (holds brake pressure so you don't creep).
- **Planner Stopping Rate** — how quickly the commanded deceleration ramps down as you approach a stop (planner side).
- **vEgo Stopping / Starting (m/s)** — the speed below which the planner calls the car "stopping," and the speed above which it's "moving again." Tightening these changes how crisply it transitions in and out of a stop.

---

## Special

### 1/2 — injection test & dashboards

- **Injection Test (Caution!)** — multiplies the lateral PID output by 999% (≈10×). It's a deliberate stress test to see how the car and EPS react to a massive steering command — useful for probing authority limits and failure behavior. Safe, empty road only, hands ready on the wheel. Not a daily setting.
- **Alternative Dashboard Speed Design** — repurposes the cluster's set-speed digits (requires openpilot longitudinal): Stock, Lead Speed (the lead car's speed in whole mph; "Stopped" under 1 mph, "--" with no lead), GPS Speed (the comma's own true speed), or Cluster Speed (exactly what the dash cluster reads).
- **Alternative Dashboard Distance Design** — repurposes the cluster's distance bars / mini-car (requires op-long): Stock, Radar (bars close in as the lead approaches), or Velocity (bars push out under acceleration, pull in under braking). Non-stock designs stay on the cluster permanently, even when not engaged.

### 2/2 — dash faults & cruise sub-mode

- **Clear Dashboard Fault Codes** — forces the cluster's FCM/icon fault bits off and suppresses the stock FCW chime, so a car with a dead or absent stock camera runs a clean dash. OFF = stock behavior (camera values passed through, FCW chime active).
- **Spoof Camera Messages** — dead-camera only: keeps the camera's CAMERA_MESSAGES broadcast alive so the cluster never throws "Auto High Beam System Problem" (that fault is just a message timeout, not a real code). Leave OFF if your stock camera works.
- **Cruise Button Sub-Mode** — a dynamic HUD. The first press of the distance button or set/resume doesn't act — it wakes a ~15s preview on the cluster showing the current personality on the distance bars (and set speed if engaged), all blinking. Only presses made while the preview is open actually change personality / set speed, and each press refreshes the window. The blink starts lazy and speeds up as the window runs out, so you can feel how much time is left.
- **Sub-Mode Visibility Time (s)** — how long that preview stays up after a press (5–60s). The blink ramp always spans the whole window, slow at the start and quickest right before it falls off.

---

## Remote Actions

These let you trigger a device action remotely (e.g. from Sunnylink) by flipping a toggle. The device flips the toggle back OFF the moment it picks up the request — that flip is your acknowledgment.

- **Force Update** — runs the full updater chain on the device: check, download, install, reboot. Only works while the car is off. Watch Remote Action Status for progress.
- **Run Tune Report Scan** — analyzes every drive log on the device and produces a per-speed steering report. A full day of logs can take a few minutes; the device flips the toggle OFF when it starts, the summary appears in Tune Report Summary when done, and the full report is saved to `/data/nrdr_tune_report.txt` (grab it via the copyparty file server in Developer).
- **Remote Action Status** — live status / progress readout for the actions above.
- **Tune Report Summary (per speed)** — the scan results. Reading it: `mean_err > 0` = under-steering vs what was desired; high `flip/100` = the controller is hunting/oscillating (lower kp); high `sat%` = you're running out of steering authority (commanding more than the EPS will give).

---

## Reference Videos

- [AerospaceControlsLab](https://www.youtube.com/channel/UCVTxuaJsdMrk3UEcHVll9Yg)
- [Controlling Self Driving Cars](https://www.youtube.com/watch?v=4Y7zG48uHRo)

---

## Drive Uploads

This fork routes drive uploads through:

```
stable.konik.ai
```

---

## Device Pairing / Offline Issues

If the device appears offline or cannot be paired, refer to:

https://community.sunnypilot.ai/t/using-stable-konik-or-any-other-hosted-routes/945

---

## Important Notes

- While running this fork, the device communicates with `stable.konik.ai` and does not connect to Comma servers.
- When switching to another fork, always perform a factory reset first.
  - This preserves your Comma Connect account.
  - It reduces the risk of pairing or account-related issues.

---

## Disclaimer

This fork is intended for use with compatible Linear EPS firmware. Users are responsible for ensuring the correct firmware is installed prior to use. Running this fork without the appropriate EPS firmware will result in incorrect lateral control behavior.
