"""Persisted setting -> background reader -> real PID/blend -> transition -> Honda LPF.

This does not start the driving processes or send any control messages. Only a
temporary Params directory is written; native graphics and network delivery are
outside this test's scope.
"""
import ast
import base64
from pathlib import Path
import threading
import time
from types import SimpleNamespace

import pytest

from opendbc.sunnypilot.car.honda.controller_features import HondaControllerFeatures
from openpilot.common.params import Params
from openpilot.nrdr.features.lateral.live_tuning import LiveTorqueTransition
from openpilot.nrdr.features.lateral.torque_output_filter import HondaTorqueOutputFilter
from openpilot.nrdr.params.snapshots import CONTROL_GROUPS, LiveParams
from openpilot.nrdr.tests.test_live_pid_updates import make_live_pid, make_snapshot
from openpilot.nrdr.ui.native_param_controls import get_native_option_spec


KEY = "NrdrInterpolatedTorqueFrictionHighway"


def native_setter(params):
  """Use the production native widget setter without constructing the graphics UI."""
  path = Path(__file__).resolve().parents[2] / "system/ui/sunnypilot/widgets/option_control.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "OptionControlSP")
  setter = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "set_value")
  namespace = {}
  exec(compile(ast.Module(body=[setter], type_ignores=[]), str(path), "exec"), namespace)
  spec = get_native_option_spec(KEY)
  widget = SimpleNamespace(params=params, param_key=spec.param, min_value=spec.min_value,
                           max_value=spec.max_value, current_value=100, value_map=None,
                           use_float_scaling=spec.use_float_scaling, on_value_changed=None)
  return lambda value: namespace["set_value"](widget, round(value * spec.native_scale))


@pytest.mark.parametrize("writer_kind", ["native_widget", "sunnylink_handler", "typed_saved_value"])
def test_highway_friction_round_trip_remains_live_through_final_software_output(tmp_path, monkeypatch, writer_kind):
  params = Params(str(tmp_path / "params"))
  for key, value in make_snapshot(1).values.items():
    params.put(key, value, block=True)
  reader = LiveParams(CONTROL_GROUPS, params=params)
  events = []
  monkeypatch.setattr(reader, "_log_applied_settings", lambda report: events.append((threading.current_thread().name, report)))
  try:
    controller, _, update = make_live_pid(monkeypatch, reader, mock_candidate=False)
    pose = SimpleNamespace(angular_velocity_valid=True, angular_velocity=SimpleNamespace(z=-0.02))
    transition = LiveTorqueTransition()
    torque_filter = HondaTorqueOutputFilter()
    # Only construct the steering post-processor's in-memory state: its normal
    # constructor initializes unrelated longitudinal storage and is not needed.
    honda = HondaControllerFeatures.__new__(HondaControllerFeatures)
    honda.override_ramp = 1.0
    honda.lat_active_previous = True
    honda.steering_pressed_filter = 0.0
    honda.steering_pressed_previous = False
    live = SimpleNamespace(increase_override_tolerance=False, override_fade_up_s=1.0,
                           torque_lpf_enabled=True, lpf_tau_low=0.1, lpf_tau_standard=0.05,
                           lpf_tau_highway=0.02, steer_delta_limiter_enabled=False,
                           driver_assist_during_override=True)
    car = SimpleNamespace(out=SimpleNamespace(vEgo=25.0, steeringPressed=False))
    command = SimpleNamespace(latActive=True, actuators=SimpleNamespace(torque=0.0))
    processed = 0.0

    def tick():
      nonlocal processed
      captured = reader.snapshot
      controller.set_live_tuning_snapshot(captured)
      raw = update(pose=pose)
      transitioned = transition.update(raw, captured, True, False, 0.01)
      command.actuators.torque = torque_filter.update(transitioned, True, car.out.vEgo, live, 0.01)
      processed, lkas_active = honda.update_steering_torque(command, car, live, processed)
      assert lkas_active
      assert processed == command.actuators.torque  # No second, car-side LPF.
      return raw, transitioned, processed

    for _ in range(200):
      before = tick()
    assert controller.interpolated_torque_pif_settings.friction_highway == 1.0
    if writer_kind == "native_widget":
      write = native_setter(params)
    elif writer_kind == "sunnylink_handler":
      from openpilot.sunnypilot.sunnylink import utils
      from openpilot.sunnypilot.sunnylink.athena import sunnylinkd

      params.put_bool("IsOffroad", False, block=True)  # Only this test's private directory.
      monkeypatch.setattr(sunnylinkd, "params", params)
      monkeypatch.setattr(utils, "Params", lambda: params)
      monkeypatch.setattr(sunnylinkd, "generate_capabilities", lambda _: {"nrdr_honda_tuning_available": True})

      def write(value):
        # Run the real admission, base64 decoding, type conversion and save.
        # No socket, remote service, or driving process is started.
        sunnylinkd.saveParams({KEY: base64.b64encode(str(value).encode()).decode()})
        assert params.get(KEY) == value
    else:
      def write(value):
        params.put(KEY, value, block=True)
    for desired in (0.3, 1.0):
      previous_output = before[2]
      written = time.monotonic()
      write(desired)
      while controller.interpolated_torque_pif_settings.friction_highway != desired:
        assert time.monotonic() - written < 2.0, "Saved friction did not reach the continuously active controller"
        previous_transitioned = before[1]
        before = tick()
        if controller.interpolated_torque_pif_settings.friction_highway == desired:
          # The update reached the controller, while the first-frame command
          # step is removed by the exact production transition implementation.
          assert before[1] == pytest.approx(previous_transitioned, abs=1e-12)
          break
        time.sleep(0.01)
      consumed_generation = controller.settings_generation
      for _ in range(120):
        before = tick()
      assert transition.remaining == 0.0
      assert before[1] == pytest.approx(before[0], abs=1e-12)
      assert abs(before[2] - before[0]) < 5e-4
      assert abs(before[2] - previous_output) > 0.02
      settings = controller.interpolated_torque_pif_settings
      assert settings.torque_share == 0.1
      assert settings.lat_accel_factor == 10.0
      assert settings.friction_low == settings.friction_standard == 1.0
      deadline = time.monotonic() + 2.0
      while not any(report["generation"] == consumed_generation and report["friction_highway"] == desired for _, report in events):
        assert time.monotonic() < deadline, "Consumed-setting event was not emitted by the worker"
        time.sleep(0.01)
      matching = [report for thread_name, report in events if report["generation"] == consumed_generation
                  and report["friction_highway"] == desired and thread_name == "nrdr-live-params"]
      assert len(matching) == 1
      assert matching[0]["active"] and matching[0]["yaw_feedback_valid"]
      assert matching[0]["torque_share_percent"] == 10.0
      assert matching[0]["torque_transition_seconds"] == 1.0
      assert all(params.get(key) == value for key, value in make_snapshot(1).values.items() if key != KEY)
  finally:
    reader.close()
