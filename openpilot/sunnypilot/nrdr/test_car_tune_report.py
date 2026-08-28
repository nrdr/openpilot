import unittest
from types import SimpleNamespace

from openpilot.sunnypilot.nrdr.car_tune_report import CarTuneReporter


class TestCarTuneReporter(unittest.TestCase):

  def test_static_pid_base_is_reported_for_all_speeds(self):
    pid = SimpleNamespace(kpV=[0.03], kiV=[0.01], kf=1.2e-5, kfV=[])
    CP = SimpleNamespace(lateralTuning=SimpleNamespace(which=lambda: "pid", pid=pid))

    self.assertEqual(
      CarTuneReporter(params=None)._pid_info(CP),
      ("P 0.03 | I 0.01", "1.2e-05", "all speeds"),
    )

  def test_mixed_pid_base_reports_feedforward_schedule_separately(self):
    pid = SimpleNamespace(
      kpV=[0.2],
      kiV=[0.05],
      kf=3.6e-6,
      kfV=[2.4e-6, 1.8e-6, 3.6e-6, 6.0e-6],
    )
    CP = SimpleNamespace(lateralTuning=SimpleNamespace(which=lambda: "pid", pid=pid))

    self.assertEqual(
      CarTuneReporter(params=None)._pid_info(CP),
      ("P 0.2 | I 0.05", "2.4/1.8/3.6/6 x10^-6", "P/I all speeds | F 0 / <25 / 25 / 50 mph"),
    )


if __name__ == "__main__":
  unittest.main()
