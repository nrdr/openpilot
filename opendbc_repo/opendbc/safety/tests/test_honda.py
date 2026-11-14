#!/usr/bin/env python3
import unittest
import numpy as np

from opendbc.car.honda.values import HondaSafetyFlags
from opendbc.safety import ALTERNATIVE_EXPERIENCE
from opendbc.safety.tests.libsafety import libsafety_py
import opendbc.safety.tests.common as common
from opendbc.car.structs import CarParams
from opendbc.safety.tests.common import CANPackerSafety, MAX_WRONG_COUNTERS
from opendbc.safety.tests.gas_interceptor_common import GasInterceptorSafetyTest

from opendbc.sunnypilot.car.honda.values_ext import HondaSafetyFlagsSP

HONDA_N_COMMON_TX_MSGS = [[0xE4, 0], [0x194, 0], [0x33D, 0]]
HONDA_N_STOCK_LONGITUDINAL_TX_MSGS = [[0x1FA, 0], [0x30C, 0]]


class Btn:
  NONE = 0
  MAIN = 1
  CANCEL = 2
  SET = 3
  RESUME = 4

# Honda safety has several different configurations tested here:
#  * Nidec
#    * normal (PCM-enable)
#    * alt SCM messages  (PCM-enable)
#    * gas interceptor (button-enable)
#    * gas interceptor with alt SCM messages (button-enable)
#  * Bosch
#    * Bosch with Longitudinal Support
#  * Bosch Radarless
#    * Bosch Radarless with Longitudinal Support
#  * Bosch CANFD
#    * Bosch CANFD with Longitudinal Support


class HondaButtonEnableBase(common.CarSafetyTest):

  # override these inherited tests since we're using button enable
  def test_disable_control_allowed_from_cruise(self):
    pass

  def test_enable_control_allowed_from_cruise(self):
    pass

  def test_cruise_engaged_prev(self):
    pass

  def test_buttons_with_main_off(self):
    for btn in (Btn.SET, Btn.RESUME, Btn.CANCEL):
      self.safety.set_controls_allowed(1)
      self._rx(self._acc_state_msg(False))
      self._rx(self._button_msg(btn, main_on=False))
      self.assertFalse(self.safety.get_controls_allowed())

  def test_set_resume_buttons(self):
    """
      Both SET and RES should enter controls allowed on their falling edge.
    """
    for main_on in (True, False):
      self._rx(self._acc_state_msg(main_on))
      for btn_prev in range(8):
        for btn_cur in range(8):
          self._rx(self._button_msg(Btn.NONE))
          self.safety.set_controls_allowed(0)
          for _ in range(10):
            self._rx(self._button_msg(btn_prev))
            self.assertFalse(self.safety.get_controls_allowed())

          # should enter controls allowed on falling edge and not transitioning to cancel or main
          should_enable = (main_on and
                           btn_cur != btn_prev and
                           btn_prev in (Btn.RESUME, Btn.SET) and
                           btn_cur not in (Btn.CANCEL, Btn.MAIN))

          self._rx(self._button_msg(btn_cur, main_on=main_on))
          self.assertEqual(should_enable, self.safety.get_controls_allowed(), msg=f"{main_on=} {btn_prev=} {btn_cur=}")

  def test_main_cancel_buttons(self):
    """
      Both MAIN and CANCEL should exit controls immediately.
    """
    for btn in (Btn.MAIN, Btn.CANCEL):
      self.safety.set_controls_allowed(1)
      self._rx(self._button_msg(btn, main_on=True))
      self.assertFalse(self.safety.get_controls_allowed())

  def test_disengage_on_main(self):
    self.safety.set_controls_allowed(1)
    self._rx(self._acc_state_msg(True))
    self.assertTrue(self.safety.get_controls_allowed())
    self._rx(self._acc_state_msg(False))
    self.assertFalse(self.safety.get_controls_allowed())

  def test_rx_hook(self):

    # TODO: move this test to common
    # checksum checks
    for msg_type in ["btn", "gas", "speed"]:
      self.safety.set_controls_allowed(1)
      if msg_type == "btn":
        msg = self._button_msg(Btn.SET)
      if msg_type == "gas":
        msg = self._user_gas_msg(0)
      if msg_type == "speed":
        msg = self._speed_msg(0)
      self.assertTrue(self._rx(msg))
      if msg_type != "btn":
        msg[0].data[4] = 0  # invalidate checksum
        msg[0].data[5] = 0
        msg[0].data[6] = 0
        msg[0].data[7] = 0
        self.assertFalse(self._rx(msg))
        self.assertFalse(self.safety.get_controls_allowed())

    # counter
    # Skip every other counter to trigger counter faults.
    for i in range(MAX_WRONG_COUNTERS + 1):
      self._speed_msg(0)
      self._button_msg(Btn.SET)
      self._user_gas_msg(0)
      if i < MAX_WRONG_COUNTERS:
        self.safety.set_controls_allowed(1)
        self._rx(self._button_msg(Btn.SET))
        self._rx(self._speed_msg(0))
        self._rx(self._user_gas_msg(0))
      else:
        self.assertFalse(self._rx(self._button_msg(Btn.SET)))
        self.assertFalse(self._rx(self._speed_msg(0)))
        self.assertFalse(self._rx(self._user_gas_msg(0)))
        self.assertFalse(self.safety.get_controls_allowed())

    # restore counters for future tests with a couple of good messages
    for _ in range(2):
      self.safety.set_controls_allowed(1)
      self._rx(self._button_msg(Btn.SET, main_on=True))
      self._rx(self._speed_msg(0))
      self._rx(self._user_gas_msg(0))
    self._rx(self._button_msg(Btn.SET, main_on=True))
    self.assertTrue(self.safety.get_controls_allowed())


class HondaPcmEnableBase(common.CarSafetyTest):

  def test_buttons(self):
    """
      Buttons should only cancel in this configuration,
      since our state is tied to the PCM's cruise state.
    """
    for controls_allowed in (True, False):
      for main_on in (True, False):
        # not a valid state
        if controls_allowed and not main_on:
          continue

        for btn in (Btn.SET, Btn.RESUME, Btn.CANCEL):
          self.safety.set_controls_allowed(controls_allowed)
          self._rx(self._acc_state_msg(main_on))

          # btn + none for falling edge
          self._rx(self._button_msg(btn, main_on=main_on))
          self._rx(self._button_msg(Btn.NONE, main_on=main_on))

          if btn == Btn.CANCEL:
            self.assertFalse(self.safety.get_controls_allowed())
          else:
            self.assertEqual(controls_allowed, self.safety.get_controls_allowed())


