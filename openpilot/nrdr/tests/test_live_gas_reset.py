"""Exercise the one-shot command with isolated Params, Panda telemetry and learner metadata."""
import ast
import base64
import gzip
import json
from pathlib import Path
import runpy
import sys
from types import SimpleNamespace as NS

import pytest

from openpilot.nrdr.car import live_gas_reset as reset
from openpilot.nrdr.car.mvl_state import MVL_STATE_KEYS, MvlStateStore
from openpilot.nrdr.params.specs import PARAM_SPECS_BY_KEY, ParamFlag


ROOT = Path(__file__).resolve().parents[3]
HONDA = NS(carFingerprint="HONDA_CIVIC", brand="honda")
KEEP = {"HondaLiveLearningGas": False, "LongPidTuneScaleStandard": 120, "CalibrationParams": b"untouched",
        **{value: 2.5 for value in MVL_STATE_KEYS.values() if value not in reset.GAS_KEYS}}


class TestParams(dict):
  __test__ = False

  def put(self, key, value, *, block):
    assert block
    self[key] = value

  put_bool = put
  get_raw = dict.get

  def get_bool(self, key):
    return bool(self.get(key))

  def remove(self, key):
    self.pop(key, None)


class Streams(dict):
  fresh = True

  def all_checks(self, services):
    assert set(services) == {"deviceState", "pandaStates"}
    return self.fresh


@pytest.fixture
def parked(tmp_path):
  params = TestParams(IsOffroad=True, **dict.fromkeys(reset.GAS_KEYS, 1.2), **KEEP)
  meta = tmp_path / "honda_learner_meta.json"
  meta.write_text(json.dumps({"car_fingerprint": HONDA.carFingerprint, "learn_version": 1}))
  panda = NS(pandaType="redPanda", safetyModel="noOutput", ignitionLine=False, ignitionCan=False, controlsAllowed=False)
  sm = Streams(deviceState=NS(started=False), pandaStates=[panda], carParams=HONDA)
  return params, sm, NS(proc=None), meta


@pytest.fixture
def rpc(parked, monkeypatch):
  # Like the other device-free nrdr tests, load production entry points without
  # importing the network daemon, initializing native Params or opening sockets.
  path = ROOT / "openpilot/sunnypilot/sunnylink/athena/sunnylinkd.py"
  ns = {"params": parked[0], "gzip": gzip, "base64": base64, "HONDA_TUNING_WRITE_KEYS": set(),
        "cloudlog": NS(warning=lambda *_: None)}
  nodes = []
  for node in ast.parse(path.read_text(encoding="utf-8")).body:
    if isinstance(node, ast.FunctionDef) and node.name in ("_remote_bool_value", "saveParams"):
      node.decorator_list = []
      nodes.append(node)
    if isinstance(node, ast.Assign) and ast.unparse(node.targets[0]) == "BLOCKED_PARAMS":
      nodes.append(node)
  exec(compile(ast.Module(nodes, []), str(path), "exec"), ns)
  monkeypatch.setattr(reset, "stored_cp", lambda p: HONDA)
  return ns["saveParams"]


def drive_manager(parked):
  params, sm, card, meta = parked
  reset.consume_reset(params, sm, card, read_cp=lambda p: HONDA, meta_path=meta, bosch_a_path=meta.parent / "bosch_a.json")


