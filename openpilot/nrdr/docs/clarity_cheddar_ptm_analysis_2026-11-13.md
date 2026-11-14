# Clarity / Cheddar PTM drive analysis — November 13, 2026

Analysis only. No controller calibration, model selection, saved parameters, or deployed source was changed.

## Inputs and method

- PTM donor: Biscuit-Labs `Honda-PTM-Testing`, `45e5b91fae934e4f423ee39055efb84d2150c575`, confirmed branch tip during this investigation.
- `000001dd--595877f920`: 6:22 p.m. Eastern, 23 full-log segments, about 22 minutes; approximately 15 minutes laterally active.
- `000001de--0ef8ed7cde`: 7:55 p.m. Eastern, 38 full-log segments, about 37 minutes; approximately 12 minutes laterally active.
- Both starts identify `HONDA_CLARITY`, Cheddar, PTM Controller / Clarity A020, code `2a582d396c`. The EPS reports TRW-A020; this does not identify the exact flashed firmware payload.
- All 61 full logs were parsed without read errors. The extraction retained raw bus-0 VSA yaw, GPS heading/quality, steering/speed/roll, model trajectory/action, control activity and command delay.
- Ran the donor's `fit_yaw_scale.py`, `fit_rack_map.py`, `plan_timing.py` calculations and command-timing report. Import/log-reading adapters supplied the same arrays from a temporary extraction, without a second repository or runtime deployment. One contiguous time-axis copy avoids repeated allocation in GPS interpolation; a test verifies identical pair results.
- The plan tool's sample thresholds, steering-press exclusion, 17 ms VSA latency, and ±0.40 s timing search were retained. Rack fitting uses all qualifying driving samples, not only openpilot engagements. Command timing uses the report's engaged/hands-off/blinker/acceleration exclusions and fixed 38 ms pipeline allowance.

