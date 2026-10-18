import ast
from pathlib import Path
from types import SimpleNamespace
import unittest

from openpilot.nrdr.features.services import TINYGRAD_RUNTIME_REF
from openpilot.nrdr.features.services.model_manager import select_default_model


class FakeParams:
  def __init__(self, *, enabled=True, download_ref=None):
    self.values = {"NrdrAutoSelectModel": enabled}
    if download_ref is not None:
      self.values["ModelManager_DownloadRef"] = download_ref

  def get_bool(self, key):
    return bool(self.values.get(key, False))

  def get(self, key):
    return self.values.get(key)

  def put(self, key, value):
    self.values[key] = value

  def put_bool(self, key, value):
    self.values[key] = value

  def remove(self, key):
    self.values.pop(key, None)


def bundle(index, display_name, ref, *, compiler=TINYGRAD_RUNTIME_REF):
  return SimpleNamespace(index=index, displayName=display_name, ref=ref, tinygradRef=compiler, runner="tinygrad",
                         models=[SimpleNamespace(artifact=SimpleNamespace(fileName="driving.pkl", downloadUri=SimpleNamespace(
                           uri="https://example.invalid/driving.pkl", sha256="a" * 64)))])


class TestSelectDefaultModel(unittest.TestCase):
  def test_selects_latest_pop_v2_by_download_ref(self):
    params = FakeParams()
    available = (
      bundle(7, "Pop Model v2", "pop-v2-old"),
      bundle(11, "Pop Model v2", "pop-v2-new"),
      bundle(12, "Different Model", "different"),
    )

    select_default_model(params, available)

    self.assertEqual(params.get("ModelManager_DownloadRef"), "pop-v2-new")
    self.assertFalse(params.get_bool("NrdrAutoSelectModel"))

  def test_pending_download_is_never_replaced(self):
    for pending in ("already-pending", "explicit-legacy-pick", b"queued-pick", ""):
      with self.subTest(pending=pending):
        params = FakeParams(download_ref=pending)
        before = dict(params.values)
        select_default_model(params, (bundle(11, "Pop Model v2", "pop-v2"),))
        self.assertEqual(params.values, before)

  def test_legacy_pop_catalog_leaves_first_run_request_pending(self):
    # PMV2/index59 is a valid selector-v19 pick, but its old compiler artifact
    # needs a separately verified migration. A fresh install has no such record.
    for compiler in (None, "", "old-compiler", "62bf6fb072880905a4c490f0f4f4a6b3c23346ec"):
      with self.subTest(compiler=compiler):
        params = FakeParams()
        before = dict(params.values)
        select_default_model(params, (bundle(59, "Pop Model v2 (March 24, 2026)", "legacy-pop", compiler=compiler),))
        self.assertEqual(params.values, before)

  def test_newest_compatible_pop_wins_not_newest_name_match(self):
    params = FakeParams()
    available = [bundle(70, "Pop Model v2", "older-compatible"),
                 bundle(75, "Pop Model v2", "compatible"),
                 bundle(100, "Pop Model v2", "legacy", compiler=""),
                 bundle(101, "Pop Model v2", "other-compiler", compiler="other-runtime"),
                 bundle(102, "Other Model", "not-pop")]
    select_default_model(params, available)
    self.assertEqual(params.get("ModelManager_DownloadRef"), "compatible")
    self.assertFalse(params.get_bool("NrdrAutoSelectModel"))

  def test_compiler_ref_alone_cannot_queue_an_unusable_download(self):
    for defect in ("runner", "models", "file", "onnx-not-compiled", "uri", "hash"):
      with self.subTest(defect=defect):
        pick = bundle(59, "Pop Model v2", "pop")
        if defect == "runner":
          pick.runner = "snpe"
        elif defect == "models":
          pick.models = []
        elif defect == "file":
          pick.models[0].artifact.fileName = ""
        elif defect == "onnx-not-compiled":
          pick.models[0].artifact.fileName = "driving.onnx"
        elif defect == "uri":
          pick.models[0].artifact.downloadUri.uri = ""
        else:
          pick.models[0].artifact.downloadUri.sha256 = "not-a-sha256"
        params = FakeParams()
        before = dict(params.values)
        select_default_model(params, (pick,))
        self.assertEqual(params.values, before)

  def test_waiting_request_can_queue_when_a_compatible_build_appears(self):
    params = FakeParams()
    legacy = bundle(59, "Pop Model v2", "legacy", compiler="")
    select_default_model(params, (legacy,))
    self.assertTrue(params.get_bool("NrdrAutoSelectModel"))
    self.assertIsNone(params.get("ModelManager_DownloadRef"))
    select_default_model(params, (legacy, bundle(60, "Pop Model v2", "compatible")))
    self.assertEqual(params.get("ModelManager_DownloadRef"), "compatible")
    self.assertFalse(params.get_bool("NrdrAutoSelectModel"))

  def test_saved_selection_is_never_replaced_by_first_run_request(self):
    for key in ("ModelManager_ActiveBundle", "ModelManager_ActiveBundleChestnut"):
      for selection in ({"ref": "saved-legacy-model"}, b"malformed-but-retained"):
        with self.subTest(slot=key, selection=selection):
          params = FakeParams()
          params.values[key] = selection
          select_default_model(params, (bundle(11, "Pop Model v2", "new-pop"),))
          self.assertIsNone(params.get("ModelManager_DownloadRef"))
          self.assertEqual(params.get(key), selection)
          self.assertTrue(params.get_bool("NrdrAutoSelectModel"))

  def test_manager_tick_calls_selection_hook_before_processing_downloads(self):
    # Run the actual host loop with pure boundaries and stop after one tick.
    source = Path(__file__).resolve().parents[3] / "openpilot/sunnypilot/models/manager.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "ModelManagerSP")
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "main_thread")

    class TickComplete(BaseException):
      pass

    def stop():
      raise TickComplete

    params = FakeParams()
    available = [bundle(11, "Pop Model v2", "new-pop")]
    processed = []
    manager = SimpleNamespace(
      params=params, sm=SimpleNamespace(update=lambda timeout: None),
      model_fetcher=SimpleNamespace(get_bundles_for_source=lambda source: available),
      _process_download_requests=lambda: processed.append(params.get("ModelManager_DownloadRef")),
      _report_status=lambda: None,
    )
    class FakeSubMaster:
      def update(self, timeout):
        pass

      def __getitem__(self, service):
        return SimpleNamespace(chestnutPresent=False)

    manager.sm = FakeSubMaster()
    namespace = {"Ratekeeper": lambda *args, **kwargs: SimpleNamespace(keep_time=stop),
                 "ModelFetcher": SimpleNamespace(MODEL_SOURCES=("qcom", "chestnut"), active_source=lambda _: "qcom"),
                 "validate_active_bundles": lambda *args: None, "get_active_bundle": lambda *args, **kwargs: None,
                 "get_selected_bundle": lambda *args: None, "select_default_model": select_default_model}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(source), "exec"), namespace)
    with self.assertRaises(TickComplete):
      namespace["main_thread"](manager)
    self.assertEqual(processed, ["new-pop"])
    self.assertFalse(params.get_bool("NrdrAutoSelectModel"))

  def test_disabled_or_unusable_catalog_leaves_request_untouched(self):
    disabled = FakeParams(enabled=False)
    select_default_model(disabled, (bundle(11, "Pop Model v2", "pop-v2"),))
    self.assertIsNone(disabled.get("ModelManager_DownloadRef"))

    missing_ref = FakeParams()
    select_default_model(missing_ref, (bundle(11, "Pop Model v2", ""),))
    self.assertIsNone(missing_ref.get("ModelManager_DownloadRef"))
    self.assertTrue(missing_ref.get_bool("NrdrAutoSelectModel"))


