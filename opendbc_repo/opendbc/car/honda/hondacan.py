from opendbc.car import CanBusBase
from opendbc.car.common.conversions import Conversions as CV
from opendbc.car.honda.values import (CAR, HondaFlags, HONDA_BOSCH, HONDA_BOSCH_ALT_RADAR, HONDA_BOSCH_RADARLESS,
                                      HONDA_BOSCH_CANFD, CarControllerParams)
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP

# CAN bus layout with relay
# 0 = ACC-CAN - radar side
# 1 = F-CAN B - powertrain
# 2 = ACC-CAN - camera side
# 3 = F-CAN A - OBDII port


class CanBus(CanBusBase):
  def __init__(self, CP=None, fingerprint=None) -> None:
    # use fingerprint if specified
    super().__init__(CP if fingerprint is None else None, fingerprint)

    # powertrain bus is split instead of radar on radarless and CAN FD Bosch
    if CP.carFingerprint in (HONDA_BOSCH - HONDA_BOSCH_RADARLESS - HONDA_BOSCH_CANFD):
      self._pt, self._radar = self.offset + 1, self.offset
      # normally steering commands are sent to radar, which forwards them to powertrain bus
      # when radar is disabled, steering commands are sent directly to powertrain bus
      self._lkas = self._pt if CP.openpilotLongitudinalControl else self._radar
    else:
      self._pt, self._radar, self._lkas = self.offset, self.offset + 1, self.offset

  @property
  def pt(self) -> int:
    return self._pt

  @property
  def radar(self) -> int:
    return self._radar

  @property
  def camera(self) -> int:
    return self.offset + 2

  @property
  def lkas(self) -> int:
    return self._lkas

  # B-CAN is forwarded to ACC-CAN radar side (CAN 0 on fake ethernet port)
  @property
  def body(self) -> int:
    return self.offset


def create_brake_command(packer, CAN, apply_brake, pump_on, pcm_override, pcm_cancel_cmd, fcw, car_fingerprint, stock_brake, CP_SP,
                         clear_dash_faults=True):
  # TODO: do we loose pressure if we keep pump off for long?
  brakelights = apply_brake > 0
  brake_rq = apply_brake > 0
  pcm_fault_cmd = False

  values = {
    "CRUISE_OVERRIDE": pcm_override,
    "CRUISE_FAULT_CMD": pcm_fault_cmd,
    "CRUISE_CANCEL_CMD": pcm_cancel_cmd,
    "COMPUTER_BRAKE_REQUEST": brake_rq,
    "SET_ME_1": 1,
    "BRAKE_LIGHTS": brakelights,
    # Clear Dashboard Fault Codes ON: suppress the stock FCW chime/flag entirely.
    # OFF: stock openpilot behavior (chime + FCW passthrough on forward collision warning).
    "CHIME": 0 if clear_dash_faults else (stock_brake["CHIME"] if fcw else 0),  # send the chime for stock fcw
    "FCW": 0 if clear_dash_faults else (fcw << 1),  # TODO: Why are there two bits for fcw?
    "AEB_REQ_1": 0,
    "AEB_REQ_2": 0,
    "AEB_STATUS": 0,
  }

  if CP_SP.flags & HondaFlagsSP.NIDEC_HYBRID:
    values["COMPUTER_BRAKE_HYBRID"] = apply_brake
    values["BRAKE_PUMP_REQUEST_HYBRID"] = apply_brake > 0
  else:
    values["COMPUTER_BRAKE"] = apply_brake
    values["BRAKE_PUMP_REQUEST"] = pump_on

  return packer.make_can_msg("BRAKE_COMMAND", CAN.pt, values)


