"""Bosch-A gas/wind learner persistence (BoschLearningParams, attach) and the three opendbc tests that were skipped
there because they need the host: adapted to the nrdr host. The factors live in the learner's own file, never in the
HondaGasFactorParams/HondaWindFactorParams keys (see test_bosch_learning_single_writer.py). Static tests; no road
evidence."""
import json
from types import SimpleNamespace

import pytest

from opendbc.car import gen_empty_fingerprint
from opendbc.car.honda.bosch_longitudinal import BoschLongitudinal, star7_params
from opendbc.car.honda.interface import CarInterface
from opendbc.car.honda.values import CAR, CarControllerParams
from opendbc.sunnypilot.car.tests.runtime_config import make_test_car_config
from openpilot.nrdr.features.longitudinal.bosch_a import learning_params
from openpilot.nrdr.features.longitudinal.bosch_a.learning_params import BoschLearningParams, attach


def car_params(identity):
  return CarInterface.get_params(identity, gen_empty_fingerprint(), [], True, False, False,
                                 make_test_car_config(bosch_a_radar=True))


def owner(identity=CAR.HONDA_CIVIC_BOSCH):
  cp = car_params(identity)
  return BoschLongitudinal(cp, star7_params(cp, CarControllerParams(cp)))


def write_state(path, version, fingerprint, gas, wind):
  path.write_text(json.dumps({"version": version, "car_fingerprint": fingerprint, "gas_factor": gas, "wind_factor": wind}))


def read_state(path):
  return json.loads(path.read_text())


def test_actual_configure_loads_typed_factors_without_startup_rewrite(tmp_path):
  # Adapted from opendbc test_bosch_longitudinal.py: attach() replaces starpilot configure_controller. Civic is the
  # car with a learner version, so the version is consulted (here: already current, as after the one-time reset).
  meta = tmp_path / "meta.json"
  cp = car_params(CAR.HONDA_CIVIC_BOSCH)
  sp = CarInterface.get_params_sp(cp, CAR.HONDA_CIVIC_BOSCH, gen_empty_fingerprint(), [], True, False, False)
  ci = CarInterface(cp, sp, make_test_car_config(bosch_a_radar=True))
  write_state(meta, ci.CC.bosch_longitudinal.learner_version, CAR.HONDA_CIVIC_BOSCH, 1.25, 0.85)
  before = meta.read_text()
  learning = attach(ci, meta_path=str(meta))
  assert learning is ci.CC.bosch_learning_params
  assert learning.owner is ci.CC.bosch_longitudinal
  assert (learning.owner.bosch_gas_factor, learning.owner.bosch_wind_factor) == (1.25, 0.85)
  learning.owner.set_factors(1.1, 0.9)
  learning.persist(0)
  learning.persist(5999)
  assert meta.read_text() == before  # no startup rewrite
  learning.persist(6000)
  assert read_state(meta)["gas_factor"] == pytest.approx(1.1)
  assert read_state(meta)["wind_factor"] == pytest.approx(0.9)
  assert read_state(meta)["version"] == learning.owner.learner_version
  mtime = meta.stat().st_mtime_ns
  learning.persist(12000)
  assert meta.stat().st_mtime_ns == mtime  # unchanged factors are not rewritten
  learning.owner.set_factors(1.2, 0.9)
  learning.persist(18000)
  assert read_state(meta)["gas_factor"] == pytest.approx(1.2)


def test_old_saved_factors_are_reset_once(tmp_path):
  meta = tmp_path / "meta.json"
  write_state(meta, learning_params_version() - 1, CAR.HONDA_CIVIC_BOSCH, 1.4, 0.7)
  first = BoschLearningParams(owner(), meta_path=str(meta))
  assert (first.owner.bosch_gas_factor, first.owner.bosch_wind_factor) == (1.0, 1.0)
  assert read_state(meta) == {"version": first.version, "car_fingerprint": CAR.HONDA_CIVIC_BOSCH,
                              "gas_factor": 1.0, "wind_factor": 1.0}
  write_state(meta, first.version, CAR.HONDA_CIVIC_BOSCH, 1.3, 0.9)  # learned on the new math
  second = BoschLearningParams(owner(), meta_path=str(meta))
  assert (second.owner.bosch_gas_factor, second.owner.bosch_wind_factor) == (1.3, 0.9)


