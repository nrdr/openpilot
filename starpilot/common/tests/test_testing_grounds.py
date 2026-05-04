import json

import pytest

from openpilot.starpilot.common import testing_grounds as tg


@pytest.mark.parametrize("hidden_slot_id", [tg.TESTING_GROUND_5])
def test_hidden_testing_ground_selection_is_migrated(tmp_path, monkeypatch, hidden_slot_id):
  state_path = tmp_path / "slots.json"
  state_path.write_text(json.dumps({
    "schemaVersion": tg.TESTING_GROUNDS_SCHEMA_VERSION,
    "activeSlot": hidden_slot_id,
    "activeVariant": tg.TESTING_GROUND_TEST_VARIANT,
  }), encoding="utf-8")

  monkeypatch.setattr(tg, "TESTING_GROUNDS_STATE_PATH", state_path)
  monkeypatch.setattr(tg, "_CACHE_LAST_REFRESH", 0.0)
  monkeypatch.setattr(tg, "_CACHE_LAST_MTIME_NS", -1)
  monkeypatch.setattr(tg, "_VISIBLE_TESTING_GROUND_IDS", tuple(slot_id for slot_id in tg.TESTING_GROUND_IDS if slot_id != hidden_slot_id))
  monkeypatch.setattr(tg, "_DEFAULT_ACTIVE_SLOT", tg.TESTING_GROUND_1)
  monkeypatch.setattr(tg, "_CACHE_ACTIVE_SLOT", tg._DEFAULT_ACTIVE_SLOT)
  monkeypatch.setattr(tg, "_CACHE_ACTIVE_VARIANT", tg.DEFAULT_TESTING_GROUND_VARIANT)

  active_slot, active_variant = tg.get_testing_ground_selection(refresh_interval_s=0.0)

  assert active_slot == tg.TESTING_GROUND_1
  assert active_variant == tg.DEFAULT_TESTING_GROUND_VARIANT

  payload = json.loads(state_path.read_text(encoding="utf-8"))
  assert payload["activeSlot"] == tg.TESTING_GROUND_1
  assert payload["activeVariant"] == tg.DEFAULT_TESTING_GROUND_VARIANT


def test_hidden_slot_invalid_variant_is_migrated_off_slot(tmp_path, monkeypatch):
  state_path = tmp_path / "slots.json"
  state_path.write_text(json.dumps({
    "schemaVersion": tg.TESTING_GROUNDS_SCHEMA_VERSION,
    "activeSlot": tg.TESTING_GROUND_5,
    "activeVariant": "C",
  }), encoding="utf-8")

  monkeypatch.setattr(tg, "TESTING_GROUNDS_STATE_PATH", state_path)
  monkeypatch.setattr(tg, "_CACHE_LAST_REFRESH", 0.0)
  monkeypatch.setattr(tg, "_CACHE_LAST_MTIME_NS", -1)
  monkeypatch.setattr(tg, "_CACHE_ACTIVE_SLOT", tg._DEFAULT_ACTIVE_SLOT)
  monkeypatch.setattr(tg, "_CACHE_ACTIVE_VARIANT", tg.DEFAULT_TESTING_GROUND_VARIANT)

  active_slot, active_variant = tg.get_testing_ground_selection(refresh_interval_s=0.0)

  assert active_slot == tg.TESTING_GROUND_1
  assert active_variant == tg.DEFAULT_TESTING_GROUND_VARIANT

  payload = json.loads(state_path.read_text(encoding="utf-8"))
  assert payload["activeSlot"] == tg.TESTING_GROUND_1
  assert payload["activeVariant"] == tg.DEFAULT_TESTING_GROUND_VARIANT
