from opendbc.car import CanBusBase
from opendbc.car.common.conversions import Conversions as CV
from opendbc.car.honda.values import (CAR, HONDA_BOSCH, HONDA_BOSCH_ALT_RADAR, HONDA_BOSCH_CANFD,
                                      HONDA_BOSCH_RADARLESS, CarControllerParams, HondaFlags)
from opendbc.sunnypilot.car.honda.can import apply_brake_alert_policy, is_braking, update_acc_hud_values
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
    if CP is not None and CP.flags & HondaFlags.BOSCH and not (CP.flags & (HondaFlags.BOSCH_RADARLESS | HondaFlags.BOSCH_CANFD)):
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


def create_brake_command(packer, CAN, apply_brake, pump_on, pcm_override, pcm_cancel_cmd, fcw, stock_brake, CP_SP, clear_dash_faults=True):
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
    "CHIME": stock_brake["CHIME"] if fcw else 0,  # send the chime for stock fcw
    "FCW": fcw << 1,  # TODO: Why are there two bits for fcw?
    "AEB_REQ_1": 0,
    "AEB_REQ_2": 0,
    "AEB_STATUS": 0,
  }
  apply_brake_alert_policy(values, fcw, stock_brake, clear_dash_faults)

  if CP_SP.flags & HondaFlagsSP.NIDEC_HYBRID:
    values["COMPUTER_BRAKE_HYBRID"] = apply_brake
    values["BRAKE_PUMP_REQUEST_HYBRID"] = apply_brake > 0
  else:
    values["COMPUTER_BRAKE"] = apply_brake
    values["BRAKE_PUMP_REQUEST"] = pump_on

  return packer.make_can_msg("BRAKE_COMMAND", CAN.pt, values)


