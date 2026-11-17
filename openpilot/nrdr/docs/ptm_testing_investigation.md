# Clarity PTM Testing investigation

## Current decision

November 16, 2026: measurement-only experiment, **ready for data collection, not a demonstrated steering improvement**. Runtime commit `d0297d254b23a1ad52aa7dc7ffbfcf0d308a1fb3` is published on `nrdr-development` and installed on the parked C4. Testing ID 2 is selected. Normal PTM's wrapper/core, final filter, safety enforcement, driver override and model/geometry settings are unchanged. No release builds or firmware flashes were performed.

The standing workflow is in the repository's `AGENTS.md`. Brake fault reading/clearing remains a separate deferred task; this investigation neither clears nor validates those faults.

## What the saved drives establish

Saved timing-On `000001ef--83987233d8` and timing-Off `000001f0--42a86d202f` used OPM10V3. The installed model is now Pop v2; new data is a separate baseline, not a matched model comparison. All six raw segments were retained and hashed in the workspace analysis directory. Recorded source trees were dirty; a commit name alone does not prove the exact historical runtime.

The pipeline is model plan/action, target smoothing and 20-to-100 Hz ramp, curvature bounds, selected variable-ratio/model-blended geometry, desired-angle slew, firmware-inversion feedforward plus angle-error P/I, pre-filter clamp, final filter, downstream override/optional limiter, E4, EPS R5/R6/internal output, wheel motion and vehicle yaw. The host's normalized command is **not direct motor torque**. The EPS also applies rate feedback internally.

PTM's feedback is steering angle. CAN yaw is decoded and logged, and the calibration tools use it, but it does not replace the angle-error term in this controller. The selected rack map, slip factor, wheelbase, offset and roll still affect target geometry. Device-motion yaw also enters the learned vehicle-parameter path; it is a different signal from CAN yaw.

### Slowing entry is different from unwind

During 116.8–117.9 s, the target is still turning inward but its rate falls. The wheel catches up and then exceeds that target; this is not yet outward motion. At 117.898 s the target is 247.88 degrees and the wheel 261.10 degrees, an excess of 13.22 degrees. The instantaneous raw FF demand is about .515, filtered FF .644, scaled P -.339, I +.012, pre-final sum .317, and final output .413. Both FF and final filtering retain more inward demand than their instantaneous inputs. I is not the dominant stored-demand term there.

The model's renewed bump first appears at about 118.075 s, after overrun has begun. It exists in the published model plan; the audited interpolation does not invent it. This timing does not prove the model reacted to the preceding error. Target angle peaks later, near 118.281 s. Wheel outward motion starts before E4/R5 sign reversal, so command zero crossing is not a physical unwind-onset measurement.

### Competing explanations

| Hypothesis | Current evidence | Next discriminating observation |
| --- | --- | --- |
| FF/rate/final-filter memory sustains demand | Directly reproduced; unwind-only gate is inactive in the earlier slowing-entry interval | Exact state replay and matched entry/release residuals; reject a candidate if retained demand falls but catch-up or subsequent-turn demand grows |
| I/limiter interaction changes history | Large I windup is not the main early term, but the host's new-command/older-output mismatch frequently freezes I | Compare logged passed/next flags, consumed publication IDs and operands; reconstruct every I update before changing this mechanism |
| FF cap or downstream rejection causes catch-up | 28 FF-cap samples, one pre-final clip in the early interval; no observed E4 rejection/attenuation in focused windows; lifting FF cap increases earlier demand | Preserve complete CAN/EPS telemetry; distinguish host clipping, transport submission and EPS/motor response |
| Geometry/yaw calibration is wrong | Well-covered 9–15 m/s rack slopes are close to 1; low-speed/high-angle coverage is inadequate; yaw fits disagree with the inherited right correction | Independent bilateral, multi-speed data and held-out yaw/geometry fits; do not change rack ratio to repair an angle-tracking error |
| Target timing or physical EPS/column dynamics dominate | No large model-frame outage or target interpolation overshoot; inverse FF is steady-state, not a validated dynamic vehicle model | Check exact input ages, measured E4-to-wheel and wheel-to-yaw response in repeated events, separately from target smoothing |

