from openpilot.cereal import car
from openpilot.common.params import Params
from openpilot.system.manager.process_config import managed_processes


def test_live_view_starts_webrtcd_offroad():
  params = Params()
  CP = car.CarParams.new_message()
  webrtcd = managed_processes["webrtcd"]

  params.put_bool("LiveView", True, block=True)
  assert webrtcd.should_run(False, params, CP)
  assert not webrtcd.should_run(True, params, CP)

  params.put_bool("LiveView", False, block=True)
  assert not webrtcd.should_run(False, params, CP)

  CP.notCar = True
  assert webrtcd.should_run(True, params, CP)
