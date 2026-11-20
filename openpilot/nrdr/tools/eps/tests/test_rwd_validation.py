import ast
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
import types
import unittest
from unittest import mock

from openpilot.nrdr.tools.eps import flash
from openpilot.nrdr.tools.eps import launcher
from openpilot.nrdr.tools.eps.rwd_format.x5a import x5a

ROOT = Path(__file__).resolve().parents[5]
EPS_DIR = ROOT / "openpilot" / "nrdr" / "tools" / "eps"
CHECK_RWD_PATH = EPS_DIR / "check_rwd.py"
EPS_UPDATE_PATH = EPS_DIR / "eps-update.py"
RWD_DIR = EPS_DIR / "rwd"
SHA256_MANIFEST = RWD_DIR / "SHA256SUMS"

EXPECTED_ASSETS = {
  "39990-T6Z-A110/39990-T6Z-A110.rwd": "7fac5c25732761f60cb123ba8ea34d010486f3e7bea1859f9c2d42ff53af4f9d",
  "39990-TBA-A030/Legacy and Stock/39990-TBA,A030-linear-max.rwd": "835b99414d4927bac327996ac6771a8f2dcd3633baac1933b2ed2d091a568fb9",
  "39990-TBA-A030/Legacy and Stock/mod-39990-TBA,A030.rwd": "b023258dd774729cfcca3f0d3f6b9fefe1bc111f8b4d1b6bb0e83d788cbfec6f",
  "39990-TBA-A030/Legacy and Stock/stock-39990-TBA-A030.rwd": "50aa2a555b44ac80149cd5528290a6ac9b3452d6d127a03a6c9f9cf6758c9226",
  "39990-TBA-A030/Proper Torque Mod/39990-TBA,A030-PTM.rwd": "55c37266229594f4353e1b8a644ac55903975b7693645fa0f8e65bfc5d969c15",
  "39990-TBA-C020 (2019 Honda Civic Sport)/Legacy and Stock/2.5x-mod-39990-TBA,C020.rwd": "077d2dda35d43bf17c631837c28c980fa0b274de7a151efff0b75439ed87bc6b",
  "39990-TBA-C020 (2019 Honda Civic Sport)/Legacy and Stock/39990-TBA-C020-linear-max-V2.1-Linear45-FlatGain.rwd": "b112945d28b0f3031bcf5f35c9a3609f9153110edd0dd6342c7e5a1a48b4576e",
  "39990-TBA-C020 (2019 Honda Civic Sport)/Legacy and Stock/39990-TBA-C020-max.rwd": "7a5ddf7fb20724647d7b251b48d43dd60ab351eae96e099d31644bec60ac90bf",
  "39990-TBA-C020 (2019 Honda Civic Sport)/Legacy and Stock/stock-39990-TBA-C020.rwd": "ad30cbd9faade0e2011f97229632c6c43e9c08e72aa5160f0a282c79843e9367",
  "39990-TBA-C020 (2019 Honda Civic Sport)/Proper Torque Mod/39990-TBA,C020-PTM.rwd": "df67bf6fa515f29cf12eafd493823d72c5359f50df13c3d5d066bd4aa35e7f25",
  "39990-TBA-C020 (2019 Honda Civic Sport)/Proper Torque Mod/39990-TBA,C020-Trk4000-PTM.rwd": "2d8836e81a53d5e1cb44fb7645ab81336481b2676361805d8de07a199347b33d",
  "39990-TBA-C120/Legacy and Stock/mod-39990-TBA,C120.rwd": "ac9c0fd6e57ad5fb118122863ae86d5aba40f88d8edd786dbfa82653a96f3dcd",
  "39990-TBA-C120/Legacy and Stock/stock-39990-TBA-C120.rwd": "273726b6bbcfc83b49a07be3a75bcffcaa9f87e8692277a918a9d8a89c18cd38",
  "39990-TBA-C120/Proper Torque Mod/39990-TBA,C120-PTM.rwd": "15e63414b3137a9c6906305bbfe90c207b48083f2b173207a8084ff7312002e3",
  "39990-TEG-A010/Legacy and Stock/39990-TEG-A010-linear-max.rwd": "4ebf643a99eda27c68ec162c639627a43aa07c3ce5924a9fd8910c13d2022040",
  "39990-TEG-A010/Proper Torque Mod/39990-TEG,A010-PTM.rwd": "80fbd0e023453553719dc7363923a5d036d05f025f705809b4f0603e664cf8b2",
  "39990-TG7-A040 (2016 Honda Pilot)/Legacy and Stock/39990-TG7-A040-STOCK.rwd": "64ac87f422f3f15879eaffdcd1b9387f0c7820a42141c0b2e2baebf939c82bbb",
  "39990-TG7-A060 (2019 Honda Pilot)/Legacy and Stock/39990-TG7-A060-STOCK.bin": "d28c27b573ef610a479875107002ac7d9a84689ba5f3660686d0aecf1afb7555",
  "39990-TG7-A060 (2019 Honda Pilot)/Legacy and Stock/39990-TG7-A060-STOCK.rwd": "f13d6b28e60ed5a39d2117c461c0c759a3d8b742b39ea9bfd6861ed7cc9fe184",
  "39990-TG7-A060 (2019 Honda Pilot)/Work in Progress/39990-TG7-A060-2X (2019 Honda Pilot)": "6ef205bceb5128f48e27182fa4e128173f2f6c0995192efd57809c237b81e40f",
  "39990-TGG-A020/Legacy and Stock/mod-39990-TGG,A020-HatchbackSport.rwd": "3a8cdf57ad75306e74d387d399306aa355628f2101c4589f9c7c1721901e235c",
  "39990-TGG-A020/Legacy and Stock/stock-39990-TGG-A020-HatchbackSport.rwd": "9b43471586cd39e31e7d932d31684b5c4bee056bc4de53d638bb3b02ee9ad73d",
  "39990-TGG-A120/39990-TGG-A120-08072026-4250.rwd": "470559fa7e02d11b8531fb83fcac19ca609a451dc3bd931ff5810343d9f4e8b4",
  "39990-TGG-A120/Proper Torque Mod/39990-TGG,A120-PTM-20261016b.rwd": "6640806da8a56d7156363bb8fc9adc440374d9c0489598e0604e906a5e56f762",
  "39990-TGG-A120/mod-39990-TGG,A120.rwd": "357b2571cd65c2100c07b33b1326101f9ce8ea9790aaa67358df69f98c089fc7",
  "39990-TGG-A120/stock-39990-TGG-A120.rwd": "3780431a47003e13d3654bf767697c73b52c9fa0be9a2d96cf1e5f6fba6c73b6",
  "39990-THR-A020 (Honda Odyssey)/Legacy and Stock/stock_39990-THR-A020.rwd": "09604ecb9132666261bb966a8cefc5f8b7f7ec628fcd350a652cbcf947abfa14",
  "39990-TJB-A220 (Acura RDX)/Legacy and Stock/39990-TJB-A220 (Stock I-HDS File).rwd": "d951de3c64d0b4be0c72edc8c0a7fb65c0650f28c0d20b13d4ce012817a60691",
  "39990-TJB-A220 (Acura RDX)/Legacy and Stock/39990-TJB-A220-Stock.rwd": "7895cace5ef2317cf72579b082de7c3ee93ba30ff86e1346a5b574800f806a4a",
  "39990-TJB-A220 (Acura RDX)/Proper Torque Mod/39990-TJB-A220-PTM-Keys.rwd": "68a6fdb43e0b1f11cbf02d1fe03146f0771a1bcdf6bc622a06c53d0f3ae1f4bc",
  "39990-TLA-A040 - (Honda_CRV_5G)/Legacy and Stock/39990-TLA-A040-linear-max.rwd": "042fe60ba415f9214d82196efc595f78aea2e54cf95f9b8f1e2216e6ca7268ad",
  "39990-TLA-A040 - (Honda_CRV_5G)/Legacy and Stock/39990-TLA-A040-stock.bin": "0ceab577022d7504562c9cbb9fe882b7995283c072baeffee54e78e18d5f3740",
  "39990-TLA-A040 - (Honda_CRV_5G)/Legacy and Stock/39990-TLA-A040-stock.rwd": "f84968c6b2b1fbba8b0d538b80a1782213186f92f2fc706be8eece485cb717d1",
  "39990-TLA-A040 - (Honda_CRV_5G)/Legacy and Stock/39990-TLA-A040_tq30000_a9000_44256c0b.rwd": "ac6dce68bc3c36e7fa990170f7f56df678f9edd92617fd62cdf74a3e7274bc42",
  "39990-TLA-A040 - (Honda_CRV_5G)/Proper Torque Mod/39990-TLA-A040_Clarity_FF_tune_telemety_8cf8e537.rwd": "26f5390b654ace80b759bd20156d4c8ef834d97dc0e22889c2d247c052980afb",
  "39990-TLA-A220 (2021 Honda CR-V)/Legacy and Stock/39990-TLA-A220-stock.rwd": "70d38d2e72a82da472786a9f429d5469740db57a49b66831bf2dee9a485d6517",
  "39990-TLA-A220 (2021 Honda CR-V)/Proper Torque Mod/39990-TLA,A220-PTM-20261016b.rwd": "2c99299725fa34ad65a7f5d25a7f32659f5fb97d173fd2789e2428aea8959227",
  "39990-TRW-A020 (Honda Clarity)/Legacy and Stock/39990-TRW-A020 (stock).rwd": "d08a7f5c18ea6af9aaa1b366828fef226bb4ce192dc89a3d79d9c2661e1a7673",
  "39990-TRW-A020 (Honda Clarity)/Proper Torque Mod/39990+TRW+A020-AnglePTM-20261119-09.rwd": "6fef0b9cd2a51e42b681befeba1a0d996b97618df2bbf52a4e3bafaca7b96d99",
  "39990-TRW-A020 (Honda Clarity)/Proper Torque Mod/ClarityMax-PTM-Latest-092826.rwd": "9e2e98857a6734f4631205cb9550bf7cb61720da566a4c117b9187a8ddf25d61",
  "39990-TRW-A020 (Honda Clarity)/Proper Torque Mod/ClarityMax-PTM.rwd": "d4fe903bcf347495f4321be65a3c650c8c931f1650c3bef6443721da0dd80f7d",
  "39990-TVA-A160 (Honda Accord)/39990-TVA,A160-V37-2xTorque.rwd": "8a809d1b320957e4846c9145ee662858759d514681ce46c247a4a197784202da",
  "39990-TVA-A160 (Honda Accord)/Proper Torque Mod/39990-TVA,A160-V300-PTM.rwd": "42f562c069d39c877b66067fe56c6437c43b1609c48ffec8a83dc7303b8e7603",
  "39990-TVA-A160 (Honda Accord)/Proper Torque Mod/39990-TVA,A160-V37A-PTM-lite.rwd": "af57a2365a1781d58410039ed6acd7303d61989253be6f13bb44ce859c040ee8",
  "39990-TVA-A160 (Honda Accord)/Stock/39990-TVA-A160-V9B-Stock.rwd": "7ad6d49d4a97b661693423bc5ad9f1a754e7f80523010491e9097708294dcfea",
  "39990-TVA-A340 (2021 Honda Accord)/Proper Torque Mod/39990-TVA,A340-V300-PTM.rwd": "2819a6f2d197327684e9a8831a938664588e567247c17f2efabec77d5ad49917",
  "39990-TVA-A340 (2021 Honda Accord)/Proper Torque Mod/39990-TVA,A340-V37A-PTM-lite.rwd": "e7728d58a12958a69a2f8441b83d5cf918f31ba0d3f5548ae5e0725f8b6fd2e6",
  "39990-TVA-A340 (2021 Honda Accord)/Stock/39990-TVA-A340-STOCK.rwd": "0965a24c77293eb4e4d42c988764640285a762ac0072ee5922bc47234d64bb21",
  "39990-TXM-A040 (2019-2022 Honda Insight)/Legacy and Stock/39990-TXM-A040 Bin/user.bin": "ccc59bb576114ae6ee906281bdc6041e425fb3fb1a320d4e7816bee96b599782",
  "39990-TXM-A040 (2019-2022 Honda Insight)/Legacy and Stock/TXM-A040-2.5x-spike.rwd": "ad7457d97dd165fc6426ad9f7948b7eac652dbbcf5e3490a7e401f25e773a59e",
  "39990-TXM-A040 (2019-2022 Honda Insight)/Legacy and Stock/TXM-A040-2x-linear.rwd": "02cf82ca9992f18796a64484cf0fe5470d77a09bd5fc5cd1a098dc61a5c3d2fb",
  "39990-TXM-A040 (2019-2022 Honda Insight)/Legacy and Stock/TXM-A040-STOCK.rwd": "834a2fc06e625553994580b1b8fbfd627e0572f5d1f86123f36bc5055c545d4a",
  "39990-TXM-A040 (2019-2022 Honda Insight)/Legacy and Stock/TXM-A040-linear-max.rwd": "563e15e3895b7b6da4a036e98d7998bdfb272b871c4ccfa9e4c7cafe0755d828",
  "39990-TXM-A040 (2019-2022 Honda Insight)/Proper Torque Mod/39990-TXM,A040-PTM.rwd": "833a41bf9c3a8b4051c37271e0f7e1b970532e58b143d7882729203fa399b6e8",
}

