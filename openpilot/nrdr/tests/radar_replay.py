"""Shared helpers for the Bosch-A radard and card replay tests (moved out of the retired test_radar_lead_bound.py).

ReplaySubMaster is a SubMaster stand-in fed by update_msgs (the real one needs a live msgq); bosch_a_radard builds a
RadarD on a Bosch-A Honda CP; card_publish drives Car.state_publish with a stub, as nrdr's card merges the radar point
statuses into the one carStateSP per frame.
"""
from types import SimpleNamespace

from opendbc.car import structs
from opendbc.car.honda.values import CAR as HONDA_CAR
from openpilot.cereal import custom, messaging
from openpilot.selfdrive.car.card import Car
from openpilot.selfdrive.controls.radard import RadarD


class ReplaySubMaster:
  """Same bookkeeping radard reads: data, recv_frame, logMonoTime, seen, all_checks."""
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
