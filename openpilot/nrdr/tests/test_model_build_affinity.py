"""Exercise SConscript command assembly without SCons, native modules, or a GPU."""

import ast
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import shlex
from types import SimpleNamespace
import unittest

from openpilot.common.file_chunker import get_chunk_targets


REPO_ROOT = Path(__file__).resolve().parents[3]
SCONSCRIPT = REPO_ROOT / "openpilot/selfdrive/modeld/SConscript"
MODEL_DIR = "/repo/openpilot/selfdrive/modeld"


class WithoutImports(ast.NodeTransformer):
  def visit_Import(self, node):
    return None

  def visit_ImportFrom(self, node):
    return None


class BuildFile:
  def __init__(self, path):
    path = str(path)
    self.abspath = str(PurePosixPath("/repo", path[1:]) if path.startswith("#") else PurePosixPath(MODEL_DIR, path))
    self.relpath = self.abspath.removeprefix("/repo/")

  def File(self, path):
    return BuildFile(str(PurePosixPath(self.abspath, path)))

  def __str__(self):
    return self.abspath


@dataclass
class BuildAction:
  function: object
  display: str


class BuildEnvironment:
  def __init__(self):
    self.commands = []
    self.side_effects = []
    self.executed = []
    self.chunk_estimates = {}

  def Clone(self):
    return self

  def Dir(self, path):
    return BuildFile(path)

  def Command(self, targets, sources, actions):
    node = SimpleNamespace(targets=targets, sources=sources, actions=actions)
    self.commands.append(node)
    return node

  def SideEffect(self, lock, node):
    self.side_effects.append((str(lock), node))

  def Execute(self, command):
    self.executed.append(command)
    return 0


def assemble_build(arch, chestnut=False, device="mici", skip=False, all_cameras=None, onnx_size=100):
  # Run production control flow and f-strings, but replace imports and all I/O.
  # This checks build wiring, not QCOM execution or on-device model correctness.
  tree = WithoutImports().visit(ast.parse(SCONSCRIPT.read_text(encoding="utf-8")))
  env = BuildEnvironment()
  chunked = []
  def record_chunk_targets(path, size):
    env.chunk_estimates[path] = size
    return [path + ".manifest", path + ".000"]
  environment = {"SKIP_TINYGRAD_COMPILE": "1" if skip else None, "PREBUILT_ALL_CAMERAS": all_cameras}
  namespace = {
    "arch": arch,
    "env": env,
    "Import": lambda *args: None,
    "File": BuildFile,
    "Dir": BuildFile,
    "Action": BuildAction,
    "Value": lambda value: value,
    "glob": SimpleNamespace(glob=lambda *args, **kwargs: ["tinygrad_repo/tinygrad/engine/jit.py"]),
    "os": SimpleNamespace(
      getenv=environment.get,
      path=SimpleNamespace(
        isfile=lambda path: True,
        join=lambda *parts: str(PurePosixPath(*parts)),
        getsize=lambda path: onnx_size,
        expanduser=lambda path: "/home/test",
      ),
    ),
    "HARDWARE": SimpleNamespace(get_device_type=lambda: device),
    "_ar_ox_fisheye": SimpleNamespace(width=1928, height=1208),
    "_os_fisheye": SimpleNamespace(width=1344, height=760),
    "MEDMODEL_INPUT_SIZE": (512, 256),
    "DM_INPUT_SIZE": (1440, 960),
    "ModelConstants": SimpleNamespace(MODEL_RUN_FREQ=20, MODEL_CONTEXT_FREQ=10),
    "TG_INPUT_DEVICES_PATH": f"{MODEL_DIR}/models/tg_input_devices.json",
    "chestnut_present": lambda: chestnut,
    "modeld_pkl_path": lambda big: f"{MODEL_DIR}/models/{'big_' if big else ''}driving_tinygrad.pkl",
    "get_existing_chunks": lambda path: [path + ".000"],
    "get_chunk_targets": record_chunk_targets,
    "chunk_file": lambda path, chunks: chunked.append((path, chunks)),
    "link_up": lambda: True,
  }
  exec(compile(tree, str(SCONSCRIPT), "exec"), namespace)
  driving = [node for node in env.commands if isinstance(node.targets, list) and "driving_tinygrad.pkl" in node.targets[0]]
  return env, driving, chunked


