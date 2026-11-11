"""Contradicted / passed lead bound and its STATUS carrier (static). Shapes from route 34 T479 (STATUS 9, and the
camera's range contradicting the radar's closing), 2ed T338.6 (a real truck the camera saw late), route 37 T903 (the
model lead moved on past the radar lead and calls for no braking)."""
import math
from types import SimpleNamespace

import pytest

from opendbc.car import structs
from opendbc.car.honda.values import CAR as HONDA_CAR
from openpilot.cereal import custom, messaging
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.car.card import Car
from openpilot.selfdrive.controls.radard import RadarD
from openpilot.nrdr.features.radar import radar_point_status
from openpilot.nrdr.features.radar.bosch_a_lead_policy import URGENT_LAST_DIRECT_S, urgency_v_rel
from openpilot.nrdr.features.radar.radar_lead_bound import (CAMERA_CLOSING_MAX, CAMERA_DECEL_MIN, CAMERA_SELF_TOL,
                                                           CONTRADICTION_FULL, CONTRADICTION_START, DISTANCE_FAR_W, DISTANCE_W,
                                                           RELEASE_S, RISE_S, SLEW_W, TREND_MIN_SAMPLES, TREND_MIN_SPAN_S,
                                                           UNCONFIRMED_W, WeakLeadBound, camera_contradiction,
                                                           camera_passed_ratio, range_slope, tell_weight)
from openpilot.nrdr.features.radar.radar_reversal_bound import W, ReversalBound, urgent
from openpilot.nrdr.tests.test_radar_reversal_bound import ABSENT, V_EGO, radar_lead, reverse, vision


def test_tell_weight():
  assert tell_weight(9, 0.0) == 0.0         # STATUS 9 alone: 8 % of lead time, under three real brakes
  assert tell_weight(9, 0.0, 5.84) == 0.0   # 2ed T338.6, a real truck the camera saw late, at its peak
  assert tell_weight(9, 0.0, 9.85) == UNCONFIRMED_W  # route 34 at +0.5 s
  assert tell_weight(9, 0.0, (CONTRADICTION_START + CONTRADICTION_FULL) / 2) == pytest.approx(UNCONFIRMED_W / 2)
  assert tell_weight(7, 0.0, 9.9) == 0.0    # confirmed
  assert tell_weight(0, 0.0, 9.9) == 0.0    # status not known
  assert tell_weight(3, 0.0, 9.9) == 0.0    # only 9 counts as unconfirmed
  assert tell_weight(7, 0.62) == 0.0  # the largest ratio among the four real far brakes
  assert tell_weight(0, 0.62) == 0.0
  assert tell_weight(7, 0.875) == pytest.approx(DISTANCE_W / 2)
  assert tell_weight(7, 1.02) == DISTANCE_W  # route 37 at the start of the tap
  assert tell_weight(9, 1.02, 9.9) == max(UNCONFIRMED_W, DISTANCE_W)
  assert tell_weight(7, 0.86) == pytest.approx(0.264, abs=0.01)  # route 37 T323 (ambiguous) at its peak: unchanged
  assert tell_weight(7, 1.25) == DISTANCE_W
  assert tell_weight(7, 1.375) == pytest.approx((DISTANCE_W + DISTANCE_FAR_W) / 2)
  assert tell_weight(7, 1.5) == DISTANCE_FAR_W  # b1 seg14 track 4, the model lead ~110 m past a 57-85 m radar point
  assert tell_weight(7, 1.9) == DISTANCE_FAR_W


def test_range_slope():
  assert range_slope([88.0 - 0.75 * k for k in range(31)]) == pytest.approx(-15.0)
  assert range_slope([88.0 - 0.75 * k if k % 3 else math.nan for k in range(31)]) == pytest.approx(-15.0)
  assert math.isnan(range_slope([60.0] * (TREND_MIN_SAMPLES - 1)))
  assert math.isnan(range_slope([60.0] * round(TREND_MIN_SPAN_S / DT_MDL)))  # 12 samples span 0.55 s
  assert range_slope([60.0] * (round(TREND_MIN_SPAN_S / DT_MDL) + 1)) == 0.0
  assert math.isnan(range_slope([math.nan] * 31))


