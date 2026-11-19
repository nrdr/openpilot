# Clarity PTM Testing investigation

## Current decision

**November 18, physical steer-ratio check (offline, no retune).** On the November 16 gas-station routes
`000001fb--d8a6ee668a` and `000001fc--4d41e3c5d1`, `eps_fit_yaw_scale --bus 0` compared integrated VSA
yaw with GPS bearing changes: 113,481 *overlapping* windows, 0.2449 deg/s/count plus 0.168 deg/s clockwise
correction, heading residual RMS 1.11°. Using those coefficients in `eps_fit_rack_map` (HONDA_CLARITY,
39990-TRW-A020) yielded 219 + 159 seconds of qualifying turning. The existing unblended donor map was
not fitted to either of these drives. Below are per-leg median **measured / predicted curvature** from
evaluating each runtime geometry on the *same* lag- and offset-corrected angles, speed and roll:

| Wheel angle, 2.5–9 m/s | Unblended PTM: outbound / return | 250° blend: outbound / return |
|---|---|---|
| 3–20° | 0.901 / 0.887 | 0.892 / 0.878 |
| 20–70° | 0.996 / 1.011 | 0.980 / 0.992 |
| 70–150° | 1.022 / 1.017 | 0.995 / 0.987 |
| 150–450° | 1.012 / 1.005 | 0.909 / 0.919 |

At 9–40 m/s there were insufficient samples above 70° for a scored cell; the 150°+ slow cells
contained 378 and 238 subsampled frames, not independent maneuvers. Low yaw and angle-offset errors
matter proportionally more near center. These are physical predictions on previously recorded motion,
not two observed drives using the candidate controller or a demonstration of lane tracking.

The shallow discrepancy concentrates at 3–10°: splitting the slow gas-station samples by route and
turn direction, the four unblended medians are 0.76–0.81, versus 0.95–0.99 at 10–20°. As a separate
check, freezing the same yaw coefficients and applying them to the earlier timing-on/off routes
`000001ef` and `000001f0` gives 0.871 / 0.828 at 3–20° slow, but 0.994 / 1.002 at 20–70° slow.
Those shorter drives do not clear the scoring threshold above 150°. Check low-rate yaw resolution
and steering zero against an independent motion reference before attributing the near-center residual to the rack.

To reproduce the unblended comparison from the repository on a host with the log dependencies:

```powershell
$raw = '../analysis/clarity-ptm-measurement-2026-11-16/raw'
$legs = @("$raw/000001fb--*/rlog.zst", "$raw/000001fc--*/rlog.zst")
python -m openpilot.nrdr.tools.lateral.eps_fit_yaw_scale --bus 0 @legs
python -m openpilot.nrdr.tools.lateral.eps_fit_rack_map --car HONDA_CLARITY --eps 39990-TRW-A020 --bus 0 --scale 0.2449 --right 0.168 @legs
```

Read the `shipped PTM` rows for the existing unblended map. The tool's `rack map` rows are
new fits, not the installed calibration. Do not apply the gas-station yaw coefficients to another car without checking them.

**November 17, user-authorized temporary SR experiment deployed; road validation pending:** runtime commit `a05e42cd6f2d739b37db81265f781753b948c543` shortens only the eligible Clarity/PTM Testing model blend from 433.8 to 250 degrees, preserving the current 17.4518434793 center and 12.72 endpoint. It uses the existing analytic inverse, not the historical measured-angle lookup. Normal PTM, other cars, model eligibility, physical rack tables, controller gains, all filters, target slew, timing-off behavior, override and safety limits remain unchanged. Cadence investigation remains unresolved and is not claimed fixed by this experiment. Published to `nrdr-development`, installed cleanly on C4, and verified in running/saved telemetry. The user confirms the dash is normal; temporary offroad/boot settings are restored.

**First moving-data audit passed; performance attribution strengthened, no steering change promoted.** The gas-station outing supplied two complete Pop v2 measurement routes, with exact scalar I/filter reconstruction across 102,620 active updates. Controls run at 84.9/86.1 Hz with moving lateral control active, but 99.1/98.9 Hz in moving-inactive portions of the same drives. Incoming CAN volume and card/selfdrived CPU use barely change. Read-only stationary profiling establishes a nearly full shared core and substantial runnable wait. Paired native replay isolates about 1.02 ms additional CPU work per active update on analysis cores; most is the active lateral-control path, with measurement logging contributing about .08 ms of the active/inactive difference (.27-.29 ms total active logging overhead). Card's parsing/decoding, command conversion and application are a large steady baseline, not the activation-specific surge. These results support active computation exceeding shared-core headroom, but are not an exact live deadline attribution or a proven optimization. Keep the tune, normal PTM and scheduler unchanged; next evaluate narrow output-identical redundant-work reductions. The user regards their previously mapped steer ratio as the strongest fix candidate, while awaiting evaluation; no event-specific intervention times were provided.

**Startup recovery verified November 16 evening; stationary logging works, road behavior remains unvalidated.** `controlsd` had exited with code 1 at `latcontrol_ptm_testing.py:89`, assigning `pid_log.ptmTesting`: the manager predated deployment and retained the old schema when forking Python workers. Fresh-process tests saw the new field but did not validate the still-running manager. After user confirmation and live verification of ignition off/disengagement, the manager was stopped cleanly and the normal launcher restarted. Startup applied an already-staged copy at the same `5c6467e526` revision and completed its ordinary native/model build; no release workflow was run.

The 1,800-frame native parity/serialization check passed again. Offroad required processes were healthy. With the user's car on but stationary in Park and assistance disengaged, controlsd stayed alive: 1,463/1,463 sampled controls messages were valid measurement-v1 records. Saved `000001fb--d8a6ee668a--0/rlog.zst` contains 5,462/5,462 valid control/trace records spanning 55.292 seconds, with 4,555 carrying both consumed car/model IDs after startup warm-up. There were no matching logger exceptions. Steering temporary/permanent flags cleared, the gas-interceptor event disappeared, and only Park/seat-belt/parking-brake events remained. The user also confirmed the unexpected dash warnings are gone. This verifies recovery, not the underlying cause of every historical vehicle DTC; no DTC clearing or vehicle-ECU flash was requested or performed.

Restart backup hashes: `/tmp/nrdr-ptm-measurement.kwi7pB/restart-params-before.json` (381 existing keys). Manual tuning, controller selection and saved models were unchanged; runtime/update metadata, transient keys and live learning changed during ordinary startup/ignition operation. Future schema changes require a full manager restart while parked and a stationary check of actual published **and saved** records before collection. Fresh-interpreter tests alone are insufficient. No steering logic or parameters were changed to recover from this crash.

November 16, 2026: measurement-only experiment, **first outing captured, not a demonstrated steering improvement**. Runtime commit `d0297d254b23a1ad52aa7dc7ffbfcf0d308a1fb3` is published on `nrdr-development` and installed on the C4. Testing ID 2 is selected. Normal PTM's wrapper/core, final filter, safety enforcement, driver override and model/geometry settings are unchanged. No release builds or firmware flashes were performed for this experiment.

