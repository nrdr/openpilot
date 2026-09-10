from types import SimpleNamespace

import numpy as np

from openpilot.common.constants import CV
from openpilot.common.parameterized import parameterized
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.controls.lib.lane_centering import (
  LANE_CENTERING_MIN_SPEED_DEFAULT_MPH,
  LANE_CENTERING_MIN_SPEED_MAX_MPH,
  LANE_CENTERING_MIN_SPEED_MIN_MPH,
  LaneCenteringController,
  lane_centering_min_speed_mph,
  lane_centering_speed_thresholds,
)


_V_EGO = 55.0 * CV.MPH_TO_MS
_XS = np.linspace(0.0, 50.0, 52)


def _path(y, y_std=0.1):
  return SimpleNamespace(
    x=_XS.copy(),
    y=np.full_like(_XS, float(y)),
    yStd=np.full_like(_XS, float(y_std)),
  )


def _model(left=-1.8, right=1.8, model_y=0.0, lane_prob=0.9, lane_std=0.1, path_std=0.1, lane_change=0):
  return SimpleNamespace(
    laneLines=[_path(0.0), _path(left), _path(right), _path(0.0)],
    laneLineProbs=[0.0, lane_prob, lane_prob, 0.0],
    laneLineStds=[0.0, lane_std, lane_std, 0.0],
    position=_path(model_y, path_std),
    meta=SimpleNamespace(laneChangeState=lane_change),
  )


def _update(controller, model, *, model_curvature=0.0, offset=0.0, authority=1.0, min_speed_mph=50, enabled=True,
            active=True, valid=True, speed=_V_EGO, pause_on_signal=False, turn_signal_active=False, driver_override=False):
  return controller.update(model_curvature, model, speed, min_speed_mph, enabled, offset, authority, active, valid,
                           pause_on_signal, turn_signal_active, driver_override)


def _converge(model, *, offset=0.0, authority=1.0):
  controller = LaneCenteringController()
  output = 0.0
  for _ in range(300):
    output = _update(controller, model, offset=offset, authority=authority)
  return controller, output


