from pathlib import Path


ROOT = Path(__file__).parents[3]


def source(path: str) -> str:
  return (ROOT / path).read_text(encoding="utf-8")


def test_controlsd_latches_once_and_shares_resolver_with_vehicle_model():
  controls = source("openpilot/selfdrive/controls/controlsd.py")
  assert "self.VM.nrdr_steer_ratio_resolver = self.steer_ratio_resolver" in controls
  assert "self.VM.sr_curve = None" in controls
  assert "self.steer_ratio_resolver.refresh(self.nrdr_live_params.snapshot, lat_active)" in controls
  assert "refresh_engagement_latches(self, lat_active)" in controls
  assert "self.steer_ratio_resolver.update_comma_ratio(lp, self.sm.valid['vehicleParameters'])" in controls
  assert "steer_ratio = self.steer_ratio_resolver.effective_ratio(CS.steeringAngleDeg)" in controls
  assert controls.index("refresh_engagement_latches(self, lat_active)") < controls.index("self.steer_ratio_resolver.refresh") \
    < controls.index("self.curvature = self.steer_ratio_resolver.calc_curvature")


def test_every_lateral_geometry_seam_delegates_to_shared_resolver():
  expected = {
    "openpilot/selfdrive/controls/lib/latcontrol_pid.py": "desired_angle_no_offset",
    "openpilot/selfdrive/controls/lib/latcontrol_angle.py": "desired_angle_no_offset",
    "openpilot/selfdrive/controls/lib/latcontrol_torque.py": "curvature_deadzone",
    "openpilot/selfdrive/controls/lib/latcontrol_curvature.py": "steer_ratio_resolver.calc_curvature",
    "openpilot/sunnypilot/selfdrive/controls/lib/latcontrol_torque_v0.py": "curvature_deadzone",
    "openpilot/sunnypilot/selfdrive/controls/lib/latcontrol_torque_ext_base.py": "measured_curvature_rate",
  }
  for path, call in expected.items():
    contents = source(path)
    assert 'getattr(VM, "nrdr_steer_ratio_resolver", None)' in contents, path
    assert call in contents, path

  for path in (
    "openpilot/selfdrive/controls/lib/latcontrol_torque.py",
    "openpilot/sunnypilot/selfdrive/controls/lib/latcontrol_torque_v0.py",
  ):
    assert "params.angleOffsetDeg" in source(path), path
  assert "self.update_calculations(CS, VM, desired_lateral_accel, params.angleOffsetDeg)" in source(
    "openpilot/sunnypilot/selfdrive/controls/lib/latcontrol_torque_ext.py"
  )


def test_nnlc_hybrid_keeps_firmware_pid_only_protection():
  hybrid = source("openpilot/sunnypilot/nrdr/latcontrol_clarity_hybrid.py")
  pid = source("openpilot/sunnypilot/nrdr/latcontrol_pid.py")
  assert "pid_extension.firmware_vgr_selected" in hybrid
  assert "return self.steer_ratio_resolver.firmware_vgr_selected" in pid


def test_live_runtime_no_longer_routes_by_model_artifact_policy():
  for path in (
    "openpilot/sunnypilot/nrdr/controlsd.py",
    "openpilot/sunnypilot/nrdr/latcontrol_pid.py",
    "openpilot/sunnypilot/nrdr/steer_ratio_tuning.py",
    "openpilot/sunnypilot/nrdr/car_tune_report.py",
    "openpilot/sunnypilot/sunnylink/capabilities.py",
  ):
    contents = source(path)
    assert "SteerRatioModelPolicy" not in contents, path
    assert "classify_steer_ratio_model" not in contents, path
    assert ".policy" not in contents, path


def test_control_loops_never_write_mode_or_manual_params():
  for path in (
    "openpilot/sunnypilot/nrdr/steer_ratio_tuning.py",
    "openpilot/sunnypilot/nrdr/controlsd.py",
    "openpilot/sunnypilot/nrdr/latcontrol_pid.py",
    "openpilot/selfdrive/controls/controlsd.py",
  ):
    contents = source(path)
    assert '.put("NrdrSteerRatio' not in contents, path
    assert '.put_bool("NrdrSteerRatio' not in contents, path


def test_native_ui_uses_exact_titles_atomic_enum_and_allows_onroad_saves():
  page = source("openpilot/selfdrive/ui/sunnypilot/layouts/settings/nrdr_sub_layouts/steer_ratio_tuning.py")
  for title in (
    "Use Comma Steer Ratio Learner",
    "Use nrdr Steer Ratio Learner",
    "Use Firmware Steer Ratio",
    "Manual Override On-Center Ratio",
    "Manual Override Final Ratio",
  ):
    assert title in page
  assert "if ui_state.engaged:\n      return" not in page
  assert "locked = ui_state.engaged" not in page
  assert 'ui_state.params.put("NrdrSteerRatioMode", int(mode))' in page
  assert 'param="NrdrSteerRatioManualCenter"' in page
  assert 'param="NrdrSteerRatioManualFinal"' in page
  assert "self._mode is SteerRatioMode.MANUAL and self._manual_available()" in page
  assert 'str(ui_state.CP.brand).lower() == "honda"' in page


def test_vehicle_model_page_retains_diagnostic_but_not_old_toggle():
  page = source("openpilot/selfdrive/ui/sunnypilot/layouts/settings/nrdr_sub_layouts/vehicle_model_learning.py")
  assert "Learned Steer Ratio" in page
  assert "Learn Steer Ratio (Auto)" not in page
  assert "NrdrLearnSteerRatio" not in page


def test_handcrafted_profile_and_dungeon_have_no_retired_sr_ownership():
  for path in (
    "openpilot/sunnypilot/nrdr/handcrafted_lateral.py",
    "openpilot/selfdrive/ui/sunnypilot/layouts/settings/nrdr_sub_layouts/pidf_ground.py",
  ):
    contents = source(path)
    for retired in (
      "NrdrLearnSteerRatio", "NrdrLaneChangeEndpointSteerRatio",
      "NrdrSteerRatioCenterClarity", "NrdrSteerRatioOuterClarity",
    ):
      assert retired not in contents, (path, retired)


def test_handcrafted_native_control_is_a_durable_one_shot_without_ui_locks():
  page = source("openpilot/selfdrive/ui/sunnypilot/layouts/settings/nrdr_sub_layouts/lateral_tuning.py")
  assert 'tr("Apply Handcrafted Lateral Profile")' in page
  assert 'tr("WAIT") if ui_state.params.get_bool("NrdrHandcraftedLateralTune") else tr("APPLY")' in page
  assert 'ui_state.params.put_bool("NrdrHandcraftedLateralTune", True, block=True)' in page
  assert "handcrafted_lateral_profile_supported(ui_state.CP, ui_state.CP_SP)" in page
  assert "supported and ui_state.is_offroad() and not pending" in page
  assert "manual changes persist" in page

  for path in (
    "openpilot/selfdrive/ui/sunnypilot/layouts/settings/models.py",
    "openpilot/selfdrive/ui/sunnypilot/layouts/settings/nrdr_sub_layouts/override_tuning.py",
    "openpilot/selfdrive/ui/sunnypilot/layouts/settings/nrdr_sub_layouts/pidf_ground.py",
    "openpilot/selfdrive/ui/sunnypilot/layouts/settings/nrdr_sub_layouts/steer_filters.py",
    "openpilot/selfdrive/ui/sunnypilot/layouts/settings/nrdr_sub_layouts/vehicle_model_learning.py",
    "openpilot/sunnypilot/nrdr/settings.py",
  ):
    assert "NrdrHandcraftedLateralTune" not in source(path), path