The standing workflow is in the repository's `AGENTS.md`. On November 16, the user confirmed that a mechanic checked the Clarity and the brake/ABS/ACC faults are resolved. This is a user-reported resolution, not an independent diagnostic rescan; no code clearing is pending here.

## Gas-station outing: first measurement validation

Saved routes `000001fb--d8a6ee668a` (19 segments, includes stationary startup validation) and `000001fc--4d41e3c5d1` (9 segments) report `5c6467e526`, Testing 2 and Pop v2/PMV2. All 28 full rlogs were copied locally and SHA256-matched to the C4. The audited controller/model/geometry/override parameter snapshots are consistent across all segments. Integrated car speed gives about 19.64 km / 12.20 mi combined; moving above 2.5 m/s accounts for 19.71 minutes. This is an observational out/back baseline, not a matched comparison with the older OPM10V3 runs.

| Check | Outbound / return | Interpretation |
| --- | --- | --- |
| Valid controls / measurement-v1 records | 96,998 / 46,687, every record | No missing trace or repeat of the schema crash; control/model/car processes retain one PID within each route |
| Active per-update reconstruction | 64,397 / 38,223 | All independent scalar I/filter checks exact; full core state differs by at most 5.46e-12 in internal R5 units and 5.56e-17 in normalized FF; Float32 published output differs by at most 2.98e-8 |
| Exact consumed carState lookup | 100% of active updates | Logged speed/angle match the identified publication exactly, eliminating the old nearest-message ambiguity for these inputs |
| Moving active wrapper cadence | 84.89 / 86.12 Hz | Publication cadence independently agrees; nominal core dt remains .010 s |
| Interval p99 / maximum | 20.21 / 44.77 ms; 20.02 / 45.07 ms | 27 / 11 intervals exceed 30 ms; none exceed 50 ms |
| Moving CPU core 4 median / thermal status | 100% / normal on both | CPU contention or work cost is plausible; not proof that measurement logging caused the slowdown |

Reconstruction restores the recorded **before** state separately for each update. It validates the payload and arithmetic, not continuous counterfactual history or physical response. I was held by host mismatch on 7,850 / 2,288 active frames; anti-windup rejected 322 / 99 trial updates; scaled final sums clipped on 1,882 / 169 frames. These categories overlap, and the largest counts include very-low-speed/manual transitions. Same-command carOutput lineage remains unresolved.

Older timing-On/Off publication rates, under the same moving/active selection, are 89.86 / 96.83 Hz, but those use OPM10V3 and are not a controlled measurement-overhead comparison. Since derivatives, filters, slew and recovery use nominal dt, slower execution changes their wall-clock behavior. Do not compensate with arbitrary gains or replace dt globally: first compare a same-model pre-instrumentation route and profile the actual work/scheduling if needed. Prior wrapper-only serialization overhead is not an onroad timing exoneration.

The existing `eps_report` and `eps_plan_timing` tools were run separately on both full routes, with numerical segment ordering. At 9–15 m/s, shipped-rack map slopes are .984/.986 outbound and 1.001/1.017 return for near-center/20–90-degree bands. This does not support a blanket ratio correction. Low-speed/high-angle coverage is still inadequate in the report; high-speed near-center slopes (.523/.742) have very small steering excitation (median absolute target ~.8 degrees) and must not be installed as ratio multipliers. Device yaw is about .98–.99 of the inherited CAN-yaw reference, with an estimated +60 ms relative lag. These are calibration-dependent comparisons, not independent truth.

Crucially, physical-rack agreement does **not** validate the model-to-target transformation. These routes selected PTM Auto (3) with Model-Specific Blend (1); the saved PMV2 bundle is in `2026 World Models`, eligible for the blend. That path applies a separate inverse angle mapping on top of the rack/slip conversion. It is not the archived `CLARITY_RAW_STEER_RATIO` curve (retired mode 2), and existing legacy raw/manual parameter values do not make that curve active. The user's report that their mapped ratio works well for this model is therefore a legitimate alternative-geometry hypothesis, not refuted by `eps_report`. Confirm which exact historical mapping they mean, reproduce current desired angles including the nominal 300-deg/s slew, then compare alternative targets and full-controller state offline with feedback held fixed. Such replay cannot prove the model's closed-loop path response would improve. Do not assume a ratio change would cure the measured lag by itself.

Plan-phase best fits show entry -130/-250 ms and exit +350/+270 ms, using 287/158 entry and 292/223 exit frames. This is consistent with an entry/exit asymmetry worth tracing, but is not a single identified EPS delay: overlapping plan forecasts, evolving model targets, inherited yaw calibration, and phase selection all matter. No latency number is promoted into the controller.

One directly measured return event at **451.619 s / 7:31.62 video time** has target 109.768 degrees, wheel 147.700 degrees, speed 5.196 m/s, and no reported raw/effective press in the displayed 446.5–453.8 s window. Weighted FF is already -.7064, scaled P -.9857, I -.01085 and final normalized output -.9661. Both target and wheel are unwinding at this instant: this is a 37.93-degree tracking gap, not proof the wheel was still turning inward. A retained *positive* FF term or a large I term cannot explain this particular instant. Earlier slowing-entry error and the subsequent near-full outward command require the complete model-to-EPS history before deciding whether filters, target slew or physical response dominate. See `return-unwind.png` in the private analysis folder.

Other sharp outbound events have much larger target error near 2.5–3 m/s, including zero admitted FF while the unchanged join gate waits for angle error below 10 degrees. These must be separated from established-FF unwind events rather than pooled into one filter diagnosis. Reported absence of a press is not proof of no driver input; driver impressions/video review remain pending.

The speed claim is not a uniform scaling error on Pop v2. In steady (|aEgo| < .3 m/s²) 9–15 m/s cohorts, median initial planned speed is +7.0/+8.6% versus car speed and camera-odometry forward speed +4.6/+6.4%. At 25–40 m/s those signs reverse: plan -3.1/-1.7%, odometry -3.6/-2.2%. GPS publication-aligned medians differ from car speed by only .01/.03 m/s and .08/.05 m/s respectively, but GPS latency is not independently calibrated. Initial planned speed is not necessarily perceived current speed; do not apply one global speed or steer-ratio correction from these summaries.

No permanent steering fault or gas-interceptor event is logged. Brief temporary-steering flags occur during low-speed maneuvers (220/215 carState samples); latest-prior CAN status is `NO_TORQUE_ALERT_1` for 220/213, with two transition-alignment samples already normal. That is not a diagnostic-code rescan or proof of a renewed brake fault. Outbound has brief `commIssueAvgFreq` events around 413.6, 750.2 and 895.2 s with `deviceState` frequency identified; optional ignored streams also appear in the diagnostic list. Startup-only DM/location/communication events and one connectivity exception are retained in the audit. Return has none of those selected events. Do not describe the entire outing as fault-free.

