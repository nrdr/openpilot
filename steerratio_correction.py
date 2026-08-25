#!/usr/bin/env python3
"""Build route-balanced steer-ratio coverage and correction diagnostics from local rlogs."""

from __future__ import annotations

import argparse
from collections.abc import Iterable
from collections import Counter, defaultdict, deque
import csv
from dataclasses import asdict, dataclass, field, fields, replace
from datetime import datetime
import glob
import gzip
import json
import math
from pathlib import Path
import re
from statistics import median
import sys
import time

from openpilot.sunnypilot.nrdr.sr_correction_analysis import (
  BinKey,
  CommandSample,
  CenterBiasEstimate,
  CorrectionSample,
  GateConfig,
  MappingSample,
  VehicleSample,
  aggregate_mapping_bin,
  aggregate_bin,
  apply_center_bias,
  correction_factor,
  estimate_center_bias,
  make_bin_key,
  mapping_rejection_reason,
  model_effective_ratio,
  model_roll_compensation,
  nearest_sample,
  phase_from_steering,
  rejection_reason,
  stable_dwell_samples,
)


MPS_TO_MPH = 2.236936
SEGMENT_DIR_RE = re.compile(r"^(.*)--(\d+)$")
SETTINGS_KEYS = (
  "NrdrLearnSteerRatio",
  "NrdrLearnStiffness",
  "NrdrLearnAngleOffset",
  "NrdrLegacyDualBpSteerRatio",
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
  "NrdrCurvServo",
  "NrdrCurvatureTrim",
  "NrdrNnlcEnabled",
)
REJECTION_COLUMNS = (
  "stale state",
  "missing offset",
  "missing command",
  "missing car output",
  "unknown software revision",
  "steering safety limited",
  "invalid vehicle model",
  "lateral inactive",
  "steering saturated",
  "lane change",
  "driver steering",
  "invalid pose",
  "speed gate",
  "angle gate",
  "desired curvature gate",
  "yaw gate",
  "yaw uncertainty",
  "yaw-accel gate",
  "steering-rate gate",
  "longitudinal-accel gate",
  "road-roll gate",
  "curvature direction mismatch",
  "angle direction mismatch",
  "angle tracking gate",
  "correction bounds",
)


def finite(value, default: float = math.nan) -> float:
  try:
    value = float(value)
    return value if math.isfinite(value) else default
  except (TypeError, ValueError):
    return default


def route_segment(source: str) -> tuple[str, int]:
  match = SEGMENT_DIR_RE.match(Path(source).parent.name)
  return (match.group(1), int(match.group(2))) if match is not None else (Path(source).parent.name, -1)


def source_sort_key(source: str) -> tuple[str, int, str]:
  route, segment = route_segment(source)
  return route, segment, source


def expand_sources(raw_sources: list[str]) -> list[str]:
  sources = []
  for raw in raw_sources:
    matches = glob.glob(raw, recursive=True)
    for candidate in matches or [raw]:
      path = Path(candidate)
      if path.is_dir():
        sources.extend(str(item) for item in path.rglob("rlog.zst"))
      elif path.is_file():
        sources.append(str(path))
  return sorted(dict.fromkeys(sources), key=source_sort_key)


def iter_local_events(source: str):
  import zstandard as zstd
  from openpilot.cereal import log

  with open(source, "rb") as compressed:
    with zstd.ZstdDecompressor().stream_reader(compressed) as reader:
      data = reader.read()
  yield from log.Event.read_multiple_bytes(data)


def decode_param_map(entries) -> dict[str, str]:
  wanted = set(SETTINGS_KEYS)
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


def settings_signature(commit: str, branch: str, settings: dict[str, str]) -> str:
  revision = (commit or "unknown")[:12]
  values = ",".join(f"{key}={settings[key]}" for key in sorted(settings))
  return f"{branch or 'unknown'}@{revision}" + (f"|{values}" if values else "")


def setting_bool(context: RouteContext, key: str, default: bool) -> bool:
  value = context.settings.get(key)
  if value is None:
    return default
  return value.strip().lower() not in ("", "0", "false", "off", "no")


@dataclass
class RouteContext:
  fingerprint: str = "UNKNOWN"
  wheelbase_m: float = math.nan
  mass_kg: float = math.nan
  center_to_front_m: float = math.nan
  tire_stiffness_front: float = math.nan
  tire_stiffness_rear: float = math.nan
  default_delay_s: float = 0.30
  commit: str = "unknown"
  branch: str = "unknown"
  settings: dict[str, str] = field(default_factory=dict)
  eps_firmware: str = "unknown"

  @property
  def signature(self) -> str:
    return settings_signature(self.commit, self.branch, self.settings)


@dataclass
class ScanState:
  car_state_t: float | None = None
  speed_mps: float = math.nan
  accel_mps2: float = math.nan
  steering_angle_deg: float = math.nan
  steering_rate_deg_s: float = math.nan
  steering_torque: float = math.nan
  steering_pressed: bool = True
  forward_gear: bool = False
  gear_known: bool = False
  left_blinker: bool = False
  right_blinker: bool = False
  steer_fault: bool = False
  controls_t: float | None = None
  saturated: bool = False
  lane_change_active: bool = False
  live_params_t: float | None = None
  live_params_valid: bool = False
  offset_valid: bool = False
  average_offset_valid: bool = False
  stiffness_valid: bool = False
  angle_offset_deg: float = math.nan
  average_angle_offset_deg: float = math.nan
  road_roll_rad: float = math.nan
  stiffness_factor: float = math.nan
  lateral_delay_s: float | None = None


@dataclass(frozen=True)
class AppliedTorqueSample:
  timestamp: float
  torque: float


@dataclass
class ScanResult:
  samples: list[CorrectionSample] = field(default_factory=list)
  experimental_samples: list[CorrectionSample] = field(default_factory=list)
  manual_mapping_samples: list[MappingSample] = field(default_factory=list)
  next_manual_dwell_id: int = 0
  manual_center_bias: list[CenterBiasEstimate] = field(default_factory=list)
  manual_applied_bias: dict[str, tuple[float, str]] = field(default_factory=dict)
  stage_seconds: defaultdict[tuple[str, float, str], set[tuple[str, int]]] = field(
    default_factory=lambda: defaultdict(set),
  )
  rejection_seconds: defaultdict[tuple[str, float, str], set[tuple[str, int]]] = field(
    default_factory=lambda: defaultdict(set),
  )
  rejected_frames: Counter[tuple[str, float, str]] = field(default_factory=Counter)
  manual_rejection_seconds: defaultdict[tuple[str, float, str], set[tuple[str, int]]] = field(
    default_factory=lambda: defaultdict(set),
  )
  manual_rejected_frames: Counter[tuple[str, float, str]] = field(default_factory=Counter)
  files_read: int = 0
  files_failed: int = 0
  routes: set[str] = field(default_factory=set)
  fingerprints: set[str] = field(default_factory=set)
  signatures: set[str] = field(default_factory=set)


def angle_bin(angle_deg: float, width: float) -> float:
  return math.floor(abs(angle_deg) / width) * width


def add_stage(result: ScanResult, fingerprint: str, angle_start: float, stage: str,
              route: str, timestamp: float) -> None:
  result.stage_seconds[(fingerprint, angle_start, stage)].add((route, math.floor(timestamp)))


def add_rejection(result: ScanResult, fingerprint: str, angle_start: float, reason: str,
                  route: str, timestamp: float) -> None:
  result.rejected_frames[(fingerprint, angle_start, reason)] += 1
  result.rejection_seconds[(fingerprint, angle_start, reason)].add((route, math.floor(timestamp)))


