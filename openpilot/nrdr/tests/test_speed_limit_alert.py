from types import SimpleNamespace

import pytest

from openpilot.common.constants import CV
from openpilot.nrdr.hooks.events_sp import speed_limit_pre_active_alert


@pytest.mark.parametrize(("metric", "speed", "expected"), ((False, 35, "35 mph"), (True, 50, "50 km/h")))
def test_speed_limit_confirmation_prompt_uses_distance_button(metric, speed, expected):
  speed_limit = speed * (CV.KPH_TO_MS if metric else CV.MPH_TO_MS)
  sm = {
    "longitudinalPlanSP": SimpleNamespace(
      speedLimit=SimpleNamespace(
        resolver=SimpleNamespace(speedLimitFinalLast=speed_limit),
      ),
    ),
  }

  alert = speed_limit_pre_active_alert(None, None, sm, metric, 0, None)

  assert alert.alert_text_1 == f"Press distance button to accept {expected} speed limit"
  assert "+" not in alert.alert_text_1
  assert "Press -" not in alert.alert_text_1