class HondaBase(common.CarSafetyTest):
  MAX_BRAKE = 255
  PT_BUS: int | None = None  # must be set when inherited
  STEER_BUS: int | None = None  # must be set when inherited
  BUTTONS_BUS: int | None = None  # must be set when inherited, tx on this bus, rx on PT_BUS

  RELAY_MALFUNCTION_ADDRS = {0: (0xE4, 0x194)}  # STEERING_CONTROL

  cnt_speed = 0
  cnt_button = 0
  cnt_brake = 0
  cnt_powertrain_data = 0
  cnt_acc_state = 0

  def _powertrain_data_msg(self, cruise_on=None, brake_pressed=None, gas_pressed=None):
    # preserve the state
    if cruise_on is None:
      # or'd with controls allowed since the tests use it to "enable" cruise
      cruise_on = self.safety.get_cruise_engaged_prev() or self.safety.get_controls_allowed()
    if brake_pressed is None:
      brake_pressed = self.safety.get_brake_pressed_prev()
    if gas_pressed is None:
      gas_pressed = self.safety.get_gas_pressed_prev()

    values = {
      "ACC_STATUS": cruise_on,
      "BRAKE_PRESSED": brake_pressed,
      "PEDAL_GAS": gas_pressed,
      "COUNTER": self.cnt_powertrain_data % 4
    }
    self.__class__.cnt_powertrain_data += 1
    return self.packer.make_can_msg_safety("POWERTRAIN_DATA", self.PT_BUS, values)

  def _pcm_status_msg(self, enable):
    return self._powertrain_data_msg(cruise_on=enable)

  def _speed_msg(self, speed):
    values = {"XMISSION_SPEED": speed, "COUNTER": self.cnt_speed % 4}
    self.__class__.cnt_speed += 1
    return self.packer.make_can_msg_safety("ENGINE_DATA", self.PT_BUS, values)

  def _acc_state_msg(self, main_on):
    values = {"MAIN_ON": main_on, "COUNTER": self.cnt_acc_state % 4}
    self.__class__.cnt_acc_state += 1
    return self.packer.make_can_msg_safety("SCM_FEEDBACK", self.PT_BUS, values)

  def _button_msg(self, buttons, main_on=False, bus=None):
    bus = self.PT_BUS if bus is None else bus
    values = {"CRUISE_BUTTONS": buttons, "COUNTER": self.cnt_button % 4}
    self.__class__.cnt_button += 1
    return self.packer.make_can_msg_safety("SCM_BUTTONS", bus, values)

  def _user_brake_msg(self, brake):
    return self._powertrain_data_msg(brake_pressed=brake)

  def _user_gas_msg(self, gas):
    return self._powertrain_data_msg(gas_pressed=gas)

  def _send_steer_msg(self, steer):
    values = {"STEER_TORQUE": steer}
    return self.packer.make_can_msg_safety("STEERING_CONTROL", self.STEER_BUS, values)

  def _send_brake_msg(self, brake):
    # must be implemented when inherited
    raise NotImplementedError

  def test_disengage_on_brake(self):
    self.safety.set_controls_allowed(1)
    self._rx(self._user_brake_msg(1))
    self.assertFalse(self.safety.get_controls_allowed())

  def test_steer_safety_check(self):
    self.safety.set_controls_allowed(0)
    self.assertTrue(self._tx(self._send_steer_msg(0x0000)))
    self.assertFalse(self._tx(self._send_steer_msg(0x1000)))

  def _lkas_button_msg(self, lkas_button=False, setting_btn=0):
    values = {"CRUISE_SETTING": 1 if lkas_button else setting_btn, "COUNTER": self.cnt_button % 4}
    self.__class__.cnt_button += 1
    return self.packer.make_can_msg_safety("SCM_BUTTONS", self.PT_BUS, values)

  def test_enable_control_allowed_with_mads_button(self):
    """Tests MADS button state transitions and internal button press state."""
    for enable_mads in (True, False):
      with self.subTest("enable_mads", mads_enabled=enable_mads):
        self.safety.set_mads_params(enable_mads, False, False)

        # Verify initial state
        self._rx(self._lkas_button_msg(False, 0))
        self.assertEqual(0, self.safety.get_mads_button_press())  # NOT_PRESSED
        self.assertFalse(self.safety.get_controls_allowed_lateral())

        # Verify press sets correct internal state
        self._rx(self._lkas_button_msg(False, 1))
        self.assertEqual(1, self.safety.get_mads_button_press())  # PRESSED
        self.assertEqual(enable_mads, self.safety.get_controls_allowed_lateral())

        # Verify release sets correct internal state
        self._rx(self._lkas_button_msg(False, 0))
        self.assertEqual(0, self.safety.get_mads_button_press())  # NOT_PRESSED
        self.assertEqual(enable_mads, self.safety.get_controls_allowed_lateral())

        # Test invalid values - should not change button press state
        for invalid_setting in (2, 3):
          self._rx(self._lkas_button_msg(False, invalid_setting))
          self.assertEqual(0, self.safety.get_mads_button_press())  # Should remain NOT_PRESSED
          self.assertEqual(enable_mads, self.safety.get_controls_allowed_lateral())

        # Verify we can still transition after invalid values
        self._rx(self._lkas_button_msg(False, 1))
        self.assertEqual(1, self.safety.get_mads_button_press())
        self._rx(self._lkas_button_msg(False, 0))
        self.assertEqual(0, self.safety.get_mads_button_press())


# ********************* Honda Nidec **********************


