"""C4 Device stock-cruise cards without graphics, native Params or vehicle I/O."""
import ast
import itertools
from types import SimpleNamespace as NS

import pytest

from opendbc.car.honda.values import CAR, HondaFlags
from openpilot.nrdr.tests.test_honda_pcm_ui import ROOT, Widget, _font_advance_upper_bound, state
from openpilot.nrdr.ui.icbm import ICBM_DESCRIPTION, icbm_available, save_icbm_choice

FACTORY = "HondaEnforceStockLongitudinal"
ICBM = "IntelligentCruiseButtonManagement"
KEYS = (FACTORY, ICBM)


class Toggle(Widget):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.checked = kwargs.get("initial_state", False)

  def set_checked(self, value):
    self.checked = value


def controls(ui):
  path = ROOT / "openpilot/nrdr/ui/settings/icbm_mici.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  tree.body = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))]
  env = {"CAR": CAR, "HondaFlags": HondaFlags, "BigToggle": Toggle, "ui_state": ui, "tr": lambda text: text,
         "ICBM_DESCRIPTION": ICBM_DESCRIPTION, "icbm_available": icbm_available, "save_icbm_choice": save_icbm_choice}
  exec(compile(tree, str(path), "exec"), env)
  return env, {control._key: control for control in env["stock_cruise_controls"]()}


def civic(**kwargs):
  return state(**({"flags": int(HondaFlags.NIDEC)} | kwargs))


@pytest.mark.parametrize("saved", [None, False, True])
def test_opening_cards_defaults_off_and_preserves_saved_choices(saved):
  ui = civic()
  if saved is not None:
    ui.params.values.update(dict.fromkeys(KEYS, saved))
  before = dict(ui.params.values)
  _, cards = controls(ui)
  for card in cards.values():
    assert card.checked is bool(saved)
    assert card.value == ("Saved: On" if saved else "Saved: Off")
    assert card.enabled()
    assert "param" not in card.kwargs
    card._update_state()
  assert ui.params.values == before and not ui.params.writes


@pytest.mark.parametrize("key", KEYS)
@pytest.mark.parametrize("selected,openlong", list(itertools.product((False, True), repeat=2)))
def test_explicit_choices_are_independent_and_request_only_next_drive_cycle(key, selected, openlong):
  ui = civic(openpilotLongitudinalControl=openlong)
  ui.params.values.update({FACTORY: not selected, ICBM: not selected, "HondaLiveLearningGas": True, "NrdrHondaLegacyPcm": True,
                           "NrdrHondaPcmFixedCruise": True, "NrdrHondaWindBrake": True, "NrdrHondaPcmMode": 2,
                           "SavedLearning": b"keep", "ModelSelection": "keep"})
  before = dict(ui.params.values)
  _, cards = controls(ui)
  cards[key].kwargs["toggle_callback"](selected)
  assert cards[key].checked is selected
  assert cards[key].value == ("Saved: On" if selected else "Saved: Off")
  assert ui.params.writes == [(key, selected), ("OnroadCycleRequested", True)]
  assert all(ui.params.get(name) == value for name, value in before.items() if name != key)
  assert ui.CP.openpilotLongitudinalControl is openlong


@pytest.mark.parametrize("key", KEYS)
@pytest.mark.parametrize("bad", [None, 0, 1, "0", "true", 1.0, [], {}])
def test_callbacks_reject_non_boolean_values_without_repair(key, bad):
  ui = civic()
  ui.params.values[key] = True
  _, cards = controls(ui)
  cards[key]._select(bad)
  assert cards[key].checked is True
  assert not ui.params.writes


@pytest.mark.parametrize("key", KEYS)
@pytest.mark.parametrize("change", ["onroad", "unknown_road", "missing_cp", "missing_sp", "other_civic", "clarity",
                                   "interceptor", "bosch", "no_nidec"])
