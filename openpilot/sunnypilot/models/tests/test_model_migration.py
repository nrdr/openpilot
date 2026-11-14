"""Same-model compiler repair: real HTTP chunks, retained files, atomic selection."""

import copy
from contextlib import contextmanager
from pathlib import Path
import threading
from types import SimpleNamespace
import unittest
from unittest import mock
from uuid import UUID

import requests

from openpilot.cereal import custom
from openpilot.common.file_chunker import get_chunk_name, get_manifest_path, open_file_chunked
from openpilot.common.params import Params
from openpilot.nrdr.features.services import TINYGRAD_RUNTIME_REF
from openpilot.nrdr.features.services.model_manager import get_model_repair_candidate
from openpilot.selfdrive.test.helpers import http_server_context
from openpilot.sunnypilot.models import fetcher as fetcher_module, helpers, manager as manager_module
from openpilot.sunnypilot.models.fetcher import ModelFetcher, ModelParser
from openpilot.sunnypilot.models.tests.test_manager_download import (
  CHUNK_BODIES, DownloadHandler, ManagerDownloadTestBase, manifest_bundle, sha256,
)


CATALOG_ORIGIN = 'https://models.example.test'


class MemoryParams:
  """Copy on read/write, like JSON Params, so in-place edits cannot hide a race."""
  def __init__(self, values=None):
    self.values = copy.deepcopy(values or {})
    self.writes = []

  def get(self, key):
    return copy.deepcopy(self.values.get(key))

  def get_bool(self, key):
    return bool(self.values.get(key, False))

  def put(self, key, value, **kwargs):
    self.values[key] = copy.deepcopy(value)
    self.writes.append((key, copy.deepcopy(value)))

  put_bool = put

  def remove(self, key):
    self.values.pop(key, None)


def repair_bundle(source='qcom', *, compiler=TINYGRAD_RUNTIME_REF):
  """Synthetic identity shared across sources to expose cross-slot resolution."""
  return custom.ModelManagerSP.ModelBundle(
    ref='saved-model-source-ref', internalName='MIGRATION', displayName='Saved model',
    index=59, generation=12, runner='tinygrad', minimumSelectorVersion=20,
    tinygradRef=compiler, onnxSha256=sha256(source.encode()), is20hz=True,
    overrides=[{'key': 'long', 'value': '.3'}],
    models=[{'type': model_type, 'artifact': {
      'fileName': name,
      'downloadUri': {'uri': f'{CATALOG_ORIGIN}/{source}/{name}', 'sha256': sha256(b''.join(CHUNK_BODIES))},
      'chunks': [{'fileName': get_chunk_name(name, i, len(CHUNK_BODIES)), 'sha256': sha256(body)}
                 for i, body in enumerate(CHUNK_BODIES)],
    }} for name, model_type in (('driving_test_tinygrad.pkl', 'vision'), ('policy_test_tinygrad.pkl', 'policy'))],
  )


class TestModelRepairCandidate(unittest.TestCase):
  def test_legacy_same_identity_gets_current_compiler_without_mutation(self):
    for compiler in ('', '62bf6fb072880905a4c490f0f4f4a6b3c23346ec'):
      with self.subTest(compiler=compiler):
        saved, target = repair_bundle(compiler=compiler), repair_bundle()
        saved.minimumSelectorVersion = 19
        before = (saved.to_dict(), target.to_dict())
        assert get_model_repair_candidate(saved, [target]) is target
        assert (saved.to_dict(), target.to_dict()) == before

  def test_identity_must_match_and_be_nonempty(self):
    saved = repair_bundle(compiler='')
    for field, value in (('ref', ''), ('ref', 'different'), ('internalName', ''), ('internalName', 'PMV2'),
                         ('generation', 13), ('runner', 'snpe'), ('tinygradRef', 'other-compiler')):
      with self.subTest(field=field, value=value):
        target = repair_bundle()
        setattr(target, field, value)
        assert get_model_repair_candidate(saved, [target]) is None
    for field in ('ref', 'internalName'):
      blank = repair_bundle(compiler='')
      setattr(blank, field, '')
      assert get_model_repair_candidate(blank, [repair_bundle()]) is None
    assert get_model_repair_candidate(None, [repair_bundle()]) is None
    assert get_model_repair_candidate(saved, []) is None

  def test_every_artifact_must_be_a_safe_compiled_https_download(self):
    for defect in ('no-models', 'filename', 'traversal', 'absolute', 'backslash', 'onnx', 'uri', 'http',
                   'full-hash', 'nonhex-full-hash', 'chunk-hash', 'nonhex-chunk-hash'):
      with self.subTest(defect=defect):
        target = repair_bundle()
        artifact = target.models[-1].artifact  # A valid first artifact must not admit a broken second one.
        if defect == 'no-models':
          target.models = []
        elif defect in ('filename', 'traversal', 'absolute', 'backslash', 'onnx'):
          artifact.fileName = {'filename': '', 'traversal': '../policy.pkl', 'absolute': '/policy.pkl',
                               'backslash': 'sub\\policy.pkl', 'onnx': 'policy.onnx'}[defect]
        elif defect in ('uri', 'http'):
          artifact.downloadUri.uri = '' if defect == 'uri' else 'http://models.example.test/policy.pkl'
        elif 'chunk' in defect:
          artifact.chunks[-1].sha256 = 'z' * 64 if defect.startswith('nonhex') else 'a' * 63
        else:
          artifact.downloadUri.sha256 = 'z' * 64 if defect.startswith('nonhex') else 'a' * 63
        assert get_model_repair_candidate(repair_bundle(compiler=''), [target]) is None

  def test_current_content_ignores_local_filenames_and_selector19(self):
    saved, target = repair_bundle(), repair_bundle()
    saved.minimumSelectorVersion = 19
    for model in saved.models:
      artifact = model.artifact
      artifact.fileName = f'nrdr-qcom-{artifact.downloadUri.sha256}-{artifact.fileName}'
      for i, chunk in enumerate(artifact.chunks):
        chunk.fileName = get_chunk_name(artifact.fileName, i, len(artifact.chunks))
    assert get_model_repair_candidate(saved, [target]) is None

  def test_https_scheme_without_a_host_is_not_a_valid_download_uri(self):
    for uri in ('https://', 'https:///policy.pkl'):
      with self.subTest(uri=uri):
        target = repair_bundle()
        target.models[-1].artifact.downloadUri.uri = uri
        assert get_model_repair_candidate(repair_bundle(compiler=''), [target]) is None

  def test_current_compiler_with_different_full_chunk_or_type_identity_needs_repair(self):
    for defect in ('full-hash', 'chunk-hash', 'type'):
      with self.subTest(defect=defect):
        saved, target = repair_bundle(), repair_bundle()
        if defect == 'full-hash':
          saved.models[-1].artifact.downloadUri.sha256 = 'a' * 64
        elif defect == 'chunk-hash':
          saved.models[-1].artifact.chunks[-1].sha256 = 'a' * 64
        else:
          saved.models[-1].type = 'supercombo'
        assert get_model_repair_candidate(saved, [target]) is target


