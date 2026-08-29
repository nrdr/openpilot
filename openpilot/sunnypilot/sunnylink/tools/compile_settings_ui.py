#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Reads settings_ui_src/ (the dev-friendly authoring tree) and emits the
canonical settings_ui.json that the device generator + frontend consume.
Canonical NRDR macros and page sections are merged from openpilot/nrdr/ui/sunnylink.

Source layout:
  _macros.yaml                                # named rule fragments
  pages/<page_id>.yaml                        # one file per panel/page
  pages/vehicle.yaml                          # special: emits vehicle_settings

NRDR extension layout:
  _macros.yaml                                # NRDR-only named rule fragments
  items/<page_id>.yaml                        # target section, anchor, items, and condition extensions
  pages/<page_id>.yaml                        # target page, anchor, and sections

Each page.yaml contains the full panel: metadata + sections + items + sub_panels
inline. Sub-panels are nested inside the section they belong to. Items appear
in the order written in the file.

Macro references use JSON-Schema-style $ref pointers:
  enablement:
    - {$ref: "#/macros/offroad"}
    - {$ref: "#/macros/mads_full_platforms"}

Macros may reference other macros (max depth 3). Cycles raise an error.

Usage:
  python compile_settings_ui.py [--src DIR] [--extension-src DIR] [--out PATH] [--check]
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys

import yaml

_REPOSITORY_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if _REPOSITORY_ROOT not in sys.path:
  sys.path.insert(0, _REPOSITORY_ROOT)

from openpilot.nrdr.ui.sunnylink import (
  ITEM_SOURCE_FILES as NRDR_ITEM_SOURCE_FILES,
  MACRO_SOURCE as NRDR_MACRO_SOURCE,
  PAGE_SOURCE_FILES as NRDR_PAGE_SOURCE_FILES,
  SOURCE_FILES as NRDR_SOURCE_FILES,
  SOURCE_ROOT as NRDR_SOURCE_ROOT,
)
from openpilot.nrdr.ui.sunnylink_schema import SunnylinkMetadataConflict, apply_sunnylink_metadata

DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SRC = os.path.join(DIR, "settings_ui_src")
DEFAULT_OUT = os.path.join(DIR, "settings_ui.json")
DEFAULT_EXTENSION_SRC = os.fspath(NRDR_SOURCE_ROOT)

SCHEMA_VERSION = "1.0"
MAX_MACRO_DEPTH = 3


class CompileError(Exception):
  pass


class _UniqueKeyLoader(yaml.SafeLoader):
  """Safe YAML loader that rejects silently overwritten mapping fields."""


def _construct_unique_mapping(loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False) -> dict:
  loader.flatten_mapping(node)
  mapping = {}
  for key_node, value_node in node.value:
    key = loader.construct_object(key_node, deep=deep)
    try:
      duplicate = key in mapping
    except TypeError as exc:
      raise yaml.constructor.ConstructorError(
        "while constructing a mapping", node.start_mark, "found an unhashable field", key_node.start_mark,
      ) from exc
    if duplicate:
      raise yaml.constructor.ConstructorError(
        "while constructing a mapping", node.start_mark, f"found duplicate field {key!r}", key_node.start_mark,
      )
    mapping[key] = loader.construct_object(value_node, deep=deep)
  return mapping


_UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping)


def _load_yaml(path: str):
  try:
    with open(path, encoding="utf-8") as f:
      return yaml.load(f, Loader=_UniqueKeyLoader) or {}
  except yaml.YAMLError as exc:
    raise CompileError(f"{path}: invalid YAML: {exc}") from exc


def _is_ref(node) -> bool:
  return isinstance(node, dict) and len(node) == 1 and "$ref" in node


def _ref_name(node: dict) -> str:
  ref = node["$ref"]
  if not isinstance(ref, str) or not ref.startswith("#/macros/"):
    raise CompileError(f"unsupported $ref: {ref!r} (must start with '#/macros/')")
  return ref[len("#/macros/"):]


