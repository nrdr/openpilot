import json
import pytest
from Crypto.PublicKey import RSA
from pathlib import Path

from openpilot.common.params import Params
from openpilot.system.athena.registration import register, UNREGISTERED_DONGLE_ID
from openpilot.system.athena.tests.helpers import MockResponse
from openpilot.common.hardware.hw import Paths


class TestRegistration:

  @pytest.fixture(autouse=True)
  def use_comma_backend(self, mocker, tmp_path):
    mocker.patch("openpilot.system.athena.registration._is_konik_backend", return_value=False)
    mocker.patch.object(Paths, "persist_root", return_value=str(tmp_path))
    # clear params and setup key paths
    self.params = Params()

    persist_dir = Path(Paths.persist_root()) / "comma"
    persist_dir.mkdir(parents=True, exist_ok=True)

    self.priv_key = persist_dir / "id_rsa"
    self.pub_key = persist_dir / "id_rsa.pub"
    self.dongle_id = persist_dir / "dongle_id"

  def _generate_keys(self):
    self.pub_key.touch()
    k = RSA.generate(2048)
    with open(self.priv_key, "wb") as f:
      f.write(k.export_key())
    with open(self.pub_key, "wb") as f:
      f.write(k.publickey().export_key())

  def test_valid_cache(self, mocker):
    # if all params are written, return the cached dongle id.
    # should work with a dongle ID on either /persist/ or normal params
    self._generate_keys()

    dongle = "DONGLE_ID_123"
    m = mocker.patch("openpilot.system.athena.registration.api_get", autospec=True)
    for persist, params in [(True, True), (True, False), (False, True)]:
      self.params.put("DongleId", dongle if params else "", block=True)
      with open(self.dongle_id, "w") as f:
        f.write(dongle if persist else "")
      assert register() == dongle
      assert not m.called

  def test_no_keys(self, mocker):
    # missing pubkey
    m = mocker.patch("openpilot.system.athena.registration.api_get", autospec=True)
    dongle = register()
    assert m.call_count == 0
    assert dongle == UNREGISTERED_DONGLE_ID
    assert self.params.get("DongleId") == dongle

  def test_missing_cache(self, mocker):
    # keys exist but no dongle id
    self._generate_keys()
    m = mocker.patch("openpilot.system.athena.registration.api_get", autospec=True)
    dongle = "DONGLE_ID_123"
    m.return_value = MockResponse(json.dumps({'dongle_id': dongle}), 200)
    assert register() == dongle
    assert m.call_count == 1

    # call again, shouldn't hit the API this time
    assert register() == dongle
    assert m.call_count == 1
    assert self.params.get("DongleId") == dongle

  def test_unregistered(self, mocker):
    # keys exist, but unregistered
    self._generate_keys()
    m = mocker.patch("openpilot.system.athena.registration.api_get", autospec=True)
    m.return_value = MockResponse(None, 402)
    dongle = register()
    assert m.call_count == 1
    assert dongle == UNREGISTERED_DONGLE_ID
    assert self.params.get("DongleId") == dongle


class TestKonikRegistration:

  @pytest.fixture(autouse=True)
  def use_test_persist(self, mocker, tmp_path):
    mocker.patch.object(Paths, "persist_root", return_value=str(tmp_path))
    self.params = Params()
    persist_dir = Path(Paths.persist_root()) / "comma"
    persist_dir.mkdir(parents=True, exist_ok=True)
    self.priv_key = persist_dir / "id_rsa"
    self.pub_key = persist_dir / "id_rsa.pub"
    self.factory_dongle_id = persist_dir / "dongle_id"

  def _generate_keys(self):
    self.pub_key.touch()
    key = RSA.generate(2048)
    self.priv_key.write_bytes(key.export_key())
    self.pub_key.write_bytes(key.publickey().export_key())

  def _setup_konik(self, mocker, tmp_path):
    durable_path = tmp_path / "konik_dongle_id"
    mocker.patch("openpilot.system.athena.registration._is_konik_backend", return_value=True)
    mocker.patch("openpilot.system.athena.registration.get_konik_dongle_id_path", return_value=durable_path)
    self._generate_keys()
    return durable_path

  def test_durable_konik_id_wins_over_factory_id(self, mocker, tmp_path):
    durable_path = self._setup_konik(mocker, tmp_path)
    durable_path.write_text("d7cee79a4d45d4cf")
    self.factory_dongle_id.write_text("a3cd4e3353309ee9")
    self.params.remove("DongleId")
    validate = mocker.patch("openpilot.system.athena.registration._validate_konik_dongle_id")
    pilotauth = mocker.patch("openpilot.system.athena.registration.api_get")

    assert register() == "d7cee79a4d45d4cf"
    assert self.params.get("DongleId") == "d7cee79a4d45d4cf"
    assert self.factory_dongle_id.read_text() == "a3cd4e3353309ee9"
    validate.assert_not_called()
    pilotauth.assert_not_called()

  def test_valid_params_id_is_migrated_to_durable_store(self, mocker, tmp_path):
    durable_path = self._setup_konik(mocker, tmp_path)
    self.params.put("DongleId", "d7cee79a4d45d4cf", block=True)
    self.factory_dongle_id.write_text("a3cd4e3353309ee9")
    mocker.patch("openpilot.system.athena.registration._validate_konik_dongle_id", return_value=True)
    pilotauth = mocker.patch("openpilot.system.athena.registration.api_get")

    assert register() == "d7cee79a4d45d4cf"
    assert durable_path.read_text() == "d7cee79a4d45d4cf"
    assert self.factory_dongle_id.read_text() == "a3cd4e3353309ee9"
    pilotauth.assert_not_called()

  def test_factory_id_is_rejected_and_new_konik_id_is_persisted(self, mocker, tmp_path):
    durable_path = self._setup_konik(mocker, tmp_path)
    self.params.put("DongleId", "a3cd4e3353309ee9", block=True)
    self.factory_dongle_id.write_text("a3cd4e3353309ee9")
    mocker.patch("openpilot.system.athena.registration._validate_konik_dongle_id", return_value=False)
    pilotauth = mocker.patch("openpilot.system.athena.registration.api_get")
    pilotauth.return_value = MockResponse(json.dumps({"dongle_id": "d7cee79a4d45d4cf"}), 200)

    assert register() == "d7cee79a4d45d4cf"
    assert self.params.get("DongleId") == "d7cee79a4d45d4cf"
    assert durable_path.read_text() == "d7cee79a4d45d4cf"
    assert pilotauth.call_count == 1

  def test_network_failure_keeps_params_id_without_persisting_it(self, mocker, tmp_path):
    durable_path = self._setup_konik(mocker, tmp_path)
    self.params.put("DongleId", "d7cee79a4d45d4cf", block=True)
    self.factory_dongle_id.write_text("a3cd4e3353309ee9")
    mocker.patch("openpilot.system.athena.registration._validate_konik_dongle_id", return_value=None)
    pilotauth = mocker.patch("openpilot.system.athena.registration.api_get")

    assert register() == "d7cee79a4d45d4cf"
    assert not durable_path.exists()
    pilotauth.assert_not_called()
