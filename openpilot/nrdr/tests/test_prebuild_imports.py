import os
from pathlib import Path
import subprocess
import sys
import unittest


class TestPrebuildImports(unittest.TestCase):
  def test_catalog_import_does_not_require_runtime_params_dependencies(self):
    repository_root = Path(__file__).resolve().parents[3]
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(filter(None, (str(repository_root), environment.get("PYTHONPATH"))))
    script = """
import sys
sys.modules["openpilot.common.params"] = None
sys.modules["pyray"] = None
sys.modules["zmq"] = None
from openpilot.nrdr.params import NRDR_UI_METADATA, NrdrParamKey
from openpilot.nrdr.params.specs import PARAM_SPECS
from openpilot.nrdr.features.lateral.model_policy import SteerRatioModelPolicy, classify_steer_ratio_model
from openpilot.nrdr.features.lateral.phase_detector import phase_with_latch
from openpilot.nrdr.features.lateral.steer_ratio_tuning import LaneChangeSteerRatioFade
from openpilot.nrdr.tools.sr_correction_analysis import CommandSample
from openpilot.nrdr.ui.native_param_controls import get_native_option_spec
from openpilot.nrdr.ui.sunnylink_schema import sunnylink_fields_for_key
from openpilot.sunnypilot.nrdr.sr_correction_analysis import CommandSample as LegacyCommandSample
from openpilot.sunnypilot.nrdr.model_policy import classify_steer_ratio_model as legacy_classify_steer_ratio_model
from openpilot.sunnypilot.nrdr.phase_detector import phase_with_latch as legacy_phase_with_latch
from openpilot.sunnypilot.nrdr.steer_ratio_tuning import LaneChangeSteerRatioFade as LegacyLaneChangeSteerRatioFade
assert PARAM_SPECS
assert len(NRDR_UI_METADATA) == 6
assert NrdrParamKey.HONDA_BOSCH_A_RADAR == "HondaBoschARadar"
assert LegacyCommandSample is CommandSample
assert legacy_classify_steer_ratio_model is classify_steer_ratio_model
assert legacy_phase_with_latch is phase_with_latch
assert LegacyLaneChangeSteerRatioFade is LaneChangeSteerRatioFade
assert classify_steer_ratio_model(None) is SteerRatioModelPolicy.UNKNOWN
assert get_native_option_spec("LatPScaleLowSpeed").format_label(100) == "100%"
assert sunnylink_fields_for_key("LatPScaleLowSpeed")["max"] == 500
assert "openpilot.nrdr.params.store" not in sys.modules
assert "openpilot.system.ui.lib.multilang" not in sys.modules
assert "openpilot.system.ui.sunnypilot.widgets.list_view" not in sys.modules
"""
    subprocess.run([sys.executable, "-c", script], cwd=repository_root, env=environment, check=True)