@pytest.mark.parametrize("compressed", (False, True))
def test_sunnylink_request_and_device_ack(parked, rpc, compressed):
  params, _, _, meta = parked
  raw = gzip.compress(b"true") if compressed else b"true"
  rpc({reset.REQUEST: base64.b64encode(raw).decode()}, compressed)
  assert params[reset.REQUEST] is True and params[reset.STATUS] == "Requested: HONDA_CIVIC"
  assert meta.exists() and all(params[key] == 1.2 for key in reset.GAS_KEYS)
  rpc({reset.REQUEST: "MA=="})  # Echoed false cannot acknowledge the command.
  rpc({reset.STATUS: "ZmFrZQ=="})  # Remote client cannot forge the result.
  assert params[reset.REQUEST] is True and params[reset.STATUS] == "Requested: HONDA_CIVIC"
  bosch_a = meta.parent / "bosch_a.json"
  bosch_a.write_text('{"gas_factor": 1.2}')  # Bosch-A learner state is a separate file and is cleared by the same reset
  drive_manager(parked)
  assert not bosch_a.exists()
  assert not meta.exists() and not (set(params) & set(reset.GAS_KEYS))
  assert {key: params[key] for key in KEEP} == KEEP
  assert params[reset.REQUEST] is False and params[reset.STATUS] == "Reset complete."
  store = MvlStateStore(params, start_worker=False)
  assert store.load("gas_factor_00", 1.0) == 1.0 and store.load("gas_alpha_low", 0.0) == 0.0
  assert store.load("wind_factor", 1.0) == 1.0 and store.load("speed_factor", 1.0) == 2.5
  params["HondaGasFactorParams"] = 1.3
  drive_manager(parked)
  assert params["HondaGasFactorParams"] == 1.3  # No replay next tick.


@pytest.mark.parametrize("reason", ("started", "road", "line", "can", "controls", "output", "missing", "unknown", "stale",
                                    "card", "selection", "live_cp", "other_metadata", "unbound"))
def test_unsafe_requests_are_rejected_not_deferred(parked, reason):
  params, sm, card, meta = parked
  reset.request_reset(params, HONDA)
  p = sm["pandaStates"][0]
  if reason == "started":
    sm["deviceState"].started = True
  elif reason == "road":
    params["IsOffroad"] = False
  elif reason == "line":
    p.ignitionLine = True
  elif reason == "can":
    p.ignitionCan = True
  elif reason == "controls":
    p.controlsAllowed = True
  elif reason == "output":
    p.safetyModel = "hondaNidec"
  elif reason == "missing":
    sm["pandaStates"].clear()
  elif reason == "unknown":
    p.pandaType = "unknown"
  elif reason == "stale":
    sm.fresh = False
  elif reason == "card":
    card.proc = object()
  elif reason == "selection":
    params["CarPlatformBundle"] = {"platform": "HONDA_CLARITY", "brand": "honda"}
  elif reason == "live_cp":
    sm["carParams"] = NS(carFingerprint="HONDA_CLARITY", brand="honda")
  elif reason == "other_metadata":
    meta.write_text('{"car_fingerprint":"HONDA_CLARITY"}')
  elif reason == "unbound":
    del params[reset.STATUS]
  drive_manager(parked)
  assert meta.is_file() and all(params[key] == 1.2 for key in reset.GAS_KEYS)
  assert params[reset.REQUEST] is False and params[reset.STATUS].startswith("Not reset")


def test_no_opt_in_no_writes_and_no_backup_restore(parked):
  params, _, _, meta = parked
  before = dict(params)
  drive_manager(parked)
  assert dict(params) == before and meta.is_file()
  assert set(reset.GAS_KEYS) == {f"HondaGas{kind}{band}Params" for kind in ("Factor", "Alpha")
                                 for band in ("", "Low", "00", "10", "20", "30")} | {"HondaWindFactorParams"}
  for key in (reset.REQUEST, reset.STATUS):
    assert PARAM_SPECS_BY_KEY[key].flags == (ParamFlag.CLEAR_ON_MANAGER_START,)


@pytest.mark.parametrize("payload", ({reset.REQUEST: "bm9wZQ=="}, {reset.REQUEST: "%%"}, {reset.REQUEST: "MQ==", "HondaLiveLearningGas": "MA=="}))
def test_invalid_or_batched_rpc_cannot_request(parked, rpc, payload):
  before = dict(parked[0])
  with pytest.raises(ValueError):
    rpc(payload)
  assert dict(parked[0]) == before


@pytest.mark.parametrize("cp", (None, NS(brand="toyota", carFingerprint="TOYOTA_CAMRY"), NS(brand="honda", carFingerprint="")))
def test_unknown_or_unsupported_vehicle_rejected(parked, cp):
  with pytest.raises(ValueError):
    reset.request_reset(parked[0], cp)
  assert reset.REQUEST not in parked[0]


