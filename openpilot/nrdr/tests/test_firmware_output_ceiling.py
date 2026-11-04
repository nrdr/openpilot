"""The controller must not integrate into the flat tail of an EPS command row."""
import math

import pytest

from openpilot.nrdr.features.lateral import vfn_eps_core as core


CALIBRATIONS = (
  core.CLARITY_A020, core.CIVIC_BOSCH_C020, core.CIVIC_TEG_A010, core.INSIGHT_TXM_A040,
  core.CIVIC_TBA_C120, core.CIVIC_TGG_A120, core.CIVIC_TBA_A030, core.CRV_TLA_A040, core.CRV_TLA_A220,
)
CRV_LIMIT = 3841 / 4096  # round up to the first integer E4 that decodes to key 1663


@pytest.mark.parametrize("cal", CALIBRATIONS)
def test_only_crv_rows_have_a_dead_tail_below_full_output(cal):
  crv = cal in (core.CRV_TLA_A040, core.CRV_TLA_A220)
  assert cal.output_ceiling() == (CRV_LIMIT if crv else 1.0)
  assert core.command_key(3840) == 1662
  assert core.command_key(3841) == 1663


@pytest.mark.parametrize("cal", (core.CRV_TLA_A040, core.CRV_TLA_A220))
@pytest.mark.parametrize("sign", (-1, 1))
def test_ceiling_reaches_the_same_firmware_target_as_full_output(cal, sign):
  assert core.r5_from_output(sign * cal.output_ceiling(), 20., cal) == core.r5_from_output(sign, 20., cal)


def test_input_clamp_can_bind_before_the_end_of_a_row():
  cal = core.EpsFirmwareCalibration(4096., [0, 1774], [0, 30000], [0, 400], [1774, 1774], -122., key_clamp=1663)
  assert cal.output_ceiling() == CRV_LIMIT


def test_speed_envelope_does_not_retune_the_output_ceiling():
  cal = core.CLARITY_A020
  assert core.key_ceiling(50., cal) < cal.key_clamp
  assert cal.output_ceiling() == 1.0


@pytest.mark.parametrize("cal", (core.CRV_TLA_A040, core.CRV_TLA_A220))
@pytest.mark.parametrize("sign", (-1, 1))
@pytest.mark.parametrize("filtered", (False, True))
def test_core_and_integrator_stop_at_the_usable_row_end(cal, sign, filtered):
  # Isolate integral windup: no P, and lane-change suppression removes FF.
  controller = core.HondaEpsLateralCore([0.], [0.], [0.], [1.], .01,
    ff=core.HondaEpsFirmwareFeedforward(.01, cal=cal), p_scale=(1., 1., 1.), i_scale=(1., 1., 1.))
  controller.output_lpf_enabled = filtered
  for _ in range(300):
    output = controller.update(sign, 0., 0., 10., 0., False, False, optimized_lane_change=True)
    assert abs(output) <= CRV_LIMIT
    assert abs(controller.pid.i) <= CRV_LIMIT
  assert controller.pid.pos_limit == CRV_LIMIT and controller.pid.neg_limit == -CRV_LIMIT
  assert math.isclose(abs(controller.pid.i), .93)
  held = controller.pid.i
  controller.update(-sign, 0., 0., 10., 0., False, True, optimized_lane_change=True)
  assert controller.pid.i == held  # an unrelated safety limit still freezes I
  controller.reset()
  assert controller.output == controller.pid.i == controller.ff_weight == 0.


@pytest.mark.parametrize("cal", (core.CRV_TLA_A040, core.CRV_TLA_A220))
@pytest.mark.parametrize("sign", (-1, 1))
def test_final_clamp_also_contains_existing_filter_state(cal, sign):
  controller = core.HondaEpsLateralCore([0.], [1.], [0.], [0.], .01,
    ff=core.HondaEpsFirmwareFeedforward(.01, cal=cal))
  controller.output_lpf.x = float(sign)
  output = controller.update(100. * sign, 0., 0., 10., 0., False, False)
  assert abs(output) <= CRV_LIMIT
