# Bare firmware-controller candidate

This is stock comma openpilot at `35e78a9d9518855ec0dacec919e719624a28131f`
with a small NRDR lateral package, not a SunnyPilot runtime. The stock model,
planner, longitudinal controller, driver monitoring, actuation gates and Honda
output rate limits remain in place. The old bare PID tuning/filter has been
removed. No firmware flasher or live car-yaw loop is included.

Math and geometry come unchanged from development
`e1d7156b5d25ee38f24f63a4a04b125675448d39`; `PORT_MANIFEST.json` pins the
individual source blobs. Bare's wrapper uses the stock LatControl API, the
unmodified stock steeringPressed signal, and no SunnyPilot services or schemas.
The copied profile document describes the development port; the bare-specific
admission and settings rules below take precedence here.

## Admission and settings

The default is stock control (`NrdrLateralController=0`). Stock/unmodified cars
keep their stock controllers and geometry. Unknown modified EPS firmware stays
dashcam-only, as in upstream. A supported modified family still cannot actuate
until the controller is selected and `NrdrFirmwareImage` separately acknowledges
the actual flashed build. That setting records a human confirmation; it does not
verify flash contents. Family strings alone cannot distinguish old/new images.

| Exact car / reported EPS family | Required image acknowledgement |
| --- | --- |
| HONDA_CLARITY / 39990-TRW-A020 | `clarity-a020-pminus5-tracker3200-norm1650` |
| HONDA_CIVIC_BOSCH / 39990-TBA-C020 | `civic-c020-targetmapd-tracker4500-norm1650` |
| HONDA_CIVIC / 39990-TEG-A010 | `civic-teg-20261016b-04147917` |
| HONDA_INSIGHT / 39990-TXM-A040 | `insight-txm-20261016b-7ba37432` |

TEG requires the corrected `20261016b` RWD whose SHA-256 begins `04147917`;
Insight requires the corrected `20261016b` RWD beginning `7ba37432`. Do not
substitute the older image with the same version string. No generic Honda,
diesel Civic, C120, A030, CR-V or cross-car fallback is admitted.

The native C3/C4 Toggles screen exposes Firmware Controller and Steer Ratio,
enabled only offroad for the acknowledged supported family. Configuration is
latched at process startup for the next drive; no frame reads Params. The
initial image acknowledgement is an explicit setup step, not an automatic
device migration. This candidate does not set it on anyone's device.

Steer-ratio choices retain the development values: 0 Manual, 1 Comma (default),
2 Measured, 3 Firmware. Missing measured evidence falls back to the real Comma
learner. Invalid transient learner values hold the last valid ratio. Shared
manual endpoints and optional hybrid A/B settings are preserved in the bare
parameter registry, with the same 5-degree invertible mapping and rejection
latch. Both measured curvature and desired angle use the same frame selection.
There are no PIF gains or Device Yaw Correction on this branch.

Optimized Lane Changes defaults on and suppresses the firmware feedforward,
including modeled EPS damping, in starting/finishing states, then rejoins only
after tracking error permits. No extra rate damping or torque/PIF blend is added.

## Timing and validation boundary

Clarity and Insight retain the source's measured prediction schedule. C020 and
TEG retain stock live prediction delay, not an invented Clarity schedule. The
command-history delay stays separate: Clarity's saved .145/.025-second endpoints,
Civic/Insight's fixed .175/.025 endpoints, fading between 10 and 15 m/s. The
development port's 25 ms compensation is retained, but these source calibrations
are model-dependent: matching them does not validate stock comma's driving model.
TEG remains provisional. Do not treat host tests as closed-loop road validation.

The owner's October 17 TEG drive analysis is preliminary evidence only: firmware
geometry, live delay .360-.379 s, logged model horizon .435-.454 s; model action
matched extraction at that horizon. On curvy roads, changing-curvature alignment
was about .23 s publish-to-raw gyro and .27 s publish-to-nominal CAN yaw, with
about .054 s publish age. Fused DeviceMotion yaw lagged raw gyro by about .07 s.
Raw CAN yaw had a standstill zero near 512; its scale remains unvalidated. The
earlier apparent sign mismatch was an analysis-convention error: raw CAN yaw and
calibrated device-frame yaw are both clockwise-positive (positive model curvature
was a right turn in the road-camera footage). Clarity's yaw_rate.py also describes
raw CAN as clockwise-positive; carState.yawRate separately negates it into its own
convention. There is no proven Civic-versus-Clarity sign reversal. These
observations do not validate applying Clarity's calibration to Civic and are not
substituted into this candidate's timing, gain, geometry or yaw calibration. No
Civic live-yaw feedback is enabled.

