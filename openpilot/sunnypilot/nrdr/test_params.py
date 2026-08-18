from openpilot.sunnypilot.nrdr.params import read_bool, read_float


class FakeParams:
  def __init__(self, values=None):
    self.values = dict(values or {})

  def get(self, key):
    return self.values.get(key)

  def get_bool(self, key):
    return bool(self.values[key])


def test_read_bool_uses_default_for_missing_values():
  params = FakeParams({"Enabled": True, "Disabled": False})
  assert read_bool(params, "Enabled")
  assert not read_bool(params, "Disabled", True)
  assert read_bool(params, "Missing", True)


def test_read_float_decodes_scales_and_bounds_values():
  params = FakeParams({"Bytes": b"125", "Number": 250, "Invalid": b"nope"})
  assert read_float(params, "Bytes", 1.0, scale=100.0) == 1.25
  assert read_float(params, "Number", 1.0, max_value=2.0, scale=100.0) == 2.0
  assert read_float(params, "Invalid", 1.5) == 1.5
  assert read_float(params, "Missing", 1.5, min_value=2.0) == 2.0
