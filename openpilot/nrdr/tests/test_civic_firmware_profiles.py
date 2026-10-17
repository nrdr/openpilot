"""Civic calibration and the explicit TEG exception, without CAN/IPC/settings writes."""
import math
from pathlib import Path
from types import SimpleNamespace as NS

import numpy as np
import pytest

from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.nrdr.features.lateral.controller_selection import (
  CIVIC_PROFILE, CLARITY_PROFILE, INSIGHT_PROFILE, TEG_PROFILE, firmware_controller_profile,
  firmware_controller_selected,
)
from openpilot.nrdr.features.lateral import vfn_eps_core as core
from openpilot.nrdr.features.lateral.yaw_control_timing import command_delay, prediction_delay_schedule
from openpilot.nrdr.params.tuning_policy import tuning_write_allowed
from openpilot.nrdr.ui.sunnylink_schema import apply_sunnylink_metadata


def car(fingerprint, firmware, *, modified=True, tuning="pid", brand="honda"):
  return (NS(brand=brand, carFingerprint=fingerprint, lateralTuning=NS(which=lambda: tuning),
             carFw=[NS(ecu="eps", fwVersion=firmware)]),
          NS(flags=HondaFlagsSP.EPS_MODIFIED.value if modified else 0))


@pytest.mark.parametrize("fingerprint,firmware,profile", [
  ("HONDA_CLARITY", b"39990-TRW-A020\0", CLARITY_PROFILE),
  ("HONDA_CIVIC_BOSCH", b"39990-TBA,C020", CIVIC_PROFILE),
  ("HONDA_CIVIC", b"39990-TEG,A010\0", TEG_PROFILE),
  ("HONDA_INSIGHT", b"39990-TXM,A040\0", INSIGHT_PROFILE),
])
def test_exact_profiles_and_selected_controller(fingerprint, firmware, profile):
  cp, sp = car(fingerprint, firmware)
  assert firmware_controller_profile(cp, sp) is profile
  for value in (1, "1", b"1"):
    assert firmware_controller_selected({"NrdrLateralController": value}, cp, sp)
  assert not firmware_controller_selected({"NrdrLateralController": 0}, cp, sp)
  assert profile.provisional == (profile is TEG_PROFILE)


@pytest.mark.parametrize("fingerprint,firmware", [
  ("HONDA_CIVIC", b"39990-TBA-A030"), ("HONDA_CIVIC", b"39990-TBA-C020"),
  ("HONDA_CIVIC_BOSCH", b"39990-TEG-A010"), ("HONDA_CIVIC_BOSCH", b"39990-TBA-C120"),
  ("HONDA_CIVIC_BOSCH", b"39990-TGG-A120"), ("HONDA_CIVIC_2022", b"39990-TEG-A010"),
  ("HONDA_CIVIC_BOSCH_DIESEL", b"39990-TBA-C020"), ("HONDA_CRV_5G", b"39990-TLA-A040"),
  ("HONDA_CLARITY", b"39990-TRW-A010"), ("LEXUS_ES_TSS2", b"39990-TEG-A010"),
])
def test_other_known_vgrs_do_not_inherit_the_c020_exception(fingerprint, firmware):
  cp, sp = car(fingerprint, firmware)
  assert firmware_controller_profile(cp, sp) is None
  assert not firmware_controller_selected({"NrdrLateralController": 1}, cp, sp)


@pytest.mark.parametrize("changes", [{"modified": False}, {"tuning": "torque"}, {"brand": "toyota"}])
@pytest.mark.parametrize("fingerprint,firmware", [("HONDA_CIVIC", b"39990-TEG-A010"), ("HONDA_CIVIC_BOSCH", b"39990-TBA-C020")])
def test_stock_or_wrong_controller_never_admitted(changes, fingerprint, firmware):
  assert firmware_controller_profile(*car(fingerprint, firmware, **changes)) is None


@pytest.mark.parametrize("output", np.linspace(-.85, .85, 19))
def test_c020_command_map_round_trip(output):
  target = core.r5_from_output(output, 20., core.CIVIC_BOSCH_C020)
  assert core.output_from_r5(target, core.CIVIC_BOSCH_C020) == pytest.approx(output, abs=.002)


@pytest.mark.parametrize("load,rate", [(500., 0.), (-1500., 0.), (800., 40.), (-800., -40.), (300., -60.),
                                       (-4000., 120.), (100., -216.), (-6000., 0.), (0., 0.)])
