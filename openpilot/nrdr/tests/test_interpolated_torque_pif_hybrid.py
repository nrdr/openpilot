from types import SimpleNamespace
from openpilot.nrdr.features.lateral.interpolated_torque_pif import InterpolatedTorquePifSettings
from openpilot.nrdr.features.lateral.latcontrol_pid import NrdrLatControlPID


def test_blend_pauses_learner_samples_but_keeps_learner_maintenance_running():
  class LearnerSpy:
    def __init__(self):
      self.calls = []

    def learn(self, *args):
      self.calls.append(args)

  controller = NrdrLatControlPID.__new__(NrdrLatControlPID)
  controller.is_eps_modified = True
  controller.model_v2 = None
  controller.live_tuning_snapshot = {}
  controller.params = SimpleNamespace(snapshot={})
  controller.interpolated_torque_pif_latch = SimpleNamespace(
    settings=InterpolatedTorquePifSettings(enabled=True),
  )
  controller.stiction_enabled = False
  controller.stiction = SimpleNamespace(freeze_integrator=False)
  controller.tune_learner = LearnerSpy()
  controller.frame = 123
  CS = SimpleNamespace(vEgo=10.0, steeringRateDeg=0.5)

  controller._update_tune_learner(
    CS, desired_angle=2.0, error=0.1, steering_pressed=False,
    params_valid=True, lane_change=False, stiction_limited=False,
  )
  assert len(controller.tune_learner.calls) == 1
  assert controller.tune_learner.calls[-1][5] is False

  controller.interpolated_torque_pif_latch.settings = InterpolatedTorquePifSettings(enabled=False)
  controller._update_tune_learner(
    CS, desired_angle=2.0, error=0.1, steering_pressed=False,
    params_valid=True, lane_change=False, stiction_limited=False,
  )
  assert len(controller.tune_learner.calls) == 2
  assert controller.tune_learner.calls[-1][5] is True
