from dataclasses import replace
import math
from types import SimpleNamespace

import pytest

import lat_stiction_shadow
from lat_stiction_shadow import ShadowFrame, iter_shadow_frames, replay_shadow, score_triggers, summarize
from openpilot.sunnypilot.nrdr.lat_stiction import LatStiction


DT = 0.01


def frame(index: int, **overrides) -> ShadowFrame:
  values = {
    "route_id": "route-a",
    "timestamp": 10.0 + index * DT,
    "active": True,
    "speed_mps": 12.0,
    "measured_angle_deg": 10.0,
    "error_deg": 0.0,
    "desired_angle_deg": 10.0,
    "desired_rate_deg_s": 0.0,
    "wheel_rate_deg_s": 0.0,
    "live_torque": 0.30,
    "applied_torque": 0.30,
    "baseline_stiction_enabled": False,
  }
  values.update(overrides)
  return ShadowFrame(**values)


@pytest.mark.parametrize("gate", [
  {"active": False},
  {"steering_pressed": True},
  {"lane_change_active": True},
  {"steer_fault": True},
  {"safety_limited": True},
  {"saturated": True},
  {"inputs_fresh": False},
])
def test_shadow_decisions_bypass_driver_lane_fault_and_limit_frames(gate):
  quiet = [frame(index) for index in range(80)]
  gated = [frame(index + len(quiet), live_torque=0.45, **gate) for index in range(40)]

  results = replay_shadow([*quiet, *gated])

  assert all(result.state not in {"throw", "capture", "hold", "reacquire"}
             for result in results[-len(gated):])
  assert results[-1].proposed_torque == pytest.approx(results[-1].frame.live_torque)
  summary = summarize(results)
  assert summary.gated_decision_violations == 0
  assert summary.nonfinite_input_frames == 0
  assert summary.nonfinite_output_frames == 0
  assert summary.torque_bound_violations == 0
  assert sum(summary.gate_frames.values()) == len(gated)


def test_blinker_without_model_lane_change_does_not_bypass(monkeypatch):
  def event(timestamp, which, **payload):
    return SimpleNamespace(logMonoTime=int(timestamp * 1e9), which=lambda: which, **payload)

  pid = SimpleNamespace(
    active=True,
    steeringAngleDesiredDeg=12.0,
    angleError=0.4,
    saturated=False,
  )
  events = [
    event(1.000, "modelV2", modelV2=SimpleNamespace(meta=SimpleNamespace(laneChangeState="off"))),
    event(1.000, "carState", carState=SimpleNamespace(
      vEgo=12.0,
      steeringAngleDeg=11.6,
      steeringRateDeg=2.0,
      steeringPressed=False,
      leftBlinker=True,
      rightBlinker=False,
      steerFaultTemporary=False,
      steerFaultPermanent=False,
    )),
    event(1.000, "carControl", carControl=SimpleNamespace(
      latActive=True,
      actuators=SimpleNamespace(torque=0.2),
    )),
    # carOutput is diagnostic and may lag; it is not an input to LatStiction.
    event(0.900, "carOutput", carOutput=SimpleNamespace(
      actuatorsOutput=SimpleNamespace(torque=0.1),
    )),
    event(1.000, "controlsState", controlsState=SimpleNamespace(
      lateralControlState=SimpleNamespace(which=lambda: "pidState", pidState=pid),
    )),
  ]
  monkeypatch.setattr(lat_stiction_shadow, "iter_local_events", lambda _source: iter(events))

  joined = list(iter_shadow_frames("route-a/rlog.zst"))

  assert len(joined) == 1
  assert joined[0].blinker_active
  assert not joined[0].lane_change_active
  assert not joined[0].safety_limited
  assert joined[0].bypass_reason is None


def test_predictive_capture_triggers_before_recorded_error_crossing():
  probe = LatStiction(DT, 1.0)
  if not hasattr(probe, "state"):
    pytest.skip("predictive TRACK/CAPTURE/HOLD prototype has not landed")
  frames = []
  for index in range(80):
    # Relative error closes at 5 deg/s and crosses zero near 0.4 seconds.
    error = 2.0 - 5.0 * index * DT
    frames.append(frame(
      index,
      error_deg=error,
      desired_rate_deg_s=0.0,
      wheel_rate_deg_s=5.0,
      live_torque=0.25 + 0.02 * math.sin(index * 0.1),
    ))

  results = replay_shadow(frames)
  captures = [result for result in results if result.transition and result.state == "capture"]

  assert captures
  assert captures[0].frame.error_deg > 0.0
  scores = score_triggers(results)
  capture_score = next(score for score in scores if score.state == "capture")
  assert 0.0 < capture_score.actual_crossing_lead_s <= 0.5
  assert 0.0 < capture_score.predicted_crossing_s <= 0.5
  timing = summarize(results).trigger_timing_by_state["capture"]
  assert timing["events"] >= 1
  assert timing["with_crossing"] >= 1
  assert timing["prediction_error_median_s"] == pytest.approx(0.0)


def test_shadow_is_left_right_symmetric():
  left = [frame(
    index,
    error_deg=1.5 - 0.04 * index,
    desired_angle_deg=15.0,
    desired_rate_deg_s=-1.0,
    wheel_rate_deg_s=3.0,
    live_torque=0.35,
    applied_torque=0.35,
  ) for index in range(80)]
  right = [replace(
    item,
    error_deg=-item.error_deg,
    desired_angle_deg=-item.desired_angle_deg,
    desired_rate_deg_s=-item.desired_rate_deg_s,
    wheel_rate_deg_s=-item.wheel_rate_deg_s,
    live_torque=-item.live_torque,
    applied_torque=-item.applied_torque,
  ) for item in left]

  left_results = replay_shadow(left)
  right_results = replay_shadow(right)

  assert [result.state for result in left_results] == [result.state for result in right_results]
  assert [result.proposed_torque for result in left_results] == pytest.approx(
    [-result.proposed_torque for result in right_results],
  )