class TestModelMigration(ManagerDownloadTestBase):
  def setUp(self):
    super().setUp()
    self.params = MemoryParams({'IsOffroad': True})
    self.manager.params = self.params
    self.manager.source_models = {'chestnut': [], 'qcom': []}  # Repair ordering must not follow this order.
    self.manager._download_ref = None
    self.manager._repair_context = None
    self.manager._repair_retry_at = {}
    self.originals = {}
    self.saved = {}
    self.targets = {}
    self.progress = []
    self.on_progress = lambda: None
    self.manager.pm.send.side_effect = self.record_progress
    self.enterContext(mock.patch.object(manager_module.Paths, 'model_root', return_value=self.dest))

  def record_progress(self, *_args):
    selected = self.manager.selected_bundle
    if selected is not None:
      self.progress.append((self.params.get('ModelManager_DownloadRef'), selected.to_dict()))
    self.on_progress()

  def seed(self, source='qcom'):
    target = repair_bundle(source)
    saved = repair_bundle(source, compiler='')
    saved.minimumSelectorVersion = 19
    for model in saved.models:
      artifact = model.artifact
      bodies = [f'old-{artifact.fileName}-{i}'.encode() for i in range(len(CHUNK_BODIES))]
      artifact.downloadUri.sha256 = sha256(b''.join(bodies))
      path = Path(self.dest) / artifact.fileName
      self.originals[path] = b''.join(bodies)
      self.originals[Path(get_manifest_path(str(path)))] = str(len(bodies)).encode()
      for i, body in enumerate(bodies):
        artifact.chunks[i].sha256 = sha256(body)
        self.originals[Path(get_chunk_name(str(path), i, len(bodies)))] = body
    for path, body in self.originals.items():
      path.write_bytes(body)
    self.saved[source] = saved.to_dict()
    self.params.values[helpers.ACTIVE_BUNDLE_KEYS[source]] = saved.to_dict()
    self.targets[source] = target
    self.manager.source_models[source] = [target]
    if source == 'qcom':
      self.manager.active_bundle = saved
    return target

  @contextmanager
  def server(self):
    # Candidate admission sees HTTPS. Only the transport is redirected; real
    # requests, HTTP errors, chunk iteration and hashing remain production code.
    original_request = requests.sessions.Session.request
    with http_server_context(handler=DownloadHandler) as (host, port):
      def local_request(session, method, url, *args, **kwargs):
        assert url.startswith(CATALOG_ORIGIN + '/'), url
        url = f'http://{host}:{port}' + url[len(CATALOG_ORIGIN):]
        return original_request(session, method, url, *args, **kwargs)
      with mock.patch.object(requests.sessions.Session, 'request', local_request):
        yield

  def assert_originals_retained(self):
    for path, body in self.originals.items():
      assert path.read_bytes() == body, path

  def selection_writes(self):
    return [(key, value) for key, value in self.params.writes if key in helpers.ACTIVE_BUNDLE_KEYS.values()]

  def assert_repair_token(self, token, source='qcom'):
    prefix = f"nrdr-repair:{source}:{self.saved[source]['ref']}:"
    assert isinstance(token, str) and token.startswith(prefix), token
    UUID(token[len(prefix):])

  def assert_not_committed(self, source='qcom'):
    assert self.params.get(helpers.ACTIVE_BUNDLE_KEYS[source]) == self.saved[source]
    assert self.selection_writes() == []
    assert self.manager.active_bundle.to_dict() == self.saved['qcom']
    self.assert_originals_retained()

  def cache_target(self, source='qcom'):
    for model in self.targets[source].models:
      artifact = model.artifact
      path = Path(self.dest) / f'nrdr-{source}-{artifact.downloadUri.sha256}-{artifact.fileName}'
      for i, body in enumerate(CHUNK_BODIES):
        Path(get_chunk_name(str(path), i, len(CHUNK_BODIES))).write_bytes(body)

  def test_both_slots_commit_only_after_all_artifacts_are_verified(self):
    self.seed('qcom')
    self.seed('chestnut')
    catalog_before = {source: target.to_dict() for source, target in self.targets.items()}
    processed = []
    tokens = {}
    original_process = self.manager._process_artifact

    async def process(artifact, destination):
      source = 'chestnut' if artifact.fileName.startswith('nrdr-chestnut-') else 'qcom'
      key = helpers.ACTIVE_BUNDLE_KEYS[source]
      assert self.params.get(key) == self.saved[source]
      token = self.params.get('ModelManager_DownloadRef')
      assert token == self.manager._download_ref
      self.assert_repair_token(token, source)
      assert tokens.setdefault(source, token) == token
      await original_process(artifact, destination)
      assert self.params.get(key) == self.saved[source]
      with open_file_chunked(str(Path(destination) / artifact.fileName)) as stream:
        assert sha256(stream.read()) == artifact.downloadUri.sha256
      processed.append(source)

    with self.server(), mock.patch.object(self.manager, '_process_artifact', side_effect=process):
      self.manager._repair_saved_bundles()
    assert processed == ['qcom', 'qcom', 'chestnut', 'chestnut']
    assert [key for key, _ in self.selection_writes()] == list(helpers.ACTIVE_BUNDLE_KEYS.values())
    for source, target in self.targets.items():
      installed = self.params.get(helpers.ACTIVE_BUNDLE_KEYS[source])
      for field in ('ref', 'internalName', 'displayName'):
        assert installed[field] == self.saved[source][field]
      assert installed['tinygradRef'] == TINYGRAD_RUNTIME_REF
      assert installed['onnxSha256'] == target.onnxSha256
      for model, expected in zip(installed['models'], target.models, strict=True):
        artifact = model['artifact']
        assert artifact['fileName'] == f'nrdr-{source}-{expected.artifact.downloadUri.sha256}-{expected.artifact.fileName}'
        assert Path(artifact['fileName']).name == artifact['fileName']
      assert not helpers._bundle_needs_reset(custom.ModelManagerSP.ModelBundle(**installed), [target])
      assert target.to_dict() == catalog_before[source]
    assert len(DownloadHandler.request_paths) == 12
    assert len(set(tokens.values())) == 2
    assert self.progress and all(ref in tokens.values() for ref, _ in self.progress)
    assert any(any(model['artifact'].get('downloadProgress', {}).get('status') == 'downloading'
                   for model in bundle['models']) for _, bundle in self.progress)
    assert self.params.get('ModelManager_DownloadRef') is None
    assert self.manager.selected_bundle is None
    assert self.manager._repair_context is None
    self.assert_originals_retained()

  def test_http_failure_retains_selection_files_and_backs_off_for_60_seconds(self):
    self.seed()
    path = get_chunk_name('/qcom/policy_test_tinygrad.pkl', 1, len(CHUNK_BODIES))
    DownloadHandler.fail_paths[path] = 503
    with self.server(), mock.patch.object(manager_module, 'time', SimpleNamespace(monotonic=lambda: 1000.0)):
      self.manager._repair_saved_bundles()
    self.assert_not_committed()
    requests_before = list(DownloadHandler.request_paths)
    assert requests_before
    with self.server(), mock.patch.object(manager_module, 'time', SimpleNamespace(monotonic=lambda: 1059.999)):
      self.manager._repair_saved_bundles()
    assert DownloadHandler.request_paths == requests_before
    DownloadHandler.fail_paths.clear()
    with self.server(), mock.patch.object(manager_module, 'time', SimpleNamespace(monotonic=lambda: 1060.0)):
      self.manager._repair_saved_bundles()
    assert len(self.selection_writes()) == 1
    assert len(DownloadHandler.request_paths) > len(requests_before)
    self.assert_originals_retained()

  def test_full_artifact_hash_is_checked_even_when_every_chunk_hash_matches(self):
    for cached in (False, True):
      with self.subTest(cached=cached):
        self.seed()
        self.manager._repair_retry_at.clear()
        self.targets['qcom'].models[-1].artifact.downloadUri.sha256 = 'f' * 64
        if cached:
          self.cache_target()
        DownloadHandler.request_paths.clear()
        with self.server():
          self.manager._repair_saved_bundles()
        self.assert_not_committed()
        assert bool(DownloadHandler.request_paths) is not cached

  def test_bad_downloaded_chunk_hash_retains_the_entire_old_bundle(self):
    target = self.seed()
    target.models[-1].artifact.chunks[-1].sha256 = '0' * 64
    with self.server():
      self.manager._repair_saved_bundles()
    assert len(DownloadHandler.request_paths) == 6
    self.assert_not_committed()

  def test_verified_cached_repair_and_repeated_current_bundle_are_network_noops(self):
    self.seed()
    self.cache_target()
    with self.server():
      self.manager._repair_saved_bundles()
      self.manager._repair_retry_at.clear()
      self.manager._repair_saved_bundles()
    assert DownloadHandler.request_paths == []
    assert len(self.selection_writes()) == 1
    self.assert_originals_retained()

  def test_other_source_catalog_cannot_repair_a_saved_slot(self):
    target = self.seed()
    self.manager.source_models = {'qcom': [], 'chestnut': [target]}
    with self.server():
      self.manager._repair_saved_bundles()
    self.assert_not_committed()
    assert DownloadHandler.request_paths == []

  def test_offroad_and_no_explicit_request_are_required_before_starting(self):
    self.seed()
    for offroad, pending in ((False, None), (True, 'user-pick'), (True, b'user-pick'), (True, '')):
      with self.subTest(offroad=offroad, pending=pending):
        self.params.values['IsOffroad'] = offroad
        self.params.values['ModelManager_DownloadRef'] = pending
        with self.server():
          self.manager._repair_saved_bundles()
        self.assert_not_committed()
        assert self.params.get('ModelManager_DownloadRef') == pending
    assert DownloadHandler.request_paths == []

  def test_cancel_onroad_selection_and_queued_ref_changes_interrupt_download(self):
    for interrupt in ('cancel', 'onroad', 'selection', 'queued-ref'):
      with self.subTest(interrupt=interrupt):
        self.seed()
        self.manager._repair_retry_at.clear()
        self.params.values['IsOffroad'] = True
        self.params.remove('ModelManager_DownloadRef')
        triggered = []

        def change(interrupt=interrupt, triggered=triggered):
          selected = self.manager.selected_bundle
          if triggered or selected is None:
            return
          if not any(str(model.artifact.downloadProgress.status) == 'downloading' and model.artifact.downloadProgress.progress > 0
                     for model in selected.models):
            return
          triggered.append(True)
          if interrupt == 'cancel':
            self.params.remove('ModelManager_DownloadRef')
          elif interrupt == 'onroad':
            self.params.values['IsOffroad'] = False
          elif interrupt == 'queued-ref':
            self.params.values['ModelManager_DownloadRef'] = 'user-pick'
          else:
            # Same ref, changed raw metadata: comparing only refs is not sufficient.
            self.params.values[helpers.ACTIVE_BUNDLE_KEYS['qcom']]['displayName'] = 'User selection wins'

        self.on_progress = change
        with self.server():
          self.manager._repair_saved_bundles()
        assert triggered
        assert self.selection_writes() == []
        expected = copy.deepcopy(self.saved['qcom'])
        if interrupt == 'selection':
          expected['displayName'] = 'User selection wins'
        assert self.params.get(helpers.ACTIVE_BUNDLE_KEYS['qcom']) == expected
        assert self.manager.active_bundle.to_dict() == self.saved['qcom']
        assert self.params.get('ModelManager_DownloadRef') == ('user-pick' if interrupt == 'queued-ref' else None)
        self.assert_originals_retained()

  def assert_backoff_after_long_attempt(self, failure):
    self.seed()
    DownloadHandler.fail_paths = ({get_chunk_name('/qcom/driving_test_tinygrad.pkl', 1, len(CHUNK_BODIES)): 503}
                                  if failure == 'http' else {})
    now = [1000.0]
    triggered = []

    def delayed_failure():
      selected = self.manager.selected_bundle
      if triggered or selected is None:
        return
      if any(str(model.artifact.downloadProgress.status) == 'downloading' and model.artifact.downloadProgress.progress > 0
             for model in selected.models):
        triggered.append(True)
        now[0] = 1090.0  # Transfer lasted longer than the retry interval.
        if failure == 'cancel':
          self.params.remove('ModelManager_DownloadRef')

    self.on_progress = delayed_failure
    with self.server(), mock.patch.object(manager_module, 'time', SimpleNamespace(monotonic=lambda: now[0])):
      self.manager._repair_saved_bundles()
      assert triggered
      self.assert_not_committed()
      assert self.manager._repair_retry_at['qcom'] == 1150.0
      requests_before = list(DownloadHandler.request_paths)
      self.on_progress = lambda: None
      DownloadHandler.fail_paths.clear()
      now[0] = 1149.999
      self.manager._repair_saved_bundles()
      assert DownloadHandler.request_paths == requests_before
      now[0] = 1150.0
      self.manager._repair_saved_bundles()
    assert len(self.selection_writes()) == 1
    tokens = [value for key, value in self.params.writes if key == 'ModelManager_DownloadRef']
    assert len(tokens) == 2 and tokens[0] != tokens[1]
    for token in tokens:
      self.assert_repair_token(token)
    self.assert_originals_retained()

  def test_backoff_starts_after_a_long_http_failure_finishes(self):
    self.assert_backoff_after_long_attempt('http')

  def test_backoff_starts_after_a_long_cancelled_attempt_finishes(self):
    self.assert_backoff_after_long_attempt('cancel')

  def test_failed_manual_canonical_download_cannot_remove_repaired_files_in_either_slot(self):
    self.seed('qcom')
    self.seed('chestnut')
    with self.server():
      self.manager._repair_saved_bundles()
    installed = {key: self.params.get(key) for key in helpers.ACTIVE_BUNDLE_KEYS.values()}
    private_files = {path: path.read_bytes() for path in Path(self.dest).iterdir() if path.name.startswith('nrdr-')}
    assert any(path.name.startswith('nrdr-qcom-') for path in private_files)
    assert any(path.name.startswith('nrdr-chestnut-') for path in private_files)
    self.params.writes.clear()
    # Both repair fixtures deliberately share a ref; make this explicit manual
    # request resolve only to qcom, independently of catalog insertion order.
    self.manager.source_models = {'qcom': [self.targets['qcom']]}
    DownloadHandler.request_paths.clear()
    failing_path = get_chunk_name('/qcom/driving_test_tinygrad.pkl', 1, len(CHUNK_BODIES))
    DownloadHandler.fail_paths[failing_path] = 503
    self.params.put('ModelManager_DownloadRef', self.targets['qcom'].ref)
    with self.server():
      self.manager._process_download_requests()
    assert failing_path in DownloadHandler.request_paths
    assert self.selection_writes() == []
    for key, raw in installed.items():
      assert self.params.get(key) == raw
    for path, body in private_files.items():
      assert path.read_bytes() == body, f'Manual download cleanup removed another artifact: {path}'

  def test_selection_and_offroad_are_rechecked_after_final_full_hash_verification(self):
    for interrupt in ('selection', 'onroad', 'queued-ref', 'cancel'):
      with self.subTest(interrupt=interrupt):
        self.seed()
        self.manager._repair_retry_at.clear()
        self.params.values['IsOffroad'] = True
        self.params.remove('ModelManager_DownloadRef')
        self.cache_target()
        verified = []
        original_verify = manager_module.verify_file

        async def verify(path, expected, interrupt=interrupt, verified=verified, original_verify=original_verify):
          result = await original_verify(path, expected)
          if path.endswith('.pkl') and result:
            verified.append(path)
            if len(verified) == len(self.targets['qcom'].models):
              if interrupt == 'selection':
                self.params.values[helpers.ACTIVE_BUNDLE_KEYS['qcom']]['displayName'] = 'User selection wins'
              elif interrupt == 'onroad':
                self.params.values['IsOffroad'] = False
              elif interrupt == 'queued-ref':
                self.params.values['ModelManager_DownloadRef'] = 'user-pick'
              else:
                self.params.remove('ModelManager_DownloadRef')
          return result

        with self.server(), mock.patch.object(manager_module, 'verify_file', side_effect=verify):
          self.manager._repair_saved_bundles()
        assert len(verified) == 2
        assert self.selection_writes() == []
        expected = copy.deepcopy(self.saved['qcom'])
        if interrupt == 'selection':
          expected['displayName'] = 'User selection wins'
        assert self.params.get(helpers.ACTIVE_BUNDLE_KEYS['qcom']) == expected
        assert self.manager.active_bundle.to_dict() == self.saved['qcom']
        assert self.params.get('ModelManager_DownloadRef') == ('user-pick' if interrupt == 'queued-ref' else None)
        self.assert_originals_retained()

  def test_conditional_claim_and_activation_guard_all_three_user_inputs(self):
    key = helpers.ACTIVE_BUNDLE_KEYS['qcom']
    for stage in ('claim', 'activation'):
      for guard in ('IsOffroad', 'ModelManager_DownloadRef', key):
        with self.subTest(stage=stage, guard=guard):
          self.seed()
          self.cache_target()
          self.manager._repair_retry_at.clear()
          self.params.values['IsOffroad'] = True
          self.params.remove('ModelManager_DownloadRef')
          triggered = []
          original_update = self.manager._conditional_param_update
          changed = (False if guard == 'IsOffroad' else 'user-ref' if guard == 'ModelManager_DownloadRef'
                     else dict(self.saved['qcom'], displayName='User selection wins'))

          def update(destination, value, expected, stage=stage, guard=guard, triggered=triggered,
                     changed=changed, original_update=original_update):
            at_boundary = value is not None and destination == ('ModelManager_DownloadRef' if stage == 'claim' else key)
            if at_boundary and not triggered:
              assert expected == {'IsOffroad': True, 'ModelManager_DownloadRef': None if stage == 'claim' else self.manager._download_ref,
                                  key: self.saved['qcom']}
              triggered.append(True)
              self.params.values[guard] = copy.deepcopy(changed)
            return original_update(destination, value, expected)

          with self.server(), mock.patch.object(self.manager, '_conditional_param_update', side_effect=update):
            self.manager._repair_saved_bundles()
          assert triggered
          assert self.selection_writes() == []
          assert self.params.get(guard) == changed
          assert self.params.get(key) == (changed if guard == key else self.saved['qcom'])
          assert self.manager.active_bundle.to_dict() == self.saved['qcom']
          self.assert_originals_retained()

  def assert_repair_locals_cleared(self):
    assert self.manager._download_ref is None
    assert self.manager._repair_context is None
    assert self.manager.selected_bundle is None

  def test_claim_commits_then_raises_without_starting_a_download_or_losing_ownership(self):
    self.seed()
    original_update = self.manager._conditional_param_update
    claimed = []

    def update(key, value, expected):
      result = original_update(key, value, expected)
      if key == 'ModelManager_DownloadRef' and value is not None and result:
        self.assert_repair_token(value)
        assert self.manager._download_ref == value
        assert self.manager._repair_context == (helpers.ACTIVE_BUNDLE_KEYS['qcom'], self.saved['qcom'])
        claimed.append(value)
        raise OSError('Injected directory fsync failure after claim rename')
      return result

    with mock.patch.object(self.manager, '_conditional_param_update', side_effect=update), \
         mock.patch.object(self.manager, '_repair_bundle') as repair:
      self.manager._repair_saved_bundles()
    assert len(claimed) == 1
    repair.assert_not_called()
    assert self.params.get('ModelManager_DownloadRef') is None
    self.assert_repair_locals_cleared()
    self.assert_not_committed()

  def test_release_failure_clears_locals_and_orphan_is_never_processed_as_a_manual_request(self):
    self.seed()
    original_update = self.manager._conditional_param_update
    release_error = OSError('Injected release failure')
    attempted_releases = []

    def update(key, value, expected):
      if key == 'ModelManager_DownloadRef' and value is None:
        attempted_releases.append(expected['ModelManager_DownloadRef'])
        raise release_error
      return original_update(key, value, expected)

    with mock.patch.object(self.manager, '_conditional_param_update', side_effect=update), \
         mock.patch.object(self.manager, '_process_artifact', side_effect=manager_module.DownloadCancelled('cancelled')):
      try:
        self.manager._repair_saved_bundles()
      except OSError as error:
        assert error is release_error
    orphan = self.params.get('ModelManager_DownloadRef')
    self.assert_repair_token(orphan)
    assert attempted_releases == [orphan]
    self.assert_repair_locals_cleared()
    self.assert_not_committed()
    with mock.patch.object(manager_module, 'resolve_bundle_by_ref', side_effect=AssertionError('orphan reached manual resolution')) as resolve, \
         mock.patch.object(self.manager, 'download', side_effect=AssertionError('orphan started a manual download')) as download:
      self.manager._process_download_requests()
    resolve.assert_not_called()
    download.assert_not_called()
    assert self.params.get('ModelManager_DownloadRef') is None
    self.assert_repair_locals_cleared()
    self.assert_not_committed()

  def test_orphan_cleanup_compare_and_swap_cannot_delete_a_new_manual_request(self):
    self.seed()
    orphan = f"nrdr-repair:qcom:{self.saved['qcom']['ref']}:00000000000040008000000000000001"
    self.params.put('ModelManager_DownloadRef', orphan)
    original_update = self.manager._conditional_param_update
    replacements = []

    def update(key, value, expected):
      assert key == 'ModelManager_DownloadRef' and value is None
      assert expected == {'ModelManager_DownloadRef': orphan}
      replacements.append(True)
      self.params.put('ModelManager_DownloadRef', self.saved['qcom']['ref'])
      return original_update(key, value, expected)

    with mock.patch.object(self.manager, '_conditional_param_update', side_effect=update), \
         mock.patch.object(self.manager, 'download') as download:
      self.manager._process_download_requests()
    assert replacements == [True]
    download.assert_not_called()
    assert self.params.get('ModelManager_DownloadRef') == self.saved['qcom']['ref']
    self.assert_not_committed()

  def test_user_default_then_same_ref_reselection_cancels_repair_and_survives_release(self):
    self.seed()
    key = helpers.ACTIVE_BUNDLE_KEYS['qcom']
    original_ref = self.saved['qcom']['ref']
    reselected = []

    def choose_default_then_same_model():
      selected = self.manager.selected_bundle
      if reselected or selected is None:
        return
      if not any(str(model.artifact.downloadProgress.status) == 'downloading' and model.artifact.downloadProgress.progress > 0
                 for model in selected.models):
        return
      self.assert_repair_token(self.params.get('ModelManager_DownloadRef'))
      self.params.remove(key)  # User chooses Default, cancelling the old saved selection.
      self.params.remove('ModelManager_DownloadRef')
      self.params.put('ModelManager_DownloadRef', original_ref)  # Then explicitly reselects exactly the same model.
      reselected.append(True)

    self.on_progress = choose_default_then_same_model
    with self.server():
      self.manager._repair_saved_bundles()
    assert reselected == [True]
    assert self.params.get(key) is None
    assert self.params.get('ModelManager_DownloadRef') == original_ref
    assert self.selection_writes() == []
    assert self.manager.active_bundle.to_dict() == self.saved['qcom']
    self.assert_repair_locals_cleared()
    self.assert_originals_retained()


