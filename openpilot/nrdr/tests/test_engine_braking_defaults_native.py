"""Real Params integration; every write stays in a pytest temporary directory."""
import ast
from pathlib import Path
import sys
from types import SimpleNamespace as NS

import pytest

from openpilot.nrdr.params import vehicle_defaults
from openpilot.nrdr.params.generate import repository_errors
from openpilot.nrdr.params.snapshots import CONTROL_GROUPS, LiveParams
from openpilot.nrdr.params.vehicle_defaults import initialize_engine_braking_default
from openpilot.nrdr.tests.test_engine_braking_defaults import KEY, ROOT, vehicle


pytestmark = pytest.mark.skipif(sys.platform != "linux", reason="Requires the built Linux native Params library")


def file_version(path):
  stat = path.stat()
  return stat.st_ino, stat.st_mtime_ns, stat.st_size


@pytest.fixture
def params(tmp_path, monkeypatch):
  from openpilot.common.params import Params

  monkeypatch.setenv("OPENPILOT_PREFIX", "engine_default_test")
  store = tmp_path / "params"
  result = Params(str(store))  # Never Params() or the device's live store.
  assert Path(result.get_param_path()).resolve().is_relative_to(tmp_path.resolve())
  return result


def manager_seed(params):
  """Run the actual generic manager loop, restricted to this native registry key."""
  tree = ast.parse((ROOT / "openpilot/system/manager/manager.py").read_text())
  loop = next(node for node in ast.walk(tree) if isinstance(node, ast.For) and ast.unparse(node.iter) == "params.all_keys()")
  only_engine = NS(all_keys=lambda: [KEY], get_default_value=params.get_default_value, get=params.get, put=params.put)
  exec(compile(ast.Module(body=[loop], type_ignores=[]), "manager-default-loop", "exec"), {"params": only_engine})


def test_generated_and_native_registry_defer_global_seed(params):
  assert not repository_errors()
  assert params.get_default_value(KEY) is None, "Rebuild native Params after regenerating the registry"
  assert params.get_raw(KEY) is None
  assert params.get(KEY, return_default=True) is None
  assert params.get_bool(KEY) is False
  manager_seed(params)
  assert params.get_raw(KEY) is None
  for cp, sp in (vehicle(carFingerprint="HONDA_CLARITY"), vehicle(enableGasInterceptor=True),
                 vehicle(openpilotLongitudinalControl=False)):
    assert not initialize_engine_braking_default(cp, sp, params)
    manager_seed(params)
    assert params.get_raw(KEY) is None


def test_native_roundtrip_live_off_and_lifecycle_preservation(params):
  from openpilot.common.params import Params, ParamKeyFlag

  others = {"NrdrHondaPcmMode": 1, "NrdrCruiseOverspeedAllowance": 10, "HondaEnforceStockLongitudinal": False,
            "NrdrClearDashFaults": True}
  for key, value in others.items():
    params.put(key, value, block=True)
  before = {key: params.get_raw(key) for key in others}
  assert initialize_engine_braking_default(*vehicle(), params)
  reader = Params(params.d)
  assert reader.get_raw(KEY) == b"1" and reader.get_bool(KEY) is True
  assert not initialize_engine_braking_default(*vehicle(), reader)
  manager_seed(reader)
  assert reader.get_bool(KEY) is True
  live = LiveParams(CONTROL_GROUPS, params=reader, start_worker=False)
  try:
    assert live.snapshot.get_bool(KEY) is True
    for saved in (False, True, False):
      params.put_bool(KEY, saved, block=True)
      stamp = file_version(Path(params.get_param_path(KEY)))
      assert not initialize_engine_braking_default(*vehicle(), reader)
      manager_seed(reader)
      for _ in CONTROL_GROUPS:
        live.poll_once()
      assert live.snapshot.get_bool(KEY) is saved
      assert reader.get_raw(KEY) == (b"1" if saved else b"0")
      assert file_version(Path(params.get_param_path(KEY))) == stamp
    for flag in (ParamKeyFlag.CLEAR_ON_MANAGER_START, ParamKeyFlag.CLEAR_ON_ONROAD_TRANSITION,
                 ParamKeyFlag.CLEAR_ON_OFFROAD_TRANSITION, ParamKeyFlag.CLEAR_ON_IGNITION_ON):
      params.clear_all(flag)
      assert params.get_raw(KEY) == b"0"
    assert {key: params.get_raw(key) for key in others} == before
  finally:
    live.close()


@pytest.mark.parametrize("raw", [b"", b"0", b"1", b"garbage"])
def test_native_raw_presence_preserves_empty_malformed_and_saved_choices(params, raw):
  path = Path(params.get_param_path(KEY))
  path.write_bytes(raw)
  before = file_version(path)
  assert not initialize_engine_braking_default(*vehicle(), params)
  assert params.get_raw(KEY) == raw
  assert file_version(path) == before


@pytest.mark.parametrize("when", ["before", "after"])
def test_concurrent_native_saved_off_wins_on_either_side_of_atomic_publication(params, monkeypatch, when):
  from openpilot.common.params import Params

  owner = Params(params.d)
  link = vehicle_defaults.os.link

  def save_off(source, destination):
    if when == "before":
      owner.put_bool(KEY, False, block=True)
    link(source, destination)
    if when == "after":
      owner.put_bool(KEY, False, block=True)

  monkeypatch.setattr(vehicle_defaults.os, "link", save_off)
  assert initialize_engine_braking_default(*vehicle(), params) == (when == "after")
  assert owner.get_raw(KEY) == params.get_raw(KEY) == b"0"
  assert not list(Path(params.get_param_path()).glob(".nrdr-engine-default-*"))
