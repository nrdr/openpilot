"""Execute the real plannerd startup/loop with isolated I/O and solver doubles."""
from types import SimpleNamespace as NS

import numpy as np
import pytest

from openpilot.nrdr.tests.test_mvl_host_parity import (
  CORE, MPC, SP, Messages, PlannerMpcDouble, car_params, definitions, environment, forbidden, planner_messages, source,
)


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
  sm = LoopMessages(planner_messages(1, np.random.default_rng(4), 1))
  sm["radarState"].leadOne = NS(present=True)
  if not mvl:
    sm["selfdriveStateSP"] = NS(buttonsReleaseToggle="button-snapshot")
  # In MVL there is deliberately no selfdriveStateSP entry: the disabled SLA
  # must not consume button messages, even on ticks without a model update.

  def new_message(service):
    payload = NS(e2eAlerts=NS()) if service == "longitudinalPlanSP" else NS()
    return NS(logMonoTime=200, **{service: payload})

  messaging = NS(SubMaster=lambda *_a, **_kw: sm, PubMaster=lambda *_: NS(send=lambda *v: sent.append(v)),
                 new_message=new_message, log_from_bytes=lambda value, _schema: value)
  env = environment(
    EventsSP=lambda: NS(clear=lambda: None, to_msg=list),
    E2EAlertsHelper=lambda: NS(update=lambda *_: None, green_light_alert=False, lead_depart_alert=False),
    SmartCruiseControl=forbidden, SpeedLimitResolver=forbidden, SpeedLimitAssist=forbidden,
    NrdrSpeedLimitAssist=forbidden, AccelBoostSP=forbidden, get_active_bundle=forbidden,
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
      assert planner.sla is None
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
  assert buttons == ([] if mvl else ["button-snapshot"] * 3)
  topics = [topic for topic, _ in sent]
  assert topics.count("driverAssistance") == 2
  assert topics.count("longitudinalPlan") == (2 if mvl else 0)
  assert topics.count("longitudinalPlanSP") == (2 if mvl else 0)
