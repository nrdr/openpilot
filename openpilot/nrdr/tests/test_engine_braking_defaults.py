"""Vehicle-admitted defaults must never erase an owner's live saved choice."""
import ast
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace as NS

import pytest

from opendbc.car.honda.values import CAR, HondaFlags
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.nrdr.params.snapshots import CONTROL_GROUPS, LiveParams
from openpilot.nrdr.params.specs import PARAM_SPECS_BY_KEY, ParamFlag
from openpilot.nrdr.params.vehicle_defaults import initialize_engine_braking_default
from openpilot.nrdr.params import vehicle_defaults


KEY = "NrdrExperimentalEngineBraking"
ROOT = Path(__file__).resolve().parents[3]


class Params:
  def __init__(self, raw=None, **values):
    self.folder = TemporaryDirectory()
    self.raw = raw
    self.values = values
    self.writes = []
    self.error = None

  def get_param_path(self, key=""):
    return str(Path(self.folder.name) / key)

  @property
  def raw(self):
    path = Path(self.get_param_path(KEY))
    return path.read_bytes() if path.exists() else None

  @raw.setter
  def raw(self, value):
    path = Path(self.get_param_path(KEY))
    if value is None:
      path.unlink(missing_ok=True)
    else:
      path.write_bytes(value)

  def get_raw(self, key):
    assert key == KEY
    if self.error:
      raise self.error
    return self.raw

  def get(self, key):
    if key == KEY:
      raw = self.get_raw(key)
      return None if raw in (None, b"") else raw == b"1"
    return self.values.get(key)

  def put_bool(self, key, value, *, block=False):
    assert key == KEY
    self.writes.append((key, value, block))
    self.raw = b"1" if value else b"0"


def vehicle(**kwargs):
  cp = NS(brand="honda", carFingerprint=CAR.HONDA_CIVIC, openpilotLongitudinalControl=True, flags=HondaFlags.NIDEC)
  sp = NS(enableGasInterceptor=False, flags=0)
  for key, value in kwargs.items():
    setattr(sp if key == "enableGasInterceptor" else cp, key, value)
  return cp, sp


def test_registry_defers_to_live_admission_without_lifecycle_clears():
  spec = PARAM_SPECS_BY_KEY[KEY]
  assert spec.default is None  # Manager must not turn missing into a saved Off.
  assert spec.flags == (ParamFlag.PERSISTENT, ParamFlag.BACKUP)
  assert KEY not in (ROOT / "openpilot/nrdr/params/defaults.py").read_text()
  assert KEY not in (ROOT / "openpilot/sunnypilot/system/params_migration.py").read_text()


def test_new_eligible_civic_defaults_on_once_without_touching_other_settings():
  params = Params(NrdrHondaPcmMode=1, NrdrCruiseOverspeedAllowance=10, HondaEnforceStockLongitudinal=False,
                  NrdrClearDashFaults=True)
  before = dict(params.values)
  assert initialize_engine_braking_default(*vehicle(), params)
  assert not initialize_engine_braking_default(*vehicle(), params)
  assert params.raw == b"1"
  assert params.values == before
  assert not params.writes  # Initialization must not use the overwriting Params.put API.
  assert sorted(path.name for path in Path(params.get_param_path()).iterdir()) == [KEY]


@pytest.mark.parametrize("raw", [b"0", b"1", b"", b"false", b"true", b"garbage", b"0\n"])
def test_every_present_value_is_preserved_across_repeated_startup(raw):
  params = Params(raw)
  for _ in range(3):
    assert not initialize_engine_braking_default(*vehicle(), params)
  assert params.raw == raw
  assert not params.writes


@pytest.mark.parametrize("car", list(CAR))
def test_missing_choice_only_defaults_for_exact_civic(car):
  params = Params()
  assert initialize_engine_braking_default(*vehicle(carFingerprint=car), params) == (car == CAR.HONDA_CIVIC)
  assert params.raw == (b"1" if car == CAR.HONDA_CIVIC else None)


@pytest.mark.parametrize("overrides", [
  {"brand": "toyota"}, {"carFingerprint": "UNKNOWN"}, {"enableGasInterceptor": True},
  {"openpilotLongitudinalControl": False}, {"flags": HondaFlags.BOSCH},
])
@pytest.mark.parametrize("raw", [None, b"0", b"1"])
def test_ineligible_vehicle_never_seeds_or_resets(overrides, raw):
  params = Params(raw)
  assert not initialize_engine_braking_default(*vehicle(**overrides), params)
  assert params.raw == raw and not params.writes


def test_stock_longitudinal_and_unknown_vehicle_do_not_seed():
  cp, sp = vehicle()
  sp.flags = HondaFlagsSP.STOCK_LONGITUDINAL
  for pair in ((cp, sp), (None, sp), (cp, None)):
    params = Params()
    assert not initialize_engine_braking_default(*pair, params)
    assert params.raw is None and not params.writes


