# Lane-center path prototype — deployment held

Status: **not drive-ready; not installed into the C4's running checkout; not published**.

Base: `8c3e4c0e155ec8119a3dd6f5d4a600657451abe9`, the private C4 stability build.
Working branch: `codex/lane-center-path-20260911`.

## Implemented

- Fit a bounded curvature correction to lane-minus-model path error across 17 preview samples instead of one endpoint.
- Require both lane boundaries; preserve the actual midpoint when their confidence differs.
- Check width over multiple horizons, continuously weight confidence/uncertainty, and add confidence rearming hysteresis and filtered width history.
- Cache geometry at model rate while retaining 100 Hz output smoothing and engagement/driver checks.
- Preserve raw/final correction caps, downstream curvature limits, driver override, lane-change suspension, and model validity checks. Bypass this controller during lateral maneuver overrides.
- Update the existing strength descriptions on-device and in Sunnylink without adding another toggle.
- Add numerical tests and a read-only, off-road-guarded log replay tool.

This adapts ideas from phr00t's legacy lane planner to the current action-based control stack. It is **not** a drop-in port of the legacy lateral MPC and does not promise exclusive lane-derived steering at 100% strength. Existing limits and Model Break-In still apply. Catpilot stabilization is out of scope.

References:

- https://github.com/phr00t/openpilot/blob/oldbranch/selfdrive/controls/lib/lane_planner.py
- https://github.com/phr00t/openpilot/blob/oldbranch/selfdrive/controls/lib/lateral_planner.py

## Verification

- Native controller regression suite on the C4, loading the candidate from an isolated temporary directory: **77 passed** using `unittest` and the installed cereal/native runtime.
- Local settings/stack and new numerical suite: **36 passed, 1 failed, 20 subtests passed**. The failure remains enabled, with its original bounds.
- Sunnylink generated metadata matches its source; Git whitespace check passes.
- Offline replay of two local highway segments (routes `00000041--650904f9fd`, `0000004c--adbfcb4969`), 1,963 model frames total, maximum recorded speed approximately 29.1 m/s: finite outputs and correction-cap checks passed for strengths 0.3/1.0 and Model Break-In 0/1.
- Replay forced lateral availability solely for offline sensitivity. It is not a closed-loop driving test. Replay-generated `modelInvalid` classifications include the harness's freshness rule and must not be interpreted as a diagnosis of the drive's communication alerts.
- On that replay, candidate fresh-frame work was approximately 1.9–2.0 ms at p95, cached ticks approximately 0.19–0.20 ms; installed-controller ticks were approximately 1.3 ms. These are isolated off-road measurements, not whole-system scheduling certification.

## Blocking result

The synthetic straight-lane bicycle test starts 0.60 m from center, with perfect boundaries and no model break-in:

| Strength | Actuation delay | Maximum absolute position | Final position at 12 s | Result |
| --- | --- | --- | --- | --- |
| 0.30 | 0.20 s | 0.600 m | -0.0969 m | Pass |
| 1.00 | 0.40 s | 1.7074 m | -1.4988 m | **Fail** |

The second case exceeds the unchanged 1.2 m excursion and 0.3 m final-error requirements. Although the simulation is simplified, growing lateral error is a reason to withhold deployment, not to weaken the test or suppress alerts.

Review also found an action-timing mismatch: the new correction fits current-frame path error over roughly 0.25–1.0 seconds ahead, while standard modeld targets actuation at live delay plus `1.5 * DT_MDL` (currently 0.075 s). Some model variants add their own smoothing delay. The correction itself also has a 0.4-second filter. At larger delays, the fit can target a region the new steering action cannot affect.

Next gate: design and verify a delay-aware, sufficiently long post-actuation preview; account for model-variant timing; rerun closed-loop speed/delay/strength/confidence sweeps, then real-log replay and startup checks. No road qualification has been performed.

## Device state and preservation

Only isolated test/replay artifacts were copied to `/tmp/codex-lane-path-validation.eYQL6l`; none were activated. No branch updates, live source edits, settings changes, reboots, CAN commands, or publishing were performed.

Post-test read-only check: C4 still reports commit `8c3e4c0`, branch `nrdr-c4-stability-09.11.2026`, off-road, ignition false, Panda `noOutput`, and no required processes stopped. This is an off-road health snapshot, not confirmation that the previously reported on-road communication issue is resolved.

Reproduce the local gate:

```text
python -m pytest -p no:cacheprovider openpilot/nrdr/tests/test_lane_centering_stack.py openpilot/selfdrive/controls/tests/test_lane_center_path.py -q
python openpilot/sunnypilot/sunnylink/tools/compile_settings_ui.py --check
```

The first command is intentionally red until the delayed-loop failure is fixed.
