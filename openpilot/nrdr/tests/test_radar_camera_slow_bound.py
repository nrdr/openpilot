"""Camera-slower bound (static). The positive case is shaped on 2f8 T1365.04 (radar vRel -2.8, camera lead 11.9 m/s)."""
from types import SimpleNamespace

import pytest

from openpilot.common.realtime import DT_MDL
from openpilot.nrdr.features.radar.radar_camera_slow_bound import (CAM_SLOW_DV_MAX, CAM_SLOW_HOLD_S, CAM_SLOW_MIN_D,
                                                                   CAM_SLOW_RAMP_IN, CAM_SLOW_W_MAX, RADAR_TO_CAMERA,
                                                                   CameraSlowBound)

V_EGO = 20.0


def radar_lead(tid=56, d=80.0, v=17.2, a=-0.3):
  return {'dRel': d, 'yRel': 0.0, 'vRel': v - V_EGO, 'vLead': v, 'vLeadK': v, 'aLeadK': a, 'aLeadTau': 0.6,
          'present': True, 'modelProb': 0.95, 'radar': True, 'radarTrackId': tid}


def vision(d=80.0, v=11.9, a=-1.0):
  return SimpleNamespace(x=[d + RADAR_TO_CAMERA], v=[v], a=[a])


ABSENT = {'present': False}


def step(cb, lead, model=None, prob=0.95, v_ego=V_EGO):
  return cb.apply([lead, ABSENT], [model or vision(), vision()], v_ego, v_ego, [prob, 0.0])[0]


def frames(seconds):
  return int(round(seconds / DT_MDL))


def run(cb, seconds, **kw):
  out = None
  for _ in range(frames(seconds)):
    out = step(cb, radar_lead(), **kw)
  return out


def test_route_2f8_shape_slows_lead_gradually_after_hold():
  cb = CameraSlowBound()
  out = run(cb, CAM_SLOW_HOLD_S - DT_MDL)
  assert out['vLead'] == pytest.approx(17.2)       # nothing before the hold
  prev = out['vLead']
  for _ in range(frames(0.5)):
    out = step(cb, radar_lead())
    assert out['vLead'] <= prev                     # only ever slower
    assert prev - out['vLead'] <= CAM_SLOW_RAMP_IN * DT_MDL * (17.2 - 11.9) + 1e-6   # no step
    prev = out['vLead']
  assert out['vLead'] < 17.2
  out = run(cb, 3.0)
  assert cb.weights[0] == pytest.approx(CAM_SLOW_W_MAX)
  assert out['vLead'] == pytest.approx(17.2 - min(CAM_SLOW_W_MAX * (17.2 - 11.9), CAM_SLOW_DV_MAX))
  assert out['vRel'] == pytest.approx(out['vLead'] - V_EGO)
  assert out['vLeadK'] == pytest.approx(out['vLead'])


def test_distance_accel_and_presence_are_never_changed():
  cb = CameraSlowBound()
  out = run(cb, 4.0)
  assert out['present'] and out['radar'] and out['radarTrackId'] == 56
  assert out['dRel'] == 80.0 and out['aLeadK'] == -0.3 and out['yRel'] == 0.0


def test_never_makes_lead_faster():
  cb = CameraSlowBound()
  for _ in range(frames(4.0)):
    out = step(cb, radar_lead(), vision(v=25.0))
    assert out['vLead'] == pytest.approx(17.2)
  assert cb.weights[0] == 0.0


def test_shift_is_capped():
  cb = CameraSlowBound()
  for _ in range(frames(4.0)):
    out = step(cb, radar_lead(v=17.2), vision(v=0.0))
  assert 17.2 - out['vLead'] == pytest.approx(CAM_SLOW_DV_MAX)


@pytest.mark.parametrize('kw', [
  {'prob': 0.8},                                    # camera not confident
  {'model': vision(d=110.0)},                       # camera on another object (30 m past)
  {'v_ego': 4.0},                                   # stop-and-go
])
def test_no_witness_no_bound(kw):
  cb = CameraSlowBound()
  out = run(cb, 4.0, **kw)
  assert out['vLead'] == pytest.approx(17.2)


def test_close_range_trusts_radar():
  cb = CameraSlowBound()
  for _ in range(frames(4.0)):
    out = step(cb, radar_lead(d=CAM_SLOW_MIN_D - 1.0), vision(d=CAM_SLOW_MIN_D - 1.0))
  assert out['vLead'] == pytest.approx(17.2)


def test_small_disagreement_does_nothing():
  cb = CameraSlowBound()
  for _ in range(frames(4.0)):
    out = step(cb, radar_lead(v=17.2), vision(v=15.5))
  assert out['vLead'] == pytest.approx(17.2)


def test_jitter_shorter_than_hold_does_nothing():
  # 2f8 T536.68 phantom shape: radar speed flips about the camera's, never slower for CAM_SLOW_HOLD_S
  cb = CameraSlowBound()
  flip = frames(CAM_SLOW_HOLD_S) - 2
  for i in range(frames(6.0)):
    slow = (i // flip) % 2 == 0
    out = step(cb, radar_lead(v=23.0 if slow else 18.0), vision(v=20.0))
    assert out['vLead'] in (pytest.approx(23.0), pytest.approx(18.0))


def test_camera_dropout_releases_without_step():
  cb = CameraSlowBound()
  out = run(cb, 4.0)
  prev = out['vLead']
  for _ in range(frames(1.0)):
    out = step(cb, radar_lead(), prob=0.1)
    assert out['vLead'] - prev <= 1.0 * DT_MDL * (17.2 - 11.9) + 1e-6
    prev = out['vLead']
  assert out['vLead'] == pytest.approx(17.2)


def test_track_change_resets():
  cb = CameraSlowBound()
  run(cb, 4.0)
  out = step(cb, radar_lead(tid=57))
  assert out['vLead'] == pytest.approx(17.2) and cb.weights[0] == 0.0


def test_vision_only_lead_untouched():
  cb = CameraSlowBound()
  lead = dict(radar_lead(), radar=False, radarTrackId=-1)
  for _ in range(frames(4.0)):
    out = step(cb, lead)
  assert out['vLead'] == pytest.approx(17.2)


def test_one_frame_dip_does_not_restart_hold():
  # 2f8 T1365.04: the camera-slower gap dipped under CAM_SLOW_DV for single frames; the hold must not restart each time
  cb = CameraSlowBound()
  for i in range(frames(3.0)):
    step(cb, radar_lead(), vision(v=16.0 if i % 6 == 5 else 11.9))
  assert cb.weights[0] > 0.0


def test_camera_lead_past_the_radar_lead_is_another_car():
  # 30a T424 (census pd216): radar 68.4 m, camera lead 78.8 m slowing hard; the old max(10 m, 20 %) matched them
  cb = CameraSlowBound()
  for _ in range(frames(4.0)):
    out = step(cb, radar_lead(d=68.4, v=18.4), vision(d=78.8, v=13.8))
  assert out['vLead'] == pytest.approx(18.4)


def test_route_2f8_t1365_range_match_still_bounds():
  # 2f8 T1365 at its CSB peak: radar 79.8 m, camera 80.7 m
  cb = CameraSlowBound()
  for _ in range(frames(4.0)):
    out = step(cb, radar_lead(d=79.8, v=17.2), vision(d=80.7, v=11.9))
  assert out['vLead'] == pytest.approx(17.2 - CAM_SLOW_DV_MAX)