def _resolve_refs(node, macros: dict, visiting: tuple[str, ...] = ()):
  """Resolve $ref nodes against macros. Recursive; depth-limited; cycle-safe.

  - $ref in list-context: macro's list spliced into parent list.
  - $ref in scalar-context (object value): macro's value substitutes.
  - Non-list macro values may not be referenced from list contexts.
  """
  if _is_ref(node):
    name = _ref_name(node)
    if name in visiting:
      raise CompileError(f"$ref cycle: {' -> '.join(visiting + (name,))}")
    if len(visiting) >= MAX_MACRO_DEPTH:
      raise CompileError(f"$ref nesting exceeds depth {MAX_MACRO_DEPTH}: {' -> '.join(visiting + (name,))}")
    if name not in macros:
      raise CompileError(f"unknown macro: {name}")
    return _resolve_refs(copy.deepcopy(macros[name]), macros, visiting + (name,))

  if isinstance(node, dict):
    return {k: _resolve_refs(v, macros, visiting) for k, v in node.items()}

  if isinstance(node, list):
    out = []
    for item in node:
      if _is_ref(item):
        resolved = _resolve_refs(item, macros, visiting)
        if not isinstance(resolved, list):
          raise CompileError(
            f"macro '{_ref_name(item)}' must resolve to a list when used in a list context"
          )
        out.extend(resolved)
      else:
        out.append(_resolve_refs(item, macros, visiting))
    return out

  return node


# Output JSON key order. Mirrors the conventions in the original hand-written
# settings_ui.json so structural diffs after extraction are minimal.
_ITEM_KEY_ORDER = [
  "key",
  "widget",
  "needs_onroad_cycle",
  "requires_attestation",
  "blocked",
  "title",
  "description",
  "details",
  "title_param_suffix",
  "min",
  "max",
  "step",
  "unit",
  "options",
  "visibility",
  "enablement",
  "sub_items",
]


def _canon_item(item: dict, macros: dict) -> dict:
  try:
    resolved = apply_sunnylink_metadata(item)
  except SunnylinkMetadataConflict as exc:
    raise CompileError(str(exc)) from exc
  for ctx in ("visibility", "enablement"):
    if ctx in resolved:
      resolved[ctx] = _resolve_refs(resolved[ctx], macros)
  if "options" in resolved:
    new_opts = []
    for opt in resolved["options"]:
      if isinstance(opt, dict):
        opt = dict(opt)
        for ctx in ("visibility", "enablement"):
          if ctx in opt:
            opt[ctx] = _resolve_refs(opt[ctx], macros)
      new_opts.append(opt)
    resolved["options"] = new_opts
  if "sub_items" in resolved:
    resolved["sub_items"] = [_canon_item(s, macros) for s in resolved["sub_items"]]

  out: dict = {}
  for k in _ITEM_KEY_ORDER:
    if k in resolved:
      out[k] = resolved[k]
  for k, v in resolved.items():
    if k not in out:
      out[k] = v
  return out


def _canon_section(section: dict, macros: dict) -> dict:
  out: dict = {"id": section["id"], "title": section["title"]}
  if "description" in section:
    out["description"] = section["description"]
  for k in ("visibility", "enablement"):
    if k in section:
      out[k] = _resolve_refs(section[k], macros)
  if "attestation_required" in section:
    out["attestation_required"] = section["attestation_required"]
  out["items"] = [_canon_item(i, macros) for i in section.get("items", [])]
  if "sub_panels" in section and section["sub_panels"]:
    out["sub_panels"] = [_canon_sub_panel(sp, macros) for sp in section["sub_panels"]]
  for k, v in section.items():
    if k not in out and k != "order":
      out[k] = v
  return out


def _canon_sub_panel(sp: dict, macros: dict) -> dict:
  out: dict = {"id": sp["id"], "label": sp["label"], "trigger_key": sp["trigger_key"]}
  if "trigger_condition" in sp:
    out["trigger_condition"] = _resolve_refs(sp["trigger_condition"], macros)
  out["items"] = [_canon_item(i, macros) for i in sp.get("items", [])]
  for k, v in sp.items():
    if k not in out:
      out[k] = v
  return out