def test_trigger_scoring_and_torque_metrics_are_deterministic():
  class ScriptedStage:
    def __init__(self, _dt, _steer_max):
      self.calls = 0
      self.state = "track"

    def update(self, _active, _speed, _error, _desired_rate, _wheel_rate, live_torque,
               _pressed, _lane_change, _saturated):
      self.calls += 1
      if self.calls == 2:
        self.state = "capture"
      elif self.calls == 3:
        self.state = "hold"
      elif self.calls == 5:
        self.state = "track"
      return live_torque + 0.1

  frames = [frame(index, error_deg=error) for index, error in enumerate((1.0, 0.5, 0.1, -0.1, -0.2))]
  results = replay_shadow(frames, stage_factory=ScriptedStage)
  scores = score_triggers(results)
  summary = summarize(results)

  assert [score.state for score in scores] == ["capture", "hold"]
  assert [score.reason for score in scores] == ["unknown", "unknown"]
  assert scores[0].actual_crossing_lead_s == pytest.approx(0.015)
  assert scores[1].actual_crossing_lead_s == pytest.approx(0.005)
  assert summary.trigger_events == 2
  assert summary.triggers_with_crossing == 2
  assert summary.transitions == 3
  assert summary.transition_reasons == {"unknown": 3}
  assert summary.torque_delta_rms == pytest.approx(0.1)
  assert summary.torque_delta_p95 == pytest.approx(0.1)
  assert summary.torque_delta_max == pytest.approx(0.1)
  assert summary.live_applied_delta_rms == pytest.approx(0.0)


def test_requested_applied_delta_is_diagnostic_not_a_bypass():
  candidate = frame(0, live_torque=0.40, applied_torque=0.10)

  results = replay_shadow([candidate])
  summary = summarize(results)

  assert candidate.bypass_reason is None
  assert summary.live_applied_delta_rms == pytest.approx(0.30)
  assert summary.live_applied_delta_p95 == pytest.approx(0.30)
  assert summary.live_applied_delta_max == pytest.approx(0.30)


def test_summary_reports_clean_and_decision_high_angle_coverage():
  class CapturingStage:
    def __init__(self, _dt, _steer_max):
      self.state = "track"

    def update(self, _active, _speed, error, _desired_rate, _wheel_rate, live_torque,
               _pressed, _lane_change, _saturated):
      self.state = "capture" if error > 0.0 else "track"
      return live_torque

  frames = [
    frame(0, measured_angle_deg=10.0, error_deg=0.0),
    frame(1, measured_angle_deg=25.0, error_deg=1.0),
    frame(2, measured_angle_deg=50.0, error_deg=1.0),
    frame(3, measured_angle_deg=100.0, error_deg=1.0, steering_pressed=True),
  ]

  summary = summarize(replay_shadow(frames, stage_factory=CapturingStage))

  assert summary.active_frames == 4
  assert summary.clean_frames == 3
  assert summary.angle_coverage_frames == {"abs_ge_20": 3, "abs_ge_45": 2, "abs_ge_90": 1}
  assert summary.clean_angle_coverage_frames == {"abs_ge_20": 2, "abs_ge_45": 1, "abs_ge_90": 0}
  assert summary.decision_angle_coverage_frames == {"abs_ge_20": 2, "abs_ge_45": 1, "abs_ge_90": 0}


def test_summary_scores_opposite_torque_and_hold_release_risk():
  class ScriptedStage:
    def __init__(self, _dt, _steer_max):
      self.calls = 0
      self.state = "hold"

    def update(self, _active, _speed, _error, _desired_rate, _wheel_rate, live_torque,
               _pressed, _lane_change, _saturated):
      self.calls += 1
      if self.calls <= 4:
        self.state = "hold"
        return -0.1
      self.state = "track"
      return live_torque + 0.2

  frames = [frame(index, speed_mps=8.0, error_deg=error, live_torque=0.4)
            for index, error in enumerate((0.1, 0.3, 0.7, 1.0, 1.1))]

  summary = summarize(replay_shadow(frames, stage_factory=ScriptedStage))

  assert summary.opposite_torque_by_state["hold"] == {
    "frames": 4,
    "duration_s": pytest.approx(0.04),
    "max_delta": pytest.approx(0.5),
  }
  assert summary.hold_opposite_live_at_or_above_release_frames == 4
  assert summary.max_same_sign_torque_delta == pytest.approx(0.2)
  assert summary.max_hold_duration_s == pytest.approx(0.04)
  assert summary.hold_outer_error_frames == 1
  assert summary.monotonic_outer_error_hold_runs == 1


def test_timestamp_gap_resets_shadow_state():
  instances = []

  class CountingStage:
    def __init__(self, _dt, _steer_max):
      self.calls = 0
      self.state = "track"
      instances.append(self)

    def update(self, *_args):
      self.calls += 1
      return 0.0

  frames = [frame(0), frame(1), replace(frame(2), timestamp=11.0)]

  replay_shadow(frames, stage_factory=CountingStage)

  assert [instance.calls for instance in instances] == [2, 1]
