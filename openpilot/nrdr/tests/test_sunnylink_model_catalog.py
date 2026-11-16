"""Remote model catalog responses, without network or persistent parameter writes."""
import ast
import base64
import copy
from enum import IntEnum
import gzip
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]


def load_function(relative_path, name, namespace):
  path = ROOT / relative_path
  method = next(n for n in ast.parse(path.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == name)
  method.decorator_list = []
  exec(compile(ast.Module(body=[method], type_ignores=[]), str(path), "exec"), namespace)
  return namespace[name]


class MemoryParams:
  def __init__(self, values):
    self.values = copy.deepcopy(values)

  def get(self, key):
    return self.values.get(key)

  def all_keys(self):
    return [key.encode() for key in self.values]

  def get_type(self, key):
    return ParamType.JSON


ParamType = IntEnum("ParamType", "STRING BOOL INT FLOAT TIME JSON BYTES", start=0)


def catalog_response(params, local):
  function = load_function("openpilot/sunnypilot/models/fetcher.py", "sunnylink_model_catalog_overrides", {
    "local_rebuilds_for_source": lambda source: local if source == "qcom" else [],
  })
  return function(params)


def cheddar():
  manifest = json.loads((ROOT / "openpilot/nrdr/config/model_artifacts.json").read_text())
  return next(recipe["catalog_bundle"] for recipe in manifest["legacy_rebuilds"].values() if recipe.get("model_name") == "CHEDDAR")


def settings():
  return {"ModelManager_ActiveJson": {"qcom": "https://example.invalid/qcom.json", "chestnut": "https://example.invalid/big.json"},
          "ModelManager_ModelsCache": {"tinygrad_ref": "original-compiler", "bundles": [{"ref": "pop", "short_name": "PMV2"}]},
          "ModelManager_ActiveBundle": {"ref": cheddar()["ref"], "internalName": "CHEDDAR"}}


def test_verified_local_model_is_in_remote_list_and_selection_matches():
  params = MemoryParams(settings())
  response = catalog_response(params, [cheddar()])
  assert response["ModelManager_ActiveJson"] == {**settings()["ModelManager_ActiveJson"], "qcom": ""}
  models = response["ModelManager_ModelsCache"]["bundles"]
  assert models == settings()["ModelManager_ModelsCache"]["bundles"] + [cheddar()]
  # Match the web UI's short_name/internalName lookup: no erroneous CD210 fallback.
  assert next(m for m in models if m["short_name"] == params.get("ModelManager_ActiveBundle")["internalName"])["display_name"].startswith("Cheddar")
  assert response["ModelManager_ModelsCache"]["tinygrad_ref"] == "original-compiler"
  assert params.values == settings()


def test_devices_without_verified_local_rebuilds_keep_existing_remote_catalog():
  params = MemoryParams(settings())
  assert catalog_response(params, []) == {}
  assert params.values == settings()


def test_local_entry_is_not_duplicated_if_upstream_catalog_already_contains_it():
  params = MemoryParams(settings())
  params.values["ModelManager_ModelsCache"]["bundles"].append(cheddar())
  assert catalog_response(params, [cheddar()])["ModelManager_ModelsCache"] == params.get("ModelManager_ModelsCache")


@pytest.mark.parametrize("compression", [False, True])
def test_rpc_transports_catalog_override_but_keeps_saved_selection_and_values(compression):
  params = MemoryParams(settings())
  response = load_function("openpilot/sunnypilot/sunnylink/athena/sunnylinkd.py", "getParams", {
    "Params": lambda: params, "ParamKeyType": ParamType, "json": json, "gzip": gzip, "base64": base64,
    "sunnylink_model_catalog_overrides": lambda p: catalog_response(p, [cheddar()]),
    "get_param_as_byte": lambda key: json.dumps(params.get(key)).encode(),
  })(list(params.values), compression)
  items = json.loads(response["params"])
  decoded = {}
  for item in items:
    raw = base64.b64decode(item["value"])
    decoded[item["key"]] = json.loads(gzip.decompress(raw) if compression else raw)
    assert response[item["key"]] == item["value"]
  assert decoded["ModelManager_ActiveJson"]["qcom"] == ""
  assert decoded["ModelManager_ModelsCache"]["bundles"][-1] == cheddar()
  assert decoded["ModelManager_ActiveBundle"] == settings()["ModelManager_ActiveBundle"]
  assert params.values == settings()


def test_unrelated_rpc_reads_do_not_inspect_model_cache():
  params = MemoryParams({"ModelManager_ActiveBundle": {"internalName": "CHEDDAR"}})
  def forbidden(_params):
    raise AssertionError("Unrelated settings request must not inspect model artifacts")
  response = load_function("openpilot/sunnypilot/sunnylink/athena/sunnylinkd.py", "getParams", {
    "Params": lambda: params, "ParamKeyType": ParamType, "json": json, "gzip": gzip, "base64": base64,
    "sunnylink_model_catalog_overrides": forbidden,
    "get_param_as_byte": lambda key: json.dumps(params.get(key)).encode(),
  })(["ModelManager_ActiveBundle"])
  assert json.loads(base64.b64decode(response["ModelManager_ActiveBundle"])) == params.get("ModelManager_ActiveBundle")
