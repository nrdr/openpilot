import ast
from pathlib import Path
import unittest

from openpilot.nrdr.features.lateral.lane_guidance import (
  LaneGuidanceMode,
  lane_guidance_mode_from_params,
  model_action_lane_guidance_mode,
  model_frame_lane_guidance_mode,
  nrdr_model_action_allowed,
  nrdr_lane_centering_allowed,
  parse_lane_guidance_mode,
  set_lane_guidance_mode,
)


class MemoryParams:
  def __init__(self, values=None):
    self.values = dict(values or {})
    self.writes = []

  def get(self, key):
    return self.values.get(key)

  def put(self, key, value, *, block=False):
    self.values[key] = value
    self.writes.append(("put", key, value, block))

  def put_bool(self, key, value, *, block=False):
    self.values[key] = bool(value)
    self.writes.append(("put_bool", key, bool(value), block))


class TestLaneGuidanceMode(unittest.TestCase):
  def test_accepts_all_canonical_modes(self):
    self.assertEqual(parse_lane_guidance_mode(0), LaneGuidanceMode.MODEL_ONLY)
    self.assertEqual(parse_lane_guidance_mode("1"), LaneGuidanceMode.NRDR)
    self.assertEqual(parse_lane_guidance_mode(b"2"), LaneGuidanceMode.BLENDFUL)

  def test_invalid_values_fail_closed(self):
    for value in (None, True, 1.2, -1, 3, " 1", "1.0", "blendful", b"\xff"):
      with self.subTest(value=value):
        self.assertEqual(parse_lane_guidance_mode(value), LaneGuidanceMode.MODEL_ONLY)

  def test_runtime_reads_only_canonical_mode(self):
    params = MemoryParams({"LaneGuidanceMode": 2, "LaneCentering": True})
    self.assertEqual(lane_guidance_mode_from_params(params), LaneGuidanceMode.BLENDFUL)

  def test_setter_mirrors_legacy_lane_centering_bool(self):
    params = MemoryParams()
    self.assertEqual(set_lane_guidance_mode(params, LaneGuidanceMode.NRDR), LaneGuidanceMode.NRDR)
    self.assertTrue(params.values["LaneCentering"])
    self.assertEqual(set_lane_guidance_mode(params, LaneGuidanceMode.BLENDFUL), LaneGuidanceMode.BLENDFUL)
    self.assertFalse(params.values["LaneCentering"])
    self.assertEqual(set_lane_guidance_mode(params, LaneGuidanceMode.MODEL_ONLY), LaneGuidanceMode.MODEL_ONLY)
    self.assertFalse(params.values["LaneCentering"])

  def test_invalid_setter_input_cannot_enable_either_correction(self):
    params = MemoryParams({"LaneCentering": True})
    self.assertEqual(set_lane_guidance_mode(params, 99), LaneGuidanceMode.MODEL_ONLY)
    self.assertEqual(params.values["LaneGuidanceMode"], 0)
    self.assertFalse(params.values["LaneCentering"])

  def test_nrdr_requires_matching_frame_that_explicitly_selected_nrdr(self):
    for model_mode in LaneGuidanceMode:
      allowed = nrdr_lane_centering_allowed(model_mode, True, 123, 123)
      self.assertEqual(allowed, model_mode == LaneGuidanceMode.NRDR)

    for invalid_mode in (None, -1, 3, 255, True, "nrdr"):
      with self.subTest(invalid_mode=invalid_mode):
        self.assertFalse(nrdr_lane_centering_allowed(invalid_mode, True, 123, 123))

    for valid, reported_frame, current_frame in (
      (False, 123, 123),
      (True, 122, 123),  # old sidecar with a new modelV2
      (True, 124, 123),  # future sidecar with an old modelV2
      (True, 0, 0),
      (True, None, 123),
    ):
      with self.subTest(valid=valid, reported_frame=reported_frame, current_frame=current_frame):
        self.assertFalse(nrdr_lane_centering_allowed(
          LaneGuidanceMode.NRDR, valid, reported_frame, current_frame))

    self.assertEqual(model_frame_lane_guidance_mode(
      LaneGuidanceMode.BLENDFUL, True, 123, 123), LaneGuidanceMode.BLENDFUL)
    self.assertEqual(model_frame_lane_guidance_mode(
      LaneGuidanceMode.BLENDFUL, True, 122, 123), LaneGuidanceMode.MODEL_ONLY)

  def test_model_action_mode_is_atomic_and_fails_closed(self):
    for mode in LaneGuidanceMode:
      self.assertEqual(model_action_lane_guidance_mode(mode, True), mode)
      self.assertEqual(nrdr_model_action_allowed(mode, True), mode == LaneGuidanceMode.NRDR)
    for invalid_mode in (None, -1, 3, 255, True, 1.0, "nrdr"):
      with self.subTest(invalid_mode=invalid_mode):
        self.assertEqual(model_action_lane_guidance_mode(invalid_mode, True), LaneGuidanceMode.MODEL_ONLY)
        self.assertFalse(nrdr_model_action_allowed(invalid_mode, True))
    self.assertEqual(model_action_lane_guidance_mode(LaneGuidanceMode.BLENDFUL, False), LaneGuidanceMode.MODEL_ONLY)
    self.assertFalse(nrdr_model_action_allowed(LaneGuidanceMode.NRDR, False))

  def test_sidecar_delivery_order_cannot_change_the_atomic_gate(self):
    cases = (
      ("model first", LaneGuidanceMode.NRDR, None, True),
      ("sidecar first", LaneGuidanceMode.NRDR, LaneGuidanceMode.NRDR, True),
      ("sidecar dropped", LaneGuidanceMode.NRDR, None, True),
      ("stale NRDR sidecar after switch to Blendful", LaneGuidanceMode.BLENDFUL, LaneGuidanceMode.NRDR, False),
      ("future NRDR sidecar while model stays Blendful", LaneGuidanceMode.BLENDFUL, LaneGuidanceMode.NRDR, False),
      ("stale Blendful sidecar after switch to NRDR", LaneGuidanceMode.NRDR, LaneGuidanceMode.BLENDFUL, True),
      ("model only with stale NRDR sidecar", LaneGuidanceMode.MODEL_ONLY, LaneGuidanceMode.NRDR, False),
    )
    for name, action_mode, _sidecar_mode, expected in cases:
      with self.subTest(delivery=name):
        self.assertEqual(nrdr_model_action_allowed(action_mode, True), expected)

  def test_controlsd_gate_uses_mode_in_the_atomic_model_action(self):
    root = Path(__file__).resolve().parents[3]
    source = (root / "openpilot/sunnypilot/selfdrive/controls/controlsd_ext.py").read_text(encoding="utf-8")
    method = source[source.index("def nrdr_lane_centering_enabled"):source.index("def get_lat_active")]
    self.assertIn("sm['modelV2'].action.laneGuidanceMode", method)
    self.assertIn("sm.all_checks(['modelV2'])", method)
    self.assertNotIn("modelDataV2SP", method)

  def test_custom_modeld_reads_mode_outside_the_slow_settings_poll(self):
    root = Path(__file__).resolve().parents[3]
    path = root / "openpilot/sunnypilot/modeld_v2/modeld.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    assignments = [
      node for node in ast.walk(tree)
      if isinstance(node, ast.Assign)
      and any(isinstance(target, ast.Name) and target.id == "lane_guidance_mode" for target in node.targets)
      and isinstance(node.value, ast.Call)
      and getattr(node.value.func, "id", None) == "parse_lane_guidance_mode"
    ]
    self.assertEqual(len(assignments), 1)
    assignment = assignments[0]
    slow_polls = [node for node in ast.walk(tree) if isinstance(node, ast.If) and "sm.frame % 60" in ast.unparse(node.test)]
    self.assertTrue(slow_polls)
    self.assertTrue(all(assignment not in tuple(ast.walk(poll)) for poll in slow_polls))

  def test_standard_modeld_fail_closes_and_clears_unavailable_blendful(self):
    root = Path(__file__).resolve().parents[3]
    source = (root / "openpilot/selfdrive/modeld/modeld.py").read_text(encoding="utf-8")
    self.assertIn("if lane_guidance_mode == LaneGuidanceMode.BLENDFUL:", source)
    self.assertIn("set_lane_guidance_mode(params, LaneGuidanceMode.MODEL_ONLY, block=False)", source)
    self.assertIn("modelv2_send.modelV2.action.laneGuidanceMode = int(lane_guidance_mode)", source)
    self.assertIn("mdv2sp_send.modelDataV2SP.laneGuidanceMode = int(lane_guidance_mode)", source)


if __name__ == "__main__":
  unittest.main()