Artifacts and reproducible scripts: workspace `analysis/clarity-ptm-measurement-2026-11-16/`, including `source-hashes.json`, `audit_outing.py`, both `*-measurement.json/.npz`, `outing_metrics.py` / `outing-metrics.json`, `health_check.py` / `health-check.json`, `run_lateral_tools.py` and per-route tool outputs, and `plot_return_unwind.py` / `return-unwind.png`. Host Python uses the existing export/test dependency paths; the plot additionally uses `Build Reports/2026-10-15-civic-pcm-long/plot-deps`. No raw route data is added to Git.

**Decision:** retain the unchanged baseline for offline analysis; arithmetic logging passes, timing acceptance remains open, no filter/ratio/gain change or new driving request. Next: identify the user's preferred historical mapping and compare its target transformation, trace return 447–453.8 s through raw model/E4/EPS alongside the low-speed FF-admission cases, and separate same-model pre-existing cadence from new instrumentation overhead. Reuse this outing before asking for another drive. Normal PTM, car parameters, code-clearing state and releases remain untouched.

## November 17: user-identified historical SR taper (proposal only)

The user's screenshot identifies the historical PID experiment: `np.interp(abs(CS.steeringAngleDeg), [0, 250], [18.50, 12.74])` assigned directly to `VM.sR`. The user reports good subjective results with Pop v2 and OPM10v3, intends 12.72 rather than 12.74, and now proposes retaining the current firmware/rack center instead of restoring 18.50. The screenshot's comments describe other ratios and are inconsistent with its executable array; the array is the evidence. This identifies the previously unspecified historical mapping, not a validated improvement on the present controller.

At source `5c6467e526`, `steer_ratio_tuning.py:390-416` already gates a center-to-published-ratio taper by recognized EPS firmware, explicit Model-Specific Blend and eligible model. The Clarity endpoint is **12.72 at 433.8 degrees** (`2.41 * 180`), not 250. Honda's [2018 PHEV specifications](https://hondanews.com/en-US/honda-automobiles/releases/release-4ddb58f0247c42a4a5d9a6177c9b5ec8-2018-honda-clarity-plug-in-hybrid-specifications-features) publish 12.72:1 and 2.41 lock-to-lock turns, but do not identify 250 degrees as the point where that ratio applies. Treat 250 as the user's experimental breakpoint, not a manufacturer calibration or universal breakpoint for other cars. Existing eligibility includes explicitly listed legacy/pre-world/world families and references, and excludes big models/Chestnut; it is not a generic generation-number check.

Offline static calculation using `RackMapGeometry(HONDA_VGR_PROFILES[0], CLARITY_TRW_A020_RACK, base, ptm_baseline=True)` and the existing `center = base * .01 / rack.physical_to_linear(.01)` yields **17.4518434793**. The arbitrary common linear anchor `base=18` cancels in this comparison. Construct existing `AngleSource(mode=0, base=base, center=center, final=12.72, outer=433.8, comma=base)` and a local in-memory counterpart with `outer=250`. Their ratio values at 0/125/250 degrees are respectively 17.45184/16.08836/14.72487 versus 17.45184/15.08592/12.72. Compare equal inputs with `candidate.inverse(current.forward(a))`: current targets 125/138/176/250 degrees become 118.2100/129.7707/162.8309/224.2393 degrees **before desired-angle slew, filters and controller state**. The proposed forward/inverse round trip passed at every integer angle from -500 through 500 degrees to 1e-9. No logs were counterfactually replayed in this check and no physical response was predicted.

The current analytic inverse solves the taper at the requested angle; the screenshot instead sampled it at the measured wheel angle. They agree only in the appropriate steady-state mapping, not during lag/unwind, and the historical VehicleModel slip assumptions also differ. The shorter taper preserves the exact center anchor but changes nonzero angles immediately; it does not preserve a finite near-center band. Its slope also changes at the 250-degree plateau. A lower target can reduce turn-in demand but can increase instantaneous target/wheel error with recorded feedback held fixed, so it is not proof of faster unwind or repaired EPS lag. Current selection code also uses the model blend for measured-curvature consumers; a future experiment must audit both directions rather than silently relabel physical rack data as a model-dependent measurement.

**Next:** compare the existing 433.8-degree inverse, proposed 250-degree inverse and explicitly labeled historical measured-angle formulation on saved inputs, including the unchanged target slew and full controller history. Keep the physical-rack diagnostic independent, final output filter and normal PTM unchanged; resolve the cadence confound before interpreting wall-clock filter behavior. Other vehicles require variant-specific verified endpoints and evidence for their transition angle. This pass changed only investigation notes/task tracking: no runtime source, parameters, build, commit, push or deployment.

## SR250 experiment verification and collection contract

The user explicitly requested deployment for subsequent logs, and authorized software offroad mode while the car remains on. A fresh eight-second Park/zero-speed/disengaged check passed (793 carState records; no invalid CAN or temporary/permanent steering fault flags). Setting the existing `OffroadMode` stopped card/controlsd/selfdrived before staging. DeviceBootMode was temporarily changed from 0 to 1 for a manager restart that stays offroad; restore 0 and the previous OffroadMode=false before handoff. No vehicle ECU commands or flashing.

Host tests: 89 passed, 32 native-only skips. Native C4 candidate checks: 121 passed, using a temporary source-import overlay at `/data/tmp/nrdr-sr250.oVWjnR` without changing the production checkout. Test suites: `test_ptm_testing_sr_blend.py`, `test_ptm_settings_cleanup.py`, `test_ptm_testing.py`, `test_ptm_controller_update.py`. Both source/controller admission and consistent measured/desired mapping are covered; normal-PTM core parity tests pass. No new schema, Params keys, UI controls or release builds. Donor branch checked at `aa31067380cdcfdff6d9000c23ef1a375fdb2157`; its actual `latcontrol_honda_eps.py` and `honda_eps_rack_map.py` have no diff from previously audited `b110c9f1529adad07b3b6302b41e5628e12a36a0`. This SR experiment is local, not a donor tune import.

Saved return segment 7 was restored from the verified host archive because it had rotated off the C4. SHA256 remains `b43366f39a6508badbd8f9fc13e9ee642b0fa852a1ed0ee7995c6b8c65fe9821`. `sr250_native_check.py replay --sr-blend` with `NRDR_REPLAY_RLOG` pointing at the staged log ran all **5,167 active updates** through real Controls methods and serialization with fixed recorded feedback, no transport/workers/writes. Baseline repeat is exact; candidate longitudinal outputs and admission are identical. Peak absolute target falls 223.4910 -> 202.7134 degrees; maximum target difference 20.7776 degrees. Absolute target is reduced on 5,150 frames and increased on 10 (continuous history/slew means not pointwise reduction everywhere). Maximum active target step 3.0000076 degrees is consistent with the unchanged 3-degree nominal step after Float32 serialization. Outputs remain finite and within existing limits; maximum absolute torque is .999638 baseline / .999866 candidate, maximum command difference .59986. At sample +30.14 s into the replay, the same recorded 233.1-degree wheel position accompanies targets 219.88 -> 199.74 and commands +.22 -> -.36. This is earlier outward **command against fixed feedback**, not measured earlier unwind or a prediction of reduced steering roughness. Complete output: private `analysis/clarity-ptm-measurement-2026-11-16/sr250-native-comparison-output.txt`.

