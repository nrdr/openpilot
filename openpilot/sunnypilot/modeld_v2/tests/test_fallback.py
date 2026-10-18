"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import io

from openpilot.common.hardware import hw
from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.modeld_v2.helpers import dump_oob
import openpilot.sunnypilot.modeld_v2.modeld as modeld_module
from openpilot.sunnypilot.modeld_v2.tests import helpers as tests_helpers
from openpilot.sunnypilot.modeld_v2.tests.helpers import DummyModel, DummyBundle, CAM_W, CAM_H

tmp_path = tests_helpers.tmp_path


class TestFallback(OpenpilotTestCase):
  def test_find_dual_model_in_bundle(self, tmp_path, monkeypatch):
    lebowski_file = 'driving_lebowski.pkl'
    tsfdo_file = 'driving_tsfdo.pkl'
    (tmp_path / lebowski_file).write_bytes(b'fkasdjfkljf')
    (tmp_path / tsfdo_file).write_bytes(b'dskfajklsdjlsfka')

    monkeypatch.setattr(hw.Paths, 'model_root', staticmethod(lambda: str(tmp_path)))
    big_bundle = DummyBundle(models=[DummyModel('supercombo', lebowski_file)])
    small_bundle = DummyBundle(models=[DummyModel('supercombo', tsfdo_file)])
    big_pkl = modeld_module._find_driving_pkl(big_bundle)
    small_pkl = modeld_module._find_driving_pkl(small_bundle)

    assert big_pkl is not None and lebowski_file in big_pkl
    assert small_pkl is not None and tsfdo_file in small_pkl

  def test_download_models_and_init_modelstate_fallback(self, tmp_path, monkeypatch):
    monkeypatch.setattr(hw.Paths, 'model_root', staticmethod(lambda: str(tmp_path)))
    big_bundle = DummyBundle(models=[DummyModel('supercombo', 'driving_big_fixture.pkl')], is_20hz=False)
    small_bundle = DummyBundle(models=[DummyModel('supercombo', 'driving_small_fixture.pkl')], is_20hz=False)
    # This is an adapter fixture, not a publisher or provenance test. Never
    # download live catalog models and then replace their contents with fake JITs.
    monkeypatch.setattr(modeld_module, 'admit_selected_artifact', lambda path, *_args, **_kwargs: path)

    buf = io.BytesIO()
    dump_oob(tests_helpers.make_pkl_data(tests_helpers.ARCHETYPES['supercombo_non20hz']), buf)
    oob_bytes = buf.getvalue()

    for bundle in (big_bundle, small_bundle):
      artifact = bundle.models[0].artifact
      (tmp_path / artifact.fileName).write_bytes(oob_bytes)

    monkeypatch.setattr(modeld_module, 'get_active_bundle', lambda params=None, *, chestnut=None: small_bundle)
    assert modeld_module.ModelState(CAM_W, CAM_H, chestnut=False).chestnut is False

    monkeypatch.setattr(modeld_module, 'get_active_bundle', lambda params=None, *, chestnut=None: big_bundle)
    try:
      assert modeld_module.ModelState(CAM_W, CAM_H, chestnut=True).chestnut is True
    except Exception as e:
      assert "AMD" in str(e) or "device" in str(e).lower()
