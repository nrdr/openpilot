"""Execute the real plannerd startup/loop with isolated I/O and solver doubles."""
from types import SimpleNamespace as NS

import numpy as np
import pytest

from openpilot.nrdr.tests.test_mvl_host_parity import (
  CORE, MPC, SP, Messages, PlannerMpcDouble, ResolverBoundary, SmartCruiseBoundary,
  car_params, definitions, environment, forbidden, planner_messages, source,
)
from openpilot.nrdr.tests.test_mvl_cruise_targets import IsolatedTargetParams, real_assist_classes


class StopLoop(Exception):
  pass


class LoopMessages(Messages):
  frame = 0
  updated = {"modelV2": False}

  def update(self):
    self.frame += 1
    if self.frame > 3:
      raise StopLoop
    self.updated = {"modelV2": self.frame != 2}


@pytest.mark.parametrize("mvl", [True, False])
def test_plannerd_startup_and_repeated_model_ticks(mvl):
  sent, created, buttons, ldw_ticks = [], [], [], []
  cp, cp_sp = car_params(flagged=mvl), NS(enableGasInterceptor=False)
  cp.pcmCruise = True
  sm = LoopMessages(planner_messages(1, np.random.default_rng(4), 1))
  sm["radarState"].leadOne = NS(present=True)
  sm["carState"].vCruiseCluster = sm["carState"].vCruise
  sm["carControl"].enabled = True
  sm["carControl"].cruiseControl = NS(override=False)
  sm["selfdriveStateSP"] = NS(buttonsReleaseToggle=4)
  # Real NRDR SLA must receive button snapshots on every tick, including the
  # tick without a model update. Feature settings stay disabled for parity.
  baseline_sla, nrdr_sla = real_assist_classes(IsolatedTargetParams())

  def new_message(service):
    payload = (NS(e2eAlerts=NS(), smartCruiseControl=NS(vision=NS(), map=NS()),
                  speedLimit=NS(resolver=NS(), assist=NS())) if service == "longitudinalPlanSP" else NS())
    return NS(logMonoTime=200, **{service: payload})

  messaging = NS(SubMaster=lambda *_a, **_kw: sm, PubMaster=lambda *_: NS(send=lambda *v: sent.append(v)),
                 new_message=new_message, log_from_bytes=lambda value, _schema: value)
  env = environment(
    EventsSP=lambda: NS(clear=lambda: None, add=lambda *_: None, to_msg=list),
    E2EAlertsHelper=lambda: NS(update=lambda *_: None, green_light_alert=False, lead_depart_alert=False),
    SmartCruiseControl=SmartCruiseBoundary, SpeedLimitResolver=ResolverBoundary, SpeedLimitAssist=baseline_sla,
    NrdrSpeedLimitAssist=nrdr_sla, AccelBoostSP=forbidden, get_active_bundle=forbidden,
    messaging=messaging, LongitudinalMpc=PlannerMpcDouble, T_IDXS_MPC=np.linspace(0., 10., 13),
  )
  env["LongitudinalPlannerSP"] = definitions(source(SP + "longitudinal_planner.py"), env)["LongitudinalPlannerSP"]
  helpers = definitions(source(CORE + "drive_helpers.py"), env)
  env.update({key: helpers[key] for key in ("get_accel_from_plan", "should_stop")})
  env["AccelBoost"] = definitions(source(MPC + "mvl_accel_boost.py"), env)["AccelBoost"]
  env["MvlLongitudinalPlanner"] = definitions(source(MPC + "mvl_planner.py"), env)["MvlLongitudinalPlanner"]
  planner_cls = definitions(source(CORE + "longitudinal_planner.py"), env)["LongitudinalPlanner"]

  def make_planner(params, params_sp):
    assert params is cp and params_sp is cp_sp
    if mvl:
      planner = planner_cls(params, params_sp)
      assert type(planner.sla) is nrdr_sla
      update_buttons = planner.sla.update_buttons

      def record_buttons(snapshot):
        buttons.append(snapshot)
        update_buttons(snapshot)

      planner.sla.update_buttons = record_buttons
    else:
      planner = NS(sla=NS(update_buttons=buttons.append), update=lambda *_: None, publish=lambda *_: None)
    created.append(planner)
    return planner

  env["car"].CarParams = object
  env["custom"].CarParamsSP = object
  env.update(
    LongitudinalPlanner=make_planner, Priority=NS(CTRL_LOW=1), config_realtime_process=lambda *_: None,
    Params=lambda: NS(get=lambda name, **_: cp if name == "CarParams" else cp_sp),
    get_gps_location_service=lambda _: "gpsLocation",
    LaneDepartureWarning=lambda: NS(left=False, right=False, update=lambda frame, *_: ldw_ticks.append(frame)),
  )
  main = definitions(source("openpilot/selfdrive/controls/plannerd.py"), env)["main"]
  with pytest.raises(StopLoop):
    main()
  assert len(created) == 1
  assert ldw_ticks == [1, 3]
  assert buttons == [4] * 3
  topics = [topic for topic, _ in sent]
  assert topics.count("driverAssistance") == 2
  assert topics.count("longitudinalPlan") == (2 if mvl else 0)
  assert topics.count("longitudinalPlanSP") == (2 if mvl else 0)
  if mvl:
    planner = created[0]
    assert len(planner.scc.vision.calls) == len(planner.scc.map.calls) == len(planner.resolver.calls) == 2
    assert planner.sla.frame == 1  # starts at -1, advances only on model ticks
    assert planner.sla._release_toggle_prev == 4
    assert planner.resolver.kwargs["nrdr_enabled"] and planner.accel_boost_sp is None
