import ast
from pathlib import Path
from types import SimpleNamespace
import unittest

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

  def remove(self, key):
    self.values.pop(key, None)


def bundle(index, display_name, ref):
  return SimpleNamespace(index=index, displayName=display_name, ref=ref)


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
    params = FakeParams(download_ref="already-pending")

    select_default_model(params, (bundle(11, "Pop Model v2", "pop-v2"),))

    self.assertEqual(params.get("ModelManager_DownloadRef"), "already-pending")
    self.assertTrue(params.get_bool("NrdrAutoSelectModel"))

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


if __name__ == "__main__":
  unittest.main()