class TestHondaNidecSafetyBase(HondaBase):
  TX_MSGS = HONDA_N_COMMON_TX_MSGS + HONDA_N_STOCK_LONGITUDINAL_TX_MSGS
  FWD_BLACKLISTED_ADDRS = {2: [0xE4, 0x194, 0x33D, 0x30C]}
  RELAY_MALFUNCTION_ADDRS = {0: (0xE4, 0x194, 0x33D, 0x30C)}

  PT_BUS = 0
  STEER_BUS = 0
  BUTTONS_BUS = 0

  MAX_GAS = 198

  BRAKE_SIG = "COMPUTER_BRAKE"

  def setUp(self):
    self.packer = CANPackerSafety("honda_civic_touring_2016_can_generated")
    self.safety = libsafety_py.libsafety
    self.safety.set_safety_hooks(CarParams.SafetyModel.hondaNidec, 0)
    self.safety.init_tests()

  def _send_brake_msg(self, brake, aeb_req=0, bus=0):
    values = {self.BRAKE_SIG: brake, "AEB_REQ_1": aeb_req}
    return self.packer.make_can_msg_safety("BRAKE_COMMAND", bus, values)

  def _rx_brake_msg(self, brake, aeb_req=0):
    return self._send_brake_msg(brake, aeb_req, bus=2)

  def _send_acc_hud_msg(self, pcm_gas, pcm_speed):
    # Used to control ACC on Nidec without pedal
    values = {"PCM_GAS": pcm_gas, "PCM_SPEED": pcm_speed}
    return self.packer.make_can_msg_safety("ACC_HUD", 0, values)

  def _driver_gas_on(self):
    self._rx(self._user_gas_msg(1))

  def _driver_gas_off(self):
    self._rx(self._user_gas_msg(0))

  def test_acc_hud_safety_check(self):
    for controls_allowed in [True, False]:
      self.safety.set_controls_allowed(controls_allowed)
      for pcm_gas in range(255):
        for pcm_speed in range(100):
          send = (controls_allowed and pcm_gas <= self.MAX_GAS) or (pcm_gas == 0 and pcm_speed == 0)
          self.assertEqual(send, self._tx(self._send_acc_hud_msg(pcm_gas, pcm_speed)))

  def test_acc_hud_gas_pressed_passthrough(self):
    # the carcontroller mirrors the driver's pedal onto ACC_HUD during a gas override; blocking it
    # makes the PCM drop ACC_STATUS, so the speed/gas checks are waived while the pedal is pressed
    self.safety.set_controls_allowed(True)
    self._driver_gas_on()
    self.assertTrue(self.safety.get_gas_pressed_prev())
    for pcm_gas in (0, 1, self.MAX_GAS, 255):
      for pcm_speed in (0, 1, 99):
        self.assertTrue(self._tx(self._send_acc_hud_msg(pcm_gas, pcm_speed)))

    # pedal released: back to the standard limits
    self._driver_gas_off()
    self.assertFalse(self.safety.get_gas_pressed_prev())
    self.assertTrue(self._tx(self._send_acc_hud_msg(self.MAX_GAS, 99)))
    self.assertFalse(self._tx(self._send_acc_hud_msg(self.MAX_GAS + 1, 0)))
    self.safety.set_controls_allowed(False)
    self.assertFalse(self._tx(self._send_acc_hud_msg(1, 0)))

  def test_fwd_hook(self):
    # normal operation, not forwarding AEB
    self.FWD_BLACKLISTED_ADDRS[2].append(0x1FA)
    self.safety.set_honda_fwd_brake(False)
    super().test_fwd_hook()

    # forwarding AEB brake signal
    self.FWD_BLACKLISTED_ADDRS = {2: [0xE4, 0x194, 0x33D, 0x30C]}
    self.safety.set_honda_fwd_brake(True)
    super().test_fwd_hook()

  def test_honda_fwd_brake_latching(self):
    # Shouldn't fwd stock Honda requesting brake without AEB
    self.assertTrue(self._rx(self._rx_brake_msg(self.MAX_BRAKE, aeb_req=0)))
    self.assertFalse(self.safety.get_honda_fwd_brake())

    # Now allow controls and request some brake
    openpilot_brake = round(self.MAX_BRAKE / 2.0)
    self.safety.set_controls_allowed(True)
    self.assertTrue(self._tx(self._send_brake_msg(openpilot_brake)))

    # Still shouldn't fwd stock Honda brake until it's more than openpilot's
    for stock_honda_brake in range(self.MAX_BRAKE + 1):
      self.assertTrue(self._rx(self._rx_brake_msg(stock_honda_brake, aeb_req=1)))
      should_fwd_brake = stock_honda_brake >= openpilot_brake
      self.assertEqual(should_fwd_brake, self.safety.get_honda_fwd_brake())

    # Shouldn't stop fwding until AEB event is over
    for stock_honda_brake in range(self.MAX_BRAKE + 1)[::-1]:
      self.assertTrue(self._rx(self._rx_brake_msg(stock_honda_brake, aeb_req=1)))
      self.assertTrue(self.safety.get_honda_fwd_brake())

    self.assertTrue(self._rx(self._rx_brake_msg(0, aeb_req=0)))
    self.assertFalse(self.safety.get_honda_fwd_brake())

  def test_brake_safety_check(self):
    for fwd_brake in [False, True]:
      self.safety.set_honda_fwd_brake(fwd_brake)
      for brake in np.arange(0, self.MAX_BRAKE + 10, 1):
        for controls_allowed in [True, False]:
          self.safety.set_controls_allowed(controls_allowed)
          if fwd_brake:
            send = False  # block openpilot brake msg when fwd'ing stock msg
          elif controls_allowed:
            send = self.MAX_BRAKE >= brake >= 0
          else:
            send = brake == 0
          self.assertEqual(send, self._tx(self._send_brake_msg(brake)))

    # Inactive brake must pass when gas blocks longitudinal actuation
    self.safety.set_honda_fwd_brake(False)
    self.safety.set_controls_allowed(True)
    self.safety.set_gas_pressed_prev(True)
    self.assertFalse(self.safety.get_longitudinal_allowed())
    self.assertTrue(self._tx(self._send_brake_msg(0)))
    self.assertFalse(self._tx(self._send_brake_msg(1)))


class TestHondaNidecPcmSafety(HondaPcmEnableBase, TestHondaNidecSafetyBase):
  """
    Covers the Honda Nidec safety mode
  """

  # Nidec doesn't disengage on falling edge of cruise. See comment in safety_honda.h
  def test_disable_control_allowed_from_cruise(self):
    pass


class TestHondaNidecGasInterceptorSafety(GasInterceptorSafetyTest, HondaButtonEnableBase, TestHondaNidecSafetyBase):
  """
    Covers the Honda Nidec safety mode with a gas interceptor, switches to a button-enable car
  """

  TX_MSGS = HONDA_N_COMMON_TX_MSGS + HONDA_N_STOCK_LONGITUDINAL_TX_MSGS + [[0x200, 0]]
  INTERCEPTOR_THRESHOLD = 492

  def setUp(self):
    self.packer = CANPackerSafety("honda_civic_touring_2016_can_generated")
    self.safety = libsafety_py.libsafety
    self.safety.set_current_safety_param_sp(HondaSafetyFlagsSP.GAS_INTERCEPTOR)
    self.safety.set_safety_hooks(CarParams.SafetyModel.hondaNidec, 0)
    self.safety.init_tests()

  def test_vehicle_specific_interceptor_threshold(self):
    self.safety.set_current_safety_param_sp(HondaSafetyFlagsSP.GAS_INTERCEPTOR |
                                            HondaSafetyFlagsSP.GAS_INTERCEPTOR_THRESHOLD_512)
    self.safety.set_safety_hooks(CarParams.SafetyModel.hondaNidec, 0)
    self.safety.init_tests()

    for gas, pressed in ((492, False), (493, False), (512, False), (513, True)):
      self.safety.set_controls_allowed(True)
      self._rx(self._interceptor_user_gas(gas))
      self.assertEqual(not pressed, self.safety.get_longitudinal_allowed())

  def _driver_gas_on(self):
    self._rx(self._interceptor_user_gas(self.INTERCEPTOR_THRESHOLD + 1))

  def _driver_gas_off(self):
    self._rx(self._interceptor_user_gas(0))


class TestHondaNidecPcmAltSafety(TestHondaNidecPcmSafety):
  """
    Covers the Honda Nidec safety mode with alt SCM messages
  """
  def setUp(self):
    self.packer = CANPackerSafety("acura_ilx_2016_can_generated")
    self.safety = libsafety_py.libsafety
    self.safety.set_safety_hooks(CarParams.SafetyModel.hondaNidec, HondaSafetyFlags.NIDEC_ALT)
    self.safety.init_tests()

  def _acc_state_msg(self, main_on):
    values = {"MAIN_ON": main_on, "COUNTER": self.cnt_acc_state % 4}
    self.__class__.cnt_acc_state += 1
    return self.packer.make_can_msg_safety("SCM_BUTTONS", self.PT_BUS, values)

  def _button_msg(self, buttons, main_on=False, bus=None):
    bus = self.PT_BUS if bus is None else bus
    values = {"CRUISE_BUTTONS": buttons, "MAIN_ON": main_on, "COUNTER": self.cnt_button % 4}
    self.__class__.cnt_button += 1
    return self.packer.make_can_msg_safety("SCM_BUTTONS", bus, values)


