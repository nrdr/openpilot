"""
nrdr Lateral Tuning sub-panel.
"""
from collections.abc import Callable
import pyray as rl

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, option_item_sp, LineSeparatorSP


class LateralTuningLayout(Widget):
  def __init__(self, back_btn_callback: Callable):
    super().__init__()
    self._back_button = NavButton(tr("Back"))
    self._back_button.set_click_callback(back_btn_callback)

    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=False, spacing=0)

  def _initialize_items(self):
    self._lat_scale_low = option_item_sp(
      param="LatPidScaleLowSpeed",
      title=lambda: tr("Low Speed PID Scale (Below 25mph) (Default: 100%)"),
      min_value=0,
      max_value=500,
      value_change_step=5,
      description=lambda: tr("Scales lateral PID output below 25 mph. Higher results in more error correction and cutting corners, lower results in wider swings on curves and fewer corrections."),
      label_callback=lambda value: f"{value}%",
    )

    self._lat_scale_standard = option_item_sp(
      param="LatPidScaleStandard",
      title=lambda: tr("Standard Speed PID Scale (25-50mph) (Default: 100%)"),
      min_value=0,
      max_value=500,
      value_change_step=5,
      description=lambda: tr("Scales lateral PID output between 25 and 50 mph. Higher results in more error correction and cutting corners, lower results in wider swings on curves and fewer corrections."),
      label_callback=lambda value: f"{value}%",
    )

    self._lat_scale_highway = option_item_sp(
      param="LatPidScaleHighway",
      title=lambda: tr("Highway PID Scale (50mph+) (Default: 100%)"),
      min_value=0,
      max_value=500,
      value_change_step=5,
      description=lambda: tr("Scales lateral PID output above 50 mph. Higher results in more error correction and cutting corners, lower results in wider swings on curves and fewer corrections."),
      label_callback=lambda value: f"{value}%",
    )

    self._scale_exclude_kf = toggle_item_sp(
      param="NrdrPidScaleExcludeKf",
      title=lambda: tr("Keep Feedforward Static (Default: OFF)"),
      description=lambda: tr("When ON, the PID scales above (and the longitudinal PID scale) multiply only the feedback (P+I) terms; the feedforward (kf) keeps its tuned value instead of being scaled along with them. Turn this on if you raise a PID scale but don't want the feedforward boosted with it."),
    )

    self._center_scale = option_item_sp(
      param="HondaCenterScale",
      title=lambda: tr("Center Scale (Default: 0.50)"),
      min_value=0,
      max_value=500,
      value_change_step=1,
      description=lambda: tr("Raise this to add extra error correction while driving straight at high speeds. Sometimes the perfect lateral tune is too soft for driving in a straight line."),
      label_callback=lambda value: f"{value / 100:.2f}",
      use_float_scaling=True,
    )

    self._unwind_freeze = toggle_item_sp(
      param="HondaUnwindFreeze",
      title=lambda: tr("Unwind Integrator Freeze (Default: OFF)"),
      description=lambda: tr("Freezes the PID integrator while the steering is returning toward center, so it doesn't hold torque through the unwind."),
    )

    self._unwind_lookahead = toggle_item_sp(
      param="HondaUnwindLookahead",
      title=lambda: tr("Unwind Lookahead (Default: ON)"),
      description=lambda: tr("Reads the model's planned path to start unwinding earlier, before the instantaneous desired curvature drops."),
    )

    self._low_pass_filter = toggle_item_sp(
      param="HondaTorqueLowPassFilter",
      title=lambda: tr("Low Pass Filter (tau) (Default: ON)"),
      description=lambda: tr("Filter that smooths steering response at the cost of adding lag. Tune to the least amount possible before oscillations begin. Live tests show that going above 0.1 tau rapidly increases the possibility of lag-induced oscillations."),
    )

    self._lpf_tau_low = option_item_sp(
      param="HondaLpfTauLowSpeed",
      title=lambda: tr("Low Pass Filter Tau (Below 25mph) (Default: 0.1)"),
      min_value=0,
      max_value=500,
      value_change_step=1,
      description=lambda: tr("Low-pass filter time constant (seconds) below 25 mph."),
      label_callback=lambda value: f"{value / 100:.2f}",
      use_float_scaling=True,
    )

    self._lpf_tau_standard = option_item_sp(
      param="HondaLpfTauStandard",
      title=lambda: tr("Standard Tau (25-50mph) (Default: 0.1)"),
      min_value=0,
      max_value=500,
      value_change_step=1,
      description=lambda: tr("Low-pass filter time constant (seconds) between 25 and 50 mph."),
      label_callback=lambda value: f"{value / 100:.2f}",
      use_float_scaling=True,
    )

    self._lpf_tau_highway = option_item_sp(
      param="HondaLpfTauHighway",
      title=lambda: tr("Highway Tau (50mph+) (Default: 0.1)"),
      min_value=0,
      max_value=500,
      value_change_step=1,
      description=lambda: tr("Low-pass filter time constant (seconds) above 50 mph."),
      label_callback=lambda value: f"{value / 100:.2f}",
      use_float_scaling=True,
    )

    self._notch_enabled = toggle_item_sp(
      param="HondaNotchEnabled",
      title=lambda: tr("Notch Filter (Default: ON)"),
      description=lambda: tr("Removes a narrow EPS chatter band (around 7Hz) without the lag a low pass filter adds."),
    )

    self._notch_freq = option_item_sp(
      param="HondaNotchFreq",
      title=lambda: tr("Notch Frequency (Default: 7.5)"),
      min_value=100,
      max_value=2000,
      value_change_step=10,
      description=lambda: tr("Frequency (Hz) of the band eliminated from the controller. If you know what Hz your EPS growls at, this can help block that out without adding any extra lag into the controller. Best used in pair with a well-tuned low pass filter."),
      label_callback=lambda value: f"{value / 100:.1f} Hz",
      use_float_scaling=True,
    )

    self._notch_q = option_item_sp(
      param="HondaNotchQ",
      title=lambda: tr("Notch Q / Width (Default: 1.5)"),
      min_value=10,
      max_value=1000,
      value_change_step=10,
      description=lambda: tr("Tolerance of the removed frequency. Higher = smaller portion removed, lower = wider (nearby frequencies will be removed as well)."),
      label_callback=lambda value: f"{value / 100:.2f}",
      use_float_scaling=True,
    )

    self._steer_delta_limiter = toggle_item_sp(
      param="HondaSteerDeltaLimiter",
      title=lambda: tr("Legacy Steer Delta Rate Limiter (Default: OFF)"),
      description=lambda: tr("Limits how quickly requested steering torque can rise or fall. This is an older system of limiting and may no longer prove useful compared to the low pass and notch filters."),
    )

    self._steer_delta_up = option_item_sp(
      param="HondaSteerDeltaUp",
      title=lambda: tr("Steer Delta Up (Default: 3.0)"),
      min_value=0,
      max_value=10000,
      value_change_step=10,
      description=lambda: tr("Controls the maximum upward steering torque rate when the rate limiter is enabled. Too low will add lag."),
      label_callback=lambda value: f"{value / 100:.1f}",
      use_float_scaling=True,
    )

    self._steer_delta_down = option_item_sp(
      param="HondaSteerDeltaDown",
      title=lambda: tr("Steer Delta Down (Default: 3.0)"),
      min_value=0,
      max_value=10000,
      value_change_step=10,
      description=lambda: tr("Controls the maximum downward steering torque rate when the rate limiter is enabled. Too low will add lag."),
      label_callback=lambda value: f"{value / 100:.1f}",
      use_float_scaling=True,
    )

    return [
      self._low_pass_filter,
      self._lat_scale_low,
      self._lpf_tau_low,
      self._lat_scale_standard,
      self._lpf_tau_standard,
      self._lat_scale_highway,
      self._lpf_tau_highway,
      self._scale_exclude_kf,
      LineSeparatorSP(40),
      self._center_scale,
      LineSeparatorSP(40),
      self._unwind_freeze,
      self._unwind_lookahead,
      LineSeparatorSP(40),
      self._notch_enabled,
      self._notch_freq,
      self._notch_q,
      LineSeparatorSP(40),
      self._steer_delta_limiter,
      self._steer_delta_up,
      self._steer_delta_down,
    ]

  def _update_state(self):
    super()._update_state()

    lpf_enabled = self._low_pass_filter.action_item.get_state()
    self._lpf_tau_low.set_visible(lpf_enabled)
    self._lpf_tau_standard.set_visible(lpf_enabled)
    self._lpf_tau_highway.set_visible(lpf_enabled)

    notch_enabled = self._notch_enabled.action_item.get_state()
    self._notch_freq.set_visible(notch_enabled)
    self._notch_q.set_visible(notch_enabled)

    steer_delta_limiter_enabled = self._steer_delta_limiter.action_item.get_state()
    self._steer_delta_up.set_visible(steer_delta_limiter_enabled)
    self._steer_delta_down.set_visible(steer_delta_limiter_enabled)

  def _render(self, rect):
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40, rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    self._scroller.show_event()