class TestModelBuildAffinity(unittest.TestCase):
  def test_driving_compiler_inherits_affinity_and_keeps_backend_arguments(self):
    cases = (
      ("comma_arm64", False, "mici", ["1344x760"]),
      ("comma_arm64", True, "mici", ["1344x760"]),
      ("comma_arm64", False, "tici", ["1928x1208"]),
      ("x86_64", False, "pc", ["1928x1208", "1344x760"]),
      ("Darwin", False, "pc", ["1928x1208", "1344x760"]),
    )
    for arch, chestnut, device, resolutions in cases:
      with self.subTest(arch=arch, chestnut=chestnut, device=device):
        env, nodes, chunked = assemble_build(arch, chestnut, device)
        self.assertEqual(len(nodes), 2 if chestnut else 1)
        for big, node in enumerate(nodes):
          prefix = "big_" if big else ""
          pkl = f"{MODEL_DIR}/models/{prefix}driving_tinygrad.pkl"
          onnx = f"{MODEL_DIR}/models/{prefix}driving_supercombo.onnx"
          if big:
            self.assertIsInstance(node.actions, BuildAction)
            self.assertIsNone(node.actions.function([], [], env))
            command = env.executed[-1]
            self.assertIn((f"{MODEL_DIR}/models/.chestnut.lock", node), env.side_effects)
          else:
            command, chunk_action = node.actions
            self.assertIsInstance(chunk_action, BuildAction)
            chunk_action.function([], [], env)
          words = shlex.split(command)
          # Environment assignments must be followed directly by python3, never
          # a taskset wrapper that rejects an offline or disallowed CPU.
          executable = next(index for index, word in enumerate(words) if "=" not in word)
          self.assertEqual(words[executable:], [
            "python3", f"{MODEL_DIR}/compile_modeld.py",
            "--model-size", "512x256", "--camera-resolutions", *resolutions,
            "--onnx", onnx, "--output", pkl, "--frame-skip", "2",
          ])
          flags = dict(word.split("=", 1) for word in words[:executable])
          expected = ({
            "DEBUG": "1", "DEV": "USB+AMD:LLVM", "FRAME_DEV": "CPU", "FLOAT16": "1",
            "JIT_BATCH_SIZE": "0", "GMMU": "0", "TC_OPT": "2", "TC_OCCUPANCY_OPT": "1",
          } if big else {
            "DEV": "QCOM", "IMAGE": "1", "FLOAT16": "1", "NOLOCALS": "1", "JIT_BATCH_SIZE": "0", "OPENPILOT_HACKS": "1",
          } if arch == "comma_arm64" else {"DEV": "CPU", "HOME": "/home/test"} if arch == "Darwin" else {"DEV": "CPU:LLVM"})
          self.assertEqual(flags, expected)
          self.assertEqual(chunked[-1], (pkl, node.targets))
          self.assertEqual(node.targets, [pkl + ".manifest", pkl + ".000"])
          dependencies = [str(source) for source in node.sources]
          self.assertIn(onnx + ".000", dependencies)
          self.assertIn(f"{MODEL_DIR}/compile_modeld.py", dependencies)
          self.assertIn("#tinygrad_repo/tinygrad/engine/jit.py", dependencies)
          self.assertIn("/repo/openpilot/common/file_chunker.py", dependencies)

  def test_prebuilt_camera_coverage_and_normal_device_selection(self):
    for device in ("mici", "tici", "tizi"):
      for chestnut in (False, True):
        for all_cameras in (None, "0", "true", "1"):
          with self.subTest(device=device, chestnut=chestnut, all_cameras=all_cameras):
            env, driving, _ = assemble_build("comma_arm64", chestnut, device, all_cameras=all_cameras)
            resolutions = (["1928x1208", "1344x760"] if all_cameras == "1" else
                           ["1344x760"] if device == "mici" else ["1928x1208"])
            self.assertEqual(len(driving), 2 if chestnut else 1)
            for node in driving:
              if isinstance(node.actions, BuildAction):
                node.actions.function([], [], env)
                command = env.executed[-1]
              else:
                command = node.actions[0]
              words = shlex.split(command)
              self.assertEqual(words[words.index("--camera-resolutions") + 1:words.index("--onnx")], resolutions)
              self.assertIn(" ".join(resolutions), node.sources)

            warps = [node for node in env.commands if isinstance(node.targets, str) and "/dm_warp_" in node.targets]
            self.assertEqual([node.targets for node in warps], [
              f"{MODEL_DIR}/models/dm_warp_{resolution}_tinygrad.pkl" for resolution in resolutions
            ])
            for resolution, node in zip(resolutions, warps, strict=True):
              words = shlex.split(node.actions)
              executable = words.index("python3")
              self.assertEqual(words[executable:], [
                "python3", f"{MODEL_DIR}/compile_dm_warp.py",
                "--camera-resolution", resolution, "--warp-to", "1440x960", "--output", node.targets,
              ])
              self.assertIn("DEV=QCOM", words[:executable])

  def test_skip_tinygrad_compile_still_skips_driving_model(self):
    for chestnut in (False, True):
      with self.subTest(chestnut=chestnut):
        _, nodes, chunked = assemble_build("comma_arm64", chestnut, skip=True)
        self.assertEqual(nodes, [])
        self.assertEqual(chunked, [])

  def test_chunk_budget_covers_every_driving_camera_without_inflating_dm(self):
    onnx_size = 50 * 1024 * 1024
    single_camera_budget = 2 * onnx_size + 10 * 1024 * 1024
    for chestnut in (False, True):
      for arch, flag, count in (("comma_arm64", None, 1), ("comma_arm64", "1", 2), ("x86_64", None, 2)):
        with self.subTest(arch=arch, chestnut=chestnut, all_cameras=flag):
          env, driving, _ = assemble_build(arch, chestnut, all_cameras=flag, onnx_size=onnx_size)
          for node in driving:
            pkl = node.targets[0].removesuffix(".manifest")
            budget = env.chunk_estimates[pkl]
            self.assertEqual(budget, count * single_camera_budget)
            reserved = len(get_chunk_targets(pkl, budget)) - 1
            if count == 2:
              # The first real dual-camera C4 build produced 176.36 MB; the
              # previous single-camera estimate reserved only three chunks.
              needed = len(get_chunk_targets(pkl, 176_360_000)) - 1
              self.assertGreaterEqual(reserved, needed)
            else:
              self.assertEqual(reserved, 3)
          dm = f"{MODEL_DIR}/models/dmonitoring_model_tinygrad.pkl"
          self.assertEqual(env.chunk_estimates[dm], single_camera_budget)


if __name__ == "__main__":
  unittest.main()
