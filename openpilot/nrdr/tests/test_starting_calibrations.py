"""Corrected-PTM (revision b) starting calibrations: the C120, TGG-A120, A030 and both CR-V images."""
import pytest

from openpilot.nrdr.features.lateral import vfn_eps_core as core
from openpilot.nrdr.features.lateral.controller_selection import (
  A030_PROFILE, C120_PROFILE, CRV_A040_PROFILE, CRV_A220_PROFILE, TGG_PROFILE,
)
from openpilot.nrdr.features.lateral.yaw_control_timing import command_delay, prediction_delay_schedule

STARTING_PROFILES = (C120_PROFILE, TGG_PROFILE, A030_PROFILE, CRV_A040_PROFILE, CRV_A220_PROFILE)
# Corrected-PTM starting calibrations. Golden R5 for the same 0xE4 at 20 m/s, from JamesL787 ns-bosch-radar-testing
# honda_eps_firmware_ff (r5_from_output(E4 / its e4_per_output)): the firmware target must not depend on the tree.
STARTING = {
  "civic_tba_c120": (core.CIVIC_TBA_C120, "9261b8db", 3840., 1663),
  "civic_tgg_a120": (core.CIVIC_TGG_A120, "6640806d", 3840., 1663),
  "civic_tba_a030": (core.CIVIC_TBA_A030, "55c37266", 3840., 1663),
  "crv_tla_a040": (core.CRV_TLA_A040, "2e6a8802", 4096., 1774),
  "crv_tla_a220": (core.CRV_TLA_A220, "2c992997", 4096., 1774),
}
STARTING_E4 = (300., 1000., 2000., 3000., 3800., 4096.)
GOLDEN_C120 = (-2324.49, -7817.21, -15622.44, -23441.43, -29675.71, -30000.03)
GOLDEN_TGG = (-2179.24, -7327.8, -14646.78, -21975.97, -27823.33, -28127.33)
GOLDEN_A030 = (-2324.32, -7812.96, -15621.64, -23441.44, -29675.68, -30000.0)
GOLDEN_A040 = (-2178.86, -7327.45, -14646.24, -21977.65, -27822.95, -28127.0)
GOLDEN_A220 = (-2179.38, -7324.23, -14648.68, -21970.75, -27822.57, -28127.0)
STARTING_GOLDEN_R5 = {
  "civic_tba_c120": GOLDEN_C120,
  "civic_tgg_a120": GOLDEN_TGG,
  "civic_tba_a030": GOLDEN_A030,
  "crv_tla_a040": GOLDEN_A040,
  "crv_tla_a220": GOLDEN_A220,
}


@pytest.mark.parametrize("name", STARTING)
def test_starting_calibrations_match_the_source_tree_and_their_build(name):
  cal, rwd, e4, clamp = STARTING[name]
  profile = next(p for p in STARTING_PROFILES if p.calibration == name)
  assert profile.required_rwd == rwd and profile.provisional
  # the Civics take their measured sibling's delay schedule; the CR-Vs keep live/manual delay
  assert profile.prediction_schedule == name.startswith("civic_")
  assert cal.e4_per_output == e4 and cal.key_clamp == clamp
  for e4_value, expected in zip(STARTING_E4, STARTING_GOLDEN_R5[name], strict=True):
    assert core.r5_from_output(e4_value / cal.e4_per_output, 20., cal) == pytest.approx(expected, abs=0.5)


@pytest.mark.parametrize("name", STARTING)
@pytest.mark.parametrize("load,rate", [(500., 0.), (-1500., 30.), (4000., -80.), (-6000., 0.)])
def test_starting_calibration_inverse_satisfies_its_firmware_law(name, load, rate):
  cal = STARTING[name][0]
  target = core.r5_for_motion(load, rate, cal=cal)
  assert core.firmware_output(target, rate, cal=cal) == pytest.approx(load, abs=1e-6)