def test_camera_contradiction():
  # (vRel, the track's range slope, the model lead's range slope, its closing, its a) from the logs at 20 Hz
  # route 34 at 0 s: the radar closes 10-17 m/s, the model lead's range 1.3 m/s, matching its closing of 2.9
  assert camera_contradiction(-10.08, -17.09, -1.26, 2.91, 0.04) == pytest.approx(8.82)
  # 2ed T338.6 at 0 s, a real truck the camera saw late: just under the start
  assert camera_contradiction(-8.06, -10.67, -2.22, 2.31, 0.0) == pytest.approx(5.84)
  # 313 T2330.2 (leans real): vRel -11.3, but the track's own range fell 4.0 m/s, near the camera's 3.1
  assert camera_contradiction(-11.28, -3.99, -3.07, 0.62, -0.02) == pytest.approx(0.92)
  # 368 T657.1 (real, stopped traffic): at +1 s the model lead's range rose 17.3 m/s at closing 8.3, so it had jumped
  # to a farther car and is no witness; at -0.7 s it was slowing at -1.14
  assert camera_contradiction(-9.43, -12.53, 17.28, 8.34, -0.46) == 0.0
  assert camera_contradiction(-11.43, -12.53, 10.52, 5.15, -1.14) == 0.0
  assert camera_contradiction(-10.08, -17.09, -1.26, 1.26 + CAMERA_SELF_TOL + 0.1, 0.04) == 0.0
  assert camera_contradiction(-10.08, -17.09, -1.26, 2.91, CAMERA_DECEL_MIN - 0.01) == 0.0
  assert camera_contradiction(-10.08, math.nan, -1.26, 2.91, 0.04) == 0.0  # a track too young for a slope
  assert camera_contradiction(-10.08, -17.09, math.nan, 2.91, 0.04) == 0.0
  assert camera_contradiction(-3.0, -3.0, -2.0, 2.0, 0.0) == pytest.approx(1.0)
  assert camera_contradiction(-1.0, -3.0, -2.0, 2.0, 0.0) == 0.0  # the camera closes faster than the radar


def test_camera_passed_ratio():
  # route 37 T903: SUV at 45 m, the model lead moved on to 62 m, closing 0.5 m/s, a 0
  assert camera_passed_ratio(45.0, 62.0, 0.5, 0.0) == pytest.approx(17.0 / 15.5)
  assert camera_passed_ratio(45.0, 62.0, CAMERA_CLOSING_MAX, CAMERA_DECEL_MIN) == pytest.approx(17.0 / 15.5)
  # route 37 T273: a pickup slowing to turn left at 82 m, the model lead at 109 m closing at 11.7 m/s: a real slowdown
  assert camera_passed_ratio(81.7, 108.8, 11.7, -0.3) == 0.0
  assert camera_passed_ratio(45.0, 62.0, CAMERA_CLOSING_MAX + 0.1, 0.0) == 0.0  # the model lead calls for braking
  assert camera_passed_ratio(45.0, 62.0, 0.5, CAMERA_DECEL_MIN - 0.1) == 0.0
  assert camera_passed_ratio(36.0, 27.5, 0.0, 0.0) == 0.0  # the model lead is nearer than the radar lead
  assert camera_passed_ratio(16.0, 18.0, 0.0, 0.0) == pytest.approx(0.4)  # the 5 m floor


def update(bound, lead, status=7, ratio=0.0, prob=0.95, contradiction=0.0):
  return bound.update([lead, ABSENT], [status, 0], [ratio, 0.0], [prob, 0.0], [contradiction, 0.0])[0]


