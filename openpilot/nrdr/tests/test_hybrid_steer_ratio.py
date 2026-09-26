import math
import time
from types import SimpleNamespace

import numpy as np
import pytest
import yaml
from pathlib import Path

from openpilot.nrdr.features.lateral.hybrid_steer_ratio import AngleSource
from openpilot.nrdr.features.lateral.steer_ratio_tuning import (
  CLARITY_RAW_STEER_RATIO, SteerRatioModeLatch, resolve_steer_ratio_selection,
)
from openpilot.nrdr.features.lateral.honda_vgr import HONDA_VGR_PROFILES
from openpilot.nrdr.params.snapshots import CONTROL_GROUPS, LiveParams


def cp(fingerprint="HONDA_CLARITY", firmware=b"39990-TRW-A020", brand="honda"):
  return SimpleNamespace(brand=brand, carFingerprint=fingerprint, steerRatio=16.5,
                         carFw=[SimpleNamespace(ecu="eps", fwVersion=firmware)] if firmware else [])


def settings(a=2, b=3, start=25, enabled=True):
  return {"NrdrSteerRatioMode": a, "NrdrSteerRatioSourceB": b, "NrdrSteerRatioBlendStart": start,
          "NrdrSteerRatioHybrid": enabled, "NrdrSteerRatioManualCenter": 20.0, "NrdrSteerRatioManualFinal": 13.75}


def source(mode, comma=18.0):
  return AngleSource(mode, str(mode), 16.5, 20.0, 13.75, 250.0, comma,
                     CLARITY_RAW_STEER_RATIO, HONDA_VGR_PROFILES[0])


@pytest.mark.parametrize("mode", range(4))
def test_sources_have_exact_forward_inverse_and_left_right_symmetry(mode):
  s = source(mode)
  for angle in (*np.linspace(-1000, 1000, 101), *CLARITY_RAW_STEER_RATIO.angles_deg, 1e-8):
    assert s.inverse(s.forward(angle)) == pytest.approx(angle, abs=1e-8)
    assert s.forward(-angle) == pytest.approx(-s.forward(angle))


@pytest.mark.parametrize("start", (0, 5, 10, 25, 90, 180))
@pytest.mark.parametrize("a", range(4))
@pytest.mark.parametrize("b", range(4))
def test_all_source_pairs_are_invertible_or_explicitly_rejected(a, b, start):
  selected = resolve_steer_ratio_selection(cp(), settings(a, b, start), 18.0)
  if not selected.available:
    assert "reverse or flatten" in selected.unavailable_reason
    assert selected.hybrid is None
    return
  h = selected.hybrid
  assert h is not None
  assert all(y > x for x, y in zip(h.linear, h.linear[1:], strict=False))
  for angle in np.concatenate((np.linspace(-500, 500, 71), np.linspace(start, start + 5, 73))):
    assert h.inverse(h.forward(angle)) == pytest.approx(angle, abs=1e-8)
  for angle in (start, start + 5):
    assert abs(h.forward(angle + 1e-7) - h.forward(angle - 1e-7)) < 1e-5
  assert h.forward(start / 2) == pytest.approx(h.a.forward(start / 2))
  assert h.forward(start + 100) == pytest.approx(h.b.forward(start + 100))


def test_clarity_measured_to_firmware_25_30_and_reverse_rejection():
  valid = resolve_steer_ratio_selection(cp(), settings())
  assert valid.available and valid.hybrid.start == 25 and valid.hybrid.end == 30
  assert valid.firmware_vgr_selected  # Preserve the existing NNLC incompatibility guard.
  assert valid.hybrid.a.forward(7.5) == pytest.approx(16.5 * 7.5 / 20.66570762352077)
  assert valid.hybrid.forward(45) == pytest.approx(HONDA_VGR_PROFILES[0].physical_to_linear(45))
  reverse = resolve_steer_ratio_selection(cp(), settings(3, 2))
  assert not reverse.available and "reverse or flatten" in reverse.unavailable_reason


@pytest.mark.parametrize("bad", (math.nan, math.inf, -1, 181, "garbage"))
def test_invalid_angles_do_not_silently_clamp(bad):
  s = resolve_steer_ratio_selection(cp(), settings(start=bad))
  assert not s.available and s.hybrid_requested


@pytest.mark.parametrize("a,b", ((99, 3), (2, 99), (None, 3), (2, "bad"), (math.inf, 3), (2, math.inf)))
def test_invalid_sources_rejected(a, b):
  assert not resolve_steer_ratio_selection(cp(), settings(a, b)).available


@pytest.mark.parametrize("vehicle", (cp(firmware=None), cp("HONDA_CIVIC", b"39990-TRW-A020"), cp(brand="toyota")))
def test_profiles_cannot_be_borrowed_between_cars_or_unknown_firmware(vehicle):
  assert not resolve_steer_ratio_selection(vehicle, settings()).available


@pytest.mark.parametrize("mode", range(4))
def test_disabled_hybrid_preserves_legacy_single_source(mode):
  values = settings(mode, b=99, start=math.nan, enabled=False)
  before = dict(values)
  s = resolve_steer_ratio_selection(cp(), values)
  baseline = resolve_steer_ratio_selection(cp(), {k: v for k, v in values.items()
                                                if k not in ("NrdrSteerRatioHybrid", "NrdrSteerRatioSourceB", "NrdrSteerRatioBlendStart")})
  assert s == baseline and s.hybrid is None and values == before


