"""Execute production display methods without starting the graphical UI."""

import ast
from pathlib import Path
from types import SimpleNamespace

import pytest

from openpilot.nrdr.ui.onroad.lateral_state import lateral_control_kind


class CheckedUnion:
  def __init__(self, kind):
    self.kind = kind

  def which(self):
    return self.kind

  def __getattr__(self, name):
    if name != self.kind:
      raise AssertionError(f"Inactive union access: {name}, selected {self.kind}")
    return SimpleNamespace(steeringAngleDesiredDeg=4.2, steeringAngleDeg=3.5)


class Messages(dict):
  def __init__(self, kind, *, received=100, alive=True, valid=True, active=False):
    super().__init__(controlsState=SimpleNamespace(lateralControlState=CheckedUnion(kind)),
                     carState=SimpleNamespace(steeringAngleDeg=1.0), carControl=SimpleNamespace(latActive=active))
    self.recv_frame = {"controlsState": received}
    self.alive = {"controlsState": alive}
    self.valid = {"controlsState": valid}


def production_method(relative, cls_name, method_name):
  path = Path(__file__).resolve().parents[2] / relative
  tree = ast.parse(path.read_text(encoding="utf-8"))
  cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == cls_name)
  method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == method_name)
  namespace = {
    "lateral_control_kind": lateral_control_kind,
    "ui_state": SimpleNamespace(started_frame=50, is_metric=False),
    "UiElement": lambda value, label, unit, color: SimpleNamespace(value=value, label=label, unit=unit, color=color),
    "rl": SimpleNamespace(WHITE="white", RED="red", Color=lambda *args: args),
  }
  exec(compile(ast.Module(body=[method], type_ignores=[]), str(path), "exec"), namespace)
  return namespace[method_name]


@pytest.fixture
def display():
  elements = "selfdrive/ui/sunnypilot/onroad/developer_ui/elements.py"
  pid_update = production_method(elements, "DesiredSteeringPIDElement", "update")
  angle_update = production_method(elements, "DesiredSteeringAngleElement", "update")
  desired = production_method("nrdr/ui/onroad/mici_onroad.py", "StripDevUiRenderer", "_desired")
  element = SimpleNamespace(unit="")
  renderer = SimpleNamespace(
    desired_pid_steer_elem=SimpleNamespace(update=lambda sm, metric: pid_update(element, sm, metric)),
    desired_steer_elem=SimpleNamespace(update=lambda sm, metric: angle_update(element, sm, metric)),
    desired_lat_accel_elem=SimpleNamespace(update=lambda *_: SimpleNamespace(value="torque")),
  )
  return lambda sm: desired(renderer, sm), lambda sm: pid_update(element, sm, False), lambda sm: angle_update(element, sm, False)


@pytest.mark.parametrize("state", ("indiStateDEPRECATED", "lqrStateDEPRECATED", "debugState", "curvatureState", "futureState"))
@pytest.mark.parametrize("active", (False, True))
def test_non_pid_union_never_falls_back_to_pid(display, state, active):
  for render in display:
    assert render(Messages(state, active=active)).value == "--"


@pytest.mark.parametrize("changes", ({"received": 0}, {"received": 49}, {"alive": False}, {"valid": False}))
def test_missing_stale_or_invalid_control_state_is_not_read(display, changes):
  messages = Messages("pidState", **changes)
  del messages["controlsState"]  # Fails if any display accesses the unavailable data.
  for render in display:
    assert render(messages).value == "--"


def test_ready_pid_and_angle_displays_preserve_normal_values(display):
  strip, pid, angle = display
  assert strip(Messages("pidState", active=True)).value == "4.2°"
  assert pid(Messages("pidState", active=True)).value == "4.2°"
  assert strip(Messages("angleState", active=True)).value == "3.5°"
  assert angle(Messages("angleState", active=True)).value == "3.5°"
  assert strip(Messages("torqueState", active=True)).value == "torque"
  assert pid(Messages("pidState", active=False)).value == "-"
  assert angle(Messages("angleState", active=False)).value == "-"
  assert pid(Messages("angleState", active=True)).value == "--"
  assert angle(Messages("pidState", active=True)).value == "--"


def test_first_valid_controller_message_recovers_without_recreating_ui(display):
  strip, _, _ = display
  messages = Messages("indiStateDEPRECATED", received=0)
  assert strip(messages).value == "--"
  messages.recv_frame["controlsState"] = 51
  messages["controlsState"].lateralControlState = CheckedUnion("pidState")
  messages["carControl"].latActive = True
  assert strip(messages).value == "4.2°"


def test_native_default_union_and_pid_transition_when_capnp_available(display):
  pytest.importorskip("capnp")
  from openpilot.cereal import log
  messages = Messages("pidState")
  native = log.ControlsState.new_message()
  messages["controlsState"] = native.as_reader()
  strip, pid, angle = display
  assert native.lateralControlState.which() == "indiStateDEPRECATED"
  assert strip(messages).value == pid(messages).value == angle(messages).value == "--"
  native.lateralControlState.init("pidState")
  native.lateralControlState.pidState.steeringAngleDesiredDeg = 4.2
  messages["controlsState"] = native.as_reader()
  messages["carControl"].latActive = True
  assert strip(messages).value == "4.2°"
