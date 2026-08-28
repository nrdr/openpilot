import struct
import unittest
from types import SimpleNamespace

from openpilot.nrdr.features.services.car_tune_report import CarTuneReporter, _longitudinal_pid_info


class TestCarTuneReporter(unittest.TestCase):

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


if __name__ == "__main__":
  unittest.main()