def test_new_track_takes_its_tell_at_once():
  bound = WeakLeadBound()
  assert update(bound, radar_lead(55, 66.0, 15.0, -3.0), status=9, contradiction=9.9) == UNCONFIRMED_W
  assert update(bound, radar_lead(56, 66.0, 15.0, -3.0), status=7) == 0.0  # and a new confirmed one drops it at once


def test_established_track_rises_and_releases_at_the_slew_rates():
  bound = WeakLeadBound()
  lead = radar_lead(32, 47.0, 28.7, 0.0)
  assert update(bound, lead, ratio=0.5) == 0.0
  rise = SLEW_W * DT_MDL / RISE_S
  assert update(bound, lead, ratio=1.1) == pytest.approx(rise)
  for _ in range(round(RISE_S / DT_MDL)):
    weight = update(bound, lead, ratio=1.1)
  assert weight == pytest.approx(DISTANCE_W)
  release = SLEW_W * DT_MDL / RELEASE_S
  assert update(bound, lead, ratio=0.5) == pytest.approx(DISTANCE_W - release)
  for _ in range(round(RELEASE_S / DT_MDL)):
    weight = update(bound, lead, ratio=0.5)
  assert weight == pytest.approx(0.0, abs=1e-9)


def test_urgent_unwitnessed_and_vision_leads_get_no_weight():
  bound = WeakLeadBound()
  assert update(bound, radar_lead(55, 29.0, 15.0, -3.0), status=9, contradiction=9.9) == 0.0          # under 30 m
  assert update(bound, radar_lead(55, 66.0, V_EGO - 17.0, -3.0), status=9, contradiction=9.9) == 0.0  # TTC 3.9 s
  assert update(bound, radar_lead(55, 66.0, 15.0, -3.0), status=9, contradiction=9.9, prob=0.2) == 0.0
  vision_lead = {'present': True, 'radar': False, 'radarTrackId': -1, 'dRel': 66.0, 'vRel': -7.0,
                 'vLead': 15.0, 'vLeadK': 15.0, 'aLeadK': -3.0}
  assert update(bound, vision_lead, status=9, contradiction=9.9) == 0.0


def test_floor_weight_blends_once_at_the_larger_weight():
  raw = radar_lead(32, 47.0, 24.8, -2.9)  # route 37: vLead dipped to 24.8 while the model lead held 29, a 0
  model = vision(29.0, 0.0)
  rb = ReversalBound()
  out = rb.apply([raw, ABSENT], [model, vision()], V_EGO, V_EGO, [0.95, 0.0], {32: None}, floor_weights=(0.3, 0.0))[0]
  assert out['vLead'] == pytest.approx(24.8 + 0.3 * (29.0 - 24.8))
  assert out['vRel'] == pytest.approx(out['vLead'] - V_EGO)
  assert out['aLeadK'] == pytest.approx(-2.9 + 0.3 * 2.9)
  assert out['dRel'] == raw['dRel'] and out['present'] and out['radar'] and rb.weights[0] == 0.3
  rb = ReversalBound()
  reverse(rb, tid=32, d=47.0)
  out = rb.apply([raw, ABSENT], [model, vision()], V_EGO, V_EGO, [0.95, 0.0], {32: None}, floor_weights=(0.3, 0.0))[0]
  assert rb.weights[0] == W and out['vLead'] == pytest.approx(24.8 + W * (29.0 - 24.8))


class FakeSM(dict):
  def __init__(self, events):
    super().__init__({event.which(): getattr(event, event.which()) for event in events})
    self.logMonoTime = {event.which(): event.logMonoTime for event in events}


def companion(stamp, statuses, tracks_stamp=None):
  event = messaging.new_message('carStateSP', valid=True)
  event.logMonoTime = stamp
  radar_point_status.write(event.carStateSP, stamp if tracks_stamp is None else tracks_stamp, statuses)
  return event.as_reader()


def tracks(stamp):
  event = messaging.new_message('radarTracks', valid=True)
  event.logMonoTime = stamp
  return event.as_reader()


