#!/usr/bin/env python3
"""
Report openpilot's learned steer-ratio scalar and estimate effective steer ratio by angle.

There are two different measurements in this report:

1. ``vehicleParameters.steerRatio`` is the scalar produced by paramsd. paramsd only
   updates it while |steeringAngleDeg| < 45 degrees, so more driving can improve
   the near-center scalar but cannot learn a variable-ratio rack's off-center curve.
2. The angle-binned estimate uses calibrated IMU yaw rate and vehicle speed:

       curvature_achieved = yaw_rate / v_ego
       road_wheel_angle = atan(wheelbase * curvature_achieved)
       effective_ratio = steering_wheel_angle / road_wheel_angle

   That is an effective *dynamic* ratio. Tire slip, compliance, road roll, speed,
   and timing error remain in the result; it is useful for validating the shape of
   a VGR curve, but it is not a direct measurement of rack-tooth geometry. The
   estimator removes the learned average steering-center offset, keeps only
   quasi-steady steering, reports both steering directions, and stratifies by
   speed so those dynamic effects are visible instead of silently averaged.

Examples (run from the openpilot checkout on the device):

  # Instant: show the scalar currently persisted by paramsd.
  python3 -m openpilot.nrdr.tools.steer_ratio.by_angle --cached

  # Fast historical check using the last 30 days of qlogs.
  python3 -m openpilot.nrdr.tools.steer_ratio.by_angle --learned-only --log-type qlog --since-days 30 \
    /data/media/0/realdata

  # Higher-rate VGR estimate from one or more deliberately curvy routes.
  python3 -m openpilot.nrdr.tools.steer_ratio.by_angle --log-type rlog \
    /data/media/0/realdata/<route>--*/rlog.zst

Inputs may be local log files, directories, shell globs, route identifiers, or
Connect URLs understood by tools.lib.logreader.LogReader. This tool is read-only.
"""

import argparse
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import glob
import math
from pathlib import Path
import re
import sys
import time

import numpy as np


M_PER_MILE = 1609.344
MPS_TO_MPH = 2.236936
ROUTE_TIME_RE = re.compile(r"(\d{4}-\d{2}-\d{2}--\d{2}-\d{2}-\d{2})")
SEGMENT_DIR_RE = re.compile(r"^(.*)--(\d+)$")


def percentile(values: list[float], q: float) -> float:
  return float(np.percentile(np.asarray(values, dtype=float), q))


@dataclass(frozen=True)
class CarStateSample:
  timestamp: float
  speed: float
  steering_angle: float
  steering_rate: float
  steering_pressed: bool
  angle_offset: float
  angle_offset_valid: bool


@dataclass(frozen=True)
class AngleRatioSample:
  ratio: float
  speed: float
  steering_angle: float


def nearest_state_sample(samples: list[CarStateSample] | deque[CarStateSample], target_time: float,
                         max_age: float) -> CarStateSample | None:
  """Return the state nearest target_time, provided the pairing is fresh enough."""
  if not samples:
    return None
  sample = min(samples, key=lambda value: abs(value.timestamp - target_time))
  return sample if abs(sample.timestamp - target_time) <= max_age else None


def effective_ratio(steering_angle_deg: float, angle_offset_deg: float, yaw_rate: float,
                    speed: float, wheelbase: float) -> float | None:
  """Compute the dynamic steering ratio after removing the learned center offset."""
  corrected_angle = steering_angle_deg - angle_offset_deg
  if speed <= 0.0 or wheelbase <= 0.0:
    return None
  road_wheel_angle = math.atan(wheelbase * abs(yaw_rate / speed))
  if road_wheel_angle <= 1e-4:
    return None
  ratio = abs(math.radians(corrected_angle)) / road_wheel_angle
  return ratio if math.isfinite(ratio) else None


def angle_bin_start(angle_deg: float, bin_width_deg: float) -> float:
  return math.floor(abs(angle_deg) / bin_width_deg) * bin_width_deg


def format_number(value: float) -> str:
  return f"{value:g}"


def source_time(path: Path) -> datetime | None:
  match = ROUTE_TIME_RE.search(str(path))
  if match is not None:
    try:
      return datetime.strptime(match.group(1), "%Y-%m-%d--%H-%M-%S")
    except ValueError:
      pass
  try:
    return datetime.fromtimestamp(path.stat().st_mtime)
  except OSError:
    return None