def _canon_panel(page: dict, macros: dict) -> dict:
  out: dict = {
    "id": page["id"],
    "label": page["label"],
    "icon": page["icon"],
    "order": page["order"],
  }
  if "remote_configurable" in page:
    out["remote_configurable"] = page["remote_configurable"]
  if "description" in page:
    out["description"] = page["description"]
  if "sections" in page and page["sections"]:
    out["sections"] = [_canon_section(s, macros) for s in page["sections"]]
  if "items" in page and page["items"]:
    out["items"] = [_canon_item(i, macros) for i in page["items"]]
  if "sub_panels" in page and page["sub_panels"]:
    out["sub_panels"] = [_canon_sub_panel(sp, macros) for sp in page["sub_panels"]]
  return out


def _canon_vehicle(page: dict, macros: dict) -> dict:
  """Convert page-shape vehicle.yaml to wire-format vehicle_settings dict."""
  out: dict = {}
  for sec in page.get("sections", []):
    brand = sec["id"]
    brand_out: dict = {"title": sec.get("title", "")}
    if "description" in sec:
      brand_out["description"] = sec["description"]
    brand_out["items"] = [_canon_item(i, macros) for i in sec.get("items", [])]
    out[brand] = brand_out
  return out


def _load_pages(src: str) -> list[dict]:
  pages_dir = os.path.join(src, "pages")
  if not os.path.isdir(pages_dir):
    return []
  pages = []
  for fn in sorted(os.listdir(pages_dir)):
    if not fn.endswith((".yaml", ".yml")):
      continue
    if fn.startswith("_"):
      continue
    path = os.path.join(pages_dir, fn)
    page = _load_yaml(path)
    if not isinstance(page, dict):
      raise CompileError(f"{path}: page YAML must be an object")
    if "id" not in page:
      raise CompileError(f"{path}: page missing 'id'")
    page["__source"] = path
    pages.append(page)
  return pages


_MACRO_EXTENSION_FIELDS = frozenset(("macros",))
_PAGE_EXTENSION_FIELDS = frozenset(("page_id", "after_section", "sections"))
_ITEM_EXTENSION_FIELDS = frozenset(("page_id", "section_id", "after_item", "items", "extend_enablement"))
_ENABLEMENT_EXTENSION_FIELDS = frozenset(("item_key", "conditions"))


def _validate_fields(document: dict, required: frozenset[str], source: str) -> None:
  if not isinstance(document, dict):
    raise CompileError(f"{source}: extension document must be an object")
  missing = required - document.keys()
  unexpected = document.keys() - required
  if missing:
    raise CompileError(f"{source}: missing required fields: {', '.join(sorted(missing))}")
  if unexpected:
    raise CompileError(f"{source}: unexpected/conflicting fields: {', '.join(sorted(unexpected))}")


def _merge_extension_macros(macros: dict, document: dict, source: str) -> dict:
  _validate_fields(document, _MACRO_EXTENSION_FIELDS, source)
  extension_macros = document["macros"]
  if not isinstance(extension_macros, dict) or not extension_macros:
    raise CompileError(f"{source}: 'macros' must be a non-empty object")
  invalid_names = sorted(repr(name) for name in extension_macros if not isinstance(name, str) or not name.replace("_", "").isalnum())
  if invalid_names:
    raise CompileError(f"{source}: invalid macro names: {invalid_names!r}")
  empty_names = sorted(name for name, body in extension_macros.items() if not body)
  if empty_names:
    raise CompileError(f"{source}: empty macros: {', '.join(empty_names)}")
  duplicates = sorted(macros.keys() & extension_macros.keys())
  if duplicates:
    raise CompileError(f"{source}: duplicate/conflicting macros: {', '.join(duplicates)}")
  return {**macros, **extension_macros}


