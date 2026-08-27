"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Sentinel tests for the capabilities payload contract. PROTOCOL_VERSION is the
wire-protocol version observable by the dashboard; bumping it is a breaking
change and must be intentional. KNOWN_PROTOCOL_VERSIONS pins the set we
explicitly support — when the constant is bumped, this list must be edited in
the same commit so the bump shows up in code review.
"""
from __future__ import annotations


from openpilot.common.params import Params
from openpilot.sunnypilot.sunnylink.capabilities import (
  CAPABILITY_DEFAULTS,
  CAPABILITY_FIELDS,
  CAPABILITY_LABELS,
  PROTOCOL_VERSION,
  generate_capabilities,
)
from openpilot.common.test import OpenpilotTestCase


KNOWN_PROTOCOL_VERSIONS = (1,)
LATEST_KNOWN = max(KNOWN_PROTOCOL_VERSIONS)


def caps():
  return generate_capabilities()


def params():
  return Params()


def _active_bundle(artifact_sha256: str) -> dict:
  return {"models": [{"artifact": {"downloadUri": {"sha256": artifact_sha256}}}]}


class TestProtocolVersion(OpenpilotTestCase):
  def test_protocol_version_in_capability_fields(self):
    assert "protocol_version" in CAPABILITY_FIELDS

  def test_protocol_version_has_label(self):
    assert "protocol_version" in CAPABILITY_LABELS

  def test_protocol_version_default_is_set(self):
    assert CAPABILITY_DEFAULTS.get("protocol_version") == PROTOCOL_VERSION

  def test_protocol_version_emitted(self, caps):
    assert "protocol_version" in caps
    assert isinstance(caps["protocol_version"], int)
    assert caps["protocol_version"] >= 1

  def test_protocol_version_matches_constant(self, caps):
    assert caps["protocol_version"] == PROTOCOL_VERSION

  def test_protocol_version_is_known(self):
    """Sentinel against accidental bumps. Edit KNOWN_PROTOCOL_VERSIONS if intentional."""
    assert PROTOCOL_VERSION in KNOWN_PROTOCOL_VERSIONS, (
      f"PROTOCOL_VERSION={PROTOCOL_VERSION} is not in KNOWN_PROTOCOL_VERSIONS={KNOWN_PROTOCOL_VERSIONS}. " +
      "If this bump is intentional, add it to KNOWN_PROTOCOL_VERSIONS."
    )

  def test_protocol_version_matches_latest_known(self):
    assert PROTOCOL_VERSION == LATEST_KNOWN, (
      "Test invariant: PROTOCOL_VERSION must equal max(KNOWN_PROTOCOL_VERSIONS)."
    )


class TestOpaquePerBrandFlags(OpenpilotTestCase):
  def test_handcrafted_lateral_profile_field_present(self):
    assert "has_handcrafted_lateral_profile" in CAPABILITY_FIELDS

  def test_handcrafted_lateral_profile_default_false(self, caps):
    assert caps["has_handcrafted_lateral_profile"] is False

  def test_nrdr_steer_ratio_policy_fields_present(self):
    assert "nrdr_steer_ratio_policy" in CAPABILITY_FIELDS
    assert "nrdr_firmware_vgr_available" in CAPABILITY_FIELDS

  def test_nrdr_steer_ratio_policy_defaults_are_conservative(self, caps):
    assert caps["nrdr_steer_ratio_policy"] == "unknown"
    assert caps["nrdr_firmware_vgr_available"] is False

  def test_pop_v2_bundle_emits_legacy_policy(self, params):
    params.put("ModelManager_ActiveBundle", _active_bundle(
      "c48899574c1303e47ca2a6f80113876ca5eb749c4a75c89b53cc8029bb3bb710",
    ))
    model_caps = generate_capabilities(params)
    assert model_caps["nrdr_steer_ratio_policy"] == "legacy_dual_bp"
    assert model_caps["nrdr_firmware_vgr_available"] is False

  def test_tsfdo_bundle_emits_pure_firmware_policy(self, params):
    params.put("ModelManager_ActiveBundle", _active_bundle(
      "92d06467e4de97c40ffdc366e385a4f5897f36fc8ea632bd9bed113a3083fea8",
    ))
    model_caps = generate_capabilities(params)
    assert model_caps["nrdr_steer_ratio_policy"] == "pure_firmware_vgr"
    assert model_caps["nrdr_firmware_vgr_available"] is False

  def test_subaru_has_sng_field_present(self):
    assert "subaru_has_sng" in CAPABILITY_FIELDS

  def test_hyundai_alpha_long_available_field_present(self):
    assert "hyundai_alpha_long_available" in CAPABILITY_FIELDS

  def test_subaru_has_sng_default_false(self, caps):
    assert caps["subaru_has_sng"] is False

  def test_hyundai_alpha_long_available_default_false(self, caps):
    assert caps["hyundai_alpha_long_available"] is False


class TestCapabilitiesShape(OpenpilotTestCase):
  def test_all_fields_present(self, caps):
    for field in CAPABILITY_FIELDS:
      assert field in caps, f"capabilities missing {field}"

  def test_all_fields_have_labels(self):
    for field in CAPABILITY_FIELDS:
      assert field in CAPABILITY_LABELS, f"CAPABILITY_LABELS missing {field}"

  def test_string_defaults_are_strings(self, caps):
    assert isinstance(caps["brand"], str)
    assert isinstance(caps["steer_control_type"], str)
    assert isinstance(caps["device_type"], str)
    assert isinstance(caps["nrdr_steer_ratio_policy"], str)