def source_sort_key(source: str) -> tuple:
  """Sort local segment logs by route and numeric segment, not --1/--10/--2."""
  path = Path(source)
  match = SEGMENT_DIR_RE.match(path.parent.name)
  if match is not None:
    return 0, match.group(1), int(match.group(2)), str(path)
  return 1, source_time(path) or datetime.min, str(path)


def format_duration(seconds: float) -> str:
  seconds = max(int(seconds), 0)
  hours, remainder = divmod(seconds, 3600)
  minutes, seconds = divmod(remainder, 60)
  return f"{hours:d}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:d}:{seconds:02d}"


def expand_sources(raw_sources: list[str], log_type: str, since: datetime | None) -> list[str]:
  log_name = f"{log_type}.zst"
  expanded: list[str] = []

  for raw in raw_sources:
    # Preserve route identifiers and URLs. Expand only things that are existing
    # filesystem paths or actual glob matches.
    matches = sorted(glob.glob(raw, recursive=True))
    candidates = matches if matches else [raw]
    for candidate in candidates:
      path = Path(candidate)
      if path.is_dir():
        files = sorted(path.rglob(log_name), key=lambda p: (source_time(p) or datetime.min, str(p)))
        for file in files:
          if since is None or (source_time(file) is not None and source_time(file) >= since):
            expanded.append(str(file))
      elif path.is_file():
        if since is None or (source_time(path) is not None and source_time(path) >= since):
          expanded.append(str(path))
      else:
        expanded.append(candidate)

  # A repeated glob or overlapping directory should not scan a segment twice.
  return sorted(dict.fromkeys(expanded), key=source_sort_key)


def print_cached_params() -> bool:
  try:
    from openpilot.cereal import log
    import openpilot.cereal.messaging as messaging
    from opendbc.car.structs import car
  except ImportError:
    from cereal import car, log
    import cereal.messaging as messaging
  from openpilot.common.params import Params

  params = Params()
  raw_lp = params.get("LiveParametersV2")
  if raw_lp is None:
    print("Cached learner: LiveParametersV2 is not present.")
    return False

  fingerprint = "unknown"
  raw_cp = params.get("CarParamsPrevRoute") or params.get("CarParams")
  if raw_cp is not None:
    try:
      fingerprint = str(messaging.log_from_bytes(raw_cp, car.CarParams).carFingerprint)
    except Exception:
      pass

  try:
    with log.Event.from_bytes(raw_lp) as event:
      lp = event.vehicleParameters
      print("Cached learner")
      print(f"  fingerprint:          {fingerprint}")
      print(f"  steer ratio:          {float(lp.steerRatio):.4f}")
      print(f"  steer-ratio std:      {float(lp.steerRatioStd):.4f}")
      print(f"  steer-ratio valid:    {bool(lp.steerRatioValid)}")
      print(f"  stiffness factor:     {float(lp.stiffnessFactor):.4f}")
      print(f"  average angle offset: {float(lp.angleOffsetAverageDeg):+.4f} deg")
      print()
      return True
  except Exception as exc:
    print(f"Cached learner: could not decode LiveParametersV2: {exc}", file=sys.stderr)
    return False


@dataclass
class CarReportData:
  wheelbases: set[float] = field(default_factory=set)
  learned_values: list[float] = field(default_factory=list)
  learned_stds: list[float] = field(default_factory=list)
  learned_valid: int = 0
  learned_total: int = 0
  angle_bins: defaultdict[float, list[AngleRatioSample]] = field(default_factory=lambda: defaultdict(list))
  rejected_samples: Counter[str] = field(default_factory=Counter)
  accepted_samples: int = 0
  offset_corrected_samples: int = 0
  distance_m: float = 0.0
  duration_s: float = 0.0


