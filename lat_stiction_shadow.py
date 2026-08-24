#!/usr/bin/env python3
"""Read-only transient shadow replay for the NRDR lateral stiction stage.

This intentionally replays controller decisions on the recorded trajectory. It
does not claim that the recorded wheel response is the response that a different
shadow torque would have produced. Historical requested torque may also already
include the prior LatStiction stage; baseline-stiction counts expose that source
contamination instead of presenting this as a clean controller counterfactual.
"""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Callable, Iterable, Sequence
from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
from statistics import median

from openpilot.sunnypilot.nrdr.lat_stiction import LatStiction
from steerratio_correction import expand_sources, iter_local_events, route_segment


CONTROL_DT = 0.01
MAX_INPUT_AGE_S = 0.05
ZERO_CROSSING_WINDOW_S = 1.0


@dataclass(frozen=True)
class ShadowFrame:
  route_id: str
  timestamp: float
  active: bool
  speed_mps: float
  measured_angle_deg: float
  error_deg: float
  desired_angle_deg: float
  desired_rate_deg_s: float
  wheel_rate_deg_s: float
  live_torque: float
  applied_torque: float
  steering_pressed: bool = False
  blinker_active: bool = False
  lane_change_active: bool = False
  steer_fault: bool = False
  safety_limited: bool = False
  saturated: bool = False
  inputs_fresh: bool = True
  baseline_stiction_enabled: bool | None = None

  @property
  def bypass_reason(self) -> str | None:
    if not self.inputs_fresh:
      return "stale inputs"
    if not self.active:
      return "inactive"
    if self.steering_pressed:
      return "driver steering"
    if self.lane_change_active:
      return "lane change"
    if self.steer_fault:
      return "steer fault"
    if self.safety_limited:
      return "safety limited"
    if self.saturated:
      return "saturated"
    return None


@dataclass(frozen=True)
class ShadowResult:
  frame: ShadowFrame
  state: str
  reason: str
  proposed_torque: float
  transition: bool


@dataclass(frozen=True)
class TriggerScore:
  route_id: str
  timestamp: float
  state: str
  reason: str
  error_deg: float
  predicted_crossing_s: float
  actual_crossing_lead_s: float
  bypass_reason: str | None


@dataclass(frozen=True)
class ShadowSummary:
  frames: int
  routes: int
  duration_s: float
  baseline_stiction_on_frames: int
  baseline_stiction_off_frames: int
  baseline_stiction_unknown_frames: int
  active_frames: int
  clean_frames: int
  angle_coverage_frames: dict[str, int]
  clean_angle_coverage_frames: dict[str, int]
  decision_angle_coverage_frames: dict[str, int]
  blinker_frames: int
  state_frames: dict[str, int]
  transitions: int
  transition_reasons: dict[str, int]
  trigger_events: int
  triggers_with_crossing: int
  trigger_lead_median_s: float | None
  trigger_lead_p10_s: float | None
  trigger_lead_p90_s: float | None
  trigger_timing_by_state: dict[str, dict[str, float | int | None]]
  gate_frames: dict[str, int]
  gate_condition_frames: dict[str, int]
  gated_decision_violations: int
  nonfinite_input_frames: int
  nonfinite_output_frames: int
  torque_bound_violations: int
  hold_opposite_live_at_or_above_release_frames: int
  torque_delta_rms: float
  torque_delta_p95: float
  torque_delta_max: float
  torque_delta_by_state: dict[str, dict[str, float | int]]
  opposite_torque_by_state: dict[str, dict[str, float | int]]
  max_same_sign_torque_delta: float
  max_hold_duration_s: float
  hold_outer_error_frames: int
  monotonic_outer_error_hold_runs: int
  live_applied_delta_rms: float
  live_applied_delta_p95: float
  live_applied_delta_max: float


def _decode_bool(value: str | None) -> bool | None:
  if value is None:
    return None
  return value.strip().lower() not in ("", "0", "false", "off", "no")


