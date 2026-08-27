#!/usr/bin/env python3
"""Read-only lateral attribution from local openpilot route logs.

This tool separates four questions which cannot be answered from steering error alone:

* Is the model path already inside the detected lane center?
* Does fused yaw follow the requested curvature, or does the controller over/under-track it?
* Which logged P/I/feed-forward terms are carrying the actuator request?
* Do the data show a phase-only lag or a vehicle-model/steer-ratio mapping mismatch?

The report is observational. It never changes params or logs, never treats unmatched
routes/configurations as a causal A/B test, and cannot separate a model-path offset caused
by planning from one caused by lane perception or calibration.

Examples:
  python3 -m openpilot.nrdr.tools.lateral.attribution /data/media/0/realdata/<route>--*/rlog.zst
  python3 -m openpilot.nrdr.tools.lateral.attribution /data/media/0/realdata/<route> --json lateral.json
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass, field
import glob
import json
import math
from pathlib import Path
from statistics import median
import sys

import numpy as np

from openpilot.nrdr.features.lateral.model_policy import SteerRatioModelPolicy, classify_steer_ratio_model


MPS_TO_MPH = 2.236936
MIN_LANE_PROB = 0.60
MAX_LANE_STD = 0.30
MAX_PATH_STD = 0.35
MIN_LANE_WIDTH_M = 2.60
MAX_LANE_WIDTH_M = 4.80
MIN_CURVATURE = 1e-4
DEFAULT_LOOKAHEADS_M = (10.0, 20.0, 30.0)
SPEED_EDGES_MPH = (5.0, 15.0, 25.0, 35.0, 50.0, 65.0, 120.0)
ANGLE_EDGES_DEG = (3.0, 10.0, 20.0, 45.0, 1000.0)
RELEVANT_PARAMS = (
  "LagdToggle",
  "LagdToggleDelay",
  "LaneCentering",
  "LaneCenteringE2EAuthority",
  "LaneCenteringPauseOnSignal",
  "LaneCenterOffset",
  "NeuralNetworkLateralControl",
  "NrdrHandcraftedLateralTune",
  "NrdrLearnAngleOffset",
  "NrdrLearnSteerRatio",
  "NrdrLearnStiffness",
  "ModelManager_ActiveBundle",
  "NrdrLaneChangeEndpointSteerRatio",
  "NrdrSteerRatioCenterClarity",
  "NrdrSteerRatioOuterClarity",
  "NrdrSteerRatioCenterCivic",
  "NrdrSteerRatioOuterCivic",
  "NrdrSteerRatioCenterAccord",
  "NrdrSteerRatioOuterAccord",
  "NrdrSteerRatioCenterCrv5g",
  "NrdrSteerRatioOuterCrv5g",
  "NrdrSteerRatioCenterInsight",
  "NrdrSteerRatioOuterInsight",
  "NrdrSteerRatioMin",
  "NrdrSteerRatioMax",
  "NrdrSteerRatioOffset",
  "LatPScaleLowSpeed",
  "LatPScaleStandard",
  "LatPScaleHighway",
  "LatIScaleLowSpeed",
  "LatIScaleStandard",
  "LatIScaleHighway",
  "LatFScaleLowSpeed",
  "LatFScaleStandard",
  "LatFScaleHighway",
  "HondaCenterScale",
  "HondaCenterBoostThreshold",
  "HondaCenterBoostMinSpeed",
  "HondaInjectionTest",
  "NrdrLatRateDamping",
  "NrdrLatRateDampingFadeSpeed",
  "NrdrLatStiction",
  "NrdrStarPilotPid",
  "NrdrTuneLearner",
  "NrdrTuneLearnerStrength",
  "NrdrTuneLearnerRate",
  "NrdrTuneLearnerMap",
)
REQUIRED_SERVICES = frozenset(("carState", "carControl", "controlsState", "deviceMotion", "modelV2", "lateralDelay", "vehicleParameters"))


def finite(value, default: float = math.nan) -> float:
  try:
    result = float(value)
  except (TypeError, ValueError):
    return default
  return result if math.isfinite(result) else default


def finite_median(values: Iterable[float]) -> float | None:
  valid = [float(value) for value in values if math.isfinite(float(value))]
  return float(median(valid)) if valid else None


def percentile(values: Iterable[float], percent: float) -> float | None:
  valid = np.asarray([float(value) for value in values if math.isfinite(float(value))], dtype=float)
  return float(np.percentile(valid, percent)) if valid.size else None


def fraction(values: Iterable[bool]) -> float | None:
  items = list(values)
  return float(sum(items) / len(items)) if items else None


def sign(value: float) -> float:
  return 1.0 if value > 0.0 else (-1.0 if value < 0.0 else 0.0)


def is_fresh(now: float, timestamp: float, max_age_s: float) -> bool:
  if not (math.isfinite(now) and math.isfinite(timestamp) and math.isfinite(max_age_s)) or max_age_s < 0.0:
    return False
  age = now - timestamp
  return 0.0 <= age <= max_age_s


def parse_edges(raw: str, name: str) -> tuple[float, ...]:
  try:
    edges = tuple(float(value.strip()) for value in raw.split(","))
  except ValueError as exc:
    raise argparse.ArgumentTypeError(f"{name} must be comma-separated numbers") from exc
  if len(edges) < 2 or any(not math.isfinite(value) for value in edges) or any(b <= a for a, b in zip(edges, edges[1:], strict=False)):
    raise argparse.ArgumentTypeError(f"{name} must contain at least two increasing finite values")
  return edges


def _source_sort_key(source: str) -> tuple[str, int, str]:
  parent = Path(source).parent.name
  route, separator, segment = parent.rpartition("--")
  return route if separator else parent, int(segment) if segment.isdigit() else -1, source


def expand_sources(raw_sources: Sequence[str], log_kind: str = "auto") -> list[str]:
  """Expand paths/globs while preserving route identifiers for LogReader."""
  sources: list[str] = []
  wanted = ("rlog.zst", "rlog") if log_kind == "rlog" else (("qlog.zst", "qlog") if log_kind == "qlog" else ())
  for raw in raw_sources:
    matches = glob.glob(raw, recursive=True)
    candidates = matches or [raw]
    for candidate in candidates:
      path = Path(candidate)
      if path.is_dir():
        if wanted:
          sources.extend(str(item) for name in wanted for item in path.rglob(name))
        else:
          by_segment: defaultdict[Path, dict[str, Path]] = defaultdict(dict)
          for name in ("rlog.zst", "rlog", "qlog.zst", "qlog"):
            for item in path.rglob(name):
              by_segment[item.parent][name] = item
          for files in by_segment.values():
            selected = files.get("rlog.zst") or files.get("rlog") or files.get("qlog.zst") or files.get("qlog")
            if selected is not None:
              sources.append(str(selected))
      elif path.is_file() or candidate == raw:
        sources.append(candidate)
  return sorted(dict.fromkeys(sources), key=_source_sort_key)


def route_id(source: str) -> str:
  path = Path(source)
  if path.exists():
    parent = path.parent.name
    route, separator, segment = parent.rpartition("--")
    return route if separator and segment.isdigit() else parent
  return source.split("/", 1)[0]


def decode_params(entries) -> dict[str, str]:
  wanted = set(RELEVANT_PARAMS)
  decoded = {}
  for entry in entries:
    key = str(entry.key)
    if key not in wanted:
      continue
    try:
      decoded[key] = bytes(entry.value).decode("utf-8", errors="replace").strip("\x00")
    except Exception:
      decoded[key] = "<unreadable>"
  return decoded


def param_bool(settings: dict[str, str], key: str) -> bool | None:
  if key not in settings:
    return None
  return settings[key].strip().lower() not in ("", "0", "false", "off", "no")


def logged_steer_ratio_model_policy(raw_bundle: str | None) -> SteerRatioModelPolicy:
  try:
    bundle = json.loads(raw_bundle) if raw_bundle else None
  except (json.JSONDecodeError, TypeError):
    bundle = None
  return classify_steer_ratio_model(bundle)


@dataclass
class Context:
  route: str
  fingerprint: str = "UNKNOWN"
  branch: str = "unknown"
  commit: str = "unknown"
  steer_ratio: float = math.nan
  steer_actuator_delay: float = math.nan
  eps_firmware: str = "unknown"
  model_sr_policy: SteerRatioModelPolicy = SteerRatioModelPolicy.UNKNOWN
  settings: dict[str, str] = field(default_factory=dict)

  @property
  def cohort(self) -> str:
    settings = ",".join(f"{key}={value}" for key, value in sorted(self.settings.items()))
    return f"{self.fingerprint}|{self.branch}@{self.commit[:12]}|eps={self.eps_firmware}|sr={self.model_sr_policy.value}|{settings}"


@dataclass(frozen=True)
class ControllerReading:
  kind: str
  active: bool
  desired_angle_deg: float
  actual_angle_deg: float
  angle_error_deg: float
  p: float
  i: float
  f: float
  output: float
  saturated: bool


@dataclass(frozen=True)
class ControlSample:
  route: str
  cohort: str
  timestamp: float
  kind: str
  speed_mps: float
  desired_angle_deg: float
  actual_angle_deg: float
  steering_rate_deg_s: float
  desired_curvature: float
  vehicle_model_curvature: float
  yaw_curvature_raw: float
  p: float
  i: float
  f: float
  output: float
  saturated: bool
  params_valid: bool

  @property
  def phase(self) -> str:
    if abs(self.steering_rate_deg_s) <= 1.5:
      return "steady"
    return "turn-in" if self.desired_angle_deg * self.steering_rate_deg_s > 0.0 else "unwind"


@dataclass(frozen=True)
class LaneSample:
  route: str
  cohort: str
  timestamp: float
  lookahead_m: float
  inside_offset_m: float
  lane_width_m: float
  lane_probability: float
  lane_std: float
  path_std: float | None
  confidence: str
  direction: str = "unknown"
  speed_mph: float = math.nan
  angle_deg: float = math.nan


@dataclass(frozen=True)
class DelaySample:
  route: str
  cohort: str
  effective_s: float
  estimate_s: float
  estimate_std_s: float
  status: str


@dataclass
class ScanResult:
  controls: list[ControlSample] = field(default_factory=list)
  lanes: list[LaneSample] = field(default_factory=list)
  delays: list[DelaySample] = field(default_factory=list)
  learned_steer_ratios: defaultdict[str, list[float]] = field(default_factory=lambda: defaultdict(list))
  configured_steer_ratios: defaultdict[str, set[float]] = field(default_factory=lambda: defaultdict(set))
  lane_attempts: Counter[tuple[str, float]] = field(default_factory=Counter)
  contexts: dict[str, Context] = field(default_factory=dict)
  files_read: int = 0
  files_failed: int = 0
  errors: list[str] = field(default_factory=list)
  incomplete_sources: dict[str, list[str]] = field(default_factory=dict)


def extract_controller_reading(lateral_state, fingerprint: str, actual_angle_deg: float,
                               desired_angle_deg: float, nnlc_enabled: bool | None = None,
                               firmware_vgr_pid_only: bool = False) -> ControllerReading | None:
  """Decode PID logs, including Clarity's PID-in-torqueState compatibility wrapper."""
  try:
    which = lateral_state.which()
    state = getattr(lateral_state, which)
  except (AttributeError, TypeError, ValueError):
    return None

  if which == "pidState":
    return ControllerReading(
      "pidState",
      bool(state.active),
      finite(state.steeringAngleDesiredDeg),
      finite(state.steeringAngleDeg),
      finite(state.angleError),
      finite(state.p), finite(state.i), finite(state.f), finite(state.output), bool(state.saturated),
    )

  if which != "torqueState" or fingerprint != "HONDA_CLARITY":
    return None

  logged_error = finite(state.error)
  expected_error = desired_angle_deg - actual_angle_deg
  error_matches_angle = (
    math.isfinite(expected_error)
    and math.isfinite(logged_error)
    and abs(logged_error - expected_error) <= max(0.5, 0.15 * abs(expected_error))
  )
  if not error_matches_angle or (nnlc_enabled is True and not firmware_vgr_pid_only):
    return None
  return ControllerReading(
    "clarityPidWrappedInTorqueState",
    bool(state.active),
    desired_angle_deg,
    actual_angle_deg,
    logged_error,
    finite(state.p), finite(state.i), finite(state.f), finite(state.output), bool(state.saturated),
  )


