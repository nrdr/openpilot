from types import SimpleNamespace

from openpilot.nrdr.features.longitudinal.bosch_a import bosch_a_ghost as G

DT = 0.05


def lead(tid=22, d=20.0, v=-5.0, y=-0.8, v_lead=8.0, a_lead=-1.0, present=True):
  return SimpleNamespace(present=present, radarTrackId=tid, dRel=d, vRel=v, yRel=y, vLeadK=v_lead, aLeadK=a_lead)


GONE = lead(present=False)
CAM_SEES = (0.9, 21.5)   # camera lead 0 still at the ghost
CAM_CLEAR = (0.1, 80.0)


def born(gl, v_ego=13.0, cam=CAM_SEES, **kw):
  assert gl.update(lead(**kw), -3.0, v_ego, {22: -0.8}, cam) == (None, None)
  return gl.update(GONE, -3.0, v_ego, {22: -0.9}, cam)


def test_a_req_physics():
  assert G.ghost_a_req(30.0, 15.0, 0.0, 0.0) < -3.0      # stopped car 30 m ahead at 15 m/s
  assert G.ghost_a_req(30.0, 10.0, 12.0, 0.0) == 0.0     # pulling away
  assert G.ghost_a_req(3.0, 10.0, 10.0, 0.0) == -10.0    # inside the stop gap


def test_dropout_close_keeps_base():
  # 84 s7 shape: 12.5 m, closing 8 m/s, camera still sees it, raw track gone
  gl = G.GhostLetoff(DT)
  jerk, floor = born(gl, v_ego=14.0, d=12.5, v=-8.0, v_lead=6.0)
  assert (jerk, floor) == (None, None) and gl.no_gas  # G3: base let-off until a clear, gas withheld


def test_lateral_exit_clears():
  gl = G.GhostLetoff(DT)
  born(gl)
  assert gl.update(GONE, -2.5, 12.0, {22: -1.6}, CAM_SEES) == (G.FAST_JERK, 0.0)
  assert gl.no_gas
  gl.update(GONE, -1.0, 12.0, {22: -3.1}, CAM_SEES)
  assert not gl.no_gas


def test_camera_clear_needs_dwell():
  gl = G.GhostLetoff(DT)
  born(gl, tid=-1, cam=CAM_CLEAR)  # camera-only lead: the camera clear applies
  n = int(G.CAM_CLEAR_S / DT)
  outs = [gl.update(GONE, -2.0, 12.0, {}, CAM_CLEAR) for _ in range(n + 1)]
  assert outs[-1] == (G.FAST_JERK, 0.0)


def test_camera_clear_blocked_while_radar_track_near_lane():
  # 84 s7 shape: camera loses it, raw track still at 1.27 m, then vanishes there
  gl = G.GhostLetoff(DT)
  born(gl, v_ego=14.0, d=13.9, v=-8.0, v_lead=6.0, y=-1.19, cam=CAM_CLEAR)
  for i in range(int(1.0 / DT)):
    jerk, floor = gl.update(GONE, -3.0, 14.0, {22: -1.27} if i < 6 else {}, CAM_CLEAR)
    assert jerk is None and floor is None and not gl.ghost.letoff_clear
  assert gl.cleared == 0


def test_ghost_behind_us_is_not_a_clear():
  # 84 s7: the extrapolated ghost passed d < 0 at 1.65 s with the car still there; G3 does not call that a clear
  gl = G.GhostLetoff(DT)
  born(gl, v_ego=14.0, d=6.0, v=-8.0, v_lead=6.0, a_lead=-3.0)
  for _ in range(int(0.9 / DT)):  # inside the shortest no-gas hold tried (1.0 s)
    out = gl.update(GONE, -3.0, 14.0, {}, CAM_SEES)
    assert out == (None, None)
  assert gl.ghost.d < 0.0 and not gl.ghost.letoff_clear and gl.no_gas and gl.cleared == 0


def test_camera_clear_allowed_for_far_off_centre_track():
  # 80 s3 shape: leadOne track already 4.3 m out and steady; the camera clears it
  gl = G.GhostLetoff(DT)
  far = lead(d=37.0, v=-11.7, v_lead=10.0, y=-4.3)
  assert gl.update(far, -3.0, 22.0, {22: -4.3}, CAM_CLEAR) == (None, None)
  outs = [gl.update(GONE, -3.0, 22.0, {22: -4.3}, CAM_CLEAR) for _ in range(int(G.CAM_CLEAR_S / DT) + 2)]
  assert outs[-1] == (G.FAST_JERK, 0.0)


