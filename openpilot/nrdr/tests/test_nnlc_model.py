"""NNLC is retired: stale settings must not re-enable a model/controller."""
import ast
import json
from pathlib import Path
from openpilot.nrdr.params.snapshots import CONTROL_GROUPS
from openpilot.nrdr.params.tuning_policy import tuning_write_allowed

ROOT = Path(__file__).resolve().parents[3]


def test_nnlc_has_no_runtime_modules_or_controller_selection():
  for relative in ("openpilot/nrdr/features/lateral/nnlc.py", "openpilot/nrdr/features/lateral/nnlc_model.py",
                   "openpilot/nrdr/features/lateral/latcontrol_clarity_hybrid.py",
                   "openpilot/sunnypilot/selfdrive/controls/lib/nnlc/nnlc.py"):
    assert not (ROOT / relative).exists()
  for relative in ("openpilot/sunnypilot/selfdrive/car/interfaces.py", "openpilot/sunnypilot/selfdrive/controls/controlsd_ext.py"):
    source = (ROOT / relative).read_text(encoding="utf-8")
    assert "nnlc" not in source.lower()
    ast.parse(source)


def test_nnlc_keys_not_polled_or_writable():
  assert not any("Nnlc" in key for group in CONTROL_GROUPS for key in group.keys)
  for key in ("NeuralNetworkLateralControl", "NrdrNnlcEnabled", "NrdrNnlcKpGain"):
    assert not tuning_write_allowed({}, key)


def test_nnlc_absent_from_remote_ui():
  schema = json.loads((ROOT / "openpilot/sunnypilot/sunnylink/settings_ui.json").read_text())
  assert "NeuralNetworkLateralControl" not in json.dumps(schema)
  assert "NrdrNnlc" not in json.dumps(schema)
