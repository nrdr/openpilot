from types import SimpleNamespace

import pytest

from openpilot.nrdr.features.lateral.steer_ratio_tuning import SteerRatioMode, SteerRatioModeLatch, resolve_steer_ratio_selection


@pytest.mark.parametrize("hybrid,a,b", [(False, 2, 3), (True, 2, 3), (True, 0, 2)])
def test_missing_measured_data_uses_live_comma_for_whole_geometry(hybrid, a, b):
  cp = SimpleNamespace(brand="honda", carFingerprint="HONDA_CRV_5G", steerRatio=16.0, carFw=[])
  selected = resolve_steer_ratio_selection(cp, {
    "NrdrSteerRatioMode": a, "NrdrSteerRatioSourceB": b, "NrdrSteerRatioHybrid": hybrid,
  }, live_comma_ratio=18.1)
  assert selected.available
  assert selected.effective_mode == SteerRatioMode.COMMA
  assert selected.hybrid is None
  assert selected.ratio_at(10.0, 18.1) == pytest.approx(18.1)
  latch = SteerRatioModeLatch(selected)
  assert latch.update(selected, active=True) is selected
  assert latch.rejected_reason == ""
