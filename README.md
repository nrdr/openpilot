# Welcome to the last Honda torque mod you'll ever need

[Come join us on Discord!](https://discord.gg/Whk2kJd)

## Overview

This fork supports the Proper Torque Modification available for select Honda platforms. We are calling this **PTC**.

[Check your car's torque-mod status and files](https://docs.google.com/spreadsheets/d/1edkzOjTJfXRjE9v0nHh0uVFfhPFSkYnI3sg0oVliRkU/edit). The sheet is the source of truth for supported cars, rack firmware, and the file intended for each EPS.

PTC combines modified EPS firmware with software that knows how that firmware behaves. The firmware and the software tune are a pair: using one without the other can produce the wrong steering response.

## Getting started

> **Flashing an EPS writes a real steering ECU.** Confirm the exact car, rack, and firmware in the status sheet; keep the vehicle on stable power; do not interrupt a flash; and ask in Discord before guessing. A wrong or interrupted flash can leave the EPS unusable.

1. Check the status sheet for your exact car and EPS firmware.
2. Factory-reset the device before changing branches. This is required when moving between NRDR, clean, bare, or another fork.
3. From the openpilot root, run `python3 flash.py`, choose the latest PTC firmware listed for your exact rack, and follow every prompt. Read the [EPS flashing guide](eps_tools/README.md) before starting.
4. Install the branch that matches how much experimentation you want.
5. Start with the branch defaults. Change one setting at a time and keep notes.

These branches are tuned for the current PTC firmware. Legacy **2X** and other older torque mods have a different, non-linear response and are not the tuning target.

## What works

Validated PTC files are designed to provide more usable steering authority than the older legacy torque-mod files. The fork adds a static Honda PID base, rack-aware steering geometry, steering filters, driver-override handling, and optional vehicle-specific tuning tools.

On the seven PTC Honda platform fingerprints in the current code, the base is static at every speed: `kp = 0.03`, `ki = 0.01`, and `kf = 0.000012`. Optional Low, Standard, and Highway P/I/F controls scale that base; **100% means no change**.

This is research software, not a safety certification and not a self-driving system. The driver must supervise it at all times.

## What doesn't yet

Some steering racks can develop **stutter**: a low-frequency feedback loop that may make noise or rock the wheel back and forth like a ratchet. Stutter is usually more of a control-quality problem than an EPS-hardware problem, but it can push the torque sensor past the driver-override threshold. NRDR may then mistake it for you taking the wheel and instantly drop NRDR's steering assist torque—even mid-turn.

If this happens, take over and disengage safely. Once parked, go to **Settings → nrdr → Lateral Tuning → Override Tuning** and raise **Driver Override Threshold** one `100`-point step at a time; use the lowest value that stops false overrides. For drops near center, raise **Override Threshold Center Boost** too, or set it equal to the main threshold so the lower near-center threshold is not used. The normal editable defaults are `1400` for the main threshold and `1000` near center. Both controls run from `100` to `5000`, and `1200` represents the car's stock threshold even when its raw sensor value is different.

If the controls are gray, **Handcrafted Lateral Tuning** owns them and locks them to its profile (`2000` main and `1200` near center). Turn that profile off only if you intend to tune these values by hand. Do not max either control: higher thresholds make NRDR slower to yield to real driver input. This is only a false-detection workaround, not a cure. If stutter is strong, repeatable, or affects control, stop testing that firmware, return to a known-good configuration, and report the exact rack/firmware plus logs in Discord.

Many Hondas also have a non-linear variable steering ratio inside the rack. A single static ratio cannot describe the whole steering range, so the car may track too far inside or outside a curve when the model and rack geometry disagree. NRDR maps reviewed EPS firmware and model artifacts to the correct geometry policy; coverage is still being expanded car by car.

## Branches to install

**You MUST factory-reset before switching branches.** Development branches are source/QC lanes, not promised end-user releases.

- **`nrdr-clean`** — compliance build intended to retain the rules needed for standing with comma and its services. Uses `connect.comma.ai`.
- **`nrdr-nightly`** — newest precompiled NRDR build. Experimental or incomplete safety-related work may be present. Use at your own risk. Uses `stable.konik.ai`.
- **`nrdr-staging-<DATE>`** — precompiled snapshot cut from development, normally named `nrdr-staging-MM.DD.YYYY`. Use one to pin a known-good build or identify when a regression appeared. Uses `stable.konik.ai`.

### Bare branches

- **`nrdr-bare`** — stock openpilot plus the hardcoded PTC tune and the minimal dynamic steer-ratio/controller integration needed for it. It omits the larger NRDR feature set. Uses `connect.comma.ai`.
- **`nrdr-bare-only-tune`** — stock openpilot with only the hardcoded PTC tuning dependency. It lacks dynamic steer-ratio tuning and the wider lateral enhancements, so it may not track as well on non-linear racks, but it is the smallest and most upstreamable branch. Uses `connect.comma.ai`.

<details>
<summary>Source and QC branches</summary>

- **`nrdr-architecture-development`** isolates NRDR-owned code under `openpilot/nrdr` for review and future integration.
- **`nrdr-development-new`** carries the same active behavior in the older layout while the architecture rewrite is validated.
- **`nrdr-development`** remains the existing development branch during that transition.

</details>

## Settings in plain English

Settings appear only when they apply to the detected car and hardware. A grayed-out control is usually locked because **Handcrafted Lateral Tuning** owns it. Start from defaults, change one thing at a time, and never use a slider to hide a firmware mismatch.

<details>
<summary><strong>Handcrafted Lateral Tuning and vehicle learning</strong></summary>

- **Handcrafted Lateral Tuning** loads the versioned, Clarity-derived road-tested profile for the supported Accord, Civic, Clarity, CR-V, and Insight fingerprints. It also restores the profile if another setting tries to change one of its owned values. Leave it OFF if you intend to tune manually.
- **Loaded Vehicle & Tune** shows the detected fingerprint, EPS firmware, controller, geometry, and the actual gains in use. Check this before assuming a setting loaded.
- **Learn Steer Ratio (Auto)** uses openpilot's learned scalar only outside NRDR's active model/firmware geometry policy. Mapped firmware and exact legacy-model policies keep their configured geometry authoritative.
- **Learn Tire Stiffness (Auto)** lets openpilot learn how strongly the tires respond. OFF pins the factor to `1.0`.
- **Learn Angle Offset (Auto)** learns which sensor angle means straight ahead. Turn it OFF temporarily if a bad learned offset is pulling the car sideways.
- **Run Tune Report Scan** reads saved drive logs and summarizes tracking by speed. It is a diagnosis helper, not an automatic permission to change gains.

</details>

<details>
<summary><strong>Controller Tuning Dungeon</strong></summary>

- **P / I / F scales** are split into Low (below 25 mph), Standard (25–50 mph), and Highway (50 mph and above). P reacts now, I corrects an error that will not go away, and F prepares for the curve the model already requested. `100%` keeps the tuned base.
- **On-Center Steer Ratio** is the rack ratio near straight ahead. **Outer Steer Ratio** is the high-angle endpoint used only by exact legacy dual-BP model artifacts.
- **Start Lane Changes at Outer SR** affects only legacy dual-BP mode. It starts a lane change at the outer ratio and fades back to the normal curve; it does nothing in pure-firmware or unclassified mode.
- **StarPilot PID Additions** enables borrowed turn-in, unwind, and left/right scaling that was not built for Honda. Leave it OFF unless you are deliberately comparing it.
- **Rate Damping (D) Strength / Fade-Out Speed** resists fast wheel movement to calm low-speed ringing, then fades away with speed. Too much makes steering heavy.
- **Center Boost / Threshold / Minimum Speed** adds extra P correction only near center and only above the chosen speed. It does not multiply I, F, or damping.
- **Predictive Lateral Stiction** tapers and holds torque as the wheel reaches a stable target, then releases immediately for driver input, lane changes, faults, or steering limits.
- **NNLC** is the optional Clarity neural lateral controller. Activation speed chooses the PID-to-NNLC handoff; KP, KI, and KF scale its three terms. Lane changes remain on PID, and raw firmware-VGR mode disables NNLC.

</details>

<details>
<summary><strong>Driver override and steering filters</strong></summary>

- **Driver Override Threshold** decides how much driver torque means “the human is steering.” **Override Threshold Center Boost** can use a lower value near center. Raising either value delays the handoff to the driver.
- **Increase Driver Override Hysteresis** makes brief torque spikes less likely to cause a false handoff.
- **Pass-through assist torque on override**, **Fade Down**, **Fade Up**, and **Torque Retain** control how assist leaves and returns when you take the wheel. These directly affect driver handoff; adjust cautiously.
- **Low Pass Filter (tau)** smooths fast steering commands. Its three speed-band tau values trade chatter for delay: larger is smoother but laggier.
- **Legacy Steer Delta Rate Limiter / Delta Up / Delta Down** caps how quickly torque may change. It is an older alternative; values that are too restrictive add lag.

</details>

<details>
<summary><strong>Longitudinal tuning</strong></summary>

- **Live Learning Gas** learns gas response and wind compensation. While it is ON, the four personality PID scales stay at 100%.
- **Distance 1–4 PID Scales** change feedback for Aggressive, Standard, Relaxed, and Econ. They apply only with a gas-pedal interceptor and Live Learning Gas OFF.
- **Keep Feedforward Static** lets a personality scale change P and I without multiplying the tuned feedforward.
- **Nidec ECU-Matched Long**, **Full Nidec Brake Authority**, and **Roen Nidec Acceleration Limits** change Nidec gas/brake shaping and authority. They are vehicle-specific; do not copy another car's result blindly.
- **Honda Bosch-A Radar** is experimental. With Alpha Long, its reverse-engineered tracks feed braking and acceleration decisions, while factory Honda AEB/CMBS is unavailable. Disable it if objects look wrong.
- **Set-Speed Overshoot Allowance** permits a small target above the selected speed. **Cruise Mismatch Correction** fixes a repeatable displayed-versus-actual cruising error.
- **Stopping Decel Rate**, **Stop Accel**, **Planner Stopping Rate**, and **vEgo Stopping/Starting** shape the final approach to zero and the move-off transition.
- **Honda Dashboard Variant B** is currently a placeholder and has no effect.

</details>

<details>
<summary><strong>Special, device, and remote tools</strong></summary>

- **Injection Test** multiplies lateral PID output by about ten. It is a stress test, not a driving mode; leave it OFF unless you understand the test and have a controlled environment.
- **Alternative Dashboard Speed/Distance** repurposes cluster graphics for lead speed, device speed, radar distance, or acceleration. It requires openpilot longitudinal control.
- **Clear Dashboard Fault Codes** hides selected camera/FCM indicators and suppresses the stock FCW chime; it does not repair a fault. **Spoof Camera Messages** is only for a dead or absent stock camera.
- **Cruise Button Sub-Mode / Visibility Time** makes the first button press open a blinking preview; presses inside that window perform the change.
- **Show Footage / File Server** creates local, offroad-only QR links to recorded drive files.
- **Re-register with konik** is only for a Konik build that cannot come online after switching backends. Clean builds remove this action.
- **Prevent Automatic Shutdown** bypasses normal offroad shutdown timing and can drain the vehicle battery. Manual Power Off still works.
- **Force Update** requests the updater while the car is off. **Remote Action Status** reports progress.

</details>

## Special thanks to

- [vote_for_nobody](https://github.com/JamesL787)
- [Peter](https://github.com/peterclampton)
- [MVL](https://github.com/mvl-boston)
- [sunnyhaibin](https://github.com/sunnyhaibin)

## Disclaimer

Use only firmware confirmed for your exact EPS. Keep both hands ready, stay attentive, and obey local laws. You are responsible for the vehicle, the flash, and every setting you change.
