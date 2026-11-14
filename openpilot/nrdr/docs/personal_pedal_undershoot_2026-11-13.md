# Personal Pedal speed undershoot — November 13, 2026

## Finding

The observed 57 mph plateau with 60 mph displayed is explained by the saved **Cruise Mismatch Correction of 95.0%**, not a disabled integral. Both route-start parameter snapshots contain 95.0%; the device still holds that value. This inspection does not establish when or why it was selected.

The logged setpoint is 59.713771 mph (approximately 96.1 km/h). The planner multiplies it by 0.95, giving **56.728083 mph**. On the latest steady interval, measured speed averages **56.726859 mph**, and the controller's speed reference averages **56.725150 mph**. Logged cluster speed is 57 mph throughout that interval.

## Evidence

C4 `comma-394684e0`, installed checkout `991cfb2`. Route initialization identifies running commit `184906c1a1`, Honda Clarity, Cheddar, and Personal Pedal selection 3; the relevant controller/planner/PID sources are unchanged between those commits. Reviewed all qlogs from the latest three drives, then full logs from segments 3–4 of `000001e2--9cd14acea6` and 4–5 of `000001e3--076f16dd40`.

Two fixed-setpoint full-rate windows, with times relative to the first qlog message:

| Measurement | Earlier drive, Relaxed | Latest drive, Aggressive |
| --- | --- | --- |
| Route | `000001e2--9cd14acea6` | `000001e3--076f16dd40` |
| Window / segment | 207–237 s / 3 | 260–300 s / 4 |
| Control samples | 2,557 | 3,362 |
| Effective cruise target | 56.728083 mph | 56.728083 mph |
| Mean measured speed | 56.834788 mph | 56.726859 mph |
| Mean PI speed reference (`deprecated.vPid`) | 56.613817 mph | 56.725150 mph |
| Integral contribution (`uiAccelCmd`), min–max | 0.577161–0.945174 m/s² | 0.423872–0.580358 m/s² |
| Mean proportional contribution | −0.058825 m/s² | −0.001311 m/s² |
| Mean feedforward contribution | −0.047823 m/s² | +0.000566 m/s² |
| Final acceleration request, min–max | 0.419205–0.947270 m/s² | 0.304296–0.887039 m/s² |
| Logged gas output, min–max | 0.041006–0.279193 | 0.010636–0.212080 |

In both windows, longitudinal control remains active in `pid`, with no accelerator/brake override, no reported lead, Experimental Mode off, and both planner source fields reporting cruise. Brake output is zero and no final request reaches the −4/+2 m/s² controller limits.

The integral moves both upward and downward, without resets in these windows. Consecutive logged increments match `Ki(v) / Kp(v) * P * 0.01` within approximately **6 × 10⁻⁸ m/s²**, consistent with log float precision and the nearest car-state sample. It is actively integrating the controller's speed error, not frozen or omitted from the request.

## Code path

- `nrdr/features/longitudinal/longitudinal_planner.py::_refresh_settings` reads `NrdrCruiseMismatchCorrection / 100`.
- `NrdrLongitudinalPlanner.cruise_target` multiplies the selected cruise target by that factor.
- `selfdrive/controls/lib/longitudinal_planner.py::update` applies it before MPC/cruise acceleration calculation; `get_cruise_accel` uses corrected target minus measured speed.
- `nrdr/features/longitudinal/personal_pedal.py::_pid_accel` integrates the resulting speed-reference error, and `controlsd.py::publish` logs the I term as `controlsState.uiAccelCmd`.

This is not evidence that every aspect of Personal Pedal matches the old controller. Historical trajectory interpolation, deadzone and feedforward differences remain separate from this particular plateau. Directly substituting future MPC speeds would also require respecting modern final arbitration; these logs contain future MPC speeds above the winning cruise target.

## Next action

Return Cruise Mismatch Correction to **100.0%**, with user approval or through the user's own setting change, before evaluating speed tracking again. Keep Kp/Ki unchanged for that comparison. No controller, model, saved setting or device file was changed; no build, push or deployment was performed.