GUIDED_IMAGES = {
  "39990-TBA-A030/Legacy and Stock/stock-39990-TBA-A030.rwd",
  "39990-TBA-A030/Proper Torque Mod/39990-TBA,A030-PTM.rwd",
  "39990-TBA-C020 (2019 Honda Civic Sport)/Legacy and Stock/stock-39990-TBA-C020.rwd",
  "39990-TBA-C020 (2019 Honda Civic Sport)/Proper Torque Mod/39990-TBA,C020-PTM.rwd",
  "39990-TBA-C120/Legacy and Stock/stock-39990-TBA-C120.rwd",
  "39990-TBA-C120/Proper Torque Mod/39990-TBA,C120-PTM.rwd",
  "39990-TEG-A010/Proper Torque Mod/39990-TEG,A010-PTM.rwd",
  "39990-TG7-A060 (2019 Honda Pilot)/Legacy and Stock/39990-TG7-A060-STOCK.rwd",
  "39990-TGG-A020/Legacy and Stock/stock-39990-TGG-A020-HatchbackSport.rwd",
  "39990-TGG-A120/Proper Torque Mod/39990-TGG,A120-PTM-20261016b.rwd",
  "39990-TGG-A120/stock-39990-TGG-A120.rwd",
  "39990-THR-A020 (Honda Odyssey)/Legacy and Stock/stock_39990-THR-A020.rwd",
  "39990-TJB-A220 (Acura RDX)/Legacy and Stock/39990-TJB-A220 (Stock I-HDS File).rwd",
  "39990-TJB-A220 (Acura RDX)/Legacy and Stock/39990-TJB-A220-Stock.rwd",
  "39990-TJB-A220 (Acura RDX)/Proper Torque Mod/39990-TJB-A220-PTM-Keys.rwd",
  "39990-TLA-A040 - (Honda_CRV_5G)/Legacy and Stock/39990-TLA-A040-stock.rwd",
  "39990-TLA-A040 - (Honda_CRV_5G)/Proper Torque Mod/39990-TLA-A040_Clarity_FF_tune_telemety_8cf8e537.rwd",
  "39990-TLA-A220 (2021 Honda CR-V)/Legacy and Stock/39990-TLA-A220-stock.rwd",
  "39990-TLA-A220 (2021 Honda CR-V)/Proper Torque Mod/39990-TLA,A220-PTM-20261016b.rwd",
  "39990-TRW-A020 (Honda Clarity)/Legacy and Stock/39990-TRW-A020 (stock).rwd",
  "39990-TRW-A020 (Honda Clarity)/Proper Torque Mod/39990+TRW+A020-AnglePTM-20261119-09.rwd",
  "39990-TRW-A020 (Honda Clarity)/Proper Torque Mod/ClarityMax-PTM-Latest-092826.rwd",
  "39990-TXM-A040 (2019-2022 Honda Insight)/Legacy and Stock/TXM-A040-STOCK.rwd",
  "39990-TXM-A040 (2019-2022 Honda Insight)/Proper Torque Mod/39990-TXM,A040-PTM.rwd",
}