Sources: [rack fit](https://github.com/Biscuit-Labs/openpilot/blob/45e5b91fae934e4f423ee39055efb84d2150c575/openpilot/tools/lateral/fit_rack_map.py), [yaw fit](https://github.com/Biscuit-Labs/openpilot/blob/45e5b91fae934e4f423ee39055efb84d2150c575/openpilot/tools/lateral/fit_yaw_scale.py), [plan timing](https://github.com/Biscuit-Labs/openpilot/blob/45e5b91fae934e4f423ee39055efb84d2150c575/openpilot/tools/lateral/plan_timing.py), [PTM report](https://github.com/Biscuit-Labs/openpilot/blob/45e5b91fae934e4f423ee39055efb84d2150c575/openpilot/tools/lateral/eps_report.py).

## Yaw calibration

The donor baseline is **0.246 deg/s/count + 0.240 deg/s clockwise correction**, ramped over +3 to +5 counts. Both drives' measured standstill zero was effectively **512.000 counts**.

| Data | Accepted GPS pairs | Fitted scale | Clockwise correction | Baseline heading RMS | Fitted heading RMS |
| --- | ---: | ---: | ---: | ---: | ---: |
| 6:22 p.m. | 56,700 | 0.248483 | −0.037607 deg/s | 1.881° | 1.478° |
| 7:55 p.m. | 74,401 | 0.246989 | +0.204405 deg/s | 0.878° | 0.818° |
| Combined | 131,101 | 0.2474 | +0.176 deg/s | 1.403° | 1.31° |

These are overlapping GPS windows, not independent turns. The first drive's replacement fit worsens heading RMS on the second drive to **2.636°**, versus **0.878°** with the baseline. The second drive's fit gives **1.786°** on the first, modestly better than its baseline 1.881°.

**Interpretation:** the latest drive supports the baseline closely; the pooled improvement is small and the independent route fits disagree. Do not remove the clockwise correction based on the first drive or install the pooled fit as a new calibration.

## Steering geometry

The donor's shipped PTM map uses effective rack ratios **17.34 near center to 16.02 at 400°**, after the firmware angle conversion, with slip factor **−0.00050**. These are not directly interchangeable with a single raw steering-ratio setting.

Qualified fitting time was **194 s** on the first drive and **380 s** on the second, **574 s combined**. The first drive alone fails the donor's 300 s minimum. The combined fit meets that minimum but has only 10–20 s in several larger-angle bands and no supported new fit beyond roughly 215°.

Measured / baseline-predicted curvature (1.000 is agreement):

| Wheel-angle band | Speed band | 6:22 p.m. | 7:55 p.m. |
| --- | --- | ---: | ---: |
| 3–20° | 2.5–9 m/s | 0.879 | 0.934 |
| 3–20° | 9–40 m/s | 0.980 | 0.989 |
| 20–70° | 2.5–9 m/s | 0.982 | 1.001 |
| 20–70° | 9–40 m/s | 0.991 | 1.004 |
| 70–150° | 2.5–9 m/s | 1.001 | 1.016 |
| 150°+ | 2.5–9 m/s | 1.010 | 1.010 |

Most populated bands agree within about 2%. The main discrepancy is **6.6–12.1% less curvature than predicted at small wheel angles and low speed**. This is an observation, not proof of an incorrect rack map: yaw quantization, angle offset, transient response and road-roll estimation can matter disproportionately near center.

Unconstrained pooled refit:

```text
angle degrees:  5.5    14.7   26.0   55.1   83.1   129.0  171.6  215.4
effective R:  19.58   18.13  17.99  17.14  16.68   16.58  16.45  16.31
slip factor: -0.00008
```

This simultaneously changes geometry and speed compensation. Holding the proven slip factor at −0.00050 instead gives ratios within **−1.62% to +3.07%** of the baseline at the fitted knots. That sensitivity is a reason not to install the unconstrained fit.

Training on the first drive and holding out the second leaves roughly **9–10% excess measured curvature** in the larger-angle bands; the first drive does not cover those bands sufficiently. The shipped map remains closer there. The donor's separate older road-ratio curve also gives roughly **10–13% excess measured curvature** in several populated medium-angle/faster bands. Neither replacement consistently beats the shipped PTM map.

## Turn timing

| Trajectory-based result | 6:22 p.m. | 7:55 p.m. |
| --- | --- | --- |
| Turn entry | 47 frames; below minimum | 25 frames; below minimum |
| Turn exit | 60 frames; below minimum | 36 frames; below minimum |
| All eligible turns, 5–12 m/s | 236 frames: best shift −0.02 s | 123 frames; below minimum |
| Median model-frame-to-publication time | 67 ms | 66 ms |

The first drive's −20 ms optimum barely reduces RMS curvature error: **0.0019635 → 0.0019615 1/m**. Individual windows vary in both directions. It is not strong evidence for a 20 ms calibration change. Cheddar's commanded steering comes from its action head; this tool compares the auxiliary trajectory, so its result is not a direct measurement of the action head's calibration.

Many frames are excluded by the donor's steering-press and speed/curvature rules. Reported `steeringPressed` edges are not verified human interventions. The thresholds were not relaxed to obtain a result.

### Actual-command timing

The updated donor report separately measures car response behind the published steering action, then subtracts the logged command delay and its assumed 38 ms pipeline allowance. Unlike the auxiliary trajectory comparison, this includes Cheddar's actual action-head output.

The donor compares that estimate with the schedule at the **speed-band midpoint**, even when the qualifying data lies near a band edge. The table below instead uses the median scheduled value at the actual qualifying speeds; the lag fit and filtering are unchanged.

| Drive | Speed band | Qualified samples | Response-derived prediction delay | Schedule at sampled speeds | Difference |
| --- | --- | ---: | ---: | ---: | --- |
| 6:22 p.m. | 9–15 m/s | 1,697 | 0.154 s | 0.098 s | 56 ms late |
| 6:22 p.m. | 15–25 m/s | 2,816 | 0.142 s | 0.167 s | 25 ms early |
| 7:55 p.m. | 15–25 m/s | 4,155 | 0.132 s | 0.146 s | 14 ms early |
| 6:22 p.m. | 25–40 m/s | 2,804 | 0.282 s | 0.267 s | 15 ms late |
| 7:55 p.m. | 25–40 m/s | 1,225 | 0.302 s | 0.267 s | 35 ms late |

For example, the donor prints **68 ms early** on the second drive's 15–25 m/s band, comparing with 0.20 s at 20 m/s. The median qualifying speed is only **15.69 m/s**, whose schedule is 0.146 s; that gives **14 ms early** instead. The report now makes this actual-speed comparison.

These are aggregate estimates, not new recommended settings: they retain the donor's 38 ms assumption, 10 ms search spacing, and possible lane-centering contributions. There is insufficient qualifying action-timing data below 9 m/s. A separate low-speed delivery fit hits its search boundary and is not a credible delay estimate. The available data does not establish a large, consistently wrong delay across speeds.

## Offline tool updates and verification

- Shared offline lookups now use the PTM sampled angle inverse, each calibration's prediction schedule, PTM rack interpolation, and the donor's RDX yaw entry. No runtime calibration table was edited.
- Rack fitting adds the donor road-curve comparison (`--road-curves <honda_lateral_common.py>`) and a comparison against the shipped PTM map, while retaining nrdr's existing `--eps` interface and CP comparison.
- Yaw fitting includes the donor's no-pairs message and avoids repeated copying of the same time axis without changing fit arithmetic.
- The PTM report reads nrdr's logged command delay and subtracts it as the updated donor report does. Missing delay remains explicitly reported as missing, not silently inferred.
- The report compares the delay schedule at the qualifying samples' actual speeds instead of a potentially misleading speed-band midpoint. This is an explicit reporting correction beyond the donor version, not a controller change.
- Ten focused native unittest checks passed using the edited tool sources in an isolated interpreter; no installed source was replaced. Donor rack-fit methods and sample selection matched exactly across 20,000 synthetic samples; the plan-shift function is unchanged. `git diff --check` passed. Full pytest was not run: the available host environments lack the combined test/native dependencies, and C4 has no pytest.

## Decision

Keep the current runtime calibration. Prioritize repeatable low-speed, near-center behavior and enough clean turn entries/exits to distinguish geometry from timing. Validate any proposed fit on a separate drive; do not promote a better in-sample score into a controller change.
