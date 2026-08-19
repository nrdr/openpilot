import csv
from dataclasses import replace
import gzip
import json
import math
import sys
from types import ModuleType
from types import SimpleNamespace

import pytest

import steerratio_correction as cli
from openpilot.sunnypilot.nrdr.sr_correction_analysis import CommandSample, CorrectionSample, MappingSample, VehicleSample


def sample(**overrides) -> CorrectionSample:
  values = {
    "route_id": "route-a",
    "timestamp": 0.1,
    "speed_mps": 10.0,
    "angle_deg": 22.0,
    "direction": "left",
    "phase": "steady",
    "desired_curvature": 0.01,
    "achieved_curvature": 0.01,
    "desired_angle_deg": -20.0,
    "actual_angle_deg": -20.0,
    "correction_factor": 1.0,
    "tracking_ratio": 1.0,
    "software_id": "build-a",
    "quality": "strict",
    "fingerprint": "HONDA_CLARITY",
  }
  values.update(overrides)
  return CorrectionSample(**values)


def mapping_sample(**overrides) -> MappingSample:
  values = {
    "route_id": "route-a",
    "timestamp": 0.0,
    "speed_mps": 10.0,
    "signed_angle_deg": -10.0,
    "direction": "left",
    "effective_ratio": 18.0,
    "ratio_per_degree": 1.8,
    "bias_corrected_angle_deg": -10.0,
    "bias_corrected_effective_ratio": 18.0,
    "fingerprint": "HONDA_CLARITY",
  }
  values.update(overrides)
  return MappingSample(**values)


def install_fake_scan_dependencies(monkeypatch):
  class FakePose:
    @staticmethod
    def from_live_pose(live_pose):
      return live_pose

  class FakePoseCalibrator:
    calib_valid = True

    def feed_live_calib(self, _calibration):
      pass

    def build_calibrated_pose(self, live_pose):
      return SimpleNamespace(angular_velocity=SimpleNamespace(z=live_pose.yaw_rate, z_std=0.01))

  fake_cereal = ModuleType("openpilot.cereal")
  fake_cereal.log = SimpleNamespace(LaneChangeState=SimpleNamespace(off=0))
  fake_helpers = ModuleType("openpilot.selfdrive.locationd.helpers")
  fake_helpers.Pose = FakePose
  fake_helpers.PoseCalibrator = FakePoseCalibrator
  monkeypatch.setitem(sys.modules, "openpilot.cereal", fake_cereal)
  monkeypatch.setitem(sys.modules, "openpilot.selfdrive.locationd.helpers", fake_helpers)


def scan_event(name, timestamp, value):
  item = SimpleNamespace(logMonoTime=round(timestamp * 1e9), valid=True)
  item.which = lambda: name
  setattr(item, name, value)
  return item


def scan_setup_events(fingerprint="HONDA_CLARITY", param_entries=()):
  return [
    scan_event("initData", 9.0, SimpleNamespace(
      gitSrcCommit="0123456789abcdef",
      gitCommit="",
      gitBranch="nrdr-development",
      params=SimpleNamespace(entries=list(param_entries)),
    )),
    scan_event("carParams", 9.0, SimpleNamespace(
      carFingerprint=fingerprint,
      wheelbase=2.75,
      mass=1600.0,
      centerToFront=1.2,
      tireStiffnessFront=100_000.0,
      tireStiffnessRear=100_000.0,
      steerActuatorDelay=0.1,
      carFw=[],
    )),
  ]


def manual_scan_frame(timestamp, *, average_offset=0.0, stiffness=1.0, steering_pressed=True):
  return (
    scan_event("liveParameters", timestamp, SimpleNamespace(
      valid=True,
      angleOffsetValid=True,
      angleOffsetAverageValid=True,
      stiffnessFactorValid=True,
      angleOffsetDeg=0.0,
      angleOffsetAverageDeg=average_offset,
      roll=0.0,
      stiffnessFactor=stiffness,
    )),
    scan_event("carState", timestamp, SimpleNamespace(
      vEgo=10.0,
      aEgo=0.0,
      steeringAngleDeg=-20.0,
      steeringRateDeg=0.0,
      steeringTorque=0.5,
      steeringPressed=steering_pressed,
      gearShifter="drive",
      leftBlinker=False,
      rightBlinker=False,
      steerFaultTemporary=False,
      steerFaultPermanent=False,
    )),
    scan_event("livePose", timestamp, SimpleNamespace(
      yaw_rate=0.1,
      inputsOK=True,
      posenetOK=True,
      sensorsOK=True,
      angularVelocityDevice=SimpleNamespace(valid=True),
    )),
  )


