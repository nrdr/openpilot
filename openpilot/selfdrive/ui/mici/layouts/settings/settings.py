from openpilot.common.params import Params
from openpilot.system.ui.widgets.scroller import NavScroller
from openpilot.selfdrive.ui.mici.widgets.button import BigButton
from openpilot.selfdrive.ui.mici.layouts.settings.toggles import TogglesLayoutMici
from openpilot.selfdrive.ui.mici.layouts.settings.network.network_layout import NetworkLayoutMici
from openpilot.selfdrive.ui.mici.layouts.settings.device import DeviceLayoutMici, PairBigButton
from openpilot.selfdrive.ui.mici.layouts.settings.developer import DeveloperLayoutMici
from openpilot.selfdrive.ui.mici.layouts.settings.software import SoftwareLayoutMici
from openpilot.selfdrive.ui.mici.layouts.settings.firehose import FirehoseLayout
from openpilot.system.ui.lib.application import gui_app, FontWeight


class SettingsBigButton(BigButton):
  def _get_label_font_size(self):
    return 64


class SettingsLayout(NavScroller):
  def __init__(self):
    super().__init__()
    self._params = Params()

    self._toggles_panel = TogglesLayoutMici()
    self._toggles_btn = SettingsBigButton("toggles", "", gui_app.texture("icons_mici/settings.png", 64, 64))
    self._toggles_btn.set_click_callback(lambda: gui_app.push_widget(self._toggles_panel))

    self._network_panel = NetworkLayoutMici()
    self._network_btn = SettingsBigButton("network", "", gui_app.texture("icons_mici/settings/network/wifi_strength_full.png", 76, 56))
    self._network_btn.set_click_callback(lambda: gui_app.push_widget(self._network_panel))

    self._device_panel = DeviceLayoutMici()
    self._device_btn = SettingsBigButton("device", "", gui_app.texture("icons_mici/settings/device_icon.png", 72, 58))
    self._device_btn.set_click_callback(lambda: gui_app.push_widget(self._device_panel))

    self._software_panel = SoftwareLayoutMici()
    self._software_btn = SettingsBigButton("software", "", gui_app.texture("icons_mici/settings/software.png", 64, 75))
    self._software_btn.set_click_callback(lambda: gui_app.push_widget(self._software_panel))

    self._developer_panel = DeveloperLayoutMici()
    self._developer_btn = SettingsBigButton("developer", "", gui_app.texture("icons_mici/settings/developer_icon.png", 64, 60))
    self._developer_btn.set_click_callback(lambda: gui_app.push_widget(self._developer_panel))

    self._firehose_panel = FirehoseLayout()
    self._firehose_btn = SettingsBigButton("firehose", "", gui_app.texture("icons_mici/settings/firehose.png", 52, 62))
    self._firehose_btn.set_click_callback(lambda: gui_app.push_widget(self._firehose_panel))

    self._pair_btn = PairBigButton()

    self._scroller.add_widgets([
      self._toggles_btn,
      self._network_btn,
      self._device_btn,
      self._software_btn,
      self._pair_btn,
      self._firehose_btn,
      self._developer_btn,
    ])

    self._font_medium = gui_app.font(FontWeight.MEDIUM)