def add_manual_rejection(result: ScanResult, fingerprint: str, angle_start: float, reason: str,
                         route: str, timestamp: float) -> None:
  result.manual_rejected_frames[(fingerprint, angle_start, reason)] += 1
  result.manual_rejection_seconds[(fingerprint, angle_start, reason)].add((route, math.floor(timestamp)))


def geometry_valid(context: RouteContext) -> bool:
  values = (
    context.wheelbase_m, context.mass_kg, context.center_to_front_m,
    context.tire_stiffness_front, context.tire_stiffness_rear,
  )
  return bool(
    all(math.isfinite(value) for value in values)
    and context.wheelbase_m > 0.0
    and context.mass_kg > 0.0
    and 0.0 < context.center_to_front_m < context.wheelbase_m
    and context.tire_stiffness_front > 0.0
    and context.tire_stiffness_rear > 0.0
  )


def extract_saturation(controls_state) -> bool:
  try:
    lateral = controls_state.lateralControlState
    return bool(getattr(lateral, lateral.which()).saturated)
  except Exception:
    return False


def update_car_params(context: RouteContext, car_params) -> None:
  context.fingerprint = str(car_params.carFingerprint)
  context.wheelbase_m = finite(car_params.wheelbase)
  context.mass_kg = finite(car_params.mass)
  context.center_to_front_m = finite(car_params.centerToFront)
  context.tire_stiffness_front = finite(car_params.tireStiffnessFront)
  context.tire_stiffness_rear = finite(car_params.tireStiffnessRear)
  context.default_delay_s = finite(car_params.steerActuatorDelay, 0.10) + 0.20
  firmware = []
  for item in car_params.carFw:
    if str(item.ecu) == "eps":
      try:
        firmware.append(bytes(item.fwVersion).split(b"\0", 1)[0].decode("ascii", errors="replace").replace(",", "-"))
      except Exception:
        pass
  context.eps_firmware = ",".join(firmware) or "unknown"


def openpilot_roll_curvature(context: RouteContext, vehicle: VehicleSample) -> float | None:
  steering_roll = model_roll_compensation(
    vehicle.speed_mps,
    vehicle.road_roll_rad,
    vehicle.stiffness_factor,
    context.wheelbase_m,
    context.mass_kg,
    context.center_to_front_m,
    context.tire_stiffness_front,
    context.tire_stiffness_rear,
  )
  return -steering_roll if steering_roll is not None else None


def command_response_factor(context: RouteContext, command: CommandSample, vehicle: VehicleSample) -> float | None:
  openpilot_roll = openpilot_roll_curvature(context, vehicle)
  if openpilot_roll is None:
    return None
  return correction_factor(
    command.desired_curvature,
    vehicle.yaw_rate_rad_s / vehicle.speed_mps,
    command.desired_angle_deg - command.angle_offset_deg,
    vehicle.actual_angle_deg - vehicle.angle_offset_deg,
    curvature_offset=openpilot_roll,
  )


def make_sample(route: str, context: RouteContext, command: CommandSample, vehicle: VehicleSample,
                quality: str, command_output_available: bool = True,
                safety_limited: bool = False,
                mapping_vehicle: VehicleSample | None = None) -> CorrectionSample | None:
  desired_angle = command.desired_angle_deg - command.angle_offset_deg
  actual_angle = vehicle.actual_angle_deg - vehicle.angle_offset_deg
  physical_vehicle = mapping_vehicle if mapping_vehicle is not None else vehicle
  geometry_offset = (physical_vehicle.angle_offset_deg if physical_vehicle.geometry_angle_offset_deg is None
                     else physical_vehicle.geometry_angle_offset_deg)
  physical_angle = physical_vehicle.actual_angle_deg - geometry_offset
  achieved_curvature = vehicle.yaw_rate_rad_s / vehicle.speed_mps
  openpilot_roll = openpilot_roll_curvature(context, vehicle)
  if openpilot_roll is None:
    return None
  factor = command_response_factor(context, command, vehicle)
  if factor is None:
    return None
  required_angle = abs(
    actual_angle * (command.desired_curvature - openpilot_roll) / (achieved_curvature - openpilot_roll)
  )
  effective_ratio = model_effective_ratio(
    physical_angle,
    physical_vehicle.yaw_rate_rad_s,
    physical_vehicle.speed_mps,
    physical_vehicle.road_roll_rad,
    physical_vehicle.stiffness_factor,
    context.wheelbase_m,
    context.mass_kg,
    context.center_to_front_m,
    context.tire_stiffness_front,
    context.tire_stiffness_rear,
  )
  return CorrectionSample(
    route_id=route,
    timestamp=vehicle.timestamp,
    speed_mps=vehicle.speed_mps,
    angle_deg=abs(physical_angle),
    direction="left" if command.desired_curvature > 0.0 else "right",
    phase=phase_from_steering(desired_angle, vehicle.steering_rate_deg_s),
    desired_curvature=command.desired_curvature,
    achieved_curvature=achieved_curvature,
    desired_angle_deg=desired_angle,
    actual_angle_deg=actual_angle,
    correction_factor=factor,
    tracking_ratio=abs(actual_angle / desired_angle),
    required_angle_deg=required_angle,
    effective_ratio=effective_ratio if effective_ratio is not None else math.nan,
    software_id=context.signature,
    quality=quality,
    fingerprint=context.fingerprint,
    command_output_available=command_output_available,
    safety_limited=safety_limited,
  )


def finalize_manual_mapping(result: ScanResult) -> None:
  by_route: defaultdict[str, list[MappingSample]] = defaultdict(list)
  for sample in result.manual_mapping_samples:
    by_route[sample.route_id].append(sample)

  estimates = []
  for route_samples in by_route.values():
    estimate = estimate_center_bias(route_samples)
    if estimate is not None:
      estimates.append(estimate)
  result.manual_center_bias = sorted(estimates, key=lambda estimate: estimate.route_id)

  estimates_by_route = {estimate.route_id: estimate for estimate in estimates}
  adjusted = []
  for route_id, route_samples in by_route.items():
    estimate = estimates_by_route.get(route_id)
    if estimate is not None and estimate.confidence in ("high", "medium"):
      applied_bias, source = estimate.bias_deg, "route-fit"
    else:
      applied_bias, source = 0.0, "none"
    result.manual_applied_bias[route_id] = (applied_bias, source)
    adjusted.extend(apply_center_bias(route_samples, applied_bias, source))
  result.manual_mapping_samples = adjusted