def controller_scan_frame(timestamp, *, average_offset=0.0, stiffness=1.0):
  live_params, car_state, live_pose = manual_scan_frame(
    timestamp,
    average_offset=average_offset,
    stiffness=stiffness,
    steering_pressed=False,
  )
  return (
    live_params,
    car_state,
    scan_event("carControl", timestamp, SimpleNamespace(
      latActive=True,
      actuators=SimpleNamespace(curvature=0.01, steeringAngleDeg=-20.0, torque=0.5),
    )),
    scan_event("carOutput", timestamp, SimpleNamespace(
      actuatorsOutput=SimpleNamespace(torque=0.5),
    )),
    live_pose,
  )


def test_settings_signature_is_stable_and_separates_tune_state():
  settings = {
    "NrdrNnlcEnabled": "0",
    "NrdrLearnSteerRatio": "1",
  }
  signature = cli.settings_signature("0123456789abcdef", "nrdr-development", settings)
  assert signature == "nrdr-development@0123456789ab|NrdrLearnSteerRatio=1,NrdrNnlcEnabled=0"
  assert signature == cli.settings_signature(
    "0123456789abcdef",
    "nrdr-development",
    dict(reversed(list(settings.items()))),
  )
  assert signature != cli.settings_signature("abcdef0123456789", "nrdr-development", settings)
  assert signature != cli.settings_signature(
    "0123456789abcdef",
    "nrdr-development",
    {**settings, "NrdrNnlcEnabled": "1"},
  )


def test_param_decode_captures_historical_sr_and_learner_settings():
  entries = [
    SimpleNamespace(key="NrdrLearnAngleOffset", value=b"0"),
    SimpleNamespace(key="NrdrLearnStiffness", value=b"1"),
    SimpleNamespace(key="NrdrSteerRatioMin", value=b"1500"),
    SimpleNamespace(key="NrdrCurvServo", value=b"1"),
    SimpleNamespace(key="UnrelatedParam", value=b"ignored"),
  ]
  assert cli.decode_param_map(entries) == {
    "NrdrLearnAngleOffset": "0",
    "NrdrLearnStiffness": "1",
    "NrdrSteerRatioMin": "1500",
    "NrdrCurvServo": "1",
  }


def test_default_route_context_is_not_ready_for_sampling():
  context = cli.RouteContext()
  assert context.fingerprint == "UNKNOWN"
  assert context.commit == "unknown"


def test_make_sample_carries_fingerprint_settings_quality_and_tracking_cancel():
  context = cli.RouteContext(
    fingerprint="HONDA_CLARITY",
    wheelbase_m=2.75,
    mass_kg=1600.0,
    center_to_front_m=1.2,
    tire_stiffness_front=100_000.0,
    tire_stiffness_rear=100_000.0,
    commit="0123456789abcdef",
    branch="nrdr-development",
    settings={"NrdrLearnSteerRatio": "1"},
  )
  command = CommandSample(
    timestamp=10.0,
    desired_curvature=0.01,
    desired_angle_deg=-18.0,
    angle_offset_deg=2.0,
    lat_active=True,
  )
  vehicle = VehicleSample(
    timestamp=10.3,
    speed_mps=10.0,
    actual_angle_deg=-14.0,
    angle_offset_deg=2.0,
    geometry_angle_offset_deg=1.0,
    steering_rate_deg_s=0.0,
    steering_pressed=False,
    yaw_rate_rad_s=0.08,
  )

  result = cli.make_sample("route-a", context, command, vehicle, "strict")
  assert result is not None
  assert result.correction_factor == pytest.approx(1.0)
  assert result.tracking_ratio == pytest.approx(0.8)
  assert result.actual_angle_deg == -16.0
  assert result.angle_deg == 15.0
  assert result.fingerprint == "HONDA_CLARITY"
  assert result.software_id == context.signature
  assert result.quality == "strict"