class TestConditionalModelParams(ManagerDownloadTestBase):
  """Real native Params, private temporary root, no device/global Params writes."""
  def setUp(self):
    super().setUp()
    del self.manager._conditional_param_update  # Exercise production flock/atomic replace, not the memory adapter.
    self.root = str(Path(self.dest) / 'params')
    self.params = Params(self.root)
    self.writer = Params(self.root)
    self.manager.params = self.params
    self.key = helpers.ACTIVE_BUNDLE_KEYS['qcom']
    self.saved = repair_bundle(compiler='').to_dict()
    self.current = repair_bundle().to_dict()
    self.params.put_bool('IsOffroad', True, block=True)
    self.params.put(self.key, self.saved, block=True)
    self.params.put('ModelManager_DownloadRef', 'repair-ref', block=True)
    self.expected = {'IsOffroad': True, 'ModelManager_DownloadRef': 'repair-ref', self.key: self.saved}

  def assert_no_temporary_writes(self):
    assert not list(Path(self.root).glob('.tmp_model_upgrade_*'))

  def test_claim_activation_and_release_use_native_types_and_preserve_other_slot(self):
    other_key = helpers.ACTIVE_BUNDLE_KEYS['chestnut']
    other = repair_bundle('chestnut', compiler='unrelated-compiler').to_dict()
    self.params.put(other_key, other, block=True)
    self.params.remove('ModelManager_DownloadRef')
    claim = dict(self.expected, ModelManager_DownloadRef=None)
    assert self.manager._conditional_param_update('ModelManager_DownloadRef', 'repair-ref', claim)
    assert self.params.get('ModelManager_DownloadRef') == 'repair-ref'
    assert self.manager._conditional_param_update(self.key, self.current, self.expected)
    assert self.params.get(self.key) == self.current
    assert self.params.get(other_key) == other
    self.writer.put('ModelManager_DownloadRef', 'user-ref', block=True)
    assert not self.manager._conditional_param_update('ModelManager_DownloadRef', None, {'ModelManager_DownloadRef': 'repair-ref'})
    assert self.params.get('ModelManager_DownloadRef') == 'user-ref'
    assert self.manager._conditional_param_update('ModelManager_DownloadRef', None, {'ModelManager_DownloadRef': 'user-ref'})
    assert self.params.get_raw('ModelManager_DownloadRef') is None
    self.assert_no_temporary_writes()

  def test_empty_queued_ref_is_not_absent_and_cannot_be_claimed(self):
    self.writer.put('ModelManager_DownloadRef', '', block=True)
    assert self.params.get_raw('ModelManager_DownloadRef') == b''
    assert not self.manager._conditional_param_update('ModelManager_DownloadRef', 'repair-ref',
                                                     dict(self.expected, ModelManager_DownloadRef=None))
    assert self.params.get_raw('ModelManager_DownloadRef') == b''
    assert self.params.get(self.key) == self.saved
    self.assert_no_temporary_writes()

  def test_native_claim_directory_sync_failure_releases_the_already_renamed_token(self):
    import os
    import stat
    self.params.remove('ModelManager_DownloadRef')
    self.manager.source_models = {'qcom': [repair_bundle()], 'chestnut': []}
    original_fsync = os.fsync
    claimed = []

    def fail_first_directory_sync(fd):
      if stat.S_ISDIR(os.fstat(fd).st_mode) and not claimed:
        # The value rename has succeeded; the directory durability step fails.
        # Native Params must see the token even though the claim call raises.
        token = self.params.get('ModelManager_DownloadRef')
        prefix = f"nrdr-repair:qcom:{self.saved['ref']}:"
        assert token.startswith(prefix)
        UUID(token[len(prefix):])
        assert self.manager._download_ref == token
        assert self.manager._repair_context == (self.key, self.saved)
        claimed.append(token)
        raise OSError('Injected post-rename directory sync failure')
      return original_fsync(fd)

    with mock.patch.object(manager_module.os, 'fsync', side_effect=fail_first_directory_sync), \
         mock.patch.object(self.manager, '_repair_bundle') as repair:
      self.manager._repair_saved_bundles()
    assert len(claimed) == 1
    repair.assert_not_called()
    assert self.params.get_raw('ModelManager_DownloadRef') is None
    assert self.params.get(self.key) == self.saved
    assert self.manager._download_ref is None
    assert self.manager._repair_context is None
    assert self.manager.selected_bundle is None
    self.assert_no_temporary_writes()

  def test_every_guard_is_compared_after_acquiring_the_native_lock(self):
    import fcntl
    original_flock = fcntl.flock
    for guard, value in (('IsOffroad', False), ('ModelManager_DownloadRef', 'user-ref'),
                         (self.key, dict(self.saved, displayName='User selection wins'))):
      with self.subTest(guard=guard):
        for key, old in self.expected.items():
          self.params.put(key, old, block=True)
        reached_lock, proceed, done = threading.Event(), threading.Event(), threading.Event()
        result, errors = [], []

        def paused_lock(fd, operation, reached_lock=reached_lock, proceed=proceed):
          reached_lock.set()
          if not proceed.wait(5):
            raise TimeoutError('Test did not release the conditional update')
          return original_flock(fd, operation)

        def activate(result=result, errors=errors, done=done):
          try:
            result.append(self.manager._conditional_param_update(self.key, self.current, self.expected))
          except Exception as error:
            errors.append(error)
          finally:
            done.set()

        worker = threading.Thread(target=activate, daemon=True)
        with mock.patch.object(fcntl, 'flock', side_effect=paused_lock):
          worker.start()
          try:
            assert reached_lock.wait(5), 'Repair never attempted to acquire the native lock'
            # This is a real C++ Params writer while the repair is paused just
            # before flock. Checking guards before acquiring it would lose this write.
            self.writer.put(guard, value, block=True)
          finally:
            proceed.set()
            worker.join(timeout=5)
        assert done.is_set() and not worker.is_alive(), 'Conditional update deadlocked'
        assert not errors, errors
        assert result == [False]
        assert self.params.get(guard) == value
        assert self.params.get(self.key) == (value if guard == self.key else self.saved)
        self.assert_no_temporary_writes()

  def test_native_writer_waits_through_guard_comparison_and_atomic_replace(self):
    import fcntl
    comparing, proceed, repaired = threading.Event(), threading.Event(), threading.Event()
    writer_started, writer_done = threading.Event(), threading.Event()
    results, errors = [], []
    original_get_raw = self.params.get_raw

    def paused_read(key):
      if key == 'IsOffroad':
        # Assert the root lock (not a lock inside the symlinked key directory)
        # is held during guard reads, matching native Params::put/remove.
        with (Path(self.params.get_param_path()).parent / '.lock').open('rb') as lock:
          with self.assertRaises(BlockingIOError):
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        comparing.set()
        if not proceed.wait(5):
          raise TimeoutError('Test did not release guard comparison')
      return original_get_raw(key)

    def activate():
      try:
        results.append(self.manager._conditional_param_update(self.key, self.current, self.expected))
      except Exception as error:
        errors.append(error)
      finally:
        repaired.set()

    def write_user_selection():
      try:
        writer_started.set()
        self.writer.put('ModelManager_DownloadRef', 'user-ref', block=True)
      except Exception as error:
        errors.append(error)
      finally:
        writer_done.set()

    repair_thread = threading.Thread(target=activate, daemon=True)
    writer_thread = threading.Thread(target=write_user_selection, daemon=True)
    with mock.patch.object(self.params, 'get_raw', side_effect=paused_read):
      repair_thread.start()
      try:
        assert comparing.wait(5), 'Repair did not reach locked guard comparison'
        writer_thread.start()
        assert writer_started.wait(5)
        assert not writer_done.wait(0.1), 'Native writer bypassed the repair lock'
      finally:
        proceed.set()
        repair_thread.join(timeout=5)
        if writer_thread.ident is not None:
          writer_thread.join(timeout=5)
    assert repaired.is_set() and writer_done.is_set(), 'Native Params update deadlocked'
    assert not repair_thread.is_alive() and not writer_thread.is_alive()
    assert not errors, errors
    assert results == [True]
    assert self.params.get(self.key) == self.current
    assert self.params.get('ModelManager_DownloadRef') == 'user-ref'
    self.assert_no_temporary_writes()


