"""The planner and controller use the same qualified, logged startup choice."""
from types import SimpleNamespace

import pytest

from opendbc.car.honda.values import HondaFlags
from openpilot.nrdr.features.longitudinal.policy import (
  longitudinal_personality, mvl_longitudinal_enabled, nrdr_custom_longitudinal_enabled, nrdr_longitudinal_enabled,
)


@pytest.mark.parametrize("brand,open_long,flag,expected", [
  ("honda", True, True, True),
  ("honda", False, True, False),
  ("honda", True, False, False),
  ("toyota", True, True, False),
])
def test_mvl_requires_qualified_honda_startup_flag(brand, open_long, flag, expected):
  cp = SimpleNamespace(brand=brand, carFingerprint="test", openpilotLongitudinalControl=open_long,
                       flags=int(HondaFlags.MVL_LONGITUDINAL) if flag else 0)
  assert mvl_longitudinal_enabled(cp) is expected
  assert nrdr_custom_longitudinal_enabled(cp) is (brand == "honda" and not expected)
  assert nrdr_longitudinal_enabled(cp) is (brand == "honda")


def test_mvl_does_not_hide_econ_or_change_non_honda_personality_domain():
  assert [longitudinal_personality(x, True) for x in range(4)] == [0, 1, 2, 3]
  assert longitudinal_personality(3, False) == 2
  assert longitudinal_personality(True, True) == 1
