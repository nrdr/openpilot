import numpy as np
from collections import defaultdict

from opendbc.can import CANDefine, CANParser
from opendbc.car import Bus, create_button_events, structs, DT_CTRL
from opendbc.car.common.conversions import Conversions as CV
from opendbc.car.honda.hondacan import CanBus
from opendbc.car.honda.values import CAR, DBC, HONDA_BOSCH, HONDA_BOSCH_ALT_RADAR, HONDA_BOSCH_CANFD, \
                                                 HONDA_NIDEC_ALT_SCM_MESSAGES, HONDA_BOSCH_RADARLESS, HONDA_BOSCH_TJA_CONTROL, \
                                                 HondaFlags, CruiseButtons, CruiseSettings, GearShifter, CarControllerParams
from opendbc.car.interfaces import CarStateBase
from opendbc.car.honda.hud_objects import HudObjectTracker

from opendbc.sunnypilot.car.honda.carstate_ext import CarStateExt
from opendbc.sunnypilot.car.honda.carstate import HondaCarStateFeatures

TransmissionType = structs.CarParams.TransmissionType
ButtonType = structs.CarState.ButtonEvent.Type

BUTTONS_DICT = {CruiseButtons.RES_ACCEL: ButtonType.accelCruise, CruiseButtons.DECEL_SET: ButtonType.decelCruise,
                CruiseButtons.MAIN: ButtonType.mainCruise, CruiseButtons.CANCEL: ButtonType.cancel}
SETTINGS_BUTTONS_DICT = {CruiseSettings.DISTANCE: ButtonType.gapAdjustCruise, CruiseSettings.LKAS: ButtonType.lkas}


