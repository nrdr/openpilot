# Lane-centering activation and timing repair

Source work stays on `nrdr-architecture-development`. No nightly publication or installed-device replacement is part of this validation. This is development software, not a road-qualified release.

## What failed

The earlier implementation joined `modelV2` to a separate `modelDataV2SP` timing event. Both model publishers populated the sidecar's fields but left its event validity at the default false. The consumer rejected those events, including timing values inside its supported range. A second restriction rejected total action times above 0.475 seconds; the recorded TSFDOM combination was approximately 0.545 seconds.

In the audited Civic drive logs, the lane-centering correction stayed zero. Oscillation reported during those drives cannot be attributed to an active lane-centering correction. The synthetic delay tests discussed here are separate experiments, not explanations of that on-road tuning behavior. Logs from the audited sessions do not establish what happened on every historical drive or on both cars.

## Implementation

- Add `ModelDataV2.Action.lateralActionTime @3 :Float32`, in seconds, without changing existing field ordinals. Old messages decode the new field as zero (unavailable).
- Both model pipelines attach the exact action time used to generate the steering action after filling that action. Timing and steering now share one event, frame, and validity flag.
- The companion `DrivingModelData.action` also carries the same timing in both publishers, without changing curvature, acceleration, stopping behavior, or event validity. Lane centering consumes only `modelV2.action`.
- Keep the older `ModelDataV2SP` fields for compatibility and make its validity follow the completed `modelV2` event. Lane centering no longer subscribes to or reads that sidecar.
- Keep the existing `modelV2` health checks, driver override, lane-change suspension, strength-zero reset, correction caps, and downstream total-curvature limits. No engagement or communication-alert rules are weakened.
- Read timing only from the current model action. Do not guess from unrelated current parameters or silently borrow timing from a different frame. Invalid/absent timing removes only the optional correction; it does not block engagement.
- Extend the numerical development range through 0.875 seconds total action time. The post-action fit horizon is `max(1.5, 3 * action_time)` seconds; required available preview is `max(1.0, 3 * action_time)` seconds. The existing 0.25-second post-action start is unchanged. Longer delay therefore changes the geometric response, not just admission through a larger cutoff.
- Require enough actual common lane/model path coverage for the delay-scaled preview. Do not extrapolate geometry or silently truncate below the minimum preview. `SHORT` reports insufficient coverage.
- Keep user strength as the direct multiplier of the fitted correction, with the same final correction ceiling. No hidden additional strength multiplier or new tuning setting is introduced.
- Show green `ON` for a nonzero correction request. This is pre-final-limit observability, not confirmation that a steering rack executed it.

## Verification

- Host numerical suite: **486 passed**, including **192 active 60-second extended-delay scenarios** at total action times 0.545/0.575/0.675/0.875 seconds, speeds 12/25/40 m/s, strengths 30/50/70/100%, both initial offset directions, and full/minimum available horizons. Existing shorter-delay cases and strict excursion/correction bounds remain in place; no unsupported-delay tests are silently skipped.
- Host settings, publisher, and consumer suite: **39 passed, 41 subtests passed**. These execute the production timing helper and consumer call, preserve the independent model-validity gate, verify the shared status colors/labels, and confirm both publishers attach timing after filling the steering action. They also verify consistent timing in the companion driving-data action without changing its existing fields. The settings JSON matches its source compiler output.
- Native C4 runtime: **90 passed** using candidate modules/schemas in a unique temporary directory, without installing them. Checks include real Cap'n Proto Event serialization, execution of the actual publisher helper, valid/invalid model events, nonzero correction at 0.325/0.545 seconds, and decoding an Event created by the installed older schema with unavailable timing. A fresh off-road/Panda-no-output guard remained active.
- Exact recorded-log replay, with no forced engagement and no assumed action time:

| Segment | Recorded total action time | Replay minimum speed | Model frames | Candidate correction frames, strength 100% / Model Break-In 0 | Installed correction frames |
| --- | --- | --- | --- | --- | --- |
| `00000053--beb73512c3--6` | 0.3249999881 s | 50 mph | 1,200 | 470 | 0 |
| `00000055--c5ed5642c1--83` | 0.5449833274 s | 12 mph | 1,199 | 473 | 0 |

The candidate replay explicitly repairs the invalid sidecar transport offline by taking only the exact recorded model-frame timing. It preserves recorded model validity, driver input, lane changes, and replay freshness/engagement gates. It explicitly enables the feature in memory for this comparison; it neither reads nor writes the device's current feature preference. The installed baseline uses its original validity/range checks and remains at zero. The candidate produced nonzero corrections on **943 of 2,399 frames**, with maximum corrections 0.0009102266 and 0.0012 m^-1 respectively (within the unchanged cap). Other classifications, including `modelInvalid`, reflect the replay's checks and must not be treated as diagnoses of the original drive's communication alerts.

Five installed source/schema hashes were identical before and after the isolated checks. No installed checkout, model weights, parameters, branch refs, safety configuration, or vehicle commands were changed. Production model inference, whole-system scheduling, the complete live producer-to-consumer path, and physical vehicle response are **not** established by these isolated checks.

The delayed-loop harness uses ideal lane geometry and simplified vehicle dynamics. It can expose numerical regressions, but cannot certify behavior with real tires, EPS response, road banking, poor markings, or model choices. Candidate replay must distinguish real recorded timing from explicitly repaired transport and from any assumed timing. A repaired offline replay is not a claim that the feature was active in the original drive.

At 0.545 seconds total action time, the required preview is 1.635 seconds after actuation (2.180 seconds of total model coverage). The preview grows continuously with delay; the strength setting and correction cap do not change.

## Deployment boundary

The model publishers, schema, and consumer must be updated together. A new consumer paired with an old publisher reports unavailable timing rather than making up a value. Before road evaluation, confirm the installed revision and observe the complete live producer-to-consumer path in a controlled environment. Do not publish this candidate to nightly based solely on the tests above.
