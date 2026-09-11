from types import SimpleNamespace

import numpy as np

from openpilot.cereal import custom
from openpilot.common.constants import CV
from openpilot.common.parameterized import parameterized
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.ui.sunnypilot.onroad.lane_centering_status import (
  LANE_CENTERING_REASON_LABELS,
  lane_centering_reason_code,
)
from openpilot.selfdrive.controls.lib.lane_centering import (
  LANE_CENTERING_MIN_SPEED_DEFAULT_MPH,
  LANE_CENTERING_MIN_SPEED_MAX_MPH,
  LANE_CENTERING_MIN_SPEED_MIN_MPH,
  LANE_CENTERING_STRENGTH_DEFAULT,
  LANE_CENTERING_STRENGTH_MAX,
  LANE_CENTERING_STRENGTH_MIN,
  LaneCenteringController,
  LaneCenteringReason,
  lane_centering_min_speed_mph,
  lane_centering_speed_thresholds,
  lane_centering_strength,
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


def _update(controller, model, *, model_curvature=0.0, offset=0.0, authority=1.0, strength=0.30, min_speed_mph=50, enabled=True,
            active=True, valid=True, speed=_V_EGO, pause_on_signal=False, turn_signal_active=False, driver_override=False):
  return controller.update(model_curvature, model, speed, min_speed_mph, enabled, offset, authority, strength, active, valid,
                           pause_on_signal, turn_signal_active, driver_override)


def _converge(model, *, offset=0.0, authority=1.0, strength=0.30):
  controller = LaneCenteringController()
  output = 0.0
  for _ in range(300):
    output = _update(controller, model, offset=offset, authority=authority, strength=strength)
  return controller, output


class TestLaneCentering(OpenpilotTestCase):
  def test_diagnostic_reason_values_are_stable(self):
    reason_values = [
      "unavailable",
      "disabled",
      "lateralInactive",
      "invalidInput",
      "modelInvalid",
      "driverOverride",
      "laneChange",
      "belowSpeed",
      "turnSignalFade",
      "laneDataInvalid",
      "laneConfidenceLow",
      "laneGeometryInvalid",
      "centered",
      "modelAuthority",
      "correcting",
      "zeroStrength",
    ]
    assert [reason.value for reason in LaneCenteringReason] == reason_values
    capnp_reason = custom.LaneCenteringStateSP.Reason
    assert [int(getattr(capnp_reason, name)) for name in reason_values] == list(range(len(reason_values)))

  def test_diagnostics_capnp_roundtrip(self):
    msg = custom.LaneCenteringStateSP.new_message()
    msg.reason = LaneCenteringReason.CORRECTING.value
    msg.speedArmed = True
    msg.active = True
    msg.correctionCurvature = 0.0002
    msg.centerError = 0.17
    msg.laneWidth = 3.6

    with custom.LaneCenteringStateSP.from_bytes(msg.to_bytes()) as decoded:
      assert decoded.reason == custom.LaneCenteringStateSP.Reason.correcting
      assert decoded.speedArmed
      assert decoded.active
      assert np.isclose(decoded.correctionCurvature, 0.0002)
      assert np.isclose(decoded.centerError, 0.17)
      assert np.isclose(decoded.laneWidth, 3.6)

      # Decoded pycapnp enums compare equal to their integer constant but do
      # not share its hash. The production UI must normalize before lookup.
      reason_code = lane_centering_reason_code(decoded.reason)
      assert reason_code == int(custom.LaneCenteringStateSP.Reason.correcting)
      assert LANE_CENTERING_REASON_LABELS[reason_code] == "ACT"

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

  @parameterized.expand([
    (None,),
    ("",),
    ("malformed",),
    (10 ** 10000,),
    (float("nan"),),
    (float("inf"),),
    (-0.01,),
    (1.01,),
  ])
  def test_strength_invalid_values_fail_closed_to_legacy_default(self, value):
    assert lane_centering_strength(value) == LANE_CENTERING_STRENGTH_DEFAULT

  @parameterized.expand([
    (0.0, LANE_CENTERING_STRENGTH_MIN),
    (b"0.30", LANE_CENTERING_STRENGTH_DEFAULT),
    (1.0, LANE_CENTERING_STRENGTH_MAX),
  ])
  def test_strength_exact_bounds_and_param_bytes_are_valid(self, value, expected):
    assert lane_centering_strength(value) == expected

  def test_malformed_runtime_strength_fails_closed_without_correction(self):
    controller = LaneCenteringController()
    model_curvature = 0.0013
    assert _update(controller, _model(left=-1.5, right=2.1), model_curvature=model_curvature,
                   authority=0.0, strength="malformed") == model_curvature
    assert controller.diagnostics.reason == LaneCenteringReason.INVALID_INPUT
    assert not controller.diagnostics.active

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

  @parameterized.expand([
    ({"enabled": False}, LaneCenteringReason.DISABLED),
    ({"active": False}, LaneCenteringReason.LATERAL_INACTIVE),
    ({"valid": False}, LaneCenteringReason.MODEL_INVALID),
    ({"speed": 4.9}, LaneCenteringReason.BELOW_SPEED),
    ({"driver_override": True}, LaneCenteringReason.DRIVER_OVERRIDE),
  ])
  def test_hard_gate_diagnostics(self, kwargs, expected_reason):
    controller = LaneCenteringController()
    assert _update(controller, _model(left=-1.5, right=2.1), **kwargs) == 0.0
    assert controller.diagnostics.reason == expected_reason
    assert not controller.diagnostics.speed_armed
    assert not controller.diagnostics.active

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
    assert controller.diagnostics.reason == LaneCenteringReason.TURN_SIGNAL_FADE
    assert controller.diagnostics.speed_armed
    assert not controller.diagnostics.active

    for _ in range(300):
      fading = _update(controller, model, authority=0.0, pause_on_signal=True, turn_signal_active=True)
    assert abs(fading) < 1e-6

  def test_turn_signal_pause_can_be_disabled(self):
    model = _model(left=-1.5, right=2.1)
    _, output = _converge(model, authority=0.0)
    controller, _ = _converge(model, authority=0.0)
    signaled = _update(controller, model, authority=0.0, turn_signal_active=True)
    assert abs(signaled - output) < 1e-7
    assert controller.diagnostics.reason == LaneCenteringReason.CORRECTING
    assert controller.diagnostics.active

    # This setting controls only the early blinker fade. A model lane-change
    # state always suspends lane centering so it cannot oppose the maneuver.
    lane_change = _model(left=-1.5, right=2.1, lane_change=1)
    assert _update(controller, lane_change, authority=0.0, turn_signal_active=True) == 0.0
    assert controller.diagnostics.reason == LaneCenteringReason.LANE_CHANGE
    assert not controller.diagnostics.active

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
    controller = LaneCenteringController()
    assert _update(controller, model) == 0.0
    expected = LaneCenteringReason.LANE_DATA_INVALID if not np.isfinite(value) else LaneCenteringReason.LANE_CONFIDENCE_LOW
    assert controller.diagnostics.reason == expected

  def test_input_must_cover_lookahead(self):
    model = _model(left=-1.5, right=2.1)
    model.laneLines[1].x = model.laneLines[1].x[:10]
    model.laneLines[1].y = model.laneLines[1].y[:10]
    assert _update(LaneCenteringController(), model) == 0.0

  def test_lane_center_error_steers_toward_center(self):
    controller, right = _converge(_model(left=-1.5, right=2.1), authority=0.0)
    _, left = _converge(_model(left=-2.1, right=1.5), authority=0.0)
    assert right > 0.0
    assert left < 0.0
    diagnostics = controller.diagnostics
    assert diagnostics.reason == LaneCenteringReason.CORRECTING
    assert diagnostics.speed_armed
    assert diagnostics.active
    assert diagnostics.correction_curvature == right
    assert diagnostics.target_correction_curvature > 0.0
    assert np.isclose(diagnostics.center_error, 0.3)
    assert np.isclose(diagnostics.effective_center_error, 0.22)
    assert np.isclose(diagnostics.lane_width, 3.6)
    assert np.isclose(diagnostics.lookahead, _V_EGO)
    assert np.isclose(diagnostics.min_lane_probability, 0.9)
    assert np.isclose(diagnostics.max_lane_std, 0.1)

  def test_small_center_error_does_not_chatter(self):
    controller, output = _converge(_model(left=-1.75, right=1.85), authority=0.0)
    assert output == 0.0
    assert controller.diagnostics.reason == LaneCenteringReason.CENTERED
    assert not controller.diagnostics.active

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
    controller, e2e_authority = _converge(model, authority=1.0)
    assert lane_authority > 0.0
    assert abs(e2e_authority) < 1e-9
    assert controller.diagnostics.reason == LaneCenteringReason.MODEL_AUTHORITY
    assert not controller.diagnostics.active

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

  def test_strength_zero_is_exact_model_output(self):
    model_curvature = -0.0017
    controller = LaneCenteringController()
    for _ in range(300):
      output = _update(controller, _model(left=-1.0, right=2.6, path_std=0.6),
                       model_curvature=model_curvature, authority=0.0, strength=0.0)
      assert output == model_curvature
    assert controller.diagnostics.reason == LaneCenteringReason.ZERO_STRENGTH
    assert controller.diagnostics.correction_curvature == 0.0
    assert controller.diagnostics.target_correction_curvature == 0.0
    assert not controller.diagnostics.active

  def test_strength_is_monotonic_and_preserves_existing_final_envelope(self):
    model = _model(left=0.0, right=3.0, path_std=0.6)
    outputs = [_converge(model, authority=0.0, strength=strength)[1] for strength in (0.0, 0.15, 0.30, 0.50, 1.0)]
    assert outputs == sorted(outputs)
    assert outputs[0] == 0.0
    assert np.isclose(outputs[2], 0.004 * 0.30, atol=1e-6)
    assert all(output <= 0.004 * 0.30 + 1e-12 for output in outputs)

  def test_default_strength_target_preserves_raw_and_final_caps(self):
    rng = np.random.default_rng(0x1A2E)
    samples = np.concatenate((
      np.array([-1.0, -0.004, -0.004 + 1e-12, 0.0, 0.004 - 1e-12, 0.004, 1.0]),
      rng.uniform(-0.02, 0.02, 10_000),
    ))
    controller = LaneCenteringController()
    model = _model()
    for raw_correction in samples:
      bounded = float(np.clip(raw_correction, -0.004, 0.004))
      legacy = bounded * 0.30
      controller._raw_correction = lambda *_: (True, float(raw_correction))
      _update(controller, model, strength=LANE_CENTERING_STRENGTH_DEFAULT)
      assert controller.diagnostics.target_correction_curvature.hex() == legacy.hex()

  def test_strength_changes_ordinary_error_where_model_break_in_is_flat(self):
    # A 10 cm raw disagreement is below the 15 cm model break-in threshold,
    # proving strength and Model Break-In are independent controls.
    model = _model(left=-1.75, right=1.95, path_std=0.1)
    low = _converge(model, authority=1.0, strength=0.30)[1]
    high = _converge(model, authority=1.0, strength=1.0)[1]
    no_break_in = _converge(model, authority=0.0, strength=1.0)[1]
    assert 0.0 < low < high
    assert high == no_break_in