class TestLaneCentering(OpenpilotTestCase):
  @parameterized.expand([
    (None,),
    ("",),
    ("malformed",),
    (10 ** 10000,),
    (float("nan"),),
    (float("inf"),),
    (-100,),
    (11,),
    (49.5,),
    (101,),
  ])
  def test_min_speed_invalid_values_fail_closed_to_default(self, value):
    assert lane_centering_min_speed_mph(value) == LANE_CENTERING_MIN_SPEED_DEFAULT_MPH

  @parameterized.expand([
    (12, LANE_CENTERING_MIN_SPEED_MIN_MPH),
    (50, LANE_CENTERING_MIN_SPEED_DEFAULT_MPH),
    (100, LANE_CENTERING_MIN_SPEED_MAX_MPH),
  ])
  def test_min_speed_exact_bounds_are_valid(self, value, expected):
    assert lane_centering_min_speed_mph(value) == expected

  def test_default_speed_thresholds_are_exact_mph(self):
    arm, release = lane_centering_speed_thresholds(50)
    assert arm == 50.0 * CV.MPH_TO_MS
    assert release == 47.0 * CV.MPH_TO_MS
    assert np.isclose(arm, 22.352)
    assert np.isclose(release, 21.01088)

    minimum_arm, minimum_release = lane_centering_speed_thresholds(12)
    assert minimum_arm == 12.0 * CV.MPH_TO_MS
    assert minimum_release == 5.0

  def test_existing_enabled_install_with_missing_setting_adopts_default(self):
    model = _model(left=-1.5, right=2.1)
    controller = LaneCenteringController()
    assert _update(controller, model, authority=0.0, min_speed_mph=None,
                   speed=(50.0 * CV.MPH_TO_MS) - 1e-6) == 0.0
    assert _update(controller, model, authority=0.0, min_speed_mph=None,
                   speed=50.0 * CV.MPH_TO_MS) > 0.0

  def test_maximum_speed_exact_arm_boundary(self):
    model = _model(left=-1.5, right=2.1)
    controller = LaneCenteringController()
    below = _update(controller, model, authority=0.0, min_speed_mph=100,
                    speed=(100.0 * CV.MPH_TO_MS) - 1e-6)
    assert below == 0.0
    at = _update(controller, model, authority=0.0, min_speed_mph=100,
                 speed=100.0 * CV.MPH_TO_MS)
    assert at > 0.0

  @parameterized.expand([
    ({"enabled": False},),
    ({"active": False},),
    ({"valid": False},),
    ({"speed": 4.9},),
  ])
  def test_hard_gates_are_noop(self, kwargs):
    assert _update(LaneCenteringController(), _model(left=-1.5, right=2.1), **kwargs) == 0.0

  def test_lane_change_is_noop(self):
    assert _update(LaneCenteringController(), _model(left=-1.5, right=2.1, lane_change=1)) == 0.0

  def test_speed_hysteresis_arms_holds_releases_and_requires_rearm(self):
    model = _model(left=-1.5, right=2.1)
    controller = LaneCenteringController()
    model_curvature = 0.0013

    below_arm = _update(controller, model, model_curvature=model_curvature, authority=0.0,
                        speed=(50.0 * CV.MPH_TO_MS) - 1e-6)
    assert below_arm == model_curvature

    at_arm = _update(controller, model, model_curvature=model_curvature, authority=0.0,
                     speed=50.0 * CV.MPH_TO_MS)
    assert at_arm > model_curvature

    at_release = _update(controller, model, model_curvature=model_curvature, authority=0.0,
                         speed=47.0 * CV.MPH_TO_MS)
    assert at_release > model_curvature

    below_release = _update(controller, model, model_curvature=model_curvature, authority=0.0,
                            speed=(47.0 * CV.MPH_TO_MS) - 1e-6)
    assert model_curvature < below_release < at_release

    for _ in range(300):
      faded = _update(controller, model, model_curvature=model_curvature, authority=0.0,
                      speed=48.0 * CV.MPH_TO_MS)
    assert abs(faded - model_curvature) < 1e-6

    rearmed = _update(controller, model, model_curvature=model_curvature, authority=0.0,
                      speed=50.0 * CV.MPH_TO_MS)
    assert rearmed > model_curvature

  def test_turn_signal_fade_preserves_speed_latch(self):
    model = _model(left=-1.5, right=2.1)
    controller, centered = _converge(model, authority=0.0)
    fading = _update(controller, model, authority=0.0, speed=48.0 * CV.MPH_TO_MS,
                     pause_on_signal=True, turn_signal_active=True)
    assert 0.0 < fading < centered

    resumed = _update(controller, model, authority=0.0, speed=48.0 * CV.MPH_TO_MS)
    assert resumed > fading

  def test_confidence_fade_preserves_speed_latch(self):
    model = _model(left=-1.5, right=2.1)
    controller, centered = _converge(model, authority=0.0)
    fading = _update(controller, _model(left=-1.5, right=2.1, lane_prob=0.2),
                     authority=0.0, speed=48.0 * CV.MPH_TO_MS)
    assert 0.0 < fading < centered

    resumed = _update(controller, model, authority=0.0, speed=48.0 * CV.MPH_TO_MS)
    assert resumed > fading

  @parameterized.expand([
    ({"active": False},),
    ({"speed": 4.9},),
  ])
  def test_lat_inactive_and_absolute_floor_clear_speed_latch(self, reset_kwargs):
    model = _model(left=-1.5, right=2.1)
    controller, centered = _converge(model, authority=0.0)
    assert centered > 0.0
    model_curvature = 0.0013
    assert _update(controller, model, model_curvature=model_curvature, authority=0.0,
                   **reset_kwargs) == model_curvature
    assert _update(controller, model, model_curvature=model_curvature, authority=0.0,
                   speed=48.0 * CV.MPH_TO_MS) == model_curvature

  def test_active_signal_does_not_mask_lane_change_reset(self):
    model = _model(left=-1.5, right=2.1)
    controller, centered = _converge(model, authority=0.0)
    assert centered > 0.0
    model_curvature = 0.0013
    lane_change = _model(left=-1.5, right=2.1, lane_change=1)
    assert _update(controller, lane_change, model_curvature=model_curvature, authority=0.0,
                   pause_on_signal=True, turn_signal_active=True) == model_curvature
    assert _update(controller, model, model_curvature=model_curvature, authority=0.0,
                   speed=48.0 * CV.MPH_TO_MS) == model_curvature

  def test_minimum_setting_honors_floor_and_hysteresis(self):
    model = _model(left=-1.5, right=2.1)
    controller = LaneCenteringController()
    assert _update(controller, model, authority=0.0, min_speed_mph=12,
                   speed=(12.0 * CV.MPH_TO_MS) - 1e-6) == 0.0
    assert _update(controller, model, authority=0.0, min_speed_mph=12,
                   speed=12.0 * CV.MPH_TO_MS) > 0.0
    assert _update(controller, model, authority=0.0, min_speed_mph=12, speed=5.0) > 0.0
    assert _update(controller, model, authority=0.0, min_speed_mph=12,
                   speed=5.0 - 1e-6) == 0.0

  def test_speed_release_fades_monotonically_to_model_curvature(self):
    model = _model(left=-1.5, right=2.1)
    controller, centered = _converge(model, authority=0.0)
    model_curvature = -0.0013
    outputs = [
      _update(controller, model, model_curvature=model_curvature, authority=0.0,
              speed=46.0 * CV.MPH_TO_MS)
      for _ in range(300)
    ]
    assert outputs[0] < model_curvature + centered
    assert all(current <= previous for previous, current in zip(outputs[:-1], outputs[1:], strict=True))
    assert abs(outputs[-1] - model_curvature) < 1e-6

  @parameterized.expand([
    ("driver",),
    ("lane_change",),
    ("model_invalid",),
  ])
  def test_hard_reset_clears_speed_latch(self, reset_kind):
    model = _model(left=-1.5, right=2.1)
    controller, centered = _converge(model, authority=0.0)
    assert centered > 0.0
    model_curvature = 0.0013

    reset_model = _model(left=-1.5, right=2.1, lane_change=1) if reset_kind == "lane_change" else model
    reset_output = _update(
      controller,
      reset_model,
      model_curvature=model_curvature,
      authority=0.0,
      driver_override=reset_kind == "driver",
      valid=reset_kind != "model_invalid",
    )
    assert reset_output == model_curvature
    assert _update(controller, model, model_curvature=model_curvature, authority=0.0,
                   speed=48.0 * CV.MPH_TO_MS) == model_curvature
    assert _update(controller, model, model_curvature=model_curvature, authority=0.0,
                   speed=50.0 * CV.MPH_TO_MS) > model_curvature

  @parameterized.expand([
    (12,),
    (50,),
    (100,),
    ("malformed",),
  ])
  def test_master_off_is_exact_model_curvature_parity(self, min_speed_mph):
    controller, _ = _converge(_model(left=-1.5, right=2.1), authority=0.0)
    model_curvature = -0.0017
    output = _update(controller, _model(left=-1.5, right=2.1), model_curvature=model_curvature,
                     min_speed_mph=min_speed_mph, enabled=False)
    assert output == model_curvature
    arm_speed, release_speed = lane_centering_speed_thresholds(min_speed_mph)
    assert _update(controller, _model(left=-1.5, right=2.1), model_curvature=model_curvature,
                   min_speed_mph=min_speed_mph, speed=(arm_speed + release_speed) * 0.5) == model_curvature

  def test_turn_signal_fades_lane_centering_correction(self):
    model = _model(left=-1.5, right=2.1)
    controller, centered = _converge(model, authority=0.0)
    fading = _update(controller, model, authority=0.0, pause_on_signal=True, turn_signal_active=True)
    assert 0.0 < fading < centered

    for _ in range(300):
      fading = _update(controller, model, authority=0.0, pause_on_signal=True, turn_signal_active=True)
    assert abs(fading) < 1e-6

  def test_turn_signal_pause_can_be_disabled(self):
    model = _model(left=-1.5, right=2.1)
    _, output = _converge(model, authority=0.0)
    controller, _ = _converge(model, authority=0.0)
    signaled = _update(controller, model, authority=0.0, turn_signal_active=True)
    assert abs(signaled - output) < 1e-7

  def test_driver_override_resets_and_reacquires_smoothly(self):
    model = _model(left=-1.5, right=2.1)
    controller, centered = _converge(model, authority=0.0)
    model_curvature = 0.0013

    assert _update(controller, model, model_curvature=model_curvature, authority=0.0, driver_override=True) == model_curvature
    reacquiring = _update(controller, model, model_curvature=model_curvature, authority=0.0)
    assert model_curvature < reacquiring < model_curvature + centered

  @parameterized.expand([
    ("prob", np.nan),
    ("prob", 1.1),
    ("std", np.nan),
    ("std", -0.1),
  ])
  def test_invalid_lane_confidence_is_rejected(self, field, value):
    model = _model(left=-1.5, right=2.1)
    values = model.laneLineProbs if field == "prob" else model.laneLineStds
    values[1] = value
    assert _update(LaneCenteringController(), model) == 0.0

  def test_input_must_cover_lookahead(self):
    model = _model(left=-1.5, right=2.1)
    model.laneLines[1].x = model.laneLines[1].x[:10]
    model.laneLines[1].y = model.laneLines[1].y[:10]
    assert _update(LaneCenteringController(), model) == 0.0

  def test_lane_center_error_steers_toward_center(self):
    _, right = _converge(_model(left=-1.5, right=2.1), authority=0.0)
    _, left = _converge(_model(left=-2.1, right=1.5), authority=0.0)
    assert right > 0.0
    assert left < 0.0

  def test_small_center_error_does_not_chatter(self):
    _, output = _converge(_model(left=-1.75, right=1.85), authority=0.0)
    assert output == 0.0

  def test_offset_direction(self):
    _, right = _converge(_model(), offset=0.2, authority=0.0)
    _, left = _converge(_model(), offset=-0.2, authority=0.0)
    assert right > 0.0
    assert left < 0.0

  def test_offset_is_reduced_in_narrow_lane(self):
    narrow = _model(left=-1.3, right=1.3)
    _, at_safe_limit = _converge(narrow, offset=0.2, authority=0.0)
    _, above_safe_limit = _converge(narrow, offset=0.3, authority=0.0)
    assert np.isclose(at_safe_limit, above_safe_limit)

  def test_confident_e2e_path_can_fully_break_in(self):
    model = _model(left=-1.0, right=2.6, model_y=0.0, path_std=0.1)
    _, lane_authority = _converge(model, authority=0.0)
    _, e2e_authority = _converge(model, authority=1.0)
    assert lane_authority > 0.0
    assert abs(e2e_authority) < 1e-9

  def test_uncertain_e2e_path_does_not_break_in(self):
    model = _model(left=-1.0, right=2.6, model_y=0.0, path_std=0.6)
    _, output = _converge(model, authority=1.0)
    assert output > 0.0

  def test_e2e_authority_blends_lane_correction(self):
    model = _model(left=-1.2, right=2.4, model_y=0.0, path_std=0.1)
    _, lane_only = _converge(model, authority=0.0)
    _, blended = _converge(model, authority=0.5)
    _, e2e = _converge(model, authority=1.0)
    assert lane_only > blended > e2e >= 0.0

  def test_confident_e2e_authority_starts_before_large_offset(self):
    model = _model(left=-1.7, right=2.1, model_y=0.0, path_std=0.1)
    _, lane_only = _converge(model, authority=0.0)
    _, e2e = _converge(model, authority=1.0)
    assert lane_only > e2e > 0.0

  def test_confidence_loss_drops_filtered_correction(self):
    controller, output = _converge(_model(left=-1.5, right=2.1), authority=0.0)
    assert output > 0.0
    fading = _update(controller, _model(left=-1.5, right=2.1, lane_prob=0.2), authority=0.0)
    assert 0.0 < fading < output

    for _ in range(300):
      fading = _update(controller, _model(left=-1.5, right=2.1, lane_prob=0.2), authority=0.0)
    assert abs(fading) < 1e-6

  def test_correction_is_smoothed_and_capped(self):
    controller = LaneCenteringController()
    model = _model(left=0.0, right=3.0, path_std=0.6)
    first = _update(controller, model, authority=0.0)
    _, steady = _converge(model, authority=0.0)
    assert 0.0 < first < steady
    assert np.isclose(steady, 0.004 * 0.30, atol=1e-6)
