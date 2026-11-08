from types import SimpleNamespace

from openpilot.nrdr.features.longitudinal.bosch_a import bosch_a_coast_first as cf


def lead(d, v, a=0.0):
  return SimpleNamespace(present=True, radar=True, dRel=d, vLead=v, aLeadK=a)


def planner(monkeypatch):
  monkeypatch.setattr(cf, 'vehicle_supported', lambda CP: True)
  return cf.BoschACoastFirst(SimpleNamespace(radarUnavailable=False))


def step(p, ld, target, v_ego=31.2, follow_s=1.25, fcw=False):
  return p.step(lead_one=ld, lead_two=None, target=target, v_ego=v_ego, follow_s=follow_s, fcw=fcw, reset_state=False)


def test_route_71_1203_distant_tap_coasts_first(monkeypatch):
  # 727.4: pickup about 58 m ahead (1.86 s), 4 m/s slower, braking -2.2; planner asks -2.25
  p = planner(monkeypatch)
  assert step(p, lead(58.0, 27.0, -2.2), -2.25) == cf.COAST_ACCEL
  out = step(p, lead(57.0, 26.5, -2.5), -2.25)
  assert cf.COAST_ACCEL - 0.15 < out < cf.COAST_ACCEL  # floor ramps down at RAMP_JERK, the brake is staged not cut


def test_staged_floor_reaches_full_brake(monkeypatch):
  p = planner(monkeypatch)
  out = None
  for _ in range(60):
    out = step(p, lead(80.0, 30.0, 0.0), -2.0)
  assert out == -2.0


def test_close_gap_brakes_at_once(monkeypatch):
  p = planner(monkeypatch)
  assert step(p, lead(40.0, 27.0, -1.0), -2.25) == -2.25  # 1.28 s < follow + margin
  assert step(p, lead(80.0, 30.0, 0.0), -2.25) == -2.25   # latched for the rest of the event


def test_hard_lead_brake_and_fcw_bypass(monkeypatch):
  p = planner(monkeypatch)
  assert step(p, lead(60.0, 27.0, -5.0), -3.0) == -3.0
  p = planner(monkeypatch)
  assert step(p, lead(60.0, 27.0, -1.0), -3.0, fcw=True) == -3.0


def test_sustained_lead_brake_fails_projection(monkeypatch):
  p = planner(monkeypatch)
  assert step(p, lead(52.0, 24.0, -3.5), -2.5) == -2.5


def test_gentle_target_and_low_speed_untouched(monkeypatch):
  p = planner(monkeypatch)
  assert step(p, lead(60.0, 30.0), -0.3) == -0.3
  assert step(p, lead(30.0, 5.0), -2.0, v_ego=8.0) == -2.0


def test_route_8f_bookmark_1_distant_tap_coasts_first(monkeypatch):
  # 0000008f 4445.2 (second dip): car 37 m ahead at 32 mph, TTC 14.5 s; only the old 15 m/s speed floor stood it down
  p = planner(monkeypatch)
  assert step(p, lead(37.0, 11.6, -1.0), -1.8, v_ego=14.1) == cf.COAST_ACCEL


def test_projection_holds_the_lead_decel_only_for_the_hold(monkeypatch):
  # illustrative tap geometry: 29 m, lead 11 m/s braking -3, ego 14.2. Three seconds of -3 closes the projected gap;
  # LEAD_DECEL_HOLD_S of -3, then the lead's speed held, does not
  assert cf.projected_gap_ok(29.0, 11.0, -3.0, 14.2, cf.COAST_ACCEL)
  monkeypatch.setattr(cf, 'LEAD_DECEL_HOLD_S', cf.HORIZON_S)
  assert not cf.projected_gap_ok(29.0, 11.0, -3.0, 14.2, cf.COAST_ACCEL)


def test_below_the_speed_floor_brakes_at_once(monkeypatch):
  p = planner(monkeypatch)
  assert step(p, lead(37.0, 11.6, -1.0), -1.8, v_ego=13.0) == -1.8