def test_readback_failure_is_not_acknowledged_as_success(parked, monkeypatch):
  params, _, _, _ = parked
  reset.request_reset(params, HONDA)
  monkeypatch.setattr(params, "remove", lambda k: None)
  drive_manager(parked)
  assert params[reset.STATUS].startswith("Reset incomplete") and params[reset.REQUEST] is False


def test_onroad_rpc_cannot_queue_a_later_reset(parked, rpc):
  params, _, _, meta = parked
  params["IsOffroad"] = False
  with pytest.raises(ValueError):
    rpc({reset.REQUEST: "MQ=="})
  params["IsOffroad"] = True
  drive_manager(parked)
  assert reset.REQUEST not in params and meta.is_file()


def test_generated_sunnylink_control_is_honda_only_offroad_and_confirmed():
  data = json.loads((ROOT / "openpilot/sunnypilot/sunnylink/settings_ui.json").read_text(encoding="utf-8"))
  steering = next(p for p in data["panels"] if p["id"] == "steering")
  nrdr = next(s for s in steering["sections"] if s["id"] == "nrdr")
  items = next(p for p in nrdr["sub_panels"] if p["id"] == "nrdr_longitudinal")["items"]
  action, = [i for i in items if i.get("key") == reset.REQUEST]
  status, = [i for i in items if i.get("key") == reset.STATUS]
  assert action["widget"] == "toggle" and action["requires_attestation"] is True
  assert action["visibility"] == [{"type": "capability", "field": "nrdr_honda_tuning_available", "equals": True}]
  assert status["widget"] == "info" and status["visibility"] == action["visibility"]
  assert {"type": "offroad_only"} in action["enablement"]


def test_native_confirmations_do_not_write_until_confirmed_and_still_parked(parked, monkeypatch):
  params, _, _, _ = parked
  ui = NS(params=params, CP=HONDA, ignition=False, is_offroad=lambda: params.get_bool("IsOffroad"))
  dialogs = []
  def create_widget(*args, **kwargs):
    return NS(args=args, **kwargs)

  class MiciConfirmation:
    def __init__(self, title, action, icon, callback, **kwargs):
      self.confirm = callback
      self.value = ""

    def set_enabled(self, enabled):
      self.enabled = enabled

    def _update_state(self):
      pass

    def get_value(self):
      return self.value

    def set_value(self, value):
      self.value = value

  for module, shim in {
    "openpilot.selfdrive.ui.ui_state": NS(ui_state=ui),
    "openpilot.system.ui.lib.application": NS(gui_app=NS(push_widget=dialogs.append, texture=lambda *_: None)),
    "openpilot.system.ui.lib.multilang": NS(tr=str),
    "openpilot.system.ui.sunnypilot.widgets.list_view": NS(button_item_sp=create_widget),
    "openpilot.system.ui.widgets": NS(DialogResult=NS(CONFIRM=1, CANCEL=0)),
    "openpilot.system.ui.widgets.confirm_dialog": NS(ConfirmDialog=create_widget),
    "openpilot.selfdrive.ui.mici.layouts.settings.device": NS(EngagedConfirmationButton=MiciConfirmation),
  }.items():
    monkeypatch.setitem(sys.modules, module, shim)
  adapter = runpy.run_path(str(ROOT / "openpilot/nrdr/ui/settings/live_gas_reset.py"))
  large = adapter["large_reset_button"]()
  mici = adapter["mici_reset_button"]()
  large.callback()
  dialogs[0].callback(0)  # cancelled
  ui.ignition = True
  dialogs[0].callback(1)  # ignition changed with the dialog open
  mici.confirm()  # stale C4 slide confirmation
  assert reset.REQUEST not in params and not mici.enabled()
  ui.ignition = False
  assert mici.enabled() and large.enabled()
  mici.confirm()
  assert params[reset.REQUEST] is True
  mici._update_state()
  assert mici.value == "requested" and not large.enabled()
  drive_manager(parked)
  mici._update_state()
  assert mici.value == "complete" and large.enabled()
  large.callback()
  dialogs[-1].callback(1)
  assert params[reset.REQUEST] is True
