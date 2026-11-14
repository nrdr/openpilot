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
- Fidx's additional `fidx` input remains zero-initialized, matching the inspected upstream runner; no model-specific semantics have been invented.
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