def _state_name(stage: object) -> str:
  state = getattr(stage, "state", None)
  if state is not None:
    name = getattr(state, "name", None)
    if name is None:
      value = getattr(state, "value", state)
      name = getattr(value, "name", value)
    return str(name).lower()
  return "hold" if bool(getattr(stage, "holding", False)) else "track"


def _is_active_decision(state: str) -> bool:
  return state.lower() in {"throw", "capture", "hold", "reacquire"}


def _percentile(values: Sequence[float], percentile: float) -> float | None:
  if not values:
    return None
  ordered = sorted(values)
  position = (len(ordered) - 1) * percentile / 100.0
  lower = math.floor(position)
  upper = math.ceil(position)
  if lower == upper:
    return float(ordered[lower])
  weight = position - lower
  return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def _error_hi(speed_mps: float) -> float:
  breakpoints = LatStiction.E_HI_BP
  values = LatStiction.E_HI_V
  if speed_mps <= breakpoints[0]:
    return float(values[0])
  if speed_mps >= breakpoints[-1]:
    return float(values[-1])
  for index in range(len(breakpoints) - 1):
    if speed_mps < breakpoints[index + 1]:
      fraction = (speed_mps - breakpoints[index]) / (breakpoints[index + 1] - breakpoints[index])
      return float(values[index] + fraction * (values[index + 1] - values[index]))
  return float(values[-1])


def _param_map(init_data) -> dict[str, str]:
  values = {}
  for entry in getattr(getattr(init_data, "params", None), "entries", ()):
    try:
      values[str(entry.key)] = bytes(entry.value).decode("utf-8", errors="replace").strip("\x00")
    except (TypeError, ValueError):
      continue
  return values


def iter_shadow_frames(source: str) -> Iterable[ShadowFrame]:
  """Join the 100 Hz controller streams required by the shadow stage."""
  route_id, _segment = route_segment(source)
  car_state: tuple[float, dict] | None = None
  car_control: tuple[float, dict] | None = None
  car_output: tuple[float, float] | None = None
  lane_change_active = False
  angle_offset_deg = 0.0
  learn_angle_offset = True
  baseline_stiction_enabled: bool | None = None
  previous_timestamp: float | None = None
  previous_desired_no_offset: float | None = None

  for event in iter_local_events(source):
    timestamp = event.logMonoTime / 1e9
    which = event.which()
    if which == "initData":
      params = _param_map(event.initData)
      learn_angle_offset = _decode_bool(params.get("NrdrLearnAngleOffset")) is not False
      baseline_stiction_enabled = _decode_bool(params.get("NrdrLatStiction"))
    elif which == "liveParameters":
      angle_offset_deg = float(event.liveParameters.angleOffsetDeg) if learn_angle_offset else 0.0
    elif which == "modelV2":
      lane_change_active = str(event.modelV2.meta.laneChangeState) != "off"
    elif which == "carState":
      state = event.carState
      car_state = timestamp, {
        "speed_mps": float(state.vEgo),
        "measured_angle_deg": float(state.steeringAngleDeg),
        "wheel_rate_deg_s": float(state.steeringRateDeg),
        "steering_pressed": bool(state.steeringPressed),
        "blinker_active": bool(state.leftBlinker or state.rightBlinker),
        "steer_fault": bool(state.steerFaultTemporary or state.steerFaultPermanent),
      }
    elif which == "carControl":
      control = event.carControl
      car_control = timestamp, {
        "active": bool(control.latActive),
        "live_torque": float(control.actuators.torque),
      }
    elif which == "carOutput":
      car_output = timestamp, float(event.carOutput.actuatorsOutput.torque)
    elif which != "controlsState":
      continue
    else:
      controls = event.controlsState
      if controls.lateralControlState.which() != "pidState" or car_state is None or car_control is None:
        continue
      pid = controls.lateralControlState.pidState
      state_timestamp, state = car_state
      control_timestamp, control = car_control
      applied_torque = car_output[1] if car_output is not None else math.nan
      desired_angle = float(pid.steeringAngleDesiredDeg)
      desired_no_offset = desired_angle - angle_offset_deg
      dt = timestamp - previous_timestamp if previous_timestamp is not None else math.nan
      if previous_desired_no_offset is not None and 0.0 < dt <= MAX_INPUT_AGE_S:
        desired_rate = (desired_no_offset - previous_desired_no_offset) / dt
      else:
        desired_rate = 0.0
      previous_timestamp = timestamp
      previous_desired_no_offset = desired_no_offset
      inputs_fresh = (
        abs(timestamp - state_timestamp) <= MAX_INPUT_AGE_S
        and abs(timestamp - control_timestamp) <= MAX_INPUT_AGE_S
      )
      yield ShadowFrame(
        route_id=route_id,
        timestamp=timestamp,
        active=bool(pid.active and control["active"]),
        speed_mps=state["speed_mps"],
        measured_angle_deg=state["measured_angle_deg"],
        error_deg=float(pid.angleError),
        desired_angle_deg=desired_no_offset,
        desired_rate_deg_s=desired_rate,
        wheel_rate_deg_s=state["wheel_rate_deg_s"],
        live_torque=control["live_torque"],
        applied_torque=applied_torque,
        steering_pressed=state["steering_pressed"],
        blinker_active=state["blinker_active"],
        lane_change_active=lane_change_active,
        steer_fault=state["steer_fault"],
        # Honda's requested-to-applied delta includes normal LPF/rate limiting,
        # so it is a diagnostic below rather than an inferred safety bypass.
        safety_limited=False,
        saturated=bool(pid.saturated),
        inputs_fresh=inputs_fresh,
        baseline_stiction_enabled=baseline_stiction_enabled,
      )


