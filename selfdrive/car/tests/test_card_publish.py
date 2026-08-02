from types import SimpleNamespace

from cereal import car, custom
from opendbc.car import structs
from openpilot.selfdrive.car.card import Car


class RecordingPubMaster:
  def __init__(self):
    self.services = []

  def send(self, service, _message):
    self.services.append(service)


def test_car_state_sp_is_published_before_car_state_trigger():
  card = object.__new__(Car)
  card.sm = SimpleNamespace(frame=1, all_checks=lambda _services: True)
  card.pm = RecordingPubMaster()
  card.rk = SimpleNamespace(remaining=0.0)
  card.last_actuators_output = structs.CarControl.Actuators()
  card.can_rcv_cum_timeout_counter = 0

  CS = car.CarState(canValid=True)
  CS_SP = custom.CarStateSP(gasInterceptorState=5)
  card.state_publish(CS, CS_SP, None)

  assert card.pm.services == ["carOutput", "carStateSP", "carState"]