def test_make_sample_uses_learned_geometry_even_when_application_toggles_are_off(monkeypatch):
  seen = {}

  def capture_ratio(steering_angle_deg, *_args):
    seen["angle"] = steering_angle_deg
    seen["stiffness"] = _args[3]
    return 18.0

  monkeypatch.setattr(cli, "model_effective_ratio", capture_ratio)
  context = cli.RouteContext(
    fingerprint="HONDA_CLARITY",
    wheelbase_m=2.75,
    mass_kg=1600.0,
    center_to_front_m=1.2,
    tire_stiffness_front=100_000.0,
    tire_stiffness_rear=100_000.0,
    settings={"NrdrLearnAngleOffset": "0", "NrdrLearnStiffness": "0"},
  )
  command = CommandSample(
    timestamp=10.0,
    desired_curvature=-0.01,
    desired_angle_deg=23.0,
    angle_offset_deg=3.0,
    lat_active=True,
  )
  vehicle = VehicleSample(
    timestamp=10.3,
    speed_mps=10.0,
    actual_angle_deg=23.0,
    angle_offset_deg=3.0,
    geometry_angle_offset_deg=1.0,
    stiffness_factor=1.25,
    steering_rate_deg_s=0.0,
    steering_pressed=False,
    yaw_rate_rad_s=-0.10,
  )

  result = cli.make_sample("route-a", context, command, vehicle, "strict")

  assert result is not None
  assert result.tracking_ratio == pytest.approx(1.0)
  assert result.angle_deg == pytest.approx(22.0)
  assert seen["angle"] == pytest.approx(22.0)
  assert seen["stiffness"] == pytest.approx(1.25)


def test_scan_requires_half_second_continuous_steady_dwell_for_strict(tmp_path, monkeypatch):
  class FakePose:
    @staticmethod
    def from_live_pose(live_pose):
      return live_pose

  class FakePoseCalibrator:
    calib_valid = True

    def feed_live_calib(self, _calibration):
      pass

    def build_calibrated_pose(self, live_pose):
      return SimpleNamespace(angular_velocity=SimpleNamespace(z=live_pose.yaw_rate, z_std=0.01))

  fake_cereal = ModuleType("openpilot.cereal")
  fake_cereal.log = SimpleNamespace(LaneChangeState=SimpleNamespace(off=0))
  fake_helpers = ModuleType("openpilot.selfdrive.locationd.helpers")
  fake_helpers.Pose = FakePose
  fake_helpers.PoseCalibrator = FakePoseCalibrator
  monkeypatch.setitem(sys.modules, "openpilot.cereal", fake_cereal)
  monkeypatch.setitem(sys.modules, "openpilot.selfdrive.locationd.helpers", fake_helpers)

  def event(name, timestamp, value):
    item = SimpleNamespace(logMonoTime=round(timestamp * 1e9), valid=True)
    item.which = lambda: name
    setattr(item, name, value)
    return item

  events = [
    event("initData", 9.0, SimpleNamespace(
      gitSrcCommit="0123456789abcdef",
      gitCommit="",
      gitBranch="nrdr-development",
      params=SimpleNamespace(entries=[]),
    )),
    event("carParams", 9.0, SimpleNamespace(
      carFingerprint="HONDA_CLARITY",
      wheelbase=2.75,
      mass=1600.0,
      centerToFront=1.2,
      tireStiffnessFront=100_000.0,
      tireStiffnessRear=100_000.0,
      steerActuatorDelay=0.1,
      carFw=[],
    )),
  ]
  steady_times = (10.02, 10.12, 10.22, 10.32, 10.42, 10.51, 10.53)
  for timestamp, steering_rate in ((10.0, 2.0), *((value, 0.0) for value in steady_times)):
    events.extend((
      event("liveParameters", timestamp, SimpleNamespace(
        valid=True,
        angleOffsetValid=True,
        angleOffsetAverageValid=True,
        stiffnessFactorValid=True,
        angleOffsetDeg=0.0,
        angleOffsetAverageDeg=0.0,
        roll=0.0,
        stiffnessFactor=1.0,
      )),
      event("carState", timestamp, SimpleNamespace(
        vEgo=10.0,
        aEgo=0.0,
        steeringAngleDeg=-20.0,
        steeringRateDeg=steering_rate,
        steeringTorque=0.5,
        steeringPressed=False,
        gearShifter="drive",
        leftBlinker=False,
        rightBlinker=False,
        steerFaultTemporary=False,
        steerFaultPermanent=False,
      )),
      event("carControl", timestamp, SimpleNamespace(
        latActive=True,
        actuators=SimpleNamespace(curvature=0.01, steeringAngleDeg=-20.0, torque=0.5),
      )),
      event("carOutput", timestamp, SimpleNamespace(
        actuatorsOutput=SimpleNamespace(torque=0.5),
      )),
      event("livePose", timestamp, SimpleNamespace(
        yaw_rate=0.1,
        inputsOK=True,
        posenetOK=True,
        sensorsOK=True,
        angularVelocityDevice=SimpleNamespace(valid=True),
      )),
    ))

  source = tmp_path / "route-a--0" / "rlog.zst"
  monkeypatch.setattr(cli, "iter_local_events", lambda _source: iter(events))

  result = cli.scan_sources([str(source)], 5.0, 0.0, 0.02, 100)

  assert [value.phase for value in result.samples] == ["unwind", *("steady" for _ in steady_times)]
  assert [value.quality for value in result.samples] == [*("relaxed" for _ in range(7)), "strict"]


