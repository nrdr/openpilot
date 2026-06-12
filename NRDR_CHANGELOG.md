# nrdr branch — Changelog

**Baseline:** `c93469ed00 🔧 Prerequisites` (2026-02-11)
**Through:** `nrdr-development` HEAD (2026-06-12)
**Scope:** the `nrdr-development` branch of `nrdr/openpilot` (formerly `mvl-testing-05.28.2026`), plus the linked `opendbc` submodule (`nrdr/opendbc`, branch `nrdr-dbc-development`).

Grouped by area, newest work first. The opendbc sections summarize the submodule changes the parent pointers reference.

---

## The everything update (2026-06-11 → 06-12)

One marathon session: tune intelligence, the Dynamic HUD, remote actions, roadside footage, AGNOS per-device support, and the release pipeline rebuilt.

### Tuning & control
- **Tune Report on the UI with scoring & advice** — `tune_report.py` now opens with a `TUNE SCORE` section: a 0–10 score (transparent penalty model: weighted bias up to −4, rms noise −3, oscillation −2, saturation −1; constants at the top of the file), a plain-English headline ("…most error on left turns at 42 mph; logs show PID values might be undertuned at this speed"), ranked findings classified undertuned / overtuned / saturated with suggestions that name the exact slider (speed-band PID Scales, Center Boost, taus, Notch), and an automatic left/right asymmetry check pointing at the `_pid_output_scale` quadrants. Findings only aggregate individually-bad mph bins (healthy bins diluted hot spots and could flip a diagnosis); bias-dominance outranks flip count. On-device: **Tune Report** item at the top of Lateral Tuning with SCAN/VIEW buttons (error-log-style modal; full report persists at `/data/nrdr_tune_report.txt`).
- **PID Tune Information** — VIEW popup under Tune Report showing the kp/ki/kf actually loaded for the car's fingerprint (from `CarParamsPersistent`), with BPs in mph, longitudinal PID, steerRatio/actuator delay/geometry. Friendly message when no car has fingerprinted yet.
- **Keep Feedforward Static split** — `NrdrPidScaleExcludeKf` replaced by `StaticFeedforwardLateral` + `StaticFeedforwardLong` (both default ON): PID scales multiply P+I only; kf keeps its tuned value. Separate toggles in Lateral and Longitudinal Tuning.
- **Center Scale → Center Boost** — all speed-interp logic removed (including the −0.09 low-speed taper); one static value across all speeds, displayed as a percentage (50% = the old 0.50). New **Center Boost Threshold** (°, default 3.0, 0.1 steps): the boost is active only within this angle of dead-center, with a 1° linear fade past it.
- **Driver Override Threshold** — slider (default 1200, steps of 100) for the `STEER_THRESHOLD` steeringPressed detection point. 1200 = Honda stock; on cars with table overrides (RDX 400, Accord 9G 30, …) the value applies proportionally so 1200 always means stock. The old tolerance toggle is renamed **Increase Driver Override Hysteresis** (doubles the threshold) and now defaults **OFF**.
- **Minimum Steer Speed** — slider at the bottom of Lateral Tuning (0–45 mph, default 0 = stock). Below it the carcontroller commands zero steering torque and drops lkas_active; at 0 the gate can never fire.

### Dynamic HUD & Special panel (formerly Party Tricks)
- **Cruise Button Sub-Mode** (`NrdrCruiseButtonSubMode`, default ON) — pressing distance or set/resume first wakes a preview on the cluster: bars lit with the CURRENT personality regardless of engagement, set speed if engaged, all blinking. Only presses during the preview act; each press refreshes the window. Window length adjustable 5–60 s (`NrdrCruiseButtonSubModeSecs`, default 15); blink accelerates continuously from 1000/200 ms to ~5 Hz at cutoff via `np.interp` over the whole window. Press gating in `selfdrived.py` (personality) and `cruise.py` (v_cruise) through the shared `nrdr_hud_submode.py` deadline param; blink rendered in the opendbc carcontroller.
- **Alternative Dashboard split into two designs** — Speed (`HondaAltDashboardSpeed`: Stock / Lead Speed / GPS Speed / Cluster Speed; whole-mph values) and Distance (`HondaAltDashboardDistance`: Stock / Radar / Velocity). Non-stock designs stay on the cluster permanently: mini car forced on and `HUD_LEAD` tracks lead presence regardless of engagement (the disengaged lead-icon bug). ACC_ON bars only on Stock distance or during the sub-mode.
- **Clear Dashboard Fault Codes** (`NrdrClearDashFaults`, default ON) — the previously hardcoded FCM/icon zeroing + FCW chime suppression is now a toggle; OFF restores exact stock passthrough (and the FCW chime).
- **Spoof Camera Messages** (`HondaSpoofCameraMessages`, default OFF) — dead-camera cars: the "Auto High Beam System Problem" fault is a timeout on the camera's `CAMERA_MESSAGES` (0x35E) broadcast, not a code. This keeps the message alive at 10 Hz on Nidec. Required adding 0x35E to the Honda Nidec safety TX allowlist.
- **Show Footage** — first item in Special: pick a drive, get a QR pointing a phone (device hotspot or same Wi-Fi) at the copyparty file server for that drive's video. Hotspot/wlan-preferring IP selection (never the LTE address). `EnableCopyparty` now defaults ON via the nrdr defaults system.

