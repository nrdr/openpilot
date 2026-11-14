# PTM settings consolidation and Experimental PCM proposal

Status: implemented and validated; development publishing and C4 deployment authorized, with installed checks pending. The cleanup and default migration are implemented; the proposed PCM mode strategy below remains research. The pedal PI module, gains, speed reference and feedforward are unchanged. Model selection, vehicle setup, privacy and remote access are excluded from the migration; no release branch or release script is changed.

## Confirmed scope

The longitudinal selector shows, in order (only supported choices are selectable):

1. Standard
2. MVL Live Learning Gas
3. Bosch-A Radar
4. Nidec Experimental PCM
5. PTM Pedal Interceptor

Existing IDs are retained: PTM Pedal remains ID 3 and Nidec Experimental PCM is ID 4. The latter enables the existing Experimental shaping path alongside MVL learning. Vehicle eligibility remains authoritative: it supports the non-interceptor Nidec Civic, not every Nidec merely because of its label. The one-time approved defaults select PTM Pedal or MVL, never Experimental; users can select Experimental afterward.

| Area | Requested result |
| --- | --- |
| Pedal controller | Rename Aragon's Personal Pedal to PTM Pedal Interceptor; retain exact speed-error PI gains, reference, feedforward, output limits, and brake/override interlocks. |
| Pedal Wind Brake | Grey out for PTM Pedal Interceptor. Enforce today's gas-only pedal formula internally, retaining separate brake-side wind compensation. Do not turn off both forms of compensation. |
| Keep Feedforward Static | Grey out for PTM Pedal Interceptor; retain its current fixed feedforward behavior. |
| Live PID tuning | Editable only for Standard; preserve inactive saved values rather than reinterpret them as PTM gains. |
| Full Nidec Brake Authority | Show only for Standard; use the enabled behavior internally for the other supported controllers without changing platform safety limits. |
| Roen acceleration limits | Remove the option and runtime override; retain historical values in notes below, not as a new personality profile. |
| Dashboard Variant B | Remove the no-op option. Do not implement the Pilot display fix yet. |
| PCM deadzone | Remove the control and its Experimental speed-target transform; retain any necessary registered tombstone for old saved values. Do not add a new deadzone to the pedal controller. |
| PCM shaping control | Move the current Experimental selection into the longitudinal selector. Do not implement the proposed new PCM strategy as part of this UI move. Resolve the old ECU-Matched selection and MVL-plus-shaping migration explicitly. |
| Main-menu help | For Apply Suggested Settings, Force Update, and Prevent Automatic Shutdown, use Sunnylink's existing `details` field rather than inline descriptions. Keep the shutdown/battery warning in the help. Native interfaces retain accessible tap-to-view help. |
| Audio | Rename June 2026 to Legacy; retain sound-pack ID, assets, and matching volumes. |
| Steer filters | Make Legacy Steer Delta Rate Limiter unavailable under PTM lateral control; ensure stale saved values cannot apply the retired filter there. |
| Override defaults | Straight/curve thresholds 1200/1200; assist pass-through on; fade down 0.1 s, fade up 1.0 s; retained torque 0%. |
| Cruise and stopping | Default cruise correction 100%; extra stopped lead gap 1.0 m; stopping rate 30 in its stored hundredths representation, stop acceleration -2.0 m/s², planner stopping rate 0.3, stopping/starting speeds 0.5 m/s. These were read from the C4, not inferred from UI labels. |
| Lane centering / model | Blendful suggested; OPM10V3 requested for first-install C3X download. Do not replace an existing model selection or change the C4 model default without a separate decision. Physical C3X model execution remains unverified. |

## Steering-ratio simplification

Only two controls remain:

- Primary Steer Ratio Source: **PTM (Auto)** by default, or **Comma's Learner (Legacy)**.
- **Model-Specific Blend**, on by default. Suggested concise description: “Applies model-specific steering-ratio compensation. Off uses the primary source unchanged.”

The user confirmed the blend applies **only to PTM (Auto)**; Comma's Learner remains unchanged. Reuse the existing model-family eligibility used for Optimized Lane Changes, independently of that feature's saved toggle. Big/Chestnut and newer Deep RL models remain unblended.

For an eligible model and a verified car, interpolate from the PTM on-center ratio to the published endpoint over actual center-to-full-lock steering-wheel travel. Half travel uses the average of those two values. Both steering directions and measured/desired angle conversions must share the same invertible mapping; do not apply firmware linearization a second time to a ratio that already incorporates it.

Verified initial references:

