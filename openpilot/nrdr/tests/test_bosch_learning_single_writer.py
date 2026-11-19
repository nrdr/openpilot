"""Every learner store has exactly one writer per car case (static tests over a real CarInterface, the real
HondaParamsProvider and a recording Params; no road evidence).

HondaGasFactorParams / HondaWindFactorParams are written by nrdr's provider (digest-checked) and by MVL. The Bosch-A
learner (BoschLearningParams) must never write them: it owns its own file."""
import json

import pytest

from opendbc.car import structs
from opendbc.car.honda.interface import CarInterface
from opendbc.car.honda.values import CAR
from openpilot.nrdr.car.opendbc import HondaParamsProvider, OpendbcParamKey
from openpilot.nrdr.features.longitudinal.bosch_a.learning_params import attach
from openpilot.nrdr.tests.test_opendbc_boundary import FakeParams
from openpilot.sunnypilot.selfdrive.car.opendbc_config import build_sunnypilot_car_config

PID = structs.CarControl.Actuators.LongControlState.pid
SHARED = {str(OpendbcParamKey.HONDA_GAS_FACTOR), str(OpendbcParamKey.HONDA_WIND_FACTOR)}
SHARED_AND_ALPHA = SHARED | {str(OpendbcParamKey.HONDA_GAS_ALPHA)}
FRAMES = 6001


def run_case(tmp_path, car, *, mvl, bosch_a=True, drive_frames=FRAMES, params=None):
  params = params or FakeParams()
  params.values[str(OpendbcParamKey.HONDA_BOSCH_A_RADAR)] = bosch_a
  params.values[str(OpendbcParamKey.HONDA_LIVE_LEARNING_GAS)] = mvl
  config = build_sunnypilot_car_config(params, start_worker=False, metadata_path=tmp_path / "nrdr_meta.json")
  fp = {i: {} for i in range(7)}
  cp = CarInterface.get_params(car, fp, [], True, False, False, config)
  sp = CarInterface.get_params_sp(cp, car, fp, [], True, False, False)
  ci = CarInterface(cp, sp, config)
  ci.update([])
  ci.CS.out.vEgo = 12.0
  ci.CS.out.cruiseState.speed = 25.0
  ci.CS.out.cruiseState.available = True
  bosch_file = tmp_path / "bosch_learner.json"
  learning = attach(ci, meta_path=str(bosch_file))
  if learning is not None:
    learning.owner.set_factors(1.234, 0.876)  # a learned value that differs from the saved one, so persist must write
  baseline = len(params.writes)
  cc = structs.CarControl(enabled=True, longActive=True, latActive=True)
  cc.actuators.accel = 0.3
  cc.actuators.longControlState = PID
  for tick in range(drive_frames):
    ci.apply(cc.as_reader(), structs.CarControlSP(), tick * 10_000_000)
  provider = config.honda.provider
  # Drain what the paced writers would write, as the real worker threads do.
  while provider._write_queue.qsize():
    item = provider._write_queue.get_nowait()
    if item is not None:
      provider._write_longitudinal_state(*item)
  while provider._mvl_state.flush_one():
    pass
  writes = [key for key, *_ in params.writes[baseline:]]
  return ci, params, provider, bosch_file, writes, tmp_path / "nrdr_meta.json"


def test_civic_mvl_off_only_the_bosch_a_learner_writes_and_only_its_own_file(tmp_path):
  ci, params, provider, bosch_file, writes, nrdr_meta = run_case(tmp_path, CAR.HONDA_CIVIC_BOSCH, mvl=False)
  assert ci.CC.bosch_longitudinal is not None
  assert not (set(writes) & SHARED_AND_ALPHA)  # nothing touches the keys nrdr and MVL own
  assert not nrdr_meta.exists()  # nrdr's digest record is not rewritten either
  state = json.loads(bosch_file.read_text())
  assert (state["gas_factor"], state["wind_factor"]) == ci.CC.bosch_learning_params.saved  # what the learner holds
  assert state["car_fingerprint"] == CAR.HONDA_CIVIC_BOSCH


