import io
import unittest
from contextlib import redirect_stdout
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

from openpilot.nrdr.tools.eps.check_teg_dump import main


class TestTegDump(unittest.TestCase):
  def setUp(self):
    tmp = TemporaryDirectory()
    self.addCleanup(tmp.cleanup)
    self.flash, self.sram, self.second = (Path(tmp.name) / name for name in ("flash.bin", "sram.bin", "second.bin"))
    self.data = bytes(range(256)) * 1536
    self.flash.write_bytes(self.data)
    self.sram.write_bytes(bytes(range(256)) * 256)

  def check(self, *extra):
    with redirect_stdout(io.StringIO()) as out:
      rc = main([str(self.flash), str(self.sram), *map(str, extra)])
    return rc, out.getvalue()

  def test_sizes_and_hash(self):
    rc, out = self.check()
    self.assertEqual(rc, 0)
    self.assertIn(sha256(self.data).hexdigest(), out)
    self.assertIn(sha256(self.sram.read_bytes()).hexdigest(), out)

  def test_truncation_padding_and_wrong_profile(self):
    for n in (0, 393215, 393217, 524288):
      with self.subTest(n=n):
        self.flash.write_bytes(bytes(n))
        rc, out = self.check()
        self.assertNotEqual(rc, 0)
        self.assertIn("expected exactly 393,216", out)
    self.flash.write_bytes(self.data)
    self.sram.write_bytes(bytes(65535))
    self.assertIn("expected exactly 65,536", self.check()[1])

  def test_missing_and_uniform_files(self):
    self.sram.unlink()
    self.assertNotEqual(self.check()[0], 0)
    self.sram.write_bytes(bytes([255]) * 65536)
    self.assertIn("every byte", self.check()[1])

  def test_comparison(self):
    self.assertNotEqual(self.check("--compare-flash", self.flash)[0], 0)
    self.second.write_bytes(self.data)
    self.assertEqual(self.check("--compare-flash", self.second)[0], 0)
    self.second.write_bytes(b"z" + self.data[1:])
    self.assertNotEqual(self.check("--compare-flash", self.second)[0], 0)
