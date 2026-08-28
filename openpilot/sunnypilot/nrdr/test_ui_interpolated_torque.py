from pathlib import Path


def test_local_interpolated_torque_controls_have_shared_support_and_engagement_gate():
  root = Path(__file__).resolve().parents[3]
  source = (
    root / "openpilot/selfdrive/ui/sunnypilot/layouts/settings/nrdr_sub_layouts/pidf_ground.py"
  ).read_text(encoding="utf-8")

  for key in (
    "NrdrInterpolatedTorquePifBlend",
    "NrdrInterpolatedTorqueShare",
    "NrdrInterpolatedTorqueLatAccelFactor",
    "NrdrInterpolatedTorqueFriction",
  ):
    assert f'param="{key}"' in source

  assert "is_interpolated_torque_pif_supported(ui_state.CP, ui_state.CP_SP)" in source
  assert "interpolated_supported and not ui_state.engaged" in source
  assert "item.set_visible(interpolated_supported)" in source
  assert "interpolated_unlocked and interpolated_enabled" in source
  assert "not firmware_vgr_active and not interpolated_enabled" in source
  assert 'title=tr("Interpolated Torque/PIF Blend")' in source
  assert "complete steering-angle P/I/F answer" in source
  assert "the final answer temporarily becomes exact P/I/F" in source
  assert "Torque state holds until yaw returns" in source
  assert "angle is not substituted" in source
  assert "historically road-proven on Honda" in source
  assert "It scales Torque error and feedforward, but not friction" in source
  assert 'f"Torque {value}% / P/I/F {100 - value}%"' in source
  assert source.index("self._interpolated_torque_pif_blend,", source.index("return [")) \
    < source.index("self._starpilot,", source.index("return ["))