def scan_sources(sources: list[str], angle_width_deg: float, delay_override: float | None,
                 pair_age_s: float, progress_every: int) -> ScanResult:
  from openpilot.cereal import log
  from openpilot.selfdrive.locationd.helpers import Pose, PoseCalibrator

  relaxed_config = GateConfig()
  experimental_config = GateConfig(
    min_speed_mps=2.0,
    max_speed_mps=15.0,
    min_angle_deg=20.0,
    min_curvature=5e-5,
    min_yaw_rate_rad_s=0.005,
    max_yaw_rate_std_rad_s=0.10,
    max_yaw_accel_rad_s2=5.0,
    max_steering_rate_deg_s=120.0,
    max_longitudinal_accel_mps2=3.0,
    max_road_roll_rad=0.12,
    min_tracking_ratio=0.40,
    max_tracking_ratio=1.60,
    min_correction_factor=0.25,
    max_correction_factor=4.0,
  )
  result = ScanResult()
  route_contexts: dict[str, RouteContext] = {}
  started = time.monotonic()

  for source_index, source in enumerate(sources, start=1):
    route, _segment = route_segment(source)
    context = route_contexts.setdefault(route, RouteContext())
    state = ScanState()
    calibrator = PoseCalibrator()
    command_history: deque[CommandSample] = deque(maxlen=1000)
    output_history: deque[AppliedTorqueSample] = deque(maxlen=1000)
    manual_candidates: list[MappingSample] = []
    strict_since: float | None = None
    previous_pose_t: float | None = None
    previous_yaw_rate = 0.0
    result.routes.add(route)

    try:
      for event in iter_local_events(source):
        which = event.which()
        timestamp = float(event.logMonoTime) * 1e-9

        if which == "initData":
          init = event.initData
          context.commit = str(init.gitSrcCommit or init.gitCommit or context.commit)
          context.branch = str(init.gitBranch or context.branch)
          context.settings.update(decode_param_map(init.params.entries))

        elif which == "carParams":
          update_car_params(context, event.carParams)
          result.fingerprints.add(context.fingerprint)

        elif which == "extrinsicsCalibration":
          calibrator.feed_extrinsics_calibration(event.extrinsicsCalibration)

        elif which == "vehicleParameters":
          lp = event.vehicleParameters
          state.live_params_t = timestamp
          state.live_params_valid = bool(event.valid and lp.valid)
          state.offset_valid = bool(lp.angleOffsetValid)
          state.average_offset_valid = bool(lp.angleOffsetAverageValid)
          state.stiffness_valid = bool(lp.stiffnessFactorValid)
          state.angle_offset_deg = finite(lp.angleOffsetDeg)
          state.average_angle_offset_deg = finite(lp.angleOffsetAverageDeg)
          state.road_roll_rad = finite(lp.roll)
          state.stiffness_factor = finite(lp.stiffnessFactor)

        elif which == "lateralDelay":
          state.lateral_delay_s = finite(event.lateralDelay.lateralDelay, context.default_delay_s)

        elif which == "modelV2":
          state.lane_change_active = event.modelV2.meta.laneChangeState != log.LaneChangeState.off

        elif which == "carState":
          car_state = event.carState
          state.car_state_t = timestamp
          state.speed_mps = finite(car_state.vEgo)
          state.accel_mps2 = finite(car_state.aEgo)
          state.steering_angle_deg = finite(car_state.steeringAngleDeg)
          state.steering_rate_deg_s = finite(car_state.steeringRateDeg)
          state.steering_torque = finite(car_state.steeringTorque)
          state.steering_pressed = bool(car_state.steeringPressed)
          gear = str(car_state.gearShifter)
          state.gear_known = gear != "unknown"
          state.forward_gear = gear in ("drive", "sport", "low", "brake", "eco", "manumatic")
          state.left_blinker = bool(car_state.leftBlinker)
          state.right_blinker = bool(car_state.rightBlinker)
          state.steer_fault = bool(car_state.steerFaultTemporary or car_state.steerFaultPermanent)

        elif which == "controlsState":
          state.controls_t = timestamp
          state.saturated = extract_saturation(event.controlsState)

        elif which == "carControl":
          control = event.carControl
          desired_curvature = finite(control.actuators.curvature)
          desired_angle = finite(control.actuators.steeringAngleDeg)
          applied_offset = state.angle_offset_deg if setting_bool(context, "NrdrLearnAngleOffset", True) else 0.0
          if math.isfinite(desired_curvature) and math.isfinite(desired_angle):
            command_history.append(CommandSample(
              timestamp=timestamp,
              desired_curvature=desired_curvature,
              desired_angle_deg=desired_angle,
              angle_offset_deg=applied_offset,
              lat_active=bool(control.latActive),
              saturated=state.saturated,
              lane_change_active=bool(state.lane_change_active or state.left_blinker or state.right_blinker),
              requested_torque=finite(control.actuators.torque),
            ))

        elif which == "carOutput":
          output_history.append(AppliedTorqueSample(
            timestamp=timestamp,
            torque=finite(event.carOutput.actuatorsOutput.torque),
          ))

        elif which == "deviceMotion":
          if context.fingerprint == "UNKNOWN":
            strict_since = None
            continue
          device_motion = event.deviceMotion
          raw_pose = Pose.from_device_motion(device_motion)
          calibrated_pose = calibrator.build_calibrated_pose(raw_pose)
          yaw_rate = finite(calibrated_pose.angular_velocity.z)
          yaw_std = finite(calibrated_pose.angular_velocity.z_std)
          pose_velocity = getattr(calibrated_pose, "velocity", None)
          pose_forward = finite(getattr(pose_velocity, "x", math.nan)) > 0.5
          yaw_accel = 0.0
          pose_dt = timestamp - previous_pose_t if previous_pose_t is not None else math.nan
          if math.isfinite(pose_dt) and pose_dt > 0.15:
            strict_since = None
          if math.isfinite(pose_dt) and 0.01 <= pose_dt <= 0.20:
            yaw_accel = (yaw_rate - previous_yaw_rate) / pose_dt
          previous_pose_t = timestamp
          previous_yaw_rate = yaw_rate

          pose_valid = bool(
            calibrator.calib_valid
            and device_motion.inputsOK
            and device_motion.posenetOK
            and device_motion.sensorsOK
            and device_motion.angularVelocityDevice.valid
          )
          raw_angle = state.steering_angle_deg
          learn_offset = setting_bool(context, "NrdrLearnAngleOffset", True)
          learn_stiffness = setting_bool(context, "NrdrLearnStiffness", True)
          applied_offset = state.angle_offset_deg if learn_offset and state.offset_valid else 0.0
          controller_geometry_offset_valid = state.average_offset_valid if learn_offset else True
          controller_geometry_offset = state.average_angle_offset_deg if learn_offset and state.average_offset_valid else 0.0
          controller_stiffness_valid = state.stiffness_valid if learn_stiffness else True
          controller_stiffness = state.stiffness_factor if learn_stiffness and state.stiffness_valid else 1.0
          controller_angle = raw_angle - controller_geometry_offset
          mapping_geometry_offset = state.average_angle_offset_deg
          mapping_stiffness = state.stiffness_factor
          mapping_angle = raw_angle - mapping_geometry_offset
          stage_angle = mapping_angle if math.isfinite(mapping_angle) else raw_angle
          start = angle_bin(stage_angle if math.isfinite(stage_angle) else 0.0, angle_width_deg)
          fingerprint = context.fingerprint
          if pose_valid:
            add_stage(result, fingerprint, start, "raw_pose_valid", route, timestamp)

          current_command = command_history[-1] if command_history else None
          if current_command is not None and current_command.lat_active:
            add_stage(result, fingerprint, start, "lat_active", route, timestamp)
          if current_command is not None and current_command.lat_active and not state.steering_pressed:
            add_stage(result, fingerprint, start, "no_driver", route, timestamp)

          if state.car_state_t is None or timestamp - state.car_state_t > 0.10:
            add_rejection(result, fingerprint, start, "stale state", route, timestamp)
            add_manual_rejection(result, fingerprint, start, "stale state", route, timestamp)
            strict_since = None
            continue
          mapping_vehicle: VehicleSample | None = None
          mapping_params_valid = bool(
            state.live_params_valid
            and state.average_offset_valid
            and state.stiffness_valid
            and state.live_params_t is not None
            and timestamp - state.live_params_t <= 0.50
            and math.isfinite(mapping_geometry_offset)
            and math.isfinite(mapping_stiffness)
          )
          if not mapping_params_valid:
            add_manual_rejection(result, fingerprint, start, "invalid live parameters", route, timestamp)
          else:
            mapping_vehicle = VehicleSample(
              timestamp=timestamp,
              speed_mps=state.speed_mps,
              actual_angle_deg=state.steering_angle_deg,
              steering_rate_deg_s=state.steering_rate_deg_s,
              steering_pressed=state.steering_pressed,
              yaw_rate_rad_s=yaw_rate,
              yaw_rate_std_rad_s=yaw_std,
              yaw_accel_rad_s2=yaw_accel,
              longitudinal_accel_mps2=state.accel_mps2,
              road_roll_rad=state.road_roll_rad,
              stiffness_factor=mapping_stiffness,
              pose_valid=pose_valid and not state.steer_fault,
              geometry_angle_offset_deg=mapping_geometry_offset,
              steering_torque=state.steering_torque,
              forward_gear=state.forward_gear if state.gear_known else pose_forward,
            )
            mapping_ratio = model_effective_ratio(
              mapping_angle,
              yaw_rate,
              state.speed_mps,
              state.road_roll_rad,
              mapping_stiffness,
              context.wheelbase_m,
              context.mass_kg,
              context.center_to_front_m,
              context.tire_stiffness_front,
              context.tire_stiffness_rear,
            )
            mapping_reason = mapping_rejection_reason(
              mapping_vehicle,
              mapping_ratio,
              geometry_valid=geometry_valid(context),
              average_offset_valid=state.average_offset_valid,
              stiffness_valid=state.stiffness_valid,
            )
            if mapping_reason is None and mapping_ratio is not None:
              zero_roll_ratio = model_effective_ratio(
                mapping_angle, yaw_rate, state.speed_mps, 0.0, mapping_stiffness,
                context.wheelbase_m, context.mass_kg, context.center_to_front_m,
                context.tire_stiffness_front, context.tire_stiffness_rear,
              )
              unit_stiffness_ratio = model_effective_ratio(
                mapping_angle, yaw_rate, state.speed_mps, state.road_roll_rad, 1.0,
                context.wheelbase_m, context.mass_kg, context.center_to_front_m,
                context.tire_stiffness_front, context.tire_stiffness_rear,
              )
              manual_candidates.append(MappingSample(
                route_id=route,
                timestamp=timestamp,
                speed_mps=state.speed_mps,
                signed_angle_deg=mapping_angle,
                direction="left" if mapping_angle < 0.0 else "right",
                effective_ratio=mapping_ratio,
                ratio_per_degree=mapping_ratio / abs(mapping_angle),
                steering_torque=state.steering_torque,
                fingerprint=fingerprint,
                steering_rate_deg_s=state.steering_rate_deg_s,
                yaw_rate_rad_s=yaw_rate,
                yaw_rate_std_rad_s=yaw_std,
                road_roll_rad=state.road_roll_rad,
                stiffness_factor=mapping_stiffness,
                longitudinal_accel_mps2=state.accel_mps2,
                lateral_accel_mps2=yaw_rate * state.speed_mps,
                zero_roll_effective_ratio=zero_roll_ratio if zero_roll_ratio is not None else math.nan,
                unit_stiffness_effective_ratio=(
                  unit_stiffness_ratio if unit_stiffness_ratio is not None else math.nan
                ),
              ))
            else:
              add_manual_rejection(
                result, fingerprint, start, mapping_reason or "invalid vehicle model", route, timestamp,
              )

          if context.commit == "unknown":
            add_rejection(result, fingerprint, start, "unknown software revision", route, timestamp)
            strict_since = None
            continue

          command_params_valid = bool(
            state.live_params_valid
            and controller_geometry_offset_valid
            and controller_stiffness_valid
            and (not learn_offset or state.offset_valid)
            and state.live_params_t is not None
            and timestamp - state.live_params_t <= 0.50
            and math.isfinite(controller_geometry_offset)
            and math.isfinite(controller_stiffness)
          )
          if not command_params_valid:
            add_rejection(result, fingerprint, start, "missing offset", route, timestamp)
            strict_since = None
            continue

          controller_vehicle = VehicleSample(
            timestamp=timestamp,
            speed_mps=state.speed_mps,
            actual_angle_deg=state.steering_angle_deg,
            steering_rate_deg_s=state.steering_rate_deg_s,
            steering_pressed=state.steering_pressed,
            yaw_rate_rad_s=yaw_rate,
            yaw_rate_std_rad_s=yaw_std,
            yaw_accel_rad_s2=yaw_accel,
            longitudinal_accel_mps2=state.accel_mps2,
            road_roll_rad=state.road_roll_rad,
            stiffness_factor=controller_stiffness,
            pose_valid=pose_valid and not state.steer_fault,
            angle_offset_deg=applied_offset,
            geometry_angle_offset_deg=controller_geometry_offset,
            steering_torque=state.steering_torque,
            forward_gear=state.forward_gear,
          )

          delay = delay_override if delay_override is not None else (
            state.lateral_delay_s if state.lateral_delay_s is not None else context.default_delay_s
          )
          command = nearest_sample(command_history, timestamp - delay, pair_age_s)
          if command is None:
            add_rejection(result, fingerprint, start, "missing command", route, timestamp)
            strict_since = None
            continue
          applied_output = nearest_sample(output_history, command.timestamp, 0.05)
          output_available = bool(
            applied_output is not None
            and math.isfinite(command.requested_torque)
            and math.isfinite(applied_output.torque)
          )
          safety_limited = bool(
            output_available and abs(applied_output.torque - command.requested_torque) > 0.01
          )
          if not output_available:
            add_rejection(result, fingerprint, start, "missing car output", route, timestamp)
          elif safety_limited:
            add_rejection(result, fingerprint, start, "steering safety limited", route, timestamp)
          else:
            add_stage(result, fingerprint, start, "command_response_usable", route, timestamp)

          vehicle = controller_vehicle
          curvature_offset = openpilot_roll_curvature(context, vehicle)
          if curvature_offset is None:
            add_rejection(result, fingerprint, start, "invalid vehicle model", route, timestamp)
            strict_since = None
            continue
          reason = rejection_reason(command, vehicle, relaxed_config, curvature_offset)
          if reason is None:
            phase = phase_from_steering(
              command.desired_angle_deg - command.angle_offset_deg,
              vehicle.steering_rate_deg_s,
            )
            instant_strict = (
              phase == "steady"
              and abs(vehicle.longitudinal_accel_mps2) <= 0.50
              and abs(vehicle.yaw_accel_rad_s2) <= 0.03
            )
            if instant_strict:
              strict_since = timestamp if strict_since is None else strict_since
            else:
              strict_since = None
            quality = "strict" if strict_since is not None and timestamp - strict_since >= 0.50 else "relaxed"
            sample = make_sample(
              route, context, command, vehicle, quality,
              command_output_available=output_available,
              safety_limited=safety_limited,
              mapping_vehicle=mapping_vehicle,
            )
            if sample is not None:
              result.samples.append(sample)
              add_stage(result, fingerprint, start, "relaxed_usable", route, timestamp)
              if quality == "strict":
                add_stage(result, fingerprint, start, "strict_usable", route, timestamp)
          else:
            add_rejection(result, fingerprint, start, reason, route, timestamp)
            strict_since = None

          if (abs(controller_angle) >= 20.0
              and rejection_reason(command, vehicle, experimental_config, curvature_offset) is None):
            experimental = make_sample(
              route, context, command, vehicle, "experimental-transient",
              command_output_available=output_available,
              safety_limited=safety_limited,
              mapping_vehicle=mapping_vehicle,
            )
            if experimental is not None and experimental.phase != "steady":
              minus_command = nearest_sample(command_history, timestamp - max(0.0, delay - 0.10), pair_age_s)
              plus_command = nearest_sample(command_history, timestamp - delay - 0.10, pair_age_s)
              minus_factor = command_response_factor(context, minus_command, vehicle) if minus_command is not None else None
              plus_factor = command_response_factor(context, plus_command, vehicle) if plus_command is not None else None
              result.experimental_samples.append(replace(
                experimental,
                factor_delay_minus_100ms=minus_factor if minus_factor is not None else math.nan,
                factor_delay_plus_100ms=plus_factor if plus_factor is not None else math.nan,
              ))

      dwell_samples = stable_dwell_samples(manual_candidates)
      if dwell_samples:
        local_dwell_count = max(sample.dwell_id for sample in dwell_samples) + 1
        dwell_samples = [
          replace(sample, dwell_id=sample.dwell_id + result.next_manual_dwell_id)
          for sample in dwell_samples
        ]
        result.next_manual_dwell_id += local_dwell_count
      accepted = {(sample.timestamp, sample.direction) for sample in dwell_samples}
      for sample in manual_candidates:
        if (sample.timestamp, sample.direction) not in accepted:
          add_manual_rejection(
            result, sample.fingerprint, angle_bin(sample.signed_angle_deg, angle_width_deg),
            "dwell gate", route, sample.timestamp,
          )
      result.manual_mapping_samples.extend(dwell_samples)
      result.files_read += 1
      result.signatures.add(context.signature)
    except Exception as exc:
      result.files_failed += 1
      print(f"!! {source}: {exc}", file=sys.stderr, flush=True)

    if source_index == len(sources) or source_index % progress_every == 0:
      elapsed = time.monotonic() - started
      rate = source_index / elapsed if elapsed else 0.0
      eta = (len(sources) - source_index) / rate if rate else 0.0
      print(
        "".join((
          f"Progress {source_index}/{len(sources)} ({100.0 * source_index / len(sources):.1f}%) | ",
          f"accepted {len(result.samples)} + manual {len(result.manual_mapping_samples)} ",
          f"+ experimental {len(result.experimental_samples)} | ",
          f"elapsed {elapsed / 60.0:.1f} min | ETA {eta / 60.0:.1f} min",
        )),
        file=sys.stderr,
        flush=True,
      )

  finalize_manual_mapping(result)
  return result


