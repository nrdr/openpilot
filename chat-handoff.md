# openpilot Fork — Session Handoff

Context dump for continuing this work in another assistant. Written by Claude (Cowork), for Brett (GitHub: **nrdr**).

## Who / setup

- Personal **sunnypilot-based openpilot fork** for **Honda Clarity/Pilot** (Nidec EPS), a **Lexus**, and **Ford**.
- Devices: **Comma 3X (C3X)** and **Comma 4 (C4, codename "mici")**. Both run the same AGNOS/compute/sensors, so the C3 can be sold and dev continues on the C4.
- All git / scons / flashing is run on **native Windows CMD** (not the sandbox). File edits are reliable via editor tools; the Linux sandbox mount can read *torn/truncated* copies of just-edited files, so **native `py_compile` / native compile is the authoritative gate** — ignore sandbox-only "syntax errors" at unrelated lines.

## Repos & branches

- Main openpilot dev branch: **`mvl-testing-07.15.2026`** (dated, rotates; previously `-06.26.2026`). This is where all work lands.
- opendbc is a **submodule `opendbc_repo`** on branch **`nrdr-dbc-06.26.2026`**. Pushed separately: `git push --recurse-submodules=no` on the main repo, and push the submodule branch on its own. `git config push.recurseSubmodules no` is set.
- **`nrdr-nightly` is a machine-generated PREBUILT/artifact branch.** `build_prebuilt.sh` force-pushes a compiled snapshot to it on **every commit**. It is an orphan-ish tree (vendored submodules flattened to real files, binaries where source expects Git LFS pointers). **Never base PRs on it, never merge it into source, never cherry-pick its "…prebuilt" commits.**
- Contributor fork remote `risky` = `RiskyBiscuit-arc/openpilot` (their nightly/staging are also prebuilt).

## Work completed this session (all on the source dev branch)

**Lateral controller** (`selfdrive/controls/lib/latcontrol_pid.py`): banded P/I/F scales, rate-damping D, center boost, borrowed StarPilot `_pid_output_scale` (toggle), unwind helpers — all inside the `is_eps_modified` block.

