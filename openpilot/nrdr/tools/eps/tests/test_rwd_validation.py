import contextlib
import hashlib
import importlib.util
import io
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

from openpilot.nrdr.tools.eps import launcher
from openpilot.nrdr.tools.eps import flash

ROOT = Path(__file__).resolve().parents[5]
EPS_DIR = ROOT / "openpilot" / "nrdr" / "tools" / "eps"
CHECK_RWD_PATH = EPS_DIR / "check_rwd.py"
RWD_DIR = EPS_DIR / "rwd"
SHA256_MANIFEST = RWD_DIR / "SHA256SUMS"
EXPECTED_IMAGES = {
  "39990-TBA-C120-linear-max.rwd": "5605d97eb0218be32622b091557d2631efe4929bff37271d21ab45bae12e9fba",
  "39990-TBA-C120-stock.rwd": "273726b6bbcfc83b49a07be3a75bcffcaa9f87e8692277a918a9d8a89c18cd38",
  "39990-TG7-A060_2X.rwd": "6ef205bceb5128f48e27182fa4e128173f2f6c0995192efd57809c237b81e40f",
  "39990-TG7-A060_STOCK.rwd": "f13d6b28e60ed5a39d2117c461c0c759a3d8b742b39ea9bfd6861ed7cc9fe184",
  "39990-TLA-A040-linear-max.rwd": "042fe60ba415f9214d82196efc595f78aea2e54cf95f9b8f1e2216e6ca7268ad",
  "39990-TLA-A040-stock.rwd": "f84968c6b2b1fbba8b0d538b80a1782213186f92f2fc706be8eece485cb717d1",
  "39990-TRW-A020-06.18.2026-stable.rwd": "9e33b987627038f4211817d1a864cc892340c5ba47631f6808e9d5a00e2cff0f",
  "39990-TXM-A040-linear-max.rwd": "563e15e3895b7b6da4a036e98d7998bdfb272b871c4ccfa9e4c7cafe0755d828",
  "39990-TXM-A040-stock.rwd": "834a2fc06e625553994580b1b8fbfd627e0572f5d1f86123f36bc5055c545d4a",
  "Clarity-1663.rwd": "9e33b987627038f4211817d1a864cc892340c5ba47631f6808e9d5a00e2cff0f",
  "ClarityMax-20260719-1202-FFV1.rwd": "4cb41d2143fb43ea88acb868b39d5f960ac45deb3699200db3eadf3c1a94d3f5",
  "ClarityMax-20260719-1202-Smooth.rwd": "623ef3583b7cfd0235152e44d453ec601c109981734f503e737289d35832130c",
  "ClarityMax-20260722-1806-FF45-Tracker3200-Norm1650-3840.rwd": "d4fe903bcf347495f4321be65a3c650c8c931f1650c3bef6443721da0dd80f7d",
  "Clarity_PShapeSmooth_KFF45_R6Lead_R6L2_B6_NoSHLL2_CCP728_Telem6A3_TXFIX.rwd": "2d67ed146274fd5f7ff86c283cd17695a1cc833d28127c9f14135b3a460dd783",
  "Clarity_R6L2_B6_FFV1P_KFF8_NoSHLL2_CCP728_Telem6A3_TXFIX.rwd": "15593081c6b6d6bcccc5ce0a2e7adb5c69ff86dd0c1daaada97095684de921f4",
}

spec = importlib.util.spec_from_file_location("check_rwd", CHECK_RWD_PATH)
assert spec is not None and spec.loader is not None
check_rwd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_rwd)


def block_offset(data):
  idx = 3
  for _ in range(6):
    count = data[idx]
    idx += 1
    for _ in range(count):
      length = data[idx]
      idx += length + 1
  return idx


def repair_file_checksum(data):
  struct.pack_into("<I", data, len(data) - 4, sum(data[:-4]) & 0xffffffff)


