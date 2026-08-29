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
    "NrdrInterpolatedTorqueFrictionStandard",
    "NrdrInterpolatedTorqueFrictionHighway",
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
  assert "All six settings stay fixed for one" in source
  assert "It scales Torque error and feedforward, but not any friction band" in source
  assert 'tr("Low-Speed Torque Friction (Below 25mph)")' in source
  assert 'tr("Standard-Speed Torque Friction (25-50mph)")' in source
  assert 'tr("Highway Torque Friction (50mph+)")' in source
  assert "Default 0.12" in source
  assert "Default 0.10" in source
  assert "Default 0.06" in source
  assert "24-26 mph (±1 mph around 25)" in source
  assert "fully active from 26-49 mph" in source
  assert "49-51 mph (±1 mph around 50)" in source
  assert source.count("independent of the lateral acceleration factor") == 3
  assert source.count("latch for the whole engagement") == 3
  assert 'f"Torque {value}% / P/I/F {100 - value}%"' in source
  assert source.index("self._interpolated_torque_pif_blend,", source.index("return [")) \
    < source.index("self._starpilot,", source.index("return ["))
