"""MVL owns the controller tune, not SCC/SLA speed-target preferences.

Execute actual planner definitions with recording SCC/SLA/solver boundaries and
real SP capnp payloads, without Params, sockets, or native acados. These are host
target-routing/publication regressions, not optimizer or vehicle validation.
"""
from types import SimpleNamespace as NS

import numpy as np
import pytest

from opendbc.car.honda.values import CAR, HondaFlags
from opendbc.car.structs import car
from openpilot.cereal import custom
from openpilot.common.constants import CV
from openpilot.nrdr.features.longitudinal.policy import mvl_longitudinal_enabled, nrdr_longitudinal_enabled
from openpilot.nrdr.tests.test_mvl_host_parity import (
  CORE, MPC, SP, Messages, PlannerMpcDouble, car_params, constant, definitions, environment, forbidden, planner_messages, source,
)
from openpilot.sunnypilot import PARAMS_UPDATE_PERIOD
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit import CONFIRM_SPEED_THRESHOLD, PCM_LONG_REQUIRED_MAX_SET_SPEED
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.common import Mode, OffsetType, Policy

PLAN_SOURCE = custom.LongitudinalPlanSP.LongitudinalPlanSource
CRUISE_MAX = constant(source("openpilot/selfdrive/car/cruise.py"), "V_CRUISE_MAX")


class IsolatedTargetParams:
  """Allowlisted target preferences only; never read or write device Params."""
  def __init__(self, *_args):
    self.values = {"SmartCruiseControlVision": False, "SmartCruiseControlMap": False,
                   "SpeedLimitMode": Mode.information, "SpeedLimitPolicy": Policy.car_state_only,
                   "SpeedLimitOffsetType": OffsetType.off, "SpeedLimitValueOffset": 0,
                   "IsMetric": True, "IsReleaseSpBranch": False, "UbloxAvailable": False,
                   "LastGPSPosition": None, "MapTargetVelocities": None,
                   "CustomAccIncrementsEnabled": False, "CustomAccShortPressIncrement": 1, "CustomAccLongPressIncrement": 5}
    self.reads = []

  def get(self, key, **_kwargs):
    assert key in self.values, f"Unexpected settings read: {key}"
    self.reads.append(key)
    return self.values[key]

  def get_bool(self, key):
    return bool(self.get(key))

  def put(self, *_args, **_kwargs):
    raise AssertionError("Native target fixtures must not write Params")


def real_assist_classes(settings):
  """Actual SLA and NRDR distance-confirmation definitions, isolated Params."""
  env = environment(car=car, custom=custom, Params=IsolatedTargetParams, Mode=Mode, SpeedLimitMode=Mode,
                    EventsSP=object, PARAMS_UPDATE_PERIOD=PARAMS_UPDATE_PERIOD,
                    CONFIRM_SPEED_THRESHOLD=CONFIRM_SPEED_THRESHOLD, PCM_LONG_REQUIRED_MAX_SET_SPEED=PCM_LONG_REQUIRED_MAX_SET_SPEED)
  helpers = definitions(source(SP + "speed_limit/helpers.py"), env)
  env.update({key: helpers[key] for key in ("compare_cluster_target", "set_speed_limit_assist_availability")})
  env["Params"] = lambda: settings
  base = definitions(source(SP + "speed_limit/speed_limit_assist.py"), env)
  env.update({key: base[key] for key in ("SpeedLimitAssist", "ACTIVE_STATES", "CRUISE_BUTTON_CONFIRM_HOLD")})
  env["SpeedLimitConfirmation"] = definitions(source("openpilot/nrdr/features/driver_policy/speed_limit.py"), env)["SpeedLimitConfirmation"]
  nrdr = definitions(source("openpilot/nrdr/features/driver_policy/speed_limit_assist.py"), env)
  return base["SpeedLimitAssist"], nrdr["NrdrSpeedLimitAssist"]


