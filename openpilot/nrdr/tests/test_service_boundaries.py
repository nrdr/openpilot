import ast
import os
from pathlib import Path
import subprocess
import sys
import unittest


CANONICAL_CONSUMERS = {
  "openpilot/system/hardware/hardwared.py": "from openpilot.nrdr.features.services.hardware import",
  "openpilot/system/athena/athenad.py": "from openpilot.nrdr.features.services import athena as nrdr_athena",
  "openpilot/system/athena/registration.py": "from openpilot.nrdr.features.services import registration as nrdr_registration",
  "openpilot/system/manager/process_config.py": '"openpilot.system.manager.nrdr_remoted"',
  "openpilot/system/manager/nrdr_remoted.py": "from openpilot.nrdr.features.services.car_tune_report import CarTuneReporter",
  "openpilot/sunnypilot/sunnylink/api.py": "from openpilot.nrdr.features.services.sunnylink import",
  "openpilot/sunnypilot/sunnylink/athena/sunnylinkd.py": "from openpilot.nrdr.features.services.sunnylink import",
  "openpilot/sunnypilot/sunnylink/tools/generate_settings_schema.py": "from openpilot.nrdr.features.services.sunnylink import",
  "openpilot/sunnypilot/models/manager.py": "from openpilot.nrdr.features.services.model_manager import",
}

LEGACY_SERVICE_MODULES = (
  "athena",
  "athena_streamer",
  "car_tune_report",
  "hardware",
  "model_manager",
  "registration",
  "remote_actions",
  "remoted",
  "ssh_key_refresh",
  "sunnylink",
)