T6Z_IMAGE = "39990-T6Z-A110/39990-T6Z-A110.rwd"
X31_IMAGES = {
  "39990-TVA-A160 (Honda Accord)/39990-TVA,A160-V37-2xTorque.rwd",
  "39990-TVA-A160 (Honda Accord)/Proper Torque Mod/39990-TVA,A160-V300-PTM.rwd",
  "39990-TVA-A160 (Honda Accord)/Proper Torque Mod/39990-TVA,A160-V37A-PTM-lite.rwd",
  "39990-TVA-A160 (Honda Accord)/Stock/39990-TVA-A160-V9B-Stock.rwd",
  "39990-TVA-A340 (2021 Honda Accord)/Proper Torque Mod/39990-TVA,A340-V300-PTM.rwd",
  "39990-TVA-A340 (2021 Honda Accord)/Proper Torque Mod/39990-TVA,A340-V37A-PTM-lite.rwd",
  "39990-TVA-A340 (2021 Honda Accord)/Stock/39990-TVA-A340-STOCK.rwd",
}
WIP_IMAGE = "39990-TG7-A060 (2019 Honda Pilot)/Work in Progress/39990-TG7-A060-2X (2019 Honda Pilot)"
RAW_IMAGES = {
  "39990-TG7-A060 (2019 Honda Pilot)/Legacy and Stock/39990-TG7-A060-STOCK.bin",
  "39990-TLA-A040 - (Honda_CRV_5G)/Legacy and Stock/39990-TLA-A040-stock.bin",
  "39990-TXM-A040 (2019-2022 Honda Insight)/Legacy and Stock/39990-TXM-A040 Bin/user.bin",
}
RWD_IMAGES = {name for name in EXPECTED_ASSETS if name.endswith(".rwd")}
X5A_RWD_IMAGES = RWD_IMAGES - X31_IMAGES
X5A_CONTAINERS = X5A_RWD_IMAGES | {WIP_IMAGE}
OUTER_CHECKSUM_IMAGES = RWD_IMAGES | {WIP_IMAGE}

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


