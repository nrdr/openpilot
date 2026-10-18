"""Saved selection identity and per-model compiler provenance; no native I/O."""
import ast
import copy
import hashlib
import os
from pathlib import Path
from types import ModuleType, SimpleNamespace

import numpy as np

import pytest

from openpilot.cereal import custom
from openpilot.nrdr.features.services import ModelAdmissionError, TINYGRAD_RUNTIME_REF


class ParamsMemory:
  def __init__(self, values):
    self.values = copy.deepcopy(values)
    self.writes = []

  def get(self, key):
    return self.values.get(key)

  def put(self, key, value, **_kwargs):
    self.values[key] = value
    self.writes.append((key, value))


def saved_pop(minimum=19):
  return custom.ModelManagerSP.ModelBundle(internalName='PMV2', displayName='Pop Model v2', index=59, generation=12,
                                          ref='source-model-ref', runner='tinygrad', is20hz=True, minimumSelectorVersion=minimum,
                                          overrides=[{'key': 'lat', 'value': '.0'}, {'key': 'long', 'value': '.3'}]).to_dict()


def definitions(relative, namespace):
  path = Path(__file__).resolve().parents[3] / relative
  tree = ast.parse(path.read_text(encoding='utf-8'))
  tree.body = [node for node in tree.body if isinstance(node, (ast.Assign, ast.AnnAssign, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
  module = ModuleType('selection_test')
  module.__dict__.update(namespace)
  exec(compile(tree, str(path), 'exec'), module.__dict__)
  return module


@pytest.fixture
def helpers():
  # Execute all real definitions with platform I/O imports replaced, not mocked
  # selection behavior. Native model-manager tests cover the real import graph.
  return definitions('openpilot/sunnypilot/models/helpers.py', {
    'custom': custom, 'np': np, 'os': os, 'hashlib': hashlib, 'Params': ParamsMemory,
    'Paths': SimpleNamespace(model_root=lambda: ''), 'chestnut_present': lambda: False,
    'cloudlog': SimpleNamespace(error=lambda *_: None)})


def test_selector_v19_retains_exact_pop_preference_and_replaces_only_stale_runner_cache(monkeypatch, helpers):
  raw = saved_pop()
  params = ParamsMemory({'ModelManager_ActiveBundle': raw, 'ModelRunnerTypeCache': int(custom.ModelManagerSP.Runner.stock)})
  monkeypatch.setattr(helpers, 'chestnut_present', lambda: False)
  assert helpers.get_selected_bundle(params).to_dict() == raw
  assert helpers.get_active_model_runner(params) == int(custom.ModelManagerSP.Runner.tinygrad)
  assert params.values['ModelManager_ActiveBundle'] == raw
  assert params.writes == [('ModelRunnerTypeCache', int(custom.ModelManagerSP.Runner.tinygrad))]


@pytest.mark.parametrize('raw', [saved_pop(18), {'invalid': True}, 'not a bundle'])
def test_unsupported_saved_selection_cannot_turn_into_default(raw, helpers):
  params = ParamsMemory({'ModelManager_ActiveBundle': raw})
  with pytest.raises(ModelAdmissionError, match='no default substituted'):
    helpers.get_selected_bundle(params)
  assert params.values['ModelManager_ActiveBundle'] == raw
  assert params.writes == []


def test_catalog_mismatch_keeps_saved_preference(monkeypatch, helpers):
  raw = saved_pop()
  params = ParamsMemory({'ModelManager_ActiveBundle': raw})
  monkeypatch.setattr(helpers, 'cloudlog', SimpleNamespace(error=lambda *_: None))
  helpers._LAST_VALIDATED_RAW.clear()
  helpers._validate_active_bundle(params, 'qcom', [custom.ModelManagerSP.ModelBundle(internalName='other', ref='another-ref')])
  assert params.values['ModelManager_ActiveBundle'] == raw
  assert not params.writes


def test_compiler_ref_is_per_bundle_not_model_source_ref_or_catalog_blanket(helpers):
  # Fetching, manifest writes and networking are outside this pure parser test.
  source = Path(__file__).resolve().parents[3] / 'openpilot/sunnypilot/models/fetcher.py'
  node = next(node for node in ast.parse(source.read_text(encoding='utf-8')).body if isinstance(node, ast.ClassDef) and node.name == 'ModelParser')
  namespace = {'custom': custom, 'is_bundle_version_compatible': helpers.is_bundle_version_compatible}
  exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), 'exec'), namespace)
  ModelParser = namespace['ModelParser']
  base = {'short_name': 'PMV2', 'display_name': 'Pop', 'index': 59, 'generation': 12, 'environment': 'development', 'runner': 'tinygrad',
              'is_20hz': True, 'minimum_selector_version': '19', 'models': [], 'ref': 'model-source', 'overrides': {'long': '.3'}}
  parsed = ModelParser.parse_models({'tinygrad_ref': 'catalog-compiler', 'bundles': [base, dict(base, tinygrad_ref=TINYGRAD_RUNTIME_REF)]})
  assert [bundle.tinygradRef for bundle in parsed] == ['catalog-compiler', TINYGRAD_RUNTIME_REF]
  assert all(bundle.ref == 'model-source' and bundle.overrides[0].value == '.3' for bundle in parsed)