class TestCompilerCacheRefresh(unittest.TestCase):
  def make_fetcher(self, compiler=None, *, source='qcom'):
    raw = manifest_bundle('saved', 'saved-ref', is_big=source == 'chestnut')
    raw['minimum_selector_version'] = '19'
    if compiler is None:
      raw.pop('tinygrad_ref')
    else:
      raw['tinygrad_ref'] = compiler
    params = MemoryParams()
    fetcher = ModelFetcher(params)
    fetcher.model_caches[source].set({'bundles': [raw]})
    return fetcher, raw

  def test_selector19_missing_or_old_qcom_compiler_forces_refresh(self):
    for compiler in (None, '', '62bf6fb072880905a4c490f0f4f4a6b3c23346ec'):
      with self.subTest(compiler=compiler):
        fetcher, raw = self.make_fetcher(compiler)
        assert ModelParser.parse_models({'bundles': [raw]})  # Accepted selector version is not compiler admission.
        fresh = [repair_bundle()]
        with mock.patch.object(fetcher, '_fetch_and_cache_models', return_value=fresh) as fetch:
          assert fetcher.get_bundles_for_source('qcom') == fresh
        fetch.assert_called_once_with('qcom')

  def test_current_qcom_and_unrelated_chestnut_compiler_do_not_refetch(self):
    for source, compiler in (('qcom', TINYGRAD_RUNTIME_REF), ('chestnut', 'other-chestnut-compiler')):
      fetcher, _ = self.make_fetcher(compiler, source=source)
      with mock.patch.object(fetcher, '_fetch_and_cache_models', side_effect=AssertionError('unexpected fetch')):
        assert [bundle.ref for bundle in fetcher.get_bundles_for_source(source)] == ['saved-ref']

  def test_old_qcom_fallback_refetch_is_rate_limited_for_60_seconds(self):
    with mock.patch.object(fetcher_module, 'time', SimpleNamespace(monotonic=lambda: 1000.0)):
      fetcher, _ = self.make_fetcher()
      with mock.patch.object(fetcher, '_fetch_and_cache_models', return_value=None) as fetch:
        assert fetcher.get_bundles_for_source('qcom')[0].ref == 'saved-ref'
        assert fetcher.get_bundles_for_source('qcom')[0].ref == 'saved-ref'
        assert fetch.call_count == 1
    with mock.patch.object(fetcher_module, 'time', SimpleNamespace(monotonic=lambda: 1059.999)), \
         mock.patch.object(fetcher, '_fetch_and_cache_models', return_value=None) as fetch:
      assert fetcher.get_bundles_for_source('qcom')[0].ref == 'saved-ref'
      fetch.assert_not_called()
    with mock.patch.object(fetcher_module, 'time', SimpleNamespace(monotonic=lambda: 1060.0)), \
         mock.patch.object(fetcher, '_fetch_and_cache_models', return_value=None) as fetch:
      assert fetcher.get_bundles_for_source('qcom')[0].ref == 'saved-ref'
      fetch.assert_called_once_with('qcom')