class SCCBoundary:
  def __init__(self):
    self.calls = []
    self.vision = NS(current_lat_acc=.3, max_pred_lat_acc=1.7)
    self.map = NS()

  def update(self, sm, enabled, override, v_ego, a_ego, v_cruise):
    self.calls.append((enabled, override, v_ego, a_ego, v_cruise))
    for name in ("vision", "map"):
      obj = getattr(self, name)
      obj.enabled = obj.is_enabled = getattr(sm, name + "_enabled")
      obj.is_active = obj.enabled and enabled and not override
      obj.state = "turning" if obj.is_active else "disabled"
      obj.output_v_target, obj.output_a_target = getattr(sm, name + "_target")
      # Deliberately leave stale vision outputs when inactive: the planner must
      # exclude these using its existing explicit vision eligibility check.
      if name == "map" and not obj.is_active:
        obj.output_v_target, obj.output_a_target = 255., 0.


class ResolverBoundary:
  def __init__(self, *, nrdr_enabled):
    self.nrdr_enabled = nrdr_enabled
    self.calls = []

  def update(self, v_ego, sm):
    self.calls.append(v_ego)
    self.__dict__.update(sm.resolved)


class AssistBoundary:
  def __init__(self, *_):
    self.calls = []
    self.buttons = []
    self.enabled = True

  def update_buttons(self, release_toggle):
    self.buttons.append(release_toggle)

  def update(self, enabled, override, v_ego, a_ego, cruise, limit, last, valid, distance, events):
    self.calls.append((enabled, override, v_ego, a_ego, cruise, limit, last, valid, distance, events))
    self.is_enabled = self.enabled
    self.is_active = self.enabled and enabled and not override and valid
    self.state = "active" if self.is_active else "inactive"
    self.output_v_target = min(limit or last, cruise) if self.is_active else 255.
    self.output_a_target = -.4 if self.is_active else 0.


class NrdrAssistBoundary(AssistBoundary):
  pass


class BoostBoundary:
  enabled = True

  def __init__(self):
    self.reads = 0

  def update_params(self):
    self.reads += 1

  def update(self, _sm, e2e, _mpc, _cruise):
    return e2e + .5


def new_message(service):
  payload = custom.LongitudinalPlanSP.new_message() if service == "longitudinalPlanSP" else NS()
  return NS(logMonoTime=200, **{service: payload})


def planner_environment(mode):
  return environment(
    custom=custom, V_CRUISE_MAX=CRUISE_MAX,
    mvl_longitudinal_enabled=mvl_longitudinal_enabled,
    nrdr_longitudinal_enabled=nrdr_longitudinal_enabled,
    # Do not use controller-tune eligibility to select the speed-target policy.
    nrdr_custom_longitudinal_enabled=forbidden,
    EventsSP=lambda: NS(clear=lambda: None, to_msg=list),
    E2EAlertsHelper=lambda: NS(update=lambda *_: None, green_light_alert=True, lead_depart_alert=False),
    SmartCruiseControl=SCCBoundary,
    SpeedLimitResolver=ResolverBoundary,
    NrdrSpeedLimitAssist=NrdrAssistBoundary,
    SpeedLimitAssist=AssistBoundary,
    AccelBoostSP=BoostBoundary,
    get_active_bundle=(lambda: NS(generation=8)) if mode in ("normal", "legacy") else forbidden,
    messaging=NS(SubMaster=object, PubMaster=object, new_message=new_message),
  )


def params(mode):
  cp = car_params(flagged=False)
  cp.carFingerprint = CAR.HONDA_CIVIC
  cp.flags = int(HondaFlags.NIDEC)
  if mode in ("mvl", "legacy_mvl"):
    cp.flags |= HondaFlags.MVL_LONGITUDINAL
  if mode.startswith("legacy"):
    cp.flags |= 524288  # retired cached bit must be inert
  cp.passive = cp.dashcamOnly = False
  cp.pcmCruise = True
  return cp, NS(enableGasInterceptor=False, flags=0)


def make_planner(mode):
  cls = definitions(source(SP + "longitudinal_planner.py"), planner_environment(mode))["LongitudinalPlannerSP"]
  return cls(*params(mode), object())


