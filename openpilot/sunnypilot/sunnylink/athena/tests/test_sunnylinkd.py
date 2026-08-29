"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.sunnypilot.sunnylink.athena import sunnylinkd
from openpilot.common.test import OpenpilotTestCase
from openpilot.nrdr.features.services.sunnylink import allow_param_write


class TestSunnylinkdMethods(OpenpilotTestCase):
  def setup_method(self):
    self.saved_params = []
    self.params_writes = []

    self.original_save = sunnylinkd.save_param_from_base64_encoded_string
    self.original_params = sunnylinkd.params

    class FakeParams:
      offroad = True

      def get_bool(inner_self, key):
        assert key == "IsOffroad"
        return inner_self.offroad

      def get(inner_self, key):
        assert key == "ParamsVersion"
        return None

      def put(inner_self, key, value, block=False):
        self.params_writes.append((key, value, block))

    self.fake_params = FakeParams()
    sunnylinkd.params = self.fake_params

    def mock_save_param(key, value, compression=False):
      self.saved_params.append((key, value, compression))

    sunnylinkd.save_param_from_base64_encoded_string = mock_save_param  # ty: ignore[invalid-assignment]

  def teardown_method(self):
    sunnylinkd.save_param_from_base64_encoded_string = self.original_save  # ty: ignore[invalid-assignment]
    sunnylinkd.params = self.original_params

  def test_saveParams_blocked(self):
    blocked_params = {
      "GithubUsername": "attacker",
      "GithubSshKeys": "ssh-rsa attacker_key",
    }

    sunnylinkd.saveParams(blocked_params)

    assert len(self.saved_params) == 0

  def test_saveParams_allowed(self):
    allowed_params = {
      "SpeedLimitOffset": "5",
      "MyCustomParam": "123"
    }

    sunnylinkd.saveParams(allowed_params)

    # verify content
    assert len(self.saved_params) == 2
    keys_saved = [p[0] for p in self.saved_params]
    assert "SpeedLimitOffset" in keys_saved
    assert "MyCustomParam" in keys_saved

  def test_saveParams_mixed(self):
    mixed_params = {
      "GithubUsername": "attacker",
      "SpeedLimitOffset": "10"
    }

    sunnylinkd.saveParams(mixed_params)

    # should save allowed one
    assert len(self.saved_params) == 1
    assert self.saved_params[0][0] == "SpeedLimitOffset"
    assert self.saved_params[0][1] == "10"

  def test_saveParams_blocks_personality_onroad(self):
    self.fake_params.offroad = False

    sunnylinkd.saveParams({
      "LongitudinalPersonality": "3",
      "SpeedLimitOffset": "10",
    })

    assert self.saved_params == [("SpeedLimitOffset", "10", False)]

  def test_saveParams_blocks_complete_steer_ratio_snapshot_onroad(self):
    self.fake_params.offroad = False

    sunnylinkd.saveParams({
      "NrdrSteerRatioMode": "2",
      "NrdrSteerRatioManualCenter": "15.38",
      "NrdrSteerRatioManualFinal": "10.93",
      "SpeedLimitOffset": "10",
    })

    assert self.saved_params == [("SpeedLimitOffset", "10", False)]

  def test_saveParams_blocks_complete_interpolated_torque_snapshot_onroad(self):
    self.fake_params.offroad = False

    sunnylinkd.saveParams({
      "NrdrInterpolatedTorquePifBlend": "1",
      "NrdrInterpolatedTorqueShare": "60",
      "NrdrInterpolatedTorqueLatAccelFactor": "5.0",
      "NrdrInterpolatedTorqueFriction": "0.50",
      "NrdrInterpolatedTorqueFrictionStandard": "0.30",
      "NrdrInterpolatedTorqueFrictionHighway": "0.12",
      "SpeedLimitOffset": "10",
    })

    assert self.saved_params == [("SpeedLimitOffset", "10", False)]

  def test_saveParams_allows_complete_interpolated_torque_snapshot_offroad(self):
    values = {
      "NrdrInterpolatedTorquePifBlend": "1",
      "NrdrInterpolatedTorqueShare": "60",
      "NrdrInterpolatedTorqueLatAccelFactor": "5.0",
      "NrdrInterpolatedTorqueFriction": "0.50",
      "NrdrInterpolatedTorqueFrictionStandard": "0.30",
      "NrdrInterpolatedTorqueFrictionHighway": "0.12",
    }

    sunnylinkd.saveParams(values)

    assert self.saved_params == [(key, value, False) for key, value in values.items()]

  def test_interpolated_torque_write_policy_is_server_enforced(self):
    for key in (
      "NrdrInterpolatedTorquePifBlend",
      "NrdrInterpolatedTorqueShare",
      "NrdrInterpolatedTorqueLatAccelFactor",
      "NrdrInterpolatedTorqueFriction",
      "NrdrInterpolatedTorqueFrictionStandard",
      "NrdrInterpolatedTorqueFrictionHighway",
    ):
      assert not allow_param_write(key, onroad=True)
      assert allow_param_write(key, onroad=False)

  def test_handcrafted_apply_command_is_server_enforced_offroad_only(self):
    assert not allow_param_write("NrdrHandcraftedLateralTune", onroad=True)
    assert allow_param_write("NrdrHandcraftedLateralTune", onroad=False)