Baseline/rollback source is `5c6467e526fd1607c81ad7ff2760ab484d9d9a2e`; unchanged submodules are opendbc `5320fe2df0d93a594e079d4f3669e45087f838f0`, msgq `e7396e76dadbb49e374d4b664ff6bbb43a39bcb0`. Existing C4 selection is PTM Testing (2), ratio mode 3, model blend enabled, Pop v2/PMV2 `62bf6fb072880905a4c490f0f4f4a6b3c23346ec`, optional Honda delta limiter disabled. Parameter hashes and named settings saved as `sr250-params-before.json`; original three runtime files backed up to `/data/tmp/nrdr-sr250.oVWjnR/runtime-before.tgz`. Behavior rollback: while parked select normal PTM (1) and restart/cycle onroad so the normal controller is constructed; its original 433.8-degree mapping remains. A source rollback should explicitly revert `a05e42cd6f`, not reset the branch.

**Installed verification:** C4 fast-forwarded cleanly from the baseline to `a05e42cd6f`; a full manager restart used the normal launcher and its ordinary incremental startup build, not the release script. The same 121 native tests passed on installed source. OffroadMode=false and DeviceBootMode=0 were restored. The first post-toggle observer rejected an initial non-Park gear sample before recording a report; an immediate read-only follow-up found valid Park/zero-speed/disengaged state, and the subsequent complete 25-second check passed. It observed 2,463 carState and 2,456 controls messages, every controls message carrying measurement-v1. The 986 settled carState samples had zero invalid-CAN/temporary/permanent steering faults; core processes each retained one PID (controlsd 467395, selfdrived 467396, card 467397). Thermal status was ok and final events only Park/wrongGear, seatbelt and parking brake. The user confirmed no unexpected dash warnings. Saved route `00000200--46aafcb6ee`, segment 0, independently contains the exact revision, 5,541/5,541 measurement-v1 controls records and a consumed geometry report `model_blend_outer_deg=250.0` from the running control process. Saved parameters for the controller, model, geometry and tuning are unchanged; hash differences are offroad/onroad state, ordinary live learning, uptime/pings, boot/route and Git/update/model-sync metadata. Evidence: `sr250-startup-verification.json` and `sr250-saved-log-verification.json` beside the replay output. No road-performance claim; normal PTM remains untouched. Runtime code is committed/pushed; accumulated investigation notes/task tracking remain local and uncommitted.

Prediction: comparable ordinary left/right turns should need less inward target angle and avoid the prior excessive turn-in/catch-up, without introducing understeer, abrupt unwind or straight-road instability. First collect a short ordinary supervised trip, with the same Pop v2 model and other settings, before a longer trip. Include preceding/following straight sections and normal varying-speed turns; note locations and any intervention, but never reproduce a lane departure or delay taking over. Stop assistance if warnings, unexpectedly weak/strong steering, oscillation or abrupt corrections occur; revert while parked. On receipt, compare angle/curvature requests, wheel and independent yaw, entry/exit error, P/I/FF/filter state, caps, intervention markers and actual loop cadence against baseline by comparable speed/direction. Retain/refine/revert only after measured behavior; offline replay alone is not acceptance.

## Cadence attribution: host versus vehicle

Read-only reanalysis of the same 28 full rlogs uses a common latest-prior measurement mask (`coreUpdated`, speed >= 2.5 m/s). Rates are selected interval count divided by summed monotonic intervals. `cadence_attribution.py` and `cadence-attribution.json` are retained in the private outing analysis directory above; this required no vehicle connection or runtime change.

| Stream | Outbound Hz | Return Hz |
| --- | --- | --- |
| Received bus-0 steering angle / EPS status (0x14A / 0x18F) | 100.004 | 100.002 |
| Received bus-0 yaw (0x94) | 99.993 | 99.995 |
| carState / selfdriveState / carOutput | 99.307 | 99.319 |
| controlsState / carControl | 84.886 | 86.118 |
| Steering sendcan submission (0xE4, bus 0) | 99.307 | 99.320 |
| modelV2 | 20.000 | 20.000 |

All 65,547 / 43,760 selected carState records have valid CAN. The control loop is not waiting for physical EPS motion or an actuator acknowledgment: `controlsd.update` polls `selfdriveState`, which remains near 100 Hz. Its 15-ms poll timeout is not an intentional 15-ms period. `Ratekeeper.monitor_time()` measures timing; it does not guarantee 100-Hz execution. `card` applies the latest available carControl while alive, so the faster submission loop can reuse a request between fresh control calculations; downstream driver/safety shaping can still change the transmitted value. `sendcan` establishes host submission frequency, not hardware acknowledgments or exact wire timing.

Source pins the main loops of `card`, `selfdrived` and `controlsd` to CPU 4 at the same SCHED_FIFO priority 53. Saved process-leader CPU/priority fields agree, and CPU 4 has 100% median utilization in both moving cohorts with normal reported thermals. Process-wide CPU use is approximately 44.8%, 27.4% and 32.5% of one core respectively. These include helper threads: their sum is not a valid per-thread/core allocation or proof of which function caused the delay. Shared-core scheduling/workload is the leading hypothesis; new measurement logging is neither exonerated nor established as the cause. Older task-11 evidence already showed a deficit before this instrumentation, but no matched same-model logging-on/off comparison exists.

Mean control publication spacing is about 11.6-11.8 ms instead of 10 ms; publication p99 is 21.45 / 21.10 ms and maximum 43.67 / 48.45 ms. These are publication intervals, distinct from the core-entry intervals above. Fixed-.010-s filter/slew/integrator arithmetic therefore does not represent actual elapsed time; for a constant-rate illustration, fixed-dt filter time scales would stretch by roughly 16-18%. This does not establish how much of the observed unwind gap is scheduling, geometry or EPS response. Next discriminator: per-thread execution/wait profiling and a comparable same-model instrumentation-cost check, not arbitrary gain/dt or affinity changes. Only analysis artifacts and uncommitted notes changed in this pass.

## Upstream comparison and parameter-cost check