@pytest.mark.parametrize("guess", [0., 15000., -15000.])
def test_c020_nonlinear_inverse_satisfies_its_firmware_law(load, rate, guess):
  cal = core.CIVIC_BOSCH_C020
  target = core.r5_for_motion(load, rate, guess, cal=cal)
  assert core.firmware_output(target, rate, cal=cal) == pytest.approx(load, abs=1e-6)


def test_c020_tables_load_trims_and_clarity_angle_feedback_are_separate():
  cal = core.CIVIC_BOSCH_C020
  assert cal.e4_per_output == 4096.
  assert core.CLARITY_A020.e4_per_output == 3840.
  assert cal.r5_key_bp == (0, 115, 254, 449, 654, 862, 1111, 1549, 1774)
  assert core.CIVIC_EPS_LOAD == (-5.574, -.1831, -4.540, -326.5, -83.6, -3.185)
  assert core.CIVIC_P_SCALE == (1.15, 1.25, 1.15)
  assert core.CIVIC_I_SCALE == (.75, .95, 1.)
  assert core.firmware_r6(10., 0., cal) == core.firmware_r6(10., 200., cal) == -1730.
  assert core.firmware_r6(10., 200.) != core.firmware_r6(10., 0.)
  # The nonlinear P pieces reproduce the source's interpolation over key.
  for target in np.linspace(0., 35000., 350):
    key = np.interp(target, cal.r5_v, cal.r5_key_bp)
    assert core.firmware_kp(target, cal) == pytest.approx(np.interp(key, core.KP_KEY_BP, core.KP_V))


@pytest.mark.parametrize("speed", [1., 3., 5., 12., 20., 30., 40.])
def test_c020_feedforward_respects_source_caps_and_lane_change_bypass(speed):
  ff = core.HondaEpsFirmwareFeedforward(.01, cal=core.CIVIC_BOSCH_C020, load=core.CIVIC_EPS_LOAD)
  control = core.HondaEpsLateralCore([0., 11.175, 11.176, 22.352], [.018, .024, .048, .060],
    [0., 11.175, 11.176, 22.352], [.006, .008, .016, .020], .01, ff=ff,
    p_scale=core.CIVIC_P_SCALE, i_scale=core.CIVIC_I_SCALE)
  cap = min(core.R5_CAP, .9 * np.interp(core.key_ceiling(speed, ff.cal), ff.cal.r5_key_bp, ff.cal.r5_v))
  for frame in range(200):
    output = control.update(20. + math.sin(frame / 20.), 0., 20., speed, .02, False, False)
    assert math.isfinite(output) and abs(output) <= 1.
    assert abs(ff.r5) <= cap + 1e-6
  control.update(20., 0., 20., speed, .02, False, False, optimized_lane_change=True)
  assert control.ff_weight == 0. and control.pid.f == 0.


@pytest.mark.parametrize("profile", [CIVIC_PROFILE, TEG_PROFILE])
def test_civic_keeps_shared_prediction_delay_but_not_saved_clarity_command_delay(profile):
  assert prediction_delay_schedule(profile) is None
  assert prediction_delay_schedule(CLARITY_PROFILE) is not None
  settings = {"NrdrLateralController": 1, "NrdrYawCommandDelayLow": .3, "NrdrYawCommandDelayHigh": .3}
  assert [command_delay(settings, speed, calibration=profile.calibration) for speed in (0., 10., 12.5, 15., 30.)] == \
    pytest.approx([.175, .175, .10, .025, .025])
  assert all(tuning_write_allowed(settings, key) for key in ("LagdToggle", "LagdToggleDelay"))


@pytest.mark.parametrize("key", ["LagdToggle", "LagdToggleDelay"])
@pytest.mark.parametrize("selected", [0, 1])
@pytest.mark.parametrize("scheduled", [False, True])
@pytest.mark.parametrize("suggested", [False, True])
def test_remote_and_native_delay_locks_agree(key, selected, scheduled, suggested):
  values = {"NrdrLateralController": selected, "NrdrSuggestedSettings": suggested}
  capabilities = {"nrdr_firmware_prediction_schedule": scheduled}

  def rule(condition):
    kind = condition["type"]
    if kind == "param":
      return values.get(condition["key"], False) == condition["equals"]
    if kind == "capability":
      return capabilities.get(condition["field"], False) == condition["equals"]
    if kind == "not":
      return not rule(condition["condition"])
    if kind == "all":
      return all(rule(child) for child in condition["conditions"])
    raise AssertionError(kind)

  allowed = all(rule(condition) for condition in apply_sunnylink_metadata({"key": key})["enablement"])
  assert allowed == tuning_write_allowed(values, key, firmware_prediction_schedule=scheduled)
  assert allowed == (not suggested and not (selected == 1 and scheduled))