def test_click_time_rechecks_do_not_enable_from_stale_display(key, change):
  ui = civic()
  _, cards = controls(ui)
  card = cards[key]
  assert card.enabled()
  if change in ("onroad", "unknown_road"):
    ui.params.values["IsOffroad"] = False if change == "onroad" else None
  elif change == "missing_cp":
    ui.CP = None
  elif change == "missing_sp":
    ui.CP_SP = None
  elif change in ("other_civic", "clarity"):
    ui.CP.carFingerprint = CAR.HONDA_CIVIC_BOSCH if change == "other_civic" else CAR.HONDA_CLARITY
  elif change == "interceptor":
    ui.CP_SP.enableGasInterceptor = True
  elif change == "bosch":
    ui.CP.flags |= int(HondaFlags.BOSCH)
  else:
    ui.CP.flags = 0
  card._select(True)
  card._update_state()
  assert not card.enabled() and card.checked is False
  assert not ui.params.writes


@pytest.mark.parametrize("case", ["other_brand", "passive", "dashcamOnly"])
def test_factory_control_is_narrowly_civic_and_not_passive(case):
  ui = civic()
  _, cards = controls(ui)
  if case == "other_brand":
    ui.CP.brand = "toyota"
  else:
    setattr(ui.CP, case, True)
  cards[FACTORY]._select(True)
  assert not cards[FACTORY].enabled()
  assert not ui.params.writes


def test_icbm_uses_shared_existing_platform_capability_without_enabling_factory_choice():
  ui = civic(brand="toyota", carFingerprint="OTHER_SUPPORTED_ICBM", flags=0)
  ui.CP_SP.intelligentCruiseButtonManagementAvailable = True
  _, cards = controls(ui)
  assert cards[ICBM].enabled() and not cards[FACTORY].enabled()
  cards[ICBM]._select(True)
  assert ui.params.writes == [(ICBM, True), ("OnroadCycleRequested", True)]
  assert ui.params.get(FACTORY) is None


def test_external_saved_changes_refresh_without_writes_or_claiming_active():
  ui = civic()
  _, cards = controls(ui)
  ui.params.values.update(dict.fromkeys(KEYS, True))
  ui.params.values["IsOffroad"] = False
  for card in cards.values():
    card._update_state()
    assert card.checked is True and card.value == "Saved: On"
    assert not card.enabled()
  assert not ui.params.writes


def test_card_copy_and_geometry_fit_c4_without_a_reboot_claim():
  _, cards = controls(civic())
  assert ICBM_DESCRIPTION in cards[ICBM].kwargs["description"]
  for card in cards.values():
    description = card.kwargs["description"]
    assert "Default Off" in description and "Change while parked" in description
    assert "factory ACC" in description and "following distance" in description
    assert "Applies next drive; no device reboot." in description
    assert "restart required" not in description.lower()
    width = card._title_width_hint()
    assert width == card._subtitle_width_hint() == 266
    lines = []
    for word in card.text.split():
      candidate = f"{lines[-1]} {word}" if lines else word
      if lines and _font_advance_upper_bound("Inter-Bold.ttf", candidate, 30) <= width:
        lines[-1] = candidate
      else:
        lines.append(word)
    assert len(lines) <= 2
    assert all(_font_advance_upper_bound("Inter-Bold.ttf", line, 30) < width for line in lines)
    assert all(_font_advance_upper_bound("Inter-Regular.ttf", text, 36) < width for text in ("Saved: Off", "Saved: On"))
    assert 30 * 1.16 * (1 + .9 * (len(lines) - 1)) + 36 * 1.16 + 10 < 180 - 2 * card.LABEL_VERTICAL_PADDING


def test_device_integration_adds_both_cards_and_refreshes_them_on_open():
  ui = civic()
  env, _ = controls(ui)
  items = []
  refreshes = []

  class DeviceBase:
    def __init__(self):
      self._scroller = NS(add_widgets=items.extend)

    def show_event(self):
      refreshes.append("device")

  env.update(DeviceLayoutMici=DeviceBase, longitudinal_controls=lambda: [NS()],
             attach_mici_automatic_shutdown_control=lambda _: NS(refresh=lambda: refreshes.append("power")))
  path = ROOT / "openpilot/selfdrive/ui/sunnypilot/mici/layouts/device.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  tree.body = [node for node in tree.body if isinstance(node, ast.ClassDef)]
  exec(compile(tree, str(path), "exec"), env)
  device = env["DeviceLayoutMiciSP"]()
  assert [control._key for control in items[:2]] == list(KEYS)
  ui.params.values.update(dict.fromkeys(KEYS, True))
  device.show_event()
  assert refreshes == ["device", "power"]
  assert all(control.checked is True and control.value == "Saved: On" for control in items[:2])
  assert not ui.params.writes
