import struct
import unittest
from types import SimpleNamespace

from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.sunnypilot.nrdr.car_tune_report import CarTuneReporter, _longitudinal_pid_info


class TestCarTuneReporter(unittest.TestCase):

  class FakeParams:
    def __init__(self, values):
      self.values = values

    def get(self, key, return_default=False):
      return self.values.get(key)

    def get_bool(self, key):
      return bool(self.values.get(key, False))

  def test_raw_mode_requires_exact_honda_brand_and_clarity_fingerprint(self):
    reporter = CarTuneReporter(self.FakeParams({"NrdrSteerRatioMode": 2}))
    malformed = SimpleNamespace(brand="toyota", carFingerprint="HONDA_CLARITY", steerRatio=16.5)

    self.assertEqual(
      reporter._steer_ratio_info(malformed),
      "NRDR Raw unavailable for HONDA_CLARITY -> CP static 16.5",
    )

  def test_raw_mode_reports_full_lock_anchor_domain_conversion_and_support(self):
    reporter = CarTuneReporter(self.FakeParams({"NrdrSteerRatioMode": 2}))
    clarity = SimpleNamespace(
      brand="honda", carFingerprint="HONDA_CLARITY", steerRatio=16.5, carFw=[],
    )

    report = reporter._steer_ratio_info(clarity)
    self.assertIn("original non-monotonic Clarity atan-domain medians preserved", report)
    self.assertIn("bilateral 435.7 deg anchor n=825 L/R=598/227", report)
    self.assertIn("interpolate raw, then VehicleModel conversion", report)
    self.assertIn("effective 247.5=14.870103, 435.7=14.165673", report)
    self.assertIn("clamps at 435.7 deg", report)
    self.assertIn("54f74ae3e5973aa681904780f8cac140870a2b5f", report)
    self.assertIn("8a96cab2b8d5fcfa055709e997bea38e3f5724b0", report)

  def test_static_pid_base_is_reported_for_all_speeds(self):
    pid = SimpleNamespace(kpV=[0.03], kiV=[0.01], kf=0.000012, kfV=[])
    CP = SimpleNamespace(lateralTuning=SimpleNamespace(which=lambda: "pid", pid=pid))

    self.assertEqual(
      CarTuneReporter(params=None)._pid_info(CP),
      ("P 0.03 | I 0.01", "0.000012", "all speeds"),
    )

  def test_mixed_pid_base_reports_feedforward_schedule_separately(self):
    pid = SimpleNamespace(
      kpV=[0.2],
      kiV=[0.05],
      kf=0.0000036,
      kfV=[0.0000024, 0.0000018, 0.0000036, 0.000006],
    )
    CP = SimpleNamespace(lateralTuning=SimpleNamespace(which=lambda: "pid", pid=pid))

    self.assertEqual(
      CarTuneReporter(params=None)._pid_info(CP),
      ("P 0.2 | I 0.05", "0.0000024/0.0000018/0.0000036/0.000006", "P/I all speeds | F 0 / <25 / 25 / 50 mph"),
    )

  def test_small_scalar_feedforward_never_uses_exponent_notation(self):
    pid = SimpleNamespace(kpV=[0.2], kiV=[0.05], kf=0.0000036, kfV=[])
    CP = SimpleNamespace(lateralTuning=SimpleNamespace(which=lambda: "pid", pid=pid))

    self.assertEqual(
      CarTuneReporter(params=None)._pid_info(CP),
      ("P 0.2 | I 0.05", "0.0000036", "all speeds"),
    )

  def test_float32_noise_does_not_leak_into_feedforward_output(self):
    noisy_float32 = struct.unpack("f", struct.pack("f", 0.00006))[0]
    pid = SimpleNamespace(kpV=[0.2], kiV=[0.05], kf=noisy_float32, kfV=[])
    CP = SimpleNamespace(lateralTuning=SimpleNamespace(which=lambda: "pid", pid=pid))

    self.assertEqual(
      CarTuneReporter(params=None)._pid_info(CP),
      ("P 0.2 | I 0.05", "0.00006", "all speeds"),
    )

  def test_zero_feedforward_is_reported_without_exponent_notation(self):
    pid = SimpleNamespace(kpV=[0.2], kiV=[0.05], kf=-0.0, kfV=[])
    CP = SimpleNamespace(lateralTuning=SimpleNamespace(which=lambda: "pid", pid=pid))

    self.assertEqual(
      CarTuneReporter(params=None)._pid_info(CP),
      ("P 0.2 | I 0.05", "0", "all speeds"),
    )

  def test_deprecated_longitudinal_feedforward_uses_decimal_output(self):
    noisy_float32 = struct.unpack("f", struct.pack("f", 0.00006))[0]
    longitudinal = SimpleNamespace(
      deprecated=SimpleNamespace(kpV=[0.4], kf=noisy_float32),
      kiV=[0.05],
    )

    self.assertEqual(_longitudinal_pid_info(longitudinal), "P 0.4 | I 0.05 | F 0.00006")

  def test_interpolated_torque_report_shows_complement_and_locked_values(self):
    reporter = CarTuneReporter(self.FakeParams({
      "NrdrInterpolatedTorquePifBlend": True,
      "NrdrInterpolatedTorqueShare": 35,
      "NrdrInterpolatedTorqueLatAccelFactor": 5.0,
      "NrdrInterpolatedTorqueFriction": 0.12,
      "NrdrInterpolatedTorqueFrictionStandard": 0.34,
      "NrdrInterpolatedTorqueFrictionHighway": 0.56,
    }))
    CP = SimpleNamespace(
      brand="honda",
      carFingerprint="HONDA_CIVIC",
      lateralTuning=SimpleNamespace(which=lambda: "pid"),
    )
    CP_SP = SimpleNamespace(flags=HondaFlagsSP.EPS_MODIFIED.value)

    report = reporter._interpolated_torque_info(CP, CP_SP)
    self.assertIn("ON", report)
    self.assertIn("engagement-latched", report)
    self.assertIn("Torque 35% / P/I/F 65%", report)
    self.assertIn("LAF 5 m/s^2", report)
    self.assertIn("friction Low 0.12 / Standard 0.34 / Highway 0.56", report)
    self.assertIn("learner paused", report)
    self.assertIn("P/I/F angle feedback", report)
    self.assertIn("Torque angle-to-yaw feedback", report)
    self.assertIn("not Honda road-proven", report)
    self.assertIn("required yaw unavailable: exact P/I/F + all Torque state held", report)
    self.assertIn("NNLC bypassed", report)

  def test_interpolated_torque_report_explains_master_off(self):
    reporter = CarTuneReporter(self.FakeParams({"NrdrInterpolatedTorquePifBlend": False}))
    CP = SimpleNamespace(
      brand="honda",
      carFingerprint="HONDA_CIVIC",
      lateralTuning=SimpleNamespace(which=lambda: "pid"),
    )
    CP_SP = SimpleNamespace(flags=HondaFlagsSP.EPS_MODIFIED.value)
    report = reporter._interpolated_torque_info(CP, CP_SP)
    self.assertIn("OFF | Torque 0% / P/I/F 100% | P/I/F unchanged", report)
    self.assertIn("stored next engagement", report)
    self.assertIn("friction Low 0.12 / Standard 0.10 / Highway 0.06", report)

  def test_unavailable_request_reports_effective_pif_and_stored_values(self):
    reporter = CarTuneReporter(self.FakeParams({
      "NrdrInterpolatedTorquePifBlend": True,
      "NrdrInterpolatedTorqueShare": 40,
      "NrdrInterpolatedTorqueLatAccelFactor": 6.0,
      "NrdrInterpolatedTorqueFriction": 0.25,
      "NrdrInterpolatedTorqueFrictionStandard": 0.35,
      "NrdrInterpolatedTorqueFrictionHighway": 0.45,
    }))
    CP = SimpleNamespace(
      brand="honda",
      carFingerprint="HONDA_CIVIC",
      lateralTuning=SimpleNamespace(which=lambda: "pid"),
    )
    report = reporter._interpolated_torque_info(CP, SimpleNamespace(flags=0))
    self.assertIn("requested ON but unavailable", report)
    self.assertIn("Torque 0% / P/I/F 100% | P/I/F unchanged", report)
    self.assertIn(
      "stored: Torque 40% / P/I/F 60% | LAF 6 m/s^2 | friction Low 0.25 / Standard 0.35 / Highway 0.45",
      report,
    )


if __name__ == "__main__":
  unittest.main()