def messages():
  sm = Messages(carState=NS(vCruiseCluster=108.), carControl=NS(enabled=True, cruiseControl=NS(override=False)))
  sm.vision_enabled = sm.map_enabled = True
  sm.vision_target, sm.map_target = (255., -.1), (255., -.2)
  sm.resolved = {"speed_limit": 0., "speed_limit_last": 0., "speed_limit_final": 0., "speed_limit_final_last": 0.,
                 "speed_limit_valid": False, "speed_limit_last_valid": False, "speed_limit_offset": 0., "distance": 0., "source": "none"}
  return sm


def publish(planner, sm):
  sent = {}
  planner.publish_longitudinal_plan_sp(sm, NS(send=lambda key, value: sent.update({key: value})))
  msg = sent["longitudinalPlanSP"]
  assert msg.valid
  # Round-trip the actual wire schema, without any messaging sockets.
  with custom.LongitudinalPlanSP.from_bytes(msg.longitudinalPlanSP.to_bytes()) as reader:
    return reader.to_dict()


@pytest.mark.parametrize("mode", ["normal", "mvl", "legacy", "legacy_mvl"])
def test_target_policy_separate_from_tuning_ownership(mode):
  planner = make_planner(mode)
  assert not hasattr(planner, "legacy_pcm")
  assert planner.mvl_enabled is ("mvl" in mode)
  assert isinstance(planner.scc, SCCBoundary)
  assert planner.resolver.nrdr_enabled
  assert type(planner.sla) is NrdrAssistBoundary
  planner.sla.update_buttons(4)
  assert planner.sla.buttons == [4]
  planner.update(messages())
  assert planner.apply_accel_boost({}, .2, .3, .4) == pytest.approx(.7)
  assert planner.accel_boost_sp.reads == 1
  assert planner.generation == (8 if mode in ("normal", "legacy") else None)


def test_non_honda_target_policy_keeps_baseline_assist():
  cp, cp_sp = params("normal")
  cp.brand, cp.carFingerprint = "toyota", "TOYOTA_TEST"
  cls = definitions(source(SP + "longitudinal_planner.py"), planner_environment("normal"))["LongitudinalPlannerSP"]
  planner = cls(cp, cp_sp, object())
  assert not planner.resolver.nrdr_enabled
  assert type(planner.sla) is AssistBoundary


@pytest.mark.parametrize("mode", ["normal", "mvl"])
def test_real_nrdr_assist_requires_distance_confirmation_before_target_reduction(mode):
  settings = IsolatedTargetParams()
  settings.values["SpeedLimitMode"] = Mode.assist
  baseline, nrdr = real_assist_classes(settings)
  env = planner_environment(mode)
  env.update(SpeedLimitAssist=baseline, NrdrSpeedLimitAssist=nrdr,
             EventsSP=lambda: NS(clear=lambda: None, add=lambda *_: None, to_msg=list))
  cls = definitions(source(SP + "longitudinal_planner.py"), env)["LongitudinalPlannerSP"]
  planner, sm = cls(*params(mode), object()), messages()
  assert type(planner.sla) is nrdr
  sm.resolved.update(speed_limit=15., speed_limit_final_last=15., speed_limit_valid=True)
  for _ in range(15):
    assert planner.update_targets(sm, 20., .2, 30.) == (30., .2)
  assert planner.sla.state == custom.LongitudinalPlanSP.SpeedLimit.AssistState.preActive
  release = 1 << car.CarState.ButtonEvent.Type.decelCruise
  planner.sla.update_buttons(release)
  assert planner.update_targets(sm, 20., .2, 30.) == (30., .2)
  planner.sla.update_buttons(release | (1 << car.CarState.ButtonEvent.Type.gapAdjustCruise))
  assert planner.update_targets(sm, 20., .2, 30.) == (15., .2)
  assert planner.source == PLAN_SOURCE.speedLimitAssist
  payload = publish(planner, sm)
  assert payload["speedLimit"]["assist"]["active"]
  assert payload["vTarget"] == 15.


