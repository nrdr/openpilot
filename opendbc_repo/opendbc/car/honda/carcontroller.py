import math

import numpy as np

from opendbc.can import CANPacker
from opendbc.car import ACCELERATION_DUE_TO_GRAVITY, Bus, DT_CTRL, rate_limit, make_tester_present_msg, structs
from opendbc.car.honda import hondacan
from opendbc.car.honda.values import CAR, HONDA_BOSCH, CarControllerParams, CruiseButtons, CruiseSettings, HondaFlags
from opendbc.car.interfaces import CarControllerBase
from opendbc.car.common.pid import PIDController
from opendbc.car.honda import lane_path
from opendbc.car.honda import hud_objects

from opendbc.sunnypilot.car.honda.mads import MadsCarController
from opendbc.sunnypilot.car.honda.gas_interceptor import GasInterceptorCarController
from opendbc.sunnypilot.car.honda.icbm import IntelligentCruiseButtonManagementInterface
from opendbc.sunnypilot.car.honda.can import create_camera_message
from opendbc.sunnypilot.car.honda.controller_features import HondaControllerFeatures
from opendbc.sunnypilot.car.runtime_config import HondaCarConfig

VisualAlert = structs.CarControl.HUDControl.VisualAlert
LongCtrlState = structs.CarControl.Actuators.LongControlState


def compute_gb_honda_bosch(accel, speed):
  # TODO returns 0s, is unused
  return 0.0, 0.0


def compute_gb_honda_nidec(accel, speed):
  creep_brake = 0.0
  creep_speed = 2.3
  creep_brake_value = 0.15
  if speed < creep_speed:
    creep_brake = (creep_speed - speed) / creep_speed * creep_brake_value
  gb = float(accel) / 4.8 - creep_brake
  return np.clip(gb, 0.0, 1.0), np.clip(-gb, 0.0, 1.0)


def compute_gas_brake(accel, speed, CP):
  if CP.flags & HondaFlags.BOSCH:
    return compute_gb_honda_bosch(accel, speed)
  else:
    return compute_gb_honda_nidec(accel, speed)


# TODO not clear this does anything useful
def actuator_hysteresis(brake, braking, brake_steady):
  # hyst params
  brake_hyst_on = 0.02    # to activate brakes exceed this value
  brake_hyst_off = 0.005  # to deactivate brakes below this value
  brake_hyst_gap = 0.01   # don't change brake command for small oscillations within this value

  # *** hysteresis logic to avoid brake blinking. go above 0.1 to trigger
  if (brake < brake_hyst_on and not braking) or brake < brake_hyst_off:
    brake = 0.
  braking = brake > 0.

  # for small brake oscillations within brake_hyst_gap, don't change the brake command
  if brake == 0.:
    brake_steady = 0.
  elif brake > brake_steady + brake_hyst_gap:
    brake_steady = brake - brake_hyst_gap
  elif brake < brake_steady - brake_hyst_gap:
    brake_steady = brake + brake_hyst_gap
  brake = brake_steady

  return brake, braking, brake_steady


def brake_pump_hysteresis(apply_brake, apply_brake_last, last_pump_ts, ts):
  pump_on = False

  # reset pump timer if:
  # - there is an increment in brake request
  # - we are applying steady state brakes and we haven't been running the pump
  #   for more than 20s (to prevent pressure bleeding)
  if apply_brake > apply_brake_last or (ts - last_pump_ts > 20. and apply_brake > 0):
    last_pump_ts = ts

  # once the pump is on, run it for at least 0.2s
  if ts - last_pump_ts < 0.2 and apply_brake > 0:
    pump_on = True

  return pump_on, last_pump_ts


def process_hud_alert(hud_alert):
  alert_fcw = False
  alert_steer_required = False

  # Make sure FCW is prioritized over steering required
  # TODO: implement separate available LDW alert
  if hud_alert == VisualAlert.fcw:
    alert_fcw = True
  elif hud_alert in (VisualAlert.steerRequired, VisualAlert.ldw):
    alert_steer_required = True

  return alert_fcw, alert_steer_required