class TestFirstRunModelRequest(unittest.TestCase):
  def test_dialog_and_confirm_do_not_promise_an_unsupported_model(self):
    root = Path(__file__).resolve().parents[3]
    source = root / "openpilot/nrdr/ui/home/layout.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "FirstRunSetup")
    dialogs = []
    namespace = {"Params": object, "DialogResult": SimpleNamespace(CONFIRM=1, CANCEL=0),
                 "ConfirmDialog": lambda text, button, callback: SimpleNamespace(text=text, button=button, callback=callback),
                 "gui_app": SimpleNamespace(push_widget=dialogs.append), "tr": lambda text: text}
    exec(compile(ast.Module(body=[cls], type_ignores=[]), str(source), "exec"), namespace)
    params = FakeParams(enabled=False)
    setup = namespace["FirstRunSetup"](params)
    setup.update()
    self.assertIn("compatible", dialogs[0].text.lower())
    self.assertIn("saved model choices stay unchanged", dialogs[0].text.lower())
    self.assertIn("pending", dialogs[0].text.lower())
    self.assertIn("without downloading or switching models", dialogs[0].text.lower())
    self.assertEqual(dialogs[0].button, "Request model")
    dialogs[0].callback(namespace["DialogResult"].CONFIRM)
    self.assertTrue(params.get_bool("NrdrAutoSelectModel"))
    self.assertIsNone(params.get("ModelManager_DownloadRef"))
    before = dict(params.values)
    select_default_model(params, (bundle(59, "Pop Model v2", "legacy", compiler=""),))
    self.assertEqual(params.values, before)


if __name__ == "__main__":
  unittest.main()
