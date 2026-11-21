# Upstream model catalog update — November 2026

Implemented in `bcce1996be`, pushed to `nrdr-development` and installed on the parked C4 on November 14. Cheddar remains selected; saved preferences are unchanged.

## Source and scope

Matches sunnypilot master [`b55c4be825`](https://github.com/sunnypilot/sunnypilot/tree/b55c4be825eb763b3abf7220f4c38248949f6d91/openpilot/sunnypilot/modeld_v2):

| Models | Catalog | Execution |
| --- | --- | --- |
| CH / Cheddar, plus 77 other small models | [v25](https://raw.githubusercontent.com/sunnypilot/sunnypilot-models/gh-pages/docs/driving_models_v25.json) | QCOM on C4/C3X; Cheddar's existing verified local rebuild remains preferred. |
| Flip Flop, Light Speed 2, plus 20 other big models | [Chestnut v28](https://raw.githubusercontent.com/sunnypilot/sunnypilot-models/gh-pages/docs/driving_models_chestnut_v28.json) | Supported external AMD/Chestnut hardware required; not standalone C4/C3X. |

The big catalog adds Mountain Dew, Mountain Dew v3, Train Track, Flip Flop, Light Speed, Light Speed v1.1, Light Speed 2 and Fidx Driving compared with v27. CH is Cheddar, not a separate model.

The artifacts use `SPTGPLN1`, despite their `.pkl` filenames. `plain_artifact.py` and its offline serializer are adapted from the upstream implementation, using the pinned tinygrad buffer/copy API. New short datatype names (`f16`, `f32`, etc.) resolve to the existing datatypes. Legacy portable models use upstream's host-writable GPU input buffers; old artifacts retain their previous input-memory path. Native models retain the existing separate camera warp and recurrent-state adapter, without requiring upstream's optional fused submission optimization.

The tinygrad ABI base remains `fe5d3169ba`, with a localized QCOM program-cache correction in `tinygrad/runtime/ops_qcom.py`. The approved [nrdr fork](https://github.com/nrdr/tinygrad/tree/nrdr-development) publishes this as `87846ccb3b`; the main repository pins that commit and its source hash. Existing pickle artifacts and driver-monitoring code remain in place; no broad dependency upgrade or recompile is included.

Existing selectors/downloads are reused. Same-model artifact repairs retain model identity, use private content-addressed filenames, and occur through the existing offroad mechanism. An identical artifact is not replaced just because its catalog compiler reference changed. No controller, personality, PTM calibration or saved preference changes are included.

## OP Model 10 V3 engagement failure

On installed `991cfb2`, routes `000001df--22e2636d19` and `000001e0--d82c7e7eac` contain 3,054 invalid camera-odometry samples. Localization then rejects inputs and raises `locationdTemporaryError` at engagement attempts. Raw IMU inputs were finite. The old selected artifact matched its catalog hash but also produced NaNs in isolated offroad execution, including with a strict pickle loader. Cheddar's verified rebuild produced finite outputs in the same environment.

The new catalog retains OPM10V3 identity `7d4c295c27bc3f72727c49ec73b98e45745b588d`, but replaces artifact `df76a9dd…` with portable artifact `1b199d18…`. Merely replacing the artifact did **not** fix the C4: the replacement also produced NaNs during its reference check.

The pinned QCOM runtime cached programs by binary bytes, omitting image shape and datatype. Identical binaries can require different texture descriptors. Changing that key to the full program makes the replacement OPM10V3 match its embedded policy and both camera-warp reference outputs. A focused regression fails under the original cache and passes under the correction. Upstream removed this binary-only cache in [tinygrad `c52b227c7b`](https://github.com/sunnypilot/tinygrad/commit/c52b227c7bebd924dee29de078c5571ce4a6a8a4); the local fix preserves the older runtime API rather than importing the intervening runtime rewrite. The exact failing path of the old pickle has not been independently retraced with the correction.

Full adapter execution also required the GPU-backed auxiliary inputs used by [upstream `compile_modeld.py`](https://github.com/sunnypilot/sunnypilot/blob/b55c4be825eb763b3abf7220f4c38248949f6d91/openpilot/sunnypilot/modeld_v2/compile_modeld.py). Without this, reference verification passed but runtime initialization failed when mapping CPU transform buffers. This behavior is enabled by the portable artifact's `input_devices` metadata; the old-model path is unchanged.

All model layouts now reject non-finite inference before parsing/publication, rather than applying that check only to big supercombo models. Portable loading rejects non-finite reference results, including matching NaNs, and unverified loads cannot populate the validated cache. This prevents invalid estimates reaching localization; it does not itself make a defective model usable or suppress an alert.

## Verification and remaining work

- 163 focused model tests and 24 subtests pass; eight native-dependent checks are skipped on Windows. Coverage includes actual Python-backend kernels, weights, copies, views, recurrent outputs, cache reload/invalidation, old chunked/pickle loading, artifact admission, selection migration, Sunnylink catalogs, host-written input visibility, hidden-state contracts and timing metadata. Deployment verification additionally passes 117 Wind Brake tests, 127 Honda tests and schema consistency. Three QCOM tests pass against the installed C4 checkout. Diff whitespace checks pass; Ruff is unavailable in the host runtime.
- The current parser accepts all 78 small and 22 big catalog entries. None of these current portable downloads uses a chunk manifest.
- Downloaded reference frames for OPM10V3, Cheddar, Flip Flop, Light Speed 2 and Fidx pass the unchanged output parser: finite plans `(1, 33, 15)` and poses `(1, 6)`. This validates the output interface, not device inference or driving performance.
- At the November 14 revision, Fidx's additional `fidx` input was zero-initialized. The [development timing-input port](#development-timing-inputs-and-experimental-curve-slowdown) supersedes that behavior for models declaring the input.
- Both portable OPM10V3 and Cheddar pass C4 reference verification, cache write/reload, and 110-frame runs through the actual model adapter/parser. All eight camera-odometry vector fields remain finite; messages were constructed but never published. OPM10V3's embedded C3X-size warp reference also passes on the C4 GPU; this is not physical C3X validation.
- Existing installed Cheddar produces byte-identical plan/pose sequences over 110 frames before and after the runtime correction. Its saved selection remains active.

Representative offroad timings, excluding the first ten frames:

| C4 model | Mean / p95 / maximum | Result |
| --- | --- | --- |
| Existing Cheddar, installed baseline | 47.78 / 55.24 / 61.36 ms | 110 finite frames |
| Existing Cheddar, candidate runtime | 47.16 / 52.71 / 58.02 ms | Same output digest as baseline |
| Portable OPM10V3, fresh load | 46.43 / 53.85 / 58.53 ms | 110 finite frames |
| Portable Cheddar, fresh load | 47.06 / 52.69 / 55.06 ms | 110 finite frames |

These are synthetic-frame, offroad measurements, not live-camera/onroad deadline certification. Some frames exceed the 50 ms interval, including the unchanged baseline. No scheduler, clocks, control tuning or timing thresholds were changed.

### Remaining verification

OPM10V3 still has a first-initialization repeatability discrepancy: the first 32-frame sequence in a process differs from a subsequent fresh load, while the subsequent fresh and cached loads match exactly. Observed maximum differences in the concatenated plan/pose arrays ranged from about 0.016 to 0.367, exceeding the reference-check tolerance; all values remained finite. This is **not established as a cache defect**. Zero-initializing scratch buffers and synchronizing input allocation did not resolve it; neither workaround was added. Trace the first differing inputs/intermediates before declaring OPM10V3 fully verified or recommending a driving test.

All 100 entries are registered, but not every artifact has been executed. The connected C4 reports no Chestnut accelerator. Actual AMD/Chestnut inference, physical C3X operation, and live engagement remain unverified. These require the corresponding hardware; model selection and driving tests remain user-controlled.

## Deployment verification

The C4 was fast-forwarded from `991cfb2` to `bcce1996be`, including opendbc `aaae8cfa3` and tinygrad `87846ccb3b`. The app manager/UI and Sunnylink were reloaded without a build or device reboot. Manager/device messages are valid, the UI and model manager are running, and Sunnylink pings resumed. The served schema admits Wind Brake on this pedal-equipped Clarity, and the installed catalogs contain 78 small / 22 big entries.

Installed Cheddar passed another 110-frame run: finite plan, pose and camera odometry; output digest `0d4baf84a523efebc5dd4df490c704ceca581a1bd3ff8ca3c85011f3b6539a00`, exactly matching the pre-update baseline. Mean / p95 / maximum were 43.08 / 45.01 / 56.37 ms under this offroad workload; this is not road validation.

Before/after hashes confirm 327 existing persistent keys unchanged, including the selected models and user preferences. Eight persistent bookkeeping/cache keys changed normally: daemon PID, the two model catalogs, boot count/log, Git commit/date and offroad uptime. Transient manager state was regenerated. No saved setting was manually written or toggled. Release branches and `release/build_prebuilt.sh` were untouched.

## Polaris Vega: November 18 desktop-only build, not admitted

The [publisher's Vega page](https://polaris.firestar.link/models/spz_polaris_vega) supplies the MIT-licensed source ONNX (SHA-256 `cfd9dbb518d3fdbae5f3eb1f64eeae9a8a9ea88526529038a71359de2a9cb021`) and a separate StarPilot QCOM artifact. The latter is not admitted by nrdr. Using development `a05e42cd6f`, the unmodified combined-model compiler built the source with `supercombo`, model size 512×256, camera 1344×760, derived frame skip 4, and desktop targets `CUDA:PTX;CPU:X86`. Policy and warp passed the compiler's own serialization/reload checks. The combined desktop artifact is 106,846,581 bytes, SHA-256 `2be68d401d0cbdee6f568259f95aed52528e3ecf13bab3e50650d745ab643d49`. It is **not a C4 binary**. This Windows host cannot execute nrdr's Qualcomm backend.

- **Loader:** the desktop build emits `input_devices={'warp':'CUDA'}` although its captured camera transforms and packed policy inputs reside on `NPY`. The legacy adapter treats the mere presence of that key as a request for GPU-backed auxiliary inputs. Stock adapter initialization failed when it tried to map CUDA memory for host writes. Passing GPU-resident auxiliary inputs directly to the captured warp and policy separately reproduced the input-device mismatches; passing their captured NPY layout worked. Omitting only the ambiguous marker on an **in-memory copy of this locally built artifact** allowed the existing adapter to initialize and run. No loader/admission change is approved; portable downloads really can require GPU-backed inputs.
- **Numerical comparison:** independently packed, padded synthetic NV12 buffers for both cameras with distinct integer translations; no road footage or borrowed camera pointers. Over 24 frames with identical reference-supplied feature histories, both camera warps matched the NumPy oracle byte-for-byte, all parsed outputs were finite, and peak differences vs CPU ONNX Runtime were 0.00381 m/s² lateral action and 0.000887 m/s² longitudinal action. Over a separate 144-frame test using the in-memory metadata correction, preloaded CUDA frame tensors and each implementation's own recurrent history, both warps still matched on every frame and all outputs were finite. Peak action differences were 0.00398 and 0.00195 m/s² respectively; 8/144 lateral actions exceeded a diagnostic comparison at `rtol=atol=0.001`. Across the entire raw tensor, 18.4% of values exceeded that comparison. This is **not** a C4 equivalence result or an approved tolerance; CUDA/ONNX precision, auxiliary input types and accumulation have not been isolated.
- **Loader fix (desktop-verified):** the as-built artifact already declares its auxiliary argument devices in the warp and policy call signatures. For marked bundles the adapter now keeps the transforms and packed policy inputs on the host when all three explicitly declare NPY. Portable programs without those capture details keep their previous device-backed layout; unmarked legacy programs keep their previous defaults. This is independent of model size. Repeating the independent-history test on the **unaltered** desktop artifact, without editing metadata in memory, produced the same 144-frame comparison report byte-for-byte. Added coverage for host and device captures, portable and incomplete signatures, and unmarked legacy bundles with and without the Chestnut environment setting.
- **Next:** build and verify Vega separately on a parked C4 using QCOM. Compare camera preprocessing, action, recurrent state, pose and plan against pinned reference inputs; the desktop numerical discrepancy is not resolved by this loader fix. No model selection, vehicle process, steer-ratio gate or PTM behavior changed. No lane or unwind performance claim follows from synthetic inputs.

## Polaris Vega: November 18 parked C4 bench

With the car off, the standalone adapter used the C4's own Qualcomm GPU, with no Chestnut,
live camera, vehicle publisher, selector write or change to the installed checkout. The C4
was on development `a05e42cd6f`, tinygrad `87846ccb3b`; the compiler and adapter under test
were staged from the working tree. Compared 144 deterministic synthetic frames to a separate
CPU ONNX Runtime reference (each runner feeding back its own features). Both camera warps
were also compared to independent NumPy outputs, not merely to the other runner.

The generic QCOM artifact (SHA-256 `70402e5ad9c28f0a0cc0e143f4fd692a13793a965099a23f1b5b147023b0fc29`)
reloaded and produced finite outputs; all 288 warps were byte-exact. Peak absolute action differences
were 0.00465 lateral and 0.00208 longitudinal m/s². The synchronized adapter call with preloaded
camera tensors measured 435.1 / 438.6 ms (median / p95 excluding frame zero), far over the 50 ms
model period. This was not the board's normal optimized build configuration.

Rebuilding the same ONNX with the comma-arm64 flags in `selfdrive/modeld/SConscript`
(`IMAGE=1 FLOAT16=1 NOLOCALS=1 JIT_BATCH_SIZE=0 OPENPILOT_HACKS=1`, on QCOM)
produced SHA-256 `f26652bb639f86b9d8520f3371b6df37f55af79809350b9e6235746e6d586b1d`.
The warmed synchronized adapter call fell to **40.0 / 41.1 ms** (median / p95, 143 timed frames);
policy alone was 32–33 ms. Both camera warps were again byte-exact on all frames and every parsed
output finite. Peak absolute differences vs the same reference increased to **0.01217 / 0.02179 m/s²**
(lateral / longitudinal action), exceeding the 0.001 diagnostic threshold in 125 / 135 of 144 frames.
Maximum absolute differences in the parsed plan, pose and recurrent arrays were 4.9030, 1.0659
and 0.01036 respectively; the plan and pose arrays combine components with different units.
This is not proof of numerical equivalence or of 20 Hz end-to-end performance in the driving stack.
No catalog entry or deployment. Before admission, compare identical recurrent inputs to separate
single-frame from accumulated differences, then check per-component outputs and full replay cadence
on time-aligned recorded frames. Retained isolated artifacts and logs: `/data/tmp/vega-bench.UxoC7F`
on the C4. Active bundle, SR mode and blend preference hashes were unchanged after both tests.

The local model-specific SR gate excludes Vega independently of its catalog family; it does not
disable optimized lane changes or change the saved global preference. Any future picker entry must
retain Vega's own identity rather than alias the CD210 bundle. These inference runs did not use a
steering controller. See [the Clarity's physical ratio check](ptm_testing_investigation.md#current-decision).

## Polaris Vega: saved-road replay, November 18 — not admitted

The parked C4 replayed the optimized artifact above on route `0000020d--9a6e742932`,
segment 30, encoded frames 120–839 (camera IDs 36122–36841). All 720 narrow/wide pairs
matched in sequence; speed 7.62–11.04 m/s, wheel angle −5.0° to +9.7°, no active lane changes.
This is a gentle 36-second clip, not an S-curve or closed-loop test. No vehicle controller
was started. The private replay had blend off; live Pop v2, SR and controller parameter
hashes were unchanged. Artifacts, analysis scripts and per-frame results are retained under
`../analysis/vega-road-2026-11-18` relative to the checkout.

**Numerics (unpaced, no skipped frames):** used saved calibration, exact-frame lateral action
times, Vega's zero smoothing override for longitudinal delay and identical QCOM-warped image bytes.
Compared C4 to CPU ONNX Runtime twice: CPU fed the recorded C4 feature history (cast to
the declared fp16 input), then CPU fed its own outputs. Both started from zero; histories
advanced at every frame. The parsed plan has one trajectory, not competing plan hypotheses.

| Absolute position difference at a 3-second forecast | Matched history | Independent histories |
|---|---:|---:|
| Lateral, p95 / max | 2.0 / 21.7 mm | 1.7 / 16.2 mm |
| Forward, p95 / max | 5.3 / 10.4 cm | 8.9 / 18.2 cm |
| Forward p95, first → last six seconds of footage | 5.3 → 6.9 cm | 5.9 → 16.7 cm |

No sustained lateral buildup in chronological windows. Lateral errors did widen with
*forecast horizon* (at 10 s, independent-history p95 1.05 cm, max 40.15 cm).
Recurrent differences contributed to the later forward-position increase, but it
was not monotonic over all six windows. This does not demonstrate unbounded drift.

**Paced full process:** ran the actual development model loop, installed parser, message filling
and private publishers, using the verified bench artifact and staged adapter. VisionIPC received
both padded camera streams at 20 Hz; a separate subscriber counted distinct published modelV2 IDs.
Recorded Honda parameters and vehicle/calibration messages were provided in the private namespace.
The initial setup attempt waited for missing CarParamsSP and produced no timing result. With that
record supplied, all counted model messages were valid with matching camera IDs and EOF timestamps.

| After first 20 input frames | Pass 1 (transfer overlapped) | Clean repeat |
|---|---:|---:|
| Distinct outputs / 700 inputs | 577 | 623 |
| Output Hz, first to last received | 17.17 | 17.81 |
| Output spacing p50 / p95 | 54.7 / 84.2 ms | 54.0 / 80.2 ms |
| Model execution p50 / p95 | 45.4 / 56.1 ms | 45.0 / 53.1 ms |
| Camera feed to subscriber receipt p50 / p95 | 89.0 / 130.4 ms | 87.2 / 127.2 ms |

Inputs averaged 20.000 Hz on both passes; clean feed interval p95 51.4 ms. Even excluding
the first 300 input frames, only 374/420 were published on the repeat. Only CPUs 0–3 were online
offroad, so the process used ordinary scheduling rather than the driving-time FIFO/core-7
configuration. No CPU was brought online. This **fails the parked replay cadence criterion**,
not a measurement of onroad throughput. Next: compare a known-good small model in precisely
this harness, then separate preprocessing, inference, postprocessing and publication. Repeat the
numerical comparison on turns and a longer, independent recording before considering the picker.

### Experimental Sunnylink entry for the C4

At owner request, expose **Polaris Vega (experimental, C4 only)** for personal evaluation.
This does not qualify it for general distribution or road use. The clean parked result remains
17.81 Hz; no same-harness Pop v2 comparison or sharp-curve validation has been performed.
The [publisher](https://polaris.firestar.link/models/spz_polaris_vega) also reports shoulder cutting on tight exits.

Only the exact optimized QCOM bytes above are listed, in the small-model picker on a C4 that
has the file installed. Sunnylink uses the existing device-local catalog; no server change,
publisher pickle, automatic download, auto-selection, CD210 alias or global SR setting change.
The runner checks the pinned artifact, camera and backend again when loading. A missing or
changed local file fails selection rather than fetching a substitute. The catalog uses
the replay's supercombo constants (`is_20hz: false` selects the metadata layout, **not** the camera rate),
non-MLSim path (generation 0 = unspecified for this trial), and zero smoothing overrides.
Vega is excluded from SR blend even if the saved preference is on for Pop v2.

On the test C4 the retained source is `/data/tmp/vega-road.3cT9gM/vega-replay.pkl`; the local
model filename is `/data/media/0/models/nrdr-polaris-vega-c4-f26652bb.pkl`.
Provision the exact verified file **offroad** before refreshing Sunnylink. No artifact is
distributed in Git. Clearing the inactive model cache can remove the entry; the retained
replay copy can be used to provision it again. Rollback is simply reselecting Pop v2 offroad.

### Development timing inputs and experimental curve slowdown

These are independent settings, read when the model or planner starts. They do not
change model selection, steer ratio, steering filters, or the restored-timing setting.

| Setting | Branch default | Effect |
| --- | --- | --- |
| `NrdrActionTimeCap` | Off | Caps each supplied `action_t` input (lateral and longitudinal) at 0.4 s. Does not change plan decoding, the camera rate, or legacy `lateral_control_params`. [Upstream #39401](https://github.com/commaai/openpilot/pull/39401) |
| `NrdrCurveSpeed` | Off | In the nrdr planner with openpilot longitudinal and Experimental Mode active, uses the model's predicted speed and yaw to lower the model acceleration candidate. MPC/braking/stop arbitration remains in place. Resets on pedal/override, invalid inputs, or disengagement. Independent MVL and stock-cruise paths are unchanged. [Upstream #39242](https://github.com/commaai/openpilot/pull/39242) |
| `NrdrModelFidx` | 3 | Supplies a 1–6 second path horizon only to a local runner with an actual `fidx` tensor. Not a new weight file, a JetLink protocol change, or a time offset for Vega. [Upstream experiment](https://github.com/commaai/openpilot/commit/3471915de772c645d60a563cc3c335b17da1fe0b) |

The curve port bounds both signs of bank before taking the square root. It only modifies the
model candidate: the −2 m/s² floor applies to **added curve braking**, not to stronger braking
already requested. The 2 m/s³ slew applies to the correction state, not to total vehicle jerk.
Disable the two boolean settings while parked/offroad to return to their previous behavior
at the next model/planner start. There is no dashboard toggle or change to fault reporting.

Offline check of the pre-port Vega outing `0000020e--22347bdc3d` (15 segments): all 16,925
lateral action horizons were 0.255–0.325 s; none exceeded 0.4 s. Feeding the **recorded model
acceleration** to the curve helper, no reduction was called for on the 337 frames matching
experimental longitudinal engagement, pedal/override and valid data in the recording.
Ignoring engagement/pedal gating as a counterfactual only, 181 of 13,084 moving frames with
valid roll/model data reduced the candidate by over 0.01 m/s² (largest reduction 0.92 m/s²).
This is a fixed-input helper replay, not final planner commands, closed-loop response, or a road test.
