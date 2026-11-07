"""Keep NRDR's existing model compiler usable through the upstream sync."""
from pathlib import Path

import pytest

from openpilot.common import file_chunker


def test_compiler_dependencies_include_the_manifest_and_every_chunk(tmp_path):
  model = tmp_path / "driving.onnx"
  model.write_bytes(b"camera model")
  targets = file_chunker.get_chunk_targets(model, model.stat().st_size)
  file_chunker.chunk_file(model, targets)
  assert file_chunker.get_existing_chunks(model) == targets
  assert all(Path(path).is_file() for path in targets)
  with file_chunker.open_file_chunked(model) as stream:
    assert stream.read() == b"camera model"


def test_uncompiled_model_is_preferred_over_an_old_manifest(tmp_path):
  model = tmp_path / "driving.onnx"
  model.write_bytes(b"new model")
  Path(file_chunker.get_manifest_path(model)).write_text("1")
  Path(file_chunker.get_chunk_name(model, 0, 1)).write_bytes(b"old model")
  assert file_chunker.get_existing_chunks(model) == [model]
  with file_chunker.open_file_chunked(model) as stream:
    assert stream.read() == b"new model"


def test_failed_chunk_rebuild_does_not_advertise_complete_output(tmp_path):
  model = tmp_path / "driving.onnx"
  model.write_bytes(b"new model")
  manifest = Path(file_chunker.get_manifest_path(model))
  manifest.write_text("1")
  missing_output = tmp_path / "missing" / "chunk"
  with pytest.raises(FileNotFoundError):
    file_chunker.chunk_file(model, [str(manifest), str(missing_output)])
  assert not manifest.exists()


def test_missing_model_is_not_a_silent_empty_compile(tmp_path):
  with pytest.raises(FileNotFoundError):
    file_chunker.get_existing_chunks(tmp_path / "missing.onnx")