def test_point_status_round_trip_and_pairing():
  stamp = 5_000_000_000
  assert radar_point_status.read(FakeSM([tracks(stamp), companion(stamp, {60: 7, 55: 9})])) == {55: 9, 60: 7}
  late = stamp + radar_point_status.PAIR_TOLERANCE_NS + 1
  assert radar_point_status.read(FakeSM([tracks(late), companion(stamp, {55: 9})])) == {}
  assert radar_point_status.read(FakeSM([tracks(stamp), companion(stamp, {55: 9}, tracks_stamp=0)])) == {}
  assert radar_point_status.read(FakeSM([tracks(stamp)])) == {}  # no carrier: other radars, older logs


class FakePM:
  def __init__(self):
    self.sent = []

  def send(self, service, message):
    self.sent.append((service, message.as_reader() if hasattr(message, 'as_reader') else message))


def one_point():
  rr = structs.RadarData()
  point = rr.init('points', 1)[0]
  point.trackId = 55
  point.dRel = 66.0
  return rr


def card_publish(statuses, radar_data):
  card = object.__new__(Car)
  card.sm = SimpleNamespace(frame=1, all_checks=lambda _services: True)
  card.pm = FakePM()
  card.rk = SimpleNamespace(remaining=0.0)
  card.last_actuators_output = structs.CarControl.Actuators()
  card.can_rcv_cum_timeout_counter = 0
  card.RI = SimpleNamespace(point_statuses=statuses) if statuses is not None else SimpleNamespace()
  card.state_publish(structs.CarState(canValid=True), custom.CarStateSP(), radar_data)
  return card


def test_card_sends_the_statuses_on_car_state_sp_stamped_with_the_tracks_they_describe():
  # nrdr merges the statuses into the one carStateSP per frame (no second carStateSP message); order is unchanged
  card = card_publish({55: 9}, one_point())
  assert [service for service, _ in card.pm.sent] == ['carOutput', 'carStateSP', 'carState', 'radarTracks']
  status_msg = dict(card.pm.sent)['carStateSP']
  tracks_msg = dict(card.pm.sent)['radarTracks']
  assert status_msg.carStateSP.radarTracksMonoTime == tracks_msg.logMonoTime > 0
  assert [(row.trackId, row.objectStatus) for row in status_msg.carStateSP.radarPointStatus] == [(55, 9)]
  assert card.radar_point_status == (tracks_msg.logMonoTime, {55: 9})


def test_card_sends_no_statuses_for_other_radars():
  card = card_publish(None, one_point())
  assert [service for service, _ in card.pm.sent] == ['carOutput', 'carStateSP', 'carState', 'radarTracks']
  status_msg = dict(card.pm.sent)['carStateSP']
  assert status_msg.carStateSP.radarTracksMonoTime == 0 and len(status_msg.carStateSP.radarPointStatus) == 0


class ReplaySubMaster:
  """SubMaster stand-in fed by update_msgs, with no sockets (the real one needs a live msgq).

  Same bookkeeping radard reads: data, recv_frame, logMonoTime, seen, all_checks.
  """
  def __init__(self, services):
    self.frame = -1
    self.data = {s: getattr(messaging.new_message(s), s).as_reader() for s in services}
    self.recv_frame = dict.fromkeys(services, 0)
    self.logMonoTime = dict.fromkeys(services, 0)
    self.seen = dict.fromkeys(services, False)

  def __getitem__(self, service):
    return self.data[service]

  def update_msgs(self, _current_time, msgs):
    self.frame += 1
    for event in msgs:
      service = event.which()
      if service in self.data:
        self.data[service] = getattr(event, service)
        self.recv_frame[service] = self.frame
        self.logMonoTime[service] = event.logMonoTime
        self.seen[service] = True

  def all_checks(self, *_args, **_kwargs):
    return True


def bosch_a_radard(delay=0.0):
  CP = SimpleNamespace(brand='honda', radarUnavailable=False, carFingerprint=HONDA_CAR.HONDA_CIVIC_BOSCH, radarDelay=delay)
  return RadarD(CP, SimpleNamespace(flags=0), delay)


