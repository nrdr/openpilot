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


ROOT = Path(__file__).resolve().parents[2]
CHECK_RWD_PATH = ROOT / "eps_tools" / "check_rwd.py"
RWD_DIR = ROOT / "eps_tools" / "rwd"
PILOT_IMAGES = {
  "39990-TG7-A060_STOCK.rwd": "f13d6b28e60ed5a39d2117c461c0c759a3d8b742b39ea9bfd6861ed7cc9fe184",
  "39990-TG7-A060_2X.rwd": "6ef205bceb5128f48e27182fa4e128173f2f6c0995192efd57809c237b81e40f",
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

  def test_restored_images_are_exact_and_valid(self):
    for name, expected_sha256 in PILOT_IMAGES.items():
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


if __name__ == "__main__":
  unittest.main()