def _section_ids(sections, source: str) -> list[str]:
  if not isinstance(sections, list) or not sections:
    raise CompileError(f"{source}: 'sections' must be a non-empty list")
  ids = []
  for index, section in enumerate(sections):
    if not isinstance(section, dict):
      raise CompileError(f"{source}: section {index} must be an object")
    missing = {"id", "title"} - section.keys()
    if missing:
      raise CompileError(f"{source}: section {index} missing required fields: {', '.join(sorted(missing))}")
    section_id = section["id"]
    if not isinstance(section_id, str) or not section_id:
      raise CompileError(f"{source}: section {index} has an invalid id")
    if section_id in ids:
      raise CompileError(f"{source}: duplicate section id {section_id!r}")
    ids.append(section_id)
  return ids


def _pages_by_id(pages: list[dict]) -> dict[str, dict]:
  page_ids = [page.get("id") for page in pages]
  invalid_page_ids = sorted(repr(page_id) for page_id in page_ids if not isinstance(page_id, str) or not page_id)
  if invalid_page_ids:
    raise CompileError(f"base settings source has invalid page ids: {', '.join(invalid_page_ids)}")
  duplicate_pages = sorted({page_id for page_id in page_ids if page_ids.count(page_id) > 1})
  if duplicate_pages:
    raise CompileError(f"base settings source has duplicate page ids: {', '.join(duplicate_pages)}")
  return {page["id"]: page for page in pages}


def _item_keys(items, source: str) -> list[str]:
  if not isinstance(items, list) or not items:
    raise CompileError(f"{source}: 'items' must be a non-empty list")
  keys = []
  for index, item in enumerate(items):
    if not isinstance(item, dict):
      raise CompileError(f"{source}: item {index} must be an object")
    item_key = item.get("key")
    if not isinstance(item_key, str) or not item_key:
      raise CompileError(f"{source}: item {index} has an invalid or missing key")
    if item_key in keys:
      raise CompileError(f"{source}: duplicate item key {item_key!r}")
    keys.append(item_key)
  return keys


def _merge_page_extensions(pages: list[dict], extensions: list[tuple[str, dict]]) -> list[dict]:
  pages_by_id = _pages_by_id(pages)
  extended_pages: set[str] = set()

  for source, document in extensions:
    _validate_fields(document, _PAGE_EXTENSION_FIELDS, source)
    page_id = document["page_id"]
    anchor = document["after_section"]
    if not isinstance(page_id, str) or not page_id:
      raise CompileError(f"{source}: 'page_id' must be a non-empty string")
    if not isinstance(anchor, str) or not anchor:
      raise CompileError(f"{source}: 'after_section' must be a non-empty string")
    if page_id in extended_pages:
      raise CompileError(f"{source}: duplicate extension for page {page_id!r}")
    if page_id not in pages_by_id:
      raise CompileError(f"{source}: target page {page_id!r} is missing")

    page = pages_by_id[page_id]
    existing_sections = page.get("sections")
    existing_ids = _section_ids(existing_sections, page.get("__source", page_id))
    extension_ids = _section_ids(document["sections"], source)
    if existing_ids.count(anchor) != 1:
      raise CompileError(f"{source}: anchor section {anchor!r} is missing or duplicated in page {page_id!r}")
    conflicts = sorted(set(existing_ids) & set(extension_ids))
    if conflicts:
      raise CompileError(f"{source}: duplicate/conflicting section ids in page {page_id!r}: {', '.join(conflicts)}")

    insertion_index = existing_ids.index(anchor) + 1
    existing_sections[insertion_index:insertion_index] = copy.deepcopy(document["sections"])
    extended_pages.add(page_id)

  return pages