All 639 audited E4 packets in focused entry/unwind windows had matching full-payload Panda returns. That means FIFO submission at the audited stage, not proof of wire ACK or per-command EPS acceptance. Increasing safety-block counters corresponded to 0x35E, not steering. R5 response independently supports prompt processing; physical load/response uncertainty remains. Later 119.2–119.8 s has sustained pre-final clipping and R6 at its rail, unlike the earlier interval; neither alone proves motor-current saturation.

## Full-state replay changes the candidate decision

Replay runs continuously from inactive/reset, recomputing admission, FF, I, filters and reconstructed command-age mismatch; it does not reseed each interesting turn. Primary-window baseline error is at most .0345 E4 count; qualified entry error is at most .8447 count. Whole-route error is not exact (maximum 1.2879 counts). Unlogged subscription timing is tested with alternate alignments, not claimed as known.

The prior frozen-P/I result did not show stronger qualified entry for unwind100. With dynamic mismatch/I updates, **645 of the same 1,824 entry frames become stronger**, including 432 before the known intervention window. At 112.689 s the extra demand is about 18.2 E4 counts, explained by retained I, not a new FF spike. At the first divergence, 36.666 s, the reconstructed mismatch moves from .0099497 to .0103226 across the .01 freeze threshold. Holding the freeze sequence fixed removes the candidate's I difference and those stronger entry frames.

Release100 similarly strengthens 578 entry frames. Removing I freezing adds five qualified clipping frames; it is an attribution diagnostic, not a proposed fix. Unscaled P in anti-windup versus scaled P in the actual sum is another real interaction, but did not cause the primary interval's single clip: I was already frozen there.

The approximately 20 ms earlier negative command is about two 100 Hz updates, conditional on the crossing definition. One observed early control interval was 21.825 ms. Eight qualifying contrasting episodes across both recordings include both directions and low/medium speeds; stage-only advances range approximately 9–207 ms, with the largest near zero and threshold-sensitive. No eligible data above 50 mph supports a high-speed conclusion. The 5–8 Hz command RMS change is a command-content proxy, not measured comfort or stability. No candidate is promoted from this replay.

## Upstream methods and local quantitative runs