def _valid_xy(x: np.ndarray, y: np.ndarray) -> bool:
  return bool(x.size >= 2 and x.size == y.size and np.isfinite(x).all() and np.isfinite(y).all() and np.all(np.diff(x) > 0.0))


def lane_observation(model, curvature: float, lookahead_m: float) -> tuple[LaneSample | None, str | None]:
  """Return a confidence-gated, direction-normalized model-path offset.

  Positive ``inside_offset_m`` means the model path is toward the inside of the turn
  relative to the midpoint of the two detected lane lines. Model y and curvature are
  both positive to the vehicle's right in these logs, so sign(curvature) normalizes L/R.
  """
  if not math.isfinite(curvature) or abs(curvature) < MIN_CURVATURE:
    return None, "curvature"
  try:
    lane_lines = model.laneLines
    probabilities = np.asarray(model.laneLineProbs, dtype=float)
    stds = np.asarray(model.laneLineStds, dtype=float)
    if len(lane_lines) < 3 or probabilities.size < 3 or stds.size < 3:
      return None, "missing lane lines"
    lane_prob = float(min(probabilities[1], probabilities[2]))
    lane_std = float(max(stds[1], stds[2]))
    if not (MIN_LANE_PROB <= lane_prob <= 1.0) or not (0.0 <= lane_std <= MAX_LANE_STD):
      return None, "lane confidence"

    left_x = np.asarray(lane_lines[1].x, dtype=float)
    left_y = np.asarray(lane_lines[1].y, dtype=float)
    right_x = np.asarray(lane_lines[2].x, dtype=float)
    right_y = np.asarray(lane_lines[2].y, dtype=float)
    path_x = np.asarray(model.position.x, dtype=float)
    path_y = np.asarray(model.position.y, dtype=float)
    if not (_valid_xy(left_x, left_y) and _valid_xy(right_x, right_y) and _valid_xy(path_x, path_y)):
      return None, "invalid geometry"
    if any(x[0] > lookahead_m or x[-1] < lookahead_m for x in (left_x, right_x, path_x)):
      return None, "lookahead coverage"

    left = float(np.interp(lookahead_m, left_x, left_y))
    right = float(np.interp(lookahead_m, right_x, right_y))
    width = right - left
    if not MIN_LANE_WIDTH_M <= width <= MAX_LANE_WIDTH_M:
      return None, "lane width"

    path_std = None
    path_y_std = np.asarray(getattr(model.position, "yStd", []), dtype=float)
    if path_y_std.size:
      if not _valid_xy(path_x, path_y_std):
        return None, "path uncertainty"
      path_std = float(np.interp(lookahead_m, path_x, path_y_std))
      if not 0.0 <= path_std <= MAX_PATH_STD:
        return None, "path uncertainty"

    center = 0.5 * (left + right)
    inside = sign(curvature) * (float(np.interp(lookahead_m, path_x, path_y)) - center)
    high = lane_prob >= 0.75 and lane_std <= 0.20 and 2.8 <= width <= 4.2 and path_std is not None and path_std <= 0.25
    return LaneSample("", "", 0.0, lookahead_m, inside, width, lane_prob, lane_std, path_std, "high" if high else "medium"), None
  except (AttributeError, IndexError, TypeError, ValueError):
    return None, "invalid geometry"