- [Honda Clarity 2018 specifications](https://hondanews.com/en-US/releases/release-4ddb58f0247c42a4a5d9a6177c9b5ec8-2018-honda-clarity-plug-in-hybrid-specifications-features): 12.72:1 and 2.41 turns lock-to-lock. Assuming symmetric travel, center to lock is 433.8 degrees. Honda's table lists a steering ratio but does not explicitly identify it as an instantaneous full-lock ratio; its use as this blend's endpoint is the requested tuning choice.
- [Honda Civic sedan 2016 press kit](https://hondanews.com/en-US/honda-automobiles/releases/release-ee5aa8e28ba44ca186ef015977dc9db2-2016-honda-civic-sedan-press-kit-overview): explicitly describes 10.93:1 at full off-center rotation. [2018 Civic sedan specifications](https://hondanews.com/en-US/honda-automobiles/releases/release-fff4ed8cd535421db25a9b1509185c1b-2018-civic-sedan-specifications-features): 2.22 turns lock-to-lock, giving 399.6 degrees center to lock if symmetric. Do not apply this spec indiscriminately to Si, Type R, or other racks.

The retired hybrid implementation switched sources over five degrees; its 250-degree Clarity manual endpoint was not full lock. Neither is used by the new blend. Historical measured curves and their evidence documents remain for reference but are no longer selectable. Old Manual/Measured choices resolve to admitted PTM geometry or Comma's learner; old manual/hybrid parameters are ignored and rejected by remote writes.

The blend uses the existing angle-source forward/inverse functions. Rack slip compensation remains intact, with the same mapping used by lane-change shaping. Blend Off and newer-model paths retain the original PTM map. This model-specific compensation is a requested tune, not a new measured rack calibration or a claim of donor-output parity with Blend On.

| Admitted EPS family | Published endpoint / lock-to-lock | Official reference |
| --- | --- | --- |
| Clarity TRW-A020 | 12.72 / 2.41 turns | [Clarity press kit](https://hondanews.com/en-US/releases/release-e62e02ca769c4ab1860857ecad92f7d9-2018-honda-clarity-plug-in-hybrid-press-kit) |
| Civic TBA-A030, TEG-A010 | 10.93 / 2.22 | [2018 sedan](https://hondanews.com/en-US/releases/release-fff4ed8cd535421db25a9b1509185c1b-2018-civic-sedan-specifications-features) |
| Civic TBA-C120 | 10.94 / 2.22 | [2019 sedan](https://hondanews.com/en-US/releases/release-5a7e83c266f34585a5e78065ed827628-2019-civic-sedan-specifications-features) |
| Civic TBA-C020, TGG-A120 | 11.12 / 2.11 | [2019 sedan](https://hondanews.com/en-US/releases/release-5a7e83c266f34585a5e78065ed827628-2019-civic-sedan-specifications-features), [Sport hatch](https://hondanews.com/en-US/releases/release-14c1878e52a64178a35a66ad6c277c11-2017-honda-civic-hatchback-specifications-features) |
| CR-V TLA-A040/A220 | 12.30 / 2.30 | [2017 CR-V](https://hondanews.com/en-US/honda-automobiles/releases/2017-honda-cr-v-press-kit-specifications-features) |
| Insight TXM-A040 | 12.58 / 2.54 | [2019 Insight](https://hondanews.com/en-US/releases/release-99b9311b568240639b28482eb820d667-2019-insight-specifications-and-features) |
| Ridgeline T6Z-A110 | 15.59 / 3.04 | [2019 Ridgeline](https://hondanews.com/en-US/honda-automobiles/releases/release-27a26a55e5ab446e930e090078746130-2019-rideline-specifications-features) |
| Odyssey THR-A020 | 14.35 / 2.97 | [2019 Odyssey](https://hondanews.com/en-US/releases/release-3eff8d4ea13b4a169396647f4e298ea0-2019-honda-odyssey-specifications-features) |
| Independently confirmed RDX TJB-A220 | 11.95 / 2.23 | [2019 RDX press kit](https://hondanews.com/en-US/releases/2019-acura-rdx-press-kit) |

EPS/trim association reuses the existing PTM rack/spec tables; it is not new VIN-level verification. Center-to-lock assumes symmetric travel. Honda does not label every published ratio as instantaneous full-lock ratio; using these values as blend endpoints is the user's requested tuning method. Unknown EPS/fingerprint combinations remain unblended. No Accord profile or guessed endpoint was added.

## One-time defaults and branch policy

The user explicitly wants the new defaults applied to existing users too, not merely first installs. Implement a one-time, versioned migration, not an unconditional overwrite every boot. Subsequent user edits must remain possible. Apply Suggested Settings and fresh-install initialization should use the same admitted recipe.

Automatic longitudinal selection is requested after pedal detection: supported Nidec pedal uses PTM Pedal Interceptor; supported non-pedal Honda uses MVL. Do not enable Experimental PCM automatically or assign unsupported Honda controllers to other brands. Initialization must wait for confirmed vehicle/hardware data, not guess from a missing pedal record before fingerprinting.

The user subsequently approved 250% driver-monitoring timing for development/nightly/staging and upstream timings for clean, while excluding vehicle setup, privacy and remote access. `recommended_shared_values()` contains the explicit driving/audio/visual preferences and adds DM timing only when customization is available. Clean's existing overlay disables customization and pins all upstream timing/lockout values independently of the stored percentage; no release-script changes are needed.

The existing DM option scales the **first reminder** to 250%, retaining the spacing between subsequent warnings. Vision warnings become 12.5/15.5/20.5 seconds; wheel-touch warnings 12.5/22.5/32.5. It does not multiply every monitoring or lockout timeout by 2.5. Clean retains 5/8/13 and 5/15/25 respectively, plus its other pinned upstream protections.

`NrdrSettingsDefaultsVersion` records the global migration; `NrdrVehicleDefaultsApplied` records each confirmed vehicle. Subsequent boots do not overwrite edits. Live pedal detection resolves the controller before actuator construction; the remaining vehicle recipe applies before publishing CarParams. Existing verified preset ordering is reused. Model choice, calibration, learned factors, hardware/stock-ACC setup, recording and remote-access keys are excluded from these migration writes. The pre-existing onboarding/default policies outside the new recipe are unchanged.

These changes affect future builds from development. No published release branch or device has been updated in this task.

## Experimental PCM: proposed order of work

The attached archive's November 11 firmware notes supersede several statements in its older model README. In the examined override mode, zero PCM_GAS is not unlimited authority; HOLD integrates speed lead, ACCEL follows an acceleration ceiling with slow unwind, and RELEASE differs again. Own-set clipping, ECON stages, timers, and transmission state matter. Its latest acceleration-law probes have not validated brake handoff or the near-own-set region on the actual Civic.

1. **Reproduce the current Experimental path first.** Replay the current build, its actual learned values, wire mode, and speed units. Preserve today's pedal baseline as a reference, not a fitted Civic vehicle model. Archived Civic routes 157/159 used older builds and differing roads; do not mistake their hill response for proven controller self-oscillation.
2. **Separate speed target from acceleration authority inside existing shaping.** Use the final planner reference and request. Treat PCM_GAS as the acceleration ceiling, not a pedal-position command. Evaluate the firmware-derived ceiling map offline before replacing `gas_allowance()`; retain current command bounds and rise limits. Do not simply send a large speed lead everywhere.
3. **Reduce propulsion through the PCM's HOLD response when appropriate.** Evaluate bounded, hysteretic lead changes in `speed_target()`/the existing Experimental shaping state so a small falling request need not jump into RELEASE. Account for the PCM's own-set clipping; the reported +8/+10 km/h probe strategy cannot be assumed attainable near that cap. Do not copy unverified mode thresholds into production.
4. **Evaluate coast-to-brake behavior with the actual Civic.** The current `coast_blend()` uses a provisional 0.10-0.30 m/s² credit. Improve or replace it only with measured Civic coast response and tracking residuals. Do not import Clarity regen or assume a fixed overspeed tolerance guarantees comfort. Lead/stop braking, material slowdown, override, AEB, and stale-input paths retain priority; a brake request still removes propulsion.
5. **Validate the whole handoff before changing gains.** Compare jerk, reference tracking, pedal/PCM release, brake pulses, brake demand, and recovery after hills. Verify any learning remains observable under the new command mapping. Keep all behavior changes within the existing Experimental gate and require disabled-path regression comparisons.

This is an offline candidate plan, not a claim that the proposed firmware strategy will match the pedal controller. Do not change the proven pedal controller or ordinary PCM behavior to accommodate it.

## Historical notes and deferred dashboard work

- Roen speed breakpoints: `[0, 5, 20]` m/s. Planner positive limits: `[4, 4, 2]` m/s²; Nidec controller maximum curve: `[4, 4, 3]` m/s²; turn threshold 1.3; pedal multiplier forced to 1.0. These are provenance, not recommended new personality values. Sources: `features/longitudinal/longitudinal_planner.py`, `longcontrol.py`, and opendbc `sunnypilot/car/honda/gas_interceptor.py`.
- Dashboard families reported by the user: 2018-generation Accord, 2019-generation Pilot, latest Insight generation, 2019-generation Ridgeline, and 2019-generation Odyssey. Exact fingerprint coverage still needs confirming, not a blanket model-year rule.
- Reported Pilot symptom: displayed cruise set speed jumps from 61 to 63 mph on one press. User explicitly deferred diagnosis/fix until additional Pilot logs are available. It could involve button increments, units, or display rounding; the cause is not established. Current `NrdrHondaDashVariantB` is unused at runtime.

## Verification

- Focused offline checks cover controller IDs/eligibility, first-detection config, default migration exclusions/retry/repeat-boot behavior, Standard-only tuning, remote write rejection, and help-only descriptions.
- Existing exact gains/integral/reference, gas formula, clipping/disengagement, and Standard-controller regression checks remain applicable. No claim of a fresh vehicle replay or road validation is made.
- Geometry checks cover every listed Honda EPS endpoint, both PTM map modes, center/midpoint/lock, left/right symmetry, monotonic inverse, curvature round-trip, model exclusion, and lane-change composition. Existing model-family tests exclude Cheddar/TSFDO/big models.
- Driver-monitoring tests verify the 250% schedule and clean's restoration of all 19 upstream timing/lockout fields even if development values change.
- First-install C3X model selection uses the existing verified-artifact admission; existing model selections and C4's model default are untouched. Physical C3X OPM10V3 execution and graphical rendering remain unverified.
- Final test totals and remaining host-environment limitations are recorded in `TASKS.md`. No full build, release, push, or deployment was run.
