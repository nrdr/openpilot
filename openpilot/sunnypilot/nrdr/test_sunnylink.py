from openpilot.sunnypilot.nrdr.sunnylink import ONROAD_BLOCKED_PARAMS, allow_param_write


def test_steer_ratio_contract_can_be_saved_onroad_for_next_engagement():
  for key in ("NrdrSteerRatioMode", "NrdrSteerRatioManualCenter", "NrdrSteerRatioManualFinal"):
    assert allow_param_write(key, onroad=True)
    assert allow_param_write(key, onroad=False)


def test_unrelated_param_write_policy_is_unchanged():
  assert allow_param_write("NrdrLearnStiffness", onroad=True)
  assert not allow_param_write("LongitudinalPersonality", onroad=True)


def test_lane_centering_stack_is_the_complete_additional_onroad_block():
  assert ONROAD_BLOCKED_PARAMS == {
    "LaneCentering",
    "LaneCenteringE2EAuthority",
    "LaneCenteringMinSpeed",
    "LaneCenteringPauseOnSignal",
    "LaneCenterOffset",
    "LongitudinalPersonality",
    "NrdrHandcraftedLateralTune",
  }
  for key in ("LaneCentering", "LaneCenteringE2EAuthority", "LaneCenteringMinSpeed", "LaneCenteringPauseOnSignal", "LaneCenterOffset"):
    assert not allow_param_write(key, onroad=True)
    assert allow_param_write(key, onroad=False)


def test_interpolated_torque_group_can_be_saved_onroad_for_next_engagement():
  for key in (
    "NrdrInterpolatedTorquePifBlend",
    "NrdrInterpolatedTorqueShare",
    "NrdrInterpolatedTorqueLatAccelFactor",
    "NrdrInterpolatedTorqueFriction",
    "NrdrInterpolatedTorqueFrictionStandard",
    "NrdrInterpolatedTorqueFrictionHighway",
  ):
    assert allow_param_write(key, onroad=True)
    assert allow_param_write(key, onroad=False)


def test_handcrafted_one_shot_command_cannot_be_written_onroad():
  assert not allow_param_write("NrdrHandcraftedLateralTune", onroad=True)
  assert allow_param_write("NrdrHandcraftedLateralTune", onroad=False)