def test_manual_steady_scan_is_mapping_only_without_commands_or_output(tmp_path, monkeypatch):
  install_fake_scan_dependencies(monkeypatch)
  events = scan_setup_events()
  for index in range(9):
    events.extend(manual_scan_frame(10.0 + index / 10.0))
  monkeypatch.setattr(cli, "iter_local_events", lambda _source: iter(events))

  source = tmp_path / "route-a--0" / "rlog.zst"
  result = cli.scan_sources([str(source)], 5.0, 0.0, 0.02, 100)

  assert result.files_read == 1
  assert result.files_failed == 0
  assert result.samples == []
  assert result.experimental_samples == []
  assert len(result.manual_mapping_samples) == 9
  assert all(sample.dwell_duration_s == pytest.approx(0.8) for sample in result.manual_mapping_samples)
  assert all(sample.bias_corrected_effective_ratio == pytest.approx(sample.effective_ratio)
             for sample in result.manual_mapping_samples)
  assert {sample.bias_source for sample in result.manual_mapping_samples} == {"none"}

  mapping_rows = cli.write_manual_mapping(
    tmp_path / "manual-mapping.csv", result.manual_mapping_samples, 5.0,
  )
  strict_rows = cli.write_headline(tmp_path / "strict.csv", result.samples, 5.0)
  command_rows = cli.write_command_correction(tmp_path / "command.csv", result.samples, 5.0)
  assert len(mapping_rows) == 1
  assert mapping_rows[0]["evidence_status"] == "insufficient for curve change"
  assert strict_rows == []
  assert command_rows == []


def test_manual_dwell_ids_are_unique_across_source_files(tmp_path, monkeypatch):
  install_fake_scan_dependencies(monkeypatch)
  sources = [
    tmp_path / "route-a--0" / "rlog.zst",
    tmp_path / "route-a--1" / "rlog.zst",
  ]
  events_by_source = {}
  for source_index, source in enumerate(sources):
    events = scan_setup_events()
    for frame_index in range(9):
      events.extend(manual_scan_frame(10.0 * (source_index + 1) + frame_index / 10.0))
    events_by_source[str(source)] = events
  monkeypatch.setattr(cli, "iter_local_events", lambda source: iter(events_by_source[source]))

  result = cli.scan_sources([str(source) for source in sources], 5.0, 0.0, 0.02, 100)

  by_dwell = {}
  for sample in result.manual_mapping_samples:
    by_dwell.setdefault(sample.dwell_id, []).append(sample)
  assert set(by_dwell) == {0, 1}
  assert [len(by_dwell[dwell_id]) for dwell_id in sorted(by_dwell)] == [9, 9]
  assert all(len({sample.dwell_duration_s for sample in dwell}) == 1 for dwell in by_dwell.values())