def header_value_offset(data, wanted_header, wanted_value):
  idx = 3
  for header_index in range(6):
    count = data[idx]
    idx += 1
    for value_index in range(count):
      length = data[idx]
      idx += 1
      if (header_index, value_index) == (wanted_header, wanted_value):
        return idx
      idx += length
  raise ValueError(f"No header value {wanted_header}:{wanted_value}")


def repair_file_checksum(data):
  struct.pack_into("<I", data, len(data) - 4, sum(data[:-4]) & 0xffffffff)


def load_eps_update_with_dependency_stubs():
  """Load the flasher's validation function without Panda/device dependencies."""
  fake_tqdm = types.ModuleType("tqdm")
  fake_tqdm.tqdm = lambda iterable, **_kwargs: iterable

  fake_opendbc = types.ModuleType("opendbc")
  fake_opendbc.__path__ = []
  fake_car = types.ModuleType("opendbc.car")
  fake_car.__path__ = []
  fake_structs = types.ModuleType("opendbc.car.structs")
  fake_structs.CarParams = type("CarParams", (), {})
  fake_uds = types.ModuleType("opendbc.car.uds")
  fake_uds.UdsClient = type("UdsClient", (), {})
  for name in (
      "SESSION_TYPE", "ACCESS_TYPE", "ROUTINE_CONTROL_TYPE",
      "ROUTINE_IDENTIFIER_TYPE", "DATA_IDENTIFIER_TYPE", "RESET_TYPE",
  ):
    setattr(fake_uds, name, types.SimpleNamespace())
  fake_uds.NegativeResponseError = type("NegativeResponseError", (Exception,), {})
  fake_panda = types.ModuleType("panda")
  fake_panda.Panda = type("Panda", (), {})
  fake_opendbc.car = fake_car
  fake_car.structs = fake_structs
  fake_car.uds = fake_uds

  stubs = {
    "tqdm": fake_tqdm,
    "opendbc": fake_opendbc,
    "opendbc.car": fake_car,
    "opendbc.car.structs": fake_structs,
    "opendbc.car.uds": fake_uds,
    "panda": fake_panda,
  }
  module_spec = importlib.util.spec_from_file_location("eps_update_offline_test", EPS_UPDATE_PATH)
  assert module_spec is not None and module_spec.loader is not None
  module = importlib.util.module_from_spec(module_spec)
  with mock.patch.dict(sys.modules, stubs):
    module_spec.loader.exec_module(module)
  return module


