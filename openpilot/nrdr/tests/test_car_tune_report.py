import struct
import unittest
from types import SimpleNamespace

from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.nrdr.features.lateral.steer_ratio_tuning import resolve_steer_ratio_selection
from openpilot.nrdr.features.services.car_tune_report import CarTuneReporter, _longitudinal_pid_info


class TestCarTuneReporter(unittest.TestCase):

  @staticmethod
  def _interpolated_reporter(enabled):
    values = {
      "NrdrInterpolatedTorqueShare": "60",
      "NrdrInterpolatedTorqueLatAccelFactor": "5.0",
      "NrdrInterpolatedTorqueFriction": "0.50",
      "NrdrInterpolatedTorqueFrictionStandard": "0.30",
      "NrdrInterpolatedTorqueFrictionHighway": "0.12",
    }
    params = SimpleNamespace(
      get_bool=lambda key: enabled if key == "NrdrInterpolatedTorquePifBlend" else False,
      get=lambda key, **_kwargs: values.get(key),
    )
    reporter = CarTuneReporter(params)
    reporter._cp_sp = lambda: SimpleNamespace(flags=HondaFlagsSP.EPS_MODIFIED.value)
    return reporter

  @staticmethod
  def _interpolated_cp():
    return SimpleNamespace(
      brand="honda",
      carFingerprint="HONDA_CIVIC",
      lateralTuning=SimpleNamespace(which=lambda: "pid"),
    )

  @staticmethod
  def _steer_ratio_selection(mode, fingerprint="HONDA_CLARITY", brand="honda"):
    CP = SimpleNamespace(brand=brand, carFingerprint=fingerprint, steerRatio=16.5, carFw=[])
    return resolve_steer_ratio_selection(CP, {
      "NrdrSteerRatioMode": mode,
      "NrdrSteerRatioManualCenter": 15.38,
      "NrdrSteerRatioManualFinal": 10.93,
    })

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

  def test_disabled_interpolated_report_is_explicitly_unchanged_pif(self):
    report, effective = self._interpolated_reporter(False)._interpolated_torque_pif_info(self._interpolated_cp())

    self.assertFalse(effective)
    self.assertIn("OFF | Torque 0% / P/I/F 100% | P/I/F unchanged", report)
    self.assertIn("stored next engagement: Torque 60% / P/I/F 40%", report)

  def test_enabled_interpolated_report_uses_complementary_share(self):
    report, effective = self._interpolated_reporter(True)._interpolated_torque_pif_info(self._interpolated_cp())

    self.assertTrue(effective)
    self.assertIn("ON | Torque 60% / P/I/F 40%", report)
    self.assertIn("LAF 5 m/s² | friction Low 0.5 / Standard 0.3 / Highway 0.12 | P/I/F angle feedback", report)
    self.assertIn("Torque angle→yaw 2-5 m/s, calibrated yaw >=5 m/s", report)
    self.assertIn("invalid required yaw: exact P/I/F output + Torque state held", report)
    self.assertIn("generic f13 yaw branch (not Honda road-proven)", report)
    self.assertIn("engagement-latched | NNLC bypassed/reset", report)

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

  def test_steer_ratio_report_names_selected_and_effective_manual_geometry(self):
    report = CarTuneReporter._steer_ratio_info(self._steer_ratio_selection(0))

    self.assertIn("selected Manual override | effective Manual override", report)
    self.assertIn("15.38 center -> 10.93 final by 250 deg", report)
    self.assertIn("no lane fade", report)

  def test_steer_ratio_report_exposes_raw_provenance_and_clamped_tail(self):
    report = CarTuneReporter._steer_ratio_info(self._steer_ratio_selection(2))

    self.assertIn("selected NRDR measured-angle curve | effective NRDR measured-angle curve", report)
    self.assertIn("audited near-lock anchor 435.7 deg (VM ratio 14.165673), endpoint-clamped", report)
    self.assertIn("54f74ae3e5973aa681904780f8cac140870a2b5f", report)
    self.assertIn("8a96cab2b8d5fcfa055709e997bea38e3f5724b0", report)

  def test_steer_ratio_report_makes_unsupported_mode_fallback_explicit(self):
    report = CarTuneReporter._steer_ratio_info(self._steer_ratio_selection(2, "HONDA_CIVIC_BOSCH"))

    self.assertIn("selected NRDR measured-angle curve | effective Stock car ratio (safe fallback)", report)
    self.assertIn("No exact audited NRDR raw curve exists", report)
    self.assertIn("CP 16.5", report)


if __name__ == "__main__":
  unittest.main()
