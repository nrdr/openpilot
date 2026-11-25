# Turn-desire refresh (opt-in, unvalidated on the road)

Parameter `NrdrTurnDesireRefresh`, default off. Read with the other Lane Turn Desire settings. Only acts when Lane Turn Desire is on.

On the C4: **Settings → Device → Lateral Tuning → Turn Desire Refresh**. Also available in Sunnylink under **Steering → nrdr → Lateral Tuning**. The switch is editable only while parked and with Lane Turn Desire enabled.

## Problem

modeld passes a desire to the model only on the frame it switches on (`modeld_v2/modeld.py`, rising edge of the desire vector). The model then remembers it for a fixed time. Lane Turn Desire raises the request when speed first drops below its threshold with the blinker on, which is on the approach, so longer turns and every turn from a stop run past that memory.

Measured on the Clarity, 2026-11-20 (analysis in `C:\Openpilot Workspace\analysis\ptm-angle-2026-11-20`):

| Model | Turn state held after the pulse (model's own `desireState`) | After it lapsed |
|---|---|---|
| OPM10V3 | 5.04-5.06 s in 12 of 13 pulses | Kept a partial turn estimate; started one left from a stop at 7.1 s |
| TSFDOM | 5.5-8.8 s in 9 pulses | Did not start either left-from-stop turn; the driver did, at 6.2 and 8.0 s |

Wheel peak came 4.3-10.4 s after the pulse.

## What the option does

`TurnDesireRefresh` (`features/lateral/turn_desire_refresh.py`) sits inside `LaneTurnController`. While one request stays up and the turn has not started, it drops the published direction for a single model frame so the next frame is a fresh pulse:

- when the car moves off after a stop (above 1 m/s after being below 0.5 m/s) and the last pulse is at least 2.5 s old;
- every 5 s while moving above 1 m/s.

Nothing is re-issued once the wheel is 20° or more toward the request, or after it has been 90° toward it during that request, or more than three times per request. `LaneTurnController.held` stays true through the dropped frame so lane guidance does not switch on for it. With the option off the published direction is unchanged.

## Replay of the shipped module on the recorded requests

| Drive | Pulses, shipped to refreshed | Where the extra pulses fall |
|---|---|---|
| Route 06, OPM10V3 | 9 to 11 | Two left-from-stop turns, at 6.30 and 5.76 s |
| Route 09, TSFDOM | 9 to 11 | The two left-from-stop turns the model did not start, at 5.05 and 5.80 s |

No extra pulse in any rolling turn.

## Not established

Whether a model acts on a second pulse. That needs a model replay on recorded frames with the re-timed pulse, or a supervised low-speed test. It does not help when the blinker cancels by itself, as at turn 11 of route 06.

## Rollback

Set the parameter to 0, or revert the commit.