def percentile(values: list[float], q: float) -> float:
  values = sorted(value for value in values if math.isfinite(value))
  if not values:
    return math.nan
  position = (len(values) - 1) * q / 100.0
  lower, upper = math.floor(position), math.ceil(position)
  if lower == upper:
    return values[lower]
  weight = position - lower
  return values[lower] * (1.0 - weight) + values[upper] * weight


def route_balanced_metric(samples: Iterable[CorrectionSample], attribute: str) -> tuple[float, float, float]:
  by_route_direction: defaultdict[tuple[str, str], list[float]] = defaultdict(list)
  for sample in samples:
    value = finite(getattr(sample, attribute))
    if math.isfinite(value):
      by_route_direction[(sample.route_id, sample.direction)].append(value)
  medians = [percentile(values, 50.0) for values in by_route_direction.values()]
  return percentile(medians, 50.0), percentile(medians, 25.0), percentile(medians, 75.0)


def supported_speed_strata(samples: list[CorrectionSample], attribute: str) -> list[float]:
  groups: defaultdict[tuple[float, float], list[CorrectionSample]] = defaultdict(list)
  for sample in samples:
    key = make_bin_key(sample).speed_start_mps, make_bin_key(sample).speed_end_mps
    groups[key].append(sample)

  medians = []
  for group in groups.values():
    seconds = {(sample.route_id, math.floor(sample.timestamp)) for sample in group}
    routes = {sample.route_id for sample in group}
    left_seconds = {(sample.route_id, math.floor(sample.timestamp)) for sample in group if sample.direction == "left"}
    right_seconds = {(sample.route_id, math.floor(sample.timestamp)) for sample in group if sample.direction == "right"}
    if len(seconds) < 10 or len(routes) < 2 or min(len(left_seconds), len(right_seconds)) < 3:
      continue
    value, _p25, _p75 = route_balanced_metric(group, attribute)
    if math.isfinite(value):
      medians.append(value)
  return medians


