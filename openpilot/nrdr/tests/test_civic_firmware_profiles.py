"""Civic calibration and the explicit TEG exception, without CAN/IPC/settings writes."""
import math
from pathlib import Path
from types import SimpleNamespace as NS

import numpy as np
import pytest

from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.nrdr.features.lateral.controller_selection import (
  CIVIC_PROFILE, CLARITY_PROFILE, TEG_PLACEHOLDER_PROFILE, firmware_controller_profile,
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
  ("HONDA_CIVIC", b"39990-TEG,A010\0", TEG_PLACEHOLDER_PROFILE),
])
def test_exact_profiles_and_selected_controller(fingerprint, firmware, profile):
  cp, sp = car(fingerprint, firmware)
  assert firmware_controller_profile(cp, sp) is profile
  for value in (1, "1", b"1"):
    assert firmware_controller_selected({"NrdrLateralController": value}, cp, sp)
  assert not firmware_controller_selected({"NrdrLateralController": 0}, cp, sp)
  assert profile.provisional == (profile is TEG_PLACEHOLDER_PROFILE)


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


@pytest.mark.parametrize("profile", [CIVIC_PROFILE, TEG_PLACEHOLDER_PROFILE])
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