def collect(sources: Sequence[str], log_kind: str = "auto", min_speed_mph: float = 5.0,
            min_angle_deg: float = 3.0, max_pair_age_s: float = 0.25,
            lookaheads_m: Sequence[float] = DEFAULT_LOOKAHEADS_M) -> ScanResult:
  from openpilot.tools.lib.logreader import LogReader, ReadMode

  read_mode = {"auto": ReadMode.AUTO, "rlog": ReadMode.RLOG, "qlog": ReadMode.QLOG}[log_kind]
  result = ScanResult()
  route_contexts: dict[str, Context] = {}

  for source in sources:
    route = route_id(source)
    context = route_contexts.setdefault(route, Context(route))
    v_ego = math.nan
    actual_angle = math.nan
    steering_rate = math.nan
    steering_pressed = True
    desired_angle = math.nan
    lat_active = False
    lane_change = True
    desired_curvature = math.nan
    controls_t = math.nan
    pose_t = math.nan
    yaw_rate = math.nan
    pose_valid = False
    last_sampled_pose_t = math.nan
    params_valid = False
    active_since = math.nan
    car_state_t = math.nan
    car_control_t = math.nan
    car_state_valid = False
    car_control_valid = False
    seen_services: set[str] = set()

    try:
      reader = LogReader(source, default_mode=read_mode, sort_by_time=False, only_union_types=True)
      for msg in reader:
        which = msg.which()
        timestamp = float(msg.logMonoTime) * 1e-9
        if which in REQUIRED_SERVICES:
          seen_services.add(which)

        if which == "initData":
          init = msg.initData
          context.branch = str(init.gitBranch or context.branch)
          context.commit = str(init.gitSrcCommit or init.gitCommit or context.commit)
          decoded_settings = decode_params(init.params.entries)
          context.model_sr_policy = logged_steer_ratio_model_policy(decoded_settings.pop("ModelManager_ActiveBundle", None))
          context.settings.update(decoded_settings)

        elif which == "carParams":
          car_params = msg.carParams
          context.fingerprint = str(car_params.carFingerprint)
          context.steer_ratio = finite(car_params.steerRatio)
          context.steer_actuator_delay = finite(car_params.steerActuatorDelay)
          firmware = []
          for item in car_params.carFw:
            if str(item.ecu) == "eps":
              firmware.append(bytes(item.fwVersion).split(b"\0", 1)[0].decode("ascii", errors="replace"))
          context.eps_firmware = ",".join(firmware) or context.eps_firmware

        elif which == "carState":
          car_state_t = timestamp
          car_state_valid = bool(msg.valid)
          if not car_state_valid:
            continue
          car_state = msg.carState
          v_ego = finite(car_state.vEgo)
          actual_angle = finite(car_state.steeringAngleDeg)
          steering_rate = finite(car_state.steeringRateDeg)
          steering_pressed = bool(car_state.steeringPressed)

        elif which == "carControl":
          car_control_t = timestamp
          car_control_valid = bool(msg.valid)
          if not car_control_valid:
            lat_active = False
            continue
          car_control = msg.carControl
          lat_active = bool(car_control.latActive)
          desired_angle = finite(car_control.actuators.steeringAngleDeg)

        elif which == "vehicleParameters":
          live = msg.vehicleParameters
          params_valid = bool(msg.valid and live.valid and live.steerRatioValid and live.angleOffsetValid and live.stiffnessFactorValid)
          learned_ratio = finite(live.steerRatio)
          if math.isfinite(learned_ratio):
            result.learned_steer_ratios[context.cohort].append(learned_ratio)

        elif which == "lateralDelay":
          if not msg.valid:
            continue
          delay = msg.lateralDelay
          result.delays.append(DelaySample(
            route, context.cohort, finite(delay.lateralDelay), finite(delay.lateralDelayEstimate),
            finite(delay.lateralDelayEstimateStd), str(delay.status),
          ))

        elif which == "deviceMotion":
          pose = msg.deviceMotion
          pose_t = timestamp
          yaw_rate = finite(pose.angularVelocityDevice.z)
          pose_valid = bool(msg.valid and pose.inputsOK and pose.posenetOK and pose.sensorsOK and pose.angularVelocityDevice.valid)

        elif which == "modelV2":
          model = msg.modelV2
          lane_change = not msg.valid or str(model.meta.laneChangeState) != "off"
          if not (msg.valid and context.fingerprint != "UNKNOWN" and lat_active and not steering_pressed and not lane_change
                  and car_state_valid and car_control_valid and is_fresh(timestamp, car_state_t, max_pair_age_s)
                  and is_fresh(timestamp, car_control_t, max_pair_age_s) and is_fresh(timestamp, controls_t, max_pair_age_s)
                  and math.isfinite(v_ego) and v_ego * MPS_TO_MPH >= min_speed_mph
                  and math.isfinite(desired_angle) and abs(desired_angle) >= min_angle_deg):
            continue
          direction = "right" if desired_curvature > 0.0 else "left"
          speed_bin = _edge_bin(v_ego * MPS_TO_MPH, SPEED_EDGES_MPH)
          angle_bin = _edge_bin(abs(desired_angle), ANGLE_EDGES_DEG)
          if speed_bin is None or angle_bin is None:
            continue
          for lookahead in lookaheads_m:
            result.lane_attempts[(context.cohort, float(lookahead), direction, *speed_bin, *angle_bin)] += 1
            observation, _reason = lane_observation(model, desired_curvature, float(lookahead))
            if observation is not None:
              result.lanes.append(LaneSample(
                route, context.cohort, timestamp, observation.lookahead_m, observation.inside_offset_m,
                observation.lane_width_m, observation.lane_probability, observation.lane_std,
                observation.path_std, observation.confidence, direction, v_ego * MPS_TO_MPH, abs(desired_angle),
              ))

        elif which == "controlsState":
          if not msg.valid:
            active_since = math.nan
            continue
          controls = msg.controlsState
          controls_t = timestamp
          desired_curvature = finite(controls.desiredCurvature)
          if context.fingerprint == "UNKNOWN":
            active_since = math.nan
            continue
          nnlc_enabled = param_bool(context.settings, "NeuralNetworkLateralControl")
          firmware_vgr_pid_only = (
            context.fingerprint == "HONDA_CLARITY"
            and context.model_sr_policy is not SteerRatioModelPolicy.LEGACY_DUAL_BP
            and "39990-TRW-A020" in context.eps_firmware.replace(",", "-")
          )
          reading = extract_controller_reading(
            controls.lateralControlState, context.fingerprint, actual_angle, desired_angle, nnlc_enabled, firmware_vgr_pid_only,
          )
          if reading is None:
            active_since = math.nan
            continue
          if reading.active and lat_active:
            if not math.isfinite(active_since):
              active_since = timestamp
          else:
            active_since = math.nan
            continue
          if (not math.isfinite(active_since) or timestamp < active_since or timestamp - active_since < 1.0
              or steering_pressed or lane_change or not pose_valid or not car_state_valid or not car_control_valid
              or not is_fresh(timestamp, pose_t, max_pair_age_s) or not is_fresh(timestamp, car_state_t, max_pair_age_s)
              or not is_fresh(timestamp, car_control_t, max_pair_age_s) or not math.isfinite(yaw_rate) or pose_t == last_sampled_pose_t
              or not math.isfinite(v_ego) or v_ego * MPS_TO_MPH < min_speed_mph
              or not all(math.isfinite(value) for value in (
                reading.desired_angle_deg, reading.actual_angle_deg, steering_rate,
                reading.p, reading.i, reading.f, reading.output,
              ))
              or abs(reading.desired_angle_deg) < min_angle_deg
              or not math.isfinite(desired_curvature) or abs(desired_curvature) < MIN_CURVATURE):
            continue
          last_sampled_pose_t = pose_t
          result.controls.append(ControlSample(
            route, context.cohort, timestamp, reading.kind, v_ego, reading.desired_angle_deg,
            reading.actual_angle_deg, steering_rate, desired_curvature, finite(controls.curvature),
            yaw_rate / v_ego, reading.p, reading.i, reading.f, reading.output, reading.saturated, params_valid,
          ))

      result.files_read += 1
      result.contexts[context.cohort] = Context(**asdict(context))
      if math.isfinite(context.steer_ratio):
        result.configured_steer_ratios[context.cohort].add(context.steer_ratio)
      missing = sorted(REQUIRED_SERVICES - seen_services)
      if missing:
        result.incomplete_sources[source] = missing
    except Exception as exc:
      result.files_failed += 1
      error = f"{source}: {exc}"
      result.errors.append(error)
      print(f"!! {error}", file=sys.stderr)
  return result


