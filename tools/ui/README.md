# Bounded C3X / C4 UI previews

## Verified GitHub galleries

[Run 42102783848](https://github.com/nrdr/openpilot/actions/runs/42102783848)
passed both native build/capture jobs on 2026-11-05 at `a81358ddd7`: **17 C3X
views and 15 C4 views**. Download either artifact, extract it, and open
`index.html`. The ZIP includes full-size screenshots, the source recording,
and a manifest identifying the exact revision and synthetic inputs.

GitHub had paused this fork's workflows despite its permissions API reporting
Actions enabled. The owner re-enabled them on the Actions page. The dedicated
workflow is now registered as **408596848**; matching UI pushes launch normally.
The earlier registration/host notes below describe the initial investigation,
not the current availability of GitHub previews. No Linux environment was
installed on the Windows PC.

This is an artifact-only, desktop capture companion to the existing UI tests. It
does not change or replace `test_raylib_ui.py`, the stock replay scripts, or the
existing `Create UI Report` job. No control processes, physical devices, cameras,
route downloads, deployment, or publishing are involved.

| Device | UI identity / layout | Native render size | Captures |
| --- | --- | --- | --- |
| C3X | `tici` / big `MainLayout` | 2160 × 1080 | 17 views, listed below |
| C4 | `mici` / `MiciMainLayout` | 536 × 240 | 15 views, listed below |

These are **real rendered UI pixels with synthetic replay messages**, not device
screenshots or driving validation. Onroad has no camera feed or model output;
the normal camera placeholder is expected. The gallery explicitly labels the
synthetic inputs and absent camera feed. This is not a pixel-baseline regression
comparison, exhaustive settings test, or navigation gesture test. Settings are
opened using existing native navigation methods, then their real containers are
scrolled to the requested control. No widget is reparented, rescaled, or invented.

## Actual native coverage and gaps

| Surface | Big / tici | Small / mici |
| --- | --- | --- |
| Offroad home and settings | Home + nrdr hub | Home + settings carousel |
| nrdr lateral | `LateralTuningLayout` hub | **Unsupported:** no wired mici lateral hub |
| nrdr longitudinal | `LongitudinalTuningLayout`, plus PCM row | Device's existing `PcmModeControl` and `LiveGasControl`; **not** the full panel |
| Engine braking / overshoot | Existing engine-braking toggle and overshoot row | Sixth/seventh Device controls; also opens the real overshoot selector without selecting a value |
| Steer ratio (SR) | `SteerRatioTuningLayout` | **Unsupported:** no native mici SR menu |
| Override | `OverrideTuningLayout` | **Unsupported:** no native mici override menu |
| Lane centering | Existing lateral subpanel | Existing Toggles lane-centering panel |
| Driver monitoring | Native Always-On DM toggle, scrolled into view | Native Always-On DM control, centered in carousel |
| Onroad | HUD, sidebar, personality, longitudinal, lane-centering and DM settings | HUD, settings carousel, personality, PCM, lane-centering and DM settings |

**Unsupported on both:** advanced nrdr DM reminder-timing tuning exists only in
`openpilot/nrdr/ui/sunnylink/pages/steering.yaml`, not either native settings tree.
Always-On DM captures must not be mistaken for that advanced menu. Sunnylink
web/account flows, live road/cabin cameras, model output, controller behavior,
EPS firmware capability and physical displays are not captured or validated.
The gallery and manifest repeat these gaps even when a capture job fails.

The isolated fixture identifies a synthetic Honda Civic/Nidec, enables the
openpilot-longitudinal capability, and reports no gas interceptor or EPS firmware.
This exposes the existing Honda-gated menus without bypassing their gates; options
requiring firmware or actual vehicle data remain unavailable. It seeds Star lane
centering and unlocks suggested/handcrafted tuning only in temporary preview Params.
It also marks optional first-run setup complete so the offline-map download
prompt does not cover the home screen. It does not request any maps.
It never starts a controller, sends CAN, clicks a tuning action, or changes a real
vehicle setting. Onroad means ignition-on, disengaged synthetic UI state; its
settings captures retain native restrictions. No special floating tuning menu
exists in this checkout: the onroad settings views use the same real settings tree.
Engine-braking and overshoot values are checked unchanged at every checkpoint;
the compact selector is opened through the existing control's registered callback.
The first five compact longitudinal-control indices are unchanged.

## Local capture (Linux PC / WSL2 Ubuntu 24.04)

From a Linux checkout of this repository, use the same setup/build as the stock
UI report job. Setup downloads dependencies/submodules/LFS assets and configures
the PC development environment; it is not needed again for an already-built tree.
Do not run this setup against a shared Windows checkout. For WSL, use a checkout
in the Linux filesystem to preserve native builds and symlinks.

```sh
./tools/op.sh setup
source .venv/bin/activate
sudo apt-get update
sudo apt-get install -y --no-install-recommends libgles2 libegl1 ffmpeg
scons --minimal -j2
PATH="/usr/bin:$PATH" "$PWD/.venv/bin/python" tools/ui/capture_preview.py --device all --output /tmp/nrdr-ui-preview
```

Use `--device tici` or `--device mici` to capture one device. Output must be a new
or empty directory: existing reports are deliberately never overwritten. Each
device runs in a separate process with a fresh `OpenpilotPrefix` for parameters
and messaging. Only `HardwarePc.get_device_type()` is overridden inside that
process, before UI imports; the PC backend stays active. `/AGNOS` devices are
rejected. No normal user/device parameters are changed.

`BIG`, `SCALE`, the headless backend, recording options, and sunnypilot UI mode
are explicitly set, so inherited shell settings cannot accidentally capture a
scaled C4 as a C3X. The existing `replay.run_replay`, `setup_state`, `Script` and
`send_onroad` are reused. The stock `tizi` replay variant name is just the shared
big-layout selector; the hardware identity here is **tici**, not tizi or pc.
Prime account polling is disabled for the test dongle; no real account is used.

The short script opens real settings widgets, checks ignition/nav-stack/viewport
state, and gives C4's actual delayed onroad transition time to finish. It records
under 30 seconds at 60 FPS per device (23.3s tici / about 21.3s mici). The default
replay wall-time limit is 180 seconds per device (`--timeout 1..600`); probing is
capped at 60 seconds and a single batched extraction at 120 seconds. Adding menus
does not add repeated full video decodes. Timeout terminates the worker and its
encoder process group.

Open the resulting `index.html` directly in a PC browser (including Windows).
No web server or internet access is needed to browse the extracted report:

- `<device>/<scenario>.png`: full-size captures, e.g. `steer-ratio.png` (tici),
  `longitudinal-pcm.png`, `onroad-lane-centering.png`. See `SCENARIOS` in
  `preview_scenarios.py` for the complete bounded list.
- `<device>/replay.mp4`: short source recording, useful for transitions.
- `<device>/capture.log`, `checkpoints.json`: runner diagnostics and state checks.
- `manifest.json`: commit, dirty-tree flag, host, device/layout/widget identities,
  exact frame numbers, dimensions, PNG SHA-256 hashes, fixture and unsupported surfaces.

Dimensions and decoded video frame count must match the asserted checkpoints
before any screenshot is accepted. Failure returns nonzero and writes a FAILED
gallery entry, not a stand-in image. Both devices are attempted independently.
Missing host prerequisites fail before capture; no gallery is fabricated then.
This tool does not generate placeholder screenshots.

## GitHub Actions

`nrdr-ui-preview.yaml` adds a dedicated **nrdr UI previews** workflow:

- Manual `workflow_dispatch`, plus `pull_request` limited to listed UI/tooling
  paths. A requested exception permits `push` **only to `nrdr-development` and
  only for the identical UI/tooling paths**. Generic commits and pushes to
  `nrdr-clean` do not trigger it. No `pull_request_target` or broad test run.
- Two Ubuntu jobs: C3X/tici and C4/mici, at most two concurrent captures. Superseded
  runs are cancelled; each job is capped at 35 minutes, including setup/build.
  SCons `--minimal` omits test/tool binaries; no full test suite is invoked.
- Read-only repository permissions, no saved checkout credentials, secrets,
  PR comments, artifact branch pushes, Pages publication, or remote device work.
- Seven-day downloadable artifacts containing the gallery and diagnostics. Extract
  the ZIP and open `index.html`; GitHub does not serve artifact HTML as a website.

The default branch is `nrdr-clean`. After the first preview push (`c9e300d626`),
GitHub reported Actions enabled but no registered preview workflow, checks or
runs; direct dispatch returned 404. The narrow push trigger remains unchanged,
but a registered launcher also provides an explicit fallback without modifying
the default branch or enabling broad CI.

### Registered, opt-in preview launcher

`nrdr-ui-content.yaml` is registered as workflow **367484810**, state `active`
(API verified 2026-11-05). Its `workflow_dispatch` file exists on
`nrdr-development`, but authenticated reads of both that file and the workflows
directory on `nrdr-clean` return 404. Registration is therefore historical, not
proof of a workflow file on the current default branch. This fallback must be
verified by an accepted dispatch and a matching run; it is not a guaranteed fix
for GitHub's registration/event handling. After the launcher patch is pushed to
`nrdr-development`, try that registered ID with `preview_only=true`:

```sh
gh workflow run 367484810 --repo nrdr/openpilot --ref nrdr-development -f preview_only=true
```

The equivalent API request is `POST /repos/nrdr/openpilot/actions/workflows/367484810/dispatches`
with JSON `{"ref":"nrdr-development","inputs":{"preview_only":true}}`.
Before dispatch, verify the branch HEAD is the intended reviewed push SHA. After
dispatch, verify the run's `head_sha` matches it and follow both capture jobs to
completion. Do not also dispatch the dedicated workflow if its matching push run
is already capturing that SHA.
If GitHub rejects the registered-ID dispatch, report the exact response and stop;
do not change the default branch or repository-wide Actions settings to work
around it without separate authorization.

The boolean input defaults to **false**: normal manual runs and the existing
path-filtered PR runs keep the content test job and its steps unchanged. Only a
manual dispatch with `preview_only=true` skips that job and calls the dedicated
`nrdr-ui-preview.yaml` via `workflow_call`. The local reusable-workflow reference
uses the caller's same commit; it does not render default-branch code. The caller
and callee have read-only repository permissions, pass no secrets, and reuse the
same two-job native-build/capture matrix, limits, and gallery artifacts. No new
push trigger is added to the content workflow, and its PR filters are unchanged.

The first Actions run must be checked through completion and its artifacts
inspected before claiming actual captures. This patch does not itself dispatch,
commit, push or pretend that a first capture has completed.

At the inspected revision, `tools/op.sh setup` initializes submodules before
dependency sync; it does **not** restore or replace `.gitmodules`. The workflow
requires `.gitmodules` to exist, checks it is unchanged afterwards, and rejects
missing/conflicted/off-pin submodule checkouts. It explicitly appends the actual
`$GITHUB_WORKSPACE/.venv/bin` to `$GITHUB_PATH`, verifies Python/SCons in a later
step, checks Python 3.12 and `sys.prefix`, and uses absolute venv executables for
build/capture. Sourcing activate in the setup child shell is not relied upon.
All workflow commands run from the checkout root: `tools/op.sh` is a tracked
executable (Git mode `100755`), not `openpilot/tools/op.sh`. `openpilot/tools`
is a separate tracked directory, not a symlink to root `tools`.

The existing upstream `ui_preview.yaml` publisher remains disabled and untouched.
The existing non-UI workflows retain their prior triggers; this patch does not
attempt to change broader repository CI policy. Nothing dispatches a workflow
automatically from the local capture command.

## Portable checks and native limits

```sh
python3 -B -m unittest discover -s tools/ui/tests -v
python3 -m ruff check tools/ui
```

The unit tests need only the standard library and exercise orchestration,
failure handling, environment isolation, frame selection and gallery output.
If ffmpeg/ffprobe are available, an additional codec integration test extracts
frames from a temporary test-pattern video, never passed off as UI captures.
They do **not** prove rendering works. Native capture additionally needs Python
3.12, the repository's `pyray`/Raylib package, EGL/GLES, ffmpeg/ffprobe, assets and
built native imports such as `libparams_c` and msgq/visionipc. Native Windows
capture is unsupported. Missing dependencies are reported in `capture.log` and
fail the job; successful unit tests must not be described as successful captures.

### Host audit on 2026-11-05 (no actual capture)

On the shared Windows host, `wsl --list --verbose` explicitly reported
"Windows Subsystem for Linux has no installed distributions", and
`wsl -d Ubuntu --exec /bin/true` reported "There is no distribution with the
supplied name." The per-user WSL registry has no distribution registration.
WSL2 itself is installed (kernel 5.10.102.1), but Ubuntu is not available to this
user/session. Installing a distribution/system runtime was not attempted.

Concrete missing prerequisites in this checkout:

- A registered Linux/Ubuntu distribution and Linux checkout/build environment.
- `.venv/bin/python` (required Python 3.12); Windows Python is 3.13.14.
- Python `pyray` and `capnp`; compiled `openpilot/common/libparams_c.so` and msgq/visionipc.
- Initialized msgq, panda, rednose, teleoprtc, tinygrad and neural-network-data
  submodules (`git submodule status` marks them `-`). opendbc is present but belongs
  to the concurrent parent work and was not changed.
- EGL/GLES and Linux ffmpeg must be verified/installed in Ubuntu after it exists;
  the available Windows ffmpeg/ffprobe only validate the portable extraction test.

These Windows-host limitations do not prevent the successful GitHub-hosted
Linux captures linked at the top of this page.

## Official machinery inspected

Inspected on 2026-11-05; links pin the exact upstream revisions, not moving branches:

- [Sunnypilot's Create UI Report job](https://github.com/sunnypilot/sunnypilot/blob/932ff06d9316e4351d6b6b9f1dd422d5b639badf/.github/workflows/tests.yaml)
  uses repository setup, SCons, `RAYLIB_BACKEND=headless`, and both replay layouts.
- [Sunnypilot's replay runner](https://github.com/sunnypilot/sunnypilot/blob/932ff06d9316e4351d6b6b9f1dd422d5b639badf/openpilot/selfdrive/ui/tests/diff/replay.py)
  matches this checkout's runner and is reused without modifying stock tests.
- [comma's current replay runner](https://github.com/commaai/openpilot/blob/4b20c34e51789b244d4264f47feb11011aa53cbb/openpilot/selfdrive/ui/tests/diff/replay.py)
  has the same event-loop shape but uses `raylib_nb`; that incompatible binding
  is not copied into this Sunnypilot-based checkout.