def test_unknown_fingerprint_never_enters_manual_mapping(tmp_path, monkeypatch):
  install_fake_scan_dependencies(monkeypatch)
  events = scan_setup_events(fingerprint="UNKNOWN")
  for index in range(9):
    events.extend(manual_scan_frame(10.0 + index / 10.0))
  monkeypatch.setattr(cli, "iter_local_events", lambda _source: iter(events))

  source = tmp_path / "route-a--0" / "rlog.zst"
  result = cli.scan_sources([str(source)], 5.0, 0.0, 0.02, 100)

  assert result.files_read == 1
  assert result.manual_mapping_samples == []
  assert result.samples == []


def test_missing_commit_keeps_geometry_mapping_but_not_controller_response(tmp_path, monkeypatch):
  install_fake_scan_dependencies(monkeypatch)
  events = scan_setup_events()[1:]
  for index in range(9):
    events.extend(controller_scan_frame(10.0 + index / 10.0))
  monkeypatch.setattr(cli, "iter_local_events", lambda _source: iter(events))

  source = tmp_path / "route-a--0" / "rlog.zst"
  result = cli.scan_sources([str(source)], 5.0, 0.0, 0.02, 100)

  assert len(result.manual_mapping_samples) == 9
  assert result.samples == []
  assert result.experimental_samples == []


def test_manual_mapping_scanner_uses_learned_geometry_when_application_is_disabled(
  tmp_path, monkeypatch,
):
  install_fake_scan_dependencies(monkeypatch)
  params = (
    SimpleNamespace(key="NrdrLearnAngleOffset", value=b"0"),
    SimpleNamespace(key="NrdrLearnStiffness", value=b"0"),
  )
  events = scan_setup_events(param_entries=params)
  for index in range(9):
    events.extend(manual_scan_frame(10.0 + index / 10.0, average_offset=1.0, stiffness=1.25))
  monkeypatch.setattr(cli, "iter_local_events", lambda _source: iter(events))
  seen = []

  def capture_ratio(angle, _yaw_rate, _speed, _roll, stiffness, *_geometry):
    seen.append((angle, stiffness))
    return 18.0

  monkeypatch.setattr(cli, "model_effective_ratio", capture_ratio)
  source = tmp_path / "route-a--0" / "rlog.zst"

  result = cli.scan_sources([str(source)], 5.0, 0.0, 0.02, 100)

  assert len(result.manual_mapping_samples) == 9
  assert seen[::3] == [(pytest.approx(-21.0), pytest.approx(1.25))] * 9
  assert seen[1::3] == [(pytest.approx(-21.0), pytest.approx(1.25))] * 9
  assert seen[2::3] == [(pytest.approx(-21.0), pytest.approx(1.0))] * 9
  assert all(sample.signed_angle_deg == pytest.approx(-21.0) for sample in result.manual_mapping_samples)


def test_manual_mapping_report_downgrades_speed_dependent_ratio(tmp_path):
  samples = []
  for route_number in range(5):
    for direction, angle in (("left", -10.0), ("right", 10.0)):
      for second in range(6):
        samples.append(mapping_sample(
          route_id=f"route-{route_number}",
          timestamp=float(second),
          speed_mps=4.0,
          signed_angle_deg=angle,
          direction=direction,
          effective_ratio=16.0,
          ratio_per_degree=1.6,
          bias_corrected_angle_deg=angle,
          bias_corrected_effective_ratio=16.0,
        ))
        samples.append(mapping_sample(
          route_id=f"route-{route_number}",
          timestamp=float(second + 10),
          speed_mps=10.0,
          signed_angle_deg=angle,
          direction=direction,
          effective_ratio=20.0,
          ratio_per_degree=2.0,
          bias_corrected_angle_deg=angle,
          bias_corrected_effective_ratio=20.0,
        ))

  row = cli.write_manual_mapping(tmp_path / "manual.csv", samples, 5.0)[0]

  assert row["supported_speed_strata"] == 2
  assert row["speed_strata_spread_percent"] == pytest.approx(200.0 / 9.0)
  assert row["confidence"] == "low"
  assert "speed-strata disagreement" in row["warning"]