November 16 source check: `git ls-remote upstream refs/heads/master refs/heads/dev` matched existing local objects, master `c6e564cdcd68dc6334381ac0d929133b1d824479` and dev `551cb67760be88c01b0189b6ac7dd3a1e364b20a`. Both already pin `card`, `selfdrived` and `controlsd` to core 4/priority 53; both retain 0.1-s card/selfdrived parameter workers, the 15-ms controlsd subscriber timeout, and per-frame `ChestnutLoading` / `ChestnutActive` reads in selfdrived. The extension parameter period is 3 s. This establishes inherited architecture, **not that unmodified sunnypilot runs at 85-86 Hz** on the same vehicle/hardware; no such matched runtime baseline was measured. Primary sources: [card](https://github.com/sunnypilot/sunnypilot/blob/c6e564cdcd68dc6334381ac0d929133b1d824479/openpilot/selfdrive/car/card.py), [selfdrived](https://github.com/sunnypilot/sunnypilot/blob/c6e564cdcd68dc6334381ac0d929133b1d824479/openpilot/selfdrive/selfdrived/selfdrived.py), [controlsd](https://github.com/sunnypilot/sunnypilot/blob/c6e564cdcd68dc6334381ac0d929133b1d824479/openpilot/selfdrive/controls/controlsd.py).

nrdr already separates persistent tuning reads from actuation: `params/snapshots.py` spreads 47 control keys over 12 groups in a nominal 0.5-s cycle (~42 ms between groups). `car/opendbc.py` spreads 25 Honda keys over seven groups in 0.5 s (~71 ms slots), plus one HUD-expiration key every 0.25 s. Both workers explicitly drop real-time priority and widen affinity; actual periods also include read execution time. Per-frame consumers use memory snapshots. Background Python work can still contend for the interpreter; this is not zero-overhead proof. The inherited card/selfdrived parameter threads do not explicitly demote themselves in their thread entry points.

After fresh user confirmation of parked/ignition-off state, an isolated read-only benchmark ran on C4 `192.168.1.12` at unchanged `5c6467e526`, with offroad guards before/during/after, no CAN publishers, no parameter workers, and no manager restart. `native_parameter_cost.py` and `native-parameter-cost.json` are saved in the private outing analysis directory. Each case has 50 warm-ups and 600 measured samples, alternating order. A first equivalent run is retained as `native-parameter-cost-unpinned.json`. The system only had CPUs 0-3 online offroad; trying to pin the separate benchmark to offline core 4 was rejected, and no cores or live affinities were changed. Thus these are low-power-core, warm-cache microbenchmarks, **not driving-core costs or a causal cadence A/B**.

| Isolated operation | Median wall time | Storage reads | Interpretation |
| --- | --- | --- | --- |
| nrdr control polling, one group | .384 ms | Group-dependent | At 24 groups/s, estimated CPU cost ~1.21% of one benchmark core, excluding worker wake overhead |
| Honda polling, one slow group | .492 ms | Group-dependent | At 14 groups/s, ~.64% per provider; fast HUD poll adds ~.064% |
| Read all 47 cached control keys | .050 ms | Zero | Synthetic all-key batch; not a full control-loop profile |
| Fetch cached Honda typed tuning | .0027 ms | Zero | Returning the existing typed object |
| Reconstruct current geometry selection | .308 ms | Zero | nrdr calls this every frame; cached rack grid/model classification do not prevent rebuilding selection objects |
| Chestnut status pair | .148 ms | Two | Inherited per-frame state reads, not slow user tuning |
| card parameter worker key reads | .460 ms | Five | 10-Hz polling, ~.47% projected benchmark-core CPU |
| selfdrived parameter worker direct keys | .408 ms | Six | 10-Hz polling, ~.42%; excludes personality file-lock/sync work |

CPU projections use measured thread CPU time times configured call frequency; they include timing-instrument overhead, do not account for duplicate providers or scheduler/GIL interactions, and must not be subtracted from the onroad CPU percentages above. The adapter exposes only reads. Parameter hash comparison was unchanged in the first run and changed only normal `UptimeOffroad` in the second; no keys were added/removed. Initial launch attempts failed before measurement due to selecting the system Python rather than `/usr/local/venv/bin/python`, then the old cereal car-import location; the saved script uses the native environment and opendbc car schema.

**Decision:** no 30-s refresh change is justified as a demonstrated cure yet. The user accepts slower, staggered configuration refresh if profiling proves it useful; do not apply that latency to vehicle state, faults, model/accelerator transitions or driver-interaction behavior. The repeated geometry-selection work is a separate candidate that slowing storage polling would not eliminate. Next: profile the actual fast-loop stages and thread waits under representative replay/onroad load, then compare one targeted optimization with unchanged outputs, settings-application semantics and driver protections. No control source, tuning, release or deployment changed; notes remain uncommitted.

## Actual control-path profile, unchanged behavior

November 16 evening: user requested profiling before optimization. Native `5c6467e526` replay used 5,167 consecutive saved control frames from return segment 7 (59.875 s), with 300 warm-up frames and 4,867 timed frames per pass. Local and native rlog SHA256 agree: `b43366f39a6508badbd8f9fc13e9ee642b0fa852a1ed0ee7995c6b8c65fe9821`. The real `Controls.update`, `state_control`, `publish`, `get_params_sp`, `run_ext` and `Ratekeeper.monitor_time` methods ran with unchanged PTM Testing/controller geometry. Four consumed input IDs are exact; other streams are latest-prior to controller entry, not a reconstruction of original subscription arrival order. Saved parameter bytes use native registry/default conversion through a read-only adapter. No vehicle publishers, live parameter writes, background tuning workers, process restart or installed source edits were used.

This is a calculation/publication-preparation profile: subscription handling is a saved-message adapter and output messages are natively serialized into memory, not sent over IPC. It excludes actual polling/transport and worker contention. It starts with fresh continuous controller state, so output equality across all four passes verifies **profiling transparency**, not historical-command parity or changed vehicle response. All 5,167 torque/angle/curvature/acceleration/activity output rows are exactly equal between baseline, stage-instrumented, callgraph and repeat-baseline passes. Normal PTM is untouched.

Both uninstrumented runs took **4.13 ms median**, 4.36/4.37 ms mean wall time and 4.29/4.30 ms mean thread CPU time. Stage instrumentation raised mean wall time to 4.91 ms; the detailed callgraph profiler raised it to 12.85 ms and is used only to locate work, **not to estimate achievable loop rate**. These runs used only offroad CPUs 0-3, SCHED_OTHER nice +10, not onroad core 4/FIFO53. They cannot be subtracted from the onroad 11.6-11.8 ms interval or presented as a 100-Hz deadline pass.

| Inclusive operation in stage-instrumented replay | Median wall time | Interpretation |
| --- | --- | --- |
| Full `state_control` | 2.770 ms | Includes geometry, longitudinal and lateral calculations below |
| PTM Testing wrapper | 1.126 ms | Includes unchanged control core, target mapping and measurement construction |
| PTM Testing core | .510 ms | Nested inside wrapper; feedforward is .254 ms of this |
| Geometry/live-settings stage | .533 ms | Nested inside state_control; selection rebuild alone is .313 ms |
| Geometry selection reconstruction | .313 ms | Exactly once per frame, no persistent reads; CPU mean .331 ms |
| Desired-angle / measured-curvature mapping | .072 / .066 ms | Dynamic angle/speed transformations, separate from selection reconstruction |
| `publish` preparation and memory serialization | .557 ms | Excludes actual IPC transport |
| Extension output preparation | .475 ms | Includes lead/MADS/ICBM copying and periodic lane diagnostics |
| Saved-input update plus pose handling | .600 ms | Includes adapter overhead; not a measurement of real message receive/wait |
| Parameter-refresh gate / rate monitor | .004 / .017 ms | Gate normally does no refresh; Ratekeeper does not sleep here |

Nested rows must not be summed. Timing-call overhead matters particularly for small rows. The callgraph confirms repeated dataclass/firmware/geometry selection work and substantial field access/interpolation across the wider loop, rather than one large storage operation. The native rack-grid/model-classification caches remain warm; the .313-ms selection cost is not rebuilding the rack grid. This makes selection reuse a bounded optimization candidate, not an established cure for the missing updates. No caching, polling-period, affinity, priority, dt, tune or filter change was implemented.

Saved onroad timestamp partition over consecutive active/moving frames gives:

| Phase | Outbound mean | Return mean |
| --- | --- | --- |
| Previous controlsState timestamp to next PTM entry | 10.704 ms | 10.586 ms |
| PTM entry to controlsState timestamp | 1.076 ms | 1.026 ms |
| Total publication timestamp interval | 11.780 ms | 11.612 ms |

The first phase includes the previous publication tail, extensions, next receive/poll, pose and pre-PTM work, plus any scheduling delay. It is **not all waiting**. The second includes PTM/trace and publication preparation plus any scheduling delay; controlsState is timestamped before serialization/send. Post-entry p99 is 7.95/6.56 ms versus medians .915/.893 ms, so occasional stalls also occur inside that region. The additive partition is verified numerically but cannot recover OS runnable/blocked durations from saved logs. No evidence supports blaming car message latency or a deliberate 15-ms sleep.

Artifacts in the private outing analysis directory: `control_phase_attribution.py`, `control-phase-attribution.json`, `native_control_profile.py`, `native-control-profile-output.txt`, and the read-only stationary observer `observe_control_scheduler.py`. The native parameter hash check changed only ordinary heartbeat/offroad uptime keys (`LastAthenaPingTime`, `LastSunnylinkPingTime`, `UptimeOffroad`), with none added/removed. All three analysis scripts pass syntax compilation. No runtime source, normal PTM, tuning or release changed; investigation notes remain uncommitted.

### Live stationary scheduler measurement

After user authorization and the requested minimum 90-second setup wait, the first check still found offroad state; an initial short attempt then ended as the car returned offroad. Neither supplied a complete timing result. A subsequent **30.026-second** sample completed with Park, speed < .1 m/s, disengagement and fresh state guards throughout, retaining one PID per process. The observer stayed on cores 0-3 at nice +10, used subscriptions and `/proc` reads only, and neither attached a debugger nor changed any production thread's affinity/priority. The user was told when collection finished. Results are in `stationary-control-scheduler.json`.

| Main thread, all observed on core 4 / FIFO53 | CPU execution | Runnable, waiting for CPU | Remaining wall time |
| --- | --- | --- | --- |
| controlsd | 27.70% | **50.69%** | 21.61% |
| selfdrived | 27.38% | 52.37% | 20.25% |
| card | 43.26% | 25.43% | 31.31% |

These are kernel **per-thread** runtime/runqueue counters, not process totals or inferred waits. The three main threads consume about **98.34% of one core**, with core 4 **99.77% busy**. The inherited periodic selfdrived/card helper threads remain FIFO53/core4 but use only .32/.40% CPU in this sample. nrdr controlsd background workers use 2.16/1.39% across broader core placement with SCHED_OTHER, consistent with their explicit demotion; these are distinct from the main-thread 98.34% sum. Thread roles beyond the source/priority evidence are inferred, not captured Python stacks. Polling/storage is not cost-free, but this is not evidence that simply changing tuning refresh to 30 seconds would solve the deficit.

Observed publication rates: controlsState **98.923 Hz**, carState **99.523 Hz**, selfdriveState **99.555 Hz**. controlsState interval p99 is 16.203 ms and maximum 28.303 ms. All 2,986 sampled carState messages have valid CAN and no temporary/permanent steering fault. This is a near-startup, stationary/disengaged workload with an added low-priority observer, **not a reproduction of the active moving 85-86 Hz condition**. It confirms significant scheduling contention/headroom loss; it does not assign every lost moving update to a particular function or prove an optimization's benefit. No brake-DTC rescan was performed.

Sparse main-thread wait-channel samples show `hrtimer_nanosleep`. Source explains why without inventing a deliberate 15-ms control period: `msgq` revision `e7396e76dadbb49e374d4b664ff6bbb43a39bcb0`, `msgq/msgq.cc:437`, sleeps only when no polled message is ready; publisher `SIGUSR2` notifications interrupt that sleep on Linux. `ipc_pyx.pyx` releases the GIL while polling. `Ratekeeper.monitor_time` itself does not sleep. The residual wall-time column includes blocking/sleep and is not separately apportioned to IPC or GIL; sparse wait-channel counts are not duration measurements. Wake-to-run delay is captured separately by the runnable-wait counters above.

**Decision:** profiling establishes a real shared-core constraint and a smaller repeated-geometry cost, not a geometry-only explanation or a proven tuning-refresh fix. Before any scheduler/polling/tune change, profile card's larger hot path and evaluate a narrowly scoped, output-identical geometry-selection reuse candidate with live-setting/model/firmware invalidation preserved. Keep the moving-workload and measurement-overhead comparison open. No optimization, runtime deployment, commit, push or release was performed in this pass; installed checkout remains clean at `5c6467e526`.

### Five-minute stationary follow-up

With the user reporting the car outside, plugged into charging and left on, a **300.043-second** read-only sample completed without an early stop. Park, speed < .1 m/s, disengagement and fresh-state guards held throughout. The three production PIDs remained unchanged from the short sample. The observer again ran on cores 0-3 at nice +10; no actuation, live-input simulation, tuning writes, restarts, scheduling changes or deployment occurred. Artifact: `stationary-control-scheduler-5min.json` in the same private analysis directory. This records the user's setup, not independent validation of the charging interlock.

| Main thread | CPU execution | Runnable, waiting for CPU | Remaining wall time |
| --- | --- | --- | --- |
| controlsd | 27.78% | **50.39%** | 21.82% |
| selfdrived | 27.24% | 53.34% | 19.42% |
| card | 43.38% | 26.75% | 29.87% |

Core 4 remained **99.79% busy**, with the three main threads consuming about 98.40% of one core. controlsState averaged **98.605 Hz**, versus carState 99.491 Hz and selfdriveState 99.494 Hz. Across ten 30-second windows, controlsState ranged 98.30-99.11 Hz and controlsd runnable wait 50.03-50.59%: the contention persists beyond startup, without a progressive cadence decline in this sample. controlsState interval p99 was 16.371 ms and maximum 42.525 ms, so the near-100-Hz average does not imply uniformly timely updates.

Maximum-across-CPU temperature rose from 56.1 to 59.1 C; all 596 device health reports retained thermal status `ok`. Core-4 frequency at the interval boundaries stayed 1,689,600 kHz (not a continuous frequency trace). From the first to last 30-second boundary, controlsd RSS grew 83.61 to 84.12 MiB and selfdrived 71.88 to 72.39 MiB; card stayed 80.86 MiB. Device-wide memory usage changed from 65% to 64%. No large progressive memory buildup was observed, but five minutes cannot rule out a long-term leak. All 29,848 sampled carState records had valid CAN and no temporary/permanent steering fault; this was not a brake-DTC scan.

**Conclusion:** this reproduces the shared-core scheduling constraint after warmup, not a growing heat/memory problem over the observed interval. It remains a stationary/disengaged workload with observer overhead, not a reproduction or complete explanation of moving/active 85-86 Hz. Keep the card hot-path and active-workload attribution next; normal PTM, tune and runtime remain unchanged. Collection is finished; the user does not need to leave the car on for this sample.

## Card hot path and active-workload attribution

November 16 follow-up at unchanged `5c6467e526fd1607c81ad7ff2760ab484d9d9a2e`, opendbc `5320fe2df0d93a594e079d4f3669e45087f838f0`, msgq `e7396e76dadbb49e374d4b664ff6bbb43a39bcb0`. The user reported leaving the outside, charging car on overnight. This was bounded profiling, not an overnight monitor or authorization to actuate it. All native analysis guarded fresh Park, speed < .1 m/s and disengagement; no production source/parameter/scheduler changes, restart, ECU command, build or deployment occurred.

### Same-drive observations

`workload_cohorts.py` re-reads all 28 retained rlogs. Unlike the trace's default-zero speed when inactive, cohort speed comes from actual carState. Classification uses latest-prior state and agrees at both interval endpoints; procLog intervals can still contain brief transitions. Process CPU includes helper threads and is not a main-thread timing measurement.

| Moving cohort | Outbound inactive | Outbound active | Return inactive | Return active |
| --- | --- | --- | --- | --- |
| Selected controls interval duration | 43.30 s | 659.88 s | 38.52 s | 440.57 s |
| controlsState Hz | **99.11** | **84.89** | **98.89** | **86.12** |
| carState Hz | 99.53 | 99.31 | 99.44 | 99.32 |
| card process CPU, one-core % | 45.16 | 44.82 | 45.06 | 44.81 |
| selfdrived process CPU, one-core % | 27.42 | 27.38 | 27.34 | 27.33 |
| controlsd process CPU, one-core % | 31.66 | 32.47 | 31.38 | 32.56 |
| Mean CAN frames per incoming event | 48.75 | 48.73 | 48.79 | 48.74 |

Thus the deficit is associated with **active lateral computation, not movement alone**. Radar object counts also do not surge with activation (outbound 5.84 inactive / 5.62 active, return 5.31 / 4.40). These are observational cohorts, not matched randomized maneuvers. The near-constant process CPU does not imply constant per-update cost when controls publishes fewer updates.

### Card's steady workload

Three sequential 30-second live stack samples used the installed `py-spy`, `--nonblocking --gil --threads`, 97 Hz, with the sampler restricted to cores 0-3 at nice +10. Production threads were not paused or reconfigured. Card yielded 874 main-thread samples; 477 included state_update, 256 controls_update and 97 state_publish. Message conversion, CAN parsing, Honda decoding and publication appeared prominently. There were 338/215/108 sampler errors for card/controlsd/selfdrived, so these stacks locate work but are **not precise CPU percentages**; a GIL-owner sample can include a preempted thread. No native stacks were collected.

`native_card_profile.py` then executes real card state_update/state_publish/controls_update and Honda interface/parser/controller code against saved CAN, with native serialization into memory. It skips initialization/ECU interaction, denies publisher creation, workers and parameter writes, and uses saved parameter bytes. Each dataset has 2,000 frames with 300 warmup frames: parked outbound segment 0 (mean speed 0), moving return segment 7 (12.47 m/s). SHA256 values match the retained local logs (`420131397aaa5f43f9b38da688852cea51810b94ee89cbb3beace11ba1f91f74`, `b43366f39a6508badbd8f9fc13e9ee642b0fa852a1ed0ee7995c6b8c65fe9821`).

Uninstrumented mean CPU per step was **7.305/7.372 ms parked** and **7.442/7.501 ms moving** across baseline/repeat on cores 0-3. These are slower analysis cores, **not card's actual core-4 execution times**. Instrumented inclusive CPU per step:

| Work | Parked | Moving |
| --- | --- | --- |
| state_update total | 4.55 ms | 4.59 ms |
| controls_update total | 2.88 ms | 2.93 ms |
| state_publish total | .38 ms | .39 ms |
| CAN parsers, three calls combined | 1.55 ms | 1.55 ms |
| Honda car-state decoding | 1.22 ms | 1.24 ms |
| Interface/controller application | 1.79 ms | 1.84 ms |
| CarControlSP conversion | .86 ms | .86 ms |
| Speed-limit-assist update | .41 ms | .41 ms |
| CAN input conversion | .33 ms | .33 ms |

Rows overlap; do not sum the totals and nested components. Radar update is about .38/.39 ms inclusive of its CAN parser. Per-call stages were normalized to 1,700 measured frames, rather than mistakenly treating each parser/serialization call as one full frame. Stage instrumentation adds overhead; cProfile raises mean measured step CPU to 26.34 ms and supplies call-path evidence only. Identical numerical outputs and normalized outgoing CAN payload digests passed across modes within each dataset (three parked modes, four moving modes). Nothing was published onto vehicle CAN.

An initial replay used a Cap'n Proto CP_SP reader, unlike card's actual dataclass; its output is retained as `native-card-profile-preflight-cp-reader.txt` but excluded from the numbers above. Corrected replay restores the actual CP_SP dataclass and cached publication reader. Remaining limitations: one saved CAN event per step instead of unknown actual drained batches, latest-prior rather than recorded consumed subscriptions, fresh initial controller state, in-memory Params, no live IPC/polling or background refresh. Cold replay parser warnings are not live vehicle faults; output identity is profiling transparency, not historical command parity.

Source comparison with sunnypilot master `c6e564cdcd68dc6334381ac0d929133b1d824479` finds unchanged generic CarControlSP and CAN message-conversion helpers. Its opendbc pin `c0e74738a8068b2fc88c68f1f475887e1dec290f` also uses the Python CAN parser; current raw-bit extraction relocates the same algorithm from Signal's method. This does **not** establish identical stock runtime performance. The nrdr speed-limit helper's `is_honda` also eagerly evaluates the legacy `carName` fallback even when `brand` exists; avoiding that redundant lookup is a bounded candidate, not an implemented fix.

### Isolating the active lateral cost and measurement cost

`native_control_profile.py --paired --parked --max-frames 2000` uses the same return-segment inputs over 23.210 seconds. Each pass executes the full Controls calculation/publication path, with saved subscriptions and serialization to memory on cores 0-3, nice +10. One comparison removes only Testing's measurement core/wrapper in the isolated interpreter, using their unchanged production base implementations; another forces only lateral admission inactive with the same moving inputs. No device selection or live source changes.

| Isolated replay condition | Mean CPU per update, baseline / repeat |
| --- | --- |
| Active, measurement enabled | 5.949 / 5.983 ms |
| Active, measurement omitted | 5.675 / 5.692 ms |
| Inactive, measurement enabled | 4.920 / 4.965 ms |
| Inactive, measurement omitted | 4.724 ms (one pass) |

The active/inactive increase is **1.018-1.029 ms** with measurement enabled. The measurement-free active/inactive difference is about **.950 ms**; measurement adds .274-.291 ms total when active and .196 ms in the first inactive comparison. Thus roughly **.078 ms of the first paired activation penalty** is additional measurement work, not all 1.029 ms. This distinction matters: the logger has cost but is not the dominant explanation for the activation-specific increase in this replay.

All 2,000 active commands/angles/curvatures/accelerations and activity flags were exactly equal with and without measurement, including repeats; inactive outputs were separately equal within that group. Stage profiling places the PTM wrapper at 1.591 ms, its core .707 ms and feedforward .350 ms inclusive; before/after state capture totals .069 ms. Repeated geometry selection is .543 ms inclusive on this setup, and the extension parameter-refresh gate about .01 ms. These instrumented values cannot be summed as independent costs or compared directly to the earlier offroad 4.13-ms baseline: workload, device state and clock/scheduling conditions differ. Removing measurement also changes serialization size/traffic (controlsState 792 versus 352 bytes per frame), whose downstream IPC/logger cost is not reproduced here.

**Decision:** combined evidence supports a large steady card/selfdrived workload leaving insufficient shared-core headroom for the extra active lateral work. CAN arrival lag, increasing radar traffic and tuning reads are not supported as the primary activation-specific cause. Exact per-deadline attribution and restored 100-Hz driving operation remain unverified. Next evaluate narrow behavior-preserving reductions in redundant message conversion/static platform lookup and geometry selection, with full output parity and correct invalidation; retain required measurement evidence. Do not change gains, filters, nominal dt or production affinity to compensate before validating throughput.

Artifacts in the same private analysis directory: `workload_cohorts.py`, `workload-cohorts.json`, `sample_live_stacks.py`, `stationary-stack-samples.json`, `summarize_stacks.py`, `stationary-stack-summary.json`, `native_card_profile.py`, `native-card-profile-output.txt`, expanded `native_control_profile.py`, and `native-control-paired-output.txt`. Parameter hashes across both completed native replays changed only ordinary heartbeat/location/live-learning/onroad-uptime keys; no keys added/removed and no saved tune/model/controller setting changed. Analysis scripts pass syntax compilation. Investigation notes remain uncommitted; no optimization or release operation was performed.

After analysis exited, `profile_health_check.py` / `post-profile-health.json` verified the same three production PIDs running, Park/disengagement, thermal `ok` (maximum CPU 61.1 C), and 789 sampled carState records with valid CAN and no temporary/permanent steering flags. The brief conflating subscriber observed about 98.1 controls publications/s; it is a health check, not a full-frequency benchmark or DTC scan. All samplers/replays finished; no overnight observer was left running.

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

Before selection, all 375 stored keys were hashed. Only controller selection and its two generated controller/tuning reports changed beyond ordinary ping/model-sync timestamps and uptime. Model/settings/calibration hashes otherwise matched. The initial selection did not restart the manager; that omission caused the cached-schema failure documented above. The subsequent full-manager recovery and actual saved stationary/moving records supersede the original unverified next-drive assumption.

Recovery baseline: `d9b512af79cde1438e49dcea9200ece460cb5f1b`. C4 backup `/tmp/nrdr-ptm-measurement.kwi7pB/source-before.tar.gz` and `params-before.json` retained (temporary storage is not reboot-durable). Simple behavior rollback is selecting **normal PTM, ID 1, while parked**; it has no measurement payload and unchanged arithmetic. Source rollback, if needed, should revert the measurement commit explicitly, not reset branches or erase other changes.

## Next collection and decision

The original collection plan below is retained as context. The gas-station outing now supplies moving measurement data: finish the offline timing/event checks above before requesting another collection or promoting a change.

The user reports mechanic inspection and resolution of the brake/ABS/ACC faults on November 16, removing the previously unresolved-fault blocker. Hidden warnings alone are not verification. If warnings or abnormal operation recur, stop assisted testing and resolve the safety concern first. No failed corner or lane departure needs to be reproduced.

Once suitable for supervised collection, use the installed Testing measurement baseline and keep Pop v2, geometry, all filters and override settings fixed. Collect two ordinary 10–15 minute loops in daylight with clear lane markings, safe conditions, gradual left/right curves and normal slowing-entry/release transitions, broadly 5–15 m/s where legal and appropriate. Include normal manually driven turns; do not force tight turns under assistance. Retain at least 10 seconds of preceding/following history and subsequent turns; full routes are preferable. Park between runs. Aim for at least five clean repeated events each direction and enough normal curved driving to exceed the rack fitter's 300-second eligible-data requirement; failure to meet coverage is an observation, not a reason to force maneuvers.

Maintain ordinary hands-on supervision and intervene immediately whenever needed; never let a departure build for data. End assisted testing for unexpected pull, oscillation, warning/fault, abnormal brake/steering feel or repeated correction. Park before selecting normal PTM to revert. Do not clear fault codes or change the model/firmware/tune during collection. Record approximate intervention times and impressions after parking, not while driving.

Send both route links and retain/upload full rlogs plus road video. Required streams: initData/CarParams, modelV2, carControl/carOutput, controlsState with measurement v1, vehicleParameters, carState including yaw, deviceMotion, CAN/sendcan with EPS debug frames, Panda state/counters and GPS. Normal car logging is eligible; first verify payload presence and complete segments before further analysis.

Expected measurable result is **reproducible state and timing**, not different steering feel. Reconstruct each sampled core update to floating-point precision from the new consumed inputs; compare publication intervals and command ages against baseline before trusting the data. Determine whether mismatch-threshold crossings explain I holds/rebuild across entry, release and next turn; separate true same-command attenuation where lineage is unique. Re-run the tool suite above by route/model and compare like speed/direction cohorts. Repeated unpressed wheel/command phase error with good physical-map agreement supports testing dynamic/load/feedforward parameters next; an error tracking model/blended geometry instead redirects calibration work. Reject the measurement build itself if logging creates deadline gaps or control parity breaks. Do not introduce the unwind gate until its I/history and subsequent-turn regressions are addressed.