class TestHondaNidecAltGasInterceptorSafety(GasInterceptorSafetyTest, HondaButtonEnableBase, TestHondaNidecSafetyBase):
  """
    Covers the Honda Nidec safety mode with alt SCM messages and gas interceptor, switches to a button-enable car
  """

  TX_MSGS = HONDA_N_COMMON_TX_MSGS + HONDA_N_STOCK_LONGITUDINAL_TX_MSGS + [[0x200, 0]]
  INTERCEPTOR_THRESHOLD = 492

  def setUp(self):
    self.packer = CANPackerSafety("acura_ilx_2016_can_generated")
    self.safety = libsafety_py.libsafety
    self.safety.set_current_safety_param_sp(HondaSafetyFlagsSP.GAS_INTERCEPTOR)
    self.safety.set_safety_hooks(CarParams.SafetyModel.hondaNidec, HondaSafetyFlags.NIDEC_ALT)
    self.safety.init_tests()

  def _driver_gas_on(self):
    self._rx(self._interceptor_user_gas(self.INTERCEPTOR_THRESHOLD + 1))

  def _driver_gas_off(self):
    self._rx(self._interceptor_user_gas(0))

  def _acc_state_msg(self, main_on):
    values = {"MAIN_ON": main_on, "COUNTER": self.cnt_acc_state % 4}
    self.__class__.cnt_acc_state += 1
    return self.packer.make_can_msg_safety("SCM_BUTTONS", self.PT_BUS, values)

  def _button_msg(self, buttons, main_on=False, bus=None):
    bus = self.PT_BUS if bus is None else bus
    values = {"CRUISE_BUTTONS": buttons, "MAIN_ON": main_on, "COUNTER": self.cnt_button % 4}
    self.__class__.cnt_button += 1
    return self.packer.make_can_msg_safety("SCM_BUTTONS", bus, values)


class TestHondaNidecStockLongitudinalSafety(HondaPcmEnableBase, TestHondaNidecSafetyBase):
  TX_MSGS = HONDA_N_COMMON_TX_MSGS + [[0x1A6, 0], ]
  FWD_BLACKLISTED_ADDRS = {2: [0xE4, 0x194, 0x33D]}
  RELAY_MALFUNCTION_ADDRS = {0: (0xE4, 0x194, 0x33D)}

  def setUp(self):
    self.packer = CANPackerSafety("honda_civic_touring_2016_can_generated")
    self.safety = libsafety_py.libsafety
    self.safety.set_current_safety_param_sp(HondaSafetyFlagsSP.STOCK_LONGITUDINAL)
    self.safety.set_safety_hooks(CarParams.SafetyModel.hondaNidec, 0)
    self.safety.init_tests()

  # Nidec doesn't disengage on falling edge of cruise. See comment in safety_honda.h
  def test_disable_control_allowed_from_cruise(self):
    pass

  def _send_brake_msg(self, brake, aeb_req=0, bus=0):
    pass

  def _rx_brake_msg(self, brake, aeb_req=0):
    pass

  def _send_acc_hud_msg(self, pcm_gas, pcm_speed):
    pass

  def test_acc_hud_safety_check(self):
    pass

  def test_acc_hud_gas_pressed_passthrough(self):
    pass

  def test_fwd_hook(self):
    pass

  def test_honda_fwd_brake_latching(self):
    pass

  def test_brake_safety_check(self):
    pass


class TestHondaNidecPcmRlxBridgeSafety(TestHondaNidecPcmAltSafety):
  """
    Covers the Honda Nidec safety mode for the RLX steer-bus bridge: a bridge panda relays the stock
    camera's LKAS_HUD onto the powertrain bus, so 0x33D on bus 0 is a checked RX message rather than
    a relay malfunction
  """
  FWD_BLACKLISTED_ADDRS = {2: [0xE4, 0x194, 0x30C]}
  RELAY_MALFUNCTION_ADDRS = {0: (0xE4, 0x194, 0x30C)}

  BRAKE_SIG = "COMPUTER_BRAKE_HYBRID"
  cnt_lkas_hud = 0

  def setUp(self):
    self.packer = CANPackerSafety("acura_rlx_2017_can_generated")
    self.safety = libsafety_py.libsafety
    self.safety.set_current_safety_param_sp(HondaSafetyFlagsSP.NIDEC_HYBRID)
    self.safety.set_safety_hooks(CarParams.SafetyModel.hondaNidec,
                                 HondaSafetyFlags.NIDEC_ALT | HondaSafetyFlags.RLX_STEER_BRIDGE)
    self.safety.init_tests()

  def _send_brake_msg(self, brake, aeb_req=0, bus=0):
    values = {"COMPUTER_BRAKE_HYBRID": brake, "AEB_REQ_1": aeb_req}
    return self.packer.make_can_msg_safety("BRAKE_COMMAND", bus, values)

  def _lkas_hud_msg(self, lkas_problem=False, bus=0):
    values = {"LKAS_PROBLEM": lkas_problem, "COUNTER": self.cnt_lkas_hud % 4}
    self.__class__.cnt_lkas_hud += 1
    return self.packer.make_can_msg_safety("LKAS_HUD", bus, values)

  def test_steer_safety_check(self):
    # the RLX's 4 byte STEERING_CONTROL only has a 12 bit torque field
    self.safety.set_controls_allowed(0)
    self.assertTrue(self._tx(self._send_steer_msg(0x0000)))
    self.assertFalse(self._tx(self._send_steer_msg(0x0100)))

  def test_fwd_hook(self):
    # normal operation, not forwarding AEB. LKAS_HUD is no longer statically blocked
    self.FWD_BLACKLISTED_ADDRS = {2: [0xE4, 0x194, 0x30C, 0x1FA]}
    self.safety.set_honda_fwd_brake(False)
    HondaBase.test_fwd_hook(self)

    # forwarding AEB brake signal
    self.FWD_BLACKLISTED_ADDRS = {2: [0xE4, 0x194, 0x30C]}
    self.safety.set_honda_fwd_brake(True)
    HondaBase.test_fwd_hook(self)

  def test_lkas_hud_rx_check(self):
    # the bridged stock camera LKAS_HUD is expected on the powertrain bus and never a relay malfunction
    self.safety.set_controls_allowed(True)
    for lkas_problem in (False, True):
      self.assertTrue(self._rx(self._lkas_hud_msg(lkas_problem)))
    self.assertFalse(self.safety.get_relay_malfunction())
    self.assertTrue(self.safety.get_controls_allowed())

    # a bad checksum is rejected and disengages
    msg = self._lkas_hud_msg()
    msg[0].data[4] ^= 0x1
    self.assertFalse(self._rx(msg))
    self.assertFalse(self.safety.get_controls_allowed())

    # so are repeated counter skips
    for i in range(MAX_WRONG_COUNTERS + 1):
      self.__class__.cnt_lkas_hud += 1
      if i < MAX_WRONG_COUNTERS:
        self.safety.set_controls_allowed(True)
        self._rx(self._lkas_hud_msg())
      else:
        self.assertFalse(self._rx(self._lkas_hud_msg()))
        self.assertFalse(self.safety.get_controls_allowed())

    # recover with good messages
    for _ in range(2):
      self._rx(self._lkas_hud_msg())
    self.assertTrue(self._rx(self._lkas_hud_msg()))


