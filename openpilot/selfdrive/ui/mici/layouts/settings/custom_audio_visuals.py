from openpilot.selfdrive.ui.mici.widgets.button import BigMultiToggle, BigToggle
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets.scroller import NavScroller


class CustomAudioVisualsLayoutMici(NavScroller):
  def __init__(self):
    super().__init__()
    self._sound_labels = [tr("Current"), tr("June 2026")]
    self._engagement_sounds = BigMultiToggle(
      tr("Engagement\nSounds"),
      self._sound_labels,
      select_callback=self._on_sound_pack,
      font_size=40,
      description=tr(
        "Choose engage, disengage and engagement-refused sounds with their matching automatic volume. Other alerts are unchanged. " +
        "Applies to the next chime without reboot. Quiet Mode still mutes these sounds."
      ),
    )
    self._confidence_ball = BigToggle(
      tr("Confidence Ball"), initial_state=ui_state.params.get("NrdrConfidenceBall", return_default=True),
      toggle_callback=lambda value: ui_state.params.put_bool("NrdrConfidenceBall", value, block=True), font_size=36,
      description=tr("Show the C4 confidence ball. Off hides it completely and stops its animation. Applies live."),
    )
    self._developer_sidebar = BigToggle(
      tr("Developer Sidebar"), initial_state=ui_state.params.get("NrdrDeveloperSidebar", return_default=True),
      toggle_callback=lambda value: ui_state.params.put_bool("NrdrDeveloperSidebar", value, block=True), font_size=34,
      description=tr("Show the C4 developer strip with the ball fixed beside it. " +
                     "Off hides the strip and restores the ball's original animated position. Applies live."),
    )
    self._scroller.add_widgets([self._engagement_sounds, self._confidence_ball, self._developer_sidebar])

  def _on_sound_pack(self, value: str):
    ui_state.params.put("NrdrEngagementSoundPack", self._sound_labels.index(value), block=True)

  def show_event(self):
    super().show_event()
    value = ui_state.params.get("NrdrEngagementSoundPack", return_default=True)
    self._engagement_sounds.set_value(self._sound_labels[1 if value == 1 else 0])
    self._confidence_ball.set_checked(ui_state.params.get("NrdrConfidenceBall", return_default=True))
    self._developer_sidebar.set_checked(ui_state.params.get("NrdrDeveloperSidebar", return_default=True))