## Isolated native validation

Do not run the installed launcher or restart services to test this candidate.
Build in a separate checkout with its own submodule sources and output files.
Never mix its new mass-normalized CarParams/log schema with installed development
opendbc or generated schema bindings.

Pinned dependencies:

- opendbc: `f821d62a4b044933bdbf102f08e3b2d1d3c70f71`, based on comma `b3bd79a659`.
- msgq: `0e266c1dbcf7328beee3e57b4a8688555387c877`.
- Panda: `a59195163c32a3a375ea6c86715dc08fd0984c1b`.
- tinygrad: `02e698160eed1751738212144a7ea2cfb160b3f1`.
- rednose: `8671c17c3a4cdc4be5df07a068039e2da5b94eaa`.
- teleoprtc: `1aa8fc433bef1519a95c0700c96258c3be6dfb34`.

The existing bare Clarity brake/safety encoding is retained while syncing the
new upstream safety APIs. No lateral safety constant, torque limit or override
threshold was raised. TEG's existing 3840-count bare transport is preserved only
for its exact modified family; stock Civic retains comma's 2560-count transport.

For native tests, first build the candidate's own Params library, then invoke
pytest directly (not the Windows-only run_host adapter):

```
python -m SCons -j1 --minimal --ccflags=-g0 openpilot/common/libparams_c.so
python -m pytest -q -p no:cacheprovider --rootdir=. openpilot/nrdr/tests opendbc_repo/opendbc/car/honda/tests/test_honda.py opendbc_repo/opendbc/car/tests/test_vehicle_model.py
python -m SCons -j1 --minimal --ccflags=-g0
```

Use the C4 venv Python with its bin directory on PATH and only candidate
submodule paths on PYTHONPATH. Pure pytest dependencies can be isolated in the
candidate if absent from the venv. Compile/test only; do not flash the Panda,
launch openpilot, alter device settings or promote the candidate as part of this
check. Run native Honda safety regression tests as well before promotion.

Stock build inputs downloaded and SHA-256 checked on the host:

- driving ONNX: 60,918,562 bytes, `65a08adc31d5c456219687d99b7bf5e44d61dae2d49ea67850e76105c7248cce`.
- DM ONNX: 7,844,499 bytes, `dee5a294e8afaacc9295ac5d100e00733ecac278e79264b96331e40a3ede1b04`.

Create source archives with LFS filters disabled (`-c filter.lfs.process= -c
filter.lfs.required=false`) so they contain pointers rather than downloading the
optional 800 MB model. Add the two actual working-tree model inputs separately
to a build bundle. All submodule source checkouts total roughly 57 MB before
build outputs. Model inputs are about 69 MB. The optional Chestnut precompiled
model is an additional 800 MB and is not needed to compile the small-model C4
path. A source-only native test bundle needs neither model input. A fresh full
build still needs measured free-space monitoring: these input sizes alone do
not prove its peak build/temp footprint fits the device's 8.9 GB free space.

Local host has WSL installed but no Linux distribution, no Docker, and no native
Linux/ARM compiler. Python compilation, schema loading and host tests are not a
native C4 build.

On October 17, source `0bacb8e950766211db93953bd1d32883288d7a43` with the opendbc
pin above passed a full native C4 SCons build in an isolated checkout, including
the small driving/DM models, camera warps, solvers, pandad and Panda binaries.
Native regressions: 513 passed, 29 subtests passed, 248 skipped. The skips were
abstract safety bases or unsupported regen/second-speed cases; all 25 concrete
Clarity hybrid safety checks ran. Installed source and 199 saved settings were
verified unchanged. No firmware was flashed and bare was not installed or driven.
These are compile/unit/model-compiler checks, not closed-loop validation. The
optional Chestnut model and native UI launch were not exercised. Later changes
to this paragraph only record that result; the tested runtime remains unchanged.
