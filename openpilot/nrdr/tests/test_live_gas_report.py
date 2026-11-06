"""Learner visibility without starting vehicle services or writing settings."""
from __future__ import annotations

import ast
from datetime import UTC, datetime
from pathlib import Path
import unittest

from openpilot.nrdr.car.live_gas_report import GAS_NODES, live_gas_details
from openpilot.nrdr.car.mvl_state import MVL_STATE_KEYS


ROOT = Path(__file__).resolve().parents[3]
NOW = datetime(2026, 11, 5, 17, 30, tzinfo=UTC)


class ReadOnlyParams:
  def __init__(self, values=None):
    self.values = values or {}
    self.reads = []

  def get_raw(self, key):
    self.reads.append(key)
    value = self.values.get(key)
    if isinstance(value, Exception):
      raise value
    return value


class TestLiveGasReport(unittest.TestCase):
  def test_empty_state_is_not_reported_as_trained_or_default_gains(self):
    params = ReadOnlyParams()
    text = live_gas_details(params, now=NOW)
    self.assertIn("Nov 05, 17:30 UTC", text)
    self.assertIn("Training time: not recorded", text)
    self.assertIn("No completion score", text)
    self.assertEqual(text.count("not saved"), 14)
    self.assertNotIn("1 / 0", text)
    self.assertEqual(len(params.reads), len(set(params.reads)))
    self.assertEqual(len(params.reads), 14)

  def test_actual_saved_values_and_band_order(self):
    params = ReadOnlyParams({
      "HondaGasFactor00Params": 1.25, "HondaGasAlpha00Params": -.12,
      "HondaGasFactor10Params": b"1.234567", "HondaGasAlpha10Params": "0.06",
      "HondaGasFactorLowParams": 1.75, "HondaGasAlphaLowParams": .1,
      "HondaGasFactorParams": 2, "HondaGasAlphaParams": -.2,
      "HondaWindFactorParams": 1.4, "HondaFeedForwardParams": .035,
    })
    text = live_gas_details(params, now=NOW)
    self.assertIn("0 mph: 1.25 / -0.12", text)
    self.assertIn("10 mph: 1.235 / 0.06", text)
    self.assertIn("22.4 mph: 1.75 / 0.1", text)
    self.assertIn("35.8+ mph: 2 / -0.2", text)
    self.assertIn("Drag factor: 1.4", text)
    self.assertIn("PCM response coefficient: 0.035", text)
    positions = [text.index(f"{speed} mph:") for _, speed in GAS_NODES]
    self.assertEqual(positions, sorted(positions))
    self.assertIn("may be from another car", text)
    self.assertIn("not PID feedforward", text)
    self.assertIn("Saved values lag driving", text)
    self.assertIn("Full MVL mode ignores custom PCM shaping", text)
    self.assertNotIn("freeze learning", text)
    self.assertIn("Reset clears gas/wind only", text)

  def test_corrupt_values_are_not_echoed_or_presented_as_learned(self):
    for value in (True, False, float("nan"), float("inf"), b"-inf", b"\xff", "<script>alert(1)</script>", {},
                  ValueError("bad stored float")):
      with self.subTest(value=value):
        text = live_gas_details(ReadOnlyParams({"HondaWindFactorParams": value}), now=NOW)
        self.assertIn("Drag factor: invalid", text)
        self.assertNotIn("<script>", text)
        self.assertNotIn("bad stored float", text)

  def test_reads_only_registered_learner_values(self):
    params = ReadOnlyParams()
    live_gas_details(params, now=NOW)
    self.assertTrue(set(params.reads) <= set(MVL_STATE_KEYS.values()))
    self.assertFalse(any(key in params.reads for key in ("CarParamsPersistent", "DongleId", "GitCommit")))

  def test_schema_injection_changes_only_live_gas_details_and_falls_back(self):
    # Run the actual adapter and walker without importing native Params on a PC.
    functions = {}
    for relative, names in (
      ("nrdr/features/services/sunnylink.py", ("inject_live_gas_details",)),
      ("sunnypilot/sunnylink/tools/generate_settings_schema.py", ("_walk_all_items",)),
    ):
      tree = ast.parse((ROOT / "openpilot" / relative).read_text(encoding="utf-8"))
      tree.body = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
      exec(compile(ast.fix_missing_locations(tree), relative, "exec"), functions)
    functions.update(Params=lambda: ReadOnlyParams(), UnknownKeyName=KeyError)
    target = {"key": "HondaLiveLearningGas", "description": "keep", "details": "fallback", "widget": "toggle"}
    other = {"key": "NrdrHondaPcmMode", "details": "keep"}
    schema = {"panels": [{"sections": [{"sub_panels": [{"items": [target, other]}]}]}]}
    functions["inject_live_gas_details"](schema, functions["_walk_all_items"])
    self.assertIn("Saved snapshot", target["details"])
    self.assertEqual(target["description"], "keep")
    self.assertEqual(target["widget"], "toggle")
    self.assertEqual(other, {"key": "NrdrHondaPcmMode", "details": "keep"})
    for error in (OSError("unavailable"), KeyError("unknown")):
      functions["Params"] = lambda error=error: ReadOnlyParams({"HondaGasFactor00Params": error})
      target["details"] = "fallback"
      functions["inject_live_gas_details"](schema, functions["_walk_all_items"])
      self.assertEqual(target["details"], "fallback")


if __name__ == "__main__":
  unittest.main()
