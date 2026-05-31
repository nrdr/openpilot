# nrdr branch — Changelog

**Baseline:** `c93469ed00 🔧 Prerequisites` (2026-02-11)
**Through:** `98a7320289 Live Long v2.0!` (HEAD, 2026-05-29)
**Scope:** 72 commits on the `mvl-testing-05.28.2026` branch of `nrdr/openpilot`, plus the linked `opendbc` submodule (`nrdr/opendbc`).

Grouped by area, newest work first. Hashes are the branch (parent-repo) commits; the opendbc section summarizes the submodule changes those pointers reference.

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
