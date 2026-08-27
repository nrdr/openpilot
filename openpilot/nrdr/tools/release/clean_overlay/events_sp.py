from openpilot.cereal import custom, log
from opendbc.car.structs import car
from openpilot.common.constants import CV
from openpilot.sunnypilot.selfdrive.selfdrived.events_base import Alert, ET, Priority


def speed_limit_pre_active_alert(CP, CS, sm, metric, soft_disable_time, personality):
  speed_conv = CV.MS_TO_KPH if metric else CV.MS_TO_MPH
  speed_limit = sm['longitudinalPlanSP'].speedLimit.resolver.speedLimitFinalLast
  speed = round(speed_limit * speed_conv)
  unit = "km/h" if metric else "mph"
  return Alert(
    f"Press distance button to accept {speed} {unit} speed limit", "",
    log.SelfdriveState.AlertStatus.normal, log.SelfdriveState.AlertSize.small,
    Priority.LOW, car.CarControl.HUDControl.VisualAlert.none,
    custom.SelfdriveStateSP.AudibleAlert.promptSingleLow, .1,
  )


def apply_events(events, event_name) -> None:
  events[event_name.speedLimitPreActive] = {ET.WARNING: speed_limit_pre_active_alert}