def mapping_confidence(seconds: int, routes: int, left_seconds: int, right_seconds: int,
                       median_value: float, p25_value: float, p75_value: float,
                       speed_strata: list[float]) -> str:
  relative_iqr = (p75_value - p25_value) / abs(median_value) if median_value else math.inf
  speed_spread = ((max(speed_strata) - min(speed_strata)) / abs(median(speed_strata))
                  if len(speed_strata) >= 2 and median(speed_strata) else math.inf)
  if speed_spread > 0.05:
    return "low"
  if (seconds >= 60 and routes >= 5 and min(left_seconds, right_seconds) >= 20
      and relative_iqr <= 0.08 and len(speed_strata) >= 2):
    return "high"
  if seconds >= 20 and routes >= 3 and min(left_seconds, right_seconds) >= 5 and relative_iqr <= 0.15:
    return "medium"
  return "low"


def write_samples(path: Path, samples: list[CorrectionSample]) -> None:
  if not samples:
    with gzip.open(path, "wt", encoding="utf-8"):
      pass
    return
  with gzip.open(path, "wt", newline="", encoding="utf-8", compresslevel=1) as stream:
    writer = csv.DictWriter(stream, fieldnames=list(asdict(samples[0])))
    writer.writeheader()
    for sample in samples:
      writer.writerow(asdict(sample))


def write_manual_mapping_samples(path: Path, samples: list[MappingSample]) -> None:
  fieldnames = [item.name for item in fields(MappingSample)]
  with gzip.open(path, "wt", newline="", encoding="utf-8", compresslevel=1) as stream:
    writer = csv.DictWriter(stream, fieldnames=fieldnames)
    writer.writeheader()
    for sample in samples:
      writer.writerow(asdict(sample))


def manual_supported_speed_strata(samples: list[MappingSample]) -> list[float]:
  edges = (2.0, 5.0, 8.0, 12.0, 15.000001)
  groups: defaultdict[tuple[float, float], list[MappingSample]] = defaultdict(list)
  for sample in samples:
    for lower, upper in zip(edges, edges[1:], strict=True):
      if lower <= sample.speed_mps < upper:
        groups[(lower, upper)].append(sample)
        break

  medians = []
  for group in groups.values():
    stats = aggregate_mapping_bin(group)
    if (stats is not None and stats.seconds >= 10 and stats.routes >= 2
        and min(stats.left_seconds, stats.right_seconds) >= 3):
      medians.append(stats.median_ratio)
  return medians


def mapping_variant_stats(samples: list[MappingSample], attribute: str):
  adjusted = []
  for sample in samples:
    value = finite(getattr(sample, attribute))
    if math.isfinite(value) and abs(sample.signed_angle_deg) > 1e-6:
      value *= abs(sample.bias_corrected_angle_deg) / abs(sample.signed_angle_deg)
      adjusted.append(replace(sample, bias_corrected_effective_ratio=value))
  return aggregate_mapping_bin(adjusted)