def replay_shadow(frames: Iterable[ShadowFrame], *, steer_max: float = 1.0,
                  stage_factory: Callable[[float, float], object] = LatStiction) -> list[ShadowResult]:
  results = []
  stage = None
  previous_route = None
  previous_timestamp = None
  previous_state = "bypass"
  for frame in frames:
    gap = frame.timestamp - previous_timestamp if previous_timestamp is not None else math.inf
    if stage is None or frame.route_id != previous_route or not 0.0 < gap <= MAX_INPUT_AGE_S:
      stage = stage_factory(CONTROL_DT, steer_max)
      previous_state = _state_name(stage)
    gated = frame.bypass_reason is not None
    proposed_torque = stage.update(
      frame.active and frame.inputs_fresh and not frame.steer_fault,
      frame.speed_mps,
      frame.error_deg,
      frame.desired_rate_deg_s,
      frame.wheel_rate_deg_s,
      frame.live_torque,
      frame.steering_pressed,
      frame.lane_change_active,
      frame.saturated or frame.safety_limited or frame.steer_fault,
    )
    state = _state_name(stage)
    reason = str(getattr(stage, "reason", "unknown"))
    # A stage without an explicit BYPASS state still has no active decision in TRACK.
    if gated and state == "bypass":
      proposed_torque = frame.live_torque
    results.append(ShadowResult(frame, state, reason, float(proposed_torque), state != previous_state))
    previous_route = frame.route_id
    previous_timestamp = frame.timestamp
    previous_state = state
  return results


def _predicted_crossing_s(frame: ShadowFrame) -> float:
  relative_rate = frame.desired_rate_deg_s - frame.wheel_rate_deg_s
  if abs(relative_rate) < 1e-6 or frame.error_deg * relative_rate >= 0.0:
    return math.nan
  return -frame.error_deg / relative_rate