def _edge_bin(value: float, edges: Sequence[float]) -> tuple[float, float] | None:
  for low, high in zip(edges, edges[1:], strict=False):
    if low <= value < high:
      return float(low), float(high)
  return None


def infer_yaw_sign(samples: Sequence[ControlSample]) -> tuple[float, str]:
  products = [sample.desired_curvature * sample.yaw_curvature_raw for sample in samples
              if abs(sample.desired_curvature) >= MIN_CURVATURE and abs(sample.yaw_curvature_raw) >= MIN_CURVATURE]
  product_median = finite_median(products)
  if product_median is None:
    return 1.0, "insufficient"
  return (1.0, "native") if product_median >= 0.0 else (-1.0, "inferred sign flip")


def summarize_controls(samples: Sequence[ControlSample], min_samples: int,
                       speed_edges_mph: Sequence[float], angle_edges_deg: Sequence[float]) -> tuple[dict, list[dict]]:
  yaw_sign, yaw_sign_source = infer_yaw_sign(samples)

  def metrics(group: Sequence[ControlSample]) -> dict:
    yaw_ratios = [sign(s.desired_curvature) * yaw_sign * s.yaw_curvature_raw / abs(s.desired_curvature) for s in group]
    angle_errors = [sign(s.desired_angle_deg) * (s.desired_angle_deg - s.actual_angle_deg) for s in group]
    angle_ratios = [sign(s.desired_angle_deg) * s.actual_angle_deg / abs(s.desired_angle_deg) for s in group]
    vm_ratios = [sign(s.vehicle_model_curvature) * yaw_sign * s.yaw_curvature_raw / abs(s.vehicle_model_curvature) for s in group
                 if abs(s.vehicle_model_curvature) >= MIN_CURVATURE]
    aligned_terms = []
    output_residuals = []
    for sample in group:
      direction = sign(sample.output if abs(sample.output) > 1e-4 else sample.p + sample.i + sample.f)
      aligned_terms.append((direction * sample.p, direction * sample.i, direction * sample.f))
      output_residuals.append(direction * (sample.output - sample.p - sample.i - sample.f))
    p_values, i_values, f_values = zip(*aligned_terms, strict=True) if aligned_terms else ((), (), ())
    denominator = sum(abs(s.p) + abs(s.i) + abs(s.f) for s in group)
    return {
      "samples": len(group),
      "yaw_to_desired_median": finite_median(yaw_ratios),
      "yaw_to_desired_p10": percentile(yaw_ratios, 10.0),
      "yaw_to_desired_p90": percentile(yaw_ratios, 90.0),
      "yaw_overtrack_fraction": fraction(value > 1.10 for value in yaw_ratios),
      "yaw_undertrack_fraction": fraction(value < 0.85 for value in yaw_ratios),
      "angle_error_aligned_median_deg": finite_median(angle_errors),
      "actual_to_desired_angle_median": finite_median(angle_ratios),
      "actual_under_target_fraction": fraction(value > 0.15 for value in angle_errors),
      "vehicle_model_to_yaw_median": finite_median(vm_ratios),
      "p_aligned_median": finite_median(p_values),
      "i_aligned_median": finite_median(i_values),
      "feedforward_aligned_median": finite_median(f_values),
      "p_abs_share": sum(abs(s.p) for s in group) / denominator if denominator else None,
      "i_abs_share": sum(abs(s.i) for s in group) / denominator if denominator else None,
      "feedforward_abs_share": sum(abs(s.f) for s in group) / denominator if denominator else None,
      "output_minus_raw_p_i_f_aligned_median": finite_median(output_residuals),
      "term_scope": "raw_logged_pid_terms_before_nrdr_scaling_center_boost_damping_stiction_and_learner_overlays",
      "saturated_fraction": fraction(s.saturated for s in group),
      "params_valid_fraction": fraction(s.params_valid for s in group),
    }

  overall = metrics(samples)
  overall["yaw_sign_handling"] = yaw_sign_source
  overall["controller_kinds"] = dict(Counter(sample.kind for sample in samples))

  grouped: defaultdict[tuple[float, float, float, float, str, str], list[ControlSample]] = defaultdict(list)
  for sample in samples:
    speed_bin = _edge_bin(sample.speed_mps * MPS_TO_MPH, speed_edges_mph)
    angle_bin = _edge_bin(abs(sample.desired_angle_deg), angle_edges_deg)
    if speed_bin is not None and angle_bin is not None:
      direction = "right" if sample.desired_curvature > 0.0 else "left"
      grouped[(*speed_bin, *angle_bin, sample.phase, direction)].append(sample)
  bins = []
  for key, group in sorted(grouped.items()):
    if len(group) < min_samples:
      continue
    row = {
      "speed_mph": [key[0], key[1]],
      "angle_deg": [key[2], key[3]],
      "phase": key[4],
      "direction": key[5],
    }
    row.update(metrics(group))
    bins.append(row)
  return overall, bins


