# Civic Nidec: command replay, 2026-11-04

**Supported:** veto opposing PCM propulsion fields in host stopping/off. **Not established:** a stronger universal stop ramp, an additive brake gain,
or a universal near-set taper. This tool changes no running process or setting. All outcomes below are recorded outcomes under A, not predictions under B.

## Native HUD replay of fc8b77b51

All 22 segments of 18c and 31 of 18d use recorded clean root 76bced854e (Honda e515aa289). Patch scope is the speed-led, non-interceptor Nidec Civic.
While longActive, the proposed veto clears PCM_SPEED and PCM_GAS unless the host state is PID or starting. It also inhibits the launch governor. We overlay
the output veto at real ACC_HUD packet times; we do not simulate subsequent governor state. We match each bus-128 echo to a unique preceding bus-0 send
within 50 ms with identical speed and gas fields. The host state is the latest valid carControl at/before that send (age <=50 ms), not an instrumented
controller-receive timestamp. The window clock is the echo timestamp relative to route init. No resampling for this table.

| Route / interval (s, half-open) | Active HUD packets | Veto applies | Nonzero packets changed |
|---|---:|---:|---:|
| 18c 450.993–453.446605, first interrupted stop | 25 | 25 | 0 |
| 18c 526.065–532.427987, re-engagement | 63 | 63 | 14 |
| ↳ still stationary before 527.062 | 10 | 10 | 10 |
| ↳ first motion 527.062–527.483 | 4 | 4 | 4 |
| 18c 957–968.159476, PID approach before pedal | 111 | 0 | 0 |
| 18d 740.683–742.973, successful approach | 22 | 22 | 0 |
| 18d 743.004–788.169, stationary hold before plan releases | 449 | 449 | 0 |
| 18d 788.181–791, valid PID departure | 28 | 0 | 0 (all 28 positive commands retained) |

The 14 re-engagement echoes had PCM_SPEED 1.0 m/s, gas allowance 10–190 counts, and no physical brake before the first positive brake at ~527.483 s.
All 14 would have both fields zero. This removes a command conflict; it does not prove the PCM caused all creep or that zero gas would hold the car.
Full-route totals: 18c **16/8,040** active matched HUD packets changed (90 vetoed), 18d **0/7,488** (472 vetoed).
The two other 18c echoes, t=553.15096/1091.48167 s, join to active/off and each carry gas 7 counts. Off is a transition: exact input-consumption
timing matters more than for a sustained stopped request. Of all echoes, 12,961/12,962 and 18,139/18,139 matched; unpaired is not unchanged.
JSON includes every changed echo as [segment, route seconds, state, recorded PCM_SPEED m/s, recorded PCM_GAS counts].

## Physical brake: build before standstill vs release

Accelerations are m/s²; brake and pressure are raw counts and are not interchangeable. Three 18c pedal takeovers span only **two** low-speed encounters.
The first two already had positive brake, a running pump and pressure above resting level before the driver pressed. At the third the host was still in PID.
The matched source's stopping rise limit is 0.00042 normalized brake per 50 Hz tick, or 5.376 counts/s. The observed ramps were 5.37, 5.36 and 5.39
counts/s for P07, P08 and the *successful* 18d stop. The successful case entered stopping already at 31 counts vs 12 on P07; it subsequently held ~46 s.

| Frozen rolling interval | A: brake first → last | Mean request / measured | Samples with room under doubled rise ceiling |
|---|---:|---:|---:|
| 18c 451–453.24 | 12 → 24 | −0.595 / −0.066 | 72/112 |
| 18c 527.9–532.22 | 3 → 26 | −0.846 / −0.007 | 195/216 |
| 18d 740.70–742.80, successful | 31 → 42 | −0.780 / −0.263 | 66/105 |
| 18c 963–967.95, PID | 0 → 13 | −0.275 / −0.035 | 0/248 |

The envelope requires a close lead, a matched consumed stop plan, measured acceleration above requested acceleration (less slowing), zero HUD speed
and gas, and an observed rising brake over the preceding 0.6 s. Extra room is capped at eight counts. It is **not** reconstructed uncapped brake demand:
the true change can be anywhere from zero to that bound. The successful stop also meets the trigger. No specific rise rate, stop gap, or pedal-free final
distance follows. The earlier release-tail replay changed **0/7,082** qualified low-speed frames; extending a release cannot initiate missing brake.

