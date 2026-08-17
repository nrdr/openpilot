from collections.abc import Callable
import pyray as rl

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.sunnypilot.nrdr.handcrafted_lateral import is_handcrafted_lateral_enabled
from openpilot.sunnypilot.nrdr.honda_vgr import get_honda_vgr_profile
from openpilot.sunnypilot.nrdr.steer_ratio_tuning import (
  STEER_RATIO_ENDPOINT_PROFILES,
  get_steer_ratio_endpoint_profile,
)
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.sunnypilot.widgets.list_view import option_item_sp, toggle_item_sp, LineSeparatorSP


class PidfGroundLayout(Widget):
  def __init__(self, back_btn_callback: Callable):
    super().__init__()
    self._back_button = NavButton(tr("Back"))
    self._back_button.set_click_callback(back_btn_callback)

    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=False, spacing=0)

  def _initialize_items(self):
    self._starpilot = toggle_item_sp(
      title=tr("StarPilot PID Additions"),
      description=tr("The borrowed turn-in / unwind / per-direction output scaling (the StarPilot half of _pid_output_scale) " +
                     "not built for Honda. Off = clean banded PID/F + rate-damping D, your center boost kept. " +
                     "Turn on to A/B it against the raw base."),
      param="NrdrStarPilotPid",
    )

    self._legacy_dual_bp_sr = toggle_item_sp(
      title=tr("Use Legacy Dual-BP Steer Ratio (Default: ON)"),
      description=tr("Keeps the current road-tested center-to-outer curve. Turn OFF to test the firmware-derived EPS position " +
                     "map when this car and firmware are recognized. This experimental map covers EPS sensor geometry, not the " +
                     "complete road-wheel ratio; unsupported firmware falls back to legacy. Clarity uses PID only in this mode."),
      param="NrdrLegacyDualBpSteerRatio",
    )

    self._sr_endpoint_controls = []
    for profile in STEER_RATIO_ENDPOINT_PROFILES:
      center = option_item_sp(
        param=profile.center_param,
        title=lambda profile=profile: tr(f"On-Center Steer Ratio (Default: {profile.center_default:.2f})"),
        min_value=800, max_value=2500, value_change_step=1,
        description=lambda: tr("Sets the steer ratio at zero steering-wheel angle. It anchors firmware mode and is the " +
                               "starting value of the legacy center-to-outer curve."),
        label_callback=lambda value: f"{value / 100:.2f}",
        use_float_scaling=True,
      )
      outer = option_item_sp(
        param=profile.outer_param,
        title=lambda profile=profile: tr(f"Outer Steer Ratio (Default: {profile.outer_default:.2f})"),
        min_value=800, max_value=2500, value_change_step=1,
        description=lambda: tr("Sets the high-angle endpoint used by legacy mode, firmware fallback, and the optional " +
                               "lane-change endpoint behavior."),
        label_callback=lambda value: f"{value / 100:.2f}",
        use_float_scaling=True,
      )
      self._sr_endpoint_controls.append((profile, center, outer))

    self._lane_change_endpoint_sr = toggle_item_sp(
      title=tr("Use Endpoint SR for Smoother Lane Changes (Default: ON)"),
      description=tr("While the planner has a lane change active, use this car's Outer Steer Ratio for the entire maneuver. " +
                     "The selected normal steer-ratio mode resumes only after the lane change is complete."),
      param="NrdrLaneChangeEndpointSteerRatio",
    )

    self._lat_p_low = option_item_sp(
      param="LatPScaleLowSpeed",
      title=lambda: tr("Low Speed Proportional Scale (Below 25mph) (Default: 100%)"),
      min_value=0, max_value=500, value_change_step=5,
      description=lambda: tr("Scales the proportional (P) term below 25 mph. Higher = more error correction " +
                             "(tighter, can cut corners); lower = looser with wider swings."),
      label_callback=lambda value: f"{value}%",
    )
    self._lat_i_low = option_item_sp(
      param="LatIScaleLowSpeed",
      title=lambda: tr("Low Speed Integral Scale (Below 25mph) (Default: 100%)"),
      min_value=0, max_value=500, value_change_step=5,
      description=lambda: tr("Scales the integral (I) term below 25 mph. Builds correction over time to erase steady-state error; too high oscillates."),
      label_callback=lambda value: f"{value}%",
    )
    self._lat_f_low = option_item_sp(
      param="LatFScaleLowSpeed",
      title=lambda: tr("Low Speed Feedforward Scale (Below 25mph) (Default: 100%)"),
      min_value=0, max_value=500, value_change_step=5,
      description=lambda: tr("Scales the feedforward (kf) term below 25 mph. Follows the commanded angle rather than error, " +
                             "so it adds authority without amplifying noise. 100% = tuned value (static)."),
      label_callback=lambda value: f"{value}%",
    )

    self._lat_p_standard = option_item_sp(
      param="LatPScaleStandard",
      title=lambda: tr("Standard Speed Proportional Scale (25-50mph) (Default: 100%)"),
      min_value=0, max_value=500, value_change_step=5,
      description=lambda: tr("Scales the proportional (P) term between 25 and 50 mph."),
      label_callback=lambda value: f"{value}%",
    )
    self._lat_i_standard = option_item_sp(
      param="LatIScaleStandard",
      title=lambda: tr("Standard Speed Integral Scale (25-50mph) (Default: 100%)"),
      min_value=0, max_value=500, value_change_step=5,
      description=lambda: tr("Scales the integral (I) term between 25 and 50 mph."),
      label_callback=lambda value: f"{value}%",
    )
    self._lat_f_standard = option_item_sp(
      param="LatFScaleStandard",
      title=lambda: tr("Standard Speed Feedforward Scale (25-50mph) (Default: 100%)"),
      min_value=0, max_value=500, value_change_step=5,
      description=lambda: tr("Scales the feedforward (kf) term between 25 and 50 mph. 100% = tuned value (static)."),
      label_callback=lambda value: f"{value}%",
    )

    self._lat_p_highway = option_item_sp(
      param="LatPScaleHighway",
      title=lambda: tr("Highway Proportional Scale (50mph+) (Default: 100%)"),
      min_value=0, max_value=500, value_change_step=5,
      description=lambda: tr("Scales the proportional (P) term above 50 mph."),
      label_callback=lambda value: f"{value}%",
    )
    self._lat_i_highway = option_item_sp(
      param="LatIScaleHighway",
      title=lambda: tr("Highway Integral Scale (50mph+) (Default: 100%)"),
      min_value=0, max_value=500, value_change_step=5,
      description=lambda: tr("Scales the integral (I) term above 50 mph."),
      label_callback=lambda value: f"{value}%",
    )
    self._lat_f_highway = option_item_sp(
      param="LatFScaleHighway",
      title=lambda: tr("Highway Feedforward Scale (50mph+) (Default: 100%)"),
      min_value=0, max_value=500, value_change_step=5,
      description=lambda: tr("Scales the feedforward (kf) term above 50 mph. 100% = tuned value (static)."),
      label_callback=lambda value: f"{value}%",
    )

    self._rate_damping = option_item_sp(
      param="NrdrLatRateDamping",
      title=lambda: tr("Rate Damping (D) Strength (Default: 30%)"),
      min_value=0, max_value=300, value_change_step=5,
      description=lambda: tr("The derivative term openpilot normally can't use. Adds torque opposing how fast the wheel is moving, " +
                             "which damps the low-speed oscillation plain P can't (the wheel is torque-commanded, so P alone rings). " +
                             "Relies on a clean steering-rate signal and a low-lag EPS - which this car has. 0 = off. " +
                             "Raise until the low-speed wobble flattens; too high makes turn-in feel heavy."),
      label_callback=lambda value: f"{value}%",
    )
    self._rate_damping_fade_speed = option_item_sp(
      param="NrdrLatRateDampingFadeSpeed",
      title=lambda: tr("Rate Damping Fade-Out Speed (Default: 30mph)"),
      min_value=0, max_value=60, value_change_step=1,
      description=lambda: tr("Speed at which rate damping tapers to zero. Damping is strongest at a standstill and gone by this speed, " +
                             "where tire self-aligning torque resumes damping the steering itself. " +
                             "Keeps the D term out of your highway feel."),
      label_callback=lambda value: f"{value} mph",
    )

    self._center_scale = option_item_sp(
      param="HondaCenterScale",
      title=lambda: tr("Center Boost (Default: 50%)"),
      min_value=0,
      max_value=500,
      value_change_step=1,
      description=lambda: tr("Extra proportional (P) error correction near center. It does not multiply integral, feedforward, " +
                             "or damping. Available at every speed above the minimum, including the highway."),
      label_callback=lambda value: f"{value}%",
      use_float_scaling=True,
    )

    self._center_boost_threshold = option_item_sp(
      param="HondaCenterBoostThreshold",
      title=lambda: tr("Center Boost Threshold (°) (Default: 3°)"),
      min_value=0,
      max_value=1000,
      value_change_step=10,
      description=lambda: tr("How centered should the steering wheel be when center boost is actually active?"),
      label_callback=lambda value: f"{value / 100:.1f}°",
      use_float_scaling=True,
    )

    self._center_boost_min_speed = option_item_sp(
      param="HondaCenterBoostMinSpeed",
      title=lambda: tr("Center Boost Minimum Speed (Default: 50mph)"),
      min_value=0,
      max_value=80,
      value_change_step=1,
      description=lambda: tr("Below this speed center boost is disabled. Above the short ramp it remains fully available " +
                             "with no upper-speed cutoff, including on the highway."),
      label_callback=lambda value: f"{value} mph",
    )

    self._lat_stiction = toggle_item_sp(
      title=tr("Predictive Lateral Stiction"),
      description=tr("Lets PID move the wheel normally, then tapers torque before the wheel reaches a stable target and holds it " +
                     "until another correction is needed. Available at every speed; driver input, lane changes, faults, and " +
                     "steering limits bypass it immediately."),
      param="NrdrLatStiction",
    )

    self._nnlc_enabled = toggle_item_sp(
      title=tr("Enable Neural Network Lateral Model (NNLC) (Default: OFF)"),
      description=tr("Use PID at lower speeds and during lane changes, then smoothly hand off to the Clarity neural lateral model " +
                     "at higher speeds. OFF keeps the proven Clarity PID controller active everywhere. NNLC is unavailable while " +
                     "the experimental firmware EPS position map is active."),
      param="NrdrNnlcEnabled",
    )
    self._nnlc_activation_speed = option_item_sp(
      param="NrdrNnlcActivationSpeed",
      title=lambda: tr("Activate NNLC Above (Default: 30mph)"),
      min_value=0, max_value=100, value_change_step=1,
      description=lambda: tr("Center speed of the smooth 6 mph PID-to-NNLC handoff. At the 30 mph default, PID is full through 27 mph " +
                             "and NNLC is full from 33 mph. Lane changes always select PID immediately."),
      label_callback=lambda value: f"{value} mph",
    )

    self._nnlc_kp_gain = option_item_sp(
      param="NrdrNnlcKpGain",
      title=lambda: tr("NNLC KP Gain Scale (Default: 100%)"),
      min_value=0, max_value=300, value_change_step=5,
      description=lambda: tr("NNLC proportional feedback gain. 100% gives kp = 1.0."),
      label_callback=lambda value: f"{value}%",
    )
    self._nnlc_kf_gain = option_item_sp(
      param="NrdrNnlcKfGain",
      title=lambda: tr("NNLC KF Gain Scale (Default: 50%)"),
      min_value=0, max_value=300, value_change_step=5,
      description=lambda: tr("NNLC neural-model feedforward gain. 50% gives kf = 0.5."),
      label_callback=lambda value: f"{value}%",
    )
    self._nnlc_ki_gain = option_item_sp(
      param="NrdrNnlcKiGain",
      title=lambda: tr("NNLC KI Gain Scale (Default: 10%)"),
      min_value=0, max_value=300, value_change_step=5,
      description=lambda: tr("NNLC integral feedback gain. 10% gives ki = 0.1."),
      label_callback=lambda value: f"{value}%",
    )

    return [
      self._starpilot,
      LineSeparatorSP(40),
      self._legacy_dual_bp_sr,
      *(control for _, center, outer in self._sr_endpoint_controls for control in (center, outer)),
      self._lane_change_endpoint_sr,
      LineSeparatorSP(40),
      self._lat_p_low,
      self._lat_i_low,
      self._lat_f_low,
      LineSeparatorSP(40),
      self._lat_p_standard,
      self._lat_i_standard,
      self._lat_f_standard,
      LineSeparatorSP(40),
      self._lat_p_highway,
      self._lat_i_highway,
      self._lat_f_highway,
      LineSeparatorSP(40),
      self._rate_damping,
      self._rate_damping_fade_speed,
      LineSeparatorSP(40),
      self._center_scale,
      self._center_boost_threshold,
      self._center_boost_min_speed,
      self._lat_stiction,
      LineSeparatorSP(40),
      self._nnlc_enabled,
      self._nnlc_activation_speed,
      self._nnlc_kp_gain,
      self._nnlc_kf_gain,
      self._nnlc_ki_gain,
    ]

  def _update_state(self):
    super()._update_state()
    fingerprint = str(ui_state.CP.carFingerprint) if ui_state.CP is not None else ""
    editable = not is_handcrafted_lateral_enabled(fingerprint, ui_state.params)
    active_sr_profile = get_steer_ratio_endpoint_profile(fingerprint)
    firmware_vgr_active = bool(
      ui_state.CP is not None and get_honda_vgr_profile(ui_state.CP) is not None and
      not self._legacy_dual_bp_sr.action_item.get_state()
    )
    sr_controls = [control for _, center, outer in self._sr_endpoint_controls for control in (center, outer)]
    for profile, center, outer in self._sr_endpoint_controls:
      visible = profile == active_sr_profile
      center.set_visible(visible)
      outer.set_visible(visible)
    self._legacy_dual_bp_sr.set_visible(active_sr_profile is not None)
    self._lane_change_endpoint_sr.set_visible(active_sr_profile is not None)
    for item in (
      self._starpilot, *sr_controls, self._lane_change_endpoint_sr,
      self._lat_p_low, self._lat_i_low, self._lat_f_low,
      self._lat_p_standard, self._lat_i_standard, self._lat_f_standard,
      self._lat_p_highway, self._lat_i_highway, self._lat_f_highway,
      self._rate_damping, self._rate_damping_fade_speed,
      self._center_scale, self._center_boost_threshold, self._center_boost_min_speed,
      self._lat_stiction,
    ):
      item.action_item.set_enabled(editable)

    self._legacy_dual_bp_sr.action_item.set_enabled(editable and not ui_state.engaged)

    for item in (self._nnlc_enabled, self._nnlc_activation_speed, self._nnlc_kp_gain, self._nnlc_kf_gain, self._nnlc_ki_gain):
      item.action_item.set_enabled(not firmware_vgr_active)

    nnlc_enabled = self._nnlc_enabled.action_item.get_state()
    self._nnlc_activation_speed.set_visible(nnlc_enabled)
    self._nnlc_kp_gain.set_visible(nnlc_enabled)
    self._nnlc_kf_gain.set_visible(nnlc_enabled)
    self._nnlc_ki_gain.set_visible(nnlc_enabled)

  def _render(self, rect):
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40, rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    self._scroller.show_event()