def create_acc_commands(packer, CAN, enabled, active, accel, gas, stopping_counter, car_fingerprint, gas_force):

  commands = []
  min_gas_accel = CarControllerParams.BOSCH_GAS_LOOKUP_BP[0]

  control_on = 5 if enabled else 0
  gas_command = gas if active and gas_force > min_gas_accel else -30000
  accel_command = accel if active else 0
  braking = 1 if active and gas_force < min_gas_accel else 0
  standstill = 1 if active and stopping_counter > 0 else 0
  standstill_release = 1 if active and stopping_counter == 0 else 0

  # common ACC_CONTROL values
  acc_control_values = {
    'ACCEL_COMMAND': accel_command,
    'STANDSTILL': standstill,
    'BRAKE_REQUEST': braking,
  }

  if car_fingerprint in HONDA_BOSCH_RADARLESS:
    acc_control_values.update({
      "CONTROL_ON": enabled,
    })
  else:
    acc_control_values.update({
      # setting CONTROL_ON causes car to set POWERTRAIN_DATA->ACC_STATUS = 1
      "CONTROL_ON": control_on,
      "GAS_COMMAND": gas_command,  # used for gas
      "BRAKE_LIGHTS": braking,
      "STANDSTILL_RELEASE": standstill_release,
    })
    acc_control_on_values = {
      "SET_TO_3": 0x03,
      "CONTROL_ON": enabled,
      "SET_TO_FF": 0xff,
      "SET_TO_75": 0x75,
      "SET_TO_30": 0x30,
    }
    commands.append(packer.make_can_msg("ACC_CONTROL_ON", CAN.pt, acc_control_on_values))

  commands.append(packer.make_can_msg("ACC_CONTROL", CAN.pt, acc_control_values))
  return commands


def create_steering_control(packer, CAN, apply_torque, lkas_active, tja_control):
  values = {
    "STEER_TORQUE": apply_torque if lkas_active else 0,
    "STEER_TORQUE_REQUEST": lkas_active,
  }

  if tja_control:
    values["STEER_DOWN_TO_ZERO"] = lkas_active

  return packer.make_can_msg("STEERING_CONTROL", CAN.lkas, values)


def create_bosch_supplemental_1(packer, CAN):
  # non-active params
  values = {
    "SET_ME_X04": 0x04,
    "SET_ME_X80": 0x80,
    "SET_ME_X10": 0x10,
  }
  return packer.make_can_msg("BOSCH_SUPPLEMENTAL_1", CAN.lkas, values)


# Alternative Dashboard Speed Design (HondaAltDashboardSpeed param):
# what is shown in the cluster's set-speed slot.
ALT_SPEED_STOCK = 0
ALT_SPEED_LEAD = 1     # lead speed (mph, whole numbers); "Stopped" below 1 mph, "--" with no lead
ALT_SPEED_GPS = 2      # comma's own true speed (vEgo)
ALT_SPEED_CLUSTER = 3  # exactly what the dash cluster reads (vEgoCluster)

# Alternative Dashboard Distance Design (HondaAltDashboardDistance param):
# what drives the distance bars / mini car.
ALT_DIST_STOCK = 0
ALT_DIST_RADAR = 1     # bars close in as the lead approaches
ALT_DIST_VELOCITY = 2  # bars push out under acceleration, pull in under braking


def _alt_dashboard_hud_distance(lead_visible, lead_distance_m):
  # Map lead range to Honda's distance bars so they "close in" as the lead approaches.
  # Cluster mapping: value 0 -> 4 bars (far/none), 1 -> 1 bar, 2 -> 2 bars, 3 -> 3 bars.
  if not lead_visible or lead_distance_m <= 0.0:
    return 0       # no / far lead -> 4 bars
  if lead_distance_m < 10.0:
    return 1       # very close -> 1 bar
  if lead_distance_m < 20.0:
    return 2       # 2 bars
  if lead_distance_m < 30.0:
    return 3       # 3 bars
  return 0         # >= 30 m -> 4 bars


def _alt_dashboard_accel_distance(accel):
  # Whimsical accelerometer on the distance bars: accelerating pushes them out (more
  # bars), braking pulls them in (fewer). Cluster: value 0 -> 4 bars, 3 -> 3, 2 -> 2, 1 -> 1.
  if accel >= 0.6:
    return 0       # strong accel -> 4 bars (pushed out)
  if accel >= 0.15:
    return 3       # mild accel -> 3 bars
  if accel > -0.15:
    return 2       # steady -> 2 bars
  return 1         # braking -> 1 bar (pulled in)


