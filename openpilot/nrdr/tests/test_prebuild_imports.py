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
import openpilot.nrdr.car
import openpilot.nrdr.features.driver_policy as driver_policy
from openpilot.nrdr.features.lateral.steer_ratio_tuning import SteerRatioMode
assert "openpilot.nrdr.features.lateral.model_policy" not in sys.modules
from openpilot.nrdr.features.lateral.model_policy import SteerRatioModelPolicy, classify_steer_ratio_model
from openpilot.nrdr.features.lateral.phase_detector import phase_with_latch
import openpilot.nrdr.features.longitudinal as longitudinal
import openpilot.nrdr.features.radar as radar
import openpilot.nrdr.hooks as hooks
import openpilot.nrdr.tools.lateral as lateral_tools
import openpilot.nrdr.tools.radar_re as radar_re_tools
import openpilot.nrdr.tools.steer_ratio as steer_ratio_tools
from openpilot.nrdr.tools.sr_correction_analysis import CommandSample
import openpilot.nrdr.ui as nrdr_ui
from openpilot.nrdr.ui.native_param_controls import get_native_option_spec
import openpilot.nrdr.ui.settings
from openpilot.nrdr.ui.sunnylink_schema import sunnylink_fields_for_key
from openpilot.sunnypilot.nrdr.sr_correction_analysis import CommandSample as LegacyCommandSample
from openpilot.sunnypilot.nrdr.model_policy import classify_steer_ratio_model as legacy_classify_steer_ratio_model
from openpilot.sunnypilot.nrdr.phase_detector import phase_with_latch as legacy_phase_with_latch
from openpilot.sunnypilot.nrdr.steer_ratio_tuning import SteerRatioMode as LegacySteerRatioMode
assert PARAM_SPECS
assert set(driver_policy.__all__) == set(driver_policy._EXPORT_MODULES)
assert set(longitudinal.__all__) == set(longitudinal._EXPORT_MODULES)
assert set(radar.__all__) == set(radar._EXPORT_MODULES)
assert set(hooks.__all__) == set(hooks._EXPORT_MODULES)
assert set(nrdr_ui.__all__) == set(nrdr_ui._EXPORT_MODULES)
assert lateral_tools.__doc__
assert radar_re_tools.BOSCH_RADAR_HDR_MSGS
assert steer_ratio_tools.__doc__
assert len(NRDR_UI_METADATA) == 10
assert NrdrParamKey.HONDA_BOSCH_A_RADAR == "HondaBoschARadar"
assert LegacyCommandSample is CommandSample
assert legacy_classify_steer_ratio_model is classify_steer_ratio_model
assert legacy_phase_with_latch is phase_with_latch
assert LegacySteerRatioMode is SteerRatioMode
assert classify_steer_ratio_model(None) is SteerRatioModelPolicy.UNKNOWN
assert get_native_option_spec("LatPScaleLowSpeed").format_label(100) == "100%"
assert sunnylink_fields_for_key("LatPScaleLowSpeed")["max"] == 500
assert "openpilot.nrdr.params.store" not in sys.modules
assert "openpilot.nrdr.car.opendbc" not in sys.modules
assert "openpilot.nrdr.features.driver_policy.speed_limit_assist" not in sys.modules
assert "openpilot.nrdr.features.driver_policy.lane_change" not in sys.modules
assert "openpilot.nrdr.features.driver_policy.mads" not in sys.modules
assert "openpilot.nrdr.features.longitudinal.longcontrol" not in sys.modules
assert "openpilot.nrdr.features.radar.radar" not in sys.modules
assert "openpilot.nrdr.hooks.controlsd" not in sys.modules
assert "openpilot.nrdr.hooks.events" not in sys.modules
assert "openpilot.nrdr.hooks.selfdrived" not in sys.modules
assert "openpilot.nrdr.tools.lateral.attribution" not in sys.modules
assert "openpilot.nrdr.tools.lateral.tune_report" not in sys.modules
assert "openpilot.nrdr.tools.radar_re.cli" not in sys.modules
assert "openpilot.nrdr.tools.steer_ratio.correction" not in sys.modules
assert "openpilot.system.ui.lib.multilang" not in sys.modules
assert "openpilot.system.ui.sunnypilot.widgets.list_view" not in sys.modules
assert "openpilot.nrdr.ui.settings.layout" not in sys.modules
assert "openpilot.nrdr.ui.settings_policy" not in sys.modules
"""
    subprocess.run([sys.executable, "-c", script], cwd=repository_root, env=environment, check=True)
