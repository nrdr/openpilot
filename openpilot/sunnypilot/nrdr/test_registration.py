from pathlib import Path

import pytest

from openpilot.sunnypilot.nrdr import registration


@pytest.fixture
def identity_store(mocker, tmp_path):
  path = tmp_path / "konik_dongle_id"
  mocker.patch.object(registration, "identity_path", return_value=path)
  mocker.patch.object(registration.Paths, "persist_root", return_value=str(tmp_path))
  return path


def test_durable_identity_wins(mocker, identity_store):
  identity_store.write_text("d7cee79a4d45d4cf")
  validate = mocker.patch.object(registration, "_validate")
  assert registration.resolve("a3cd4e3353309ee9") == "d7cee79a4d45d4cf"
  validate.assert_not_called()


def test_valid_param_identity_is_persisted(mocker, identity_store):
  mocker.patch.object(registration, "_validate", return_value=True)
  assert registration.resolve("d7cee79a4d45d4cf") == "d7cee79a4d45d4cf"
  assert identity_store.read_text() == "d7cee79a4d45d4cf"


def test_network_failure_keeps_param_identity(mocker, identity_store):
  mocker.patch.object(registration, "_validate", return_value=None)
  assert registration.resolve("d7cee79a4d45d4cf") == "d7cee79a4d45d4cf"
  assert not identity_store.exists()


def test_commit_does_not_replace_factory_identity(mocker, identity_store, tmp_path):
  factory_path = Path(tmp_path) / "comma" / "dongle_id"
  factory_path.parent.mkdir()
  factory_path.write_text("factory")
  registration.commit("konik", True)
  assert identity_store.read_text() == "konik"
  assert factory_path.read_text() == "factory"
