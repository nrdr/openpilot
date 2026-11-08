"""Bosch-A Track bounds on the published lead accel extrapolation (aLeadTau floor, aLeadK lower clamp)."""
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.controls.radard import KalmanParams
from openpilot.nrdr.features.radar import bosch_a_lead_policy as radar
from openpilot.nrdr.features.radar.bosch_a_lead_policy import BOSCH_A_LEAD_ACCEL_MIN, BOSCH_A_LEAD_ACCEL_TAU_MIN, Track


def _hard_braking_track(steps=60, decel=8.0):
  track = Track(5, 20.0, KalmanParams(DT_MDL))
  v_lead = 20.0
  for _ in range(steps):
    v_lead = max(v_lead - decel * DT_MDL, 0.0)
    track.update(30.0, 0.0, v_lead - 20.0, v_lead, True)
  return track


def test_tau_never_decays_below_floor():
  track = _hard_braking_track()
  assert track.aLeadTau.x >= BOSCH_A_LEAD_ACCEL_TAU_MIN
  assert track.get_RadarState()['aLeadTau'] >= BOSCH_A_LEAD_ACCEL_TAU_MIN


def test_published_accel_clamped_but_kf_state_untouched():
  track = _hard_braking_track()
  kf_accel = float(track.kf.x[radar.ACCEL][0])
  assert kf_accel < BOSCH_A_LEAD_ACCEL_MIN  # the scenario really drives the KF past the clamp
  assert track.aLeadK == BOSCH_A_LEAD_ACCEL_MIN
  assert track.get_RadarState()['aLeadK'] == BOSCH_A_LEAD_ACCEL_MIN
  # vLead / vLeadK still carry the real slowdown
  assert track.vLeadK < 20.0 - 0.5 * 8.0 * 60 * DT_MDL * 0.5


def test_gentle_lead_unchanged():
  track = Track(1, 20.0, KalmanParams(DT_MDL))
  for _ in range(40):
    track.update(30.0, 0.0, 0.0, 20.0, True)
  assert abs(track.aLeadK) < 0.5
  assert track.aLeadTau.x == radar._LEAD_ACCEL_TAU


def test_coasted_update_keeps_floor():
  track = _hard_braking_track()
  track.update(30.0, 0.0, -10.0, 10.0, False, measurement_update=False)
  assert track.aLeadTau.x >= BOSCH_A_LEAD_ACCEL_TAU_MIN
  assert track.aLeadK >= BOSCH_A_LEAD_ACCEL_MIN