def summarize_lanes(samples: Sequence[LaneSample], attempts: Counter[tuple[str, float]]) -> list[dict]:
  grouped: defaultdict[float, list[LaneSample]] = defaultdict(list)
  for sample in samples:
    grouped[sample.lookahead_m].append(sample)
  attempt_by_distance: Counter[float] = Counter()
  for attempt_key, count in attempts.items():
    distance = attempt_key[1]
    attempt_by_distance[distance] += count

  rows = []
  for distance in sorted(attempt_by_distance):
    group = grouped[distance]
    offsets = [sample.inside_offset_m for sample in group]
    rows.append({
      "lookahead_m": distance,
      "attempted_frames": attempt_by_distance[distance],
      "accepted_frames": len(group),
      "accepted_fraction": len(group) / attempt_by_distance[distance] if attempt_by_distance[distance] else None,
      "inside_offset_median_m": finite_median(offsets),
      "inside_offset_p10_m": percentile(offsets, 10.0),
      "inside_offset_p90_m": percentile(offsets, 90.0),
      "inside_fraction": fraction(offset > 0.08 for offset in offsets),
      "confidence": dict(Counter(sample.confidence for sample in group)),
      "high_confidence_fraction": fraction(sample.confidence == "high" for sample in group),
      "directions": dict(Counter(sample.direction for sample in group)),
    })
  return rows


def strict_matched_evidence(controls: Sequence[ControlSample], lanes: Sequence[LaneSample],
                            attempts: Counter[tuple], min_samples: int) -> dict:
  """Find bilateral lane/controller evidence in overlapping speed bands."""
  yaw_sign, _source = infer_yaw_sign(controls)
  control_groups: defaultdict[tuple[str, float, float, float, float], list[ControlSample]] = defaultdict(list)
  for sample in controls:
    speed_bin = _edge_bin(sample.speed_mps * MPS_TO_MPH, SPEED_EDGES_MPH)
    angle_bin = _edge_bin(abs(sample.desired_angle_deg), ANGLE_EDGES_DEG)
    if speed_bin is not None and angle_bin is not None:
      direction = "right" if sample.desired_curvature > 0.0 else "left"
      control_groups[(direction, *speed_bin, *angle_bin)].append(sample)

  controller_bands = set()
  controller_details = []
  for (direction, speed_low, speed_high, angle_low, angle_high), group in control_groups.items():
    if len(group) < max(20, min_samples):
      continue
    yaw_ratios = [sign(s.desired_curvature) * yaw_sign * s.yaw_curvature_raw / abs(s.desired_curvature) for s in group]
    errors = [sign(s.desired_angle_deg) * (s.desired_angle_deg - s.actual_angle_deg) for s in group]
    yaw = finite_median(yaw_ratios)
    error = finite_median(errors)
    under = fraction(value > 0.15 for value in errors)
    if yaw is not None and 0.85 <= yaw <= 1.15 and error is not None and error >= 0.15 and under is not None and under >= 0.55:
      controller_bands.add((direction, speed_low, speed_high, angle_low, angle_high))
      controller_details.append({"direction": direction, "speed_mph": [speed_low, speed_high],
                                 "angle_deg": [angle_low, angle_high], "samples": len(group),
                                 "yaw_to_desired_median": yaw, "angle_error_median_deg": error,
                                 "actual_under_target_fraction": under})

  lane_groups: defaultdict[tuple[str, float, float, float, float, float], list[LaneSample]] = defaultdict(list)
  for sample in lanes:
    speed_bin = _edge_bin(sample.speed_mph, SPEED_EDGES_MPH)
    angle_bin = _edge_bin(sample.angle_deg, ANGLE_EDGES_DEG)
    if speed_bin is not None and angle_bin is not None:
      lane_groups[(sample.direction, *speed_bin, *angle_bin, sample.lookahead_m)].append(sample)
  attempt_groups: Counter[tuple[str, float, float, float, float, float]] = Counter()
  for key, count in attempts.items():
    if len(key) >= 7:
      _cohort, distance, direction, speed_low, speed_high, _angle_low, _angle_high = key
      attempt_groups[(direction, speed_low, speed_high, _angle_low, _angle_high, distance)] += count

  qualified_distances: defaultdict[tuple[str, float, float, float, float], list[dict]] = defaultdict(list)
  for key, group in lane_groups.items():
    direction, speed_low, speed_high, angle_low, angle_high, distance = key
    attempted = attempt_groups[key]
    offsets = [sample.inside_offset_m for sample in group]
    accepted_fraction = len(group) / attempted if attempted else 0.0
    high_fraction = fraction(sample.confidence == "high" for sample in group) or 0.0
    inside_fraction = fraction(offset > 0.08 for offset in offsets) or 0.0
    inside_median = finite_median(offsets)
    if (len(group) >= 10 and accepted_fraction >= 0.35 and high_fraction >= 0.40
        and inside_median is not None and inside_median >= 0.10 and inside_fraction >= 0.60):
      qualified_distances[(direction, speed_low, speed_high, angle_low, angle_high)].append({
        "lookahead_m": distance, "accepted": len(group), "attempted": attempted,
        "accepted_fraction": accepted_fraction, "high_confidence_fraction": high_fraction,
        "inside_offset_median_m": inside_median, "inside_fraction": inside_fraction,
        "angle_deg_range": [min(sample.angle_deg for sample in group), max(sample.angle_deg for sample in group)],
      })

  lane_bands = {band for band, distances in qualified_distances.items() if len(distances) >= 2}
  matched_bands = sorted(controller_bands & lane_bands)
  matched_directions = sorted({band[0] for band in matched_bands})
  return {
    "both_directions": set(matched_directions) == {"left", "right"},
    "matched_directions": matched_directions,
    "matched_speed_angle_bands": [{"direction": direction, "speed_mph": [speed_low, speed_high],
                                   "angle_deg": [angle_low, angle_high],
                                   "lane_distances": qualified_distances[(direction, speed_low, speed_high, angle_low, angle_high)]}
                                  for direction, speed_low, speed_high, angle_low, angle_high in matched_bands],
    "controller_evidence": controller_details,
    "requirements": {
      "min_lane_accepted_fraction": 0.35,
      "min_lane_high_confidence_fraction": 0.40,
      "min_lane_inside_fraction": 0.60,
      "min_persistent_lookaheads": 2,
      "requires_both_directions": True,
      "requires_overlapping_speed_band": True,
      "requires_overlapping_desired_angle_band": True,
    },
  }