class CarState(CarStateBase, CarStateExt):
  def __init__(self, CP, CP_SP):
    CarStateBase.__init__(self, CP, CP_SP)
    CarStateExt.__init__(self, CP, CP_SP)
    can_define = CANDefine(DBC[CP.carFingerprint][Bus.pt])

    self.nrdr = HondaCarStateFeatures(CP)

    if CP.transmissionType != TransmissionType.manual:
      self.gearbox_msg = "GEARBOX_AUTO"
      if CP.transmissionType == TransmissionType.cvt:
        self.gearbox_msg = "GEARBOX_CVT"
      self.shifter_values = can_define.dv[self.gearbox_msg]["GEAR_SHIFTER"]

    self.car_state_scm_msg = "SCM_FEEDBACK"
    if CP.carFingerprint in HONDA_NIDEC_ALT_SCM_MESSAGES:
      self.car_state_scm_msg = "SCM_BUTTONS"

    self.brake_error_msg = "HYBRID_BRAKE_ERROR" if CP.flags & HondaFlags.HYBRID else "STANDSTILL"

    self.steer_status_values = defaultdict(lambda: "UNKNOWN", can_define.dv["STEER_STATUS"]["STEER_STATUS"])

    self.brake_switch_prev = False
    self.brake_switch_active = False
    self.low_speed_alert = False

    self.dynamic_v_cruise_units = self.CP.carFingerprint in (HONDA_BOSCH_RADARLESS | HONDA_BOSCH_ALT_RADAR |
                                                             HONDA_BOSCH_TJA_CONTROL | HONDA_BOSCH_CANFD)
    self.cruise_setting = 0
    self.v_cruise_pcm_prev = 0

    # When available we use cp.vl["CAR_SPEED"]["ROUGH_CAR_SPEED_2"] to populate vEgoCluster
    # However, on cars without a digital speedometer this is not always present (HRV, FIT, CRV 2016, ILX and RDX)
    self.dash_speed_seen = False
    self.is_metric = False
    self.v_cruise_factor = 1.

    self.initial_accFault_cleared = False
    self.initial_accFault_cleared_timer = int(10 / DT_CTRL) # 10 seconds after startup for initial faults to clear
    self.radar_ref_counter = 0
    self.radar_5hz_tick_counter = 0
    self.radar_5hz_tick = False
    self.supp_tick_counter = 0
    self.supp_tick = False
    self.hud_tick_counter = 0
    self.hud_tick = False
    self.radar_50hz_tick_counter = 0
    self.radar_50hz_tick = False

    self.scm_ambient_light = 0
    # CAN FD deferred radar disable (see carcontroller): the stock radar is assumed alive until it has
    # been silent for a few frames, and the relay is detected open once the camera's STEERING_CONTROL
    # stops being physically visible on the PT bus.
    self.stock_acc_counter = 0
    self.stock_acc_alive = False
    self.camera_steer_counter = 0
    self.camera_steer_seen = False
    self.canfd_frames = 0
    self.canfd_relay_open = False

    # Only radarless cars have a camera that emits HUD_OBJECTS to poll for secondary vehicle locations.
    # On CAN FD cars the radar owned HUD_OBJECTS and it is disabled, so there is nothing to track.
    self.hud_object_tracker = HudObjectTracker() if CP.carFingerprint in HONDA_BOSCH_RADARLESS else None

  def update(self, can_parsers) -> tuple[structs.CarState, structs.CarStateSP]:
    cp = can_parsers[Bus.pt]
    cp_cam = can_parsers[Bus.cam]
    if self.CP.enableBsm:
      cp_body = can_parsers[Bus.body]
    if self.CP.carFingerprint in HONDA_BOSCH_CANFD:
      cp_radar = can_parsers[Bus.radar]

    ret = structs.CarState()
    ret_sp = structs.CarStateSP()

    # car params
    v_weight_v = [0., 1.]  # don't trust smooth speed at low values to avoid premature zero snapping
    v_weight_bp = [1., 6.]   # smooth blending, below ~0.6m/s the smooth speed snaps to zero

    # update prevs, update must run once per loop
    prev_cruise_buttons = self.cruise_buttons
    prev_cruise_setting = self.cruise_setting
    self.cruise_setting = cp.vl["SCM_BUTTONS"]["CRUISE_SETTING"]
    self.cruise_buttons = cp.vl["SCM_BUTTONS"]["CRUISE_BUTTONS"]
    if self.CP.carFingerprint in (HONDA_BOSCH_RADARLESS | HONDA_BOSCH_CANFD):
      # The camera consumes SCM_BUTTONS content beyond the buttons (losing/zeroing this byte raises an
      # adaptive high beam error), so it must be echoed on frames sent in the SCM's place.
      self.scm_ambient_light = cp.vl["SCM_BUTTONS"]["AMBIENT_LIGHT_MAYBE"]

    # used for car hud message
    # TODO: find CAR_SPEED for HONDA_ODYSSEY_TWN or use ACC_HUD w/ detection
    self.is_metric = self.CP.carFingerprint in (CAR.HONDA_ODYSSEY_TWN,) or not cp.vl["CAR_SPEED"]["IMPERIAL_UNIT"]
    self.v_cruise_factor = CV.MPH_TO_MS if self.dynamic_v_cruise_units and not self.is_metric else CV.KPH_TO_MS

    # ******************* parse out can *******************

    # blend in transmission speed at low speed, since it has more low speed accuracy
    # STANDSTILL->WHEELS_MOVING bit can be noisy around zero, so use XMISSION_SPEED
    lowspeed_source = cp.vl["CAR_SPEED"]["CAR_SPEED"] if self.CP.carFingerprint == CAR.ACURA_INTEGRA else cp.vl["ENGINE_DATA"]["XMISSION_SPEED"]
    v_wheel = sum([cp.vl["WHEEL_SPEEDS"][f"WHEEL_SPEED_{s}"] for s in ("FL", "FR", "RL", "RR")]) / 4.0 * CV.KPH_TO_MS
    v_weight = float(np.interp(v_wheel, v_weight_bp, v_weight_v))
    ret.vEgoRaw = (1. - v_weight) * lowspeed_source * CV.KPH_TO_MS * self.CP.wheelSpeedFactor + v_weight * v_wheel
    ret.vEgo, ret.aEgo = self.update_speed_kf(ret.vEgoRaw)
    ret.standstill = lowspeed_source < 1e-5

    # doorOpen is true if we can find any door open, but signal locations vary, and we may only see the driver's door
    # TODO: Test the eight Nidec cars without SCM signals for driver's door state, may be able to consolidate further
    if self.CP.flags & HondaFlags.HAS_ALL_DOOR_STATES:
      ret.doorOpen = any([cp.vl["DOORS_STATUS"]["DOOR_OPEN_FL"], cp.vl["DOORS_STATUS"]["DOOR_OPEN_FR"],
                          cp.vl["DOORS_STATUS"]["DOOR_OPEN_RL"], cp.vl["DOORS_STATUS"]["DOOR_OPEN_RR"]])
    elif "DRIVERS_DOOR_OPEN" in cp.vl["SCM_BUTTONS"]:
      ret.doorOpen = bool(cp.vl["SCM_BUTTONS"]["DRIVERS_DOOR_OPEN"])
    else:
      ret.doorOpen = bool(cp.vl["SCM_FEEDBACK"]["DRIVERS_DOOR_OPEN"])

    ret.seatbeltUnlatched = bool(cp.vl["SEATBELT_STATUS"]["SEATBELT_DRIVER_LAMP"] or not cp.vl["SEATBELT_STATUS"]["SEATBELT_DRIVER_LATCHED"])

    steer_status = self.steer_status_values[cp.vl["STEER_STATUS"]["STEER_STATUS"]]
    ret.steerFaultPermanent = steer_status not in ("NORMAL", "NO_TORQUE_ALERT_1", "NO_TORQUE_ALERT_2", "LOW_SPEED_LOCKOUT", "TJA_LOW_SPEED_LOCKOUT",
                                                   "TMP_FAULT")
    if self.CP.carFingerprint in (HONDA_BOSCH_ALT_RADAR | HONDA_BOSCH_CANFD):
      # TODO: See if this logic works for all other Honda
      min_steer_speed = max(CarControllerParams.STEER_GLOBAL_MIN_SPEED, self.CP.minSteerSpeed)
      expected_low_speed_lockout = steer_status == "LOW_SPEED_LOCKOUT" and ret.vEgo < min_steer_speed
      ret.steerFaultTemporary = steer_status != "NORMAL" and not expected_low_speed_lockout
    else:
      # LOW_SPEED_LOCKOUT is not worth a warning
      # NO_TORQUE_ALERT_2 can be caused by bump or steering nudge from driver
      # FIXME: the stock camera stops steering on NO_TORQUE_ALERT_1
      ret.steerFaultTemporary = steer_status not in ("NORMAL", "LOW_SPEED_LOCKOUT", "TJA_LOW_SPEED_LOCKOUT", "NO_TORQUE_ALERT_2")

    if (self.CP.carFingerprint == CAR.ACURA_MDX_4G) and (steer_status == "TJA_LOW_SPEED_LOCKOUT"):
      ret.steerFaultPermanent = False
      ret.steerFaultTemporary = False

    # All Honda EPS cut off slightly above standstill, some much higher
    # Don't alert in the near-standstill range, but alert for per-vehicle configured minimums above that
    if CarControllerParams.STEER_GLOBAL_MIN_SPEED < ret.vEgo < (self.CP.minSteerSpeed + 0.5):
      self.low_speed_alert = True
    elif ret.vEgo > (self.CP.minSteerSpeed + 1.):
      # TODO: better handle delayed steering enablement on ALT_RADAR cars
      self.low_speed_alert = False
    ret.lowSpeedAlert = self.low_speed_alert

    # Log non-critical stock ACC/LKAS faults if Nidec (camera) or longitudinal CANFD alt-brake
    if self.CP.carFingerprint not in HONDA_BOSCH:
      ret.carFaultedNonCritical = bool(cp_cam.vl["ACC_HUD"]["ACC_PROBLEM"] or cp_cam.vl["LKAS_HUD"]["LKAS_PROBLEM"])

    elif self.CP.carFingerprint in HONDA_BOSCH_RADARLESS:
      ret.accFaulted = bool(cp.vl["CRUISE_FAULT_STATUS"]["CRUISE_FAULT"])
    else:
      if self.CP.openpilotLongitudinalControl:
        if self.CP.carFingerprint in (HONDA_BOSCH_CANFD | HONDA_BOSCH_TJA_CONTROL) and (self.CP.flags & HondaFlags.BOSCH_ALT_BRAKE):
          ret.accFaulted = bool(cp.vl["BRAKE_MODULE"]["CRUISE_FAULT"])
        else:
          ret.accFaulted = bool(cp.vl[self.brake_error_msg]["BRAKE_ERROR_1"] or cp.vl[self.brake_error_msg]["BRAKE_ERROR_2"])

      # Log non-critical stock ACC/LKAS faults if Nidec (camera)
      if self.CP.carFingerprint not in HONDA_BOSCH:
        ret.carFaultedNonCritical = bool(cp_cam.vl["ACC_HUD"]["ACC_PROBLEM"] or cp_cam.vl["LKAS_HUD"]["LKAS_PROBLEM"])

    ret.espDisabled = cp.vl["VSA_STATUS"]["ESP_DISABLED"] != 0

    if self.CP.carFingerprint not in (CAR.HONDA_ODYSSEY_TWN,):
      self.dash_speed_seen = self.dash_speed_seen or cp.vl["CAR_SPEED"]["ROUGH_CAR_SPEED_2"] > 1e-3
      if self.dash_speed_seen:
        conversion = CV.KPH_TO_MS if self.is_metric else CV.MPH_TO_MS
        ret.vEgoCluster = cp.vl["CAR_SPEED"]["ROUGH_CAR_SPEED_2"] * conversion

    ret.steeringAngleDeg = cp.vl["STEERING_SENSORS"]["STEER_ANGLE"]
    ret.steeringRateDeg = cp.vl["STEERING_SENSORS"]["STEER_ANGLE_RATE"]

    ret.leftBlinker, ret.rightBlinker = self.update_blinker_from_stalk(
      250, cp.vl["SCM_FEEDBACK"]["LEFT_BLINKER"], cp.vl["SCM_FEEDBACK"]["RIGHT_BLINKER"])
    ret.brakeHoldActive = cp.vl["VSA_STATUS"]["BRAKE_HOLD_ACTIVE"] == 1
    ret.parkingBrake = bool(cp.vl[self.car_state_scm_msg]["PARKING_BRAKE_ON"])

    if self.CP.transmissionType == TransmissionType.manual:
      ret.gearShifter = GearShifter.reverse if bool(cp.vl[self.car_state_scm_msg]["REVERSE_LIGHT"]) else GearShifter.drive
    else:
      gear_position = self.shifter_values.get(cp.vl[self.gearbox_msg]["GEAR_SHIFTER"], None)
      ret.gearShifter = self.parse_gear_shifter(gear_position)

    ret.gasPressed = cp.vl["POWERTRAIN_DATA"]["PEDAL_GAS"] > 1e-5

    ret.steeringTorque = cp.vl["STEER_STATUS"]["STEER_TORQUE_SENSOR"]
    ret.steeringPressed = self.nrdr.steering_pressed(ret.steeringTorque, ret.steeringAngleDeg)

    if self.CP.carFingerprint in HONDA_BOSCH:
      # The PCM always manages its own cruise control state, but doesn't publish it
      if self.CP.carFingerprint in HONDA_BOSCH_RADARLESS:
        ret.cruiseState.nonAdaptive = cp_cam.vl["ACC_HUD"]["CRUISE_CONTROL_LABEL"] != 0

      if not self.CP.openpilotLongitudinalControl:
        # ACC_HUD is on camera bus on radarless cars
        acc_hud = cp_cam.vl["ACC_HUD"] if self.CP.carFingerprint in HONDA_BOSCH_RADARLESS else cp.vl["ACC_HUD"]
        ret.cruiseState.nonAdaptive = acc_hud["CRUISE_CONTROL_LABEL"] != 0
        ret.cruiseState.standstill = acc_hud["CRUISE_SPEED"] == 252.

        # On set, cruise set speed pulses between 254~255 and the set speed prev is set to avoid this.
        ret.cruiseState.speed = self.v_cruise_pcm_prev if acc_hud["CRUISE_SPEED"] > 160.0 else acc_hud["CRUISE_SPEED"] * self.v_cruise_factor
        self.v_cruise_pcm_prev = ret.cruiseState.speed
    else:
      ret.cruiseState.speed = cp.vl["CRUISE"]["CRUISE_SPEED_PCM"] * CV.KPH_TO_MS

    if self.CP.flags & HondaFlags.BOSCH_ALT_BRAKE:
      ret.brakePressed = cp.vl["BRAKE_MODULE"]["BRAKE_PRESSED"] != 0
    else:
      # brake switch has shown some single time step noise, so only considered when
      # switch is on for at least 2 consecutive CAN samples
      # brake switch rises earlier than brake pressed but is never 1 when in park
      brake_switch_vals = cp.vl_all["POWERTRAIN_DATA"]["BRAKE_SWITCH"]
      if len(brake_switch_vals):
        brake_switch = cp.vl["POWERTRAIN_DATA"]["BRAKE_SWITCH"] != 0
        if len(brake_switch_vals) > 1:
          self.brake_switch_prev = brake_switch_vals[-2] != 0
        self.brake_switch_active = brake_switch and self.brake_switch_prev
        self.brake_switch_prev = brake_switch
      ret.brakePressed = (cp.vl["POWERTRAIN_DATA"]["BRAKE_PRESSED"] != 0) or self.brake_switch_active

    ret.deprecated.brake = cp.vl["VSA_STATUS"]["USER_BRAKE"]
    ret.cruiseState.enabled = cp.vl["POWERTRAIN_DATA"]["ACC_STATUS"] != 0
    ret.cruiseState.available = bool(cp.vl[self.car_state_scm_msg]["MAIN_ON"])

    # Bosch cars take a few minutes after startup to clear prior faults
    if ret.accFaulted:
      if (self.CP.carFingerprint in HONDA_BOSCH) and not self.initial_accFault_cleared:
        # block via cruiseState since accFaulted is not reversible until offroad
        ret.accFaulted = False
        ret.cruiseState.available = False
    elif self.initial_accFault_cleared_timer == 0:
      self.initial_accFault_cleared = True

    if self.initial_accFault_cleared_timer > 0:
      self.initial_accFault_cleared_timer -= 1

    # Gets rid of Pedal Grinding noise when brake is pressed at slow speeds for some models
    if self.CP.carFingerprint in (CAR.HONDA_PILOT, CAR.HONDA_RIDGELINE):
      if ret.deprecated.brake > 0.1:
        ret.brakePressed = True

    if self.CP.carFingerprint in HONDA_BOSCH:
      # TODO: find the radarless AEB_STATUS bit and make sure ACCEL_COMMAND is correct to enable AEB alerts
      if self.CP.carFingerprint not in HONDA_BOSCH_RADARLESS:
        ret.stockAeb = (not self.CP.openpilotLongitudinalControl) and bool(cp.vl["ACC_CONTROL"]["AEB_STATUS"] and cp.vl["ACC_CONTROL"]["ACCEL_COMMAND"] < -1e-5)
    else:
      ret.stockAeb = bool(cp_cam.vl["BRAKE_COMMAND"]["AEB_REQ_1"] and cp_cam.vl["BRAKE_COMMAND"]["COMPUTER_BRAKE"] > 1e-5)

    self.acc_hud = False
    self.lkas_hud = False
    if self.CP.carFingerprint not in HONDA_BOSCH:
      ret.stockFcw = cp_cam.vl["BRAKE_COMMAND"]["FCW"] != 0
      self.acc_hud = cp_cam.vl["ACC_HUD"]
      self.stock_brake = cp_cam.vl["BRAKE_COMMAND"]
    if self.CP.carFingerprint in (HONDA_BOSCH_RADARLESS | HONDA_BOSCH_CANFD):
      self.lkas_hud = cp_cam.vl["LKAS_HUD"]
    if self.CP.carFingerprint in HONDA_BOSCH_CANFD:
      # The radar emits low-rate "tick reference" messages that keep running even while the radar's
      # data messages are disabled, so we phase our look-alikes to the stock cadence off of them.
      #
      # There is a one-frame (10 ms) delay between reading a tick here in carstate and transmitting the
      # response in carcontroller. The stock radar sends each data message in the SAME frame as its
      # tick, so we pulse one frame BEFORE the next tick (counter == period-1): the +1 transmit delay
      # then lands the message on the next tick frame, matching stock.
      #   period (frames @100Hz): 0x710=100, 0x730=10, 0x750=2, RADAR_REFERENCE=20
      self.radar_ref_counter = cp.vl["RADAR_REFERENCE"]["COUNTER"]

      # 5 Hz: RADAR_REFERENCE (0x3A1) is on the powertrain bus (cp), not the radar bus (cp_radar).
      # RADAR_LEAD does NOT ride with the reference; stock sends it ~120 ms (12 frames) after, so fire
      # at frame 11 (+1 transmit delay -> ~120 ms).
      ref_tick_vals = cp.vl_all.get("RADAR_REFERENCE", {}).get("COUNTER", [])
      if len(ref_tick_vals) > 0:
        self.radar_5hz_tick_counter = 0
      else:
        self.radar_5hz_tick_counter += 1
      self.radar_5hz_tick = (self.radar_5hz_tick_counter == 11)

      # 1 Hz: 0x710 -> BOSCH_SUPPLEMENTAL_CANFD, one frame before the next tick
      supp_tick_vals = cp_radar.vl_all.get("RADAR_SUPP_TICK_REFERENCE", {}).get("IGNORE", [])
      if len(supp_tick_vals) > 0:
        self.supp_tick_counter = 0
      else:
        self.supp_tick_counter += 1
      self.supp_tick = (self.supp_tick_counter == 99)

      # 10 Hz: 0x730 -> RADAR_HUD_CANFD, one frame before the next tick
      hud_tick_vals = cp_radar.vl_all.get("RADAR_HUD_TICK_REFERENCE", {}).get("IGNORE", [])
      if len(hud_tick_vals) > 0:
        self.hud_tick_counter = 0
      else:
        self.hud_tick_counter += 1
      self.hud_tick = (self.hud_tick_counter == 9)

      # 50 Hz: 0x750 -> LANE_PATH/HUD_OBJECTS, one frame before the next tick
      tick_50hz_vals = cp_radar.vl_all.get("RADAR_50HZ_TICK_REFERENCE", {}).get("IGNORE", [])
      if len(tick_50hz_vals) > 0:
        self.radar_50hz_tick_counter = 0
      else:
        self.radar_50hz_tick_counter += 1
      self.radar_50hz_tick = (self.radar_50hz_tick_counter == 1)

      # Deferred radar disable (see carcontroller). The stock radar transmits ACC_CONTROL every 2
      # frames, so 4 missed frames means it has been silenced; assume alive until then so the
      # replacement stream never overlaps it.
      self.canfd_frames += 1
      if len(cp.vl_all.get("ACC_CONTROL", {}).get("COUNTER", [])) > 0:
        self.stock_acc_counter = 0
      else:
        self.stock_acc_counter += 1
      self.stock_acc_alive = self.stock_acc_counter < 4

      # While the comma relay is closed the camera's STEERING_CONTROL is physically visible on the PT
      # bus; when the relay opens it disappears (openpilot's own 0xE4 TX is not parsed as RX). As a
      # fallback, assume the relay is open after 5 s of controls in case the camera was never seen.
      if len(cp.vl_all.get("STEERING_CONTROL", {}).get("COUNTER", [])) > 0:
        self.camera_steer_counter = 0
        self.camera_steer_seen = True
      else:
        self.camera_steer_counter += 1
      self.canfd_relay_open = (self.camera_steer_seen and self.camera_steer_counter >= 5) or self.canfd_frames >= 500
    else:
      self.supp_tick = False
      self.hud_tick = False
      self.radar_5hz_tick = False
      self.radar_50hz_tick = False

    if self.CP.enableBsm:
      # BSM messages are on B-CAN, requires a panda forwarding B-CAN messages to CAN 0
      # more info here: https://github.com/commaai/openpilot/pull/1867
      ret.leftBlindspot = cp_body.vl["BSM_STATUS_LEFT"]["BSM_ALERT"] == 1
      ret.rightBlindspot = cp_body.vl["BSM_STATUS_RIGHT"]["BSM_ALERT"] == 1

    ret.buttonEvents = [
      *create_button_events(self.cruise_buttons, prev_cruise_buttons, BUTTONS_DICT),
      *create_button_events(self.cruise_setting, prev_cruise_setting, SETTINGS_BUTTONS_DICT),
    ]

    CarStateExt.update(self, ret, ret_sp, can_parsers)

    if self.hud_object_tracker is not None:
      self.hud_object_tracker.update(cp_cam)

    return ret, ret_sp

  def get_can_parsers(self, CP, CP_SP):
    pt_messages = []
    cam_messages = []
    if CP.carFingerprint in HONDA_BOSCH_CANFD:
      # Radar-alive and relay-open detection for the deferred radar disable (see carcontroller).
      # Both messages intentionally go silent (the radar is disabled, the camera ends up behind the
      # open relay), so subscribe with NaN frequency to skip the alive/timeout checks.
      pt_messages += [("ACC_CONTROL", float('nan')), ("STEERING_CONTROL", float('nan'))]
    if CP.carFingerprint in HONDA_BOSCH_RADARLESS:
      # HUD_OBJECTS is polled by the HudObjectTracker, but not every radarless camera emits it,
      # so subscribe with NaN frequency to skip the alive/timeout checks.
      cam_messages += [("HUD_OBJECTS", float('nan'))]
    parsers = {
      Bus.pt: CANParser(DBC[CP.carFingerprint][Bus.pt], pt_messages, CanBus(CP).pt),
      Bus.cam: CANParser(DBC[CP.carFingerprint][Bus.pt], cam_messages, CanBus(CP).camera),
    }
    if CP.enableBsm:
      parsers[Bus.body] = CANParser(DBC[CP.carFingerprint][Bus.body], [], CanBus(CP).radar)
    if self.CP.carFingerprint in HONDA_BOSCH_CANFD:
      # These radar tick-reference messages are only read via vl_all, which (unlike vl) does not
      # auto-subscribe messages, so they must be listed explicitly or they are never parsed.
      #   0x710 RADAR_SUPP_TICK_REFERENCE (1 Hz), 0x730 RADAR_HUD_TICK_REFERENCE (10 Hz),
      #   0x750 RADAR_50HZ_TICK_REFERENCE (50 Hz)
      parsers[Bus.radar] = CANParser(DBC[CP.carFingerprint][Bus.radar], [
        ("RADAR_SUPP_TICK_REFERENCE", 0),
        ("RADAR_HUD_TICK_REFERENCE", 0),
        ("RADAR_50HZ_TICK_REFERENCE", 0),
      ], CanBus(CP).radar)

    return parsers
