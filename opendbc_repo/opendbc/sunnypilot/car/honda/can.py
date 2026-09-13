from opendbc.car.common.conversions import Conversions as CV
from opendbc.car.honda.values import CAR, HONDA_BOSCH, HondaFlags


ALT_SPEED_STOCK = 0
ALT_SPEED_LEAD = 1
ALT_SPEED_GPS = 2
ALT_SPEED_CLUSTER = 3
ALT_DISTANCE_STOCK = 0
ALT_DISTANCE_RADAR = 1
ALT_DISTANCE_VELOCITY = 2


def apply_brake_alert_policy(values, fcw, stock_brake, clear_faults: bool):
  if clear_faults:
    values["CHIME"] = 0
    values["FCW"] = 0
  else:
    values["CHIME"] = stock_brake["CHIME"] if fcw else 0
    values["FCW"] = fcw << 1


def is_braking(active: bool, accel: float) -> bool:
  return active and accel < -0.2


def _lead_distance(visible: bool, distance: float) -> int:
  if not visible or distance <= 0.0 or distance >= 30.0:
    return 0
  if distance < 10.0:
    return 1
  if distance < 20.0:
    return 2
  return 3


def _accel_distance(accel: float) -> int:
  if accel >= 0.6:
    return 0
  if accel >= 0.15:
    return 3
  if accel > -0.15:
    return 2
  return 1


def update_acc_hud_values(values, CP, enabled, pcm_speed, pcm_accel, hud_control, hud_v_cruise,
                          acc_hud, speed_control, options=None):
  options = options or {}
  speed_design = options.get("speed_design", ALT_SPEED_STOCK)
  distance_design = options.get("distance_design", ALT_DISTANCE_STOCK)
  sub_mode_active = options.get("sub_mode_active", False)
  blink_on = options.get("blink_on", True)
  clear_faults = options.get("clear_dash_faults", True)

  if sub_mode_active:
    speed_design = ALT_SPEED_STOCK
    distance_design = ALT_DISTANCE_STOCK

  cruise_speed = hud_v_cruise
  hud_distance = hud_control.leadDistanceBars % 4
  mini_car = int(enabled)
  hud_lead = 2 if enabled and hud_control.leadVisible else int(enabled)
  send_acc_on = distance_design == ALT_DISTANCE_STOCK
  acc_on = int(enabled)

  if speed_design == ALT_SPEED_LEAD:
    if not hud_control.leadVisible:
      cruise_speed = 253
    elif hud_control.leadVLead < CV.MPH_TO_MS:
      cruise_speed = 252
    else:
      cruise_speed = min(251, max(0, round(options.get("lead_speed_display", 0.0))))
  elif speed_design == ALT_SPEED_GPS:
    cruise_speed = min(251, max(0, round(options.get("gps_speed_display", 0.0))))
  elif speed_design == ALT_SPEED_CLUSTER:
    cruise_speed = min(251, max(0, round(options.get("cluster_speed_display", 0.0))))

  if distance_design == ALT_DISTANCE_RADAR:
    hud_distance = _lead_distance(hud_control.leadVisible, hud_control.leadDistance)
  elif distance_design == ALT_DISTANCE_VELOCITY:
    hud_distance = _accel_distance(options.get("vehicle_accel", 0.0))

  if speed_design != ALT_SPEED_STOCK or distance_design != ALT_DISTANCE_STOCK:
    mini_car = 1
    hud_lead = 2 if hud_control.leadVisible else 1

  if sub_mode_active:
    send_acc_on = True
    acc_on = int(blink_on)
    mini_car = int(blink_on or enabled)
    if not (enabled and blink_on):
      cruise_speed = 255
  if options.get("max_flash_active", False) and enabled and speed_design == ALT_SPEED_STOCK and not blink_on:
    cruise_speed = 255

  values.update({
    "CRUISE_SPEED": cruise_speed,
    "ENABLE_MINI_CAR": mini_car,
    "HUD_DISTANCE": hud_distance,
    "HUD_LEAD": hud_lead,
  })

  if send_acc_on:
    values["ACC_ON"] = acc_on
  else:
    values.pop("ACC_ON", None)

  if CP.carFingerprint in HONDA_BOSCH:
    values["FCM_OFF"] = 1
    values["FCM_OFF_2"] = 1
  else:
    values["PCM_SPEED"] = pcm_speed * CV.MS_TO_KPH
    values["PCM_GAS"] = pcm_accel
    values["SET_ME_X01"] = speed_control if CP.flags & HondaFlags.HYBRID and CP.carFingerprint == CAR.ACURA_MDX_3G_MMR else 1
    for name in ("FCM_OFF", "FCM_OFF_2", "FCM_PROBLEM", "ICONS"):
      values[name] = 0 if clear_faults else acc_hud[name]
  return values


def create_camera_message(packer, bus):
  return packer.make_can_msg("CAMERA_MESSAGES", bus, {
    "HIGHBEAMS_ON": 0,
    "AUTO_HIGHBEAMS_ACTIVE": 0,
  })
