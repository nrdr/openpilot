"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Tests for the settings_ui_src/ -> settings_ui.json compiler. Covers:
  - Roundtrip: compiled output matches the checked-in settings_ui.json
  - $ref macro resolution semantics (list-splice, scalar-substitute, depth, cycles)
  - Strict NRDR macro, section, item, and condition extension merging
  - Per-page tree integrity (every page has id; vehicle page emits to vehicle_settings)

Does not cover device-side generator (test_settings_schema.py) or per-bug
regression (test_settings_changes.py); those continue to validate the
compiled output once the compiler has produced it.
"""
from __future__ import annotations

import difflib
import json
import os
import shutil
import subprocess
import sys
import tempfile

import yaml

from openpilot.sunnypilot.sunnylink.tools.compile_settings_ui import (
  CompileError,
  DEFAULT_EXTENSION_SRC,
  DEFAULT_OUT,
  DEFAULT_SRC,
  _canon_item,
  _load_extension_sources,
  _load_yaml,
  _merge_extension_macros,
  _merge_item_extensions,
  _merge_page_extensions,
  _resolve_refs,
  compile_schema,
)
from openpilot.common.test import OpenpilotTestCase


def compiled() -> dict:
  return compile_schema(DEFAULT_SRC)


def committed() -> dict:
  with open(DEFAULT_OUT) as f:
    return json.load(f)


class TestRoundtrip(OpenpilotTestCase):
  def test_compiled_matches_committed(self, compiled, committed):
    """Compiled output must match the checked-in JSON."""
    if compiled == committed:
      return
    diff = "\n".join(difflib.unified_diff(
      json.dumps(committed, indent=2).splitlines(),
      json.dumps(compiled, indent=2).splitlines(),
      fromfile="settings_ui.json (committed)",
      tofile="settings_ui.json (freshly compiled)",
      lineterm="",
    ))
    self.fail(f"settings_ui.json schema mismatch — run compile_settings_ui.py\n\n{diff}")

  def test_committed_file_is_canonical(self):
    """Compiled output must byte-match the checked-in file (including trailing newline).
    Drift means someone edited settings_ui.json by hand instead of editing settings_ui_src/."""
    schema = compile_schema(DEFAULT_SRC)
    rendered = json.dumps(schema, indent=2) + "\n"
    with open(DEFAULT_OUT) as f:
      current = f.read()
    if current == rendered:
      return
    diff = "\n".join(difflib.unified_diff(
      current.splitlines(),
      rendered.splitlines(),
      fromfile="settings_ui.json (on disk)",
      tofile="settings_ui.json (freshly compiled)",
      lineterm="",
    ))
    self.fail(f"settings_ui.json out of sync — run compile_settings_ui.py\n\n{diff}")

  def test_direct_check_entrypoint_is_cwd_independent(self):
    script = os.path.join(os.path.dirname(DEFAULT_SRC), "tools", "compile_settings_ui.py")
    with tempfile.TemporaryDirectory() as temporary_directory:
      subprocess.run([sys.executable, script, "--check"], cwd=temporary_directory, check=True, capture_output=True, text=True)


class TestRefResolution(OpenpilotTestCase):
  def test_nrdr_explicit_metadata_conflict_raises(self):
    with self.assertRaisesRegex(CompileError, "LatPScaleLowSpeed.*'max'"):
      _canon_item({"key": "LatPScaleLowSpeed", "widget": "option", "max": 501}, {})

  def test_list_context_splices(self):
    macros = {"a": [{"type": "offroad_only"}], "b": [{"type": "not_engaged"}]}
    out = _resolve_refs([{"$ref": "#/macros/a"}, {"$ref": "#/macros/b"}], macros)
    assert out == [{"type": "offroad_only"}, {"type": "not_engaged"}]

  def test_scalar_context_substitutes(self):
    macros = {"x": {"type": "capability", "field": "brand", "equals": "tesla"}}
    out = _resolve_refs({"condition": {"$ref": "#/macros/x"}}, macros)
    assert out == {"condition": {"type": "capability", "field": "brand", "equals": "tesla"}}

  def test_chained_ref_resolves(self):
    macros = {
      "leaf": [{"type": "offroad_only"}],
      "middle": [{"$ref": "#/macros/leaf"}],
    }
    out = _resolve_refs([{"$ref": "#/macros/middle"}], macros)
    assert out == [{"type": "offroad_only"}]

  def test_unknown_macro_raises(self):
    with self.assertRaisesRegex(CompileError, "unknown macro"):
      _resolve_refs([{"$ref": "#/macros/missing"}], {})

  def test_cycle_raises(self):
    macros = {"a": [{"$ref": "#/macros/b"}], "b": [{"$ref": "#/macros/a"}]}
    with self.assertRaisesRegex(CompileError, "cycle"):
      _resolve_refs([{"$ref": "#/macros/a"}], macros)

  def test_depth_limit(self):
    # Depth 4 chain should fail (limit is 3).
    macros = {
      "l1": [{"$ref": "#/macros/l2"}],
      "l2": [{"$ref": "#/macros/l3"}],
      "l3": [{"$ref": "#/macros/l4"}],
      "l4": [{"type": "offroad_only"}],
    }
    with self.assertRaisesRegex(CompileError, "depth"):
      _resolve_refs([{"$ref": "#/macros/l1"}], macros)

  def test_invalid_ref_scheme(self):
    with self.assertRaisesRegex(CompileError, "unsupported"):
      _resolve_refs([{"$ref": "https://example.com/x"}], {})

  def test_scalar_macro_in_list_context_raises(self):
    macros = {"x": {"type": "offroad_only"}}  # macro is a single rule (dict), not a list
    with self.assertRaisesRegex(CompileError, "must resolve to a list"):
      _resolve_refs([{"$ref": "#/macros/x"}], macros)


class TestExtensionMerge(OpenpilotTestCase):
  def test_page_sections_insert_after_explicit_anchor(self):
    pages = [{"id": "steering", "sections": [
      {"id": "base", "title": "Base"},
      {"id": "following", "title": "Following"},
    ]}]
    extensions = [("nrdr.yaml", {
      "page_id": "steering",
      "after_section": "base",
      "sections": [{"id": "nrdr", "title": "NRDR"}],
    })]

    merged = _merge_page_extensions(pages, extensions)

    assert [section["id"] for section in merged[0]["sections"]] == ["base", "nrdr", "following"]

  def test_missing_anchor_raises(self):
    pages = [{"id": "steering", "sections": [{"id": "base", "title": "Base"}]}]
    extensions = [("nrdr.yaml", {
      "page_id": "steering",
      "after_section": "missing",
      "sections": [{"id": "nrdr", "title": "NRDR"}],
    })]
    with self.assertRaisesRegex(CompileError, "anchor section.*missing"):
      _merge_page_extensions(pages, extensions)

  def test_duplicate_section_id_raises(self):
    pages = [{"id": "steering", "sections": [{"id": "base", "title": "Base"}]}]
    extensions = [("nrdr.yaml", {
      "page_id": "steering",
      "after_section": "base",
      "sections": [{"id": "base", "title": "Conflicting"}],
    })]
    with self.assertRaisesRegex(CompileError, "duplicate/conflicting section ids"):
      _merge_page_extensions(pages, extensions)

  def test_duplicate_page_extension_raises(self):
    pages = [{"id": "steering", "sections": [{"id": "base", "title": "Base"}]}]
    document = {
      "page_id": "steering",
      "after_section": "base",
      "sections": [{"id": "nrdr", "title": "NRDR"}],
    }
    with self.assertRaisesRegex(CompileError, "duplicate extension for page"):
      _merge_page_extensions(pages, [("one.yaml", document), ("two.yaml", document)])

  def test_unknown_fragment_field_raises(self):
    pages = [{"id": "steering", "sections": [{"id": "base", "title": "Base"}]}]
    extensions = [("nrdr.yaml", {
      "page_id": "steering",
      "after_section": "base",
      "sections": [{"id": "nrdr", "title": "NRDR"}],
      "label": "conflicts with host page metadata",
    })]
    with self.assertRaisesRegex(CompileError, "unexpected/conflicting fields: label"):
      _merge_page_extensions(pages, extensions)

  def test_missing_fragment_field_raises(self):
    pages = [{"id": "steering", "sections": [{"id": "base", "title": "Base"}]}]
    extensions = [("nrdr.yaml", {
      "page_id": "steering",
      "sections": [{"id": "nrdr", "title": "NRDR"}],
    })]
    with self.assertRaisesRegex(CompileError, "missing required fields: after_section"):
      _merge_page_extensions(pages, extensions)

  def test_duplicate_macro_name_raises(self):
    with self.assertRaisesRegex(CompileError, "duplicate/conflicting macros: offroad"):
      _merge_extension_macros(
        {"offroad": [{"type": "offroad_only"}]},
        {"macros": {"offroad": [{"type": "not_engaged"}]}},
        "nrdr.yaml",
      )

  def test_duplicate_yaml_field_raises(self):
    with tempfile.TemporaryDirectory() as temporary_directory:
      path = os.path.join(temporary_directory, "duplicate.yaml")
      with open(path, "w", encoding="utf-8") as file:
        file.write("macros:\n  duplicate: []\n  duplicate: []\n")
      with self.assertRaisesRegex(CompileError, "duplicate field 'duplicate'"):
        _load_yaml(path)

  def test_missing_or_unregistered_extension_source_raises(self):
    with tempfile.TemporaryDirectory() as temporary_directory:
      with self.assertRaisesRegex(CompileError, "source files are missing"):
        _load_extension_sources(temporary_directory)

      shutil.copytree(DEFAULT_EXTENSION_SRC, temporary_directory, dirs_exist_ok=True)
      with open(os.path.join(temporary_directory, "unexpected.yaml"), "w", encoding="utf-8") as file:
        file.write("macros: {}\n")
      with self.assertRaisesRegex(CompileError, "unregistered files: unexpected.yaml"):
        _load_extension_sources(temporary_directory)

  @staticmethod
  def _device_page():
    return [{"id": "device", "sections": [{
      "id": "general",
      "title": "General",
      "items": [
        {"key": "OnroadUploads", "widget": "toggle"},
        {"key": "MaxTimeOffroad", "widget": "option", "enablement": [{"type": "offroad_only"}]},
      ],
    }]}]

  @staticmethod
  def _device_extension():
    return ("device.yaml", {
      "page_id": "device",
      "section_id": "general",
      "after_item": "OnroadUploads",
      "items": [{"key": "DisablePowerDown", "widget": "toggle"}],
      "extend_enablement": [{
        "item_key": "MaxTimeOffroad",
        "conditions": [{"type": "param", "key": "DisablePowerDown", "equals": False}],
      }],
    })

  def test_items_insert_after_explicit_anchor_and_extend_conditions(self):
    pages = _merge_item_extensions(self._device_page(), [self._device_extension()])
    items = pages[0]["sections"][0]["items"]

    assert [item["key"] for item in items] == ["OnroadUploads", "DisablePowerDown", "MaxTimeOffroad"]
    assert items[-1]["enablement"] == [
      {"type": "offroad_only"},
      {"type": "param", "key": "DisablePowerDown", "equals": False},
    ]

  def test_item_extension_missing_section_or_anchor_raises(self):
    source, extension = self._device_extension()
    missing_section = {**extension, "section_id": "missing"}
    with self.assertRaisesRegex(CompileError, "target section 'missing' is missing"):
      _merge_item_extensions(self._device_page(), [(source, missing_section)])

    missing_anchor = {**extension, "after_item": "missing"}
    with self.assertRaisesRegex(CompileError, "anchor item 'missing' is missing"):
      _merge_item_extensions(self._device_page(), [(source, missing_anchor)])

  def test_item_extension_conflicting_key_raises(self):
    source, extension = self._device_extension()
    conflict = {**extension, "items": [{"key": "MaxTimeOffroad", "widget": "toggle"}]}
    with self.assertRaisesRegex(CompileError, "duplicate/conflicting item keys"):
      _merge_item_extensions(self._device_page(), [(source, conflict)])

  def test_duplicate_item_extension_raises(self):
    extension = self._device_extension()
    with self.assertRaisesRegex(CompileError, "duplicate item extension for section"):
      _merge_item_extensions(self._device_page(), [extension, extension])

  def test_item_enablement_target_or_condition_conflict_raises(self):
    source, extension = self._device_extension()
    missing_target = {
      **extension,
      "extend_enablement": [{"item_key": "missing", "conditions": [{"type": "offroad_only"}]}],
    }
    with self.assertRaisesRegex(CompileError, "enablement target item 'missing' is missing"):
      _merge_item_extensions(self._device_page(), [(source, missing_target)])

    duplicate_condition = {
      **extension,
      "extend_enablement": [{"item_key": "MaxTimeOffroad", "conditions": [{"type": "offroad_only"}]}],
    }
    with self.assertRaisesRegex(CompileError, "duplicate/conflicting enablement condition"):
      _merge_item_extensions(self._device_page(), [(source, duplicate_condition)])


class TestCompiledShape(OpenpilotTestCase):
  def test_panels_present(self, compiled):
    assert isinstance(compiled["panels"], list)
    assert len(compiled["panels"]) == 9
    panel_ids = {p["id"] for p in compiled["panels"]}
    assert {"steering", "cruise", "display", "visuals", "toggles",
            "device", "software", "developer", "models"} <= panel_ids

  def test_vehicle_settings_consistent_shape(self, compiled):
    """Each brand in vehicle_settings must have {title, description, items}."""
    for brand, data in compiled["vehicle_settings"].items():
      assert isinstance(data, dict), f"{brand}: expected object, got {type(data).__name__}"
      assert "title" in data, f"{brand}: missing title"
      assert "description" in data, f"{brand}: missing description"
      assert "items" in data, f"{brand}: missing items"

  def test_no_dangling_refs_after_compile(self, compiled):
    """All $ref objects must be resolved during compilation."""
    def walk(node):
      if isinstance(node, dict):
        if "$ref" in node:
          self.fail(f"unresolved $ref: {node}")
        for v in node.values():
          walk(v)
      elif isinstance(node, list):
        for x in node:
          walk(x)
    walk(compiled)


class TestSourceTreeIntegrity(OpenpilotTestCase):
  def test_macros_yaml_well_formed(self):
    with open(os.path.join(DEFAULT_SRC, "_macros.yaml")) as f:
      doc = yaml.safe_load(f)
    assert "macros" in doc
    for name, body in doc["macros"].items():
      assert name.replace("_", "").isalnum(), f"macro name '{name}' must be alphanumeric_"
      assert body, f"macro '{name}' empty"

  def test_pages_dir_well_formed(self):
    pages_dir = os.path.join(DEFAULT_SRC, "pages")
    assert os.path.isdir(pages_dir), "pages/ directory missing"
    page_files = sorted(fn for fn in os.listdir(pages_dir) if fn.endswith(".yaml"))
    # 9 panels + 1 vehicle = 10
    assert len(page_files) == 10, f"expected 10 pages, found {len(page_files)}: {page_files}"

  def test_every_page_has_id(self):
    pages_dir = os.path.join(DEFAULT_SRC, "pages")
    for fn in sorted(os.listdir(pages_dir)):
      if not fn.endswith(".yaml"):
        continue
      path = os.path.join(pages_dir, fn)
      with open(path) as f:
        doc = yaml.safe_load(f)
      assert isinstance(doc, dict), f"{path}: top-level must be a mapping"
      assert "id" in doc, f"{path}: page missing 'id'"
      # File basename should match page id (modulo .yaml extension).
      expected_id = os.path.splitext(fn)[0]
      assert doc["id"] == expected_id, (
        f"{path}: page id '{doc['id']}' must match filename '{expected_id}'"
      )

  def test_vehicle_page_kind(self):
    """vehicle.yaml must declare kind: vehicle so it routes to vehicle_settings."""
    path = os.path.join(DEFAULT_SRC, "pages", "vehicle.yaml")
    with open(path) as f:
      doc = yaml.safe_load(f)
    assert doc.get("kind") == "vehicle", "vehicle.yaml must declare kind: vehicle"