@pytest.mark.parametrize("mode", ["normal", "mvl"])
def test_live_target_changes_keep_speed_acceleration_and_source_together(mode):
  planner, sm = make_planner(mode), messages()
  stages = [
    ((18., -.1), (22., -.2), 25., (18., -.1), "sccVision"),
    ((24., -.1), (16., -.2), 25., (16., -.2), "sccMap"),
    ((24., -.1), (22., -.2), 14., (14., -.4), "speedLimitAssist"),
    ((255., 0.), (255., 0.), 0., (30., .2), "cruise"),
  ]
  for vision, map_target, limit, expected, winner in stages:
    sm.vision_target, sm.map_target = vision, map_target
    sm.resolved.update(speed_limit=limit, speed_limit_final_last=limit, speed_limit_valid=limit > 0.)
    planner.update(sm)
    assert planner.update_targets(sm, 20., .2, 30.) == expected
    assert planner.source == getattr(PLAN_SOURCE, winner)
    payload = publish(planner, sm)
    assert payload["longitudinalPlanSource"] == winner
    assert (payload["vTarget"], payload["aTarget"]) == pytest.approx(expected)
  assert len(planner.scc.calls) == len(planner.resolver.calls) == len(planner.sla.calls) == len(stages)
  assert planner.scc.calls[-1] == (True, False, 20., .2, 30.)
  assert planner.sla.calls[-1][4] == pytest.approx(108. * CV.KPH_TO_MS)


@pytest.mark.parametrize("mode", ["normal", "mvl"])
@pytest.mark.parametrize("enabled,override", [(False, False), (True, True)])
def test_enablement_override_and_stale_disabled_vision_are_forwarded(mode, enabled, override):
  planner, sm = make_planner(mode), messages()
  sm.vision_target, sm.map_target = (8., -.1), (12., -.2)
  sm.resolved.update(speed_limit=10., speed_limit_valid=True)
  assert planner.update_targets(sm, 20., .2, 30.) == (8., -.1)
  sm["carControl"].enabled, sm["carControl"].cruiseControl.override = enabled, override
  assert planner.update_targets(sm, 20., .2, 30.) == (30., .2)
  assert planner.scc.calls[-1][:2] == planner.sla.calls[-1][:2] == (enabled, override)
  sm["carControl"].enabled, sm["carControl"].cruiseControl.override = True, False
  sm.vision_enabled = False
  assert planner.update_targets(sm, 20., .2, 30.) == (10., -.4)
  assert planner.scc.vision.output_v_target == 8.  # excluded, not accidentally erased by the fixture


@pytest.mark.parametrize("mode", ["normal", "mvl"])
@pytest.mark.parametrize("valid,last_valid", [(True, False), (False, True), (True, True), (False, False)])
def test_speed_limit_validity_and_telemetry_remain_live(mode, valid, last_valid):
  planner, sm = make_planner(mode), messages()
  sm["carState"].vCruiseCluster = 250.
  limit, last = (19. if valid else 0.), (17. if last_valid else 0.)
  sm.resolved.update(speed_limit=limit, speed_limit_last=last, speed_limit_final=limit + 1. if valid else 0.,
                     speed_limit_final_last=last + 1. if last_valid else 0., speed_limit_valid=valid,
                     speed_limit_last_valid=last_valid, speed_limit_offset=1., distance=123., source="map")
  planner.update_targets(sm, 20., .2, 30.)
  args = planner.sla.calls[-1]
  assert args[4:9] == (CRUISE_MAX * CV.KPH_TO_MS, limit, sm.resolved["speed_limit_final_last"], valid or last_valid, 123.)
  assert args[9] is planner.events_sp
  payload = publish(planner, sm)
  resolver, assist = payload["speedLimit"]["resolver"], payload["speedLimit"]["assist"]
  expected = {"speedLimit": limit, "speedLimitLast": last, "speedLimitFinal": sm.resolved["speed_limit_final"],
              "speedLimitFinalLast": sm.resolved["speed_limit_final_last"], "speedLimitValid": valid,
              "speedLimitLastValid": last_valid, "speedLimitOffset": 1., "distToSpeedLimit": 123., "source": "map"}
  assert resolver == expected
  assert assist["enabled"] and assist["active"] is (valid or last_valid)
  assert assist["vTarget"] == planner.sla.output_v_target
  assert assist["aTarget"] == pytest.approx(planner.sla.output_a_target)
  assert payload["e2eAlerts"] == {"greenLightAlert": True, "leadDepartAlert": False}
  vision, map_control = (payload["smartCruiseControl"][key] for key in ("vision", "map"))
  assert vision["currentLateralAccel"] == pytest.approx(.3)
  assert vision["maxPredictedLateralAccel"] == pytest.approx(1.7)
  for published, actual in ((vision, planner.scc.vision), (map_control, planner.scc.map)):
    assert published["state"] == actual.state
    assert published["enabled"] == actual.is_enabled and published["active"] == actual.is_active
    assert (published["vTarget"], published["aTarget"]) == pytest.approx((actual.output_v_target, actual.output_a_target))