def test_lead_back_kills_ghost():
  gl = G.GhostLetoff(DT)
  born(gl)
  assert gl.update(lead(d=19.5), -2.0, 13.0, {22: -0.8}, CAM_SEES) == (None, None)
  assert gl.ghost is None and not gl.no_gas


def test_farther_closing_lead_keeps_ghost():
  # pb c1 s13: the 10.5 m turner releases to a camera lead 25.6 m out closing 1.27 m/s; the turner's track then moves out
  gl = G.GhostLetoff(DT)
  gl.update(lead(tid=23, d=10.5, v=-2.2, y=-0.7), -2.5, 13.2, {23: -0.7}, CAM_SEES)
  assert gl.update(lead(tid=-1, d=25.6, v=-1.27, y=0.9), -2.4, 13.1, {23: -0.8}, CAM_SEES) == (None, None)
  assert gl.ghost is not None
  gl.update(lead(tid=-1, d=26.4, v=-1.06, y=0.9), -2.3, 13.0, {23: -1.0}, CAM_SEES)
  assert gl.ghost is not None
  assert gl.update(lead(tid=-1, d=27.3, v=-1.0, y=0.9), -2.2, 12.9, {23: -1.6}, CAM_SEES) == (G.FAST_JERK, 0.0)


def test_nearer_closing_lead_kills_ghost():
  gl = G.GhostLetoff(DT)
  born(gl)  # ghost born at 20 m
  gl.update(lead(tid=30, d=12.0, v=-3.0), -2.0, 13.0, {22: -0.9, 30: 0.2}, CAM_SEES)
  assert gl.ghost is None and not gl.no_gas


def test_blinker_skips():
  gl = G.GhostLetoff(DT)
  gl.update(lead(), -3.0, 13.0, {22: -0.8}, CAM_SEES)
  assert gl.update(GONE, -3.0, 13.0, {}, CAM_SEES, skip=True) == (None, None)
  assert not gl.no_gas


def test_not_braking_no_ghost():
  gl = G.GhostLetoff(DT)
  gl.update(lead(), 0.2, 13.0, {22: -0.8}, CAM_SEES)
  assert gl.update(GONE, 0.2, 13.0, {}, CAM_SEES) == (None, None)


def test_ghost_expires():
  gl = G.GhostLetoff(DT)
  born(gl, d=60.0, v=-1.0, v_lead=12.0, a_lead=0.0)
  for _ in range(int(G.GHOST_MAX_S / DT) + 2):
    out = gl.update(GONE, -1.0, 13.0, {}, CAM_SEES)
  assert out == (None, None) and not gl.no_gas


def test_smooth_step_without_lead_one_keeps_base_path():
  from openpilot.nrdr.features.longitudinal.bosch_a import bosch_a_smooth as bs
  cp = SimpleNamespace(brand="honda", carFingerprint="HONDA_CIVIC_BOSCH", openpilotLongitudinalControl=True)
  s = bs.BoschASmooth(cp)
  assert s.step(-2.0, -0.5, False) == bs.brake_release_limited_target(-2.0, -0.5, s.dt)


def test_smooth_step_ghost_withholds_gas_and_never_adds_brake():
  from openpilot.nrdr.features.longitudinal.bosch_a import bosch_a_smooth as bs
  cp = SimpleNamespace(brand="honda", carFingerprint="HONDA_CIVIC_BOSCH", openpilotLongitudinalControl=True)
  s = bs.BoschASmooth(cp)
  s.step(-3.0, -3.0, False, lead_one=lead(), raw_y={22: -0.8}, v_ego=13.0, model_lead0=CAM_SEES)
  out = s.step(-3.0, 1.0, False, lead_one=GONE, raw_y={}, v_ego=13.0, model_lead0=CAM_SEES)
  assert s.ghost.no_gas and out <= 0.0
  assert out >= -3.0  # a rise or hold, never more braking than the previous target


def test_raw_track_y_degrades_to_empty():
  assert G.raw_track_y({}) == {}
  rt = SimpleNamespace(points=[SimpleNamespace(trackId=4, yRel=1.25)])

  class SM(dict):
    valid = {'radarTracks': True}
    alive = {'radarTracks': True}
  sm = SM(radarTracks=rt)
  assert G.raw_track_y(sm) == {4: 1.25}
  sm.alive = {'radarTracks': False}
  assert G.raw_track_y(sm) == {}