def test_invalid_active_edit_retains_last_accepted_geometry_and_inactive_falls_back():
  initial = resolve_steer_ratio_selection(cp(), settings())
  latch = SteerRatioModeLatch(initial)
  invalid = resolve_steer_ratio_selection(cp(), settings(3, 2))
  assert latch.update(invalid, True) is initial
  assert latch.rejected_reason == invalid.unavailable_reason
  assert latch.update(invalid, False) is invalid
  assert invalid.ratio_at(30) == 16.5
  assert invalid.linearize_measured_angle(30) == 30
  assert latch.update(initial, True) is initial and not latch.rejected_reason


def test_comma_is_captured_once_per_selection_and_does_not_mutate_old_geometry():
  first = resolve_steer_ratio_selection(cp(), settings(1, 3), 20.0)
  second = resolve_steer_ratio_selection(cp(), settings(1, 3), 21.0)
  assert first.hybrid.a.comma == 20.0 and second.hybrid.a.comma == 21.0
  assert first.hybrid.forward(10) == pytest.approx(16.5 * 10 / 20)
  assert second.hybrid.forward(10) == pytest.approx(16.5 * 10 / 21)


def test_irrelevant_comma_updates_reuse_cached_geometry():
  first = resolve_steer_ratio_selection(cp(), settings(), 17.0)
  second = resolve_steer_ratio_selection(cp(), settings(), 18.0)
  assert first.hybrid is second.hybrid


class VehicleModel:
  sR = 16.5

  def calc_curvature(self, angle, speed, roll):
    return angle / self.sR * (1 + speed * 0.01) + roll * 0.02

  def get_steer_from_curvature(self, curvature, speed, roll):
    return (curvature - roll * 0.02) * self.sR / (1 + speed * 0.01)


@pytest.mark.parametrize("speed", (0, 15, 30))
@pytest.mark.parametrize("offset", (-1.5, 0, 1.5))
def test_shared_vehicle_model_roundtrip_includes_roll_speed_and_offset(speed, offset):
  s = resolve_steer_ratio_selection(cp(), settings())
  vm = VehicleModel()
  for angle in (-100, -30, -27.5, -25, 0, 25, 27.5, 30, 100):
    curvature = s.measured_curvature(vm, angle, speed, 0.04, offset)
    desired = s.desired_angle_no_offset(vm, angle, speed, 0.04, curvature) + offset
    assert desired == pytest.approx(angle, abs=1e-8)
    rate = s.measured_curvature_rate(vm, angle, 1.0, speed, 0.01, offset)
    assert math.isfinite(rate)


def test_native_background_poll_consumes_hybrid_configuration_without_manual_refresh():
  class FakeParams:
    values = settings()

    def get(self, key):
      return self.values.get(key)

  params = FakeParams()
  reader = LiveParams(CONTROL_GROUPS, params=params, start_worker=True)
  try:
    first = resolve_steer_ratio_selection(cp(), reader.snapshot)
    assert first.hybrid.start == 25
    params.values = {**params.values, "NrdrSteerRatioBlendStart": 15.0}
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
      second = resolve_steer_ratio_selection(cp(), reader.snapshot)
      if second.hybrid and second.hybrid.start == 15:
        break
      time.sleep(0.01)
    assert second.hybrid.start == 15
    assert first.hybrid.start == 25
  finally:
    reader.close()


def test_sunnylink_two_source_selectors_have_blend_slider_between_them():
  path = Path(__file__).resolve().parents[1] / "ui/sunnylink/pages/steering.yaml"
  document = yaml.safe_load(path.read_text(encoding="utf-8"))
  panel = next(p for p in document["sections"][0]["sub_panels"] if p["id"] == "nrdr_steer_ratio_tuning")
  items = panel["items"]
  assert [i["key"] for i in items[:4]] == [
    "NrdrSteerRatioHybrid", "NrdrSteerRatioMode", "NrdrSteerRatioBlendStart", "NrdrSteerRatioSourceB",
  ]
  assert [(o["value"], o["label"]) for o in items[1]["options"]] == [(o["value"], o["label"]) for o in items[3]["options"]]
  assert items[1]["options"] == items[3]["options"]
  assert (items[2]["min"], items[2]["max"], items[2]["step"]) == (0, 180, 1)


def test_control_hook_reports_accepted_geometry_and_rejected_active_request():
  from openpilot.nrdr.hooks.controlsd import vehicle_model_state
  reports = []
  reader = SimpleNamespace(snapshot=settings(), record_applied_settings=lambda *args, **kwargs: reports.append(kwargs))
  controls = SimpleNamespace(CP=cp(), nrdr_live_params=reader, LaC=SimpleNamespace(),
                             sm=SimpleNamespace(valid={"vehicleParameters": True}),
                             steer_ratio_latch=SteerRatioModeLatch(resolve_steer_ratio_selection(cp(), reader.snapshot)))
  live = SimpleNamespace(steerRatio=19.0, steerRatioValid=True, stiffnessFactor=1.0, angleOffsetDeg=0.0)
  car_state = SimpleNamespace(steeringAngleDeg=27.5)
  vehicle_model_state(controls, live, car_state, False)
  vehicle_model_state(controls, live, car_state, True)
  assert len(reports) == 2 and not reports[0]["active"] and reports[1]["active"]
  accepted = controls.steer_ratio_latch.selection
  reader.snapshot = settings(3, 2)
  vehicle_model_state(controls, live, car_state, True)
  assert controls.steer_ratio_latch.selection is accepted
  assert reports[-1]["source_a"] == 3 and reports[-1]["source_b"] == 2
  assert reports[-1]["effective"] == accepted.effective_label
  assert "reverse or flatten" in reports[-1]["rejected_reason"]
