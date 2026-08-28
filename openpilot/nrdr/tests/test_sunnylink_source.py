import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

import yaml

from openpilot.nrdr.params.generated.keys import NrdrParamKey
from openpilot.nrdr.ui.sunnylink import ITEM_SOURCE_FILES, MACRO_SOURCE, PAGE_SOURCE_FILES, SOURCE_FILES, SOURCE_ROOT


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
HOST_SOURCE_ROOT = REPOSITORY_ROOT / "openpilot" / "sunnypilot" / "sunnylink" / "settings_ui_src"
GENERATED_SCHEMA = REPOSITORY_ROOT / "openpilot" / "sunnypilot" / "sunnylink" / "settings_ui.json"
EXPECTED_SOURCE_FILES = (
  "_macros.yaml",
  "items/device.yaml",
  "pages/cruise.yaml",
  "pages/software.yaml",
  "pages/steering.yaml",
)


def _collect_keys(node, keys: list[str]) -> None:
  if isinstance(node, dict):
    if isinstance(node.get("key"), str):
      keys.append(node["key"])
    for value in node.values():
      _collect_keys(value, keys)
  elif isinstance(node, list):
    for value in node:
      _collect_keys(value, keys)


def _yaml_document(relative_path: str) -> dict:
  return yaml.safe_load((SOURCE_ROOT / relative_path).read_text(encoding="utf-8"))


class TestSunnylinkSourceOwnership(unittest.TestCase):
  def test_manifest_is_explicit_complete_and_deterministic(self):
    self.assertEqual(MACRO_SOURCE, "_macros.yaml")
    self.assertEqual(ITEM_SOURCE_FILES, ("items/device.yaml",))
    self.assertEqual(PAGE_SOURCE_FILES, ("pages/cruise.yaml", "pages/software.yaml", "pages/steering.yaml"))
    self.assertEqual(SOURCE_FILES, EXPECTED_SOURCE_FILES)
    actual = tuple(sorted(path.relative_to(SOURCE_ROOT).as_posix() for path in SOURCE_ROOT.rglob("*.yaml")))
    self.assertEqual(actual, tuple(sorted(EXPECTED_SOURCE_FILES)))

  def test_fragments_declare_exact_consumer_anchors(self):
    macros = _yaml_document("_macros.yaml")
    self.assertEqual(set(macros), {"macros"})
    self.assertEqual(set(macros["macros"]), {"handcrafted_lateral_unlocked"})

    expected_pages = {
      "pages/cruise.yaml": ("cruise", "smart_cruise", ["nrdr"]),
      "pages/software.yaml": ("software", "updates", ["nrdr"]),
      "pages/steering.yaml": ("steering", "lane_change", ["nrdr", "nrdr_special"]),
    }
    for relative_path, (page_id, anchor, section_ids) in expected_pages.items():
      with self.subTest(source=relative_path):
        document = _yaml_document(relative_path)
        self.assertEqual(set(document), {"page_id", "after_section", "sections"})
        self.assertEqual(document["page_id"], page_id)
        self.assertEqual(document["after_section"], anchor)
        self.assertEqual([section["id"] for section in document["sections"]], section_ids)

    device = _yaml_document("items/device.yaml")
    self.assertEqual(set(device), {"page_id", "section_id", "after_item", "items", "extend_enablement"})
    self.assertEqual((device["page_id"], device["section_id"], device["after_item"]),
                     ("device", "general", "OnroadUploads"))
    self.assertEqual([item["key"] for item in device["items"]], ["DisablePowerDown"])
    self.assertEqual([extension["item_key"] for extension in device["extend_enablement"]], ["MaxTimeOffroad"])

  def test_all_active_generated_nrdr_settings_keys_have_canonical_source(self):
    catalog_keys = {key.value for key in NrdrParamKey}
    canonical_references: list[str] = []
    for relative_path in SOURCE_FILES:
      _collect_keys(_yaml_document(relative_path), canonical_references)
    generated_references: list[str] = []
    _collect_keys(json.loads(GENERATED_SCHEMA.read_text(encoding="utf-8")), generated_references)

    canonical_keys = set(canonical_references) & catalog_keys
    generated_nrdr_keys = set(generated_references) & catalog_keys
    self.assertEqual(len(canonical_keys), 81)
    self.assertEqual(canonical_keys, generated_nrdr_keys)
    self.assertEqual(set(canonical_references) - catalog_keys, set())
    retired_steer_ratio_keys = {
      "NrdrLearnSteerRatio", "NrdrLaneChangeEndpointSteerRatio",
      "NrdrSteerRatioCenterClarity", "NrdrSteerRatioOuterClarity",
      "NrdrSteerRatioCenterCivic", "NrdrSteerRatioOuterCivic",
      "NrdrSteerRatioCenterAccord", "NrdrSteerRatioOuterAccord",
      "NrdrSteerRatioCenterCrv5g", "NrdrSteerRatioOuterCrv5g",
      "NrdrSteerRatioCenterInsight", "NrdrSteerRatioOuterInsight",
    }
    self.assertFalse(retired_steer_ratio_keys & canonical_keys)

  def test_consumer_sources_do_not_redeclare_canonical_nrdr_keys(self):
    canonical_references: list[str] = []
    for relative_path in SOURCE_FILES:
      _collect_keys(_yaml_document(relative_path), canonical_references)
    canonical_keys = set(canonical_references)

    consumer_references: list[str] = []
    for relative_path in (
      "_macros.yaml",
      "pages/cruise.yaml",
      "pages/device.yaml",
      "pages/software.yaml",
      "pages/steering.yaml",
    ):
      _collect_keys(yaml.safe_load((HOST_SOURCE_ROOT / relative_path).read_text(encoding="utf-8")), consumer_references)
    self.assertEqual(set(consumer_references) & canonical_keys, set())

  def test_canonical_sources_ship_in_release_and_prebuilt_manifest(self):
    output = subprocess.check_output(
      [sys.executable, "tools/release/release_files.py"],
      cwd=REPOSITORY_ROOT,
    )
    released = {os.fsdecode(path) for path in output.split(b"\0") if path}
    expected = {
      "openpilot/nrdr/ui/sunnylink/__init__.py",
      *(f"openpilot/nrdr/ui/sunnylink/{relative_path}" for relative_path in SOURCE_FILES),
    }
    self.assertEqual(expected - released, set())

  def test_canonical_source_import_is_prebuild_safe_and_generated_schema_stays_with_consumer(self):
    self.assertTrue(GENERATED_SCHEMA.is_file())
    self.assertFalse((SOURCE_ROOT / "settings_ui.json").exists())
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(filter(None, (str(REPOSITORY_ROOT), environment.get("PYTHONPATH"))))
    script = """
import sys
sys.modules["yaml"] = None
from openpilot.nrdr.ui.sunnylink import SOURCE_FILES, SOURCE_ROOT
assert SOURCE_FILES
assert SOURCE_ROOT.is_dir()
assert "openpilot.sunnypilot.sunnylink.tools.compile_settings_ui" not in sys.modules
"""
    subprocess.run([sys.executable, "-c", script], cwd=REPOSITORY_ROOT, env=environment, check=True)


if __name__ == "__main__":
  unittest.main()