def create_acc_hud(packer, bus, CP, enabled, pcm_speed, pcm_accel, hud_control, hud_v_cruise, is_metric, acc_hud, speed_control,
                   speed_design=ALT_SPEED_STOCK, distance_design=ALT_DIST_STOCK,
                   sub_mode_active=False, blink_on=True, max_flash_active=False,
                   lead_speed_display=0.0, gps_speed_display=0.0, cluster_speed_display=0.0, vehicle_accel=0.0,
                   clear_dash_faults=True):
  if sub_mode_active:
    # Dynamic HUD (Cruise Button Sub-Mode): force the stock layout while active.
    # The bars light up with the CURRENT personality regardless of engagement state,
    # the set speed shows if cruise is engaged, and everything except the lane lines
    # blinks at the sub-mode's warning rate (handled via sub_mode_blink_on).
    speed_design = ALT_SPEED_STOCK
    distance_design = ALT_DIST_STOCK

  cruise_speed = hud_v_cruise
  hud_distance = hud_control.leadDistanceBars % 4  # 1/2/3 bars; econ -> 4 wraps to 0 which the cluster shows as 4 bars
  mini_car = 1 if enabled else 0
  hud_lead = 2 if enabled and hud_control.leadVisible else 1 if enabled else 0
  # The distance bars only draw with ACC_ON: send it only on the Stock distance
  # design (stock engaged behavior) or during the Cruise Button Sub-Mode below.
  send_acc_on = distance_design == ALT_DIST_STOCK
  acc_on = int(enabled)

  if speed_design == ALT_SPEED_LEAD:
    # Lead speed in place of set speed. mph values are always whole numbers.
    if not hud_control.leadVisible:
      cruise_speed = 253  # "--": no lead present
    elif hud_control.leadVLead < CV.MPH_TO_MS:  # lead below 1 mph
      cruise_speed = 252  # "Stopped"
    else:
      cruise_speed = min(251, max(0, int(round(lead_speed_display))))  # keep clear of 252/253
  elif speed_design == ALT_SPEED_GPS:
    cruise_speed = min(251, max(0, int(round(gps_speed_display))))
  elif speed_design == ALT_SPEED_CLUSTER:
    cruise_speed = min(251, max(0, int(round(cluster_speed_display))))

  if distance_design == ALT_DIST_RADAR:
    hud_distance = _alt_dashboard_hud_distance(hud_control.leadVisible, hud_control.leadDistance)
  elif distance_design == ALT_DIST_VELOCITY:
    hud_distance = _alt_dashboard_accel_distance(vehicle_accel)

  # Alt designs stay on the cluster permanently, not just while engaged: the mini
  # car must be lit permanently (it renders HUD_DISTANCE moves) and the lead car
  # icon (HUD_LEAD) must track lead presence regardless of engagement state.
  if speed_design != ALT_SPEED_STOCK or distance_design != ALT_DIST_STOCK:
    mini_car = 1
    hud_lead = 2 if hud_control.leadVisible else 1

  if sub_mode_active:
    # Bars show the current personality no matter the engagement state, blinking.
    send_acc_on = True
    acc_on = 1 if blink_on else 0
    mini_car = 1 if blink_on else (1 if enabled else 0)
    if not (enabled and blink_on):
      cruise_speed = 255  # blank: set speed only shows while engaged, and blinks too

  # System speed-limit flash: blink ONLY the set-speed digits (priority, independent of the sub-mode).
  # Shares blink_on with the sub-mode so the two never desync; touches nothing else on the cluster.
  if max_flash_active and enabled and speed_design == ALT_SPEED_STOCK and not blink_on:
    cruise_speed = 255

  acc_hud_values = {
    'CRUISE_SPEED': cruise_speed,
    'ENABLE_MINI_CAR': mini_car,
    # only moves the lead car without ACC_ON
    'HUD_DISTANCE': hud_distance,
    'IMPERIAL_UNIT': int(not is_metric),
    'HUD_LEAD': hud_lead,
    'SET_ME_X01_2': 1,
  }

  if CP.carFingerprint in HONDA_BOSCH:
    if send_acc_on:
      acc_hud_values['ACC_ON'] = acc_on
    acc_hud_values['FCM_OFF'] = 1
    acc_hud_values['FCM_OFF_2'] = 1
  else:
    # Shows the distance bars, TODO: stock camera shows updates temporarily while disabled
    if send_acc_on:
      acc_hud_values['ACC_ON'] = acc_on
    acc_hud_values['PCM_SPEED'] = pcm_speed * CV.MS_TO_KPH
    acc_hud_values['PCM_GAS'] = pcm_accel
    acc_hud_values['SET_ME_X01'] = speed_control if (CP.flags & HondaFlags.HYBRID) and (CP.carFingerprint in (CAR.ACURA_MDX_3G_MMR)) else 1
    if clear_dash_faults:
      # Clear Dashboard Fault Codes ON: force the FCM/icon fault bits off (Dashboard
      # Cluster Behavior Module - lets a car with a dead/absent stock camera run clean).
      acc_hud_values['FCM_OFF'] = 0
      acc_hud_values['FCM_OFF_2'] = 0
      acc_hud_values['FCM_PROBLEM'] = 0
      acc_hud_values['ICONS'] = 0
    else:
      # OFF: stock openpilot behavior - pass the camera's own values through.
      acc_hud_values['FCM_OFF'] = acc_hud['FCM_OFF']
      acc_hud_values['FCM_OFF_2'] = acc_hud['FCM_OFF_2']
      acc_hud_values['FCM_PROBLEM'] = acc_hud['FCM_PROBLEM']
      acc_hud_values['ICONS'] = acc_hud['ICONS']

  return packer.make_can_msg("ACC_HUD", bus, acc_hud_values)