def summarize_delay(samples: Sequence[DelaySample]) -> dict:
  effective = [sample.effective_s for sample in samples]
  estimates = [sample.estimate_s for sample in samples]
  return {
    "samples": len(samples),
    "effective_median_s": finite_median(effective),
    "effective_min_s": min((value for value in effective if math.isfinite(value)), default=None),
    "effective_max_s": max((value for value in effective if math.isfinite(value)), default=None),
    "estimate_median_s": finite_median(estimates),
    "estimate_std_median_s": finite_median(sample.estimate_std_s for sample in samples),
    "statuses": dict(Counter(sample.status for sample in samples)),
  }


def classify_attribution(overall: dict, bins: Sequence[dict], lane_rows: Sequence[dict], delay: dict,
                         mixed_cohorts: bool, matched: dict | None = None) -> dict:
  matched = matched or {"both_directions": False, "matched_directions": [], "matched_speed_angle_bands": []}
  yaw = overall.get("yaw_to_desired_median")
  angle_error = overall.get("angle_error_aligned_median_deg")
  under_fraction = overall.get("actual_under_target_fraction")
  p_aligned = overall.get("p_aligned_median")
  vm_ratio = overall.get("vehicle_model_to_yaw_median")

  persistent = [row for row in lane_rows if row["accepted_frames"] >= 20
                and row["inside_offset_median_m"] is not None and row["inside_offset_median_m"] >= 0.10
                and row["inside_fraction"] is not None and row["inside_fraction"] >= 0.60
                and (row["accepted_fraction"] or 0.0) >= 0.35
                and (row["high_confidence_fraction"] or 0.0) >= 0.40]
  path_inside = len(persistent) >= 2
  yaw_tracks = yaw is not None and 0.85 <= yaw <= 1.15
  actual_under_target = angle_error is not None and under_fraction is not None and angle_error >= 0.15 and under_fraction >= 0.55
  yaw_overtracks = yaw is not None and yaw > 1.15 and (overall.get("yaw_overtrack_fraction") or 0.0) >= 0.55
  delay_varied = (delay.get("effective_min_s") is not None and delay.get("effective_max_s") is not None
                  and delay["effective_max_s"] - delay["effective_min_s"] > 0.05)
  strict_path_evidence = path_inside and matched["both_directions"] and not mixed_cohorts and not delay_varied

  turn_in_yaw = finite_median(row["yaw_to_desired_median"] for row in bins
                              if row["angle_deg"][0] >= 10.0 and row["phase"] == "turn-in"
                              and row["yaw_to_desired_median"] is not None)
  steady_yaw = finite_median(row["yaw_to_desired_median"] for row in bins
                             if row["angle_deg"][0] >= 10.0 and row["phase"] == "steady"
                             and row["yaw_to_desired_median"] is not None)
  phase_lag = (turn_in_yaw is not None and steady_yaw is not None and 0.85 <= steady_yaw <= 1.15
               and turn_in_yaw < steady_yaw - 0.15)

  evidence = []
  if path_inside:
    evidence.append("Confidence-gated model path is persistently inside lane center at two or more lookaheads.")
  if yaw_tracks:
    evidence.append("Fused yaw tracks requested curvature within the observational 0.85-1.15 band.")
  if actual_under_target:
    evidence.append("Actual steering angle remains below the controller target on most sampled turns.")
  if actual_under_target and p_aligned is not None and p_aligned > 0.0:
    evidence.append("P remains corrective in the commanded direction; it is not opposing an over-command.")

  if strict_path_evidence:
    primary, confidence = "model_path_inside_detected_lane", "high"
  elif path_inside:
    primary, confidence = "model_path_inside_detected_lane", "medium" if yaw_tracks else "low"
  elif yaw_overtracks:
    primary, confidence = "controller_overtracking_observed", "medium"
    evidence.append("Fused yaw exceeds requested curvature in a majority of usable samples.")
  elif phase_lag:
    primary, confidence = "dynamic_phase_lag_observed", "medium"
    evidence.append("Turn-in tracking lags steady tracking; this is phase evidence, not a unique delay estimate.")
  else:
    primary, confidence = "inconclusive", "low"

  if primary == "model_path_inside_detected_lane":
    delay_verdict = "not_supported_as_primary_for_a_persistent_ahead_path_offset"
  elif phase_lag:
    delay_verdict = "phase_lag_present_but_live_delay_not_isolated"
  else:
    delay_verdict = "not_isolated"
  if delay_varied:
    delay_verdict += "_and_applied_delay_varied"

  if vm_ratio is not None and not 0.85 <= vm_ratio <= 1.15:
    sr_verdict = "vehicle_model_mapping_mismatch_possible_sr_stiffness_and_roll_not_separated"
  elif strict_path_evidence:
    sr_verdict = "not_supported_as_primary_by_yaw_tracking_and_bilateral_inside_path_evidence"
  elif path_inside and yaw_tracks:
    sr_verdict = "inside_path_and_yaw_tracking_argue_against_sr_as_primary_but_do_not_isolate_it"
  else:
    sr_verdict = "not_isolated"

  p_share = overall.get("p_abs_share") or 0.0
  i_share = overall.get("i_abs_share") or 0.0
  f_share = overall.get("feedforward_abs_share") or 0.0
  dominant = max((("P", p_share), ("I", i_share), ("feedforward", f_share)), key=lambda item: item[1])
  pif = {
    "dominant_raw_logged_contribution": dominant[0],
    "dominant_raw_abs_share": dominant[1],
    "output_minus_raw_terms_aligned_median": overall.get("output_minus_raw_p_i_f_aligned_median"),
    "scope": overall.get("term_scope", "raw_logged_pid_terms"),
    "causal_interpretation": "raw_contribution_only_not_a_gain_causality_test_or_final_output_decomposition",
  }
  if actual_under_target and p_aligned is not None and p_aligned > 0.0:
    pif["tracking_evidence"] = "P_is_correcting_remaining_error_not_driving_angle_overshoot"

  return {
    "primary": primary,
    "confidence": confidence,
    "evidence": evidence,
    "model_path_source_ambiguity": "cannot_separate_planner_from_lane_perception_or_calibration_with_these_logs",
    "strict_matched_evidence": matched,
    "p_i_feedforward": pif,
    "live_delay": delay_verdict,
    "steer_ratio": sr_verdict,
    "causal_comparison": False,
    "causal_comparison_reason": (
      "mixed software/settings cohorts; no route-to-route deltas are interpreted" if mixed_cohorts
      else "observational route logs are not a road-matched, one-variable A/B test"
    ),
    "promotion_limitations": [reason for condition, reason in (
      (mixed_cohorts, "mixed_cohorts"),
      (delay_varied, "multiple_effective_delay_regimes"),
      (not matched["both_directions"], "bilateral_matched_evidence_missing"),
    ) if condition],
  }