class CarController(CarControllerBase, MadsCarController, GasInterceptorCarController, IntelligentCruiseButtonManagementInterface):
  def __init__(self, dbc_names, CP, CP_SP, config: HondaCarConfig | None = None):
    if config is None:
      raise ValueError("Honda controller requires a host-provided HondaCarConfig")
    CarControllerBase.__init__(self, dbc_names, CP, CP_SP)
    MadsCarController.__init__(self)
    GasInterceptorCarController.__init__(self, CP, CP_SP)
    IntelligentCruiseButtonManagementInterface.__init__(self, CP, CP_SP)
    self.packer = CANPacker(dbc_names[Bus.pt])
    self.params = CarControllerParams(CP)
    self.CAN = hondacan.CanBus(CP)
    self.hud_object_author = hud_objects.HudObjectAuthor()
    self.lane_path_fitter = lane_path.LanePathFitter()
    self.dash_lane = lane_path.DashLane([lane_path.OFFSET_UNAVAILABLE] * lane_path.NUM_PTS, 0.0, False, False)
    self.lkas_hud_key = None
    self.lkas_state_change_frames = 0
    self.tja_control = bool(CP.flags & HondaFlags.BOSCH_TJA_CONTROL)
    self.nrdr = HondaControllerFeatures(CP, CP_SP, config)

    self.braking = False
    self.brake_steady = 0.
    self.brake_last = 0.
    self.apply_brake_last = 0
    self.last_pump_ts = 0.
    self.stopping_counter = 0

    self.accel = 0.0
    self.speed = 0.0
    self.gas = 0.0
    self.brake = 0.0
    self.last_torque = 0.0
    self.bosch_last_gas = 0

    self.lkas_button_send_remaining = 0
    self.last_lkas_button_frame = 0
    self.radar_disable_counter = 0

    self.gasfactor, self.windfactor = self.nrdr.longitudinal_factors
    self.gasfactor_before_gasmax = self.gasfactor
    self.windfactor_before_gasmax = self.windfactor_before_brake = self.windfactor
    self.pitch = 0.0
    self.radar_mux = 0
    # stock RADAR_HUD_CANFD raises its CMBS bit only for a short burst after ACC engages (see
    # create_radar_hud_canfd); counted in 10 Hz hud ticks
    self.radar_hud_pulse = 0
    self.last_acc_enabled = False

    # Bosch extra-brake controller
    self.brake_pid = PIDController(k_p=0.0,
                                   k_i=1.0,
                                   pos_limit=0.0,
                                   neg_limit=-2.0,
                                   rate=50)
    self.brake_pid.reset()

  def update(self, CC, CC_SP, CS, now_nanos):
    MadsCarController.update(self, self.CP, CC, CC_SP)
    live = self.nrdr.live_tuning()
    self.gasfactor, self.windfactor = self.nrdr.longitudinal_factors
    gas_pedal_force = 0.0
    min_gas = self.params.BOSCH_GAS_LOOKUP_BP[0]
    actuators = CC.actuators
    hud_control = CC.hudControl
    hud_v_cruise = hud_control.setSpeed / CS.v_cruise_factor if hud_control.speedVisible else 255
    self.nrdr.update_system_speed_flash(CC, CS, hud_control)
    pcm_cancel_cmd = CC.cruiseControl.cancel

    if len(CC.orientationNED) == 3:
      self.pitch = CC.orientationNED[1]
    hill_brake = math.sin(self.pitch) * ACCELERATION_DUE_TO_GRAVITY

    if CC.longActive:
      accel = actuators.accel
      if (self.CP.carFingerprint in (CAR.ACURA_MDX_3G, CAR.ACURA_MDX_3G_MMR)) and (accel > max(0, CS.out.aEgo) + 0.1):
        accel = 10000.0 # help with lagged accel until pedal tuning is inserted
      ecu_matched = live.ecu_matched_long and self.CP.carFingerprint not in HONDA_BOSCH
      accel_cmd = self.nrdr.nidec_accel_command(actuators.accel, ecu_matched)
      gas, brake = compute_gas_brake(accel_cmd + hill_brake, CS.out.vEgo, self.CP)
      brake = self.nrdr.nidec_brake_authority(
        accel_cmd + hill_brake, brake, CS.out.vEgo, live.full_brake_authority,
      )
      gas, brake = self.nrdr.nidec_gas_brake(accel_cmd, gas, brake, CS.out.vEgo, ecu_matched)
    else:
      accel = 0.0
      gas, brake = 0.0, 0.0
      self.nrdr.reset_longitudinal()

    # *** rate limit steer ***
    limited_torque, lkas_active = self.nrdr.update_steering_torque(CC, CS, live, self.last_torque)
    self.last_torque = limited_torque

    # *** apply brake hysteresis ***
    pre_limit_brake, self.braking, self.brake_steady = actuator_hysteresis(brake, self.braking, self.brake_steady)

    # *** rate limit after the enable check ***
    brake_rate_up = live.stopping_decel_rate if actuators.longControlState == LongCtrlState.stopping else 3.0
    self.brake_last = rate_limit(pre_limit_brake, self.brake_last, -2., brake_rate_up * DT_CTRL)

    # vehicle hud display, wait for one update from 10Hz 0x304 msg
    alert_fcw, alert_steer_required = process_hud_alert(hud_control.visualAlert)

    # **** process the car messages ****

    # steer torque is converted back to CAN reference (positive when steering right)
    apply_torque = int(np.interp(-limited_torque * self.params.STEER_MAX,
                                 self.params.STEER_LOOKUP_BP, self.params.STEER_LOOKUP_V))

    speed_control = 1 if ((accel <= 0.0) and (CS.out.vEgo == 0)) else 0

    # Send CAN commands
    can_sends = []

    if self.CP.flags & HondaFlags.BOSCH and not (self.CP.flags & HondaFlags.BOSCH_RADARLESS) and self.CP.openpilotLongitudinalControl:
      if self.CP.flags & HondaFlags.BOSCH_CANFD and CS.stock_acc_alive:
        # CAN FD: the radar is still transmitting. It is silenced from here rather than from
        # CarInterface.init(), and only once the comma relay is confirmed open: init() ran while the
        # panda was still in the ELM327 safety mode, so the replacement ACC_CONTROL stream was blocked
        # until the safety-mode switch landed, and whenever the switch took longer than ~110 ms after
        # the radar went silent the brake module latched CRUISE_FAULT (accFaulted) for the whole drive.
        # With the relay already open the stock radar keeps feeding the brake module (and, via panda
        # forwarding, the camera) right up to the switchover, and the replacement stream starts within
        # a few frames of radar silence (see CS.stock_acc_alive), well inside the fault threshold.
        if CS.canfd_relay_open:
          if self.radar_disable_counter % 50 == 0:
            # UDS extended diagnostic session, required before CommunicationControl
            can_sends.append((0x18DAB0F1, b'\x02\x10\x03\x00\x00\x00\x00\x00', self.CAN.pt))
          elif self.radar_disable_counter % 50 == 5:
            # UDS CommunicationControl disableRxAndTx (0x80 suppresses the response); the same request
            # CarInterface.init() used to send, retried every 0.5 s until the radar goes silent
            can_sends.append((0x18DAB0F1, b'\x03\x28\x83\x03\x00\x00\x00\x00', self.CAN.pt))
          self.radar_disable_counter += 1
      elif self.frame % 10 == 0:
        # tester present - w/ no response (keeps radar disabled)
        bus = 0 if self.CP.flags & HondaFlags.BOSCH_CANFD else 1
        can_sends.append(make_tester_present_msg(0x18DAB0F1, bus, suppress_response=True))

    # simulate canfd radar to prevent faults
    # These radar look-alikes are consumed by both the camera ECU (behind the relay, on the camera
    # bus) and the powertrain (radar bus). openpilot's own transmissions are not forwarded across the
    # open relay, so they must be sent explicitly on both buses. Each message is packed exactly once
    # so the packer's counter/checksum only advance once per cycle, then the identical bytes are
    # mirrored onto both buses (re-packing would double-increment the counter and desync the buses).
    # While the stock radar is still transmitting (drive start, before the deferred disable above has
    # silenced it), it authors all of these itself: sending look-alikes too would double them up.
    if (self.CP.flags & HondaFlags.BOSCH_CANFD) and self.CP.openpilotLongitudinalControl and not CS.stock_acc_alive:
      if CC.enabled and not self.last_acc_enabled:
        self.radar_hud_pulse = 30  # ~3 s at 10 Hz, matching the stock 2-6 s engage burst
      self.last_acc_enabled = CC.enabled
      radar_msgs = []
      if CS.hud_tick:
        radar_msgs.append(hondacan.create_radar_hud_canfd(self.packer, self.CAN.pt, CC.enabled, self.radar_hud_pulse > 0))
        if self.radar_hud_pulse > 0:
          self.radar_hud_pulse -= 1
      if CS.supp_tick:
        radar_msgs.append(hondacan.create_canfd_supplemental(self.packer, self.CAN.pt))
      if CS.radar_50hz_tick:
        # Cycle the radar MUX through the same banks the stock radar uses: 1-10, 17-26, 33-42, 49-58.
        # This counter also drives the LANE_PATH/HUD_OBJECTS mux below: it advances exactly one step
        # per transmitted frame, so the sweep stays contiguous even when a tick is missed (deriving
        # the mux from the frame counter skipped a mux on every missed tick, leaving holes in the
        # sweep the stock radar never produces).
        # These must be elif (not sequential if): a bare `if` that sets the bank start would fall
        # through to the `else` increment, skipping the bank-start values (17, 33, 49).
        if self.radar_mux >= 58:
          self.radar_mux = 1
        elif self.radar_mux == 10:
          self.radar_mux = 17
        elif self.radar_mux == 26:
          self.radar_mux = 33
        elif self.radar_mux == 42:
          self.radar_mux = 49
        else:
          self.radar_mux += 1
        # radar_msgs.extend(hondacan.create_canfd_50hz_radar_messages(self.packer, self.CAN.pt, self.radar_mux))
      if CS.radar_5hz_tick:
        # RADAR_LEAD's LANE_PATH_LENGTH must track the valid-point count of the LANE_PATH sweep we are
        # authoring; the stock radar keeps the two in lockstep and the dash won't draw lanes otherwise.
        # LEFT_LANE/RIGHT_LANE carry the per-side line-detected status (3/0) the same way the stock
        # radar mirrors the camera's LANE_LINES bits; the dash draws no lane lines while both are 0.
        radar_msgs.extend(hondacan.create_canfd_5hz_radar_messages(self.packer, self.CAN.pt, CS.radar_ref_counter,
                                                                   lane_path.canfd_lane_length(self.dash_lane),
                                                                   lane_path.LANE_LINE_ON if self.dash_lane.left_line else 0,
                                                                   lane_path.LANE_LINE_ON if self.dash_lane.right_line else 0))

      # mirror each packed frame onto both the powertrain bus and the camera bus
      for addr, dat, _ in radar_msgs:
        can_sends.append((addr, dat, self.CAN.pt))
        can_sends.append((addr, dat, self.CAN.camera))

    # Send steering command.
    can_sends.append(hondacan.create_steering_control(self.packer, self.CAN, apply_torque, lkas_active, self.tja_control))

    # wind brake from air resistance decel at high speed
    wind_brake = np.interp(CS.out.vEgo, [0.0, 2.3, 35.0], [0.001, 0.002, 0.15]) * self.windfactor # not in m/s2 units
    wind_brake_ms2 = np.interp(CS.out.vEgo, [0.0, 13.4, 22.4, 31.3, 40.2], [0.000, 0.049, 0.136, 0.267, 0.441]) # in m/s2 units

    # all of this is only relevant for HONDA NIDEC
    speed_control = 0
    max_accel = np.interp(CS.out.vEgo, self.params.NIDEC_MAX_ACCEL_BP, self.params.NIDEC_MAX_ACCEL_V)
    # TODO this 1.44 is just to maintain previous behavior
    pcm_speed_BP = [-wind_brake,
                    -wind_brake * (3 / 4),
                    0.0,
                    0.5]
    # The Honda ODYSSEY seems to have different PCM_ACCEL
    # msgs, is it other cars too?
    if self.CP_SP.enableGasInterceptor or not CC.longActive:
      pcm_speed = 0.0
      pcm_accel = int(0.0)
    elif self.CP.flags & HondaFlags.NIDEC_ALT_PCM_ACCEL:
      pcm_speed_V = [0.0,
                     np.clip(CS.out.vEgo - 3.0, 0.0, 100.0),
                     np.clip(CS.out.vEgo + 0.0, 0.0, 100.0),
                     np.clip(CS.out.vEgo + 5.0, 0.0, 100.0)]
      pcm_speed = float(np.interp(gas - brake, pcm_speed_BP, pcm_speed_V))
      pcm_accel = int(1.0 * self.params.NIDEC_GAS_MAX)
    elif (self.CP.carFingerprint in (CAR.ACURA_MDX_3G, CAR.ACURA_MDX_3G_MMR)):
      pcm_speed_V = [0.0,
                     np.clip(CS.out.vEgo - 2.0, 0.0, 100.0),
                     np.clip(CS.out.vEgo + 2.0, 0.0, 100.0),
                     np.clip(CS.out.vEgo + 20.0, 0.0, 100.0)]
      pcm_speed = float(np.interp(gas - brake, pcm_speed_BP, pcm_speed_V))
      pcm_accel = int(np.clip((accel / 1.44) / max_accel, 10.0 / self.params.NIDEC_GAS_MAX, 1.0) * self.params.NIDEC_GAS_MAX)
      if speed_control == 1 and CC.longActive:
        pcm_accel = 198
    else:
      pcm_speed_V = [0.0,
                     np.clip(CS.out.vEgo - 2.0, 0.0, 100.0),
                     np.clip(CS.out.vEgo + 2.0, 0.0, 100.0),
                     np.clip(CS.out.vEgo + 5.0, 0.0, 100.0)]
      pcm_speed = float(np.interp(gas - brake, pcm_speed_BP, pcm_speed_V))
      pcm_accel = int(np.clip((accel / 1.44) / max_accel, 0.0, 1.0) * self.params.NIDEC_GAS_MAX)

    if not self.CP.openpilotLongitudinalControl:
      if self.frame % 2 == 0 and not (self.CP.flags & (HondaFlags.BOSCH_RADARLESS | HondaFlags.BOSCH_CANFD)) and not self.CP.flags & HondaFlags.NIDEC:
        can_sends.append(hondacan.create_bosch_supplemental_1(self.packer, self.CAN))
      # If using stock ACC, spam cancel command to kill gas when OP disengages.
      if pcm_cancel_cmd:
        can_sends.append(hondacan.spam_buttons_command(self.packer, self.CAN, CruiseButtons.CANCEL, 0, CS.scm_ambient_light, self.CP))
      elif CC.cruiseControl.resume:
        can_sends.append(hondacan.spam_buttons_command(self.packer, self.CAN, CruiseButtons.RES_ACCEL, 0, CS.scm_ambient_light, self.CP))

    else:
      # Send gas and brake commands.
      if self.frame % 2 == 0:
        ts = self.frame * DT_CTRL

        if self.CP.flags & HondaFlags.BOSCH:
          if not self.nrdr.replaces_longitudinal and (accel < min_gas) and \
              (CS.out.vEgo < 3.0) and not (-1e-3 < CS.out.vEgo < 1e-3):
            brake_addon = self.brake_pid.update(error = accel - CS.out.aEgo, speed = CS.out.vEgo)
            targetaccel = min(accel,accel + brake_addon)
          elif self.nrdr.replaces_longitudinal:
            self.brake_pid.reset()
            targetaccel = accel
          else:
            if (self.brake_pid.i < 0.0) and (accel < min_gas):
              self.brake_pid.i = min(0.0, self.brake_pid.i + 0.02) # release 1m/s2 @ 50hz
            else:
              self.brake_pid.reset()
            targetaccel = min(accel,accel + self.brake_pid.i)

          self.accel = float(np.clip(targetaccel, self.params.BOSCH_ACCEL_MIN, self.params.BOSCH_ACCEL_MAX))
          gas_pedal_force = accel + wind_brake_ms2 * self.windfactor + hill_brake # not using self.accel since pid resets w gas pedal

          # live-learn gas pedal adjustments when openpilot is controlling gas
          if not self.nrdr.replaces_longitudinal and (actuators.longControlState == LongCtrlState.pid) and (not CS.out.gasPressed):
            gas_error = accel - CS.out.aEgo
            if gas_error != 0.0 and gas_pedal_force > min_gas:
              if self.CP.carFingerprint in (CAR.HONDA_INSIGHT, CAR.HONDA_CIVIC_BOSCH): # gas pedal reacts too slowly
                learn_speed = 150
              elif self.CP.carFingerprint in (CAR.ACURA_RDX_3G, CAR.ACURA_RDX_3G_MMR): # Prevent overreacting to turbo lag
                learn_speed = 300
              else:
                learn_speed = 50
              self.gasfactor = np.clip(self.gasfactor + gas_error / learn_speed * (gas_pedal_force - min_gas), 0.01, 3.0)
            if gas_error != 0.0 and (not CS.out.brakePressed) and (CS.out.vEgo > 0.0):
              if self.CP.carFingerprint in (CAR.ACURA_RDX_3G, CAR.ACURA_RDX_3G_MMR): # Faster reaction
                wind_learn_speed = 100
              else:
                wind_learn_speed = 1000
              wind_adjust = 1 + wind_brake_ms2 / wind_learn_speed
              self.windfactor = np.clip(self.windfactor * (wind_adjust if (gas_error > 0) else 1.0/wind_adjust), 0.1, 3.0)
            if gas_pedal_force <= min_gas: # don't reduce windfactor while braking, allow increases
              self.windfactor = max(self.windfactor, self.windfactor_before_brake)
            else:
              self.windfactor_before_brake = self.windfactor
            if gas_pedal_force >= self.params.BOSCH_ACCEL_MAX: # don't increase gasfactor nor windfactor at accel max, allow decreases
              self.gasfactor = min(self.gasfactor, self.gasfactor_before_gasmax)
              self.windfactor = min(self.windfactor, self.windfactor_before_gasmax)
            else:
              self.gasfactor_before_gasmax = self.gasfactor
              self.windfactor_before_gasmax = self.windfactor
          self.gasfactor, self.windfactor = self.nrdr.update_bosch_learner(
            CC, CS, actuators, accel, gas_pedal_force, wind_brake_ms2, self.pitch, self.params, live.live_learning_gas,
          )
          self.gas = float(np.interp((gas_pedal_force - min_gas) * self.gasfactor + min_gas,
                                     self.params.BOSCH_GAS_LOOKUP_BP, self.params.BOSCH_GAS_LOOKUP_V))

          # limit gas ramp to 60 units per frame, matches stock.  Higher sometimes causes powertrain to ignore gas command.
          max_gas = max(60, self.bosch_last_gas + 60)
          self.gas = min(self.gas, max_gas)
          self.bosch_last_gas = self.gas

          stopping = actuators.longControlState == LongCtrlState.stopping
          self.stopping_counter = self.stopping_counter + 1 if stopping else 0
          # CAN FD: never overlap the stock radar's own ACC_CONTROL stream; ours starts within a few
          # frames of the radar going silent (see the deferred radar disable above)
          if not (self.CP.flags & HondaFlags.BOSCH_CANFD and CS.stock_acc_alive):
            can_sends.extend(hondacan.create_acc_commands(self.packer, self.CAN, CC.enabled, CC.longActive, self.accel, self.gas,
                                                          self.stopping_counter, self.CP, gas_pedal_force))
        else:
          apply_brake = self.nrdr.nidec_brake_command(self.brake_last, wind_brake, live.full_brake_authority)
          apply_brake = int(np.clip(apply_brake * self.params.NIDEC_BRAKE_MAX, 0, self.params.NIDEC_BRAKE_MAX - 1))
          pump_on, self.last_pump_ts = brake_pump_hysteresis(apply_brake, self.apply_brake_last, self.last_pump_ts, ts)

          pcm_override = True
          can_sends.append(hondacan.create_brake_command(self.packer, self.CAN, apply_brake, pump_on,
                                                         pcm_override, pcm_cancel_cmd, alert_fcw,
                                                         CS.stock_brake, self.CP_SP,
                                                         clear_dash_faults=live.clear_dash_faults))
          self.apply_brake_last = apply_brake
          self.brake = apply_brake / self.params.NIDEC_BRAKE_MAX

          gas_error = actuators.accel - CS.out.aEgo
          if not self.nrdr.replaces_longitudinal and (not CS.out.gasPressed) and \
              (actuators.longControlState == LongCtrlState.pid) and self.CP_SP.enableGasInterceptor:
            if gas_error != 0.0 and gas > 0.0:
              self.gasfactor = np.clip(self.gasfactor + gas_error / 150 * (gas * 4.8), 0.1, 3.0)
            if gas_error != 0.0 and (not CS.out.brakePressed) and (CS.out.vEgo > 0.0):
              wind_adjust = 1 + (wind_brake * 4.8) / 1000
              self.windfactor = np.clip(self.windfactor * (wind_adjust if (gas_error > 0) else 1.0/wind_adjust), 0.1, 5.0)
            if gas <= 0.0: # don't reduce windfactor while braking, allow increases
              self.windfactor = max(self.windfactor, self.windfactor_before_brake)
            else:
              self.windfactor_before_brake = self.windfactor

          learned_gas = self.nrdr.update_nidec_learner(CC, CS, actuators, gas, brake, wind_brake, self.pitch,
                                                       live.live_learning_gas and self.CP_SP.enableGasInterceptor)
          self.gasfactor, self.windfactor = self.nrdr.longitudinal_factors
          can_sends.extend(GasInterceptorCarController.update(
            self, CC, CS, learned_gas, brake, wind_brake, self.packer, self.frame, live.roen_acceleration_limits,
          ))

    # Send dashboard UI commands. On CAN FD, ACC_HUD is a radar/ADAS look-alike that openpilot only
    # owns when it has disabled the radar (op longitudinal); in stock ACC the real system sends it and
    # the non-long safety config doesn't allowlist it.
    if (self.CP.flags & HondaFlags.BOSCH_CANFD) and CS.hud_tick and self.CP.openpilotLongitudinalControl and not CS.stock_acc_alive:
        pcm_accel = actuators.accel
        can_sends.append(hondacan.create_acc_hud(self.packer, self.CAN.pt, self.CP, CC.enabled, pcm_speed, pcm_accel,
                                                 hud_control, hud_v_cruise, CS.is_metric, CS.acc_hud, speed_control,
                                                 self.CP.openpilotLongitudinalControl))

    if self.frame % 10 == 0:
      if CC.longActive and (self.CP.carFingerprint in (CAR.ACURA_MDX_3G, CAR.ACURA_MDX_3G_MMR)):
        # standstill disengage
        if (accel >= 0.01) and (CS.out.vEgo < 4.0) and (pcm_speed < 25.0 / 3.6):
          pcm_speed = 25.0 / 3.6

      if self.CP.openpilotLongitudinalControl:
        if not (self.CP.flags & HondaFlags.BOSCH_CANFD):
          # On Nidec, this also controls longitudinal positive acceleration
          can_sends.append(hondacan.create_acc_hud(self.packer, self.CAN.pt, self.CP, CC.enabled, pcm_speed, pcm_accel,
                                                   hud_control, hud_v_cruise, CS.is_metric, CS.acc_hud, speed_control,
                                                   self.CP.openpilotLongitudinalControl,
                                                   nrdr_options=self.nrdr.nidec_hud_options(CC, CS, hud_control, live)))

      if live.spoof_camera_messages and self.CP.carFingerprint not in HONDA_BOSCH:
        can_sends.append(create_camera_message(self.packer, self.CAN.pt))

      steering_available = CS.out.cruiseState.available and CS.out.vEgo > max(self.params.STEER_GLOBAL_MIN_SPEED, self.CP.minSteerSpeed)
      reduced_steering = CS.out.steeringPressed
      steer_maxed = abs(apply_torque) >= self.params.STEER_MAX

      lkas_state_change = None
      if self.CP.flags & HondaFlags.BOSCH_CANFD:
        # The stock camera holds LKAS_STATE_CHANGE low and pulses it high for ~3s around HUD state
        # changes; holding it high permanently (the default below) suppresses the dash lane lines.
        # The key must contain exactly the signals that change the LKAS_HUD payload, nothing more:
        # steer_maxed used to be in here (via SOLID_LANES) and its 10Hz flicker during city-speed
        # steering re-triggered the pulse continuously, keeping LKAS_STATE_CHANGE high whenever a
        # real lane path was being sent - which suppressed the dash lane lines entirely.
        # latActive drives SOLID_LANES (under sunnypilot MADS the lateral control stays engaged
        # when ACC disengages, and the dash LKAS indication follows it); dashed_lanes (MADS armed,
        # from MadsCarController) drives DASHED_LANES so parked LKAS presses get cluster feedback.
        hud_key = (bool(CC.latActive), bool(self.dashed_lanes), bool(alert_steer_required), bool(CS.out.steerFaultPermanent))
        if hud_key != self.lkas_hud_key:
          self.lkas_hud_key = hud_key
          self.lkas_state_change_frames = 30  # 3s at the 10Hz LKAS_HUD rate, matching stock pulse length
        lkas_state_change = self.lkas_state_change_frames > 0
        self.lkas_state_change_frames = max(0, self.lkas_state_change_frames - 1)

      can_sends.extend(hondacan.create_lkas_hud(self.packer, self.CAN.lkas, self.CP, hud_control, CC.latActive,
                                                steering_available, reduced_steering, alert_steer_required, CS.lkas_hud, self.dashed_lanes,
                                                steer_maxed, CS, lkas_state_change=lkas_state_change))

      if self.CP.openpilotLongitudinalControl:
        # TODO: combining with create_acc_hud block above will change message order and will need replay logs regenerated
        if self.CP.flags & HondaFlags.BOSCH and not (self.CP.flags & HondaFlags.BOSCH_RADARLESS) and not (self.CP.flags & HondaFlags.BOSCH_CANFD):
          can_sends.append(hondacan.create_radar_hud(self.packer, self.CAN.pt))
        if self.CP.carFingerprint == CAR.HONDA_CIVIC_BOSCH:
          can_sends.append(hondacan.create_legacy_brake_command(self.packer, self.CAN.pt))
        if not (self.CP.flags & HondaFlags.BOSCH):
          self.speed = pcm_speed
          if not self.CP_SP.enableGasInterceptor:
            self.gas = pcm_accel / self.params.NIDEC_GAS_MAX

    # Intelligent Cruise Button Management
    can_sends.extend(IntelligentCruiseButtonManagementInterface.update(self, CC_SP, CS, self.packer, self.frame,
                                                                       self.last_button_frame, self.CAN))

    # Render OP's lane and lead car on the dash. On CAN FD these are radar look-alikes that only exist
    # (and are only allowed by panda safety) when the radar is disabled, i.e. openpilot longitudinal;
    # in stock ACC the real radar still owns LANE_PATH/HUD_OBJECTS, so don't author them.
    if ((self.frame % 2 == 0 and self.CP.flags & HondaFlags.BOSCH_RADARLESS) or
        (CS.radar_50hz_tick and self.CP.flags & HondaFlags.BOSCH_CANFD and self.CP.openpilotLongitudinalControl
         and not CS.stock_acc_alive)):
      leads = hud_objects.leads_from_model(self.model, CS.out.vEgo)
      lead = leads[0]
      lead_d = lead.dRel if lead.status else 0.0  # extend the lane out to the lead (0 = no lead)
      self.dash_lane = self.lane_path_fitter.update(self.model, CS.out.vEgo, lead_d)
      # Important: same mux for lane_path and hud_objects. Lane display freezes if muxes don't match.
      if self.CP.flags & HondaFlags.BOSCH_CANFD:
        # self.radar_mux advances one step per 50Hz tick (above), so the mux sweep stays contiguous
        # across missed ticks, unlike a frame-derived mux.
        mux = self.radar_mux
        # No LKAS_HUD_2 on CAN FD: the dash reads the lane length from the stock radar's in-band
        # terminator, so reshape the path into the terminated-prefix form (see lane_path.py).
        lane_offsets = lane_path.canfd_lane_offsets(self.dash_lane)
      else:
        mux = lane_path.MUX_CYCLE[(self.frame // 2) % len(lane_path.MUX_CYCLE)]
        lane_offsets = self.dash_lane.offsets
      lane_msg = lane_path.create_lane_path(self.packer, self.CAN.lkas, lane_offsets, mux)
      can_sends.append(lane_msg)

      # CAN FD cars have no camera HUD_OBJECTS to poll (the disabled radar owned it), so there are no
      # secondary vehicle locations: author OP's lead in slot 0 with the other slots blank (tracks=None).
      tracks = CS.hud_object_tracker.snapshot() if CS.hud_object_tracker is not None else None
      if self.CP.openpilotLongitudinalControl:
        # For OP long, replace lead car and forward rest of objects
        hud_msg = self.hud_object_author.create(self.packer, self.CAN.lkas, lead, tracks, mux, now_nanos * 1e-9,
                                                extra_leads=leads[1:])
      else:
        # For ACC, forward objects but with our mux
        hud_msg = hud_objects.forward_hud_object(self.packer, self.CAN.lkas, mux, tracks)
      can_sends.append(hud_msg)

      # On CAN FD the camera (behind the relay) also consumes these radar look-alikes, and openpilot's
      # own TX is not forwarded across the open relay. Mirror the identical packed bytes onto the camera
      # bus (packed once above, so the counter/checksum don't double-increment and both buses match).
      if self.CP.flags & HondaFlags.BOSCH_CANFD:
        for addr, dat, _ in (lane_msg, hud_msg):
          can_sends.append((addr, dat, self.CAN.camera))

    if self.frame % 20 == 0 and self.CP.flags & HondaFlags.BOSCH_RADARLESS:
      # COUNTER_2 trails the packer's COUNTER (frame//20 % 4) by one. TODO: do we need the - 1 trail?
      dl = self.dash_lane
      can_sends.append(lane_path.create_lkas_hud_2(self.packer, self.CAN.lkas, (self.frame // 20 - 1) % 4,
                                                   dl.reach, dl.lane_cross, dl.left_line, dl.right_line))

    # Radarless + CAN FD: when stock LKAS is active, the touch-steering-wheel timer/nag eventually forces an ACC
    # disengagement (on CAN FD it shows up as a brake tap from the VSA). Disable LKAS automatically and block the
    # driver's LKAS button from reaching the camera by taking over SCM_BUTTONS on the camera bus while engaged
    # (panda blocks the forwarded stock SCM_BUTTONS when engaged; the standard button spamming isn't reliably
    # accepted by the camera).
    if self.CP.flags & (HondaFlags.BOSCH_RADARLESS | HondaFlags.BOSCH_CANFD) and CC.enabled and self.frame % 4 == 0 and \
        not pcm_cancel_cmd and not CC.cruiseControl.resume:
      if self.lkas_button_send_remaining == 0 and CS.lkas_hud["LKAS_READY"] and self.frame >= self.last_lkas_button_frame + 500:
        self.lkas_button_send_remaining = 3

      if self.lkas_button_send_remaining > 0:
        self.last_lkas_button_frame = self.frame
        self.lkas_button_send_remaining -= 1
        cruise_setting = CruiseSettings.LKAS
      elif CS.cruise_setting == CruiseSettings.LKAS:
        cruise_setting = 0  # block driver's LKAS button press
      else:
        cruise_setting = CS.cruise_setting

      can_sends.append(hondacan.spam_buttons_command(self.packer, self.CAN, CS.cruise_buttons, cruise_setting,
                                                     CS.scm_ambient_light, self.CP, bus=self.CAN.camera))

    new_actuators = actuators.as_builder()
    new_actuators.speed = self.speed
    new_actuators.accel = self.accel
    new_actuators.gas = float(self.gasfactor)
    new_actuators.brake = float(self.windfactor)
    new_actuators.torque = self.last_torque
    new_actuators.torqueOutputCan = apply_torque

    if self.frame % 6000 == 0:
      self.nrdr.persist()

    self.frame += 1
    return new_actuators, can_sends
