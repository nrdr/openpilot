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


def apply_events(events, event_name):
  alert_status = log.SelfdriveState.AlertStatus
  alert_size = log.SelfdriveState.AlertSize
  visual_alert = car.CarControl.HUDControl.VisualAlert
  audible_alert = car.CarControl.HUDControl.AudibleAlert

  events[event_name.controlsMismatchLateral] = {
    ET.WARNING: Alert(
      "Possible Controls Mismatch", "Openpilot may not have fully disengaged.",
      alert_status.normal, alert_size.mid, Priority.LOW,
      visual_alert.none, audible_alert.none, 1.,
    ),
  }
  events[event_name.laneTurnLeft] = {}
  events[event_name.laneTurnRight] = {}
  events[event_name.speedLimitActive] = {
    ET.WARNING: Alert(
      "Automatically Changing Max Speed", "The new speed limit has been applied.",
      alert_status.normal, alert_size.mid, Priority.LOW,
      visual_alert.none, custom.SelfdriveStateSP.AudibleAlert.promptSingleHigh, 5.,
    ),
  }
  events[event_name.speedLimitPreActive] = {ET.WARNING: speed_limit_pre_active_alert}
  events[event_name.speedLimitPending] = {
    ET.WARNING: Alert(
      "Automatically Changing Max Speed", "The last known speed limit has been applied.",
      alert_status.normal, alert_size.mid, Priority.LOW,
      visual_alert.none, custom.SelfdriveStateSP.AudibleAlert.promptSingleHigh, 5.,
    ),
  }