def _merge_item_extensions(pages: list[dict], extensions: list[tuple[str, dict]]) -> list[dict]:
  pages_by_id = _pages_by_id(pages)
  extended_sections: set[tuple[str, str]] = set()

  for source, document in extensions:
    _validate_fields(document, _ITEM_EXTENSION_FIELDS, source)
    page_id = document["page_id"]
    section_id = document["section_id"]
    anchor = document["after_item"]
    for field, value in (("page_id", page_id), ("section_id", section_id), ("after_item", anchor)):
      if not isinstance(value, str) or not value:
        raise CompileError(f"{source}: {field!r} must be a non-empty string")
    target = (page_id, section_id)
    if target in extended_sections:
      raise CompileError(f"{source}: duplicate item extension for section {section_id!r} in page {page_id!r}")
    if page_id not in pages_by_id:
      raise CompileError(f"{source}: target page {page_id!r} is missing")

    page = pages_by_id[page_id]
    sections = page.get("sections")
    section_ids = _section_ids(sections, page.get("__source", page_id))
    if section_ids.count(section_id) != 1:
      raise CompileError(f"{source}: target section {section_id!r} is missing or duplicated in page {page_id!r}")
    section = sections[section_ids.index(section_id)]
    existing_items = section.get("items")
    existing_keys = _item_keys(existing_items, page.get("__source", page_id))
    extension_keys = _item_keys(document["items"], source)
    if existing_keys.count(anchor) != 1:
      raise CompileError(f"{source}: anchor item {anchor!r} is missing or duplicated in section {section_id!r}")
    conflicts = sorted(set(existing_keys) & set(extension_keys))
    if conflicts:
      raise CompileError(f"{source}: duplicate/conflicting item keys in section {section_id!r}: {', '.join(conflicts)}")

    insertion_index = existing_keys.index(anchor) + 1
    existing_items[insertion_index:insertion_index] = copy.deepcopy(document["items"])

    enablement_extensions = document["extend_enablement"]
    if not isinstance(enablement_extensions, list) or not enablement_extensions:
      raise CompileError(f"{source}: 'extend_enablement' must be a non-empty list")
    extended_items: set[str] = set()
    for index, extension in enumerate(enablement_extensions):
      extension_source = f"{source}: enablement extension {index}"
      _validate_fields(extension, _ENABLEMENT_EXTENSION_FIELDS, extension_source)
      item_key = extension["item_key"]
      if not isinstance(item_key, str) or not item_key:
        raise CompileError(f"{extension_source}: 'item_key' must be a non-empty string")
      if item_key in extended_items:
        raise CompileError(f"{source}: duplicate enablement extension for item {item_key!r}")
      matching_items = [item for item in existing_items if item.get("key") == item_key]
      if len(matching_items) != 1:
        raise CompileError(f"{source}: enablement target item {item_key!r} is missing or duplicated")
      conditions = extension["conditions"]
      if not isinstance(conditions, list) or not conditions or not all(isinstance(condition, dict) for condition in conditions):
        raise CompileError(f"{extension_source}: 'conditions' must be a non-empty list of objects")
      if any(condition in conditions[:index] for index, condition in enumerate(conditions)):
        raise CompileError(f"{extension_source}: duplicate conditions")
      target_item = matching_items[0]
      target_enablement = target_item.get("enablement")
      if not isinstance(target_enablement, list):
        raise CompileError(f"{source}: enablement target item {item_key!r} has no condition list")
      if any(condition in target_enablement for condition in conditions):
        raise CompileError(f"{source}: duplicate/conflicting enablement condition for item {item_key!r}")
      target_enablement.extend(copy.deepcopy(conditions))
      extended_items.add(item_key)

    extended_sections.add(target)

  return pages