def radard_tick(sm, tick, statuses, v_lead=5.4, d_rel=66.0, v_ego=16.0, track_id=55, model_x=None, model_v=13.5):
  stamp = 1_000_000_000 + tick * 50_000_000
  model_event = messaging.new_message('modelV2', valid=True)
  model_event.logMonoTime = stamp
  model_event.modelV2.velocity.x = [v_ego]
  for lead in model_event.modelV2.init('leadsV3', 2):
    lead.x = [d_rel + 1.52 if model_x is None else model_x]
    lead.y = [0.0]
    lead.v = [model_v]
    lead.a = [0.0]
    lead.xStd = lead.yStd = lead.vStd = [1.0]
    lead.prob = 0.99
  car_event = messaging.new_message('carState', valid=True)
  car_event.logMonoTime = stamp
  car_event.carState.vEgo = v_ego
  radar_event = messaging.new_message('radarTracks', valid=True)
  radar_event.logMonoTime = stamp
  point = radar_event.radarTracks.init('points', 1)[0]
  point.trackId = track_id
  point.dRel = d_rel
  point.vRel = v_lead - v_ego
  point.deprecated.measured = True
  events = [model_event.as_reader(), car_event.as_reader(), radar_event.as_reader()]
  if statuses is not None:
    events.append(companion(stamp, statuses))
  sm.update_msgs(stamp / 1e9, events)


def run_radard(statuses, ticks=60, shape=lambda tick: {}):
  sm = ReplaySubMaster(['modelV2', 'carState', 'radarTracks', 'carStateSP'])
  radar = bosch_a_radard()
  for tick in range(ticks):
    radard_tick(sm, tick, statuses, **shape(tick))
    radar.update(sm, sm['radarTracks'])
  return radar


def route_34_shape(camera_range_rate, model_v):
  def shape(tick):
    # track 55 sweeps in at 15 m/s reading vRel -10.6; at the end 50.8 m, TTC 4.8 s, so never urgent
    return {'d_rel': 95.0 - 0.75 * tick, 'model_x': 63.0 + 1.52 + camera_range_rate * tick * DT_MDL, 'model_v': model_v}
  return shape


def test_route_34_shape_through_radard():
  # route 34: the model lead's range holds at 63 m and it reads 13.5 m/s (closing 2.5), a 0
  shape = route_34_shape(0.0, 13.5)
  plain = run_radard(None, shape=shape).radar_state.leadOne
  assert plain.radar and plain.radarTrackId == 55
  confirmed = run_radard({55: 7}, shape=shape).radar_state.leadOne
  assert confirmed.to_dict() == plain.to_dict()  # confirmed: as before the carrier
  unconfirmed = run_radard({55: 9}, shape=shape)
  bounded = unconfirmed.radar_state.leadOne
  assert unconfirmed.tracks[55].objectStatus == 9
  assert bounded.radar and bounded.radarTrackId == 55 and bounded.dRel == plain.dRel
  assert bounded.vLead == pytest.approx(plain.vLead + UNCONFIRMED_W * (13.5 - plain.vLead), abs=0.05)


def test_unconfirmed_lead_the_camera_backs_is_not_bounded():
  # a real lead the camera sees late, like 2ed T338.6 (5.84 m/s there): its range falls 5 m/s at closing 3, so the
  # radar's vRel -10.6 runs 5.6 m/s ahead of it, under the start
  shape = route_34_shape(-5.0, 13.0)
  plain = run_radard(None, shape=shape).radar_state.leadOne
  assert plain.radar and plain.radarTrackId == 55
  assert run_radard({55: 9}, shape=shape).radar_state.leadOne.to_dict() == plain.to_dict()


