import unittest
from pathlib import Path


class TestUiDecimalFeedforward(unittest.TestCase):
  def test_lateral_tuning_routes_all_feedforward_outputs_through_decimal_formatters(self):
    repository_root = Path(__file__).resolve().parents[3]
    source = (
      repository_root / "openpilot/selfdrive/ui/sunnypilot/layouts/settings/nrdr_sub_layouts/lateral_tuning.py"
    ).read_text(encoding="utf-8")

    self.assertIn("self._fmt_decimal_vals(pid.kfV)", source)
    self.assertIn("self._fmt_decimal(pid.kf)", source)
    self.assertIn("self._fmt_decimal(lt_deprecated.kf)", source)
    self.assertNotIn("float(pid.kf):g", source)
    self.assertNotIn("float(lt_deprecated.kf):g", source)


if __name__ == "__main__":
  unittest.main()
