from unittest.mock import Mock

import pytest

from opendbc.car.structs import car
from openpilot.common.params import Params
from openpilot.sunnypilot.nrdr import athena
from openpilot.system.webrtc import helpers


@pytest.fixture
def params():
  params = Params()
  params.put("CarParamsPersistent", car.CarParams.new_message().to_bytes(), block=True)
  params.put_bool("IsOffroad", True, block=True)
  params.put_bool("LiveViewEnabled", True, block=True)
  return params


def test_remote_pin_lifecycle():
  pin = athena.RemotePin()
  pin.clear(force=True)
  assert pin.set("1234") == {"success": True}
  verified = pin.verify("1234")
  assert verified["success"]
  pin.require_auth(verified["token"])
  assert pin.change("1234", "5678") == {"success": True}
  assert pin.clear(pin="5678") == {"success": True}


def test_start_stream(mocker, params):
  mocker.patch.object(helpers, "wait_for_webrtcd")
  response = Mock(ok=True)
  response.json.return_value = {"sdp": "answer", "type": "answer"}
  post = mocker.patch.object(helpers.requests, "post", return_value=response)

  assert athena._start_stream("offer", True) == response.json.return_value
  assert params.get_bool("IsLiveStreaming")
  post.assert_called_once()


def test_stop_stream(mocker, params):
  params.put_bool("IsLiveStreaming", True, block=True)
  params.put_bool("LiveView", True, block=True)
  post = mocker.patch.object(helpers.requests, "post")
  assert athena._start_stream(enabled=False) == {"success": True}
  assert not params.get_bool("IsLiveStreaming")
  assert not params.get_bool("LiveView")
  post.assert_not_called()


def test_start_stream_rejects_onroad(params):
  params.put_bool("IsOffroad", False, block=True)
  with pytest.raises(Exception, match="unavailable while onroad"):
    athena._start_stream("offer", True)
