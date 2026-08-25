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
sys.modules["zmq"] = None
from openpilot.nrdr.params import NrdrParamKey
from openpilot.nrdr.params.specs import PARAM_SPECS
assert PARAM_SPECS
assert NrdrParamKey.HONDA_BOSCH_A_RADAR == "HondaBoschARadar"
assert "openpilot.nrdr.params.store" not in sys.modules
"""
    subprocess.run([sys.executable, "-c", script], cwd=repository_root, env=environment, check=True)