Pinned upstream tip: [b110c9f1529a](https://github.com/Biscuit-Labs/openpilot/tree/b110c9f1529adad07b3b6302b41e5628e12a36a0), compared with integrated donor `45e5b91fae934e4f423ee39055efb84d2150c575`. The audited Clarity wrapper/core, rack map, controller documentation and seven analysis tools have identical blobs. Calibration-file changes concern RDX required-firmware metadata, not a new Clarity tune.

Relevant inspected precedents include [online yaw-trim removal](https://github.com/Biscuit-Labs/openpilot/commit/626e1cbf5f2edfcbb71e7afc3fe378c6a13c7aa4), [prediction-schedule reversal](https://github.com/Biscuit-Labs/openpilot/commit/4f0b8670723f68746b15d4445bd1bcea43b1a2ee), [smoothing restoration](https://github.com/Biscuit-Labs/openpilot/commit/ba85691cf602912bff933dec26427f1def7fb8a4), and [command-delay accounting correction](https://github.com/Biscuit-Labs/openpilot/commit/b4304398aff5cc2777a05c789b2d6efcd4ba2e18). Diffs establish what changed, not universal road improvement. Increasing nominal plan-source command delay is not useful here: it ramps to zero in established plan operation.

Upstream's newer [override-hysteresis change](https://github.com/Biscuit-Labs/openpilot/commit/8aa76640746af441ba72774aa6b761f24e543787) moves press ownership into carState, uses a .6 release fraction for .1 s, removes the co-direction .28 s hold and adds opt-in soft cutting. Its reported press-chatter results are a separate hypothesis for override/recovery, not an explanation of our unpressed primary window. Those changes were **not ported**; nrdr override protections remain unchanged.

| Local tool | Question and actual result | Important restriction |
| --- | --- | --- |
| `eps_report` | Separate physical map, wheel tracking and delivery; Off 9–15 m/s map slopes 1.004 near center and .998 at 20–90 degrees | No qualifying low-speed cells validate this sharp event; report reference is shipped rack, not runtime model-blend reconstruction |
| `eps_plan_timing` | Off entry 130/exit 108 selected frames, below 150 minimum; no phase estimate | All-turn -.22 s fit excludes the 4.6–4.9 m/s primary event and is not actuator delay |
| `eps_fit_yaw_scale` | Per-route .2489/.2477 deg/s/count; pooled .2484 with right correction -.015 versus inherited .246/+.24 | Overlapping GPS windows are correlated; preserve inherited calibration pending independent holdout |
| `eps_fit_rack_map` | Correctly refused 183 eligible seconds, below 300 required | Requires calibrated yaw, known Table A, both directions/speeds and timing sensitivity checks |
| `eps_fit_column_load --source clarity` | Fitted/shipped route-held-out R² .923/.892 and .928/.891 | Internal-output units, correlated terms and pooled lag selection; improved fit does not establish improved closed-loop response |
| `tune_trace`, `tune_attribute` | Ranked angle-error events and coverage from raw logs | Generic advice is not a PTM-inversion tuning recipe; trace “RMS” is demeaned RMS |

Yaw, report, plan, rack and load calculations were actually executed. Host import adapters only supplied log decoding or the exact Clarity calibration lookup; fitting algorithms were unchanged. `eps_live_row_fit` supports different firmware telemetry and was not applied to Clarity. The upstream closed-loop simulator is not a ready substitute: it disables the final filter, omits limiter/driver behavior, uses assumed inertia/delays and prints higher-speed comparisons. Adaptation would first require held-out measured-command-to-wheel validation at the relevant low speeds.

Practical order, inferred from tool dependencies: verify firmware/command map; verify time/sign/yaw calibration; validate rack geometry across speed/direction; fit independent internal-output load residuals; measure target timing; replay exact controller state; then evaluate one justified parameter or logic change. Existing rate-filter, lead, FF-filter, friction/load and P/I knobs precede adding a new gate, but none should be selected from pooled fit score alone.

Exact commands, outputs, source paths and limitations are retained in workspace `analysis/clarity-timing-ab-2026-11-16/`: `upstream-methods-audit.txt`, `local-tool-yaw-audit.txt`, `full_core_replay_poincare.txt/.json/.py`, `root-cause-events.json`, `downstream-eps-audit.txt/.json`, and `telemetry_core_audit_poincare.json/.py`. These private raw-data artifacts are not uploaded into the source repository.

## Measurement contract and installed configuration

`controlsState.lateralControlState.pidState.ptmTesting` is present only in Testing. Version 1 contains Float64 consumed inputs and pre/post core state, effective/raw press, recovery state, passed limiter flag, observed wrapper interval, model identity, exact consumed carState/carOutput/vehicleParameters/model publication IDs, and the existing mismatch operands/next flag. Inactive frames explicitly indicate no core update. `modelValid` denotes presence, not freshness/health.

Pin the source to derive bleed/reset/freeze, candidate I, anti-windup bounds, scaled-P sum and filter/clamp attribution offline. The trace does not claim the unslewed geometry local or originating carControl identity of carOutput, nor sensor acquisition time or a hardware ACK. Those limitations remain distinct from the now-directly observed core decisions.

Verified installed settings: controller 2 resolves to `LatControlPtmTesting` using persistent Clarity parameters and A020 calibration; Pop v2 (`PMV2`) retained; ratio mode 3/PTM Auto and old-model blend on; Honda delta limiter off; recovery 1.0 s; rate filter .10 s, FF filter .15 s, final taus .07/.05/.01 s. Timing Restoration remains permanently off. Do not enable the optional delta limiter for this comparison: the existing provider suppresses it for ID 1 but not ID 2.

Relevant unchanged submodules: opendbc `5320fe2df0d93a594e079d4f3669e45087f838f0`, Panda `4230530f5ec4c7f11971f868ae9930b3547346eb`, msgq `e7396e76dadbb49e374d4b664ff6bbb43a39bcb0`, tinygrad `87846ccb3b4c84810acf756120ae99359d915b16`. The EPS version string is not a flashed-image checksum.

Verification: 142 host tests pass/26 native skips; all 168 focused tests pass natively. An additional unchanged legacy wrapper suite gives 162 passes/17 failures, reproduced with the saved baseline wrapper loaded in memory and byte-identical core/timing/geometry/test files. Do not report the entire legacy suite green. Independent serialized-state audit covers 6,500 cases/12 calibrations plus a zero-I-scale probe. Native 1,800-frame output/target parity passes. Wrapper plus serialization median .642 ms normal versus .783 ms Testing; p99 .824 versus 1.049 ms; about 440 extra serialized bytes/frame (44 kB/s at 100 Hz). This is not full publisher/I/O or road-deadline validation.

Before selection, all 375 stored keys were hashed. Only controller selection and its two generated controller/tuning reports changed beyond ordinary ping/model-sync timestamps and uptime. Model/settings/calibration hashes otherwise match. No processes were restarted; controlsd was not running while offroad and will load the new Python code on the next drive. Actual onroad trace production still requires the next log.

Recovery baseline: `d9b512af79cde1438e49dcea9200ece460cb5f1b`. C4 backup `/tmp/nrdr-ptm-measurement.kwi7pB/source-before.tar.gz` and `params-before.json` retained (temporary storage is not reboot-durable). Simple behavior rollback is selecting **normal PTM, ID 1, while parked**; it has no measurement payload and unchanged arithmetic. Source rollback, if needed, should revert the measurement commit explicitly, not reset branches or erase other changes.

## Next collection and decision

First establish whether the previously reported brake/ABS/ACC faults are resolved and whether the car is safe for the intended test. Hidden warnings and ordinary-feeling braking are not verification. Do not perform an assisted-steering experiment while that safety status is uncertain. No failed corner or lane departure needs to be reproduced.

Once suitable for supervised collection, use the installed Testing measurement baseline and keep Pop v2, geometry, all filters and override settings fixed. Collect two ordinary 10–15 minute loops in daylight with clear lane markings, safe conditions, gradual left/right curves and normal slowing-entry/release transitions, broadly 5–15 m/s where legal and appropriate. Include normal manually driven turns; do not force tight turns under assistance. Retain at least 10 seconds of preceding/following history and subsequent turns; full routes are preferable. Park between runs. Aim for at least five clean repeated events each direction and enough normal curved driving to exceed the rack fitter's 300-second eligible-data requirement; failure to meet coverage is an observation, not a reason to force maneuvers.

Maintain ordinary hands-on supervision and intervene immediately whenever needed; never let a departure build for data. End assisted testing for unexpected pull, oscillation, warning/fault, abnormal brake/steering feel or repeated correction. Park before selecting normal PTM to revert. Do not clear fault codes or change the model/firmware/tune during collection. Record approximate intervention times and impressions after parking, not while driving.

Send both route links and retain/upload full rlogs plus road video. Required streams: initData/CarParams, modelV2, carControl/carOutput, controlsState with measurement v1, vehicleParameters, carState including yaw, deviceMotion, CAN/sendcan with EPS debug frames, Panda state/counters and GPS. Normal car logging is eligible; first verify payload presence and complete segments before further analysis.

Expected measurable result is **reproducible state and timing**, not different steering feel. Reconstruct each sampled core update to floating-point precision from the new consumed inputs; compare publication intervals and command ages against baseline before trusting the data. Determine whether mismatch-threshold crossings explain I holds/rebuild across entry, release and next turn; separate true same-command attenuation where lineage is unique. Re-run the tool suite above by route/model and compare like speed/direction cohorts. Repeated unpressed wheel/command phase error with good physical-map agreement supports testing dynamic/load/feedforward parameters next; an error tracking model/blended geometry instead redirects calibration work. Reject the measurement build itself if logging creates deadline gaps or control parity breaks. Do not introduce the unwind gate until its I/history and subsequent-turn regressions are addressed.