def score_triggers(results: Sequence[ShadowResult]) -> list[TriggerScore]:
  by_route: dict[str, list[ShadowResult]] = {}
  for result in results:
    by_route.setdefault(result.frame.route_id, []).append(result)
  scores = []
  for route_id, route_results in by_route.items():
    zero_crossings = []
    for previous, current in zip(route_results, route_results[1:], strict=False):
      previous_error = previous.frame.error_deg
      current_error = current.frame.error_deg
      if current_error == 0.0 and previous_error != 0.0:
        zero_crossings.append(current.frame.timestamp)
      elif previous_error * current_error < 0.0:
        fraction = abs(previous_error) / (abs(previous_error) + abs(current_error))
        zero_crossings.append(
          previous.frame.timestamp + fraction * (current.frame.timestamp - previous.frame.timestamp),
        )
    for result in route_results:
      if not result.transition or result.state not in {"capture", "hold"}:
        continue
      timestamp = result.frame.timestamp
      nearby = [crossing - timestamp for crossing in zero_crossings
                if abs(crossing - timestamp) <= ZERO_CROSSING_WINDOW_S]
      lead = min(nearby, key=abs) if nearby else math.nan
      scores.append(TriggerScore(
        route_id,
        timestamp,
        result.state,
        result.reason,
        result.frame.error_deg,
        _predicted_crossing_s(result.frame),
        lead,
        result.frame.bypass_reason,
      ))
  return scores


