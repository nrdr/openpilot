from types import SimpleNamespace

import pytest

from opendbc.car.honda.values import CAR
from opendbc.sunnypilot.car.honda.controller_features import HondaControllerFeatures
from opendbc.sunnypilot.car.honda.gas_interceptor import gas_multiplier


def _features(fingerprint):
  features = HondaControllerFeatures.__new__(HondaControllerFeatures)
  features.CP = SimpleNamespace(carFingerprint=fingerprint)
  return features


def test_full_brake_authority_uses_complete_nidec_range():
  features = _features(CAR.HONDA_CLARITY)
  assert features.nidec_brake_authority(-4.0, 0.8, 10.0, True) == 1.0
  assert features.nidec_brake_authority(-3.5, 0.7, 10.0, True) == pytest.approx(0.875)
  assert features.nidec_brake_authority(-4.0, 0.8, 10.0, False) == 0.8


def test_full_brake_authority_does_not_change_bosch():
  features = _features(CAR.HONDA_CIVIC_BOSCH)
  assert features.nidec_brake_authority(-4.0, 0.8, 10.0, True) == 0.8


def test_full_brake_authority_preserves_top_end_wind_headroom():
  assert HondaControllerFeatures.nidec_brake_command(0.94, 0.10, True) == pytest.approx(0.84)
  assert HondaControllerFeatures.nidec_brake_command(0.96, 0.10, True) == pytest.approx(0.96)
  assert HondaControllerFeatures.nidec_brake_command(0.96, 0.10, False) == pytest.approx(0.86)


def test_roen_limits_remove_only_the_low_speed_pedal_taper():
  assert gas_multiplier(0.0, False) == pytest.approx(0.4)
  assert gas_multiplier(5.0, False) == pytest.approx(0.7)
  assert gas_multiplier(0.0, True) == 1.0
  assert gas_multiplier(10.0, True) == 1.0
