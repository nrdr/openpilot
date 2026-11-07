"""R6, the EPS firmware's rate feedback, computed from each image's own Table A and clamped where the firmware clamps it."""
import pytest

from openpilot.nrdr.features.lateral import vfn_eps_core as core
from openpilot.nrdr.features.lateral.honda_vgr import HONDA_VGR_PROFILES

# Centre values from JamesL787 ns-bosch-radar-testing computed_r6 (the same Table A, -122 * A[0] / 16384)
CENTRE = {"Clarity TRW-A020": -122.0, "Civic C020/TGG-A120": -153.74, "Civic C120/A030/TEG": -156.16,
          "CR-V TLA-A040": -124.97, "Insight TXM-A040": -131.15}
# Every calibration and the Table A its image carries
TABLE_A = {
  "CLARITY_A020": "Clarity TRW-A020", "CIVIC_BOSCH_C020": "Civic C020/TGG-A120", "CIVIC_TGG_A120": "Civic C020/TGG-A120",
  "CIVIC_TEG_A010": "Civic C120/A030/TEG", "CIVIC_TBA_A030": "Civic C120/A030/TEG", "CIVIC_TBA_C120": "Civic C120/A030/TEG",
  "CRV_TLA_A040": "CR-V TLA-A040", "CRV_TLA_A220": "CR-V TLA-A040", "INSIGHT_TXM_A040": "Insight TXM-A040",
}
PROFILE = {p.name: p for p in HONDA_VGR_PROFILES}


@pytest.mark.parametrize("name", CENTRE)
def test_centre_is_the_clarity_constant_through_the_images_centre_divisor(name):
  centre, _, gain = core.computed_r6(PROFILE[name])
  assert centre == pytest.approx(CENTRE[name], abs=0.01) and gain[0] == 1.0


@pytest.mark.parametrize("cal_name,table", TABLE_A.items())
def test_every_calibration_takes_its_table_as_computed_r6(cal_name, table):
  cal = getattr(core, cal_name)
  centre, bp, gain = core.computed_r6(PROFILE[table])
  assert (cal.r6_per_deg_s, tuple(cal.r6_angle_bp), tuple(cal.r6_angle_gain)) == (centre, bp, gain)


@pytest.mark.parametrize("cal_name", TABLE_A)
def test_r6_rails_at_the_firmware_clamp(cal_name):
  cal = getattr(core, cal_name)
  for angle in (0.0, 90.0, 300.0):
    assert core.firmware_r6(1000.0, angle, cal) == -core.R6_CLAMP
    assert core.firmware_r6(-1000.0, angle, cal) == core.R6_CLAMP
    assert core.firmware_r6(20.0, angle, cal) == pytest.approx(20.0 * core.firmware_r6(1.0, angle, cal))


def test_the_clarity_rails_later_than_the_civics():
  # the rail sits at ~260 deg/s on the Clarity and ~185-210 deg/s on the Civics near centre
  def rail(cal):
    return core.R6_CLAMP / abs(cal.r6_per_deg_s)
  assert rail(core.CLARITY_A020) > 260 and 200 < rail(core.CIVIC_BOSCH_C020) < 215
