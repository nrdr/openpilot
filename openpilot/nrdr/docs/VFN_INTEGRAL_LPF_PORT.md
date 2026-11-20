# VFN integral and torque-filter adaptation

Local implementation for `nrdr-architecture-development`, September 13, 2026.
This is a logic change, not a gain/preset migration or a road-validated tune.

## Source and scope

The steering reference is JamesL787/openpilot `vfn`, pinned to
`662933847fcad19625dcfb8a6549331222087155`:

- [Integral accumulation and reset](https://github.com/JamesL787/openpilot/blob/662933847fcad19625dcfb8a6549331222087155/common/pid.py)
- [Lateral freeze policy and pre-request LPF](https://github.com/JamesL787/openpilot/blob/662933847fcad19625dcfb8a6549331222087155/selfdrive/controls/lib/latcontrol_pid.py)
- [Reason for removing the car-side LPF](https://github.com/JamesL787/openpilot/blob/662933847fcad19625dcfb8a6549331222087155/opendbc_repo/opendbc/car/honda/carcontroller.py)

The separately supplied [753fe437 commit](https://github.com/JamesL787/openpilot/commit/753fe43726f5d3d69a4b40fcd20fb97bb68f44d5)
changes Bosch-A radar range conversion, not steering. It is not included in this
adaptation. The user clarified that it was informational and must not be
cherry-picked as part of this rollout.

## Adaptation to NRDR

- NRDR lateral PID scales Ki during accumulation instead of multiplying the
  already-stored integral at output. The shared upstream PID and non-NRDR users
  remain unchanged. Base anti-windup is inherited without modification.
- Requested-angle unwind alone no longer freezes I. Driver override, reported
  steering limiting, the existing low-speed thresholds, and NRDR's optional
  stiction guard remain.
- Selecting zero I clears stored I, including while another guard freezes
  updates. Modified-EPS I resets below 2 m/s; inactive NRDR PID resets its state.
- The existing first-order torque LPF now runs after lateral PID/torque blending
  and NRDR's live-edit transition, before `carControl.actuators.torque` is assigned.
  This placement differs from VFN's PID-local placement to retain filtering for
  all previously filtered Honda torque-controller paths, including Clarity's
  hybrid. Non-Honda torque paths retain only their existing live-edit transition.
- Honda's car-side LPF is removed, so it cannot filter a second time or create a
  command/output mismatch from comfort filtering alone. Driver-override fade and
  optional torque rate limits remain car-side, after the filter, as in VFN.
- The filter reuses the existing Honda background settings provider, with an
  explicitly non-refreshing read in the control loop. Existing keys, bounds,
  defaults, speed bands, UI, and saved values are unchanged. LPF enable and time
  constants remain live; no new polling or filesystem reads enter the loop.

No VFN gain defaults, rate feedforward, target-angle limiter, SR tables, dynamic
output shaping, or radar changes were imported. Existing NRDR blend and shaping
are retained. The earlier uncommitted Civic measured-curve work is separate and
was not edited by this adaptation.

Same settings do not mean identical steering behavior: nonzero I scaling now
changes accumulation rate, zero I really clears state, and override fade follows
the LPF. Reduced filter-related freezing can permit more correction. These
changes require native integration and controlled validation before release.

## Validation and release gate

Focused local suite: **116 passed**. Lint checks passed for all files touched by
this port. Root and submodule whitespace checks passed.

The local mathematical and isolated handoff tests cover base-PID parity at unit
I scale, scaled accumulation, freeze guards, zero-I reset, low-speed behavior,
saturation/anti-windup, LPF response, live edits, sign changes, reset, non-Honda
bypass, and retained override/rate-limit differences. Honda steering methods in
the handoff test execute directly from production source, without their unrelated
native CAN/serialization imports; this is not a full vehicle-process test.

A 100-frame, 60-mph synthetic command ramp with tau 0.07 reproduces 91 false
limiting-threshold crossings with the former filter placement and none with the
new same-frame handoff. The new ramp also stays below the threshold with one
frame of output feedback latency. This proves the isolated mechanism, not its
frequency in real route logs or closed-loop stability.

Full native tests are also extended in `test_live_pid_updates.py`,
`test_live_friction_pipeline.py`, and `test_opendbc_boundary.py`. The isolated,
offroad C4 suite passed **637 tests and 153 subtests**, including these integration
tests, Civic measured-curve/tooling coverage, Sunnylink compilation, and a native
Cap'n Proto regression for the developer UI's default-to-PID union transition.
One optional `jsonschema` test was skipped. The previously confirmed baseline
Toyota handcrafted-profile capability failure was explicitly deselected.
All 85 monitored settings/model/calibration hashes and the installed checkout
were unchanged by testing. Lint and whitespace checks passed for the candidate.
This is not a road test or proof of closed-loop stability. Deployment and
publication results are recorded separately in the release handoff.

The root repository and its `opendbc_repo` submodule contain paired changes.
They must be packaged together; mixing versions could leave a duplicate LPF or
remove filtering entirely. Rollout is scoped to the C4, nightly, and September 13
staging; `350`, `clean`, older staging branches, and radar code remain unchanged.
Existing tuning values and model selection are preserved. The provisional Civic
measured curve becomes available, but is not selected automatically.