## Highway undertracking and historical regression

18c 585.03–590.45 s: 271/271 samples with zero brake, pressure1 mean 103, request −0.780 vs actual −0.043. Lead range fell 46.75 → 30.69 m.
18b 225–233 s: 400/400 zero, request −1.186 vs actual −0.176. At both windows, requiring zero numeric PCM_SPEED **and** zero gas misses every sample.
With no positive speed lead (PCM_SPEED <= ego) and zero gas, all 271 and 400 pass the sustained-error and settled-pressure diagnostic. The gate was already
satisfied before each window. This is a benchmark for comparing the separate DBC bench implementation, **not** another brake law.

The rejected a05e57683c/d5485d618 did more than add feedback: it replaced the wind-subtracted, gain-scaled baseline with the grade-adjusted pre-wind base,
then applied P/I. Its feedback rise limiter did not bound growth of that base. Replaying only its negative rolling PID slice on frozen observed zero-brake
inputs gives normalized-effort-equivalent means of **254.9 and 251.7 counts out of 255** in those windows. This is before final packet release limiting;
it uses 50 Hz hysteresis approximation, zero seeding per contiguous slice, and measured motion that cannot respond to the alternative. It is not an exact
whole-controller replay, a measured bad-patch drive, or predicted jerk. The archived 188/189 runs with that build were stock ACC.
Counterexample: in the evening drives there were 2,094 otherwise eligible zero-brake samples with request <−0.15 and measured accel already within
0.1 m/s² of request; the historical slice still adds positive effort on 2,017. Do not conclude that every negative request needs friction.

## Near-set acceleration and stock coverage

Across all nine previously screened approaches, the offline one-second projection capped the speed target on at least some cruise-selected samples in every
approach. It did not alter either gas allowance or a lead-selected frame. On 18d/13 the command trim reached 6.38 m/s (46 sampled ticks); the original
host was already tapering: at ~1 mph below set, request +0.44 vs actual +0.67, allowance 198. At crossing, +0.009 vs +0.55, allowance 133. This was
a steady **96 km/h** setpoint (displayed 60 mph). But 18c/10 never crossed and the same cap still reduced its target by up to **6.02 m/s** (51 ticks).
18c/05 had already cut allowance 25% at 4.20 mph below set. These are counterexamples to blanket early lift. Neither Honda internal integration nor safe
gas calibration is identifiable. The retained powertrain sidecars are ECU estimates, not measured wheel torque.

Six archived stock routes (218 distinct segments, 332,768 engaged/pedal-free valid camera-command samples) yielded **no >=0.5 s** active approach
with ego <4 m/s, lead within 22 m and |lead speed| <1 m/s. For the 271-sample 18c closing window, zero stock samples matched joint 2 m/s speed,
1° pitch, 10 m range and 2 m/s relative-speed bins. Relaxing range/closing rate left 330 stock samples with the same speed/pitch cells and a lead;
only five had positive camera brake. Do not derive a stock target, stop gap, or matched gain. As *unmatched* positive controls, 147/1156.38–1161.62
had mean command 31.48, pressure1 peak 129 and net acceleration −0.099; 189/1659.814–1666.694 had mean 67.09, peak pressure1 166 and −1.073.
These confirm that stock does build pressure, not what it would have done in the OP windows.

## Reproduction

From the worktree root, with NumPy installed and the completed local archives:

```powershell
$base = 'C:/Users/brett/.codex/tmp'
$py = "$base/civic-brake-20261104/venv/Scripts/python.exe"
$env:CIVIC_REPLAY_ARCHIVES = $base
& $py -B -m unittest -q openpilot.nrdr.tests.test_civic_pre_stop_replay openpilot.nrdr.tests.test_civic_pcm_brake_shadow
& $py -B -m openpilot.nrdr.tools.civic_pre_stop_replay "$base/civic-evening-20261104" "$base/civic-brake-20261104/deep-scan-v3/segments" "$base/civic-brake-20261104/deep-scan-v2/segments"
```

The runner checks segment inventories and source metadata, including the evening manifest hashes; it does not redownload or rehash original rlogs.
It reuses the saved nine approach definitions to avoid selecting on the alternative's outcome. Non-HUD results use causal 50 Hz aligned samples, exact
plan IDs where relevant, finite freshness bounds, segment resets and unchanged Panda block counters. Frames are correlated exposure, not independent trials.