def build_report(result: ScanResult, min_samples: int = 30,
                 speed_edges_mph: Sequence[float] = SPEED_EDGES_MPH,
                 angle_edges_deg: Sequence[float] = ANGLE_EDGES_DEG) -> dict:
  controls = [sample for sample in result.controls if not sample.saturated]
  valid_controls = [sample for sample in controls if sample.params_valid]
  primary_controls = valid_controls if len(valid_controls) >= max(min_samples, len(controls) // 2) else controls
  overall, bins = summarize_controls(primary_controls, min_samples, speed_edges_mph, angle_edges_deg)
  lanes = summarize_lanes(result.lanes, result.lane_attempts)
  delay = summarize_delay(result.delays)
  matched = strict_matched_evidence(primary_controls, result.lanes, result.lane_attempts, min_samples)
  cohorts = sorted({sample.cohort for sample in result.controls} | {sample.cohort for sample in result.lanes})
  contexts = []
  for cohort in cohorts:
    context = result.contexts.get(cohort)
    contexts.append({
      "cohort": cohort,
      "fingerprint": context.fingerprint if context else "UNKNOWN",
      "branch": context.branch if context else "unknown",
      "commit": context.commit if context else "unknown",
      "eps_firmware": context.eps_firmware if context else "unknown",
      "model_sr_policy": context.model_sr_policy.value if context else SteerRatioModelPolicy.UNKNOWN.value,
      "settings": context.settings if context else {},
      "configured_steer_ratio": finite_median(result.configured_steer_ratios[cohort]),
      "learned_steer_ratio_median": finite_median(result.learned_steer_ratios[cohort]),
      "configured_steer_actuator_delay_s": (
        context.steer_actuator_delay if context and math.isfinite(context.steer_actuator_delay) else None
      ),
    })
  report = {
    "schema_version": 1,
    "read_only": True,
    "observational_only": True,
    "input": {
      "files_read": result.files_read,
      "files_failed": result.files_failed,
      "routes": sorted({sample.route for sample in result.controls} | {sample.route for sample in result.lanes}),
      "cohorts": contexts,
      "errors": result.errors,
      "complete": not result.incomplete_sources and bool(primary_controls),
      "incomplete_sources": result.incomplete_sources,
    },
    "controller": {
      "active_hands_off_samples": len(result.controls),
      "non_saturated_samples": len(controls),
      "primary_params_valid_samples": len(valid_controls),
      "summary": overall,
      "speed_angle_phase_bins": bins,
    },
    "lane_placement": lanes,
    "strict_matched_evidence": matched,
    "live_delay": delay,
  }
  report["verdict"] = classify_attribution(overall, bins, lanes, delay, len(cohorts) > 1, matched)
  return report


def _fmt(value, digits: int = 3, suffix: str = "") -> str:
  return "n/a" if value is None else f"{value:.{digits}f}{suffix}"


def print_report(report: dict) -> None:
  input_data = report["input"]
  controller = report["controller"]
  overall = controller["summary"]
  print("\nLateral attribution (read-only, observational)")
  file_summary = f"{input_data['files_read']}/{input_data['files_failed']}"
  print(f"  files read/failed: {file_summary} | routes: {len(input_data['routes'])} | cohorts: {len(input_data['cohorts'])}")
  if not input_data["complete"]:
    print(f"  INCOMPLETE: missing required services or usable controller samples: {input_data['incomplete_sources']}")
  print(f"  controller samples: {controller['active_hands_off_samples']} active hands-off, {controller['non_saturated_samples']} non-saturated")

  delay = report["live_delay"]
  print("\nLive delay seen by controls")
  print(
    f"  effective: {_fmt(delay['effective_median_s'], 3, ' s')} median "
    + f"({_fmt(delay['effective_min_s'], 3)}-{_fmt(delay['effective_max_s'], 3)} s) | "
    + f"estimator: {_fmt(delay['estimate_median_s'], 3, ' s')}"
  )

  print("\nController tracking and logged term contribution")
  print(
    f"  fused yaw / desired curvature: {_fmt(overall.get('yaw_to_desired_median'))} median "
    + f"(p10-p90 {_fmt(overall.get('yaw_to_desired_p10'))}-{_fmt(overall.get('yaw_to_desired_p90'))})"
  )
  print(
    f"  actual / desired angle:       {_fmt(overall.get('actual_to_desired_angle_median'))} | "
    + f"aligned angle error {_fmt(overall.get('angle_error_aligned_median_deg'), 2, ' deg')}"
  )
  print(
    f"  raw P / I / feedforward:      {_fmt(overall.get('p_abs_share'), 2)} / {_fmt(overall.get('i_abs_share'), 2)} / "
    + f"{_fmt(overall.get('feedforward_abs_share'), 2)}"
  )
  print(f"  final output - raw P/I/F:     {_fmt(overall.get('output_minus_raw_p_i_f_aligned_median'))} aligned median")
  print("  note: raw PID terms precede NRDR scaling, center boost, damping, stiction, and learner overlays.")
  print(f"  fused yaw / vehicle model:    {_fmt(overall.get('vehicle_model_to_yaw_median'))} | yaw sign: {overall.get('yaw_sign_handling', 'n/a')}")

  print("\nConfidence-gated model path relative to lane center (+ = inside turn)")
  print(f"{'ahead':>7} {'accepted':>12} {'median':>10} {'p10-p90':>17} {'inside%':>9}")
  for row in report["lane_placement"]:
    inside_fraction = row["inside_fraction"]
    inside_text = "n/a" if inside_fraction is None else f"{100.0 * inside_fraction:.0f}%"
    print(
      f"{row['lookahead_m']:>5.0f} m {row['accepted_frames']:>5}/{row['attempted_frames']:<5} "
      + f"{_fmt(row['inside_offset_median_m'], 3, ' m'):>10} "
      + f"{(_fmt(row['inside_offset_p10_m'], 3) + ' to ' + _fmt(row['inside_offset_p90_m'], 3)):>17} {inside_text:>9}"
    )

  bins = controller["speed_angle_phase_bins"]
  if bins:
    print("\nSpeed / angle / phase bins")
    print(f"{'mph':>9} {'angle':>11} {'dir':>5} {'phase':>8} {'n':>6} {'yaw/des':>8} {'err deg':>8} {'raw P/I/F':>15}")
    for row in bins:
      speed = f"{row['speed_mph'][0]:g}-{row['speed_mph'][1]:g}"
      angle = f"{row['angle_deg'][0]:g}-{row['angle_deg'][1]:g}"
      shares = f"{_fmt(row['p_abs_share'], 2)}/{_fmt(row['i_abs_share'], 2)}/{_fmt(row['feedforward_abs_share'], 2)}"
      print(
        f"{speed:>9} {angle:>11} {row['direction']:>5} {row['phase']:>8} {row['samples']:>6} "
        + f"{_fmt(row['yaw_to_desired_median']):>8} {_fmt(row['angle_error_aligned_median_deg'], 2):>8} {shares:>15}"
      )

  verdict = report["verdict"]
  print("\nVerdict")
  print(f"  {verdict['primary']} ({verdict['confidence']} confidence)")
  print("  This cannot distinguish planning from lane-perception or calibration error.")
  for evidence in verdict["evidence"]:
    print(f"  - {evidence}")
  print(f"  raw P/I/FF: {verdict['p_i_feedforward'].get('tracking_evidence', verdict['p_i_feedforward']['causal_interpretation'])}")
  print(f"  live delay: {verdict['live_delay']}")
  print(f"  steer ratio: {verdict['steer_ratio']}")
  print(f"  causal guard: {verdict['causal_comparison_reason']}")


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument("sources", nargs="+", help="route identifiers, segment logs, directories, or globs")
  parser.add_argument("--log-kind", choices=("auto", "rlog", "qlog"), default="auto",
                      help="prefer rlog per segment and fall back to that segment's qlog (default: auto)")
  parser.add_argument("--json", metavar="PATH", help="also write the machine-readable report; use '-' for JSON-only stdout")
  parser.add_argument("--min-samples", type=int, default=30, help="minimum samples for a speed/angle/phase row (default: 30)")
  parser.add_argument("--min-speed-mph", type=float, default=5.0, help="minimum analyzed speed (default: 5 mph)")
  parser.add_argument("--min-angle-deg", type=float, default=3.0, help="minimum absolute desired angle (default: 3 deg)")
  parser.add_argument("--max-pair-age", type=float, default=0.25, help="maximum state/pose age in seconds (default: 0.25)")
  parser.add_argument("--speed-edges-mph", default=",".join(str(value) for value in SPEED_EDGES_MPH))
  parser.add_argument("--angle-edges-deg", default=",".join(str(value) for value in ANGLE_EDGES_DEG))
  parser.add_argument("--lookaheads-m", default=",".join(str(value) for value in DEFAULT_LOOKAHEADS_M))
  return parser


def main() -> int:
  parser = build_parser()
  args = parser.parse_args()
  if args.min_samples <= 0 or args.min_speed_mph < 0.0 or args.min_angle_deg < 0.0 or args.max_pair_age <= 0.0:
    parser.error("sample minimum and pairing age must be positive; speed and angle gates cannot be negative")
  speed_edges = parse_edges(args.speed_edges_mph, "--speed-edges-mph")
  angle_edges = parse_edges(args.angle_edges_deg, "--angle-edges-deg")
  lookaheads = parse_edges("0," + args.lookaheads_m, "--lookaheads-m")[1:]
  sources = expand_sources(args.sources, args.log_kind)
  if not sources:
    print("No matching logs found.", file=sys.stderr)
    return 1

  result = collect(sources, args.log_kind, args.min_speed_mph, args.min_angle_deg, args.max_pair_age, lookaheads)
  report = build_report(result, args.min_samples, speed_edges, angle_edges)
  encoded = json.dumps(report, indent=2, allow_nan=False)
  if args.json == "-":
    print(encoded)
  else:
    print_report(report)
    if args.json:
      Path(args.json).write_text(encoded + "\n", encoding="utf-8")
      print(f"\nWrote {args.json}")
  if not result.files_read:
    return 1
  return 2 if not report["input"]["complete"] else 0


if __name__ == "__main__":
  raise SystemExit(main())


__all__ = (
  "ANGLE_EDGES_DEG",
  "DEFAULT_LOOKAHEADS_M",
  "MAX_LANE_STD",
  "MAX_LANE_WIDTH_M",
  "MAX_PATH_STD",
  "MIN_CURVATURE",
  "MIN_LANE_PROB",
  "MIN_LANE_WIDTH_M",
  "MPS_TO_MPH",
  "RELEVANT_PARAMS",
  "REQUIRED_SERVICES",
  "SPEED_EDGES_MPH",
  "Context",
  "ControllerReading",
  "ControlSample",
  "DelaySample",
  "LaneSample",
  "ScanResult",
  "build_parser",
  "build_report",
  "classify_attribution",
  "collect",
  "decode_params",
  "expand_sources",
  "extract_controller_reading",
  "finite",
  "finite_median",
  "fraction",
  "infer_yaw_sign",
  "is_fresh",
  "lane_observation",
  "logged_steer_ratio_model_policy",
  "main",
  "param_bool",
  "parse_edges",
  "percentile",
  "print_report",
  "route_id",
  "sign",
  "strict_matched_evidence",
  "summarize_controls",
  "summarize_delay",
  "summarize_lanes",
)