def create_acc_commands(packer, CAN, enabled, active, accel, gas, stopping_counter, CP, gas_force):
  commands = []
  min_gas_accel = CarControllerParams.BOSCH_GAS_LOOKUP_BP[0]

  control_on = 5 if enabled else 0
  gas_command = gas if active and gas_force > min_gas_accel else -30000
  accel_command = accel if active else 0
  braking = int(is_braking(active, accel))
  standstill = 1 if active and stopping_counter > 0 else 0
  standstill_release = 1 if active and stopping_counter == 0 else 0

  # common ACC_CONTROL values
  acc_control_values = {
    'ACCEL_COMMAND': accel_command,
    'STANDSTILL': standstill,
  }

  if CP.flags & HondaFlags.BOSCH_RADARLESS:
    acc_control_values.update({
      "CONTROL_ON": enabled,
      # required whenever braking for Hybrid and Bosch Alt Brake vehicles, allow idle stop after 4 seconds (50 Hz) for other vehicles
      "COMPUTER_BRAKE_ASSIST": braking if CP.flags & (HondaFlags.HYBRID | HondaFlags.BOSCH_ALT_BRAKE) else stopping_counter > 200,
    })
  else:
    acc_control_values.update({
      # setting CONTROL_ON causes car to set POWERTRAIN_DATA->ACC_STATUS = 1
      "CONTROL_ON": control_on,
      "GAS_COMMAND": gas_command,  # used for gas
      "BRAKE_LIGHTS": braking,
      "BRAKE_REQUEST": braking,
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


def create_acc_hud(packer, bus, CP, enabled, pcm_speed, pcm_accel, hud_control, hud_v_cruise, is_metric, acc_hud, speed_control,
                   alphalong, nrdr_options=None):
  acc_hud_values = {
    'CRUISE_SPEED': hud_v_cruise,
    'ENABLE_MINI_CAR': 1 if enabled else 0,
    # only moves the lead car without ACC_ON
    'HUD_DISTANCE': hud_control.leadDistanceBars,  # wraps to 0 at 4 bars
    'IMPERIAL_UNIT': int(not is_metric),
    'HUD_LEAD': 2 if enabled and hud_control.leadVisible else 1 if enabled else 0,
    'SET_ME_X01_2': 1,
  }

  if CP.flags & HondaFlags.BOSCH_CANFD:
    acc_hud_values['SET_ME_X01'] = int(enabled and (bool(acc_hud_values['HUD_LEAD']) or (pcm_accel < 0.2)))
    acc_hud_values['SET_ME_X01_2'] = int(enabled and (bool(acc_hud_values['HUD_LEAD']) or (pcm_accel < 0.2)))

  if CP.flags & HondaFlags.BOSCH:
    acc_hud_values['ACC_ON'] = int(enabled)
    acc_hud_values['FCM_OFF'] = bool(0)
    acc_hud_values['FCM_OFF_2'] = bool(0)
  else:
    # Shows the distance bars, TODO: stock camera shows updates temporarily while disabled
    acc_hud_values['ACC_ON'] = int(enabled)
    acc_hud_values['PCM_SPEED'] = pcm_speed * CV.MS_TO_KPH
    acc_hud_values['PCM_GAS'] = pcm_accel
    acc_hud_values['SET_ME_X01'] = speed_control if (CP.flags & HondaFlags.HYBRID) and (CP.carFingerprint in (CAR.ACURA_MDX_3G_MMR)) else 1
    acc_hud_values['FCM_OFF'] = acc_hud['FCM_OFF']
    acc_hud_values['FCM_OFF_2'] = acc_hud['FCM_OFF_2']
    acc_hud_values['FCM_PROBLEM'] = acc_hud['FCM_PROBLEM']
    acc_hud_values['ICONS'] = acc_hud['ICONS']

  acc_hud_values = update_acc_hud_values(acc_hud_values, CP, enabled, pcm_speed, pcm_accel, hud_control,
                                          hud_v_cruise, acc_hud, speed_control, nrdr_options)
  return packer.make_can_msg("ACC_HUD", bus, acc_hud_values)


def create_lkas_hud(packer, bus, CP, hud_control, lat_active, steering_available, reduced_steering, alert_steer_required, lkas_hud, dashed_lanes,
                    steer_maxed, CS, lkas_state_change=None):
  commands = []

  lkas_hud_values = {
    'LKAS_READY': 1,
    'LKAS_STATE_CHANGE': 1,
    'STEERING_REQUIRED': alert_steer_required,
    'SOLID_LANES': lat_active,
    'DASHED_LANES': dashed_lanes,
    'BEEP': 0,
  }

  # MDX CAN FD factory logs show the stock camera holds LKAS_STATE_CHANGE low, pulsing it high for ~3s
  # only when the HUD state changes; holding it high permanently suppresses the dash lane-line rendering.
  if lkas_state_change is not None:
    lkas_hud_values['LKAS_STATE_CHANGE'] = int(lkas_state_change)

  if CP.flags & (HondaFlags.BOSCH_RADARLESS | HondaFlags.BOSCH_CANFD):
    lkas_hud_values['LANE_LINES'] = 3

    # car likely needs to see LKAS_PROBLEM fall within a specific time frame, so forward from camera
    # TODO: needed for Bosch CAN FD?
    if CP.flags & HondaFlags.BOSCH_RADARLESS:
      lkas_hud_values['LKAS_PROBLEM'] = lkas_hud['LKAS_PROBLEM']

    if CP.flags & (HondaFlags.BOSCH_RADARLESS | HondaFlags.BOSCH_CANFD):
      lkas_hud_values['LKAS_PROBLEM'] = CS.out.steerFaultPermanent # CS.lkas_hud['LKAS_PROBLEM']
      if CP.flags & HondaFlags.BOSCH_RADARLESS:
        lkas_hud_values['DASHED_LANES'] = 1  # show gray lanes when disengaged
      else:
        # CAN FD: dashed lanes are the MADS armed indication (MadsCarController sets dashed_lanes to
        # mads.enabled and not latActive, which is not standstill-gated - so parked/standstill LKAS
        # button presses produce cluster feedback; latActive alone stays 0 below 0.3 m/s and armed
        # toggles would render nothing). ORed with lat_active while steering so the engaged payload
        # keeps SOLID and DASHED set together (0x44), byte-matching the stock camera's lanes-on state.
        lkas_hud_values['DASHED_LANES'] = dashed_lanes or lat_active

    if CP.flags & HondaFlags.BOSCH_CANFD:
      # Don't let steer saturation flicker SOLID_LANES: every payload change must coincide with an
      # LKAS_STATE_CHANGE pulse (see carcontroller), and a 10Hz flicker would keep the pulse
      # re-triggering, which suppresses the dash lane lines.
      # Keyed on lat_active, NOT hud_control.lanesVisible (== CC.enabled): under sunnypilot MADS
      # the lateral control stays engaged when a brake press disengages ACC, and the dash LKAS
      # indication must follow the lateral state or the driver can't tell MADS is still steering
      # (drivers pressing the LKAS button to "re-engage" silently toggled MADS off). On forks
      # without MADS, lat_active == enabled while moving, so this stays equivalent there.
      lkas_hud_values['SOLID_LANES'] = lat_active

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


def spam_buttons_command(packer, CAN, cruise_button, cruise_setting, ambient_light, CP, bus=None):
  values = {
    'CRUISE_BUTTONS': cruise_button,
    'CRUISE_SETTING': cruise_setting,
    # the camera consumes this byte too (adaptive high beam); echo the SCM's live value
    'AMBIENT_LIGHT_MAYBE': ambient_light,
  }
  if bus is None:
    # send buttons to camera on radarless (camera does ACC) cars
    bus = CAN.camera if CP.flags & HondaFlags.BOSCH_RADARLESS else CAN.pt
  return packer.make_can_msg("SCM_BUTTONS", bus, values)


def create_radar_hud_canfd(packer, bus, acc, acc_pulse=False):
  values = {
    # The stock radar only raises this bit in short (~2-6 s) bursts right after ACC engages/resumes,
    # then drops it for the rest of the drive; it is never held for a whole engagement.
    'CMBS_ENABLED_MAYBE': 1 if (acc and acc_pulse) else 0,
    'ACC_ON': acc,
    'SET_ME_X01': 0x01,
    'SET_ME_X01_2': 0x01,
  }
  return packer.make_can_msg("RADAR_HUD_CANFD", bus, values)


def create_canfd_supplemental(packer, bus):
  values = {
    'SET_ME_X01': 0x01,
    'SET_ME_X41': 0x41,
  }
  return packer.make_can_msg("BOSCH_SUPPLEMENTAL_CANFD", bus, values)


# Radar MUX banks: 1-10, 17-26, 33-42, 49-58. Each bank is a fresh sweep of path points.
RADAR_MUX_BANK_STARTS = (1, 17, 33, 49)
# "no detection" sentinel the stock radar uses for an empty path point / object slot
PATH_OFFSET_INVALID = 2047


def _lane_path_offsets(radar_mux):
  # The stock radar reports path points as a sweep within each MUX bank: the first point (bank start)
  # is 0, the second has the first two offsets valid (0) and the rest invalid, and the remaining points
  # are fully invalid. Match that exact per-MUX pattern so the camera sees a consistent empty path.
  pos = next((radar_mux - start for start in RADAR_MUX_BANK_STARTS if start <= radar_mux <= start + 9), 0)
  if pos == 0:
    return (0, 0, 0, 0)
  if pos == 1:
    return (0, 0, PATH_OFFSET_INVALID, PATH_OFFSET_INVALID)
  return (PATH_OFFSET_INVALID,) * 4


def create_canfd_50hz_radar_messages(packer, bus, radar_mux):
  commands = []

  offsets = _lane_path_offsets(radar_mux)
  lane_path_values = {
    'MUX': radar_mux,
    'PATH_OFFSET_1': offsets[0],
    'PATH_OFFSET_2': offsets[1],
    'PATH_OFFSET_3': offsets[2],
    'PATH_OFFSET_4': offsets[3],
  }
  commands.append(packer.make_can_msg('LANE_PATH', bus, lane_path_values))

  # Empty-object-slot sentinel the stock radar transmits (no lead/object): max distances, CAR_TYPE=-1.
  hud_objects_values = {
    'MUX': radar_mux,
    'OBJECT_ID': 0,
    'IS_LEAD_CAR': 0,
    'CAR_TYPE': -1,
    'ROTATION': -128,
    'LONG_DIST': 196.9,
    'LAT_DIST': 204.7,
  }
  commands.append(packer.make_can_msg('HUD_OBJECTS', bus, hud_objects_values))

  return commands


def create_canfd_5hz_radar_messages(packer, bus, radar_ref_cntr, lane_path_length=6, left_lane=0, right_lane=0):
  commands = []

  radar_lead_values = {
    'CNTR_REF': radar_ref_cntr,
    'SET_ME_X01': 0x01,
    # stock radar transmits a constant 140 here (confirmed from logs); 120 causes a camera mismatch
    'TARGET_SPEED_MAYBE': 140,
    # stock: per-side lane-line detection status (3 = line present, 0 = none), in lockstep with the
    # camera's LKAS_HUD LANE_LINES bits. This is the CAN FD counterpart of radarless LKAS_HUD_2's
    # LEFT_LANE/RIGHT_LANE; the dash does not draw lane lines while both are 0.
    'LEFT_LANE': left_lane,
    'RIGHT_LANE': right_lane,
    # stock: number of valid points in the current LANE_PATH sweep (6 = idle). The dash cross-checks
    # this against the path's in-band 2047 terminator; a mismatch suppresses the lane-line rendering.
    'LANE_PATH_LENGTH': lane_path_length,
  }
  commands.append(packer.make_can_msg('RADAR_LEAD', bus, radar_lead_values))

  radar_lead2_values = {
    'SET_ME_X88': 136,
    'SET_ME_X78': 120,
    'LEAD_DISTANCE_MAYBE': 0,
  }
  commands.append(packer.make_can_msg('RADAR_LEAD2', bus, radar_lead2_values))

  return commands


def honda_checksum(address: int, sig, d: bytearray) -> int:
  s = 0
  extended = address > 0x7FF
  # Higher extended-ID range adds 10, lower adds 3. TODO: confirm the exact boundary.
  high_extended = address > 0x100000
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
    s += 10 if high_extended else 3
  return s & 0xF