# ********************* Honda Bosch **********************


class TestHondaBoschSafetyBase(HondaBase):
  PT_BUS = 1
  STEER_BUS = 0
  BUTTONS_BUS = 1

  TX_MSGS = [[0xE4, 0], [0xE5, 0], [0x296, 1], [0x33D, 0], [0x33DA, 0], [0x33DB, 0]]
  FWD_BLACKLISTED_ADDRS = {2: [0xE4, 0xE5, 0x33D, 0x33DA, 0x33DB]}
  RELAY_MALFUNCTION_ADDRS = {0: (0xE4, 0xE5, 0x33D, 0x33DA, 0x33DB)}  # STEERING_CONTROL, BOSCH_SUPPLEMENTAL_1

  def setUp(self):
    self.packer = CANPackerSafety("honda_civic_hatchback_ex_2017_can_generated")
    self.safety = libsafety_py.libsafety

  def _alt_brake_msg(self, brake):
    values = {"BRAKE_PRESSED": brake, "COUNTER": self.cnt_brake % 4}
    self.__class__.cnt_brake += 1
    return self.packer.make_can_msg_safety("BRAKE_MODULE", self.PT_BUS, values)

  def _send_brake_msg(self, brake):
    pass

  def test_spam_cancel_safety_check(self):
    self.safety.set_controls_allowed(0)
    self.assertTrue(self._tx(self._button_msg(Btn.CANCEL, bus=self.BUTTONS_BUS)))
    self.assertFalse(self._tx(self._button_msg(Btn.RESUME, bus=self.BUTTONS_BUS)))
    self.assertFalse(self._tx(self._button_msg(Btn.SET, bus=self.BUTTONS_BUS)))
    # do not block resume if we are engaged already
    self.safety.set_controls_allowed(1)
    self.assertTrue(self._tx(self._button_msg(Btn.RESUME, bus=self.BUTTONS_BUS)))


class TestHondaBoschAltBrakeSafetyBase(TestHondaBoschSafetyBase):
  """
    Base Bosch safety test class with an alternate brake message
  """
  def setUp(self):
    super().setUp()
    self.safety.set_safety_hooks(CarParams.SafetyModel.hondaBosch, HondaSafetyFlags.ALT_BRAKE)
    self.safety.init_tests()

  def _user_brake_msg(self, brake):
    return self._alt_brake_msg(brake)

  def test_alt_brake_rx_hook(self):
    self.safety.set_honda_alt_brake_msg(1)
    self.safety.set_controls_allowed(1)
    msg = self._alt_brake_msg(0)
    self.assertTrue(self._rx(msg))
    msg[0].data[2] = msg[0].data[2] & 0xF0  # invalidate checksum
    self.assertFalse(self._rx(msg))
    self.assertFalse(self.safety.get_controls_allowed())

  def test_alt_disengage_on_brake(self):
    self.safety.set_honda_alt_brake_msg(1)
    self.safety.set_controls_allowed(1)
    self._rx(self._alt_brake_msg(1))
    self.assertFalse(self.safety.get_controls_allowed())

    self.safety.set_honda_alt_brake_msg(0)
    self.safety.set_controls_allowed(1)
    self._rx(self._alt_brake_msg(1))
    self.assertTrue(self.safety.get_controls_allowed())


class TestHondaBoschSafety(HondaPcmEnableBase, TestHondaBoschSafetyBase):
  """
    Covers the Honda Bosch safety mode with stock longitudinal
  """
  def setUp(self):
    super().setUp()
    self.safety.set_safety_hooks(CarParams.SafetyModel.hondaBosch, 0)
    self.safety.init_tests()


class TestHondaBoschAltBrakeSafety(HondaPcmEnableBase, TestHondaBoschAltBrakeSafetyBase):
  """
    Covers the Honda Bosch safety mode with stock longitudinal and an alternate brake message
  """


class TestHondaBoschLongSafety(HondaButtonEnableBase, TestHondaBoschSafetyBase):
  """
    Covers the Honda Bosch safety mode with longitudinal control
  """
  NO_GAS = -30000
  MAX_GAS = 2000
  MAX_ACCEL = 2.0  # accel is used for brakes, but openpilot can set positive values
  MIN_ACCEL = -3.5

  STEER_BUS = 1
  TX_MSGS = [[0xE4, 1], [0x1DF, 1], [0x1EF, 1], [0x1FA, 1], [0x30C, 1], [0x33D, 1], [0x33DA, 1], [0x33DB, 1], [0x39F, 1], [0x18DAB0F1, 1]]
  FWD_BLACKLISTED_ADDRS = {}
  # 0x1DF is to test that radar is disabled
  RELAY_MALFUNCTION_ADDRS = {1: (0xE4, 0x1DF, 0x33D, 0x33DA, 0x33DB)}  # STEERING_CONTROL, ACC_CONTROL

  def setUp(self):
    super().setUp()
    self.safety.set_safety_hooks(CarParams.SafetyModel.hondaBosch, HondaSafetyFlags.BOSCH_LONG)
    self.safety.init_tests()

  def _send_gas_brake_msg(self, gas, accel):
    values = {
      "GAS_COMMAND": gas,
      "ACCEL_COMMAND": accel,
      "BRAKE_REQUEST": accel < 0,
    }
    return self.packer.make_can_msg_safety("ACC_CONTROL", self.PT_BUS, values)

  # Longitudinal doesn't need to send buttons
  def test_spam_cancel_safety_check(self):
    pass

  def test_diagnostics(self):
    tester_present = libsafety_py.make_CANPacket(0x18DAB0F1, self.PT_BUS, b"\x02\x3E\x80\x00\x00\x00\x00\x00")
    self.assertTrue(self._tx(tester_present))

    not_tester_present = libsafety_py.make_CANPacket(0x18DAB0F1, self.PT_BUS, b"\x03\xAA\xAA\x00\x00\x00\x00\x00")
    self.assertFalse(self._tx(not_tester_present))

    # the radar disable requests are only allowed on CAN FD
    ext_diag = libsafety_py.make_CANPacket(0x18DAB0F1, self.PT_BUS, b"\x02\x10\x03\x00\x00\x00\x00\x00")
    self.assertFalse(self._tx(ext_diag))
    comm_control_disable = libsafety_py.make_CANPacket(0x18DAB0F1, self.PT_BUS, b"\x03\x28\x83\x03\x00\x00\x00\x00")
    self.assertFalse(self._tx(comm_control_disable))

  def test_gas_safety_check(self):
    for controls_allowed in [True, False]:
      for gas in np.arange(self.NO_GAS, self.MAX_GAS + 2000, 100):
        accel = 0 if gas < 0 else gas / 1000
        self.safety.set_controls_allowed(controls_allowed)
        send = (controls_allowed and 0 <= gas <= self.MAX_GAS) or gas == self.NO_GAS
        self.assertEqual(send, self._tx(self._send_gas_brake_msg(gas, accel)), (controls_allowed, gas, accel))

  def test_brake_safety_check(self):
    for controls_allowed in [True, False]:
      for accel in np.arange(self.MIN_ACCEL - 1, self.MAX_ACCEL + 1, 0.01):
        accel = round(accel, 2)  # floats might not hit exact boundary conditions without rounding
        self.safety.set_controls_allowed(controls_allowed)
        send = self.MIN_ACCEL <= accel <= self.MAX_ACCEL if controls_allowed else accel == 0
        self.assertEqual(send, self._tx(self._send_gas_brake_msg(self.NO_GAS, accel)), (controls_allowed, accel))