def test_manual_center_bias_never_leaks_another_routes_fit_into_one_sided_data():
  samples = []
  true_bias = 0.5
  for bin_index, magnitude in enumerate((7.5, 12.5, 17.5)):
    for second in range(7):
      for direction, true_angle in (("left", -magnitude), ("right", magnitude)):
        signed_angle = true_angle + true_bias
        samples.append(mapping_sample(
          route_id="route-fit",
          timestamp=float(bin_index * 10 + second),
          signed_angle_deg=signed_angle,
          direction=direction,
          effective_ratio=18.0 / magnitude * abs(signed_angle),
          ratio_per_degree=18.0 / magnitude,
          bias_corrected_angle_deg=math.nan,
          bias_corrected_effective_ratio=math.nan,
        ))
  for second in range(9):
    samples.append(mapping_sample(
      route_id="route-one-sided",
      timestamp=float(second),
      signed_angle_deg=-9.5,
      direction="left",
      effective_ratio=17.1,
      ratio_per_degree=1.8,
      bias_corrected_angle_deg=math.nan,
      bias_corrected_effective_ratio=math.nan,
    ))
  result = cli.ScanResult(manual_mapping_samples=samples)

  cli.finalize_manual_mapping(result)

  assert result.manual_applied_bias["route-fit"] == (pytest.approx(true_bias), "route-fit")
  assert result.manual_applied_bias["route-one-sided"] == (0.0, "none")
  fallback = [sample for sample in result.manual_mapping_samples if sample.route_id == "route-one-sided"]
  assert all(sample.bias_source == "none" for sample in fallback)
  assert all(sample.bias_corrected_effective_ratio == pytest.approx(17.1) for sample in fallback)


def test_command_report_never_blends_commits_or_settings(tmp_path):
  samples = [
    sample(route_id="route-a", direction="left", software_id="build-a", correction_factor=1.10),
    sample(route_id="route-b", direction="right", software_id="build-a", correction_factor=1.10),
    sample(route_id="route-c", direction="left", software_id="build-b", correction_factor=0.90),
    sample(route_id="route-d", direction="right", software_id="build-b", correction_factor=0.90),
    sample(route_id="route-e", software_id="ignored-relaxed", quality="relaxed", correction_factor=1.50),
  ]
  output = tmp_path / "command.csv"

  rows = cli.write_command_correction(output, samples, 5.0)
  by_signature = {row["settings_signature"]: row for row in rows}
  assert set(by_signature) == {"build-a", "build-b"}
  assert by_signature["build-a"]["full_correction_percent"] == pytest.approx(10.0)
  assert by_signature["build-b"]["full_correction_percent"] == pytest.approx(-10.0)

  with output.open(newline="", encoding="utf-8") as stream:
    csv_rows = list(csv.DictReader(stream))
  assert {row["settings_signature"] for row in csv_rows} == {"build-a", "build-b"}


def test_command_report_bins_the_requested_angle_not_physical_actual_angle(tmp_path):
  output = tmp_path / "command.csv"
  rows = cli.write_command_correction(output, [sample(
    angle_deg=17.0,
    desired_angle_deg=-24.0,
    actual_angle_deg=-17.0,
    tracking_ratio=17.0 / 24.0,
  )], 5.0)

  assert len(rows) == 1
  assert rows[0]["angle_start_deg"] == 20.0
  assert rows[0]["angle_end_deg"] == 25.0


def test_detail_report_keeps_direction_speed_and_phase_cells_distinct(tmp_path):
  output = tmp_path / "detail.csv"
  cli.write_detail(output, [
    sample(direction="left", speed_mps=10.0, phase="steady"),
    sample(direction="right", speed_mps=10.0, phase="steady"),
    sample(direction="left", speed_mps=18.0, phase="turn-in"),
  ], 5.0)

  with output.open(newline="", encoding="utf-8") as stream:
    rows = list(csv.DictReader(stream))
  cells = {
    (row["direction"], row["phase"], float(row["speed_start_mps"]), float(row["speed_end_mps"]))
    for row in rows
  }
  assert cells == {
    ("left", "steady", 7.0, 12.0),
    ("right", "steady", 7.0, 12.0),
    ("left", "turn-in", 18.0, 25.0),
  }


