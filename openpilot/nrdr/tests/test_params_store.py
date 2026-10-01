from __future__ import annotations

import unittest

from openpilot.common.params import UnknownKeyName
from openpilot.nrdr.params import NrdrParamKey, ParamReader, read_bool, read_float


class FakeParams:
  def __init__(self, values=None):
    self.values = dict(values or {})

  def get(self, key: str):
    return self.values.get(key)


class UnknownParams:
  def get(self, key: str):
    raise UnknownKeyName(key)


class BrokenParams:
  def get(self, key: str):
    raise RuntimeError(key)


class TestParamStore(unittest.TestCase):
  def test_reader_contract_is_read_only_and_structural(self):
    reader = FakeParams()
    self.assertIsInstance(reader, ParamReader)
    self.assertFalse(hasattr(ParamReader, "put"))
    self.assertFalse(hasattr(ParamReader, "remove"))

  def test_read_bool_accepts_historical_truthy_values(self):
    for value in (True, 1, b"1", b" true ", "yes"):
      with self.subTest(value=value):
        self.assertTrue(read_bool(FakeParams({"Enabled": value}), "Enabled"))

  def test_read_bool_accepts_historical_false_values(self):
    for value in (False, 0, b"", b"0", b" FALSE ", "", "false"):
      with self.subTest(value=value):
        self.assertFalse(read_bool(FakeParams({"Enabled": value}), "Enabled", True))

  def test_read_bool_uses_default_for_missing_and_unknown_keys(self):
    self.assertTrue(read_bool(FakeParams(), "Missing", True))
    self.assertTrue(read_bool(UnknownParams(), "Missing", True))

  def test_generated_keys_are_string_compatible(self):
    params = FakeParams({"HondaLiveLearningGas": b"1"})
    self.assertIsInstance(NrdrParamKey.HONDA_LIVE_LEARNING_GAS, str)
    self.assertTrue(read_bool(params, NrdrParamKey.HONDA_LIVE_LEARNING_GAS))

  def test_read_float_decodes_scales_and_clamps_values(self):
    params = FakeParams({"Bytes": b"125", "Number": 250})
    self.assertEqual(read_float(params, "Bytes", 1.0, scale=100.0), 1.25)
    self.assertEqual(read_float(params, "Number", 1.0, max_value=2.0, scale=100.0), 2.0)
    self.assertEqual(read_float(FakeParams({"Low": -5}), "Low", 1.0, min_value=-2.0), -2.0)

  def test_read_float_uses_default_before_applying_bounds(self):
    params = FakeParams({"Invalid": b"not-a-number"})
    self.assertEqual(read_float(params, "Invalid", 1.5), 1.5)
    self.assertEqual(read_float(params, "Missing", 1.5, min_value=2.0), 2.0)
    self.assertEqual(read_float(UnknownParams(), "Unknown", 3.0, max_value=2.0), 2.0)

  def test_unrelated_reader_errors_are_not_hidden(self):
    with self.assertRaises(RuntimeError):
      read_bool(BrokenParams(), "Broken")
    with self.assertRaises(RuntimeError):
      read_float(BrokenParams(), "Broken", 1.0)
