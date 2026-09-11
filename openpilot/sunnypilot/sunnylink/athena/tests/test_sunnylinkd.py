"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import base64
import gzip

from openpilot.sunnypilot.sunnylink.athena import sunnylinkd
from openpilot.common.test import OpenpilotTestCase
from openpilot.nrdr.features.services.sunnylink import HONDA_TUNING_WRITE_KEYS, ONROAD_WRITE_BLOCKLIST, allow_param_write


def remote_value(value: str, *, compression: bool = False) -> str:
  raw = value.encode()
  if compression:
    raw = gzip.compress(raw)
  return base64.b64encode(raw).decode()


class TestSunnylinkdMethods(OpenpilotTestCase):
  def setup_method(self):
    self.saved_params = []
    self.params_writes = []

    self.original_save = sunnylinkd.save_param_from_base64_encoded_string
    self.original_params = sunnylinkd.params
    self.original_generate_capabilities = sunnylinkd.generate_capabilities

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
    sunnylinkd.generate_capabilities = lambda _: {
      "has_handcrafted_lateral_profile": True,
      "nrdr_honda_tuning_available": True,
    }

    def mock_save_param(key, value, compression=False):
      self.saved_params.append((key, value, compression))

    sunnylinkd.save_param_from_base64_encoded_string = mock_save_param  # ty: ignore[invalid-assignment]

  def teardown_method(self):
    sunnylinkd.save_param_from_base64_encoded_string = self.original_save  # ty: ignore[invalid-assignment]
    sunnylinkd.params = self.original_params
    sunnylinkd.generate_capabilities = self.original_generate_capabilities

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

  def test_saveParams_blocks_lane_centering_stack_onroad(self):
    self.fake_params.offroad = False
    lane_centering = {
      "LaneCentering": "1",
      "LaneCenteringMinSpeed": "50",
      "LaneCenteringPauseOnSignal": "0",
      "LaneCenterOffset": "0.12",
      "LaneCenteringStrength": "0.30",
      "LaneCenteringE2EAuthority": "0.45",
    }

    sunnylinkd.saveParams({**lane_centering, "SpeedLimitOffset": "10"})

    assert self.saved_params == [("SpeedLimitOffset", "10", False)]

  def test_saveParams_allows_lane_centering_stack_offroad(self):
    lane_centering = {
      "LaneCentering": "1",
      "LaneCenteringMinSpeed": "50",
      "LaneCenteringPauseOnSignal": "0",
      "LaneCenterOffset": "0.12",
      "LaneCenteringStrength": "0.30",
      "LaneCenteringE2EAuthority": "0.45",
    }

    sunnylinkd.saveParams(lane_centering)

    assert self.saved_params == [(key, value, False) for key, value in lane_centering.items()]

  def test_lane_centering_strength_is_vehicle_agnostic_but_still_offroad_only(self):
    sunnylinkd.generate_capabilities = lambda _: {
      "has_handcrafted_lateral_profile": False,
      "nrdr_honda_tuning_available": False,
    }

    sunnylinkd.saveParams({"LaneCenteringStrength": "0.55"})
    assert self.saved_params == [("LaneCenteringStrength", "0.55", False)]

    self.saved_params.clear()
    self.fake_params.offroad = False
    sunnylinkd.saveParams({"LaneCenteringStrength": "0.60"})
    assert self.saved_params == []

  def test_saveParams_allows_complete_steer_ratio_snapshot_onroad(self):
    self.fake_params.offroad = False

    values = {
      "NrdrSteerRatioMode": "2",
      "NrdrSteerRatioManualCenter": "15.38",
      "NrdrSteerRatioManualFinal": "10.93",
      "SpeedLimitOffset": "10",
    }
    sunnylinkd.saveParams(values)

    assert self.saved_params == [(key, value, False) for key, value in values.items()]

  def test_saveParams_allows_complete_interpolated_torque_snapshot_onroad(self):
    self.fake_params.offroad = False

    values = {
      "NrdrInterpolatedTorquePifBlend": "1",
      "NrdrInterpolatedTorqueShare": "60",
      "NrdrInterpolatedTorqueLatAccelFactor": "5.0",
      "NrdrInterpolatedTorqueFriction": "0.50",
      "NrdrInterpolatedTorqueFrictionStandard": "0.30",
      "NrdrInterpolatedTorqueFrictionHighway": "0.12",
      "SpeedLimitOffset": "10",
    }
    sunnylinkd.saveParams(values)

    assert self.saved_params == [(key, value, False) for key, value in values.items()]

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

  def test_latched_lateral_write_policy_allows_onroad_saves(self):
    for key in (
      "NrdrSteerRatioMode",
      "NrdrSteerRatioManualCenter",
      "NrdrSteerRatioManualFinal",
      "NrdrInterpolatedTorquePifBlend",
      "NrdrInterpolatedTorqueShare",
      "NrdrInterpolatedTorqueLatAccelFactor",
      "NrdrInterpolatedTorqueFriction",
      "NrdrInterpolatedTorqueFrictionStandard",
      "NrdrInterpolatedTorqueFrictionHighway",
    ):
      assert allow_param_write(key, onroad=True, honda_tuning_available=True)
      assert allow_param_write(key, onroad=False, honda_tuning_available=True)

  def test_honda_tuning_cohort_is_fail_closed_for_every_remote_write(self):
    assert len(HONDA_TUNING_WRITE_KEYS) == 51
    for key in HONDA_TUNING_WRITE_KEYS:
      assert allow_param_write(key, onroad=False, honda_tuning_available=True)
      assert allow_param_write(key, onroad=True, honda_tuning_available=True)
      assert not allow_param_write(key, onroad=False, honda_tuning_available=False)
      assert not allow_param_write(key, onroad=False, honda_tuning_available=None)

  def test_saveParams_rejects_honda_tuning_for_confirmed_non_honda(self):
    sunnylinkd.generate_capabilities = lambda _: {
      "has_handcrafted_lateral_profile": False,
      "nrdr_honda_tuning_available": False,
    }
    values = dict.fromkeys(HONDA_TUNING_WRITE_KEYS, "unchanged")
    values["SpeedLimitOffset"] = "10"

    sunnylinkd.saveParams(values)

    assert self.saved_params == [("SpeedLimitOffset", "10", False)]

  def test_onroad_blocklist_is_exact(self):
    assert ONROAD_WRITE_BLOCKLIST == frozenset((
      "LaneCentering",
      "LaneCenteringE2EAuthority",
      "LaneCenteringMinSpeed",
      "LaneCenteringPauseOnSignal",
      "LaneCenteringStrength",
      "LaneCenterOffset",
      "LongitudinalPersonality",
      "NrdrHandcraftedLateralTune",
    ))

  def test_handcrafted_apply_command_is_server_enforced_by_road_and_vehicle(self):
    key = "NrdrHandcraftedLateralTune"
    assert not allow_param_write(key, onroad=True, handcrafted_profile_available=True, requested_bool=True)
    assert not allow_param_write(key, onroad=True, handcrafted_profile_available=False, requested_bool=False)
    assert allow_param_write(key, onroad=False, handcrafted_profile_available=True, requested_bool=True)
    assert not allow_param_write(key, onroad=False, handcrafted_profile_available=False, requested_bool=True)
    assert not allow_param_write(key, onroad=False, handcrafted_profile_available=None, requested_bool=True)
    assert allow_param_write(key, onroad=False, handcrafted_profile_available=False, requested_bool=False)
    assert not allow_param_write(key, onroad=False, handcrafted_profile_available=True, requested_bool=None)

  def test_saveParams_accepts_supported_handcrafted_request_offroad(self):
    encoded = remote_value("1")

    sunnylinkd.saveParams({"NrdrHandcraftedLateralTune": encoded})

    assert self.saved_params == [("NrdrHandcraftedLateralTune", encoded, False)]

  def test_saveParams_rejects_unsupported_handcrafted_enable_but_allows_cancel(self):
    sunnylinkd.generate_capabilities = lambda _: {
      "has_handcrafted_lateral_profile": False,
      "nrdr_honda_tuning_available": False,
    }
    enabled = remote_value("true")
    disabled = remote_value("false")

    sunnylinkd.saveParams({"NrdrHandcraftedLateralTune": enabled})
    assert self.saved_params == []

    sunnylinkd.saveParams({"NrdrHandcraftedLateralTune": disabled})
    assert self.saved_params == [("NrdrHandcraftedLateralTune", disabled, False)]

  def test_saveParams_fails_closed_on_unknown_capability_or_malformed_bool(self):
    key = "NrdrHandcraftedLateralTune"
    sunnylinkd.generate_capabilities = lambda _: {}
    sunnylinkd.saveParams({key: remote_value("1")})
    sunnylinkd.generate_capabilities = lambda _: {
      "has_handcrafted_lateral_profile": True,
      "nrdr_honda_tuning_available": True,
    }
    sunnylinkd.saveParams({key: remote_value("not-a-bool")})
    sunnylinkd.saveParams({key: "%%%not-base64%%%"})

    assert self.saved_params == []

  def test_saveParams_enforces_vehicle_policy_for_compressed_values(self):
    key = "NrdrHandcraftedLateralTune"
    encoded = remote_value("yes", compression=True)

    sunnylinkd.saveParams({key: encoded}, compression=True)

    assert self.saved_params == [(key, encoded, True)]
