"""BP-styled Toggles panel — mirrors selfdrive/ui/mici/layouts/settings/toggles.py.

Same param keys, same enable/disable gates, same toggles in the same order — but
rendered as a one-item-per-page paged carousel.
"""
from openpilot.selfdrive.ui.bp.mici.widgets.sub_panel import BPSubPanel
from openpilot.selfdrive.ui.bp.mici.widgets.cards import BigToggleCard, BigMultiToggleCard


class TogglesLayoutBP(BPSubPanel):
  TITLE = "Toggles"

  def _build_pages(self):
    return [
      BigMultiToggleCard(
        "Driving Personality",
        "Pick how aggressive bluepilot follows the car ahead.",
        options=["aggressive", "standard", "relaxed"],
        param_key="LongitudinalPersonality",
      ),
      BigToggleCard(
        "Experimental Mode",
        "End-to-end longitudinal control. Behavior may change without warning.",
        param_key="ExperimentalMode",
      ),
      BigToggleCard(
        "Use Metric Units",
        "Display speed in km/h instead of mph.",
        param_key="IsMetric",
      ),
      BigToggleCard(
        "Lane Departure Warnings",
        "Visual + audible alert when you drift out of your lane unintentionally.",
        param_key="IsLdwEnabled",
      ),
      BigToggleCard(
        "Always-on Driver Monitor",
        "Track driver attention even while bluepilot is disengaged.",
        param_key="AlwaysOnDM",
      ),
      BigToggleCard(
        "Record & Upload Driver Camera",
        "Send driver-facing footage to comma after each drive.",
        param_key="RecordFront",
      ),
      BigToggleCard(
        "Record & Upload Mic Audio",
        "Save in-cabin microphone audio with each drive.",
        param_key="RecordAudio",
      ),
      BigToggleCard(
        "Enable bluepilot",
        "Master gate. When off, bluepilot will not engage.",
        param_key="OpenpilotEnabledToggle",
      ),
    ]