def test_no_saved_state_resets_a_civic_once_and_records_the_version(tmp_path):
  meta = tmp_path / "meta.json"
  learning = BoschLearningParams(owner(), meta_path=str(meta))
  assert (learning.owner.bosch_gas_factor, learning.owner.bosch_wind_factor) == (1.0, 1.0)
  assert read_state(meta)["version"] == learning.version is not None


def test_other_cars_never_reset_saved_factors(tmp_path):
  meta = tmp_path / "meta.json"
  write_state(meta, None, CAR.HONDA_ACCORD, 1.4, 0.7)
  learning = BoschLearningParams(owner(CAR.HONDA_ACCORD), meta_path=str(meta))
  assert (learning.owner.bosch_gas_factor, learning.owner.bosch_wind_factor) == (1.4, 0.7)
  assert read_state(meta)["gas_factor"] == 1.4  # untouched: no startup write


def test_other_cars_start_from_one_and_write_only_when_the_factors_move(tmp_path):
  meta = tmp_path / "meta.json"
  learning = BoschLearningParams(owner(CAR.HONDA_ACCORD), meta_path=str(meta))
  assert (learning.owner.bosch_gas_factor, learning.owner.bosch_wind_factor) == (1.0, 1.0)
  assert not meta.exists()
  learning.persist(6000)
  assert not meta.exists()
  learning.owner.set_factors(1.2, 0.8)
  learning.persist(12000)
  assert read_state(meta) == {"version": None, "car_fingerprint": CAR.HONDA_ACCORD, "gas_factor": 1.2, "wind_factor": 0.8}


def test_factors_saved_for_another_car_are_not_loaded(tmp_path):
  meta = tmp_path / "meta.json"
  write_state(meta, None, CAR.HONDA_CRV_5G, 1.4, 0.7)
  learning = BoschLearningParams(owner(CAR.HONDA_ACCORD), meta_path=str(meta))
  assert (learning.owner.bosch_gas_factor, learning.owner.bosch_wind_factor) == (1.0, 1.0)


@pytest.mark.parametrize("gas,wind", [(float("nan"), float("inf")), ("x", None), (True, [1]), (99.0, -1.0)])
def test_invalid_saved_values_fall_back_to_one(tmp_path, gas, wind):
  meta = tmp_path / "m.json"
  meta.write_text(json.dumps({"version": None, "car_fingerprint": CAR.HONDA_ACCORD, "gas_factor": gas, "wind_factor": wind})
                  .replace("NaN", "null").replace("Infinity", "null"))
  learning = BoschLearningParams(owner(CAR.HONDA_ACCORD), meta_path=str(meta))
  assert (learning.owner.bosch_gas_factor, learning.owner.bosch_wind_factor) == (1.0, 1.0)


def test_corrupt_file_is_ignored(tmp_path):
  meta = tmp_path / "m.json"
  meta.write_text("{not json")
  learning = BoschLearningParams(owner(CAR.HONDA_ACCORD), meta_path=str(meta))
  assert (learning.owner.bosch_gas_factor, learning.owner.bosch_wind_factor) == (1.0, 1.0)


def test_unwritable_meta_still_resets_and_does_not_raise(tmp_path):
  learning = BoschLearningParams(owner(), meta_path=str(tmp_path / "missing_dir" / "meta.json"))
  assert (learning.owner.bosch_gas_factor, learning.owner.bosch_wind_factor) == (1.0, 1.0)
  learning.owner.set_factors(1.2, 0.9)
  learning.persist(6000)  # does not raise
  assert learning.saved == (1.0, 1.0)  # not recorded as saved, so the next period retries


def test_attach_ignores_cars_without_a_bosch_actuator(tmp_path):
  meta = tmp_path / "m.json"
  assert attach(SimpleNamespace(CC=SimpleNamespace(bosch_longitudinal=None), CP=SimpleNamespace(brand="honda")), str(meta)) is None
  assert attach(SimpleNamespace(CC=SimpleNamespace(bosch_longitudinal=owner()), CP=SimpleNamespace(brand="toyota")), str(meta)) is None
  assert attach(SimpleNamespace(CC=None, CP=None), str(meta)) is None
  assert not meta.exists()


def test_default_meta_path_is_separate_from_the_nrdr_mvl_learner():
  assert learning_params.LEARNER_META_PATH == "/data/star7_honda_gas_learner.json"
  assert learning_params.LEARNER_META_PATH != "/data/honda_learner_meta.json"


def learning_params_version():
  return owner().learner_version