def create_camera_messages(packer, bus):
  # CAMERA_MESSAGES (0x35E) is normally broadcast by the stock camera. With a
  # dead/absent camera the cluster raises "Auto High Beam System Problem" when this
  # message times out - there is no fault flag to clear anywhere, the message just
  # has to keep existing. Spoof it with high beams reported off/inactive.
  values = {
    'HIGHBEAMS_ON': 0,
    'AUTO_HIGHBEAMS_ACTIVE': 0,
  }
  return packer.make_can_msg("CAMERA_MESSAGES", bus, values)


def create_lkas_hud(packer, bus, CP, hud_control, lat_active, steering_available, reduced_steering, alert_steer_required, lkas_hud, dashed_lanes,
                    steer_maxed):
  commands = []

  lkas_hud_values = {
    'LKAS_READY': 1,
    'LKAS_STATE_CHANGE': 1,
    'STEERING_REQUIRED': alert_steer_required,
    'SOLID_LANES': lat_active,
    'DASHED_LANES': dashed_lanes,
    'BEEP': 0,
  }

  if CP.carFingerprint in (HONDA_BOSCH_RADARLESS | HONDA_BOSCH_CANFD):
    lkas_hud_values['LANE_LINES'] = 3
    lkas_hud_values['DASHED_LANES'] = lat_active

    # car likely needs to see LKAS_PROBLEM fall within a specific time frame, so forward from camera
    # TODO: needed for Bosch CAN FD?
    if CP.carFingerprint in HONDA_BOSCH_RADARLESS:
      lkas_hud_values['LKAS_PROBLEM'] = lkas_hud['LKAS_PROBLEM']

  if not (CP.flags & HondaFlags.BOSCH_EXT_HUD):
    lkas_hud_values['RDM_OFF'] = 1
    lkas_hud_values['LANE_ASSIST_BEEP_OFF'] = 1

  # New HUD concept for selected Bosch cars, overwrites some of the above
  # TODO: make global across all Honda if feedback is favorable
  if CP.carFingerprint in HONDA_BOSCH_ALT_RADAR:
    lkas_hud_values['DASHED_LANES'] = steering_available and lat_active
    lkas_hud_values['SOLID_LANES'] = lat_active

  if CP.flags & HondaFlags.BOSCH_EXT_HUD and not CP.openpilotLongitudinalControl:
    commands.append(packer.make_can_msg('LKAS_HUD_A', bus, lkas_hud_values))
    commands.append(packer.make_can_msg('LKAS_HUD_B', bus, lkas_hud_values))
  else:
    commands.append(packer.make_can_msg('LKAS_HUD', bus, lkas_hud_values))

  return commands


def create_radar_hud(packer, bus):
  radar_hud_values = {
    'CMBS_OFF': 0x01,
    'SET_TO_1': 0x01,
  }

  return packer.make_can_msg('RADAR_HUD', bus, radar_hud_values)


def create_legacy_brake_command(packer, bus):
  return packer.make_can_msg("LEGACY_BRAKE_COMMAND", bus, {})


def spam_buttons_command(packer, CAN, button_val, car_fingerprint):
  values = {
    'CRUISE_BUTTONS': button_val,
    'CRUISE_SETTING': 0,
  }
  # send buttons to camera on radarless (camera does ACC) cars
  bus = CAN.camera if car_fingerprint in HONDA_BOSCH_RADARLESS else CAN.pt
  return packer.make_can_msg("SCM_BUTTONS", bus, values)


def honda_checksum(address: int, sig, d: bytearray) -> int:
  s = 0
  extended = address > 0x7FF
  addr = address
  while addr:
    s += addr & 0xF
    addr >>= 4
  for i in range(len(d)):
    x = d[i]
    if i == len(d) - 1:
      x >>= 4
    s += (x & 0xF) + (x >> 4)
  s = 8 - s
  if extended:
    s += 3
  return s & 0xF
