"""Native ICBM schema/conversion/Civic packet acceptance in private staging.

Real production imports and capnp messages, not AST extracts. No live Params,
stats writes, publishers, subscribers, CAN transport, or onroad processes.
Windows deliberately skips before importing native host dependencies.
"""
import sys
from pathlib import Path

import pytest

if sys.platform == "win32":
  pytest.skip("Native ICBM acceptance runs in the private Linux overlay", allow_module_level=True)

from opendbc.car import structs
from opendbc.car.honda.tests import test_stock_icbm as stock_icbm
from opendbc.car.honda.values import CruiseButtons, HondaFlags
from opendbc.sunnypilot.car.honda.icbm import IntelligentCruiseButtonManagementInterface
from openpilot.cereal import custom, messaging
from openpilot.common import params as native_params
from openpilot.common.constants import CV
from openpilot.selfdrive.car import helpers
from openpilot.sunnypilot.selfdrive.car import cruise_ext, interfaces
from openpilot.sunnypilot.selfdrive.car.intelligent_cruise_button_management import controller


class MemoryParams:
  def __init__(self):
    self.reads = []

  def get_bool(self, key):
    assert key == "IntelligentCruiseButtonManagement"
    self.reads.append(key)
    return True


@pytest.fixture(autouse=True)
def no_external_io(monkeypatch):
  def forbidden(*args, **kwargs):
    pytest.fail("Native ICBM test attempted Params, stats, or messaging I/O")

  # Keep actual native module imports, but prohibit opening any Params store.
  monkeypatch.setattr(native_params, "Params", forbidden)
  monkeypatch.setattr(interfaces, "Params", forbidden)
  monkeypatch.setattr(cruise_ext, "Params", forbidden)
  monkeypatch.setattr(interfaces.STATSLOGSP, "raw", forbidden)
  monkeypatch.setattr(interfaces.STATSLOGSP, "_send", forbidden)
  monkeypatch.setattr(interfaces.STATSLOGSP, "connect", forbidden)
  for name in ("PubMaster", "SubMaster", "pub_sock", "sub_sock"):
    monkeypatch.setattr(messaging, name, forbidden)


def setup_stock_icbm(*, modified_eps=False):
  ci = stock_icbm.build(modified_eps=modified_eps)
  assert not ci.CP.openpilotLongitudinalControl and ci.CP.pcmCruise
  assert ci.CP_SP.intelligentCruiseButtonManagementAvailable and ci.CP_SP.pcmCruiseSpeed
  params = MemoryParams()
  # Actual startup admission with explicit in-memory Params; do not invoke the
  # broader setup_interfaces(), which intentionally emits configuration stats.
  interfaces._initialize_intelligent_cruise_button_management(ci.CP, ci.CP_SP, params)
  assert params.reads == ["IntelligentCruiseButtonManagement"]
  assert not ci.CP_SP.pcmCruiseSpeed
  cp_sp = helpers.convert_to_capnp(ci.CP_SP)
  host = controller.IntelligentCruiseButtonManagement(ci.CP, cp_sp.as_reader())
  cc = structs.CarControl.new_message(enabled=True)
  return ci, host, cc


def convert_host_command(host):
  capnp_command = custom.CarControlSP.new_message()
  icbm = capnp_command.intelligentCruiseButtonManagement
  icbm.state = host.state
  icbm.sendButton = host.cruise_button
  icbm.vTarget = float(host.v_target)
  # Exercise the serialized reader boundary used by card, not a hand-built
  # opendbc dataclass that could conceal enum/schema conversion failures.
  with custom.CarControlSP.from_bytes(capnp_command.to_bytes()) as reader:
    converted = helpers.convert_carControlSP(reader)
  assert isinstance(converted, structs.CarControlSP)
  assert isinstance(converted.intelligentCruiseButtonManagement, structs.IntelligentCruiseButtonManagement)
  assert converted.intelligentCruiseButtonManagement.state == str(icbm.state)
  assert converted.intelligentCruiseButtonManagement.sendButton == str(icbm.sendButton)
  assert icbm.state.raw == host.state and icbm.sendButton.raw == host.cruise_button
  assert converted.intelligentCruiseButtonManagement.vTarget == float(host.v_target)
  return converted


def send_adapter(ci, cc, command, frame):
  return IntelligentCruiseButtonManagementInterface.update(
    ci.CC, cc.as_reader(), command, ci.CS, ci.CC.packer, frame, ci.CC.last_button_frame, ci.CC.CAN,
  )