@pytest.mark.parametrize("mode", ["legacy", "legacy_mvl"])
def test_retired_legacy_bit_does_not_remove_speed_control_telemetry(mode):
  planner, sm = make_planner(mode), messages()
  assert planner.update_targets(sm, 20., .2, 30.) == (30., .2)
  payload = publish(planner, sm)
  assert payload["longitudinalPlanSource"] == "cruise"
  assert "smartCruiseControl" in payload and "speedLimit" in payload
  assert payload["e2eAlerts"]["greenLightAlert"]


@pytest.mark.parametrize("target", ["vision", "map", "speedLimit"])
@pytest.mark.parametrize("experimental", [False, True])
def test_restored_targets_reach_mvl_cruise_response_and_publication(target, experimental):
  env = planner_environment("mvl")
  env.update(LongitudinalMpc=PlannerMpcDouble, T_IDXS_MPC=np.linspace(0., 10., 13))
  env["LongitudinalPlannerSP"] = definitions(source(SP + "longitudinal_planner.py"), env)["LongitudinalPlannerSP"]
  helpers = definitions(source(CORE + "drive_helpers.py"), env)
  env.update({key: helpers[key] for key in ("get_accel_from_plan", "should_stop")})
  env["AccelBoost"] = definitions(source(MPC + "mvl_accel_boost.py"), env)["AccelBoost"]
  cls = definitions(source(MPC + "mvl_planner.py"), env)["MvlLongitudinalPlanner"]
  planner = cls(*params("mvl"), init_v=20.)
  sm = planner_messages(1, np.random.default_rng(7), 1)
  sm.__dict__.update(messages().__dict__)
  sm["carState"].vEgo, sm["carState"].aEgo, sm["carState"].vCruise, sm["carState"].vCruiseCluster = 20., 0., 108., 108.
  sm["carState"].standstill = sm["carState"].gasPressed = False
  sm["carControl"].enabled, sm["carControl"].cruiseControl = True, NS(override=False)
  sm["radarState"].accel = sm["modelV2"].action.desiredAcceleration = 1.
  sm["modelV2"].action.shouldStop = False
  sm["selfdriveState"].experimentalMode = experimental
  planner.update(sm)
  assert planner.output_v_target == pytest.approx(30.)
  assert planner.output_a_target > 0.
  if target == "speedLimit":
    sm.resolved.update(speed_limit=15., speed_limit_valid=True)
  else:
    setattr(sm, target + "_target", (15., -.2))
  for _ in range(5):
    planner.update(sm)
  assert planner.output_v_target == 15.
  assert planner.output_a_target < 0.
  assert planner.accel_boost_sp.enabled and planner.mpc.kwargs["mvl_enabled"]
  assert planner.mpc.weights[1] == 1  # personality is unchanged
  payload = publish(planner, sm)
  expected_source = {"vision": "sccVision", "map": "sccMap", "speedLimit": "speedLimitAssist"}[target]
  assert payload["longitudinalPlanSource"] == expected_source
  assert payload["vTarget"] == 15.
  assert payload["aTarget"] == pytest.approx(planner.output_a_target)
