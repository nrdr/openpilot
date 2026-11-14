"""Model-family gating is independent of the saved lane-change preference."""
import ast
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace

import pytest

from openpilot.nrdr.features.lateral import lane_change_tuning as tuning


@pytest.mark.parametrize("family", sorted(tuning.OPTIMIZED_MODEL_FAMILIES))
@pytest.mark.parametrize("stored", [False, True])
def test_world_and_older_families_accept_catalog_and_saved_metadata(family, stored):
  overrides = [{"key": "folder", "value": family}] if stored else {"folder": family}
  assert tuning.model_supports_optimized_lane_changes({"generation": 12, "overrides": overrides})


@pytest.mark.parametrize("ref", sorted(tuning.OPTIMIZED_MODEL_REFS))
def test_older_release_and_master_models_are_identified_by_ref(ref):
  assert tuning.model_supports_optimized_lane_changes({"ref": ref, "overrides": {"folder": "Master Models"}})


@pytest.mark.parametrize("name", ["TSFDOM", "CHEDDAR", "MRLV2"])
def test_deep_rl_does_not_share_world_gate_despite_same_generation(name):
  assert not tuning.model_supports_optimized_lane_changes({
    "internalName": name, "generation": 12, "overrides": [{"key": "folder", "value": "2026 Deep RL Models"}],
  })


def test_big_and_unknown_models_are_not_admitted():
  world = {"ref": next(iter(tuning.OPTIMIZED_MODEL_REFS)), "overrides": {"folder": "2026 World Models"}}
  assert not tuning.model_supports_optimized_lane_changes(world, chestnut=True)
  assert not tuning.model_supports_optimized_lane_changes({**world, "is_big": True})
  assert not tuning.model_supports_optimized_lane_changes({"ref": "unknown", "generation": 12})
  assert tuning.model_supports_optimized_lane_changes(None)  # Current stock small model is CD210.
  assert not tuning.model_supports_optimized_lane_changes(None, chestnut=True)


@pytest.mark.parametrize("supported", [False, True])
@pytest.mark.parametrize("enabled", [False, True])
def test_gate_covers_all_adjustments_without_editing_preference(monkeypatch, supported, enabled):
  monkeypatch.setattr(tuning, "active_model_supports_optimized_lane_changes", lambda: supported)
  settings = {"NrdrOptimizedLaneChanges": enabled}
  expected = tuning.OPTIMIZED_VALUES if supported and enabled else tuning.BASELINE_VALUES
  for key, value in expected.items():
    assert tuning.bounded_setting(settings, key, -1, -1, 100) == value
  for state in range(4):
    assert tuning.optimized_lane_change_active(settings, SimpleNamespace(raw=state)) == (supported and enabled and state in (2, 3))
  entry = tuning.LaneChangeEntry()
  values = [entry.update(active=True, valid=True, state=2, direction=1, driver_override=False, settings=settings, dt=.01)
            for _ in range(20)]
  assert (max(values) > 0) == (supported and enabled)
  assert settings == {"NrdrOptimizedLaneChanges": enabled}


def test_model_identity_is_read_once_per_process_not_per_control_frame(monkeypatch):
  calls = []
  params = ModuleType("openpilot.common.params")
  params.Params = lambda: SimpleNamespace(get=lambda key: calls.append(key) or {
    "overrides": [{"key": "folder", "value": "2026 Deep RL Models"}],
  })
  helpers = ModuleType("openpilot.selfdrive.modeld.helpers")
  helpers.chestnut_present = lambda: calls.append("usb") or False
  monkeypatch.setitem(sys.modules, params.__name__, params)
  monkeypatch.setitem(sys.modules, helpers.__name__, helpers)
  tuning.active_model_supports_optimized_lane_changes.cache_clear()
  try:
    for _ in range(100):
      assert not tuning.optimized_lane_changes_enabled({"NrdrOptimizedLaneChanges": True})
    assert calls == ["ModelManager_ActiveBundle", "usb"]
  finally:
    tuning.active_model_supports_optimized_lane_changes.cache_clear()


def test_model_gate_is_warmed_during_live_parameter_initialization():
  path = Path(__file__).resolve().parents[3] / "openpilot/nrdr/params/snapshots.py"
  tree = ast.parse(path.read_text())
  method = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "get_live_params")
  source = ast.unparse(method)
  assert source.index("active_model_supports_optimized_lane_changes()") < source.index("LiveParams(groups)")