def test_starting_calibration_vehicle_side_and_command_delay():
  from openpilot.nrdr.features.lateral.latcontrol_fw import _OWN_CALIBRATIONS
  assert _OWN_CALIBRATIONS["crv_tla_a040"][1:] == (core.CRV_TLA_EPS_LOAD, (1., 1., 1.), (1., 1., 1.))
  assert _OWN_CALIBRATIONS["crv_tla_a220"][1:] == _OWN_CALIBRATIONS["crv_tla_a040"][1:]
  assert _OWN_CALIBRATIONS["civic_tba_a030"][1] == core.CIVIC_TEG_EPS_LOAD
  assert _OWN_CALIBRATIONS["civic_tba_c120"][1] == _OWN_CALIBRATIONS["civic_tgg_a120"][1] == core.CIVIC_EPS_LOAD
  for name in ("civic_tba_c120", "civic_tgg_a120", "civic_tba_a030"):
    assert command_delay({"NrdrYawCommandDelayLow": 0.3}, 5.0, calibration=name) == pytest.approx(.175)
  for name in ("crv_tla_a040", "crv_tla_a220"):
    assert command_delay({"NrdrYawCommandDelayLow": 0.3}, 5.0, calibration=name) == pytest.approx(.145)
  # above 15 m/s the Civics hold theirs (as the C020 and TEG, measured); the CR-Vs, unmeasured, keep the old fade
  for name in ("civic_tba_c120", "civic_tgg_a120", "civic_tba_a030"):
    assert command_delay({"NrdrYawCommandDelayHigh": 0.3}, 30.0, calibration=name) == pytest.approx(.175)
  for name in ("crv_tla_a040", "crv_tla_a220"):
    assert command_delay({"NrdrYawCommandDelayHigh": 0.3}, 30.0, calibration=name) == pytest.approx(.025)


@pytest.mark.parametrize("name,sibling", [("civic_tba_a030", "civic_teg_a010"), ("civic_tba_c120", "civic_bosch_c020"),
                                          ("civic_tgg_a120", "civic_bosch_c020")])
def test_starting_civics_are_told_their_siblings_measured_lag(name, sibling):
  from openpilot.nrdr.features.lateral.controller_selection import _PROFILES
  profiles = {p.calibration: p for p in _PROFILES.values()}
  assert prediction_delay_schedule(profiles[name]) == prediction_delay_schedule(profiles[sibling])
  assert prediction_delay_schedule(profiles[name]) != prediction_delay_schedule(profiles["clarity_a020"])
  # The CR-V's key clamp is 1774 (the C120's 1663), though its row ends at key 1663, so R5 is flat from there to the clamp.
  assert core.key_ceiling(20., core.CRV_TLA_A040) == 1774 and core.key_ceiling(20., core.CIVIC_TBA_C120) == 1663
  assert core.CIVIC_TBA_A030.r5_v == core.CIVIC_TEG_A010.r5_v and core.CIVIC_TBA_A030.r6_angle_gain == core.CIVIC_TEG_A010.r6_angle_gain


def test_every_civic_and_the_insight_are_sent_their_images_3840():
  # opendbc sends 3840 per unit to every platform whose EPS clamps at key 1663 (the CR-V's clamps at 1774 = 4096)
  import ast
  from pathlib import Path
  path = Path(__file__).resolve().parents[3] / "opendbc_repo/opendbc/sunnypilot/car/honda/interface_ext.py"
  tree = ast.parse(path.read_text())
  assignment, = [node for node in tree.body if isinstance(node, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == "_EXTENDED_TORQUE_LIMITS" for t in node.targets)]
  limits = {key.attr: value.value for key, value in zip(assignment.value.keys, assignment.value.values, strict=True)}
  for cal in (core.CIVIC_BOSCH_C020, core.CIVIC_TBA_C120, core.CIVIC_TGG_A120):
    assert cal.e4_per_output == limits["HONDA_CIVIC_BOSCH"] == 3840
  assert core.INSIGHT_TXM_A040.e4_per_output == limits["HONDA_INSIGHT"] == 3840
  assert core.CRV_TLA_A040.e4_per_output == limits["HONDA_CRV_5G"] == 4096
  # at 3840 the full output reaches the clamp: u = 1 decodes to key 1662, the last key under it (1773 at 4096, clamped
  # from u ~0.94 on)
  assert core.command_key(-1.0 * 3840) == -1662 and core.command_key(-1.0 * 4096) == -1773

