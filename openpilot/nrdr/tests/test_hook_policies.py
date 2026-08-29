from types import SimpleNamespace
import unittest

from openpilot.nrdr.features.driver_policy.mads import AutoLkas
from openpilot.nrdr.features.lateral.steer_ratio_tuning import SteerRatioModeLatch, resolve_steer_ratio_selection
from openpilot.nrdr.hooks.controlsd import apply_hud_lead, stopping_inputs, vehicle_model_params
from openpilot.nrdr.hooks.driver_monitoring import apply_driver_monitoring_policy


class TestHookPolicies(unittest.TestCase):
  @staticmethod
  def _controls(mode=1):
    CP = SimpleNamespace(brand="honda", carFingerprint="HONDA_CLARITY", steerRatio=15.0, carFw=[])
    selection = resolve_steer_ratio_selection(CP, {
      "NrdrSteerRatioMode": mode,
      "NrdrSteerRatioManualCenter": 15.38,
      "NrdrSteerRatioManualFinal": 10.93,
    })
    return SimpleNamespace(
      learn_stiffness=False,
      learn_angle_offset=False,
      CP=CP,
      sm=SimpleNamespace(valid={"vehicleParameters": True}),
      steer_ratio_latch=SteerRatioModeLatch(selection),
    )

  def test_vehicle_model_policy_respects_learning_gates_and_explicit_comma_mode(self):
    controls = self._controls()
    live_params = SimpleNamespace(stiffnessFactor=0.8, steerRatio=16.5, steerRatioValid=True, angleOffsetDeg=1.2)

    self.assertEqual(vehicle_model_params(controls, live_params), (1.0, 16.5, 0.0))

    controls.learn_stiffness = True
    controls.learn_angle_offset = True
    self.assertEqual(vehicle_model_params(controls, live_params), (0.8, 16.5, 1.2))

  def test_vehicle_model_policy_preserves_positive_floor_and_rejects_invalid_comma_ratio(self):
    controls = self._controls()
    controls.learn_stiffness = True
    live_params = SimpleNamespace(stiffnessFactor=-1.0, steerRatio=0.0, steerRatioValid=True, angleOffsetDeg=0.0)

    self.assertEqual(vehicle_model_params(controls, live_params), (0.1, 15.0, 0.0))

  def test_stopping_inputs_and_hud_lead_translate_framework_messages(self):
    pose = SimpleNamespace(orientation=SimpleNamespace(xyz=(0.0, 0.04, 0.0)))
    plan = SimpleNamespace(hasLead=True, leadTrajectoryX0=(21.5,))
    self.assertEqual(stopping_inputs(pose, plan), (0.04, 21.5))
    self.assertEqual(stopping_inputs(None, SimpleNamespace(hasLead=False, leadTrajectoryX0=())), (None, None))

    hud = SimpleNamespace(leadDistance=-1.0, leadVLead=-1.0)
    apply_hud_lead(hud, SimpleNamespace(present=True, dRel=21.5, vLead=17.0))
    self.assertEqual((hud.leadDistance, hud.leadVLead), (21.5, 17.0))
    apply_hud_lead(hud, SimpleNamespace(present=False, dRel=99.0, vLead=99.0))
    self.assertEqual((hud.leadDistance, hud.leadVLead), (0.0, 0.0))

  def test_driver_monitoring_policy_retains_disabled_timeout_values(self):
    settings = SimpleNamespace()
    apply_driver_monitoring_policy(settings)

    self.assertEqual(settings._WHEELTOUCH_POLICY_ALERT_1_TIMEOUT, 86400.0 - 15.0)
    self.assertEqual(settings._WHEELTOUCH_POLICY_ALERT_2_TIMEOUT, 86400.0 - 6.0)
    self.assertEqual(settings._WHEELTOUCH_POLICY_ALERT_3_TIMEOUT, 86400.0)
    self.assertEqual(settings._VISION_POLICY_ALERT_1_TIMEOUT, 86400.0 - 8.0)
    self.assertEqual(settings._VISION_POLICY_ALERT_2_TIMEOUT, 86400.0 - 6.0)
    self.assertEqual(settings._VISION_POLICY_ALERT_3_TIMEOUT, 86400.0)
    self.assertEqual(settings._NO_RESPONSE_TIMEOUT, 86400.0)
    self.assertEqual(settings._MAX_ALERT_3, 86400)
    self.assertEqual(settings._MAX_NO_RESPONSE, 86400)

  def test_auto_lkas_rearms_only_after_main_becomes_unavailable(self):
    auto_lkas = AutoLkas()
    added = []
    events = SimpleNamespace(add=added.append)
    event_name = SimpleNamespace(lkasEnable="lkasEnable")
    available = SimpleNamespace(cruiseState=SimpleNamespace(available=True))
    unavailable = SimpleNamespace(cruiseState=SimpleNamespace(available=False))

    auto_lkas.request(available, True, events, event_name)
    self.assertEqual(added, ["lkasEnable"])

    auto_lkas.update(True)
    auto_lkas.request(available, True, events, event_name)
    self.assertEqual(added, ["lkasEnable"])

    auto_lkas.request(unavailable, True, events, event_name)
    auto_lkas.request(available, True, events, event_name)
    self.assertEqual(added, ["lkasEnable", "lkasEnable"])