def write_manual_mapping(path: Path, samples: list[MappingSample], angle_width: float) -> list[dict]:
  groups: defaultdict[tuple[str, float], list[MappingSample]] = defaultdict(list)
  for sample in samples:
    groups[(sample.fingerprint, angle_bin(sample.bias_corrected_angle_deg, angle_width))].append(sample)

  rows = []
  for (fingerprint, start), group in sorted(groups.items()):
    stats = aggregate_mapping_bin(group)
    if stats is None:
      continue
    speed_strata = manual_supported_speed_strata(group)
    speed_spread = ((max(speed_strata) - min(speed_strata)) / abs(median(speed_strata))
                    if len(speed_strata) >= 2 and median(speed_strata) else math.nan)
    confidence = stats.confidence
    warnings = []
    if not math.isfinite(stats.bilateral_gap_percent) or stats.bilateral_gap_percent > 5.0:
      confidence = "low"
      warnings.append("left/right disagreement")
    if len(speed_strata) < 2:
      confidence = "low"
      warnings.append("fewer than two supported speed strata")
    elif speed_spread > 0.05:
      confidence = "low"
      warnings.append("speed-strata disagreement")

    torque_values = [abs(sample.steering_torque) for sample in group if math.isfinite(sample.steering_torque)]
    torque_p25 = percentile(torque_values, 25.0)
    torque_p75 = percentile(torque_values, 75.0)
    low_torque = [sample for sample in group if math.isfinite(sample.steering_torque)
                  and abs(sample.steering_torque) <= torque_p25]
    high_torque = [sample for sample in group if math.isfinite(sample.steering_torque)
                   and abs(sample.steering_torque) >= torque_p75]
    low_torque_stats = aggregate_mapping_bin(low_torque)
    high_torque_stats = aggregate_mapping_bin(high_torque)
    torque_spread = (
      100.0 * abs(high_torque_stats.median_ratio - low_torque_stats.median_ratio) / stats.median_ratio
      if low_torque_stats is not None and high_torque_stats is not None and stats.median_ratio else math.nan
    )
    if math.isfinite(torque_spread) and torque_spread > 5.0:
      confidence = "low"
      warnings.append("driver-torque quartiles disagree")
    zero_roll_stats = mapping_variant_stats(group, "zero_roll_effective_ratio")
    unit_stiffness_stats = mapping_variant_stats(group, "unit_stiffness_effective_ratio")
    zero_roll_delta = (
      100.0 * (zero_roll_stats.median_ratio / stats.median_ratio - 1.0)
      if zero_roll_stats is not None and stats.median_ratio else math.nan
    )
    unit_stiffness_delta = (
      100.0 * (unit_stiffness_stats.median_ratio / stats.median_ratio - 1.0)
      if unit_stiffness_stats is not None and stats.median_ratio else math.nan
    )
    model_sensitivity = max(
      (abs(value) for value in (zero_roll_delta, unit_stiffness_delta) if math.isfinite(value)),
      default=math.nan,
    )
    if math.isfinite(model_sensitivity) and model_sensitivity > 5.0:
      confidence = "low"
      warnings.append("roll/stiffness model sensitivity exceeds 5%")
    rows.append({
      "fingerprint": fingerprint,
      "angle_start_deg": start,
      "angle_end_deg": start + angle_width,
      "unique_seconds": stats.seconds,
      "routes": stats.routes,
      "route_directions": stats.route_directions,
      "paired_routes": stats.paired_routes,
      "left_seconds": stats.left_seconds,
      "right_seconds": stats.right_seconds,
      "mapping_effective_ratio": stats.median_ratio,
      "ratio_p25": stats.p25_ratio,
      "ratio_p75": stats.p75_ratio,
      "left_effective_ratio": stats.left_median_ratio,
      "right_effective_ratio": stats.right_median_ratio,
      "bilateral_gap_percent": stats.bilateral_gap_percent,
      "supported_speed_strata": len(speed_strata),
      "speed_strata_spread_percent": 100.0 * speed_spread,
      "torque_quartile_spread_percent": torque_spread,
      "zero_roll_delta_percent": zero_roll_delta,
      "unit_stiffness_delta_percent": unit_stiffness_delta,
      "model_sensitivity_percent": model_sensitivity,
      "confidence": confidence,
      "evidence_status": "cross-check-worthy" if confidence == "high" else "insufficient for curve change",
      "warning": "; ".join(warnings) or "mapping evidence only; not a controller-response trim",
    })
  write_dict_rows(path, rows)
  return rows


def write_manual_center_bias(path: Path, result: ScanResult) -> list[dict]:
  estimates = {estimate.route_id: estimate for estimate in result.manual_center_bias}
  rows = []
  for route_id in sorted(result.manual_applied_bias):
    applied_bias, source = result.manual_applied_bias[route_id]
    estimate = estimates.get(route_id)
    rows.append({
      "route_id": route_id,
      "fitted_bias_deg": estimate.bias_deg if estimate is not None else math.nan,
      "applied_bias_deg": applied_bias,
      "bias_source": source,
      "paired_angle_speed_cells": estimate.paired_bins if estimate is not None else 0,
      "left_seconds": estimate.left_seconds if estimate is not None else 0,
      "right_seconds": estimate.right_seconds if estimate is not None else 0,
      "objective_before_log_ratio": estimate.objective_before if estimate is not None else math.nan,
      "objective_after_log_ratio": estimate.objective_after if estimate is not None else math.nan,
      "fit_confidence": estimate.confidence if estimate is not None else "none",
    })
  write_dict_rows(path, rows)
  return rows


def write_manual_mapping_rejections(path: Path, result: ScanResult, angle_width: float) -> list[dict]:
  rows = []
  for fingerprint, start, reason in sorted(result.manual_rejection_seconds):
    rows.append({
      "fingerprint": fingerprint,
      "angle_start_deg": start,
      "angle_end_deg": start + angle_width,
      "reason": reason,
      "unique_seconds": len(result.manual_rejection_seconds[(fingerprint, start, reason)]),
      "frames": result.manual_rejected_frames[(fingerprint, start, reason)],
    })
  write_dict_rows(path, rows)
  return rows


def write_headline(path: Path, samples: list[CorrectionSample], angle_width: float) -> list[dict]:
  groups: defaultdict[tuple[str, float], list[CorrectionSample]] = defaultdict(list)
  for sample in samples:
    if sample.quality == "strict" and sample.phase == "steady" and math.isfinite(sample.effective_ratio):
      groups[(sample.fingerprint, angle_bin(sample.angle_deg, angle_width))].append(sample)

  rows = []
  for (fingerprint, start), group in sorted(groups.items()):
    stats = aggregate_bin(group)
    if stats is None:
      continue
    ratio, ratio_p25, ratio_p75 = route_balanced_metric(group, "effective_ratio")
    required, required_p25, required_p75 = route_balanced_metric(group, "required_angle_deg")
    speed_strata = supported_speed_strata(group, "effective_ratio")
    speed_spread = ((max(speed_strata) - min(speed_strata)) / abs(median(speed_strata))
                    if len(speed_strata) >= 2 and median(speed_strata) else math.nan)
    rows.append({
      "fingerprint": fingerprint,
      "angle_start_deg": start,
      "angle_end_deg": start + angle_width,
      "unique_seconds": stats.seconds,
      "routes": stats.routes,
      "route_directions": stats.route_directions,
      "left_seconds": stats.left_seconds,
      "right_seconds": stats.right_seconds,
      "model_effective_ratio": ratio,
      "ratio_p25": ratio_p25,
      "ratio_p75": ratio_p75,
      "required_angle_deg": required,
      "required_angle_p25": required_p25,
      "required_angle_p75": required_p75,
      "median_tracking_ratio": stats.median_tracking_ratio,
      "supported_speed_strata": len(speed_strata),
      "speed_strata_spread_percent": 100.0 * speed_spread,
      "confidence": mapping_confidence(
        stats.seconds, stats.routes, stats.left_seconds, stats.right_seconds,
        ratio, ratio_p25, ratio_p75, speed_strata,
      ),
    })
  write_dict_rows(path, rows)
  return rows


