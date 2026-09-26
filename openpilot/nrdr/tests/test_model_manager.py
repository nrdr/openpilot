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