@pytest.mark.parametrize("bundle", [{}, False, "honda", {"brand": "honda"},
  {"brand": "honda", "platform": "HONDA_CLARITY"}, {"brand": "toyota", "platform": "HONDA_CIVIC"}])
def test_conflicting_or_incomplete_selection_does_not_seed(bundle):
  params = Params(CarPlatformBundle=bundle)
  assert not initialize_engine_braking_default(*vehicle(), params)
  assert params.raw is None and not params.writes


def test_matching_selection_allows_default_and_saved_off_still_wins():
  params = Params(CarPlatformBundle={"brand": "honda", "platform": "HONDA_CIVIC"})
  assert initialize_engine_braking_default(*vehicle(), params)
  params.put_bool(KEY, False, block=True)
  writes = list(params.writes)
  assert not initialize_engine_braking_default(*vehicle(), params)
  assert params.raw == b"0" and params.writes == writes


def test_ineligible_first_start_does_not_consume_missing_preference():
  params = Params()
  assert not initialize_engine_braking_default(*vehicle(enableGasInterceptor=True), params)
  assert initialize_engine_braking_default(*vehicle(), params)


@pytest.mark.parametrize("error", [OSError("unreadable store"), PermissionError("denied"), RuntimeError("read failure")])
def test_storage_fault_is_not_a_missing_choice(error):
  params = Params(b"0")
  params.error = error
  with pytest.raises(type(error)):
    initialize_engine_braking_default(*vehicle(), params)
  assert params.raw == b"0" and not params.writes


def test_startup_hook_is_before_cp_publication_and_not_in_the_control_loop():
  tree = ast.parse((ROOT / "openpilot/selfdrive/car/card.py").read_text())
  cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Car")
  init = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "__init__")
  calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and
           isinstance(node.func, ast.Name) and node.func.id == "initialize_engine_braking_default"]
  assert len(calls) == 1 and calls[0] in list(ast.walk(init))
  normal_startup = next(node for node in ast.walk(init) if isinstance(node, ast.If) and ast.unparse(node.test) == "CI is None")
  assert calls[0] in [child for node in normal_startup.body for child in ast.walk(node)]
  publications = [node for node in ast.walk(init) if isinstance(node, ast.Call) and
                  node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value in ("FirmwareQueryDone", "CarParams")]
  assert publications and all(calls[0].lineno < node.lineno for node in publications)


@pytest.mark.parametrize("raw,expected", [(None, False), (b"0", False), (b"1", True)])
def test_live_initial_read_is_not_a_writer_or_an_implicit_on_default(raw, expected):
  params = Params(raw, NrdrCruiseOverspeedAllowance=10)
  live = LiveParams(CONTROL_GROUPS, params=params, start_worker=False)
  assert live.snapshot.get_bool(KEY) is expected
  assert params.raw == raw and not params.writes


def test_live_saved_off_remains_off_and_missing_or_faulted_reads_retain_last_good_value(monkeypatch):
  params = Params(NrdrCruiseOverspeedAllowance=10)
  assert initialize_engine_braking_default(*vehicle(), params)
  live = LiveParams(CONTROL_GROUPS, params=params, start_worker=False)
  monkeypatch.setattr(live, "_warn", lambda *_: None)

  def poll():
    for _ in CONTROL_GROUPS:
      live.poll_once()

  for raw, expected in ((None, True), (b"0", False), (None, False), (b"1", True)):
    params.raw = raw
    poll()
    assert live.snapshot.get_bool(KEY) is expected
  params.error = OSError("temporary read fault")
  poll()
  assert live.snapshot.get_bool(KEY) is True
  params.error = None
  params.raw = b"0"
  poll()
  assert not initialize_engine_braking_default(*vehicle(), params)
  assert live.snapshot.get_bool(KEY) is False
  assert params.raw == b"0" and not params.writes


@pytest.mark.parametrize("saved", [False, True])
def test_concurrent_owner_write_between_missing_read_and_publication_wins(monkeypatch, saved):
  params = Params()
  link = vehicle_defaults.os.link

  def save_before_publication(source, destination):
    params.put_bool(KEY, saved, block=True)
    link(source, destination)

  monkeypatch.setattr(vehicle_defaults.os, "link", save_before_publication)
  assert not initialize_engine_braking_default(*vehicle(), params)
  assert params.raw == (b"1" if saved else b"0")
  assert params.writes == [(KEY, saved, True)]
  assert sorted(path.name for path in Path(params.get_param_path()).iterdir()) == [KEY]


def test_unsupported_atomic_publication_never_falls_back_to_overwriting_put(monkeypatch):
  params = Params()

  def fail(*_):
    raise OSError("hard links unavailable")

  monkeypatch.setattr(vehicle_defaults.os, "link", fail)
  with pytest.raises(OSError):
    initialize_engine_braking_default(*vehicle(), params)
  assert params.raw is None and not params.writes
  assert not list(Path(params.get_param_path()).iterdir())