def write_command_correction(path: Path, samples: list[CorrectionSample], angle_width: float) -> list[dict]:
  groups: defaultdict[tuple[str, str, float], list[CorrectionSample]] = defaultdict(list)
  for sample in samples:
    if (sample.quality == "strict" and sample.phase == "steady"
        and sample.command_output_available and not sample.safety_limited):
      groups[(sample.fingerprint, sample.software_id, angle_bin(sample.desired_angle_deg, angle_width))].append(sample)
  rows = []
  for (fingerprint, signature, start), group in sorted(groups.items()):
    stats = aggregate_bin(group)
    if stats is None:
      continue
    speed_strata = supported_speed_strata(group, "correction_factor")
    speed_spread = ((max(speed_strata) - min(speed_strata)) / abs(median(speed_strata))
                    if len(speed_strata) >= 2 and median(speed_strata) else math.nan)
    rows.append({
      "fingerprint": fingerprint,
      "settings_signature": signature,
      "angle_start_deg": start,
      "angle_end_deg": start + angle_width,
      "unique_seconds": stats.seconds,
      "routes": stats.routes,
      "route_directions": stats.route_directions,
      "left_seconds": stats.left_seconds,
      "right_seconds": stats.right_seconds,
      "full_correction_percent": 100.0 * (stats.median_factor - 1.0),
      "factor_p25": stats.p25_factor,
      "factor_p75": stats.p75_factor,
      "median_tracking_ratio": stats.median_tracking_ratio,
      "supported_speed_strata": len(speed_strata),
      "speed_strata_spread_percent": 100.0 * speed_spread,
      "confidence": mapping_confidence(
        stats.seconds, stats.routes, stats.left_seconds, stats.right_seconds,
        stats.median_factor, stats.p25_factor, stats.p75_factor, speed_strata,
      ),
    })
  write_dict_rows(path, rows)
  return rows


def write_detail(path: Path, samples: list[CorrectionSample], angle_width: float) -> None:
  groups: defaultdict[tuple[str, BinKey], list[CorrectionSample]] = defaultdict(list)
  for sample in samples:
    groups[(sample.fingerprint, make_bin_key(sample, angle_width))].append(sample)
  rows = []
  for (fingerprint, key), group in sorted(groups.items(), key=lambda item: (item[0][0], *asdict(item[0][1]).values())):
    stats = aggregate_bin(group)
    if stats is None:
      continue
    ratio, ratio_p25, ratio_p75 = route_balanced_metric(group, "effective_ratio")
    rows.append({
      "fingerprint": fingerprint,
      **asdict(key),
      "unique_seconds": stats.seconds,
      "routes": stats.routes,
      "median_factor": stats.median_factor,
      "factor_p25": stats.p25_factor,
      "factor_p75": stats.p75_factor,
      "model_effective_ratio": ratio,
      "ratio_p25": ratio_p25,
      "ratio_p75": ratio_p75,
    })
  write_dict_rows(path, rows)


def write_stage_coverage(path: Path, result: ScanResult, angle_width: float) -> list[dict]:
  bins = sorted({(fingerprint, start) for fingerprint, start, _stage in result.stage_seconds} |
                {(fingerprint, start) for fingerprint, start, _reason in result.rejection_seconds})
  rows = []
  for fingerprint, start in bins:
    row = {
      "fingerprint": fingerprint,
      "angle_start_deg": start,
      "angle_end_deg": start + angle_width,
      "raw_pose_valid_seconds": len(result.stage_seconds[(fingerprint, start, "raw_pose_valid")]),
      "lat_active_seconds": len(result.stage_seconds[(fingerprint, start, "lat_active")]),
      "no_driver_seconds": len(result.stage_seconds[(fingerprint, start, "no_driver")]),
      "command_response_usable_seconds": len(result.stage_seconds[(fingerprint, start, "command_response_usable")]),
      "relaxed_usable_seconds": len(result.stage_seconds[(fingerprint, start, "relaxed_usable")]),
      "strict_usable_seconds": len(result.stage_seconds[(fingerprint, start, "strict_usable")]),
    }
    for reason in REJECTION_COLUMNS:
      name = re.sub(r"[^a-z0-9]+", "_", reason.lower()).strip("_")
      row[f"reject_{name}_seconds"] = len(result.rejection_seconds[(fingerprint, start, reason)])
      row[f"reject_{name}_frames"] = result.rejected_frames[(fingerprint, start, reason)]
    rows.append(row)
  write_dict_rows(path, rows)
  return rows


def write_experimental(path: Path, samples: list[CorrectionSample], angle_width: float) -> list[dict]:
  groups: defaultdict[tuple[str, str, float, str], list[CorrectionSample]] = defaultdict(list)
  for sample in samples:
    groups[(sample.fingerprint, sample.software_id, angle_bin(sample.angle_deg, angle_width), sample.phase)].append(sample)
  rows = []
  for (fingerprint, signature, start, phase), group in sorted(groups.items()):
    stats = aggregate_bin(group)
    if stats is None:
      continue
    usable = [sample for sample in group if sample.command_output_available and not sample.safety_limited]
    usable_stats = aggregate_bin(usable)
    minus = [sample.factor_delay_minus_100ms for sample in usable if math.isfinite(sample.factor_delay_minus_100ms)]
    plus = [sample.factor_delay_plus_100ms for sample in usable if math.isfinite(sample.factor_delay_plus_100ms)]
    paired_spans = [
      100.0 * abs(sample.factor_delay_plus_100ms - sample.factor_delay_minus_100ms)
      for sample in usable
      if math.isfinite(sample.factor_delay_minus_100ms) and math.isfinite(sample.factor_delay_plus_100ms)
    ]
    missing_output_seconds = {
      (sample.route_id, math.floor(sample.timestamp)) for sample in group if not sample.command_output_available
    }
    safety_limited_seconds = {
      (sample.route_id, math.floor(sample.timestamp)) for sample in group if sample.safety_limited
    }
    effective_ratio, effective_ratio_p25, effective_ratio_p75 = route_balanced_metric(group, "effective_ratio")
    rows.append({
      "fingerprint": fingerprint,
      "settings_signature": signature,
      "angle_start_deg": start,
      "angle_end_deg": start + angle_width,
      "phase": phase,
      "unique_seconds": stats.seconds,
      "routes": stats.routes,
      "command_usable_seconds": usable_stats.seconds if usable_stats is not None else 0,
      "missing_output_seconds": len(missing_output_seconds),
      "safety_limited_seconds": len(safety_limited_seconds),
      "transient_model_effective_ratio": effective_ratio,
      "transient_effective_ratio_p25": effective_ratio_p25,
      "transient_effective_ratio_p75": effective_ratio_p75,
      "nominal_full_correction_percent": (
        100.0 * (usable_stats.median_factor - 1.0) if usable_stats is not None else math.nan
      ),
      "minus_100ms_factor_median": percentile(minus, 50.0),
      "plus_100ms_factor_median": percentile(plus, 50.0),
      "median_200ms_sensitivity_points": percentile(paired_spans, 50.0),
      "warning": "experimental transient diagnostic; never merge into the strict SR recommendation",
    })
  write_dict_rows(path, rows)
  return rows


def write_dict_rows(path: Path, rows: list[dict]) -> None:
  if not rows:
    path.write_text("", encoding="utf-8")
    return
  with path.open("w", newline="", encoding="utf-8") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)


