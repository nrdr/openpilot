"""Check the paired Chestnut message migration without USB/GPU or device I/O."""
import ast
from pathlib import Path
import struct
from types import SimpleNamespace as NS

from openpilot.cereal import log
from openpilot.cereal.services import SERVICE_LIST

ROOT = Path(__file__).resolve().parents[3]


class UsbError(Exception):
  pass


def read_state(handle, gpu_state=None):
  path = ROOT / 'openpilot/system/hardware/chestnut/monitoring.py'
  node = next(node for node in ast.parse(path.read_text(encoding='utf-8')).body
              if isinstance(node, ast.FunctionDef) and node.name == 'read_chestnut_state')
  namespace = {'struct': struct, 'usb1': NS(USBError=UsbError),
               'messaging': NS(new_message=lambda service: log.Event.new_message(**{service: {}}))}
  exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), namespace)
  return namespace['read_chestnut_state'](handle, gpu_state)


def test_power_and_link_publish_without_gpu_model_context():
  handle = NS(controlRead=lambda request_type, request, *_args, **_kwargs:
              struct.pack('<Hh?', 12000, 1700, False) if request == 0xC0 else bytes([0x78]))
  msg = read_state(handle)
  assert msg.valid
  assert (msg.chestnutState.supplyVoltage, msg.chestnutState.supplyCurrent, msg.chestnutState.supplyFault) == (12000, 1700, False)
  assert msg.chestnutState.pcieLtssm == 0x78


def test_gpu_metrics_and_fresh_usb_measurements_are_combined_without_overwriting_each_other():
  gpu = log.ChestnutState.new_message(tempC=65., memoryTempC=70., gpuUsagePercent=85., powerDrawW=52.)
  gpu.supplyVoltage = 0
  handle = NS(controlRead=lambda request_type, request, *_args, **_kwargs:
              struct.pack('<Hh?', 12050, 1900, False) if request == 0xC0 else bytes([0x78]))
  msg = read_state(handle, gpu)
  assert msg.valid and msg.chestnutState.tempC == 65.
  assert msg.chestnutState.gpuUsagePercent == 85.
  assert msg.chestnutState.supplyVoltage == 12050
  assert gpu.supplyVoltage == 0  # no mutation of the GPU producer's message


def test_usb_failure_invalidates_combined_state_instead_of_publishing_stale_power_as_valid():
  def fail(*_args, **_kwargs):
    raise UsbError()
  assert not read_state(NS(controlRead=fail), log.ChestnutState.new_message(tempC=60.)).valid
  assert not read_state(NS(controlRead=lambda *_args, **_kwargs: b'')).valid


def test_separate_publishers_keep_both_services_but_only_one_owner_each():
  state = log.Event.new_message(chestnutGpuState={'gpuUsagePercent': 80.})
  assert state.which() == 'chestnutGpuState'
  assert SERVICE_LIST['chestnutGpuState'].frequency == SERVICE_LIST['chestnutState'].frequency == 10
  model_source = (ROOT / 'openpilot/selfdrive/modeld/modeld.py').read_text(encoding='utf-8')
  monitor_source = (ROOT / 'openpilot/system/hardware/chestnut/monitoring.py').read_text(encoding='utf-8')
  assert "self.pm.send('chestnutGpuState', msg)" in model_source
  assert "self.pm.send('chestnutState', msg)" not in model_source
  assert "pm.send('chestnutState', msg)" in monitor_source
  assert "SubMaster(['chestnutGpuState'])" in monitor_source