class SteerRatioReport:
  def __init__(self, args: argparse.Namespace):
    self.args = args
    self.cars: dict[str, CarReportData] = {}
    self.current_fingerprint: str | None = None
    self.current_wheelbase: float | None = None
    self.files_read = 0
    self.files_failed = 0

  def car_data(self, fingerprint: str | None = None) -> CarReportData:
    key = fingerprint or self.current_fingerprint or "UNKNOWN"
    if key not in self.cars:
      self.cars[key] = CarReportData()
    return self.cars[key]

  def scan(self, sources: list[str]) -> None:
    from openpilot.selfdrive.locationd.helpers import Pose, PoseCalibrator
    from openpilot.tools.lib.logreader import LogReader

    print(f"Scanning {len(sources)} log source(s)...", file=sys.stderr, flush=True)
    started = time.monotonic()
    progress_interval = max(1, min(25, len(sources) // 20))

    for source_index, source in enumerate(sources, start=1):
      try:
        reader = LogReader(source, sort_by_time=True)
      except Exception as exc:
        self.files_failed += 1
        print(f"!! could not open {source}: {exc}", file=sys.stderr)
        self.print_progress(source_index, len(sources), started, progress_interval)
        continue

      # State is reset per source so timestamps that restart between routes cannot
      # create bogus distance or stale cross-route sensor pairings.
      fingerprint = self.current_fingerprint
      wheelbase = self.current_wheelbase
      speed = 0.0
      steering_angle = 0.0
      steering_pressed = True
      lat_active = False
      car_state_t: float | None = None
      car_control_t: float | None = None
      previous_car_t: float | None = None
      previous_speed = 0.0
      steering_rate = 0.0
      angle_offset = 0.0
      angle_offset_valid = False
      state_history: deque[CarStateSample] = deque(maxlen=1000)
      calibrator = PoseCalibrator()

      try:
        for event in reader:
          which = event.which()
          t = float(event.logMonoTime) * 1e-9

          if which == "carParams":
            new_fingerprint = str(event.carParams.carFingerprint)
            if fingerprint is not None and new_fingerprint != fingerprint:
              previous_car_t = None
              previous_speed = 0.0
            fingerprint = new_fingerprint
            wheelbase = float(event.carParams.wheelbase)
            self.current_fingerprint = fingerprint
            self.current_wheelbase = wheelbase
            self.car_data(fingerprint).wheelbases.add(round(wheelbase, 6))

          elif which == "extrinsicsCalibration":
            calibrator.feed_extrinsics_calibration(event.extrinsicsCalibration)

          elif which == "vehicleParameters":
            data = self.car_data(fingerprint)
            lp = event.vehicleParameters
            # The average component represents the persistent steering-sensor
            # center. The fast component in angleOffsetDeg is a dynamic model
            # correction and would contaminate a rack-geometry estimate.
            if event.valid and lp.angleOffsetAverageValid and math.isfinite(float(lp.angleOffsetAverageDeg)):
              angle_offset = float(lp.angleOffsetAverageDeg)
              angle_offset_valid = True
            value = float(lp.steerRatio)
            std = float(lp.steerRatioStd)
            valid = bool(event.valid and lp.steerRatioValid and math.isfinite(value))
            data.learned_total += 1
            if valid:
              data.learned_valid += 1
              data.learned_values.append(value)
              if math.isfinite(std):
                data.learned_stds.append(std)

          elif which == "carState":
            speed = float(event.carState.vEgo)
            steering_angle = float(event.carState.steeringAngleDeg)
            steering_rate = float(event.carState.steeringRateDeg)
            steering_pressed = bool(event.carState.steeringPressed)
            car_state_t = t
            state_history.append(CarStateSample(t, speed, steering_angle, steering_rate, steering_pressed,
                                                angle_offset, angle_offset_valid))

            if previous_car_t is not None:
              dt = t - previous_car_t
              if 0.0 < dt < 1.0:
                data = self.car_data(fingerprint)
                data.distance_m += 0.5 * (max(previous_speed, 0.0) + max(speed, 0.0)) * dt
                data.duration_s += dt
            previous_car_t = t
            previous_speed = speed

          elif which == "carControl":
            lat_active = bool(event.carControl.latActive)
            car_control_t = t

          elif which == "deviceMotion" and not self.args.learned_only:
            data = self.car_data(fingerprint)
            if wheelbase is None or not calibrator.calib_valid:
              data.rejected_samples["missing car/calibration"] += 1
              continue
            if car_state_t is None or car_control_t is None or not state_history:
              data.rejected_samples["missing state/control"] += 1
              continue
            current_state = nearest_state_sample(state_history, t, self.args.max_pair_age)
            steering_state = nearest_state_sample(state_history, t - self.args.yaw_delay, self.args.max_pair_age)
            if current_state is None or steering_state is None or t - car_control_t > self.args.max_pair_age:
              data.rejected_samples["stale state/control"] += 1
              continue
            if not lat_active or current_state.steering_pressed or steering_state.steering_pressed:
              data.rejected_samples["inactive/driver steering"] += 1
              continue
            speed = current_state.speed
            if not (self.args.min_speed <= speed <= self.args.max_speed):
              data.rejected_samples["speed gate"] += 1
              continue
            sample_offset = steering_state.angle_offset if steering_state.angle_offset_valid else 0.0
            if self.args.require_angle_offset and not steering_state.angle_offset_valid:
              data.rejected_samples["missing angle offset"] += 1
              continue
            corrected_angle = steering_state.steering_angle - sample_offset
            if abs(corrected_angle) < self.args.min_angle:
              data.rejected_samples["angle gate"] += 1
              continue
            if abs(steering_state.steering_rate) > self.args.max_steering_rate:
              data.rejected_samples["steering-rate gate"] += 1
              continue
            if not (event.deviceMotion.inputsOK and event.deviceMotion.posenetOK and event.deviceMotion.sensorsOK):
              data.rejected_samples["invalid pose"] += 1
              continue

            pose = calibrator.build_calibrated_pose(Pose.from_device_motion(event.deviceMotion))
            yaw_rate = float(pose.angular_velocity.xyz[2])
            if not math.isfinite(yaw_rate) or abs(yaw_rate) < self.args.min_yaw:
              data.rejected_samples["yaw gate"] += 1
              continue

            ratio = effective_ratio(steering_state.steering_angle, sample_offset, yaw_rate, speed, wheelbase)
            if ratio is None:
              data.rejected_samples["invalid ratio"] += 1
              continue

            if self.args.min_ratio <= ratio <= self.args.max_ratio:
              bin_start = angle_bin_start(corrected_angle, self.args.angle_bin)
              data.angle_bins[bin_start].append(AngleRatioSample(ratio, speed, corrected_angle))
              data.accepted_samples += 1
              data.offset_corrected_samples += int(steering_state.angle_offset_valid)
            else:
              data.rejected_samples["ratio bounds"] += 1

        self.files_read += 1
      except Exception as exc:
        self.files_failed += 1
        print(f"!! failed while reading {source}: {exc}", file=sys.stderr)

      self.print_progress(source_index, len(sources), started, progress_interval)

  @staticmethod
  def print_progress(completed: int, total: int, started: float, interval: int) -> None:
    if completed != total and completed % interval != 0:
      return
    elapsed = time.monotonic() - started
    rate = completed / elapsed if elapsed > 0.0 else 0.0
    eta = (total - completed) / rate if rate > 0.0 else 0.0
    progress = " | ".join((
      f"Progress: {completed}/{total} ({100.0 * completed / total:.1f}%)",
      f"elapsed {format_duration(elapsed)}",
      f"ETA {format_duration(eta)}",
    ))
    print(
      progress,
      file=sys.stderr,
      flush=True,
    )

  def print_report(self) -> None:
    print("Log summary")
    print(f"  sources read/failed: {self.files_read}/{self.files_failed}")
    print(f"  fingerprints:        {', '.join(sorted(self.cars)) or 'not present in logs'}")
    print()

    for car_index, (fingerprint, data) in enumerate(sorted(self.cars.items())):
      if car_index:
        print()
      print(f"[{fingerprint}]")
      print(f"  wheelbase(s):        {', '.join(f'{v:.3f} m' for v in sorted(data.wheelbases)) or 'not present in logs'}")
      print(f"  sampled distance:    {data.distance_m / M_PER_MILE:.1f} mi")
      print(f"  sampled drive time:  {data.duration_s / 3600.0:.1f} h")
      print()

      self.print_learned_report(data)
      if not self.args.learned_only:
        self.print_angle_report(data, fingerprint)

  def print_learned_report(self, data: CarReportData) -> None:
    if data.learned_values:
      final_window = data.learned_values[-min(len(data.learned_values), 1000):]
      learned_delta = data.learned_values[-1] - data.learned_values[0]
      print("paramsd learned scalar (near-center; |steering angle| < 45 deg)")
      print(f"  valid samples:       {data.learned_valid}/{data.learned_total}")
      print(f"  first -> last:       {data.learned_values[0]:.4f} -> {data.learned_values[-1]:.4f} ({learned_delta:+.4f})")
      print(f"  all-sample median:   {percentile(data.learned_values, 50):.4f}")
      print(f"  10th-90th range:     {percentile(data.learned_values, 10):.4f} - {percentile(data.learned_values, 90):.4f}")
      print(f"  final-window median: {percentile(final_window, 50):.4f} (last {len(final_window)} samples)")
      if data.learned_stds:
        print(f"  final reported std:  {data.learned_stds[-1]:.4f}")
    else:
      print("paramsd learned scalar: no valid vehicleParameters samples found.")
    print()

  def print_angle_report(self, data: CarReportData, fingerprint: str) -> None:
    rows = []
    for bin_start in sorted(data.angle_bins):
      samples = data.angle_bins[bin_start]
      if len(samples) < self.args.min_samples:
        continue
      ratios = [sample.ratio for sample in samples]
      speeds = [sample.speed for sample in samples]
      negative = [sample.ratio for sample in samples if sample.steering_angle < 0.0]
      positive = [sample.ratio for sample in samples if sample.steering_angle > 0.0]
      rows.append((
        bin_start,
        bin_start + self.args.angle_bin,
        len(samples),
        percentile(ratios, 50),
        percentile(ratios, 25),
        percentile(ratios, 75),
        percentile(speeds, 50),
        percentile(speeds, 25),
        percentile(speeds, 75),
        len(negative),
        percentile(negative, 50) if negative else math.nan,
        len(positive),
        percentile(positive, 50) if positive else math.nan,
      ))

    print("Angle estimator diagnostics")
    print(f"  accepted samples:    {data.accepted_samples}")
    print(f"  offset-corrected:    {data.offset_corrected_samples}/{data.accepted_samples}")
    print(f"  steering/yaw delay:  {self.args.yaw_delay:.3f} s")
    print(f"  max steering rate:   {self.args.max_steering_rate:.1f} deg/s")
    if data.rejected_samples:
      rejected = ", ".join(f"{reason}={count}" for reason, count in data.rejected_samples.most_common())
      print(f"  rejected:            {rejected}")
    print()

    if not rows:
      print("Angle-binned effective ratio: no bins met the sample threshold.")
      print("Use selected curvy rlogs; highway driving mostly improves the scalar above.")
      return

    print("Angle-binned effective dynamic ratio")
    print(f"{'|angle| bin':>17} {'n':>8} {'median SR':>10} {'SR IQR':>15} {'speed mph IQR':>19} {'steer-/+ SR':>17}")
    for start, end, count, median, p25, p75, _speed, speed_p25, speed_p75, neg_n, neg_sr, pos_n, pos_sr in rows:
      direction_sr = f"{neg_sr:.2f}/{pos_sr:.2f}" if neg_n and pos_n else "insufficient"
      line = (
        f"{format_number(start):>5}-{format_number(end):<5} deg {count:>8} {median:>10.2f} "
        + f"{p25:>6.2f}-{p75:<6.2f} {speed_p25 * MPS_TO_MPH:>6.1f}-{speed_p75 * MPS_TO_MPH:<6.1f} "
        + f"{direction_sr:>17}"
      )
      print(line)

    if self.args.speed_bin > 0.0:
      speed_rows = []
      for angle_start in sorted(data.angle_bins):
        by_speed: defaultdict[float, list[float]] = defaultdict(list)
        for sample in data.angle_bins[angle_start]:
          speed_start = math.floor(sample.speed / self.args.speed_bin) * self.args.speed_bin
          by_speed[speed_start].append(sample.ratio)
        for speed_start, ratios in sorted(by_speed.items()):
          if len(ratios) >= self.args.min_samples:
            speed_rows.append((angle_start, speed_start, len(ratios), percentile(ratios, 50),
                               percentile(ratios, 25), percentile(ratios, 75)))
      if speed_rows:
        print("\nAngle/speed-stratified ratio (reveals speed-dependent tire/understeer bias)")
        print(f"{'|angle| bin':>17} {'speed bin':>18} {'n':>8} {'median SR':>10} {'SR IQR':>15}")
        for angle_start, speed_start, count, median, p25, p75 in speed_rows:
          angle_end = angle_start + self.args.angle_bin
          speed_end = speed_start + self.args.speed_bin
          line = (
            f"{format_number(angle_start):>5}-{format_number(angle_end):<5} deg "
            + f"{speed_start * MPS_TO_MPH:>6.1f}-{speed_end * MPS_TO_MPH:<6.1f} mph "
            + f"{count:>8} {median:>10.2f} {p25:>6.2f}-{p75:<6.2f}"
          )
          print(line)

    if self.args.csv is not None:
      csv_path = Path(self.args.csv)
      if len(self.cars) > 1:
        csv_path = csv_path.with_name(f"{csv_path.stem}-{fingerprint}{csv_path.suffix}")
      with csv_path.open("w", newline="", encoding="utf-8") as stream:
        header = (
          "angle_start_deg,angle_end_deg,samples,median_ratio,p25_ratio,p75_ratio,"
          + "median_speed_mps,p25_speed_mps,p75_speed_mps,negative_samples,negative_median_ratio,"
          + "positive_samples,positive_median_ratio\n"
        )
        stream.write(header)
        for row in rows:
          line = (
            f"{row[0]:g},{row[1]:g},{row[2]},{row[3]:.6f},{row[4]:.6f},{row[5]:.6f},"
            + f"{row[6]:.6f},{row[7]:.6f},{row[8]:.6f},{row[9]},{row[10]:.6f},"
            + f"{row[11]},{row[12]:.6f}\n"
          )
          stream.write(line)
      print(f"\nWrote {csv_path}")


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument("sources", nargs="*", help="log files, directories, globs, route identifiers, or Connect URLs")
  parser.add_argument("--cached", action="store_true", help="show the currently persisted LiveParametersV2 value")
  parser.add_argument("--learned-only", action="store_true", help="skip the angle-binned IMU estimate")
  parser.add_argument("--log-type", choices=("rlog", "qlog"), default="rlog", help="file selected while scanning directories")
  parser.add_argument("--since-days", type=float, help="only scan local logs from approximately the last N days")
  parser.add_argument("--csv", help="write accepted angle-bin rows to this CSV")
  parser.add_argument("--angle-bin", type=float, default=25.0, help="angle-bin width in degrees (default: 25)")
  parser.add_argument("--speed-bin", type=float, default=5.0,
                      help="also stratify each angle bin by this speed width in m/s; 0 disables (default: 5)")
  parser.add_argument("--min-samples", type=int, default=30, help="minimum accepted samples per angle bin (default: 30)")
  parser.add_argument("--min-angle", type=float, default=5.0, help="minimum absolute steering angle in degrees")
  parser.add_argument("--min-yaw", type=float, default=0.03, help="minimum absolute calibrated yaw rate in rad/s")
  parser.add_argument("--min-speed", type=float, default=3.0, help="minimum speed in m/s")
  parser.add_argument("--max-speed", type=float, default=25.0, help="maximum speed in m/s; limits dynamic understeer bias")
  parser.add_argument("--max-pair-age", type=float, default=0.25, help="maximum sensor/state pairing age in seconds")
  parser.add_argument("--yaw-delay", type=float, default=0.0,
                      help="pair yaw with steering measured this many seconds earlier (default: 0; use only when measured)")
  parser.add_argument("--max-steering-rate", type=float, default=5.0,
                      help="keep quasi-steady samples at or below this absolute steering rate in deg/s (default: 5)")
  parser.add_argument("--require-angle-offset", action="store_true",
                      help="reject samples until a valid learned steering-angle offset is available")
  parser.add_argument("--min-ratio", type=float, default=5.0, help="minimum sane effective ratio")
  parser.add_argument("--max-ratio", type=float, default=40.0, help="maximum sane effective ratio")
  return parser


def main() -> int:
  args = build_parser().parse_args()

  if args.angle_bin <= 0 or args.speed_bin < 0 or args.min_samples <= 0:
    raise SystemExit("--angle-bin and --min-samples must be positive; --speed-bin cannot be negative")
  if args.yaw_delay < 0 or args.max_pair_age <= 0 or args.max_steering_rate < 0:
    raise SystemExit("--yaw-delay must be non-negative; pairing age must be positive; steering-rate limit cannot be negative")
  if args.since_days is not None and args.since_days < 0:
    raise SystemExit("--since-days must be non-negative")

  if args.cached:
    print_cached_params()

  if not args.sources:
    if args.cached:
      return 0
    build_parser().error("provide at least one log source, or use --cached")

  since = datetime.now() - timedelta(days=args.since_days) if args.since_days is not None else None
  sources = expand_sources(args.sources, args.log_type, since)
  if not sources:
    print("No matching logs found.", file=sys.stderr)
    return 1

  report = SteerRatioReport(args)
  report.scan(sources)
  report.print_report()
  return 0 if report.files_read else 1


if __name__ == "__main__":
  raise SystemExit(main())


__all__ = (
  "M_PER_MILE",
  "MPS_TO_MPH",
  "ROUTE_TIME_RE",
  "SEGMENT_DIR_RE",
  "AngleRatioSample",
  "CarReportData",
  "CarStateSample",
  "SteerRatioReport",
  "angle_bin_start",
  "build_parser",
  "effective_ratio",
  "expand_sources",
  "format_duration",
  "format_number",
  "main",
  "nearest_state_sample",
  "percentile",
  "print_cached_params",
  "source_sort_key",
  "source_time",
)
