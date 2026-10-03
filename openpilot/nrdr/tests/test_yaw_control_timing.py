"""Yaw Control timing: model delay schedule, command delay, and the modeld seam."""
import math
from types import SimpleNamespace

import pytest

from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.nrdr.features.lateral import yaw_control_timing as timing
from openpilot.nrdr.hooks.modeld import model_lateral_delay_schedule
from openpilot.nrdr.params.snapshots import ParamSnapshot


def test_schedule_is_the_refit_table():
  assert [timing.clarity_lateral_delay(v) for v in (0., 3.5, 7., 12., 20., 30., 40.)] == \
    pytest.approx([.15, .15, .08, .10, .20, .30, .30])


@pytest.mark.parametrize("settings, speed, expected", [
  (None, 0., .145), (None, 12.5, .085), (None, 30., .025),
  (ParamSnapshot(1, {}), 5., .145),
  (ParamSnapshot(1, {"NrdrYawCommandDelayLow": .2, "NrdrYawCommandDelayHigh": .05}), 12.5, .125),
  (ParamSnapshot(1, {"NrdrYawCommandDelayLow": 9., "NrdrYawCommandDelayHigh": -1.}), 5., timing.MAX_COMMAND_DELAY),
  (ParamSnapshot(1, {"NrdrYawCommandDelayLow": 9., "NrdrYawCommandDelayHigh": -1.}), 20., 0.),
  (ParamSnapshot(1, {"NrdrYawCommandDelayLow": math.nan, "NrdrYawCommandDelayHigh": b"x"}), 5., .145),
  (ParamSnapshot(1, {"NrdrYawCommandDelayLow": math.nan, "NrdrYawCommandDelayHigh": b"x"}), 20., .025),
])
def test_command_delay_defaults_fade_and_bounds(settings, speed, expected):
  assert timing.command_delay(settings, speed) == pytest.approx(expected)


def test_delay_line_interpolates_between_samples_and_never_runs_out():
  line = timing.CommandDelay(.01)
  assert line.update(1., .025) == 1.
  for value in range(2, 40):
    out = line.update(float(value), .025)
  assert out == pytest.approx(39. - 2.5)
  assert line.update(40., 0.) == 40.
  assert len(line.buf) == line.buf.maxlen == 32


class Params:
  def __init__(self, values):
    self.values = values
    self.reads = []

  def get(self, key, block=False):
    self.reads.append(key)
    return self.values.get(key)


def car(fingerprint="HONDA_CLARITY", firmware=b"39990-TRW-A020"):
  return SimpleNamespace(brand="honda", carFingerprint=fingerprint,
                         carFw=[SimpleNamespace(ecu="eps", fwVersion=firmware)],
                         lateralTuning=SimpleNamespace(which=lambda: "pid"))


@pytest.fixture
def car_params_sp(monkeypatch):
  import openpilot.cereal.messaging as messaging
  monkeypatch.setattr(messaging, "log_from_bytes", lambda data, _: SimpleNamespace(flags=data))
  return HondaFlagsSP.EPS_MODIFIED.value


def test_modeld_uses_the_schedule_only_for_selected_yaw_control(car_params_sp):
  params = Params({"NrdrLateralController": 1, "CarParamsSP": car_params_sp})
  assert model_lateral_delay_schedule(params, car()) is timing.clarity_lateral_delay
  assert model_lateral_delay_schedule(Params({**params.values, "NrdrYawDelaySchedule": False}), car()) is None
  assert model_lateral_delay_schedule(Params({**params.values, "NrdrLateralController": 0}), car()) is None
  assert model_lateral_delay_schedule(Params({**params.values, "CarParamsSP": 0}), car()) is None
  assert model_lateral_delay_schedule(params, car(firmware=b"39990-TRW-A010")) is None


def test_modeld_never_waits_for_car_params_sp_on_other_cars():
  params = Params({"NrdrLateralController": 1})
  assert model_lateral_delay_schedule(params, car(fingerprint="HONDA_CIVIC")) is None
  assert model_lateral_delay_schedule(params, SimpleNamespace(brand="toyota", carFingerprint="TOYOTA_RAV4",
                                                              lateralTuning=SimpleNamespace(which=lambda: "torque"))) is None
  assert "CarParamsSP" not in params.reads
