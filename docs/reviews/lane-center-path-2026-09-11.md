# Delay-aware lane centering — development source only

Branch: `codex/lane-center-path-20260911` in `nrdr/openpilot`.
Base: `8c3e4c0e155ec8119a3dd6f5d4a600657451abe9`, the private C4 stability build.

**Not a road-qualified release. Not activated on the C4 or published to nightly.**
The feature remains disabled by default; an existing enabled preference is preserved.

## Implemented

- Fit lane-minus-model path error across multiple samples using both confident boundaries. Coherent model/lane curves cancel.
- Both model pipelines publish their actual steering-action time, including model-specific smoothing, and the exact matching model-message identity.
- Accept only matching, valid timing. Missing, legacy, mismatched, invalid, or excessive timing fades out only the lane overlay. This is not a new global communication-health or engagement dependency.
- Locate actuation using the model's position time/distance samples. Only absent/empty time arrays use the explicit constant-speed approximation; malformed nonempty arrays fail closed.
- Fit the response 0.25–1.5 seconds after actuation, requiring at least one second of valid common preview. Never extrapolate beyond available lane/model coverage.
- Remove the redundant 0.4-second feedback filter. The combined model and lane command still passes through the existing total-curvature jerk/acceleration limiter. Keep smooth release on confidence, timing, speed, and signal loss.
- Preserve correction caps, driver override, lane-change suspension, both-boundary checks, and model validity checks. Bypass during lateral maneuver overrides. Zero strength clears residual correction even if timing disappears simultaneously.
- Check corridor width across multiple horizons; weight confidence continuously and add rearming hysteresis. Width history affects confidence, not the lane midpoint.
- Cache geometry at model rate. Add `TIME` and `SHORT` diagnostics without another settings toggle.
- Add source-only GitHub numerical/wiring checks. They do not compile, release, mutate branches, or access devices.

This adapts ideas from [phr00t's lane planner](https://github.com/phr00t/openpilot/blob/oldbranch/selfdrive/controls/lib/lane_planner.py) to the current action-based stack, not a drop-in port of the [legacy lateral MPC](https://github.com/phr00t/openpilot/blob/oldbranch/selfdrive/controls/lib/lateral_planner.py). At 100% strength, correction caps and Model Break-In still apply; this is not exclusive lane-derived steering or a promise of exact physical position. Catpilot stabilization is out of scope.

## Restricted timing envelope

The published action-time ceiling is **0.475 seconds**, corresponding to the conservative synthetic test's 0.4-second physical delay plus 0.075-second perception/action timing. It is total published action time, not merely a user-entered software-delay setting.

Above this limit, the overlay fades toward the original model command and shows `TIME`. Do not raise the limit without revalidating the closed loop. This guard does not repair combinations outside the supported range; it prevents the overlay from operating there.

A 60-second simulation at 40 m/s, 0.5-second physical delay, and full strength retained an approximately 0.44 m side-to-side limit cycle despite passing the short test and respecting correction caps. That scenario remains an explicit opt-in, gate-bypassing extrapolation test with the original strict failure bound, not supported behavior.

## Verification and limitations

- Combined local numerical, settings, and timing suite: **268 passed, 20 subtests passed, 2 skipped**. The two skips are the explicitly unsupported, opt-in mirrored half-second-delay extrapolations described above.
- Native C4 runtime: **79 controller/schema checks passed** with candidate schemas/modules loaded from an isolated temporary directory, including actual Cap'n Proto timing serialization.
- Supported long-duration numerical envelope: **36/36 cases passed** (60 seconds each): 40 m/s across 0.1–0.4-second physical delays, strengths 0.3/0.5/0.7/1, and both signs of initial offset; plus 12 and 25 m/s at 0.4-second delay/full strength/both signs.
- The numerical harness uses ideal lane detection, a conservative 75 ms-old perception state, explicit actuation delay, and the actual shared curvature limiter. Its zero neural-model steering action and simplified bicycle dynamics do not prove compatibility with real learned steering, obstacle avoidance, tire/EPS response, or camera calibration.
- Offline replay of two highway segments (1,963 model frames; maximum recorded speed about 29.1 m/s) passed finite-output and correction-cap checks at strengths 0.3/1 and Model Break-In 0/1.
- Those legacy logs lack the new timing fields. Replay used an **explicit 0.275-second timing assumption** and forced lateral availability only for offline sensitivity. It does not verify actual steering response or the new live cross-message timing path.
- Replay-generated `modelInvalid` classifications include the harness freshness rule and are not a diagnosis of the drive's communication alerts.
- Candidate geometric work measured about 2.1–2.2 ms at p95 for new frames, 0.19–0.20 ms for cached ticks. These are isolated off-road measurements, not whole-system scheduling certification.

Before deployment/release: hardware-in-loop or controlled-course validation, actual model-action interactions and message-skew checks, splits/poor markings/sharp or banked curves, and vehicle-specific Clarity/Lexus testing. The broader communication-alert investigation is separate and is **not claimed fixed** here. Existing nonfinite-base-action handling outside the overlay is also not reworked.

## Historical failure

The first prototype (`0a4d79efe5`) passed existing tests but failed a 12-second delayed loop at 25 m/s, full strength, and 0.4-second actuation delay: 1.7074 m excursion and 1.4988 m final error. It was never activated. Temporal misalignment and the extra feedback filter motivated the revised architecture and longer tests.

## Reproduction

```text
python -m pytest -p no:cacheprovider openpilot/selfdrive/controls/tests/test_lane_center_path.py openpilot/nrdr/tests/test_lane_centering_stack.py openpilot/nrdr/tests/test_model_timing_metadata.py openpilot/nrdr/tests/test_lane_timing_consumer.py -q
python openpilot/sunnypilot/sunnylink/tools/compile_settings_ui.py --check
```

Native checks use `openpilot/tools/diagnostics/lane_centering_native_check.py`; legacy-log sensitivity uses `lane_centering_replay.py`. Both require fresh off-road/no-output state. Neither changes the live checkout, installed branch, user settings, model files, safety configuration, or CAN outputs.