def test_headline_confidence_requires_speed_strata_to_agree(tmp_path):
  samples = []
  for route_number in range(5):
    for direction in ("left", "right"):
      for second in range(6):
        low_speed = second < 3
        samples.append(sample(
          route_id=f"route-{route_number}",
          timestamp=float(second),
          direction=direction,
          speed_mps=5.0 if low_speed else 25.0,
          effective_ratio=10.0 if low_speed else 20.0,
          required_angle_deg=20.0,
        ))

  disagreeing = cli.write_headline(tmp_path / "disagreeing.csv", samples, 5.0)[0]
  assert disagreeing["supported_speed_strata"] == 2
  assert disagreeing["speed_strata_spread_percent"] == pytest.approx(200.0 / 3.0)
  assert disagreeing["confidence"] == "low"

  agreeing_samples = [replace(value, effective_ratio=15.0) for value in samples]
  agreeing = cli.write_headline(tmp_path / "agreeing.csv", agreeing_samples, 5.0)[0]
  assert agreeing["supported_speed_strata"] == 2
  assert agreeing["speed_strata_spread_percent"] == pytest.approx(0.0)
  assert agreeing["confidence"] == "high"


def test_headline_downgrades_confidence_when_speed_strata_disagree(tmp_path):
  samples = []
  for route_index in range(5):
    for second in range(6):
      for direction in ("left", "right"):
        samples.append(sample(
          route_id=f"route-{route_index}",
          timestamp=float(second),
          speed_mps=10.0,
          direction=direction,
          effective_ratio=10.0,
        ))
        samples.append(sample(
          route_id=f"route-{route_index}",
          timestamp=float(second + 10),
          speed_mps=20.0,
          direction=direction,
          effective_ratio=20.0,
        ))

  rows = cli.write_headline(tmp_path / "headline.csv", samples, 5.0)

  assert len(rows) == 1
  assert rows[0]["supported_speed_strata"] == 2
  assert rows[0]["speed_strata_spread_percent"] == pytest.approx(200.0 / 3.0)
  assert rows[0]["confidence"] == "low"


def test_empty_scan_writes_truthful_no_correction_report_without_touching_source(tmp_path, monkeypatch):
  source = tmp_path / "rlog.zst"
  source.write_bytes(b"not read because scan is mocked")
  original = source.read_bytes()
  output = tmp_path / "analysis"
  empty = cli.ScanResult(files_read=1)
  empty.routes.add("route-a")
  monkeypatch.setattr(cli, "scan_sources", lambda *_args, **_kwargs: empty)

  assert cli.main([str(source), "--output-dir", str(output)]) == 0
  assert source.read_bytes() == original

  report = (output / "sr_report.txt").read_text(encoding="utf-8")
  summary = json.loads((output / "sr_summary.json").read_text(encoding="utf-8"))
  assert "accepted relaxed/strict samples: 0" in report
  assert "headline rows: 0" in report
  assert summary["accepted_samples"] == 0
  assert summary["strict_angle_coverage"] == []
  assert summary["command_correction"] == []
  assert (output / "sr_command_correction.csv").read_text(encoding="utf-8") == ""


def test_empty_sample_write_replaces_stale_gzip_output(tmp_path):
  output = tmp_path / "samples.csv.gz"
  output.write_bytes(b"stale output from an earlier forced run")

  cli.write_samples(output, [])

  with gzip.open(output, "rt", encoding="utf-8") as stream:
    assert stream.read() == ""


def test_experimental_missing_delay_pairs_are_json_null_not_report_failure(tmp_path, monkeypatch):
  source = tmp_path / "rlog.zst"
  source.write_bytes(b"not read because scan is mocked")
  output = tmp_path / "analysis"
  result = cli.ScanResult(files_read=1)
  result.routes.add("route-a")
  result.experimental_samples.append(sample(
    phase="turn-in",
    quality="experimental-transient",
    factor_delay_minus_100ms=math.nan,
    factor_delay_plus_100ms=math.nan,
  ))
  monkeypatch.setattr(cli, "scan_sources", lambda *_args, **_kwargs: result)

  assert cli.main([str(source), "--output-dir", str(output)]) == 0
  summary = json.loads((output / "sr_summary.json").read_text(encoding="utf-8"))
  transient = summary["experimental_transient"][0]
  assert transient["minus_100ms_factor_median"] is None
  assert transient["plus_100ms_factor_median"] is None
  assert transient["median_200ms_sensitivity_points"] is None