def write_report(path: Path, result: ScanResult, headline: list[dict], command_rows: list[dict],
                 stage_rows: list[dict], experimental_rows: list[dict],
                 manual_rows: list[dict], bias_rows: list[dict],
                 manual_rejection_rows: list[dict]) -> None:
  lines = [
    "Steer-ratio correction and coverage report",
    "",
    f"files read/failed: {result.files_read}/{result.files_failed}",
    f"routes: {len(result.routes)}",
    f"fingerprints: {', '.join(sorted(result.fingerprints)) or 'none'}",
    f"settings signatures: {len(result.signatures)}",
    f"accepted relaxed/strict samples: {len(result.samples)}",
    f"manual mapping-only steady-dwell samples: {len(result.manual_mapping_samples)}",
    f"experimental transient samples: {len(result.experimental_samples)}",
    "",
    "Strict mapping-independent coverage",
  ]
  for row in headline:
    lines.append(
      "".join((
        f"  {row['fingerprint']} {row['angle_start_deg']:g}-{row['angle_end_deg']:g} deg: ",
        f"{row['unique_seconds']} s, {row['routes']} routes, ",
        f"effective SR {row['model_effective_ratio']:.3f} ",
        f"({row['ratio_p25']:.3f}-{row['ratio_p75']:.3f}), {row['confidence']} confidence",
      ))
    )
  lines.extend((
    "",
    "Manual/command-independent steady-state effective-SR cohort",
    "  Does not require latActive, desired commands, or controller output, and does not exclude manual steering.",
    "  Driver-torque quartile sensitivity is reported and can downgrade confidence.",
    "  Requires calibrated pose/live parameters, forward motion, stable yaw/steering, bounded acceleration, and >=0.75 s dwell.",
    "  A per-route additive steering-center bias is fitted from bilateral 2-20 deg evidence; weak/unavailable fits remain unadjusted.",
    "  Values remain dependent on the vehicle/tire model, learned roll, and stiffness; sensitivity columns audit that dependence.",
    "  They are not controller-response trims or automatic deployment values.",
  ))
  for row in manual_rows:
    lines.append(
      "".join((
        f"  {row['fingerprint']} {row['angle_start_deg']:g}-{row['angle_end_deg']:g} deg: ",
        f"{row['unique_seconds']} s, {row['routes']} routes, ",
        f"effective SR {row['mapping_effective_ratio']:.3f} ",
        f"({row['ratio_p25']:.3f}-{row['ratio_p75']:.3f}), ",
        f"L/R gap {row['bilateral_gap_percent']:.1f}%, {row['confidence']} confidence",
      ))
    )
  lines.extend((
    "",
    "Coverage attrition by angle is in sr_stage_coverage.csv.",
    "Controller-response correction candidates are stratified by commit/settings in sr_command_correction.csv.",
    "They are roll-normalized and tracking-cancelled, but are not deployment-ready SR trim values.",
    "High-rate low-speed turns are isolated in sr_experimental_transient.csv with +/-100 ms lag sensitivity.",
    "Experimental transient rows are not part of the strict recommendation.",
    "",
    f"headline rows: {len(headline)}",
    f"command-stratified rows: {len(command_rows)}",
    f"stage rows: {len(stage_rows)}",
    f"experimental rows: {len(experimental_rows)}",
    f"manual mapping rows: {len(manual_rows)}",
    f"manual center-bias rows: {len(bias_rows)}",
    f"manual rejection rows: {len(manual_rejection_rows)}",
  ))
  path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("sources", nargs="+", help="local rlog.zst files, globs, or archive directories")
  parser.add_argument("--output-dir", type=Path, required=True, help="new output directory outside the checkout")
  parser.add_argument("--angle-bin", type=float, default=5.0, help="absolute steering-angle bin width (default: 5 deg)")
  parser.add_argument("--delay", type=float, help="override logged/default lateral delay in seconds")
  parser.add_argument("--max-pair-age", type=float, default=0.03,
                      help="maximum distance from requested delayed command sample (default: 0.03 s)")
  parser.add_argument("--progress-every", type=int, default=10, help="progress interval in rlogs (default: 10)")
  parser.add_argument("--force", action="store_true", help="allow replacing analyzer outputs in an existing directory")
  return parser


def json_safe(value):
  if isinstance(value, float):
    return value if math.isfinite(value) else None
  if isinstance(value, dict):
    return {key: json_safe(item) for key, item in value.items()}
  if isinstance(value, (list, tuple)):
    return [json_safe(item) for item in value]
  return value


def main(argv: list[str] | None = None) -> int:
  parser = build_parser()
  args = parser.parse_args(argv)
  if args.angle_bin <= 0.0 or args.max_pair_age <= 0.0 or args.progress_every <= 0:
    parser.error("angle bin, pair age, and progress interval must be positive")
  if args.delay is not None and args.delay < 0.0:
    parser.error("delay cannot be negative")

  sources = expand_sources(args.sources)
  if not sources:
    parser.error("no local rlog.zst files found")
  output_dir = args.output_dir.resolve()
  checkout = Path(__file__).resolve().parent
  if output_dir == checkout or checkout in output_dir.parents:
    parser.error("analysis output must be outside the source checkout")

  output_names = (
    "sr_samples.csv.gz",
    "sr_experimental_samples.csv.gz",
    "sr_manual_mapping_samples.csv.gz",
    "sr_strict_angle_coverage.csv",
    "sr_manual_mapping.csv",
    "sr_manual_center_bias.csv",
    "sr_manual_mapping_rejections.csv",
    "sr_command_correction.csv",
    "sr_detail_coverage.csv",
    "sr_stage_coverage.csv",
    "sr_experimental_transient.csv",
    "sr_summary.json",
    "sr_report.txt",
  )
  existing = [name for name in output_names if (output_dir / name).exists()]
  if existing and not args.force:
    parser.error(f"output files already exist ({', '.join(existing)}); choose a new directory or use --force")
  output_dir.mkdir(parents=True, exist_ok=True)

  print(f"Scanning {len(sources)} unique local rlogs...", file=sys.stderr, flush=True)
  result = scan_sources(sources, args.angle_bin, args.delay, args.max_pair_age, args.progress_every)
  write_samples(output_dir / "sr_samples.csv.gz", result.samples)
  write_samples(output_dir / "sr_experimental_samples.csv.gz", result.experimental_samples)
  write_manual_mapping_samples(output_dir / "sr_manual_mapping_samples.csv.gz", result.manual_mapping_samples)
  headline = write_headline(output_dir / "sr_strict_angle_coverage.csv", result.samples, args.angle_bin)
  manual_rows = write_manual_mapping(
    output_dir / "sr_manual_mapping.csv", result.manual_mapping_samples, args.angle_bin,
  )
  bias_rows = write_manual_center_bias(output_dir / "sr_manual_center_bias.csv", result)
  manual_rejection_rows = write_manual_mapping_rejections(
    output_dir / "sr_manual_mapping_rejections.csv", result, args.angle_bin,
  )
  command_rows = write_command_correction(output_dir / "sr_command_correction.csv", result.samples, args.angle_bin)
  write_detail(output_dir / "sr_detail_coverage.csv", result.samples, args.angle_bin)
  stage_rows = write_stage_coverage(output_dir / "sr_stage_coverage.csv", result, args.angle_bin)
  experimental_rows = write_experimental(
    output_dir / "sr_experimental_transient.csv", result.experimental_samples, args.angle_bin,
  )
  summary = {
    "created": datetime.now().astimezone().isoformat(),
    "sources": len(sources),
    "files_read": result.files_read,
    "files_failed": result.files_failed,
    "routes": len(result.routes),
    "fingerprints": sorted(result.fingerprints),
    "settings_signatures": sorted(result.signatures),
    "accepted_samples": len(result.samples),
    "experimental_samples": len(result.experimental_samples),
    "manual_mapping_samples": len(result.manual_mapping_samples),
    "strict_angle_coverage": headline,
    "manual_mapping": manual_rows,
    "manual_center_bias": bias_rows,
    "manual_mapping_rejections": manual_rejection_rows,
    "command_correction": command_rows,
    "stage_coverage": stage_rows,
    "experimental_transient": experimental_rows,
  }
  (output_dir / "sr_summary.json").write_text(
    json.dumps(json_safe(summary), indent=2, allow_nan=False) + "\n",
    encoding="utf-8",
  )
  write_report(
    output_dir / "sr_report.txt", result, headline, command_rows, stage_rows, experimental_rows,
    manual_rows, bias_rows, manual_rejection_rows,
  )
  print((output_dir / "sr_report.txt").read_text(encoding="utf-8"))
  print(f"Wrote analysis to {output_dir}")
  return 0 if result.files_read else 1


if __name__ == "__main__":
  raise SystemExit(main())
