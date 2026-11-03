from types import SimpleNamespace

import pytest

from opendbc.car.honda.values import CAR
from opendbc.car.honda.tests.test_civic_pcm import interface
from openpilot.nrdr.features.longitudinal.civic_pcm import pcm_reference
from openpilot.cereal import custom
from openpilot.selfdrive.car.helpers import convert_carControlSP


@pytest.mark.parametrize('car,interceptor', [(CAR.HONDA_CLARITY, False), (CAR.HONDA_CLARITY, True),
                                          (CAR.HONDA_CIVIC, True), (CAR.HONDA_CIVIC_BOSCH, False)])
def test_reference_handoff_is_civic_pcm_only(car, interceptor):
  ci, _ = interface(car, interceptor=interceptor)
  assert pcm_reference(ci.CP, ci.CP_SP, [20.0], 100, True) == (False, 0.0, 0)


@pytest.mark.parametrize('speed,valid,mono', [(float('nan'), True, 100), (float('inf'), True, 100),
                                           (-1.0, True, 100), (101.0, True, 100),
                                           (20.0, False, 100), (20.0, True, 0)])
def test_invalid_reference_does_not_change_mode(speed, valid, mono):
  cp = SimpleNamespace(carFingerprint=CAR.HONDA_CIVIC, openpilotLongitudinalControl=True, flags=0)
  sp = SimpleNamespace(enableGasInterceptor=False, flags=0)
  assert pcm_reference(cp, sp, [speed], mono, valid) == (True, 0.0, 0)
  assert pcm_reference(cp, sp, [], 100, True) == (True, 0.0, 0)


@pytest.mark.parametrize('speed', [0.0, 20.0, 100.0])
def test_reference_survives_capnp_and_card_conversion(speed):
  ci, _ = interface()
  enabled, target, stamp = pcm_reference(ci.CP, ci.CP_SP, [speed], 10_000_000_000, True)
  message = custom.CarControlSP.new_message(civicPcmEnabled=enabled, civicPcmReferenceSpeed=target,
                                            civicPcmReferenceMonoTime=stamp)
  with custom.CarControlSP.from_bytes(message.to_bytes()) as reader:
    converted = convert_carControlSP(reader)
  assert converted.civicPcmEnabled
  assert converted.civicPcmReferenceSpeed == speed
  assert converted.civicPcmReferenceMonoTime == stamp
