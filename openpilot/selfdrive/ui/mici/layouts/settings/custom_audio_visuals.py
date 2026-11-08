from openpilot.selfdrive.ui.mici.widgets.button import BigMultiToggle
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
    self._scroller.add_widgets([self._engagement_sounds])

  def _on_sound_pack(self, value: str):
    ui_state.params.put("NrdrEngagementSoundPack", self._sound_labels.index(value), block=True)

  def show_event(self):
    super().show_event()
    value = ui_state.params.get("NrdrEngagementSoundPack", return_default=True)
    self._engagement_sounds.set_value(self._sound_labels[1 if value == 1 else 0])