class TestServiceBoundaries(unittest.TestCase):
  @property
  def repository_root(self) -> Path:
    return Path(__file__).resolve().parents[3]

  def test_legacy_service_shims_import_and_preserve_export_identity(self):
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(filter(None, (str(self.repository_root), environment.get("PYTHONPATH"))))
    script = r'''
import importlib
import sys
import types


def install_module(name, package=False, **members):
  module = types.ModuleType(name)
  if package:
    module.__path__ = []
  module.__dict__.update(members)
  sys.modules[name] = module
  return module


class DummyParams:
  pass


class DummyPaths:
  pass


class UnknownKeyName(Exception):
  pass


dummy_type = type("RuntimeDependency", (), {})
cloudlog = types.SimpleNamespace()
install_module("opendbc", package=True)
install_module("opendbc.car", package=True)
install_module("opendbc.car.structs", car=types.SimpleNamespace(CarParams=dummy_type))
install_module("opendbc.car.car_helpers", interfaces={})
install_module("aiortc", RTCPeerConnection=dummy_type, RTCConfiguration=dummy_type, RTCIceServer=dummy_type,
               RTCSessionDescription=dummy_type, RTCRtpCodecCapability=dummy_type)
install_module("aiortc.sdp", candidate_from_sdp=lambda value: value)
install_module("requests", get=lambda *args, **kwargs: None)
install_module("openpilot.common.api", package=True, Api=dummy_type, api_get=lambda *args, **kwargs: None)
install_module("openpilot.common.api.comma_connect", API_HOST="https://athena.konik.ai")
install_module("openpilot.common.basedir", BASEDIR="/data/openpilot")
install_module("openpilot.common.hardware", package=True, HARDWARE=types.SimpleNamespace(), PC=True)
install_module("openpilot.common.hardware.hw", Paths=DummyPaths)
install_module("openpilot.common.params", Params=DummyParams, UnknownKeyName=UnknownKeyName)
install_module("openpilot.common.swaglog", cloudlog=cloudlog)
install_module("openpilot.common.version", sunnylink_consent_version="1", terms_version="1", terms_version_sp="1", training_version="1")
install_module("openpilot.cereal", package=True, custom=types.SimpleNamespace(), messaging=types.SimpleNamespace())
install_module("openpilot.nrdr.params", apply_handcrafted_lateral_profile=lambda *args: None,
               get_handcrafted_lateral_profile=lambda *args: None, get_steer_ratio_endpoint_profile=lambda *args: None,
               is_handcrafted_lateral_enabled=lambda *args: False)
install_module("openpilot.nrdr.features.lateral", package=True)
install_module("openpilot.nrdr.features.lateral.model_policy", SteerRatioModelResolution=dummy_type,
               SteerRatioModelPolicy=types.SimpleNamespace(LEGACY_DUAL_BP=object(), PURE_FIRMWARE_VGR=object()),
               resolve_steer_ratio_model=lambda *args: None)
install_module("openpilot.nrdr.features.lateral.honda_vgr", get_honda_vgr_profile=lambda *args: None)
install_module("openpilot.sunnypilot.models.helpers", get_active_bundle=lambda *args: None)
install_module("openpilot.system.webrtc.device", package=True)
install_module("openpilot.system.webrtc.device.video", LiveStreamVideoStreamTrack=dummy_type)

service_modules = ("athena", "athena_streamer", "car_tune_report", "hardware", "model_manager", "registration",
                   "remote_actions", "ssh_key_refresh", "sunnylink")
for module_name in service_modules:
  canonical = importlib.import_module(f"openpilot.nrdr.features.services.{module_name}")
  legacy = importlib.import_module(f"openpilot.sunnypilot.nrdr.{module_name}")
  assert legacy.__all__ == canonical.__all__
  for name in canonical.__all__:
    assert getattr(legacy, name) is getattr(canonical, name), (module_name, name)

entrypoint = importlib.import_module("openpilot.system.manager.nrdr_remoted")
service = importlib.import_module("openpilot.nrdr.features.services.remoted")
legacy = importlib.import_module("openpilot.sunnypilot.nrdr.remoted")
assert legacy.main is entrypoint.main
assert set(legacy.__all__) == {*service.__all__, "main"}
for name in service.__all__:
  assert getattr(legacy, name) is getattr(service, name), name
'''
    subprocess.run([sys.executable, "-c", script], cwd=self.repository_root, env=environment, check=True)

  def test_service_implementations_do_not_import_the_legacy_namespace(self):
    services_dir = self.repository_root / "openpilot" / "nrdr" / "features" / "services"
    for path in services_dir.glob("*.py"):
      with self.subTest(path=path.name):
        source = path.read_text(encoding="utf-8")
        self.assertNotIn("openpilot.sunnypilot.nrdr", source)

  def test_service_exports_cover_module_defined_public_objects(self):
    services_dir = self.repository_root / "openpilot" / "nrdr" / "features" / "services"
    for path in services_dir.glob("*.py"):
      if path.name == "__init__.py":
        continue
      with self.subTest(path=path.name):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.name)
        public_names: set[str] = set()
        exports: set[str] = set()
        for node in tree.body:
          if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            public_names.add(node.name)
          elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else (node.target,)
            for target in targets:
              if isinstance(target, ast.Name) and not target.id.startswith("_"):
                public_names.add(target.id)
              if isinstance(target, ast.Name) and target.id == "__all__":
                value = node.value
                exports = set(ast.literal_eval(value))
        self.assertLessEqual(public_names, exports)

  def test_legacy_service_files_are_explicit_shims(self):
    legacy_dir = self.repository_root / "openpilot" / "sunnypilot" / "nrdr"
    for module_name in LEGACY_SERVICE_MODULES:
      with self.subTest(module=module_name):
        path = legacy_dir / f"{module_name}.py"
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.name)
        definitions = [node.name for node in tree.body if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))]
        assigned_names = {
          target.id
          for node in tree.body if isinstance(node, ast.Assign)
          for target in node.targets if isinstance(target, ast.Name)
        }
        self.assertEqual(definitions, [])
        self.assertIn("__all__", assigned_names)

  def test_framework_consumers_use_canonical_service_paths(self):
    forbidden = (
      "openpilot.sunnypilot.nrdr.athena",
      "openpilot.sunnypilot.nrdr.car_tune_report",
      "openpilot.sunnypilot.nrdr.hardware",
      "openpilot.sunnypilot.nrdr.model_manager",
      "openpilot.sunnypilot.nrdr.registration",
      "openpilot.sunnypilot.nrdr.remoted",
      "openpilot.sunnypilot.nrdr.sunnylink",
    )
    for relative_path, expected in CANONICAL_CONSUMERS.items():
      with self.subTest(path=relative_path):
        source = (self.repository_root / relative_path).read_text(encoding="utf-8")
        self.assertIn(expected, source)
        self.assertFalse(any(old_path in source for old_path in forbidden))

  def test_remoted_entrypoint_is_only_a_process_adapter(self):
    entrypoint_path = self.repository_root / "openpilot" / "system" / "manager" / "nrdr_remoted.py"
    tree = ast.parse(entrypoint_path.read_text(encoding="utf-8"), filename=entrypoint_path.name)
    functions = [node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]

    self.assertEqual(functions, ["main"])
    self.assertIn(
      "from openpilot.nrdr.features.services.remoted import _park, _validate_params, run",
      entrypoint_path.read_text(encoding="utf-8"),
    )

  def test_remoted_service_preserves_startup_and_poll_order(self):
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(filter(None, (str(self.repository_root), environment.get("PYTHONPATH"))))
    script = r'''
import sys
import types

events = []
swaglog = types.ModuleType("openpilot.common.swaglog")
swaglog.cloudlog = types.SimpleNamespace(info=lambda *args: None, exception=lambda *args: None)
sys.modules["openpilot.common.swaglog"] = swaglog
basedir = types.ModuleType("openpilot.common.basedir")
basedir.BASEDIR = "/data/openpilot"
sys.modules["openpilot.common.basedir"] = basedir
requests = types.ModuleType("requests")
requests.get = lambda *args, **kwargs: None
sys.modules["requests"] = requests

from openpilot.nrdr.features.services import remoted


class StopLoop(Exception):
  pass


class Params:
  def get_bool(self, key):
    return False


class Actions:
  def __init__(self, params):
    events.append("actions")

  def set_status(self, status):
    events.append(f"status:{status}")


class Reporter:
  def __init__(self, params):
    events.append("reporter")

  def publish(self):
    events.append("publish")


remoted.RemoteActions = Actions
remoted.refresh_github_ssh_keys = lambda params, logger: events.append("refresh") or False
remoted.time.monotonic = lambda: 0.0


def stop_after_first_poll(interval):
  events.append(f"sleep:{interval}")
  raise StopLoop


remoted.time.sleep = stop_after_first_poll
try:
  remoted.run(Params(), Reporter)
except StopLoop:
  pass

assert events == ["actions", "reporter", "status:idle", "refresh", "publish", "sleep:2.0"], events
'''
    subprocess.run([sys.executable, "-c", script], cwd=self.repository_root, env=environment, check=True)


if __name__ == "__main__":
  unittest.main()
