"""Retired experiments are absent; old persisted choices cannot change control."""
from pathlib import Path
import pytest

from opendbc.car.honda.values import CAR, HondaFlags
from opendbc.car.structs import car
from openpilot.nrdr.params.specs import PARAM_SPECS_BY_KEY
from openpilot.nrdr.params.tuning_policy import tuning_write_allowed
from openpilot.nrdr.tests.test_honda_pcm_ui import state as base_state
from openpilot.nrdr.tests.test_opendbc_boundary import FakeParams
from openpilot.sunnypilot.selfdrive.car.opendbc_config import build_sunnypilot_car_config
from openpilot.sunnypilot.sunnylink.tools.compile_settings_ui import DEFAULT_SRC, compile_schema

ROOT = Path(__file__).resolve().parents[3]
KEYS = ("NrdrHondaPcmFixedCruise", "NrdrHondaLegacyPcm")


def cp_bytes(flags=0, **kwargs):
  return car.CarParams.new_message(**({"brand": "honda", "carFingerprint": "HONDA_CIVIC", "openpilotLongitudinalControl": True,
                                      "flags": int(HondaFlags.NIDEC | flags)} | kwargs)).to_bytes()


def state(**kwargs):
  return base_state(**({"flags": int(HondaFlags.NIDEC)} | kwargs))


@pytest.mark.parametrize("saved", [False, True])
def test_retired_saved_choices_never_enter_runtime_config(tmp_path, saved):
  params = FakeParams({**dict.fromkeys(KEYS, saved), "HondaLiveLearningGas": True, "NrdrHondaPcmMode": 2})
  config = build_sunnypilot_car_config(params, start_worker=False, metadata_path=tmp_path / "meta.json")
  assert config.honda.mvl_longitudinal and config.honda.nidec_pcm_mode == 2
  assert not hasattr(config.honda, "nidec_fixed_cruise")
  assert not hasattr(config.honda, "nidec_legacy_pcm")
  assert not params.writes


def test_retired_settings_absent_from_schema_and_rejected_for_writes():
  import json
  schema = json.dumps(compile_schema(DEFAULT_SRC))
  for key in KEYS:
    assert key not in schema
    assert PARAM_SPECS_BY_KEY[key].lifecycle.value == "tombstone"
    assert not tuning_write_allowed(FakeParams({}), key, is_offroad=True)


@pytest.mark.parametrize("fingerprint", [CAR.HONDA_CIVIC, CAR.HONDA_CIVIC_BOSCH])
def test_retired_civic_icbm_ignores_stale_availability(fingerprint):
  from types import SimpleNamespace as NS
  from openpilot.nrdr.ui.icbm import icbm_available
  assert icbm_available(NS(carFingerprint=fingerprint), NS(intelligentCruiseButtonManagementAvailable=True)) is (fingerprint != CAR.HONDA_CIVIC)
