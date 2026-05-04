import copy
import numpy as np
from opendbc.car import CanBusBase, CanData
from opendbc.car.crc import CRC16_XMODEM
from opendbc.car.hyundai.values import HyundaiFlags


def _set_value(msg: bytearray, sig, ival: int) -> None:
  i = sig.lsb // 8
  bits = sig.size
  if sig.size < 64:
    ival &= (1 << sig.size) - 1
  while 0 <= i < len(msg) and bits > 0:
    shift = sig.lsb % 8 if (sig.lsb // 8) == i else 0
    size = min(bits, 8 - shift)
    mask = ((1 << size) - 1) << shift
    msg[i] &= ~mask
    msg[i] |= (ival & ((1 << size) - 1)) << shift
    bits -= size
    ival >>= size
    i = i + 1 if sig.is_little_endian else i - 1


class CanBus(CanBusBase):
  def __init__(self, CP, fingerprint=None, lka_steering=None) -> None:
    super().__init__(CP, fingerprint)

    if lka_steering is None:
      lka_steering = CP.flags & HyundaiFlags.CANFD_LKA_STEERING.value if CP is not None else False

    # On the CAN-FD platforms, the LKAS camera is on both A-CAN and E-CAN. LKA steering cars
    # have a different harness than the LFA steering variants in order to split
    # a different bus, since the steering is done by different ECUs.
    self._a, self._e = 1, 0
    if lka_steering:
      self._a, self._e = 0, 1

    self._a += self.offset
    self._e += self.offset
    self._cam = 2 + self.offset

  @property
  def ECAN(self):
    return self._e

  @property
  def ACAN(self):
    return self._a

  @property
  def CAM(self):
    return self._cam


def _update_checksum(packer, address: int, dat: bytearray) -> None:
  msg = packer.dbc.addr_to_msg[address]
  sig_checksum = next((s for s in msg.sigs.values() if s.calc_checksum is not None), None)
  if sig_checksum is None:
    return

  checksum = sig_checksum.calc_checksum(address, sig_checksum, dat)
  _set_value(dat, sig_checksum, checksum)


def _create_angle_lfa_msg(packer, CAN, values, apply_angle: float, lat_active: bool, torque_reduction_gain: float):
  address = packer.dbc.name_to_msg["LFA"].address
  dat = packer.pack(address, values)

  desired_angle = int(round(np.clip(apply_angle, -819.1, 819.1) * 10.0))
  if desired_angle < 0:
    desired_angle += 1 << 14

  dat[9] = (dat[9] & ~0x30) | (((2 if lat_active else 1) & 0x3) << 4)
  dat[10] = (dat[10] & 0x03) | ((desired_angle & 0x3F) << 2)
  dat[11] = (desired_angle >> 6) & 0xFF
  dat[12] = int(np.clip(round(torque_reduction_gain / 0.004), 0, 250))
  _update_checksum(packer, address, dat)

  return address, bytes(dat), CAN.ECAN


def _create_angle_adas_cmd_msg(packer, CAN, apply_angle: float, lat_active: bool, torque_reduction_gain: float):
  values = {
    "ADAS_ActvACISta": 0,
    "ADAS_ActvACILvl2Sta": 2 if lat_active else 1,
    "ADAS_StrAnglReqVal": apply_angle,
    "ADAS_ACIAnglTqRedcGainVal": torque_reduction_gain if lat_active else 0.0,
    "FCA_ESA_ActvSta": 0,
    "FCA_ESA_TqBstGainVal": 0.0,
  }
  return packer.make_can_msg("ADAS_CMD_35_10ms", CAN.ECAN, values)


def create_steering_messages(packer, CP, CAN, enabled, lat_active, apply_torque, apply_angle,
                             lfa_base_values=None, lkas_base_values=None):
  control_values = {
    "LKA_MODE": 2,
    "LKA_ICON": 2 if enabled else 1,
    "TORQUE_REQUEST": 0 if CP.flags & HyundaiFlags.CANFD_ANGLE_STEERING else apply_torque,
    "LKA_ASSIST": 0,
    "STEER_REQ": 0 if CP.flags & HyundaiFlags.CANFD_ANGLE_STEERING else (1 if lat_active else 0),
    "STEER_MODE": 0,
  }

  if lkas_base_values:
    lkas_values = {k: v for k, v in lkas_base_values.items() if k not in ("CHECKSUM", "COUNTER")}
    lkas_values.update(control_values)
  else:
    lkas_values = copy.copy(control_values)
    lkas_values["LKA_AVAILABLE"] = 0

  if lfa_base_values:
    # Preserve stock UI/status fields and only override the actuation-relevant signals.
    lfa_values = {k: v for k, v in lfa_base_values.items() if k not in ("CHECKSUM", "COUNTER")}
    lfa_values.update(control_values)
  else:
    lfa_values = copy.copy(control_values)
    lfa_values["HAS_LANE_SAFETY"] = 0  # hide LKAS settings
    lfa_values["NEW_SIGNAL_1"] = 0
    lfa_values["NEW_SIGNAL_2"] = 0
    lfa_values["DAMP_FACTOR"] = 100  # can potentially tuned for better perf [3, 200]

  if CP.flags & HyundaiFlags.CANFD_ANGLE_STEERING and CP.flags & HyundaiFlags.CANFD_LKA_STEERING_ALT:
    lkas_values["ADAS_StrAnglReqVal"] = apply_angle
    lkas_values["LKAS_ANGLE_ACTIVE"] = 2 if lat_active else 1
    lkas_values["ADAS_ACIAnglTqRedcGainVal"] = apply_torque if lat_active else 0.0

  ret = []
  if CP.flags & HyundaiFlags.CANFD_LKA_STEERING:
    lkas_msg = "LKAS_ALT" if CP.flags & HyundaiFlags.CANFD_LKA_STEERING_ALT else "LKAS"
    if CP.openpilotLongitudinalControl:
      ret.append(packer.make_can_msg("LFA", CAN.ECAN, lfa_values))
    ret.append(packer.make_can_msg(lkas_msg, CAN.ACAN, lkas_values))
  else:
    if CP.flags & HyundaiFlags.CANFD_ANGLE_STEERING:
      if CP.flags & HyundaiFlags.SEND_LFA:
        ret.append(_create_angle_adas_cmd_msg(packer, CAN, apply_angle, lat_active, apply_torque))
      else:
        ret.append(_create_angle_lfa_msg(packer, CAN, lfa_values, apply_angle, lat_active, apply_torque))
    else:
      ret.append(packer.make_can_msg("LFA", CAN.ECAN, lfa_values))

  return ret


def create_suppress_lfa(packer, CAN, lfa_block_msg, lka_steering_alt):
  suppress_msg = "CAM_0x362" if lka_steering_alt else "CAM_0x2a4"
  msg_bytes = 32 if lka_steering_alt else 24

  values = {f"BYTE{i}": lfa_block_msg[f"BYTE{i}"] for i in range(3, msg_bytes) if i != 7}
  values["COUNTER"] = lfa_block_msg["COUNTER"]
  values["SET_ME_0"] = 0
  values["SET_ME_0_2"] = 0
  values["LEFT_LANE_LINE"] = 0
  values["RIGHT_LANE_LINE"] = 0
  return packer.make_can_msg(suppress_msg, CAN.ACAN, values)


def create_buttons(packer, CP, CAN, cnt, btn):
  values = {
    "COUNTER": cnt,
    "SET_ME_1": 1,
    "CRUISE_BUTTONS": btn,
  }

  bus = CAN.ECAN if CP.flags & HyundaiFlags.CANFD_LKA_STEERING else CAN.CAM
  return packer.make_can_msg("CRUISE_BUTTONS", bus, values)


def create_acc_cancel(packer, CP, CAN, cruise_info_copy):
  # TODO: why do we copy different values here?
  if CP.flags & HyundaiFlags.CANFD_CAMERA_SCC.value:
    values = {s: cruise_info_copy[s] for s in [
      "COUNTER",
      "CHECKSUM",
      "NEW_SIGNAL_1",
      "MainMode_ACC",
      "ACCMode",
      "ZEROS_9",
      "CRUISE_STANDSTILL",
      "ZEROS_5",
      "DISTANCE_SETTING",
      "VSetDis",
    ]}
  else:
    values = {s: cruise_info_copy[s] for s in [
      "COUNTER",
      "CHECKSUM",
      "ACCMode",
      "VSetDis",
      "CRUISE_STANDSTILL",
    ]}
  values.update({
    "ACCMode": 4,
    "aReqRaw": 0.0,
    "aReqValue": 0.0,
  })
  return packer.make_can_msg("SCC_CONTROL", CAN.ECAN, values)


def create_lfahda_cluster(packer, CAN, enabled, base_values=None):
  values = {k: v for k, v in base_values.items() if k not in ("CHECKSUM", "COUNTER")} if base_values else {}
  values.update({
    "HDA_ICON": 1 if enabled else 0,
    "LFA_ICON": 2 if enabled else 0,
  })
  return packer.make_can_msg("LFAHDA_CLUSTER", CAN.ECAN, values)


def create_blindspot_status_messages(packer, CAN, rear_values, front_corner_values,
                                     left_blindspot=False, right_blindspot=False,
                                     left_blinker=False, right_blinker=False):
  # Reuse the last known-good payload but regenerate the rolling counter/checksum.
  rear = {k: v for k, v in rear_values.items() if k not in ("CHECKSUM", "COUNTER")}
  front = {k: v for k, v in front_corner_values.items() if k not in ("CHECKSUM", "COUNTER")}
  left_state = 2 if left_blindspot and left_blinker else (1 if left_blindspot else 0)
  right_state = 2 if right_blindspot and right_blinker else (1 if right_blindspot else 0)

  rear["BCW_Sta"] = int(left_blindspot or right_blindspot)
  rear["BCW_LtIndSta"] = left_state
  rear["BCW_RtIndSta"] = right_state
  rear["BCW_IndSta"] = max(left_state, right_state)
  rear["OSMrrLamp_LtIndSta"] = left_state
  rear["OSMrrLamp_RtIndSta"] = right_state
  # Keep the older fields aligned where they still correlate on some platforms.
  rear["FL_INDICATOR"] = left_state
  rear["FR_INDICATOR"] = right_state
  if "NEW_SIGNAL_3" not in front:
    front["NEW_SIGNAL_3"] = 1

  return [
    packer.make_can_msg("BLINDSPOTS_REAR_CORNERS", CAN.ECAN, rear),
    packer.make_can_msg("BLINDSPOTS_FRONT_CORNER_1", CAN.ECAN, front),
  ]


IONIQ_6_CLUSTER_BLINDSPOT_31A = {
  "right": (
    bytes.fromhex("fa7c10f0f0ffff03898aff0b0a8678ff000000007e0055550000000000000000"),
    bytes.fromhex("ac0e11f0f0ffff03898aff0c0a8678ff000000007e0055550000000000000000"),
    bytes.fromhex("76ce12f0f0ffff03898aff0b0a8678ff000000007e0055550000000000000000"),
    bytes.fromhex("309713f0f0ffff03898aff0b0a8678ff000000007e0055550000000000000000"),
    bytes.fromhex("d32214f0f0ffff03898aff0c0a8678ff000000007e0055550000000000000000"),
    bytes.fromhex("957b15f0f0ffff03898aff0c0a8678ff000000007e0055550000000000000000"),
  ),
  "left": (
    bytes.fromhex("851828f0f0ffff03898aff0a098678ff000000007e0055550000000000000000"),
    bytes.fromhex("c34129f0f0ffff03898aff0a098678ff000000007e0055550000000000000000"),
    bytes.fromhex("09aa2af0f0ffff03898aff0a098678ff000000007e0055550000000000000000"),
    bytes.fromhex("4ff32bf0f0ffff03898aff0a098678ff000000007e0055550000000000000000"),
    bytes.fromhex("bc6d2cf0f0ffff03898aff0a098678ff000000007e0055550000000000000000"),
    bytes.fromhex("fa342df0f0ffff03898aff0a098678ff000000007e0055550000000000000000"),
  ),
}

IONIQ_6_CLUSTER_BLINDSPOT_3B5 = {
  "right": (
    bytes.fromhex("caa95c00000000464600000000000000d7020000000069070000000000000000"),
    bytes.fromhex("8cf05d00000000464600000000000000d7020000000069070000000000000000"),
    bytes.fromhex("461b5e00000000464600000000000000d7020000000069070000000000000000"),
    bytes.fromhex("00425f00000000464600000000000000d7020000000069070000000000000000"),
  ),
  "left": (
    bytes.fromhex("2c69c500000000464600000000000000da020000000069070000000000000000"),
    bytes.fromhex("e682c600000000464600000000000000da020000000069070000000000000000"),
    bytes.fromhex("21afc800000000464600000000000000da020000000069070000000000000000"),
    bytes.fromhex("67f6c900000000464600000000000000da020000000069070000000000000000"),
  ),
}


IONIQ_6_CLUSTER_LANE_CHANGE_3C1 = {
  "right": {
    "trigger": bytes.fromhex("e910300041000000"),
    "steady": bytes.fromhex("ab20300001000000"),
  },
  "left": {
    "trigger": bytes.fromhex("3d40304010000000"),
    "steady": bytes.fromhex("3e50300000000000"),
  },
}


def create_ioniq_6_cluster_blindspot_messages(CAN, frame, left_blindspot=False, right_blindspot=False,
                                              left_blinker=False, right_blinker=False):
  side = None
  if left_blindspot and not right_blindspot:
    side = "left"
  elif right_blindspot and not left_blindspot:
    side = "right"
  elif left_blindspot and right_blindspot:
    if left_blinker and not right_blinker:
      side = "left"
    elif right_blinker and not left_blinker:
      side = "right"

  if side is None:
    return []

  ret = []
  if frame % 20 == 0:
    seq_3b5 = IONIQ_6_CLUSTER_BLINDSPOT_3B5[side]
    ret.append((0x3B5, seq_3b5[(frame // 20) % len(seq_3b5)], CAN.ECAN))
  if frame % 100 == 0:
    seq_31a = IONIQ_6_CLUSTER_BLINDSPOT_31A[side]
    ret.append((0x31A, seq_31a[(frame // 100) % len(seq_31a)], CAN.ECAN))

  return ret


def create_ioniq_6_cluster_lane_change_messages(CAN, frame, side=None, trigger=False):
  if side not in IONIQ_6_CLUSTER_LANE_CHANGE_3C1:
    return []

  if trigger:
    return [(0x3C1, IONIQ_6_CLUSTER_LANE_CHANGE_3C1[side]["trigger"], CAN.ECAN)]
  if frame % 20 == 0:
    return [(0x3C1, IONIQ_6_CLUSTER_LANE_CHANGE_3C1[side]["steady"], CAN.ECAN)]
  return []


def create_acc_control(packer, CAN, enabled, accel_last, accel, stopping, gas_override, set_speed, hud_control,
                       main_mode_acc=1, jerk_lower=None, jerk_upper=None, direct_accel=False):
  jerk = 5
  jn = jerk / 50
  if not enabled or gas_override:
    a_val, a_raw = 0, 0
  elif direct_accel:
    a_raw = accel
    a_val = accel
  else:
    a_raw = accel
    a_val = np.clip(accel, accel_last - jn, accel_last + jn)

  values = {
    "ACCMode": 0 if not enabled else (2 if gas_override else 1),
    "MainMode_ACC": main_mode_acc,
    "StopReq": 1 if stopping else 0,
    "aReqValue": a_val,
    "aReqRaw": a_raw,
    "VSetDis": set_speed,
    "JerkLowerLimit": jerk_lower if jerk_lower is not None else (jerk if enabled else 1),
    "JerkUpperLimit": jerk_upper if jerk_upper is not None else 3.0,

    "ACC_ObjDist": 1,
    "ObjValid": 0,
    "OBJ_STATUS": 2,
    "SET_ME_2": 0x4,
    "SET_ME_3": 0x3,
    "SET_ME_TMP_64": 0x64,
    "DISTANCE_SETTING": hud_control.leadDistanceBars,
  }

  return packer.make_can_msg("SCC_CONTROL", CAN.ECAN, values)


def create_spas_messages(packer, CAN, left_blink, right_blink):
  ret = []

  values = {
  }
  ret.append(packer.make_can_msg("SPAS1", CAN.ECAN, values))

  blink = 0
  if left_blink:
    blink = 3
  elif right_blink:
    blink = 4
  values = {
    "BLINKER_CONTROL": blink,
  }
  ret.append(packer.make_can_msg("SPAS2", CAN.ECAN, values))

  return ret


def create_fca_warning_light(packer, CAN, frame):
  ret = []

  if frame % 2 == 0:
    values = {
      'AEB_SETTING': 0x1,  # show AEB disabled icon
      'SET_ME_2': 0x2,
      'SET_ME_FF': 0xff,
      'SET_ME_FC': 0xfc,
      'SET_ME_9': 0x9,
    }
    ret.append(packer.make_can_msg("ADRV_0x160", CAN.ECAN, values))
  return ret


def create_adrv_messages(packer, CAN, frame):
  # messages needed to car happy after disabling
  # the ADAS Driving ECU to do longitudinal control

  ret = []

  values = {
  }
  ret.append(packer.make_can_msg("ADRV_0x51", CAN.ACAN, values))

  ret.extend(create_fca_warning_light(packer, CAN, frame))

  if frame % 5 == 0:
    values = {
      'SET_ME_1C': 0x1c,
      'SET_ME_FF': 0xff,
      'SET_ME_TMP_F': 0xf,
      'SET_ME_TMP_F_2': 0xf,
    }
    ret.append(packer.make_can_msg("ADRV_0x1ea", CAN.ECAN, values))

    values = {
      'SET_ME_E1': 0xe1,
      'SET_ME_3A': 0x3a,
    }
    ret.append(packer.make_can_msg("ADRV_0x200", CAN.ECAN, values))

  if frame % 20 == 0:
    values = {
      'SET_ME_15': 0x15,
    }
    ret.append(packer.make_can_msg("ADRV_0x345", CAN.ECAN, values))

  if frame % 100 == 0:
    values = {
      'SET_ME_22': 0x22,
      'SET_ME_41': 0x41,
    }
    ret.append(packer.make_can_msg("ADRV_0x1da", CAN.ECAN, values))

  return ret


def hkg_can_fd_checksum(address: int, sig, d: bytearray) -> int:
  crc = 0
  for i in range(2, len(d)):
    crc = ((crc << 8) ^ CRC16_XMODEM[(crc >> 8) ^ d[i]]) & 0xFFFF
  crc = ((crc << 8) ^ CRC16_XMODEM[(crc >> 8) ^ ((address >> 0) & 0xFF)]) & 0xFFFF
  crc = ((crc << 8) ^ CRC16_XMODEM[(crc >> 8) ^ ((address >> 8) & 0xFF)]) & 0xFFFF
  if len(d) == 8:
    crc ^= 0x5F29
  elif len(d) == 16:
    crc ^= 0x041D
  elif len(d) == 24:
    crc ^= 0x819D
  elif len(d) == 32:
    crc ^= 0x9F5B
  return crc