def test_tegs_can_and_safety_limits_are_not_replaced_with_bosch_limits():
  # Full native get_params coverage remains necessary; this guards the transport
  # constants the provisional wrapper deliberately leaves alone.
  import ast
  root = Path(__file__).resolve().parents[3]
  path = root / "opendbc_repo/opendbc/sunnypilot/car/honda/interface_ext.py"
  tree = ast.parse(path.read_text())
  assignment, = [node for node in tree.body if isinstance(node, ast.Assign)
                  and any(isinstance(target, ast.Name) and target.id == "_EXTENDED_TORQUE_LIMITS" for target in node.targets)]
  limits = {key.attr: value.value for key, value in zip(assignment.value.keys, assignment.value.values, strict=True)}
  assert limits["HONDA_CIVIC"] == 3840
  assert limits["HONDA_CIVIC_BOSCH"] == 4096


def test_calibrations_default_to_the_shared_p_axis_and_honour_their_own():
  assert core.CIVIC_BOSCH_C020.kp_key_bp == core.CLARITY_A020.kp_key_bp == tuple(core.KP_KEY_BP)
  c020 = core.CIVIC_BOSCH_C020
  own = core.EpsFirmwareCalibration(c020.e4_per_output, c020.r5_key_bp, c020.r5_v, c020.envelope_bp, c020.envelope_v,
                                    c020.r6_per_deg_s, kp_key_bp=(0, 111, 222, 333, 499, 665, 887, 1108, 1774))
  for target in np.linspace(0., 30000., 61):
    key = np.interp(target, own.r5_v, own.r5_key_bp)
    assert core.firmware_kp(target, own) == pytest.approx(np.interp(key, own.kp_key_bp, core.KP_V))
  with pytest.raises(ValueError):
    core.EpsFirmwareCalibration(3840., (0, 1), (0, 18), (0, 1), (1774, 1774), -122., r5_per_key=18.04, kp_key_bp=(0, 1))


# Command rows 2 and 3 as the images hold them (axis, R5).
TEG_ROW_AXES = {2: (0, 111, 222, 333, 499, 665, 887, 1108, 1774), 3: (0, 222, 333, 495, 656, 887, 1108, 1552, 1774)}
TEG_EARLIER_ROW_3_R5 = (0, 1926, 4938, 8455, 12036, 15926, 20138, 26955, 30000)  # Tracker1-3200 build
TEG_FIXED_ROW_2_R5 = (0, 2000, 4000, 6000, 9009, 12000, 16000, 20000, 32000)  # corrected PTM build (04147917)


def test_teg_runs_the_corrected_ptm_builds_row_3_at_its_own_can_scale():
  cal = core.CIVIC_TEG_A010
  assert TEG_PROFILE.calibration == "civic_teg_a010" and TEG_PROFILE.provisional
  assert cal.e4_per_output == 3840.  # = the HONDA_CIVIC transport limit, see test_tegs_can_and_safety_limits...
  assert cal.r5_key_bp == TEG_ROW_AXES[3] and cal.r5_v == (0, 4000, 6000, 8937, 11838, 16000, 20000, 28000, 32000)
  assert cal.kp_key_bp == tuple(core.KP_KEY_BP)  # the corrected build moved rows 0-5 P onto the Clarity's knots
  assert cal.envelope_v == core.CIVIC_BOSCH_C020.envelope_v and cal.r6_per_deg_s == -152.5
  # R6 per published deg/s by |angle| band, measured on routes 133/134/137, within 1.5%
  for angle, measured in ((7.5, -151.4), (30., -152.2), (67.5, -165.7), (120., -170.4), (200., -176.4)):
    assert core.firmware_r6(1.0, angle, cal) == pytest.approx(measured, rel=.015)
  assert core.CIVIC_TEG_EPS_LOAD == (-7.833, -.169, -8.29, -311.2, 59.18, -4.457)
  # Why row 3: the owner's telemetry R5 by command key (route 0000012f medians, earlier build) sits on that
  # build's row 3 within 3 %.
  for key, measured in ((40, 338), (80, 685), (120, 1032), (160, 1379), (200, 1726), (240, 2360)):
    assert np.interp(key, TEG_ROW_AXES[3], TEG_EARLIER_ROW_3_R5) == pytest.approx(measured, rel=.03)


