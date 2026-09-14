"""Exercise real Sunnylink request routing without importing native runtime modules."""

import ast
import base64
import gzip
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock


ROOT = Path(__file__).resolve().parents[2]
COMMAND_KEY = "NrdrHandcraftedLateralTune"
CONTEXT_KEY = "NrdrHandcraftedLateralRequest"


def _load_definitions(relative_path, names, namespace):
  path = ROOT / relative_path
  tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
  selected = []
  found = set()
  for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name in names:
      node.decorator_list = []
      selected.append(node)
      found.add(node.name)
    elif isinstance(node, ast.Assign):
      assigned = {target.id for target in node.targets if isinstance(target, ast.Name)}
      if assigned & names:
        selected.append(node)
        found.update(assigned & names)
  if found != names:
    raise AssertionError(f"Missing production definitions in {relative_path}: {names - found}")
  exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), "exec"), namespace)


class TestHandcraftedRequestRouting(unittest.TestCase):
  def setUp(self):
    self.params = SimpleNamespace(
      get_bool=Mock(return_value=True),
      get=Mock(return_value="0"),
      put=Mock(),
    )
    self.request = Mock(return_value=True)
    self.generic_write = Mock()
    self.namespace = {
      "base64": base64,
      "gzip": gzip,
      "params": self.params,
      "cloudlog": SimpleNamespace(warning=Mock(), error=Mock()),
      "_vehicle_tuning_capabilities": Mock(return_value={"has_handcrafted_lateral_profile": True}),
      "request_stored_handcrafted_lateral_profile": self.request,
      "save_param_from_base64_encoded_string": self.generic_write,
    }
    _load_definitions("nrdr/features/services/sunnylink.py", {
      "ONROAD_WRITE_BLOCKLIST", "HONDA_TUNING_WRITE_KEYS", "allow_param_write",
    }, self.namespace)
    _load_definitions("sunnypilot/sunnylink/athena/sunnylinkd.py", {
      "BLOCKED_PARAMS", "_remote_bool_value", "saveParams",
    }, self.namespace)
    self.save_params = self.namespace["saveParams"]

  @staticmethod
  def _encode(raw, compression=False):
    return base64.b64encode(gzip.compress(raw) if compression else raw).decode("ascii")

  def test_true_routes_only_through_bound_request(self):
    for compression in (False, True):
      with self.subTest(compression=compression):
        self.request.reset_mock()
        self.save_params({COMMAND_KEY: self._encode(b"1", compression)}, compression)
        self.request.assert_called_once_with(self.params)
        self.generic_write.assert_not_called()

  def test_rejected_bound_request_never_falls_through_to_generic_write(self):
    self.request.return_value = False
    self.save_params({COMMAND_KEY: self._encode(b"true")})
    self.request.assert_called_once_with(self.params)
    self.generic_write.assert_not_called()

  def test_false_preserves_generic_cancellation(self):
    for compression in (False, True):
      with self.subTest(compression=compression):
        self.generic_write.reset_mock()
        value = self._encode(b"0", compression)
        self.save_params({COMMAND_KEY: value}, compression)
        self.generic_write.assert_called_once_with(COMMAND_KEY, value, compression)
        self.request.assert_not_called()

  def test_onroad_true_is_not_routed_or_written(self):
    self.params.get_bool.return_value = False
    self.save_params({COMMAND_KEY: self._encode(b"1")})
    self.request.assert_not_called()
    self.generic_write.assert_not_called()

  def test_remote_context_is_blocked_before_policy_or_routing(self):
    for offroad in (False, True):
      with self.subTest(offroad=offroad):
        self.params.get_bool.return_value = offroad
        # Even an overly permissive admission policy cannot bypass the RPC blocklist.
        policy = Mock(return_value=True)
        self.namespace["allow_param_write"] = policy
        self.save_params({CONTEXT_KEY: self._encode(b'{"version":18}')})
        policy.assert_not_called()
        self.request.assert_not_called()
        self.generic_write.assert_not_called()

  def test_policy_independently_rejects_context_in_both_road_states(self):
    for onroad in (False, True):
      with self.subTest(onroad=onroad):
        self.assertFalse(self.namespace["allow_param_write"](
          CONTEXT_KEY, onroad, handcrafted_profile_available=True,
          honda_tuning_available=True, requested_bool=True,
        ))


if __name__ == "__main__":
  unittest.main()
