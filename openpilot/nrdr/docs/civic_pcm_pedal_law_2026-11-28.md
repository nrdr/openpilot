# Civic Experimental PCM: pedal-like gas/brake transition (unvalidated on the road)

Applies to the Civic without interceptor on the Nidec Experimental PCM controller. Code: `opendbc/car/honda/civic_pcm.py` (`PedalLaw`, `road_load_fraction`), wired in `opendbc/car/honda/carcontroller.py`. Switch: `HondaCarConfig.civic_pcm_pedal_law`, default on; off restores the speed-target law. Analysis: `C:\Openpilot Workspace\analysis\civic-pcm-2026-11-28`.

## Problem

Measured on route `00000031--0fa3f0ec26`, 2026-11-28 (686 s in control above 18 mph):

| | Speed-target law | Clarity with pedal, 2026-11-14 |
|---|---|---|
| Brake command on | 27.9% of the time, 5.1 episodes per minute | 3.9%, 0.4 per minute |
| Planner request at brake onset | zero or positive in 26 of 58 | below −0.3 m/s² in 5 of 5 |
| Propulsion when the brake comes on | part throttle, cut in the same tick | at zero for 2.1 s already |
| `PCM_GAS` with a positive request | 190 or more 83% of the time | not applicable |

The brake decision used `request + g·sin(pitch)` with no road load, every brake command forced `PCM_SPEED = 0`, and `PCM_GAS` did not carry the amount of acceleration wanted.

## What the law does

1. Brake: the command is reduced by road load, the interceptor path's wind-brake curve at factor 1 (`nidec_brake_command`), with or without a lead. The eligibility flag and coast credit are not used. The learned wind factor is not used. The brake-gain fit is frozen while the offset applies.
2. Lift-off: for a negative request, or acceleration above the request by 0.05 m/s², `PCM_SPEED` is set a small lead from speed, `10 km/h per m/s²` of acceleration error, limited to −6 to +1.4 km/h. That keeps the PCM in its hold mode, where the lead acts as a throttle rate, instead of its release mode.
3. Drive: `PCM_SPEED` is 10 km/h above speed, which keeps the PCM in its acceleration mode, and `PCM_GAS` is the requested acceleration as a share of the PCM's ceiling at that speed.
4. Cap: the request is limited to that ceiling (0.76 m/s² at 30 km/h falling to 0.49 at 122 km/h) before it is commanded or integrated.
5. Integral: 0.25 1/s on acceleration error, clamped to ±0.15 m/s², frozen while braking, lifting off or saturated.
6. Speed error: 0.25 m/s² per m/s of (planner's present speed − speed), limited to ±0.3 m/s², added to the propulsion command only. Same error signal as the interceptor's Personal Pedal controller and its Econ highway gain, without that controller's integral. Before this change the non-interceptor path had no speed-error term: long control was feedforward only (`kiV` 0, request equal to the plan), and Personal Pedal requires the interceptor.

A request at or below −0.5 m/s² releases the throttle at once, as before. Any brake command above zero still sends `PCM_SPEED = 0` and `PCM_GAS = 0`. Below 6 m/s the speed-target law is unchanged; the two are blended up to 10 m/s. Launch, stopping, override, AEB and reference-freshness handling are unchanged.

## Where the numbers come from

Lead thresholds, the ceiling and the lift-off gain are from emulator probes of the 37805-5AJ-A520 firmware (`PCM_FIRMWARE_LAW_20261109.md`, section "accel-command law"): acceleration steps tracked within about 0.02 to 0.06 m/s², 1.3 to 3.4 s up and 0.3 to 1.7 s down, at 60 to 122 km/h. The integral gain is between the two probed settings (0 and 0.5). The road-load curve is the one the interceptor path uses; measured Civic lift-off retardation was 0.3 to 0.6 m/s² at highway speed on few samples.

## Command-level replay on the recorded drives

Same request, speed and measured acceleration as recorded under the speed-target law. Not a prediction of the car's motion.

| | Route 31, before | Route 31, replayed | Route 30, before | Route 30, replayed |
|---|---|---|---|---|
| Brake command on | 27.9% | 6.8% | 11.5% | 0.6% |
| Brake episodes | 58 | 16 | 15 | 2 |
| Planner request zero or positive at onset | 26 | 2 | 10 | 0 |
| `PCM_GAS` at 190 or more, positive request | 68% | 66% | 83% | 67% |
| Correlation of `PCM_GAS` with the request | +0.23 | +0.57 | +0.31 | +0.57 |

On these recordings the car ran a mean 0.4 to 0.6 m/s under the planner's speed, so the speed-error term is positive most of the time (mean +0.11 and +0.14 m/s²) and keeps `PCM_GAS` high. Without that term the replay gives 51% and 38% at 190 or more and a correlation of +0.73.

## Not established

- Closed-loop behaviour on the car or on the firmware-in-the-loop bench. Nothing here has driven.
- Behaviour with ECON on. The probes did not exercise the ECON throttle stages; on 2026-11-28 the PCM delivered a third to a half of the requested acceleration at full allowance with ECON on.
- Behaviour within a few km/h of the PCM's own set speed, where the PCM limits the target itself.
- Mode chatter from accelerometer noise around zero error (the probes were noise-free).
- With a lead the first brake count now waits for road load, as on the interceptor path. PCM lift-off takes longer than a pedal's, so requests between lift-off and −0.5 m/s² arrive later than before.
- Controller-level tests. The pure law has 12 tests (`tests/test_civic_pcm_pedal_law.py`); the existing Civic PCM regressions run with the switch off and still describe the speed-target law. The wiring in `carcontroller.py` compiles but has not been executed.
- The speed-error gain with the PCM's lag. A proportional gain of 0.25 1/s against a 1.5 to 2 s lag leaves a comfortable margin on paper; it has not been run.

## Test order

1. `pytest opendbc/car/honda/tests`.
2. Firmware-in-the-loop bench with the real carcontroller on the two recorded windows (route 31, 536 to 556 s and 589 to 611 s) and the standard scenarios, ECON on and off.
3. Supervised drive on a clear road, ECON off first.

## Rollback

Set `civic_pcm_pedal_law` to false in `HondaCarConfig`, or revert the opendbc commit.