### Sunnylink
- **econ 4th personality finally on the website** — `cruise.yaml` was never updated for the 4-bar personality; fixed.
- **Remote Actions panel** — website "buttons" via trigger params consumed and cleared by the new `nrdr_remoted` daemon (offroad): Force Update (full updater chain) and Tune Scan (full report to disk, per-speed friendly summary + status mirrored back via `NrdrRemoteStatus` / `NrdrTuneReportSummary` info rows).
- Both dashboard designs are dropdowns (`widget: option`); panel renamed **Special**; every new toggle/slider mirrored.

### System, build & release
- **Force Update does the real thing** — the home-screen button drives the actual updater chain (SIGUSR1 check → SIGHUP download → DoReboot install) as a state machine with live status on the button; opsync.sh retired from that path.
- **Three branches per build** — `build_prebuilt.sh` pushes the dated staging branch, `nrdr-nightly` (overwritten), and `nrdr-clean`: a single fresh commit with the QoL + konik commits reverse-applied **before** committing, via static patches in `release/clean_excludes/` (device git history can't be trusted on shallow installs), konik API/Athena exports stripped, and the home subtitle rewritten to connect.comma.ai. Device reboots itself after a successful build (kills the corrupted "ghost install" state).
- **AGNOS is now per-device** — mici (comma 4) runs 18.4 from the new `agnos-mici.json`; tici/tizi (C3/C3X) run 18.3 from `agnos.json` (comma's tici images at v0.11.1 — same firmware partitions as 18.4, tici system image). Selection by devicetree model in `launch_env.sh` / `launch_chffrplus.sh` and by `HARDWARE.get_device_type()` in `updated.py`. Root cause of the 06-12 C3X crash: PR #3 synced the *shared* manifest from commaai release-mici, putting comma-4 system images on C3X flash paths. The C3 is untouched (own env + manifest under `sunnypilot/system/hardware/c3/`).
- **AGNOS 18.x build fixes** — `fonts/process.py` handles both raylib generations (new LoadFontData takes a glyph-count out-param and returns only found glyphs; everything downstream now uses that count — the old assumption segfaulted); `loggerd/SConscript` links `va`/`va-drm`/`drm` on device (18.x ffmpeg is VAAPI-enabled), matching upstream v0.11.1.
- **Home screen shows the device IP** (hotspot/wlan-preferred) in place of the old joke line; refreshes every 10 s.

---

## Defaults, econ & Party Tricks v1 (2026-06-09)

- **econ 4th personality** — `log.capnp` `econ @3`, planner `get_T_FOLLOW` = 2.0 s, UI button, `% len(enum)` cycling, and the 4th Honda distance bar (`HUD_DISTANCE = leadDistanceBars % 4`).
- **Party Tricks panel (v1)** — Injection Test (x9.99 PID scale diagnostic) and the original 3-way Alternative Dashboard (superseded 06-11 by the Speed/Distance split).
- **nrdr defaults system** — `apply_nrdr_default_params` in `manager_init` seeds defaults (metered off, nrdr toggles, econ, ChevronInfo=All, ACC increments, …) without overriding user choices; hardened so one bad put can't crash boot (C4-safe).
- **First-run popups** — Pop V2 model + full-US OSM map prompts on factory-fresh boot; model auto-select daemon-side.
- **Couch-config un-greying** — cruise/visuals/speed-limit panels no longer wipe params when the car isn't detected.
- **Learned Parameters** moved to its own nrdr sub-panel; `tune_report.py` (SSH version) added at repo root.

---

## Lateral tuning additions (2026-06 early series)

- **Center Scale live param** — replaced the per-car `_center_taper_high()` lookup in `latcontrol_pid.py` with a live `HondaCenterScale` param (FLOAT, default 0.5; 0.01-step "Center Scale" slider under Lateral PID Tune Scale). Note: Clarity previously used 1.24 and Civic Bosch 0.25 via the lookup — those cars now default to 0.5 until the slider is set. *(Superseded 06-11: renamed Center Boost, % display, speed interp removed, threshold-gated — see above.)*
- **Unwind Integrator Freeze** — opt-in `HondaUnwindFreeze` toggle (default OFF). When on, freezes the PID integrator while the desired angle is unwinding (`phase < -0.2`) and heading near center (`< 8°`), so it stops holding torque through the release. Applies regardless of hands-on state. Targets steady-state-error / "torque held into the exit" on the linear EPS.
- **Unwind Lookahead** — opt-in `HondaUnwindLookahead` toggle (default OFF). Feeds `modelV2` into `latcontrol_pid` and reads the planned lateral-accel profile (~1s ahead) to anticipate the turn release *before* the instantaneous desired curvature drops. Ramps the unwind FF weight early and (with Unwind Freeze also on) freezes the integrator ahead of the release. Falls back to the backward-difference phase logic when the model frame is invalid. `controlsd.py` now feeds `modelV2` to the PID controller. Targets the late-unwind / late-phase-switch on intersections and curves.
- Exposed in `nrdr.py` and the Sunnylink `steering.yaml`. `HondaCenterScale` (FLOAT), `HondaUnwindFreeze` (BOOL), `HondaUnwindLookahead` (BOOL) added to `params_keys.h` — C++, require a device recompile.
- **Notch Filter (steering chatter)** — opt-in `HondaNotchEnabled` toggle (default OFF), with `HondaNotchFreq` (default 7.5 Hz) and `HondaNotchQ` (default 1.5). RBJ notch biquad in `carcontroller.py` (opendbc submodule), applied in series after the LPF and before the steer-delta limiter; resets when lat control is inactive. Targets a measured ~7 Hz EPS resonance (FFT of logged steering torque showed ~47% of >0.5 Hz energy in the 5–9 Hz band). Removes the chatter without the broadband lag a low-pass filter adds — verified in sim: 7.5 Hz → 0.0, 0.5–1.5 Hz control band → ~1.0. Exposed in `nrdr.py` + `steering.yaml`. Params are C++ → device recompile.
- **nrdr UI restructured into sub-panels** — the flat nrdr panel is now a top-level page (learned-param display rows + three navigation buttons) leading to `Lateral Tuning`, `Override Tuning`, and `Longitudinal Tuning` sub-panels, mirroring the MADS/Torque sub-panel pattern. New device files: `nrdr_sub_layouts/{lateral,override,longitudinal}_tuning.py`; `nrdr.py` slimmed to the page + dispatch. `steering.yaml` restructured into three `sub_panels` (navigation-only, `trigger_key: null`) and `settings_ui.json` recompiled. All tuning descriptions rewritten from on-road testing.
- **Live Learning Gas default is now platform-aware** — `carcontroller.py` defaults `HondaLiveLearningGas` ON for Bosch, OFF for Nidec (only applies when the param is unset).
- **Sunnylink fix:** `settings_ui.json` is the compiled artifact the website reads; it must be regenerated via `compile_settings_ui.py` after any `steering.yaml` edit and committed. (Earlier missing-settings bug was a stale JSON that predated the yaml edits.)
- **Learned-param Auto toggles** — `NrdrLearnSteerRatio`, `NrdrLearnStiffness`, `NrdrLearnAngleOffset` (BOOL, default ON/Auto). When a toggle is OFF, `controlsd.py` feeds the static base to the vehicle model instead of the live-learned value: steerRatio → `CP.steerRatio` (values.py spec), stiffness → `1.0`, angleOffset → `0.0`. Lets you bypass a drifted/garbage learned value that's hurting performance. Read on the `get_params_sp` cadence in `controlsd_ext.py` (raw `get() != b"0"` so unset = ON, sidestepping `getBool`'s false-when-unset behavior). Learning still runs in the background; toggles only choose whether the controller uses it. The learned values keep displaying for reference even when bypassed. Toggles on the nrdr main page (paired with the display rows) + Sunnylink Lateral Tuning panel.

---

## Live tuning & Honda controls (2026-05-29)

The big push: making the Honda tune adjustable live from the on-device UI, plus fixing several bugs that made the live tuners non-functional.

- **Lateral/Longitudinal PID Tune Scale fixed** (`5f95fb6082`, `0190ccf278`) — the scale multiplier was applying ~100× instead of 1:1 (a units mismatch in the param default/bounds), then a second bug (`Params.get()` returns typed values, not bytes) made the sliders read their default every time. Both fixed; 100% now maps 1:1 to the base tune, and the sliders actually take effect.
- **Live tuner pass** (`11651ae9bc`, `42d65ccb31`, `0035dc0dd6`, `381f95c7d4`) — copied the live-torque read method, wired live PID/long scale reads.
- **nrdr menu overhaul** (`834ef002fb`, `cf3ddf88d7`, `9c7a2eaeba`, `8f2c33e2d8`, `9be8d33377`):
  - PID scale sliders moved to the top; 5% step increments.
  - Speed-banded **Low Pass Filter tau** sliders (Low <25 mph / Standard 25–50 / Highway 50+), 0.01 steps; hidden when LPF is off. Replaced the old hardcoded tau lookup.
  - Override Torque Fade Up/Down in 0.1 s steps; steer-delta in 0.1 steps.
  - **"Replace LKAS torque…" override behavior reversed and relabeled** ("Pass-through standard assist torque on override") — ON now gives way to the driver during override.
  - `(Default: X)` labels added to every param; defaults aligned (LPF on, override tolerance on, etc.).
  - Read-only **learned live-params display** at the top (steer ratio, tire stiffness, angle offset avg/instant), one line each, always visible.
  - Live Learning Gas greyed out while onroad.
- **Live Long v2.0** (`98a7320289`) — longitudinal stopping params (stop accel, planner stopping rate, vEgo stopping/starting) exposed live via `longcontrol.py` / `longitudinal_planner.py`.
- **UI crash fix** (`9c7a2eaeba`) — `speed_limit.py` referenced `controlsState.vCruiseDEPRECATED`, which doesn't exist in this schema; switched to `controls_state.deprecated.vCruise`. Was crashing the UI on long engage.
- **opendbc submodule repointed** (`097caa4dea`) — moved from `mvl-boston/opendbc` back to `nrdr/opendbc` (the `.gitmodules` URL was pulling it to MVL on every sync); corrupted submodule `HEAD` repaired.

## Honda params & settings groundwork (2026-05-28)

- **Keys & Params / param plumbing** (`ba0ec63ed9`, `2992e3f108`, `d20ad129f5`, `cc07658070`, `262eb2c494`, `cac22d16b0`) — added the nrdr Honda param keys and default values to `params_keys.h`.
- **nrdr settings panel** (`18988add6c`, `755561fed2`, `2ab39e6497`, `ad18a39d0f`, `3c3038bfb0`, `31db737701`) — new Honda tuning settings, labels, and default annotations.
- **Dashboard Cluster Behavior Module** (`2c6253d6dc`).
- **opendbc submodule bumps for NRDR Honda controls** (`266b890435`, `5f07a3fde3`, `5f5713e932`, `de4e9dea4a`) — pointer updates carrying the Honda carcontroller work (see opendbc section).
- Several `bump` / fixup commits (`45e4137e45`, `ba15f4ac9f`, `ca35978505`, `87a7bc6540`, `ac8e11e5ec`, `2554c4ceba`).

## Home screen & UI layout (2026-05-28)

- **New home screen** (`0680ac386f`, `327b8bbbd7`) and a long series of iterative layout/hitbox/button-size tweaks across ~15 commits (`f30a65012a`→`73a52c5e77`), plus import-bug fixes (`9d921f9d9a`, `788ce800fe`) and a feedback entry point (`627754158f`).

## Sunnylink integration (2026-05-28)

- Attempts to make the Sunnylink frontend work alongside nrdr (`376fd96875`, `4a257c835d`, `209ea705b8`, `eb0e78da1c`) — most were subsequently **reverted** (`86271e0eec`, `074f76b9d2`, `0adaa7f24b`), with the working approach merged in. "Always Enable Sunnylink" (`31e55fd7d7`).

## Feature modules (2026-05-16)

- **Speed Limit & Cruise Control Module** (`c9833451bc`)
- **Quality of Life Module** (`181c61ee64`)
- **stable.konik.ai full support** (`a1c50bb664`)
- **Repository Update Utility Script** (`76ff300112`)
- **Persistent Power Module** (`e304096628`)
- **User Guide** (`0f26861ee4`)

## Onboarding & nrdr UI foundation

- **nrdr User Interface Module** (`ba4d633d95`) and **"Eliminate onboarding purgatory"** (`e71814fdba`) — the initial nrdr UI + onboarding rework that the rest builds on. `init` (`894aabeda3`).

---

## opendbc submodule (`nrdr/opendbc`)

The submodule pointer advanced several times over this range; the Honda-side work it carries:

- **Honda live tuning params** in `carcontroller.py` — override fade up/down, override torque retain, steer-delta limiter + up/down, gas/wind factors, stopping decel rate, all readable live.
- **`get_param_float` bytes fix** — `Params.get()` returns typed values for INT/FLOAT keys, so the old `.decode()` always fell back to defaults; now handles bytes/str/number. This is what made the Honda sliders actually respond.
- **Speed-banded LPF tau** — `torque_lpf_tau` rewritten to use the three tunable tau bands instead of hardcoded 0.02–0.15 values.
- **Driver-assist-during-override** logic reversed to match the new UI label.
- Param types corrected to `FLOAT` where the UI stores decimals (steer delta, override fade, tau).

---

## Notes

- `params_keys.h` changes are C++ — they require a device recompile to register.
- Python changes (UI, longcontrol, planner, latcontrol) take effect on a process restart.
- opendbc/carcontroller changes require the device to be on the matching submodule commit.