class TestCuratedRwdLibrary(unittest.TestCase):
  def check_quietly(self, path):
    with contextlib.redirect_stdout(io.StringIO()):
      return check_rwd.check(path)

  def test_exact_drive_audited_asset_paths_hashes_and_manifest(self):
    self.assertEqual(len(EXPECTED_ASSETS), 54)
    manifest = {}
    for line in SHA256_MANIFEST.read_text().splitlines():
      if not line.strip():
        continue
      digest, name = line.split(maxsplit=1)
      self.assertNotIn(name, manifest)
      manifest[name] = digest
    self.assertEqual(manifest, EXPECTED_ASSETS)

    actual = {
      path.relative_to(RWD_DIR).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
      for path in RWD_DIR.rglob("*")
      if path.is_file() and path.name not in {"README.md", "SHA256SUMS", "SOURCES.md"}
    }
    self.assertEqual(actual, EXPECTED_ASSETS)

  def test_all_rwd_containers_have_valid_outer_checksums(self):
    self.assertEqual(len(OUTER_CHECKSUM_IMAGES), 51)
    for name in OUTER_CHECKSUM_IMAGES:
      with self.subTest(name=name):
        raw = (RWD_DIR / name).read_bytes()
        self.assertGreaterEqual(len(raw), 4)
        self.assertEqual(struct.unpack("<I", raw[-4:])[0], sum(raw[:-4]) & 0xffffffff)

  def test_all_x5a_containers_pass_full_offline_validation(self):
    self.assertEqual(len(X5A_CONTAINERS), 44)
    for name in X5A_CONTAINERS:
      with self.subTest(name=name):
        self.assertTrue(self.check_quietly(RWD_DIR / name))

  def test_guided_menu_matches_current_drive_images(self):
    self.assertEqual(len(GUIDED_IMAGES), 24)
    self.assertEqual(sum("/Proper Torque Mod/" in name for name in GUIDED_IMAGES), 11)
    self.assertEqual(sum("stock" in Path(name).name.lower() for name in GUIDED_IMAGES), 13)
    self.assertEqual(set(flash.GUIDED_FLASH_FILES), GUIDED_IMAGES)
    self.assertEqual(
      {Path(path).relative_to(RWD_DIR).as_posix() for path in flash.find_images()},
      GUIDED_IMAGES,
    )

  def test_angle_build_is_a_separate_clarity_choice_with_its_own_supported_ids(self):
    rows = {flash.image_display_name(path): flash.rwd_supported_versions(path) for path in flash.find_images()}
    angle = "39990-TRW-A020 (Honda Clarity)/Proper Torque Mod/39990+TRW+A020-AnglePTM-20261119-09.rwd"
    stock = "39990-TRW-A020 (Honda Clarity)/Legacy and Stock/39990-TRW-A020 (stock).rwd"
    torque = "39990-TRW-A020 (Honda Clarity)/Proper Torque Mod/ClarityMax-PTM-Latest-092826.rwd"
    for eps_id, expected in (("39990-TRW-A020", {stock, torque, angle}), ("39990-TRW,A020", {stock, torque, angle}),
                             ("39990+TRW+A020", {angle})):
      self.assertEqual({path for path, ids in rows.items() if flash.norm_fw(eps_id) in ids}, expected)

  def test_every_guided_image_passes_updater_checks_and_seed_lookup(self):
    updater = load_eps_update_with_dependency_stubs()
    for name in GUIDED_IMAGES:
      with self.subTest(name=name), contextlib.redirect_stdout(io.StringIO()):
        path = RWD_DIR / name
        self.assertTrue(flash.validate(path))
        firmware = x5a(path.read_bytes())
        updater.validate_fw(firmware)
        self.assertEqual(updater.get_can_address(firmware), 0x18da30f1)
        for app_id in firmware.file_headers[3].values:
          self.assertEqual(len(updater.get_seed_secret(firmware, app_id.value)), 6)

  def test_rom_crc_and_shadow_corruption_fail_even_with_repaired_checksums(self):
    self.assertEqual(check_rwd.crc32_bzip2(b"123456789"), 0xfc891918)
    images = [name for name in GUIDED_IMAGES if name.startswith(("39990-THR", "39990-TJB"))]
    updater = load_eps_update_with_dependency_stubs()
    encrypt = {value: key for key, value in check_rwd.DECRYPT_LOOKUP.items()}
    for name in images:
      original = (RWD_DIR / name).read_bytes()
      fw = x5a(original)
      start = fw.firmware_blocks[0]["start"]
      for defect in ("ROM CRC failed", "monitor shadow stale"):
        with self.subTest(name=name, defect=defect):
          plain = bytearray(check_rwd.DECRYPT_LOOKUP[b] for b in fw.firmware_encrypted[0])
          address = check_rwd.ROM_CRC_REGIONS[0][2] if defect == "ROM CRC failed" else check_rwd.SHADOW_FIELDS[0][1]
          plain[address - start] ^= 1
          if defect == "monitor shadow stale":
            for lo, hi, slot in check_rwd.ROM_CRC_REGIONS:
              struct.pack_into("!I", plain, slot - start, check_rwd.crc32_bzip2(plain[lo - start:hi - start]))
          for negative, offset, _ in check_rwd.checksum_definitions(len(plain)):
            total = sum(struct.unpack(f"!{offset // 2}H", plain[:offset]))
            struct.pack_into("!H", plain, offset, (-total if negative else total) & 0xffff)
          damaged = bytearray(original)
          offset = block_offset(damaged) + 8
          damaged[offset:offset + len(plain)] = bytes(encrypt[b] for b in plain)
          repair_file_checksum(damaged)
          with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(ValueError, defect):
              updater.validate_fw(x5a(damaged))

  def test_unknown_lengths_and_wrong_eps_addresses_fail_closed(self):
    name = "39990-TBA-A030/Proper Torque Mod/39990-TBA,A030-PTM.rwd"
    original = (RWD_DIR / name).read_bytes()
    updater = load_eps_update_with_dependency_stubs()
    wrong_address = bytearray(original)
    wrong_address[header_value_offset(wrong_address, 2, 0)] = 0x31
    repair_file_checksum(wrong_address)
    unknown_length = bytearray(original[:-6] + original[-4:])
    at = block_offset(unknown_length) + 4
    struct.pack_into("!I", unknown_length, at, struct.unpack_from("!I", original, at)[0] - 2)
    repair_file_checksum(unknown_length)
    for data, message in ((wrong_address, "not an EPS image"), (unknown_length, "unsupported firmware length")):
      with self.subTest(message=message), contextlib.redirect_stdout(io.StringIO()):
        with self.assertRaisesRegex(ValueError, message):
          updater.validate_fw(x5a(data))

  def test_pilot_a040_is_validated_offline_but_not_flashable(self):
    name = "39990-TG7-A040 (2016 Honda Pilot)/Legacy and Stock/39990-TG7-A040-STOCK.rwd"
    self.assertTrue(self.check_quietly(RWD_DIR / name))
    self.assertFalse(flash.validate(RWD_DIR / name))
    updater = load_eps_update_with_dependency_stubs()
    with contextlib.redirect_stdout(io.StringIO()):
      with self.assertRaisesRegex(ValueError, "Pilot A040 is reference-only"):
        updater.validate_fw(x5a((RWD_DIR / name).read_bytes()))

  def test_truncated_containers_and_bad_outer_checksum_are_rejected(self):
    name = "39990-TBA-A030/Proper Torque Mod/39990-TBA,A030-PTM.rwd"
    original = (RWD_DIR / name).read_bytes()
    for length in (0, 6, 10, 17, 29, block_offset(original) + 7, len(original) - 2):
      with self.subTest(length=length), self.assertRaises(ValueError):
        x5a(original[:length])
    corrupt = bytearray(original)
    corrupt[-1] ^= 1
    with self.assertRaisesRegex(ValueError, "file checksum mismatch"):
      x5a(corrupt)
    with tempfile.TemporaryDirectory() as directory:
      path = Path(directory) / "bad-checksum.rwd"
      path.write_bytes(corrupt)
      result = subprocess.run([sys.executable, "-O", str(CHECK_RWD_PATH), str(path)],
                              capture_output=True, text=True, check=False)
      self.assertNotEqual(result.returncode, 0)
      self.assertIn("file checksum mismatch", result.stdout)

  def test_updater_rejects_skip_flag_and_invalid_images_before_any_device_access(self):
    updater = load_eps_update_with_dependency_stubs()
    source = ast.parse(EPS_UPDATE_PATH.read_text())
    entry = source.body[-1]
    self.assertIsInstance(entry, ast.If)
    entry_code = compile(ast.Module(body=entry.body, type_ignores=[]), str(EPS_UPDATE_PATH), "exec")
    with mock.patch.object(updater, "get_uds_client") as connect:
      for args, error in (
          (["missing.rwd", "--skip-checksum", "--danger"], SystemExit),
          ([str(RWD_DIR / next(iter(X31_IMAGES))), "--danger"], ValueError),
          ([str(RWD_DIR / T6Z_IMAGE), "--danger"], ValueError),
      ):
        with self.subTest(args=args), mock.patch.object(sys, "argv", [str(EPS_UPDATE_PATH), *args]), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
          with self.assertRaises(error):
            exec(entry_code, vars(updater))
      connect.assert_not_called()

  def test_guided_invalid_selection_never_stops_openpilot(self):
    with mock.patch.object(flash, "find_images", return_value=[str(RWD_DIR / T6Z_IMAGE)]), \
         mock.patch.object(flash, "car_eps_fw", return_value=None), \
         mock.patch.object(flash, "stop_openpilot") as stop, \
         mock.patch.object(flash, "resolve_bus") as probe, \
         mock.patch.object(sys, "argv", ["flash.py"]), \
         mock.patch("builtins.input", return_value="1"), contextlib.redirect_stdout(io.StringIO()):
      with self.assertRaisesRegex(SystemExit, "failed validation or is unsupported"):
        flash.main()
      stop.assert_not_called()
      probe.assert_not_called()

  def test_t6z_is_offline_only_and_eps_update_remains_fail_closed(self):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
      self.assertTrue(check_rwd.check(RWD_DIR / T6Z_IMAGE))
    self.assertIn(check_rwd.T6Z_REFERENCE_NOTICE, output.getvalue())
    self.assertNotIn(T6Z_IMAGE, flash.GUIDED_FLASH_FILES)

    eps_update = load_eps_update_with_dependency_stubs()
    firmware = x5a((RWD_DIR / T6Z_IMAGE).read_bytes())
    with contextlib.redirect_stdout(io.StringIO()):
      with self.assertRaisesRegex(ValueError, "bootloader sequence"):
        eps_update.validate_fw(firmware)

  def test_t6z_exact_profile_rejects_header_can_secret_key_start_and_payload_mutations(self):
    original = (RWD_DIR / T6Z_IMAGE).read_bytes()
    mutations = {}
    for label, header_index, value_index in (
        ("header-zero", 0, 0),
        ("can-address", 2, 0),
        ("app-id", 3, 0),
        ("software-secret", 4, 0),
        ("encryption-key", 5, 0),
    ):
      changed = bytearray(original)
      changed[header_value_offset(changed, header_index, value_index)] ^= 1
      repair_file_checksum(changed)
      mutations[label] = changed

    wrong_start = bytearray(original)
    struct.pack_into(">I", wrong_start, block_offset(wrong_start), 0x20000)
    repair_file_checksum(wrong_start)
    mutations["flash-start"] = wrong_start

    wrong_payload_identity = bytearray(original)
    payload_identity = block_offset(wrong_payload_identity) + 8 + check_rwd.T6Z_IDENTITY_OFFSET
    wrong_payload_identity[payload_identity] ^= 1
    repair_file_checksum(wrong_payload_identity)
    mutations["decrypted-identity"] = wrong_payload_identity

    with tempfile.TemporaryDirectory() as tmpdir:
      for label, data in mutations.items():
        with self.subTest(label=label):
          path = Path(tmpdir) / f"t6z-{label}.rwd"
          path.write_bytes(data)
          self.assertFalse(self.check_quietly(path))

  def test_newer_t6z_header_layout_remains_offline_only(self):
    original = (RWD_DIR / T6Z_IMAGE).read_bytes()
    fw = x5a(original)
    headers = [[v.value for v in h.values] for h in fw.file_headers]
    headers[3] = [b"39990-T6Z-A110\x00\x00", b"39990,T6Z,A110\x00\x00", b"39990-T6Z,A110\x00\x00"]
    headers[4] = headers[4][:2]
    data = bytearray(original[:3])
    for values in headers:
      data.append(len(values))
      for value in values:
        data.append(len(value))
        data.extend(value)
    data.extend(original[block_offset(original):])
    repair_file_checksum(data)
    newer = x5a(data)
    with contextlib.redirect_stdout(io.StringIO()):
      check_rwd.validate_firmware(newer)
      with self.assertRaisesRegex(ValueError, "bootloader sequence"):
        check_rwd.require_uds_flashable(newer)

  def test_x31_files_are_reference_only_and_rejected(self):
    self.assertEqual(len(X31_IMAGES), 7)
    self.assertTrue(X31_IMAGES.isdisjoint(flash.GUIDED_FLASH_FILES))
    for name in X31_IMAGES:
      with self.subTest(name=name):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
          self.assertFalse(check_rwd.check(RWD_DIR / name))
        self.assertIn("not a complete 0x5A RWD container", output.getvalue())

  def test_wip_raw_and_noncurated_library_files_are_not_guided(self):
    self.assertNotIn(WIP_IMAGE, flash.GUIDED_FLASH_FILES)
    self.assertTrue(RAW_IMAGES.isdisjoint(flash.GUIDED_FLASH_FILES))
    self.assertTrue((set(EXPECTED_ASSETS) - GUIDED_IMAGES).isdisjoint(flash.GUIDED_FLASH_FILES))

  def test_no_old_flat_payload_or_trailing_space_path_component(self):
    self.assertEqual(
      {path.name for path in RWD_DIR.iterdir() if path.is_file()},
      {"README.md", "SHA256SUMS", "SOURCES.md"},
    )
    for name in EXPECTED_ASSETS:
      with self.subTest(name=name):
        self.assertTrue(all(part == part.rstrip() for part in Path(name).parts))

  def test_payload_corruption_fails_and_cli_exits_nonzero(self):
    stock = "39990-TG7-A060 (2019 Honda Pilot)/Legacy and Stock/39990-TG7-A060-STOCK.rwd"
    data = bytearray((RWD_DIR / stock).read_bytes())
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

  def test_wrong_v850_identity_and_flash_start_fail_with_valid_outer_checksum(self):
    stock = "39990-TG7-A060 (2019 Honda Pilot)/Legacy and Stock/39990-TG7-A060-STOCK.rwd"
    original = (RWD_DIR / stock).read_bytes()
    mutations = {}

    wrong_identity = bytearray(original)
    identity_at = wrong_identity.index(b"39990-TG7-A060")
    original_identity = b"39990-TG7-A060"
    wrong_identity[identity_at:identity_at + len(original_identity)] = b"39990-TG7-A999"
    repair_file_checksum(wrong_identity)
    mutations["wrong-identity.rwd"] = wrong_identity

    wrong_start = bytearray(original)
    struct.pack_into(">I", wrong_start, block_offset(wrong_start), 0x20000)
    repair_file_checksum(wrong_start)
    mutations["wrong-start.rwd"] = wrong_start

    with tempfile.TemporaryDirectory() as tmpdir:
      for filename, data in mutations.items():
        with self.subTest(filename=filename):
          path = Path(tmpdir) / filename
          path.write_bytes(data)
          self.assertFalse(self.check_quietly(path))

  def test_launcher_maps_nested_aliases_and_recursive_globs(self):
    nested = "39990-TBA-C120/Proper Torque Mod/39990-TBA,C120-PTM.rwd"
    expected = str(RWD_DIR / Path(nested))
    self.assertEqual(launcher.normalized_arguments("check_rwd.py", [f"rwd/{nested}"]), [expected])
    self.assertEqual(launcher.normalized_arguments("eps-update.py", [f"eps_tools/rwd/{nested}"]), [expected])
    self.assertEqual(launcher.normalized_arguments("flash.py", ["--bus", "1"]), ["--bus", "1"])

    expanded = launcher.normalized_arguments("check_rwd.py", ["rwd/**/*.rwd"])
    self.assertEqual(
      {Path(path).relative_to(RWD_DIR).as_posix() for path in expanded},
      RWD_IMAGES,
    )
    with self.assertRaisesRegex(SystemExit, "matched more than one image"):
      launcher.normalized_arguments("eps-update.py", ["rwd/**/*.rwd"])

  def test_guided_flasher_keeps_danger_explicit(self):
    dry_run = flash.run_eps_update("rwd/example.rwd", 1, skip_checksum=False, danger=False)
    real_flash = flash.run_eps_update("rwd/example.rwd", 1, skip_checksum=False, danger=True)
    self.assertNotIn("--danger", dry_run)
    self.assertEqual(real_flash.count("--danger"), 1)
    self.assertIn(str(EPS_DIR / "eps-update.py"), dry_run)
    self.assertIn(str(ROOT), flash.subprocess_env()["PYTHONPATH"].split(os.pathsep))

  def test_recovery_guidance_does_not_promise_success_or_blind_retry(self):
    readme = (EPS_DIR / "README.md").read_text()
    flash_source = (EPS_DIR / "flash.py").read_text()
    diag_source = (EPS_DIR / "eps-diag.py").read_text()

    self.assertNotIn("the EPS is not permanently bricked", readme)
    self.assertNotIn("the EPS is recoverable: just run this again", flash_source)
    self.assertNotIn("EPS is responding — try the flash again", diag_source)
    self.assertNotIn("re-run eps-update.py with the same .rwd", diag_source)
    self.assertIn("recovery is not guaranteed", flash_source)
    self.assertIn("it does **not** prove that the selected image", readme)
    self.assertIn("Do not blindly reuse the previous .rwd", diag_source)

  def test_root_and_historical_commands_accept_nested_paths_with_spaces(self):
    nested = "rwd/39990-TBA-C120/Proper Torque Mod/39990-TBA,C120-PTM.rwd"
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    commands = (
      ([sys.executable, str(ROOT / "check_rwd.py"), nested], ROOT),
      ([sys.executable, "check_rwd.py", nested], ROOT / "eps_tools"),
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

  def test_root_guided_command_lists_only_curated_nested_paths_before_quit(self):
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
    for name in GUIDED_IMAGES:
      with self.subTest(guided=name):
        self.assertIn(name, output)
    for name in set(EXPECTED_ASSETS) - GUIDED_IMAGES:
      with self.subTest(reference=name):
        self.assertNotIn(name, output)

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
