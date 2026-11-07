"""NRDR-owned remote and system service implementations.

Modules stay independently importable so optional runtime dependencies such as
WebRTC are only loaded by the processes that use them.
"""
from openpilot.nrdr.features.services.model_artifacts import (
  ARTIFACT_ABI,
  TINYGRAD_RUNTIME_REF,
  ModelAdmissionError,
  admit_default_artifact,
  admit_selected_artifact,
  artifact_sha256,
  runtime_provenance,
  write_artifact_record,
)

__all__ = ("ARTIFACT_ABI", "TINYGRAD_RUNTIME_REF", "ModelAdmissionError", "admit_default_artifact",
           "admit_selected_artifact", "artifact_sha256", "runtime_provenance", "write_artifact_record")