def _load_extension_sources(src: str) -> tuple[tuple[str, dict], list[tuple[str, dict]], list[tuple[str, dict]]]:
  if not os.path.isdir(src):
    raise CompileError(f"canonical extension source directory is missing: {src}")

  expected = {path.replace("\\", "/") for path in NRDR_SOURCE_FILES}
  actual = set()
  for root, _, filenames in os.walk(src):
    for filename in filenames:
      if filename.endswith((".yaml", ".yml")):
        actual.add(os.path.relpath(os.path.join(root, filename), src).replace("\\", "/"))
  missing = sorted(expected - actual)
  unexpected = sorted(actual - expected)
  if missing:
    raise CompileError(f"canonical extension source files are missing: {', '.join(missing)}")
  if unexpected:
    raise CompileError(f"canonical extension source has unregistered files: {', '.join(unexpected)}")

  macro_source = os.path.join(src, NRDR_MACRO_SOURCE)
  macro_document = _load_yaml(macro_source)
  item_extensions = []
  for relative_path in NRDR_ITEM_SOURCE_FILES:
    source = os.path.join(src, relative_path)
    document = _load_yaml(source)
    expected_page_id = os.path.splitext(os.path.basename(relative_path))[0]
    if document.get("page_id") != expected_page_id:
      raise CompileError(
        f"{source}: page_id {document.get('page_id')!r} conflicts with filename {expected_page_id!r}",
      )
    item_extensions.append((source, document))
  page_extensions = []
  for relative_path in NRDR_PAGE_SOURCE_FILES:
    source = os.path.join(src, relative_path)
    document = _load_yaml(source)
    expected_page_id = os.path.splitext(os.path.basename(relative_path))[0]
    if document.get("page_id") != expected_page_id:
      raise CompileError(
        f"{source}: page_id {document.get('page_id')!r} conflicts with filename {expected_page_id!r}",
      )
    page_extensions.append((source, document))
  return (macro_source, macro_document), page_extensions, item_extensions


def compile_schema(src: str, extension_src: str = DEFAULT_EXTENSION_SRC) -> dict:
  macros_doc = _load_yaml(os.path.join(src, "_macros.yaml"))
  macros = (macros_doc.get("macros") or {}) if isinstance(macros_doc, dict) else {}
  macro_extension, page_extensions, item_extensions = _load_extension_sources(extension_src)
  macros = _merge_extension_macros(macros, macro_extension[1], macro_extension[0])

  pages = _load_pages(src)
  pages = _merge_page_extensions(pages, page_extensions)
  pages = _merge_item_extensions(pages, item_extensions)

  panels_out = []
  vehicle_out: dict = {}

  # Order panels by `order` field (falling back to file position).
  panel_pages = [p for p in pages if p.get("kind") != "vehicle"]
  panel_pages.sort(key=lambda p: (p.get("order", 999), p["id"]))

  for page in panel_pages:
    panels_out.append(_canon_panel(page, macros))

  for page in pages:
    if page.get("kind") == "vehicle":
      vehicle_out = _canon_vehicle(page, macros)

  return {
    "$schema": "./settings_ui.schema.json",
    "schema_version": SCHEMA_VERSION,
    "panels": panels_out,
    "vehicle_settings": vehicle_out,
  }


def _main() -> int:
  parser = argparse.ArgumentParser(description="Compile settings_ui_src/ -> settings_ui.json")
  parser.add_argument("--src", default=DEFAULT_SRC)
  parser.add_argument("--extension-src", default=DEFAULT_EXTENSION_SRC)
  parser.add_argument("--out", default=DEFAULT_OUT)
  parser.add_argument("--check", action="store_true",
                      help="Compile and diff against existing settings_ui.json; exit non-zero on diff.")
  args = parser.parse_args()

  schema = compile_schema(args.src, args.extension_src)
  rendered = json.dumps(schema, indent=2) + "\n"

  if args.check:
    if not os.path.exists(args.out):
      print(f"--check: {args.out} does not exist", file=sys.stderr)
      return 1
    with open(args.out, encoding="utf-8") as f:
      current = f.read()
    if current.strip() == rendered.strip():
      print(f"--check: {args.out} matches compiled output")
      return 0
    print(f"--check: {args.out} differs from compiled output", file=sys.stderr)
    cur_obj = json.loads(current)
    if cur_obj == schema:
      print("(structurally equal; only formatting differs)", file=sys.stderr)
    return 1

  with open(args.out, "w", encoding="utf-8", newline="\n") as f:
    f.write(rendered)
  print(f"Wrote {args.out}")
  return 0


if __name__ == "__main__":
  sys.exit(_main())
