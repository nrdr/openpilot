"""Portable contract checks. The standalone companion uses actual native Params."""

from pathlib import Path

from openpilot.nrdr.tools import check_lane_guidance_native as checks


class FileParams:
  """Raw files plus typed/defaulting reads; no native library or device needed."""
  KEYS = {"LaneGuidanceMode": 2, "LaneCentering": 1, "IsMetric": 1, "HondaWindFactorParams": 3}

  def __init__(self, root):
    self.root = Path(root)
    namespace = {"Path": Path}
    checks.load_definitions("common/params.py", {"get_raw"}, namespace)
    self._raw_read = namespace["get_raw"]

  def check_key(self, key):
    if isinstance(key, bytes):
      key = key.decode()
    if key not in self.KEYS:
      raise KeyError(key)
    return key

  def get_param_path(self, key=""):
    return str(self.root / key)

  def get_raw(self, key):
    return self._raw_read(self, key)

  def get_type(self, key):
    return self.KEYS[key]

  def get_default_value(self, key):
    return 2 if key == "LaneGuidanceMode" else None

  def get(self, key, return_default=False):
    raw = self.get_raw(key)
    default = self.get_default_value(key) if return_default else None
    if not raw:
      return default
    try:
      if self.KEYS[key] == 1:
        return raw == b"1"
      return int(raw) if self.KEYS[key] == 2 else float(raw)
    except ValueError:
      return default

  def put(self, key, value, block=False):
    assert block
    key = self.check_key(key)
    encoded = str(int(value) if type(value) is bool else value).encode()
    (self.root / key).write_bytes(encoded)

  def put_bool(self, key, value, block=False):
    self.put(key, bool(value), block=block)

  def all_keys(self, _flag):
    return [key.encode() for key in self.KEYS if key != "HondaWindFactorParams"]


class TestLaneGuidanceFailsafe(checks.LaneGuidanceFailsafeChecks):
  @staticmethod
  def make_params(root):
    return FileParams(root)