@pytest.mark.parametrize("output", np.linspace(.02, 1., 50))
def test_teg_makes_the_clarity_command_on_both_rows(output):
  # The PTM rule: at 3840 E4 per unit, the same output asks for the Clarity's R5 and Kp. Rows 2 (TEGA1) and
  # 3 (TEGA2) of the corrected build agree, so the variant no longer matters. The residue is knot rounding.
  teg = core.r5_from_output(output, 20., core.CIVIC_TEG_A010)
  clarity = core.r5_from_output(output, 20., core.CLARITY_A020)
  assert teg == pytest.approx(clarity, rel=.005, abs=2.)
  key = abs(core.command_key(-output * 3840.))
  assert np.interp(key, TEG_ROW_AXES[2], TEG_FIXED_ROW_2_R5) == pytest.approx(abs(teg), rel=.005, abs=2.)
  assert core.firmware_kp(teg, core.CIVIC_TEG_A010) == pytest.approx(core.firmware_kp(clarity, core.CLARITY_A020), rel=.005)


@pytest.mark.parametrize("output", np.linspace(-.85, .85, 19))
def test_teg_command_map_round_trip(output):
  target = core.r5_from_output(output, 20., core.CIVIC_TEG_A010)
  assert core.output_from_r5(target, core.CIVIC_TEG_A010) == pytest.approx(output, abs=.002)


@pytest.mark.parametrize("load,rate", [(500., 0.), (-1500., 0.), (800., 40.), (-800., -40.), (-4000., 120.), (0., 0.)])
@pytest.mark.parametrize("guess", [0., 15000., -15000.])
def test_teg_nonlinear_inverse_satisfies_its_firmware_law(load, rate, guess):
  cal = core.CIVIC_TEG_A010
  target = core.r5_for_motion(load, rate, guess, cal=cal)
  assert core.firmware_output(target, rate, cal=cal) == pytest.approx(load, abs=1e-6)


def _extended_torque_limits():
  import ast
  root = Path(__file__).resolve().parents[3]
  tree = ast.parse((root / "opendbc_repo/opendbc/sunnypilot/car/honda/interface_ext.py").read_text())
  assignment, = [node for node in tree.body if isinstance(node, ast.Assign)
                  and any(isinstance(target, ast.Name) and target.id == "_EXTENDED_TORQUE_LIMITS" for target in node.targets)]
  return {key.attr: value.value for key, value in zip(assignment.value.keys, assignment.value.values, strict=True)}


def test_insight_runs_the_corrected_ptm_at_this_trees_can_scale():
  cal = core.INSIGHT_TXM_A040
  assert INSIGHT_PROFILE.calibration == "insight_txm_a040" and not INSIGHT_PROFILE.provisional
  assert prediction_delay_schedule(INSIGHT_PROFILE) == prediction_delay_schedule(CLARITY_PROFILE)
  assert cal.e4_per_output == _extended_torque_limits()["HONDA_INSIGHT"] == 4096
  # rows 0-1 of the corrected image are the Clarity's own command map and P table
  assert (cal.r5_key_bp, cal.r5_v, cal.kp_key_bp) == (core.CLARITY_A020.r5_key_bp, core.CLARITY_A020.r5_v,
                                                     core.CLARITY_A020.kp_key_bp)
  assert cal.kp_pieces == core.CLARITY_A020.kp_pieces and cal.envelope_v == (1774,) * 9
  assert cal.r6_per_deg_s == -131.15 and core.INSIGHT_TXM_EPS_LOAD == (-4.876, -.1376, -4.452, -397.2, 65.41, -4.29)
  # R6 per published deg/s follows its own A table: 1.0 at centre, ~1.22 past 120 deg
  assert core.firmware_r6(1.0, 0.0, cal) == pytest.approx(-131.15)
  assert core.firmware_r6(1.0, 150.0, cal) == pytest.approx(-131.15 * 1.2156)
  assert command_delay(None, 5.0, calibration="insight_txm_a040") == pytest.approx(.175)


@pytest.mark.parametrize("u", np.linspace(.02, .93, 40))
def test_insight_asks_the_clarity_target_for_the_same_e4(u):
  # the same 0xE4 value makes the same firmware target on both images; this tree just sends the Insight 4096 per unit
  e4 = u * 3840.
  assert core.r5_from_output(e4 / 4096., 20., core.INSIGHT_TXM_A040) == pytest.approx(core.r5_from_output(u, 20., core.CLARITY_A020))
  target = core.r5_from_output(u, 20., core.CLARITY_A020)
  assert core.output_from_r5(target, core.INSIGHT_TXM_A040) == pytest.approx(core.output_from_r5(target, core.CLARITY_A020) * 3840 / 4096)