class TestPilotRwdValidation(unittest.TestCase):
  def check_quietly(self, path):
    with contextlib.redirect_stdout(io.StringIO()):
      return check_rwd.check(path)

  def test_every_image_is_manifested_exact_and_valid(self):
    manifest = {
      name: digest
      for digest, name in (line.split(maxsplit=1) for line in SHA256_MANIFEST.read_text().splitlines() if line.strip())
    }
    self.assertEqual(manifest, EXPECTED_IMAGES)
    self.assertEqual({path.name for path in RWD_DIR.glob("*.rwd")}, set(EXPECTED_IMAGES))

    for name, expected_sha256 in EXPECTED_IMAGES.items():
      with self.subTest(name=name):
        path = RWD_DIR / name
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected_sha256)
        self.assertTrue(self.check_quietly(path))

  def test_payload_corruption_fails_and_cli_exits_nonzero(self):
    data = bytearray((RWD_DIR / "39990-TG7-A060_STOCK.rwd").read_bytes())
    data[block_offset(data) + 8 + 0x100] ^= 1
    repair_file_checksum(data)

    with tempfile.TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / "corrupt.rwd"
      path.write_bytes(data)
      self.assertFalse(self.check_quietly(path))
      env = os.environ.copy()
      env["PYTHONUTF8"] = "1"
      result = subprocess.run([sys.executable, str(CHECK_RWD_PATH), str(path)],
                              env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
      self.assertNotEqual(result.returncode, 0)

  def test_wrong_flash_start_fails_with_valid_file_checksum(self):
    data = bytearray((RWD_DIR / "39990-TG7-A060_STOCK.rwd").read_bytes())
    struct.pack_into(">I", data, block_offset(data), 0x20000)
    repair_file_checksum(data)

    with tempfile.TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / "wrong-start.rwd"
      path.write_bytes(data)
      self.assertFalse(self.check_quietly(path))

  def test_launcher_maps_historical_rwd_aliases(self):
    expected = str(RWD_DIR / "39990-TG7-A060_STOCK.rwd")
    self.assertEqual(launcher.normalized_arguments("check_rwd.py", ["rwd/39990-TG7-A060_STOCK.rwd"]), [expected])
    self.assertEqual(launcher.normalized_arguments("eps-update.py", ["eps_tools/rwd/39990-TG7-A060_STOCK.rwd"]), [expected])
    self.assertEqual(launcher.normalized_arguments("flash.py", ["--bus", "1"]), ["--bus", "1"])

  def test_guided_flasher_keeps_danger_explicit(self):
    dry_run = flash.run_eps_update("rwd/example.rwd", 1, skip_checksum=False, danger=False)
    real_flash = flash.run_eps_update("rwd/example.rwd", 1, skip_checksum=False, danger=True)
    self.assertNotIn("--danger", dry_run)
    self.assertEqual(real_flash.count("--danger"), 1)
    self.assertIn(str(EPS_DIR / "eps-update.py"), dry_run)
    self.assertIn(str(ROOT), flash.subprocess_env()["PYTHONPATH"].split(os.pathsep))

  def test_root_and_historical_check_commands_resolve_canonical_image(self):
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    commands = (
      ([sys.executable, str(ROOT / "check_rwd.py"), "rwd/39990-TG7-A060_STOCK.rwd"], ROOT),
      ([sys.executable, "check_rwd.py", "rwd/39990-TG7-A060_STOCK.rwd"], ROOT / "eps_tools"),
    )
    for command, cwd in commands:
      with self.subTest(command=command, cwd=cwd):
        result = subprocess.run(command, cwd=cwd, env=environment, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ALL GOOD", result.stdout)

  def test_legacy_eps_directory_contains_launchers_only(self):
    legacy = ROOT / "eps_tools"
    self.assertFalse((legacy / "rwd").exists())
    self.assertFalse((legacy / "rwd_format").exists())
    self.assertEqual(
      {path.name for path in legacy.iterdir() if path.name != "__pycache__"},
      {"README.md", "_bootstrap.py", "check_rwd.py", "eps-diag.py", "eps-update.py", "flash.py"},
    )

  def test_root_guided_command_finds_every_canonical_image_before_quit(self):
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    result = subprocess.run(
      [sys.executable, str(ROOT / "flash.py")],
      cwd=ROOT,
      env=environment,
      input="q\n",
      capture_output=True,
      text=True,
      timeout=60,
      check=False,
    )
    output = result.stdout + result.stderr
    self.assertNotEqual(result.returncode, 0)
    self.assertIn("Aborted", output)
    for name in EXPECTED_IMAGES:
      with self.subTest(name=name):
        self.assertIn(name, output)

  def test_eps_bundle_and_launchers_ship_in_release(self):
    output = subprocess.check_output([sys.executable, "tools/release/release_files.py"], cwd=ROOT)
    released = {os.fsdecode(path) for path in output.split(b"\0") if path}
    expected = {
      path.relative_to(ROOT).as_posix()
      for path in EPS_DIR.rglob("*")
      if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }
    expected.update(("flash.py", "eps-update.py", "eps-diag.py", "check_rwd.py"))
    expected.update(
      f"eps_tools/{name}"
      for name in ("README.md", "_bootstrap.py", "check_rwd.py", "eps-diag.py", "eps-update.py", "flash.py")
    )
    self.assertEqual(expected - released, set())


if __name__ == "__main__":
  unittest.main()