class TestHondaBoschRadarlessSafetyBase(TestHondaBoschSafetyBase):
  """Base class for radarless Honda Bosch"""
  PT_BUS = 0
  STEER_BUS = 0
  BUTTONS_BUS = 2  # camera controls ACC, need to send buttons on bus 2

  TX_MSGS = [[0xE4, 0], [0x296, 2], [0x33D, 0], [0x6CD5554, 0], [0xF31AA54, 0], [0x6CD5557, 0]]
  FWD_BLACKLISTED_ADDRS = {2: [0xE4, 0x33D, 0x6CD5554, 0xF31AA54, 0x6CD5557]}
  # STEERING_CONTROL, LANE_PATH, LKAS_HUD_2, HUD_OBJECTS
  RELAY_MALFUNCTION_ADDRS = {0: (0xE4, 0x33D, 0x6CD5554, 0xF31AA54, 0x6CD5557)}

  def setUp(self):
    self.packer = CANPackerSafety("honda_bosch_radarless_generated")
    self.safety = libsafety_py.libsafety

  def test_buttons_fwd(self):
    # SCM_BUTTONS (0x296) forwards to the camera unless OP's replacement button stream is flowing
    # (engaged + a recent OP SCM_BUTTONS tx on the camera bus). The camera needs the message content
    # beyond the buttons, so the block fails safe back to forwarding when OP stops sending (e.g. it
    # refuses to engage even though the panda's button state machine allowed controls).
    self.safety.set_controls_allowed(False)
    self.assertEqual(2, self.safety.safety_fwd_hook(0, 0x296))

    # engaged but OP not sending buttons: keep forwarding
    self.safety.set_controls_allowed(True)
    self.assertEqual(2, self.safety.safety_fwd_hook(0, 0x296))

    # OP button stream flowing: block the stock buttons
    self.assertTrue(self._tx(self._button_msg(Btn.NONE, bus=2)))
    self.assertEqual(-1, self.safety.safety_fwd_hook(0, 0x296))

    # never blocked while disengaged
    self.safety.set_controls_allowed(False)
    self.assertEqual(2, self.safety.safety_fwd_hook(0, 0x296))
    self.safety.set_controls_allowed(True)
    self.assertEqual(-1, self.safety.safety_fwd_hook(0, 0x296))

    # freshness decays after 10 stock button frames without an OP tx
    for _ in range(10):
      self._rx(self._button_msg(Btn.NONE, main_on=True))
    self.assertEqual(2, self.safety.safety_fwd_hook(0, 0x296))


class TestHondaBoschRadarlessSafety(HondaPcmEnableBase, TestHondaBoschRadarlessSafetyBase):
  """
    Covers the Honda Bosch Radarless safety mode with stock longitudinal
  """

  def setUp(self):
    super().setUp()
    self.safety.set_safety_hooks(CarParams.SafetyModel.hondaBosch, HondaSafetyFlags.RADARLESS)
    self.safety.init_tests()


class TestHondaBoschRadarlessAltBrakeSafety(HondaPcmEnableBase, TestHondaBoschRadarlessSafetyBase, TestHondaBoschAltBrakeSafetyBase):
  """
    Covers the Honda Bosch Radarless safety mode with stock longitudinal and an alternate brake message
  """

  def setUp(self):
    super().setUp()
    self.safety.set_safety_hooks(CarParams.SafetyModel.hondaBosch, HondaSafetyFlags.RADARLESS | HondaSafetyFlags.ALT_BRAKE)
    self.safety.init_tests()


class TestHondaBoschRadarlessLongSafety(common.LongitudinalAccelSafetyTest, HondaButtonEnableBase,
                                        TestHondaBoschRadarlessSafetyBase):
  """
    Covers the Honda Bosch Radarless safety mode with longitudinal control
  """
  TX_MSGS = [[0xE4, 0], [0x33D, 0], [0x1C8, 0], [0x30C, 0], [0x296, 2], [0x6CD5554, 0], [0xF31AA54, 0], [0x6CD5557, 0]]
  FWD_BLACKLISTED_ADDRS = {2: [0xE4, 0x33D, 0x1C8, 0x30C, 0x6CD5554, 0xF31AA54, 0x6CD5557]}
  RELAY_MALFUNCTION_ADDRS = {0: (0xE4, 0x1C8, 0x30C, 0x33D, 0x6CD5554, 0xF31AA54, 0x6CD5557)}

  def setUp(self):
    super().setUp()
    self.safety.set_safety_hooks(CarParams.SafetyModel.hondaBosch, HondaSafetyFlags.RADARLESS | HondaSafetyFlags.BOSCH_LONG)
    self.safety.init_tests()

  def _accel_msg(self, accel):
    values = {
      "ACCEL_COMMAND": accel,
    }
    return self.packer.make_can_msg_safety("ACC_CONTROL", self.PT_BUS, values)

  # Longitudinal doesn't need to send buttons
  def test_spam_cancel_safety_check(self):
    pass