**2D online auto-tuner** (`selfdrive/controls/lib/nrdr_tune_learner.py`): gain-scheduled persistent integrator; bilinear-interpolated additive FF trim per (speed, |angle|) cell; hard-clamped; slow; gated on quasi-steady + hands-off + **paramsd-converged** (so it doesn't fight the existing kinematic learner). Trim cap raised to 100%. Offline tools: `tune_learn_tool.py` (seed/view), `tune_attribute.py` (residual→culprit-term regression). Brett confirmed it's measurably improving drives.

**Speed-limit "only-at-the-sign" bug FIX** (`sunnypilot/.../speed_limit/speed_limit_resolver.py`): removed a broken `distance_since_fix` that mixed `time.monotonic()` (seconds-since-boot) with `unixTimestampMillis` → garbage → the ≤1000 m preemptive swap never fired. Replaced with `speedLimitAheadDistance`. (Sibling `gps_fix_age` gate has the same monotonic/unix bug — flagged, left as-is.) **Still pending:** the tunable "Pre-Adjust Lower Speed Limit" slider (convert hardcoded `LIMIT_AHEAD_PREEMPTIVE_DISTANCE = 1000.` to a param + UI, time-based preferred).

**C4 (mici) onroad UI** (`selfdrive/ui/mici/onroad/`, 60px right strip): real+set speed cluster top-left (real white, set green when engaged); driver-monitoring widget moved bottom-right; confidence ball pinned top-right of the camera feed; compact devUI in the right strip (`strip_dev_ui.py`, rows REAL/DESIRE/DIST/LSPD, gated on `DevUIInfo`). Speed hides during alerts and during set-speed changes. Most recent tweak: strip `TOP_OFFSET 40→28`, `ROW_SPACING 56→44` to lift the stack and stop LSPD clipping (iterate these two numbers on device).

**Honda cluster blink/flash feature** (`opendbc_repo/.../honda/carcontroller.py`, `hondacan.py`): `ACC_HUD` (0x30C) is the Nidec longitudinal command message, sent at 10 Hz. System flashes the cluster speed for 5 s when the set speed is system-"bumped"; blink shares a global-clock oscillator with `CruiseButtonSubMode` so they auto-sync; blink goes 2× faster (`phase_ms 1000→500`) in the final 5 s; system flash blinks ONLY the speed and takes priority. `NrdrCruiseButtonSubMode` default changed to **OFF** ("0") in both `params_keys.h` and the carcontroller.

**Clarity tune (historical; superseded):** The earlier "DOUBLED" four-breakpoint experiment documented here is no longer current. Dev-new now matches architecture's static Honda PID base on Accord, Civic, Civic Bosch, Civic Bosch Diesel, Clarity, CR-V 5G, and Insight: `kp = 0.03`, `ki = 0.01`, and `kf = 0.000012` at all speeds, with no feedforward schedule. UI P/I/F scales default to a neutral 100%. NBOX and out-of-scope Honda platforms retain their existing platform tunes.

**Sunnylink settings UI**: added StarPilot toggle + auto-tuner controls; swept ~53 verbose/clipping descriptions across 10 pages into short inline `description` + full `details` (modal). Pipeline: edit YAML in `sunnypilot/sunnylink/settings_ui_src/pages/*.yaml` → run **`python sunnypilot\sunnylink\tools\compile_settings_ui.py`** → commit both the pages dir and `settings_ui.json`. The web frontend is hosted (not in the repo); it clips long inline text and renders the `info` widget one-word-per-line — hence moving text to `details`.

## Device update (SSH)

```
cd /data/openpilot
git pull
git submodule update --init --recursive
git submodule status                 # leading space = matches recorded pointer
grep -n "0.036" opendbc_repo/opendbc/car/honda/interface.py   # proof the tune landed
```
`git submodule update` checks out the commit the **superproject recorded**, so the submodule pointer must be bumped + pushed in the main repo (not just the submodule branch). Pure-Python changes need only a restart/reboot; C++ (`params_keys.h`) needs scons.

## IN-FLIGHT: merging PRs #9 and #10 into `mvl-testing-07.15.2026`

Both PRs (guided EPS flasher tooling) were opened against `nrdr-nightly`. They **auto-closed** — not manually — because `build_prebuilt.sh` force-pushed the base branch out from under them; GitHub re-evaluates a PR whose base is force-pushed and closes it, attributing it to the account whose push triggered it (nrdr).

Fix underway: get the PRs off the prebuilt branch. Structural fix for the future = **change the repo's default branch to a source branch** (Settings → Branches) so forks/PRs share history and merge cleanly; ideally a stable-named `dev` as permanent default with dated snapshots cut off it.

Merge mechanics learned the hard way:
- `.patch` via unauthenticated `curl` returns a 43-byte stub (private repo) → don't use it.
- The PR branches share **unrelated history** with source (forked off a prebuilt tree), so a plain merge refuses, and `--allow-unrelated-histories` / UI-retarget would dump the entire compiled tree.
- **Do NOT cherry-pick a range** like `arc-nightly..pr-9` — it includes an `openpilot vX prebuilt` snapshot commit (`b6b96f0b3b`) that the flasher was committed on top of; cherry-picking that explodes tinygrad, overwrites submodules, and hits LFS "should have been pointers" errors.
- **Correct move: cherry-pick ONLY the real flasher commit by SHA.** For #9 that is **`337073dff9`** ("Add guided EPS flash helper and harden flasher exit paths"):
  ```
  git cherry-pick --abort            # if stuck mid-pick
  git cherry-pick 337073dff9
  git show --stat HEAD               # should show only eps_tools/ files
  git push origin mvl-testing-07.15.2026
  ```
  Fallback if it conflicts on eps-update.py/eps-diag.py: `git checkout 337073dff9 -- eps_tools/` then commit.
- **#10 not yet resolved:** need `git log --oneline pr-10 -8` to identify its real commit SHA(s) (one/two commits sitting on another `…prebuilt` snapshot) and cherry-pick those individually — same no-range rule.

Safety: after any abort run `git status`; the uncommitted **tune-doubling + strip-UI edits must survive** — do **not** `git reset --hard`.

## Open items

1. Resolve PR #10 cherry-pick (identify SHA[s], pick, push).
2. Change repo default branch off `nrdr-nightly` (stop the auto-close recurrence).
3. Speed-limit **pre-adjust slider** (param + UI; time-based).
4. Verify + deploy the Sunnylink description sweep (native compile the JSON, commit).
5. Optional: compact the device-written Car & Tune Info string in `nrdr_remoted`.