def test_native_module_imports_use_overlay_and_one_schema_family():
  root = Path(__file__).resolve().parents[3]
  # C4 staging keeps opendbc beside root; root/opendbc may point at the active
  # checkout and must not win import resolution. Ordinary Linux checkouts keep
  # their private opendbc_repo inside the root instead.
  dbc = root.parent / "opendbc_repo"
  if not dbc.is_dir():
    dbc = root / "opendbc_repo"
  assert Path(stock_icbm.__file__).resolve().is_relative_to(dbc.resolve())
  for module in (controller, interfaces):
    assert Path(module.__file__).resolve().is_relative_to(root)
  # Unchanged helpers.py may be a read-only symlink to the active checkout.
  assert controller.car is structs.car
  assert controller.custom is helpers.custom is custom
  assert controller.IntelligentCruiseButtonManagement.__module__ == controller.__name__
  assert callable(helpers.convert_carControlSP)
  assert helpers.convert_carControlSP.__module__ == helpers.__name__
  assert native_params.lib is not None  # Actual native import, no Params handle opened.


@pytest.mark.parametrize("modified_eps", [False, True])
@pytest.mark.parametrize("metric", [False, True])
@pytest.mark.parametrize("direction,button", [("increase", CruiseButtons.RES_ACCEL), ("decrease", CruiseButtons.DECEL_SET)])
def test_native_host_capnp_conversion_to_civic_button_packet(modified_eps, metric, direction, button):
  ci, host, cc = setup_stock_icbm(modified_eps=modified_eps)
  conversion = CV.KPH_TO_MS if metric else CV.MPH_TO_MS
  ci.CS.out.cruiseState.speedCluster = 50 * conversion
  target = 55 if direction == "increase" else 45
  plan = custom.LongitudinalPlanSP.new_message(vTarget=target * conversion)
  sends = []
  for frame in range(41):
    host.run(ci.CS.out.as_reader(), cc.as_reader(), plan.as_reader(), metric)
    command = convert_host_command(host)
    packets = send_adapter(ci, cc, command, frame)
    if frame < 40:
      assert command.intelligentCruiseButtonManagement.sendButton == "none"
      assert packets == []
    sends.extend(packets)
  assert host.v_target == target
  assert host.cruise_button == getattr(controller.SendButtonState, direction)
  assert len(sends) == 1
  packet = sends[0]
  assert packet[0] == 0x296 and packet[2] == ci.CC.CAN.camera and len(packet[1]) == 4
  decoded = stock_icbm.decode(ci.CP, packet)
  assert decoded["CRUISE_BUTTONS"] == button and decoded["CRUISE_SETTING"] == 0
  assert decoded["COUNTER"] == 0
  assert ci.CC.last_button_frame == 40
  # Packet generation only: nothing publishes or transmits these bytes.


@pytest.mark.parametrize("reason", ["fixed_op_long", "standstill", "manual_lkas"])
def test_native_ineligible_host_clears_serialized_pending_command(reason):
  ci, host, cc = setup_stock_icbm(modified_eps=True)
  ci.CS.out.cruiseState.speedCluster = 20.
  plan = custom.LongitudinalPlanSP.new_message(vTarget=25.)
  for _ in range(41):
    host.run(ci.CS.out.as_reader(), cc.as_reader(), plan.as_reader(), True)
  assert host.cruise_button == controller.SendButtonState.increase
  if reason == "fixed_op_long":
    ci.CP.openpilotLongitudinalControl = True
    ci.CP.flags = int(ci.CP.flags | HondaFlags.NIDEC_PCM_FIXED_CRUISE)
    assert not host.CP_SP.pcmCruiseSpeed  # False alone must not admit Fixed PCM.
  elif reason == "standstill":
    ci.CS.out.standstill = True
  else:
    ci.CS.out.buttonEvents = [structs.CarState.ButtonEvent(type="lkas", pressed=True)]
  host.run(ci.CS.out.as_reader(), cc.as_reader(), plan.as_reader(), True)
  assert host.state == controller.State.inactive and host.pre_active_timer == 0
  command = convert_host_command(host)
  assert command.intelligentCruiseButtonManagement.sendButton == "none"
  assert send_adapter(ci, cc, command, frame=6) == []