class TestHondaBoschRadarlessLongNoEngineDataMsgSafety(TestHondaBoschRadarlessLongSafety):
  """
    Covers the Honda Bosch Radarless safety mode with longitudinal control and no engine_data message
  """

  def setUp(self):
    super().setUp()
    self.safety.set_safety_hooks(CarParams.SafetyModel.hondaBosch,
                                 HondaSafetyFlags.RADARLESS | HondaSafetyFlags.BOSCH_LONG | HondaSafetyFlags.NO_ENGINE_DATA_MSG)
    self.safety.init_tests()

  # ABS_SENSOR values increase with movement. Change in sum of units per message approximates units of XMISSION_SPEED.
  def _speed_msg(self, speed):
    self._abs_tick = getattr(self, '_abs_tick', 0) + speed
    values = {
      "ABS_SENSOR_FL": (self._abs_tick // 4) % 256,
      "ABS_SENSOR_FR": (self._abs_tick // 4) % 256,
      "ABS_SENSOR_RL": (self._abs_tick // 4) % 256,
      "ABS_SENSOR_RR": ((self._abs_tick // 4) + (self._abs_tick % 4)) % 256,
    }
    return self.packer.make_can_msg_safety("ABS_SENSOR", self.PT_BUS, values)


class TestHondaBoschCANFDSafetyBase(TestHondaBoschSafetyBase):
  """Base class for CANFD Honda Bosch"""
  PT_BUS = 0
  STEER_BUS = 0
  BUTTONS_BUS = 0

  TX_MSGS = [[0xE4, 0], [0x296, 0], [0x296, 2], [0x33D, 0]]
  FWD_BLACKLISTED_ADDRS = {2: [0xE4, 0x33D]}
  RELAY_MALFUNCTION_ADDRS = {0: (0xE4, 0x33D)}

  def setUp(self):
    self.packer = CANPackerSafety("honda_common_canfd_generated")
    self.safety = libsafety_py.libsafety

  def test_buttons_fwd(self):
    # SCM_BUTTONS (0x296) forwards to the camera unless OP's replacement button stream is flowing
    # (engaged + a recent OP SCM_BUTTONS tx on the camera bus); see the radarless variant of this test
    self.safety.set_controls_allowed(True)
    self.assertEqual(2, self.safety.safety_fwd_hook(0, 0x296))

    self.assertTrue(self._tx(self._button_msg(Btn.NONE, bus=2)))
    self.assertEqual(-1, self.safety.safety_fwd_hook(0, 0x296))

    self.safety.set_controls_allowed(False)
    self.assertEqual(2, self.safety.safety_fwd_hook(0, 0x296))

    self.safety.set_controls_allowed(True)
    for _ in range(10):
      self._rx(self._button_msg(Btn.NONE, main_on=True))
    self.assertEqual(2, self.safety.safety_fwd_hook(0, 0x296))

  def test_radar_diag_response_fwd(self):
    # the radar's UDS responses (0x18DAF1B0) never forward to the camera: the radar disable handshake
    # happens after the relay is open on CAN FD
    self.safety.set_controls_allowed(False)
    self.assertEqual(-1, self.safety.safety_fwd_hook(0, 0x18DAF1B0))
    self.safety.set_controls_allowed(True)
    self.assertEqual(-1, self.safety.safety_fwd_hook(0, 0x18DAF1B0))

  def test_buttons_tx_camera_bus(self):
    # Buttons to the camera (bus 2): cancel-only while disengaged, any button while engaged
    # (OP takes over SCM_BUTTONS towards the camera when engaged)
    self.safety.set_controls_allowed(0)
    self.assertTrue(self._tx(self._button_msg(Btn.CANCEL, bus=2)))
    self.assertFalse(self._tx(self._button_msg(Btn.RESUME, bus=2)))
    self.assertFalse(self._tx(self._button_msg(Btn.SET, bus=2)))
    self.safety.set_controls_allowed(1)
    self.assertTrue(self._tx(self._button_msg(Btn.NONE, bus=2)))
    self.assertTrue(self._tx(self._button_msg(Btn.RESUME, bus=2)))


class TestHondaBoschCANFDSafety(HondaPcmEnableBase, TestHondaBoschCANFDSafetyBase):
  """
    Covers the Honda Bosch CANFD safety mode with stock longitudinal
  """

  def setUp(self):
    super().setUp()
    self.safety.set_safety_hooks(CarParams.SafetyModel.hondaBosch, HondaSafetyFlags.BOSCH_CANFD)
    self.safety.init_tests()


class TestHondaBoschCANFDAltBrakeSafety(HondaPcmEnableBase, TestHondaBoschCANFDSafetyBase, TestHondaBoschAltBrakeSafetyBase):
  """
    Covers the Honda Bosch CANFD safety mode with stock longitudinal and an alternate brake message
  """

  def setUp(self):
    super().setUp()
    self.safety.set_safety_hooks(CarParams.SafetyModel.hondaBosch, HondaSafetyFlags.BOSCH_CANFD | HondaSafetyFlags.ALT_BRAKE)
    self.safety.init_tests()


class TestHondaBoschCANFDLongSafety(TestHondaBoschLongSafety, TestHondaBoschCANFDSafetyBase):
  """
    Covers the Honda Bosch CANFD safety mode with longitudinal control
  """

  PT_BUS = 0
  STEER_BUS = 0
  BUTTONS_BUS = 0

  TX_MSGS = [[0xE4, 0], [0x1DF, 0],  [0x1EF, 0], [0x30C, 0], [0x33D, 0], [0x39F, 0], [0x296, 2], [0x18DAB0F1, 0], [0x310, 0], [0x310, 2]]
  FWD_BLACKLISTED_ADDRS = {2: [0xE4, 0x1DF, 0x33D]}
  RELAY_MALFUNCTION_ADDRS = {0: (0xE4, 0x1DF, 0x33D)}  # STEERING_CONTROL / ACC_CONTROL / LKAS_HUD

  def setUp(self):
    super().setUp()
    self.safety.set_safety_hooks(CarParams.SafetyModel.hondaBosch, HondaSafetyFlags.BOSCH_CANFD | HondaSafetyFlags.BOSCH_LONG)
    self.safety.init_tests()

  def test_diagnostics(self):
    # CAN FD silences the radar from CarController after the relay opens, so exactly the extended
    # diagnostic session and the suppressed-response CommunicationControl disable are allowed too
    tester_present = libsafety_py.make_CANPacket(0x18DAB0F1, self.PT_BUS, b"\x02\x3E\x80\x00\x00\x00\x00\x00")
    self.assertTrue(self._tx(tester_present))
    ext_diag = libsafety_py.make_CANPacket(0x18DAB0F1, self.PT_BUS, b"\x02\x10\x03\x00\x00\x00\x00\x00")
    self.assertTrue(self._tx(ext_diag))
    comm_control_disable = libsafety_py.make_CANPacket(0x18DAB0F1, self.PT_BUS, b"\x03\x28\x83\x03\x00\x00\x00\x00")
    self.assertTrue(self._tx(comm_control_disable))

    # anything else stays blocked, including re-enabling the radar and non-zero trailing bytes
    comm_control_enable = libsafety_py.make_CANPacket(0x18DAB0F1, self.PT_BUS, b"\x03\x28\x80\x03\x00\x00\x00\x00")
    self.assertFalse(self._tx(comm_control_enable))
    not_tester_present = libsafety_py.make_CANPacket(0x18DAB0F1, self.PT_BUS, b"\x03\xAA\xAA\x00\x00\x00\x00\x00")
    self.assertFalse(self._tx(not_tester_present))
    trailing_bytes = libsafety_py.make_CANPacket(0x18DAB0F1, self.PT_BUS, b"\x02\x10\x03\x00\x00\x00\x00\x01")
    self.assertFalse(self._tx(trailing_bytes))


class TestHondaNidecHybridSafety(TestHondaNidecPcmSafety):
  """
    Covers the Honda Nidec safety mode with hybrid brake
  """

  BRAKE_SIG = "COMPUTER_BRAKE_HYBRID"

  def setUp(self):
    self.packer = CANPackerSafety("honda_clarity_hybrid_2018_can_generated")
    self.safety = libsafety_py.libsafety
    self.safety.set_current_safety_param_sp(HondaSafetyFlagsSP.NIDEC_HYBRID)
    self.safety.set_safety_hooks(CarParams.SafetyModel.hondaNidec, 0)
    self.safety.init_tests()


class TestClarityInterceptorBrakeGuard(unittest.TestCase):
  FLAGS = HondaSafetyFlagsSP.CLARITY_INTERCEPTOR_BRAKE | HondaSafetyFlagsSP.NIDEC_HYBRID | HondaSafetyFlagsSP.GAS_INTERCEPTOR

  def setUp(self):
    self.safety = libsafety_py.libsafety
    self.packer = CANPackerSafety("honda_clarity_hybrid_2018_can_generated")
    self.configure(self.FLAGS)

  def configure(self, sp_flags, flags=0):
    self.safety.set_current_safety_param_sp(sp_flags)
    self.safety.set_safety_hooks(CarParams.SafetyModel.hondaNidec, flags)
    self.safety.init_tests()
    self.safety.set_controls_allowed(True)

  def pedal(self, bus=0, length=6):
    self.safety.safety_rx_hook(libsafety_py.make_CANPacket(0x201, bus, bytes(length)))

  def packet(self, standard=0, hybrid=0, *, bus=0, aeb=False):
    return self.packer.make_can_msg_safety("BRAKE_COMMAND", bus, {"COMPUTER_BRAKE": standard, "COMPUTER_BRAKE_HYBRID": hybrid,
                                                                  "AEB_REQ_1": int(aeb)})

  def test_separate_fields_and_permissions(self):
    self.pedal()
    for allowed, gas in ((True, False), (True, True), (False, False)):
      self.safety.set_controls_allowed(allowed)
      self.safety.set_gas_pressed_prev(gas)
      for standard in (0, 1, 254, 255, 256, 320, 1023):
        for hybrid in (0, 1, 255, 256, 319, 320, 321, 1023):
          expected = standard <= 255 and hybrid <= 320 if allowed and not gas else standard == hybrid == 0
          with self.subTest(allowed=allowed, gas=gas, standard=standard, hybrid=hybrid):
            self.assertEqual(self.safety.safety_tx_hook(self.packet(standard, hybrid)), expected)

  def test_requires_qualified_pedal_rx_after_every_init(self):
    for _ in range(2):
      self.configure(self.FLAGS)
      self.pedal(bus=2)
      self.pedal(length=8)
      self.assertFalse(self.safety.safety_tx_hook(self.packet(hybrid=256)))
      self.assertTrue(self.safety.safety_tx_hook(self.packet(hybrid=255)))
      self.pedal()
      self.assertTrue(self.safety.safety_tx_hook(self.packet(hybrid=320)))

  def test_invalid_configurations(self):
    for sp, param in ((self.FLAGS & ~HondaSafetyFlagsSP.GAS_INTERCEPTOR, 0),
                      (self.FLAGS & ~HondaSafetyFlagsSP.NIDEC_HYBRID, 0),
                      (HondaSafetyFlagsSP.CLARITY_INTERCEPTOR_BRAKE, 0),
                      (self.FLAGS | HondaSafetyFlagsSP.GAS_INTERCEPTOR_THRESHOLD_512, 0),
                      (self.FLAGS | HondaSafetyFlagsSP.STOCK_LONGITUDINAL, 0),
                      (self.FLAGS, HondaSafetyFlags.NIDEC_ALT), (self.FLAGS, HondaSafetyFlags.RLX_STEER_BRIDGE)):
      with self.subTest(sp=sp, param=param):
        self.configure(sp, param)
        self.pedal()
        self.assertFalse(self.safety.safety_tx_hook(self.packet(0, 256)))
        self.assertFalse(self.safety.safety_tx_hook(self.packet(256, 0)))
    # Other hybrid Hondas with a pedal retain the existing hybrid limit.
    self.configure(self.FLAGS & ~HondaSafetyFlagsSP.CLARITY_INTERCEPTOR_BRAKE)
    self.pedal()
    self.assertTrue(self.safety.safety_tx_hook(self.packet(hybrid=255)))
    self.assertFalse(self.safety.safety_tx_hook(self.packet(hybrid=256)))

  def test_stock_aeb_compares_last_transmitted_hybrid_brake(self):
    self.pedal()
    self.assertTrue(self.safety.safety_tx_hook(self.packet(10, 319)))
    self.assertFalse(self.safety.safety_tx_hook(self.packet(256, 700)))
    for stock, forward in ((318, False), (319, True), (200, True)):
      self.assertTrue(self.safety.safety_rx_hook(self.packet(0, stock, bus=2, aeb=True)))
      self.assertEqual(self.safety.get_honda_fwd_brake(), forward)
      if forward:
        self.assertFalse(self.safety.safety_tx_hook(self.packet()))
        self.assertFalse(self.safety.safety_tx_hook(self.packet(0, 320)))
    self.assertTrue(self.safety.safety_rx_hook(self.packet(bus=2)))
    self.assertFalse(self.safety.get_honda_fwd_brake())
    self.assertTrue(self.safety.safety_tx_hook(self.packet(0, 320)))

  def test_stock_aeb_rx_forward_and_host_tx_sequence(self):
    def check_camera(camera, brake, aeb, destination):
      msg = camera.make_can_msg_safety("BRAKE_COMMAND", 2, {"COMPUTER_BRAKE_HYBRID": brake, "AEB_REQ_1": int(aeb)})
      self.assertTrue(self.safety.safety_rx_hook(msg))
      self.assertEqual(self.safety.safety_fwd_hook(2, msg.addr), destination)

    for disable_stock_aeb in (False, True):
      for takeover_brake in (200, 201):
        with self.subTest(disable_stock_aeb=disable_stock_aeb, takeover_brake=takeover_brake):
          self.configure(self.FLAGS)
          self.safety.set_alternative_experience(ALTERNATIVE_EXPERIENCE.DISABLE_STOCK_AEB if disable_stock_aeb else 0)
          self.pedal()
          # Independent camera counter: host brake transmissions must not advance it.
          camera = CANPackerSafety("honda_clarity_hybrid_2018_can_generated")

          self.assertTrue(self.safety.safety_tx_hook(self.packet(hybrid=200)))
          check_camera(camera, 80, True, -1)  # Valid RX, but weaker than the host: do not forward to bus 0.
          for tick in (1, 2, 3):
            self.safety.set_timer(tick * 20_000)
            self.assertTrue(self.safety.safety_tx_hook(self.packet(hybrid=200)))  # No intervening camera RX.

          destination = -1 if disable_stock_aeb else 0
          check_camera(camera, takeover_brake, True, destination)
          self.assertEqual(self.safety.safety_tx_hook(self.packet(hybrid=200)), disable_stock_aeb)
          check_camera(camera, 80, True, destination)  # Once forwarded, the camera keeps priority through weaker requests.
          self.assertEqual(self.safety.safety_tx_hook(self.packet(hybrid=200)), disable_stock_aeb)
          check_camera(camera, 0, False, -1)
          self.assertTrue(self.safety.safety_tx_hook(self.packet(hybrid=200)))


if __name__ == "__main__":
  unittest.main()