def route_37_shape(model_v):
  def shape(tick):
    if tick < 30:  # the SUV ahead at 53 m, matched through the strict gate
      return {'track_id': 32, 'd_rel': 53.0, 'v_lead': 28.6, 'v_ego': 29.8, 'model_x': 53.0 + 1.52, 'model_v': 28.6}
    # it moves out: the radar reads it slowing to 25.3 at 45 m while the model lead moves on to 64 m
    return {'track_id': 32, 'd_rel': 45.0, 'v_lead': 25.3, 'v_ego': 29.8, 'model_x': 64.0 + 1.52, 'model_v': model_v}
  return shape


def test_route_37_shape_through_radard():
  # control: the model lead closing at 11.7 m/s calls for braking itself (route 37 T273's pickup): no bound
  plain = run_radard(None, shape=route_37_shape(18.1)).radar_state.leadOne
  assert plain.radar and plain.radarTrackId == 32 and plain.vLead < 26.0
  bounded = run_radard(None, shape=route_37_shape(29.3)).radar_state.leadOne  # route 37 T903: closing 0.5 m/s
  assert bounded.radar and bounded.radarTrackId == 32 and bounded.dRel == plain.dRel
  assert bounded.vLead == pytest.approx(plain.vLead + DISTANCE_W * (29.3 - plain.vLead), abs=0.05)


def test_urgency_uses_the_last_direct_reading_on_an_unmeasured_point():
  # b1 seg14 47.7 s: track 4 at 69 m, last direct reading -11.7, then the parser's floor estimate -31 (TTC 2.2 s)
  floor = radar_lead(4, 69.0, V_EGO - 31.0, -3.0)
  assert urgent(floor) and not urgent(floor, -11.7)
  assert urgent(floor, -17.5)                              # TTC 3.9 s on a fast last reading: still urgent
  assert urgent(radar_lead(4, 29.0, V_EGO - 1.0, -3.0), -1.0)  # under 30 m stays urgent whatever the speed
  hop = [90.0 - 0.75 * k for k in range(31)]               # range falling 15 m/s: a reflector hop, not used
  track = SimpleNamespace(direct=False, last_direct_vrel=-11.7, direct_age=5, range_history=hop)
  assert urgency_v_rel(track) == -11.7                     # the range slope does not override the last reading
  track.direct_age = round(URGENT_LAST_DIRECT_S / DT_MDL) + 1
  assert urgency_v_rel(track) is None                      # too old: the published vRel, as before
  track.direct_age, track.last_direct_vrel = 5, math.nan
  assert urgency_v_rel(track) is None                      # never measured: the published vRel
  track.direct, track.last_direct_vrel = True, -11.7
  assert urgency_v_rel(track) is None                      # a direct reading: the published vRel
  assert urgency_v_rel(None) is None


def test_bounds_keep_their_weight_when_only_the_floor_estimate_is_urgent():
  floor = radar_lead(4, 69.0, V_EGO - 31.0, -3.0)
  bound = WeakLeadBound()
  assert bound.update([floor, ABSENT], [9, 0], [0.0, 0.0], [0.95, 0.0], [9.9, 0.0]) == [0.0, 0.0]
  bound = WeakLeadBound()
  assert bound.update([floor, ABSENT], [9, 0], [0.0, 0.0], [0.95, 0.0], [9.9, 0.0], [-11.7, None])[0] == UNCONFIRMED_W
  model = vision(21.5, 0.0)
  rb = ReversalBound()
  assert rb.apply([floor, ABSENT], [model, vision()], V_EGO, V_EGO, [0.95, 0.0], {4: None}, floor_weights=(0.6, 0.0))[0] == floor
  out = rb.apply([floor, ABSENT], [model, vision()], V_EGO, V_EGO, [0.95, 0.0], {4: None}, floor_weights=(0.6, 0.0),
                 urgent_v_rels=(-11.7, None))[0]
  assert rb.weights[0] == 0.6 and out['dRel'] == floor['dRel'] and out['present'] and out['radar']
  assert out['vLead'] == pytest.approx(floor['vLead'] + 0.6 * (21.5 - floor['vLead']))