def test_civic_mvl_on_bosch_a_learner_does_not_collide_with_mvl(tmp_path):
  ci, params, provider, bosch_file, writes, nrdr_meta = run_case(tmp_path, CAR.HONDA_CIVIC_BOSCH, mvl=True)
  assert ci.CC.mvl_longitudinal and ci.CC.bosch_longitudinal.civic_learner is not None
  # Bosch-A learner: own file, factors as set.
  learned_gas = ci.CC.bosch_learning_params.saved[0]
  assert json.loads(bosch_file.read_text())["gas_factor"] == learned_gas  # the Civic learner moves it; it is saved here
  # MVL is the only writer to the shared keys: each key written by the MVL store at most once per flush, and the
  # value MVL wrote is never the Bosch-A learner's 1.234/0.876 (which would mean a second writer).
  for key in SHARED:
    assert writes.count(key) <= 1
  assert params.values.get(str(OpendbcParamKey.HONDA_GAS_FACTOR)) != learned_gas
  assert params.values.get(str(OpendbcParamKey.HONDA_WIND_FACTOR)) != 0.876


@pytest.mark.parametrize("mvl", [False, True])
def test_crv_bosch_a_learner_never_writes_shared_keys(tmp_path, mvl):
  ci, params, provider, bosch_file, writes, nrdr_meta = run_case(tmp_path, CAR.HONDA_CRV_5G, mvl=mvl)
  state = json.loads(bosch_file.read_text())
  assert state["gas_factor"] == ci.CC.bosch_learning_params.saved[0] and state["car_fingerprint"] == CAR.HONDA_CRV_5G
  assert params.values.get(str(OpendbcParamKey.HONDA_GAS_FACTOR)) != 1.234
  assert params.values.get(str(OpendbcParamKey.HONDA_WIND_FACTOR)) != 0.876
  if not mvl:
    assert not (set(writes) & SHARED_AND_ALPHA)  # CR-V MVL off: nrdr persist is skipped, nobody writes the keys


def test_non_bosch_a_honda_has_no_bosch_a_learner_and_keeps_the_nrdr_writer(tmp_path):
  ci, params, provider, bosch_file, writes, nrdr_meta = run_case(tmp_path, CAR.HONDA_CIVIC_BOSCH, mvl=False, bosch_a=False)
  assert ci.CC.bosch_longitudinal is None
  assert not bosch_file.exists()
  # nrdr's own persist() is the writer (Bosch car: persists at frame % 6000); its digest record is then valid.
  assert SHARED <= set(writes)
  meta = json.loads(nrdr_meta.read_text())
  assert meta["pending"] is False
  assert provider.load_longitudinal_factors(CAR.HONDA_CIVIC_BOSCH) == pytest.approx(tuple(params.values[k] for k in
    (str(OpendbcParamKey.HONDA_GAS_FACTOR), str(OpendbcParamKey.HONDA_WIND_FACTOR))))


def test_bosch_a_learning_does_not_invalidate_the_nrdr_digest(tmp_path):
  # nrdr stores a state with its digest, then the Bosch-A learner runs on the same Params: nrdr's value must still load.
  params = FakeParams()
  provider = HondaParamsProvider(params, start_worker=False, metadata_path=tmp_path / "nrdr_meta.json")
  provider._write_longitudinal_state(1.0, 1.15, 0.95, CAR.HONDA_CIVIC_BOSCH)
  assert provider.load_longitudinal_factors(CAR.HONDA_CIVIC_BOSCH) == pytest.approx((1.15, 0.95))
  run_case(tmp_path, CAR.HONDA_CIVIC_BOSCH, mvl=False, params=params)
  fresh = HondaParamsProvider(params, start_worker=False, metadata_path=tmp_path / "nrdr_meta.json")
  assert fresh.load_longitudinal_factors(CAR.HONDA_CIVIC_BOSCH) == pytest.approx((1.15, 0.95))
