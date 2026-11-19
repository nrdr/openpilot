# Clarity angle mode: why steering assistance dropped out

**Conclusion, November 19, 2026:** The steering rack reported that its angle command was stale, and nrdr withdrew steering assistance in response. The C4 was still publishing active commands at about 100 Hz. Its logs do **not** show a 32 ms publishing gap that explains the faults. They also do **not** measure when the rack received and accepted each command. The dropout is confirmed; the reason the rack’s freshness check expired remains open.

**Decision:** Keep experimental angle assistance off on this Clarity. No further road collection is needed. Smooth steering between dropouts is compatible with this failure. There is no basis here to raise the send rate, relax the timeout, suppress the alert, retune steer ratio, or switch to mode 4 as a fix.

## Evidence from the drive

2018 Honda Clarity; AnglePTM build 05; route `00000215--f9b07ae7a5`; all 14 full-rate log segments (about 13 min 16 s). A **fault onset** is a rising edge of the rack’s angle-fault bit, not every frame that repeats the fault or its last-reason code.

| Question | What the recording shows |
| --- | --- |
| What did the rack report? | 71 fault onsets. All reported reason 2 (stale steering command), with angle mode 3 both requested and active. None reported a rejected target jump or invalid angle sensor as the reason. |
| Did assistance actually drop? | All 71 onsets were followed by lateral assistance becoming inactive within 100 ms. There were 40 separate “TAKE CONTROL IMMEDIATELY” alert onsets. Alerts and rack faults are different counts. |
| Was this only a parking maneuver? | No. 56 faults occurred at or above 5 mph; the highest fault speed was about 27 mph. |
| Did the C4 stop publishing? | In the 100 ms immediately before each reported onset, it published 9–11 active angle commands. Across those windows the median interval was 9.98 ms; the longest interval without an active publication was 22.66 ms, including the window edges. |
| Did the Panda report losing or rejecting those sends? | All 705 active publications in those windows matched byte-for-byte, in order, to Panda transmit receipts. No rolling-counter skips were seen in the pre-fault active receipts, and no steering-message rejection was logged near an onset. A transmit receipt is not an acknowledgment from the rack. |

## Who withdrew steering assistance?

On all 71 fault edges the rack’s reported angle-control output (`ANGLE_OUT`) went from nonzero in its preceding status frame to zero in its first stale-fault frame. The C4’s high-level lateral-assistance flag was still on before every edge and switched off **7.8–26.7 ms after** the first logged fault frame (median 14.9 ms). This is the automated angle-control output, not a measurement of the driver’s ordinary power steering.

For 70 of 71 events, the last outgoing steering request before the fault report was also still active: the rack reported zero output before nrdr withdrew the request. The exception was at 435.0 s: driver steering input was flagged, and nrdr published an inactive request 0.9 ms **before** the logged fault report. That order on the C4’s clock does not resolve which happened first inside the rack. In all 71 cases the first Panda receipt of the inactive request followed the logged rack fault. The evidence identifies the usual **cutoff** at the rack, not the underlying **cause** of the stale timer.

## Follow-up: were the steering counter or checksum wrong?

**Neither was wrong in the recorded commands.** At James’s suggestion, we independently recalculated the Honda checksum from each recorded `0xE4` payload and checked the two-bit rolling counter against the preceding frame in the same stream (including across active/inactive transitions and log-segment boundaries). The [Clarity steering frame definition](../../../opendbc_repo/opendbc/dbc/generator/honda/_steering_control_a.dbc) and [Honda checksum implementation](../../../opendbc_repo/opendbc/car/honda/hondacan.py) specify the checks. A separate calculation agreed, and deliberately changing one bit in an offline sample failed validation as expected.

| Observation point | Within 250 ms either side of any of the 71 fault onsets | Whole drive |
| --- | --- | --- |
| C4 outgoing steering commands | 3,344 checked; zero checksum or counter errors | 78,234 checked; zero checksum or counter errors |
| Panda steering transmit receipts | 3,332 checked; zero checksum or counter errors | 78,223 checked; zero checksum or counter errors |

Overlapping windows are counted once; each stream is windowed on its own log timestamps, so the two window totals are not a packet-loss calculation. Comparing content directly over the whole drive, **all 30,647 active angle-command payloads matched the Panda returns byte-for-byte, in order**. No steering rejection was logged in the 250 ms windows. The 1,683 rack-status frames (`0x6A4`) in those windows also passed their checksum and counter checks. This rules out a malformed checksum or a skipped/repeated counter in the observed command streams as the explanation for the dropouts. It does not establish when the rack received or accepted a command.

## Why the receipts don’t settle the cause

The [Clarity signal definition](../../../opendbc_repo/opendbc/dbc/generator/honda/honda_clarity_hybrid_2018_can.dbc) identifies reason 2 as the rack considering the steering message (`0xE4`) stale after more than 32 ms. **32 ms is the documented rack threshold, not a wire interval measured on this drive.** The rack reports status at 50 Hz; the first logged fault frame is an observation of the fault, not the instant its internal timer expired.

At the first fault (29.96 s), an apparent **32.7 ms gap** in Panda returns ended with **three successive steering commands under the same host timestamp**, their rolling counters in sequence. The [C4 receive code](../../selfdrive/pandad/pandad.cc) publishes a batch of frames as one timestamped event. That gap could include delay in transmission, delay collecting the receipts, or both. Receipt batching explains why the timestamps are ambiguous; it does not, by itself, explain the rack fault.

The remaining distinction is **late arrival versus late acceptance**: did valid commands arrive too far apart at the rack, or did they arrive on time without refreshing its timer? The route has neither independent rack-side bus timestamps nor the rack’s internal timer history. It does not establish a faulty Panda, a firmware bug, or a StarPilot-versus-nrdr scheduling difference. The earlier 85–86 Hz observation from another drive is not a substitute for the command timings measured here.

## What would settle it

1. **Compare existing recordings first.** James’s [car-side PR](https://github.com/nrdr/opendbc/pull/5) references routes e8/e9 on his personal branch and reports no firmware faults on build 05. We have his report, not a matched raw trace. Request a full-rate build-05 segment with mode 3 active and its running commit. Compare command spacing, transmit receipts and rack fault edges using the same definitions above.
2. **If that comparison is inconclusive, separate arrival from acceptance on a bench.** Use an independent, hardware-timestamped capture at the rack input aligned with its status. A verified gap there would support a delivery-timing diagnosis. Valid, timely frames through a fault would instead direct attention to what the firmware counts as fresh. Retain the existing timeout and disengagement behavior in either case.

Mode 4 lowers the speed-dependent angle limit; it is not a documented change to command freshness. The earlier controller startup crash is also separate: in this recording, mode 3 was acknowledged and steering commands were being published when the faults occurred.