def summarize(results: Sequence[ShadowResult], *, steer_max: float = 1.0) -> ShadowSummary:
  state_frames = Counter(result.state for result in results)
  gate_frames = Counter(
    result.frame.bypass_reason for result in results if result.frame.bypass_reason is not None
  )
  gate_conditions = {
    "stale inputs": sum(not result.frame.inputs_fresh for result in results),
    "inactive": sum(not result.frame.active for result in results),
    "driver steering": sum(result.frame.steering_pressed for result in results),
    "lane change": sum(result.frame.lane_change_active for result in results),
    "steer fault": sum(result.frame.steer_fault for result in results),
    "safety limited": sum(result.frame.safety_limited for result in results),
    "saturated": sum(result.frame.saturated for result in results),
  }
  scores = score_triggers(results)
  leads = [score.actual_crossing_lead_s for score in scores if math.isfinite(score.actual_crossing_lead_s)]
  trigger_timing_by_state = {}
  for state in sorted({score.state for score in scores}):
    state_scores = [score for score in scores if score.state == state]
    state_leads = [
      score.actual_crossing_lead_s for score in state_scores
      if math.isfinite(score.actual_crossing_lead_s)
    ]
    state_predictions = [
      score.predicted_crossing_s for score in state_scores
      if math.isfinite(score.predicted_crossing_s)
    ]
    prediction_errors = [
      score.predicted_crossing_s - score.actual_crossing_lead_s for score in state_scores
      if math.isfinite(score.predicted_crossing_s) and math.isfinite(score.actual_crossing_lead_s)
    ]
    trigger_timing_by_state[state] = {
      "events": len(state_scores),
      "with_crossing": len(state_leads),
      "predicted_valid": len(state_predictions),
      "actual_lead_median_s": median(state_leads) if state_leads else None,
      "actual_lead_p10_s": _percentile(state_leads, 10.0),
      "actual_lead_p90_s": _percentile(state_leads, 90.0),
      "prediction_error_median_s": median(prediction_errors) if prediction_errors else None,
    }
  deltas = [result.proposed_torque - result.frame.live_torque for result in results]
  routes = {result.frame.route_id for result in results}
  sample_durations = [0.0] * len(results)
  for index, (previous, current) in enumerate(zip(results, results[1:], strict=False)):
    dt = current.frame.timestamp - previous.frame.timestamp
    if current.frame.route_id == previous.frame.route_id and 0.0 < dt <= MAX_INPUT_AGE_S:
      sample_durations[index] = dt
  duration_s = sum(sample_durations)
  rms = math.sqrt(sum(delta * delta for delta in deltas) / len(deltas)) if deltas else 0.0
  abs_deltas = [abs(delta) for delta in deltas]
  live_applied_deltas = [
    result.frame.applied_torque - result.frame.live_torque for result in results
    if math.isfinite(result.frame.applied_torque)
  ]
  live_applied_rms = (
    math.sqrt(sum(delta * delta for delta in live_applied_deltas) / len(live_applied_deltas))
    if live_applied_deltas else 0.0
  )
  abs_live_applied_deltas = [abs(delta) for delta in live_applied_deltas]
  release_threshold = float(getattr(LatStiction, "DIRECTION_CHANGE_TORQUE", 0.03))
  nonfinite_input_frames = sum(
    not all(math.isfinite(value) for value in (
      result.frame.timestamp,
      result.frame.speed_mps,
      result.frame.measured_angle_deg,
      result.frame.error_deg,
      result.frame.desired_angle_deg,
      result.frame.desired_rate_deg_s,
      result.frame.wheel_rate_deg_s,
      result.frame.live_torque,
    ))
    for result in results
  )

  torque_delta_by_state = {}
  opposite_torque_by_state = {}
  for state in sorted(state_frames):
    state_items = [
      (result, duration) for result, duration in zip(results, sample_durations, strict=True)
      if result.state == state
    ]
    state_deltas = [abs(result.proposed_torque - result.frame.live_torque) for result, _ in state_items]
    torque_delta_by_state[state] = {
      "frames": len(state_items),
      "rms": math.sqrt(sum(delta * delta for delta in state_deltas) / len(state_deltas)),
      "p95": _percentile(state_deltas, 95.0) or 0.0,
      "max": max(state_deltas, default=0.0),
    }
    opposite_items = [
      (result, duration) for result, duration in state_items
      if result.proposed_torque * result.frame.live_torque < 0.0
    ]
    opposite_torque_by_state[state] = {
      "frames": len(opposite_items),
      "duration_s": sum(duration for _, duration in opposite_items),
      "max_delta": max((
        abs(result.proposed_torque - result.frame.live_torque) for result, _ in opposite_items
      ), default=0.0),
    }
  max_same_sign_torque_delta = max((
    abs(result.proposed_torque - result.frame.live_torque) for result in results
    if result.proposed_torque * result.frame.live_torque >= 0.0
  ), default=0.0)

  hold_runs: list[list[int]] = []
  for index, result in enumerate(results):
    clean_hold = result.state == "hold" and result.frame.bypass_reason is None
    contiguous = (
      bool(hold_runs)
      and index == hold_runs[-1][-1] + 1
      and sample_durations[index - 1] > 0.0
    )
    if clean_hold and contiguous:
      hold_runs[-1].append(index)
    elif clean_hold:
      hold_runs.append([index])
  max_hold_duration_s = max((
    sum(sample_durations[index] for index in run) for run in hold_runs
  ), default=0.0)
  hold_outer_error_frames = sum(
    abs(result.frame.error_deg) >= _error_hi(result.frame.speed_mps)
    for result in results if result.state == "hold" and result.frame.bypass_reason is None
  )
  monotonic_outer_error_hold_runs = 0
  for run in hold_runs:
    first = results[run[0]].frame
    if abs(first.error_deg) >= _error_hi(first.speed_mps):
      continue
    previous_error = abs(first.error_deg)
    for index in run[1:]:
      current = results[index].frame
      current_error = abs(current.error_deg)
      if current_error < previous_error:
        break
      if current_error >= _error_hi(current.speed_mps):
        monotonic_outer_error_hold_runs += 1
        break
      previous_error = current_error

  def angle_coverage(selected: Iterable[ShadowResult]) -> dict[str, int]:
    selected = list(selected)
    return {
      "abs_ge_20": sum(abs(result.frame.measured_angle_deg) >= 20.0 for result in selected),
      "abs_ge_45": sum(abs(result.frame.measured_angle_deg) >= 45.0 for result in selected),
      "abs_ge_90": sum(abs(result.frame.measured_angle_deg) >= 90.0 for result in selected),
    }

  return ShadowSummary(
    frames=len(results),
    routes=len(routes),
    duration_s=duration_s,
    baseline_stiction_on_frames=sum(result.frame.baseline_stiction_enabled is True for result in results),
    baseline_stiction_off_frames=sum(result.frame.baseline_stiction_enabled is False for result in results),
    baseline_stiction_unknown_frames=sum(result.frame.baseline_stiction_enabled is None for result in results),
    active_frames=sum(result.frame.active for result in results),
    clean_frames=sum(result.frame.bypass_reason is None for result in results),
    angle_coverage_frames=angle_coverage(results),
    clean_angle_coverage_frames=angle_coverage(
      result for result in results if result.frame.bypass_reason is None
    ),
    decision_angle_coverage_frames=angle_coverage(
      result for result in results
      if result.frame.bypass_reason is None and _is_active_decision(result.state)
    ),
    blinker_frames=sum(result.frame.blinker_active for result in results),
    state_frames=dict(sorted(state_frames.items())),
    transitions=sum(result.transition for result in results),
    transition_reasons=dict(sorted(Counter(
      result.reason for result in results if result.transition
    ).items())),
    trigger_events=len(scores),
    triggers_with_crossing=len(leads),
    trigger_lead_median_s=median(leads) if leads else None,
    trigger_lead_p10_s=_percentile(leads, 10.0),
    trigger_lead_p90_s=_percentile(leads, 90.0),
    trigger_timing_by_state=trigger_timing_by_state,
    gate_frames=dict(sorted(gate_frames.items())),
    gate_condition_frames=gate_conditions,
    gated_decision_violations=sum(
      result.frame.bypass_reason is not None and _is_active_decision(result.state)
      for result in results
    ),
    nonfinite_input_frames=nonfinite_input_frames,
    nonfinite_output_frames=sum(not math.isfinite(result.proposed_torque) for result in results),
    torque_bound_violations=sum(abs(result.proposed_torque) > steer_max + 1e-9 for result in results),
    hold_opposite_live_at_or_above_release_frames=sum(
      result.state == "hold"
      and result.proposed_torque * result.frame.live_torque < 0.0
      and abs(result.frame.live_torque) >= release_threshold
      for result in results
    ),
    torque_delta_rms=rms,
    torque_delta_p95=_percentile(abs_deltas, 95.0) or 0.0,
    torque_delta_max=max(abs_deltas, default=0.0),
    torque_delta_by_state=torque_delta_by_state,
    opposite_torque_by_state=opposite_torque_by_state,
    max_same_sign_torque_delta=max_same_sign_torque_delta,
    max_hold_duration_s=max_hold_duration_s,
    hold_outer_error_frames=hold_outer_error_frames,
    monotonic_outer_error_hold_runs=monotonic_outer_error_hold_runs,
    live_applied_delta_rms=live_applied_rms,
    live_applied_delta_p95=_percentile(abs_live_applied_deltas, 95.0) or 0.0,
    live_applied_delta_max=max(abs_live_applied_deltas, default=0.0),
  )


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("sources", nargs="+", help="local rlog.zst files, globs, or archive directories")
  parser.add_argument("--max-files", type=int, help="limit replay to the first N expanded rlogs")
  parser.add_argument("--steer-max", type=float, default=1.0)
  parser.add_argument("--json-output", type=Path, help="optional path for the summary JSON")
  return parser


def main() -> int:
  args = build_parser().parse_args()
  sources = expand_sources(args.sources)
  if args.max_files is not None:
    sources = sources[:args.max_files]
  if not sources:
    raise SystemExit("no local rlogs found")
  frames = (frame for source in sources for frame in iter_shadow_frames(source))
  results = replay_shadow(frames, steer_max=args.steer_max)
  summary = asdict(summarize(results, steer_max=args.steer_max))
  output = json.dumps(summary, indent=2, allow_nan=False) + "\n"
  if args.json_output is not None:
    args.json_output.write_text(output, encoding="utf-8")
  print(output, end="")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
