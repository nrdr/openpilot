from hypothesis import settings, given, strategies as st
from types import SimpleNamespace

import pytest

from opendbc.can import CANPacker, CANParser
from opendbc.car import Bus, ButtonType, gen_empty_fingerprint, structs
from opendbc.car.structs import CarControl, CarParams
from opendbc.car.fw_versions import build_fw_dict, match_fw_to_car
from opendbc.car.hyundai.carcontroller import CarController, Ioniq6LongitudinalTuningState, GenesisG90LongitudinalTuningState, \
                                              IONIQ_6_IPEDAL_PADDLE_BURST_COUNT, update_ioniq_6_longitudinal_tuning, \
                                              update_genesis_g90_longitudinal_tuning
from opendbc.car.hyundai.carstate import CarState, decode_ioniq_6_blindspot_radar_state, decode_ioniq_6_ipedal_intermediate_state, \
                                        decode_ioniq_6_ipedal_state, decode_ioniq_6_max_regen_state
from opendbc.car.hyundai.interface import CarInterface
from opendbc.car.hyundai import hyundaican, hyundaicanfd
from opendbc.car.hyundai.hyundaicanfd import CanBus
from opendbc.car.hyundai.radar_interface import RADAR_START_ADDR
from opendbc.car.hyundai.values import CAMERA_SCC_CAR, CANFD_CAR, CAN_GEARS, CAR, CHECKSUM, DATE_FW_ECUS, \
                                         HYBRID_CAR, EV_CAR, FW_QUERY_CONFIG, LEGACY_SAFETY_MODE_CAR, CANFD_FUZZY_WHITELIST, \
                                         UNSUPPORTED_LONGITUDINAL_CAR, PLATFORM_CODE_ECUS, HYUNDAI_VERSION_REQUEST_LONG, \
                                         CarControllerParams, DBC, HyundaiFlags, get_platform_codes, HyundaiSafetyFlags, Buttons

LongCtrlState = CarControl.Actuators.LongControlState
from opendbc.car.hyundai.fingerprints import FW_VERSIONS

Ecu = CarParams.Ecu

# Some platforms have date codes in a different format we don't yet parse (or are missing).
# For now, assert list of expected missing date cars
NO_DATES_PLATFORMS = {
  # CAN FD
  CAR.KIA_SPORTAGE_5TH_GEN,
  CAR.KIA_SPORTAGE_HEV_2026,
  CAR.HYUNDAI_SANTA_CRUZ_1ST_GEN,
  CAR.HYUNDAI_TUCSON_4TH_GEN,
  # CAN
  CAR.HYUNDAI_ELANTRA,
  CAR.HYUNDAI_ELANTRA_GT_I30,
  CAR.KIA_CEED,
  CAR.KIA_FORTE,
  CAR.KIA_OPTIMA_G4,
  CAR.KIA_OPTIMA_G4_FL,
  CAR.KIA_SORENTO,
  CAR.HYUNDAI_KONA,
  CAR.HYUNDAI_KONA_EV,
  CAR.HYUNDAI_KONA_EV_2022,
  CAR.HYUNDAI_KONA_HEV,
  CAR.HYUNDAI_SONATA_LF,
  CAR.HYUNDAI_VELOSTER,
  CAR.HYUNDAI_KONA_2022,
}

CANFD_EXPECTED_ECUS = {Ecu.fwdCamera, Ecu.fwdRadar}


def get_test_toggles() -> SimpleNamespace:
  return SimpleNamespace(always_ipedal=False, always_on_lateral_lkas=False, force_torque_controller=False, nnff=False, nnff_lite=False)


class TestHyundaiFingerprint:
  def test_feature_detection(self):
    # LKA steering
    for lka_steering in (True, False):
      fingerprint = gen_empty_fingerprint()
      if lka_steering:
        cam_can = CanBus(None, fingerprint).CAM
        fingerprint[cam_can] = [0x50, 0x110]  # LKA steering messages
      CP = CarInterface.get_params(CAR.KIA_EV6, fingerprint, [], False, False, False, None)
      assert bool(CP.flags & HyundaiFlags.CANFD_LKA_STEERING) == lka_steering

    # radar available
    for radar in (True, False):
      fingerprint = gen_empty_fingerprint()
      if radar:
        fingerprint[1][RADAR_START_ADDR] = 8
      CP = CarInterface.get_params(CAR.HYUNDAI_SONATA, fingerprint, [], False, False, False, None)
      assert CP.radarUnavailable != radar

    forte_no_scc = CarInterface.get_params(CAR.KIA_FORTE, gen_empty_fingerprint(), [], True, False, False, None)
    assert bool(forte_no_scc.flags & HyundaiFlags.NON_SCC)
    assert not forte_no_scc.alphaLongitudinalAvailable
    assert forte_no_scc.pcmCruise

    forte_with_scc = gen_empty_fingerprint()
    forte_with_scc[0][0x420] = 8
    forte_with_scc[0][0x421] = 8
    CP = CarInterface.get_params(CAR.KIA_FORTE, forte_with_scc, [], True, False, False, None)
    assert not bool(CP.flags & HyundaiFlags.NON_SCC)
    assert CP.alphaLongitudinalAvailable

    CP = CarInterface.get_params(CAR.KIA_SPORTAGE_HEV_2026, gen_empty_fingerprint(), [], False, False, False, None)
    assert CP.steerControlType == CarParams.SteerControlType.angle
    assert CP.safetyConfigs[-1].safetyParam & HyundaiSafetyFlags.CANFD_ANGLE_STEERING

    fingerprint = gen_empty_fingerprint()
    cam_can = CanBus(None, fingerprint).CAM
    fingerprint[cam_can][0xCB] = 24
    CP = CarInterface.get_params(CAR.KIA_SPORTAGE_HEV_2026, fingerprint, [], False, False, False, None)
    assert CP.flags & HyundaiFlags.SEND_LFA

    palisade_2023 = CarInterface.get_params(CAR.HYUNDAI_PALISADE_2023, gen_empty_fingerprint(), [], True, False, False, None)
    assert palisade_2023.flags & HyundaiFlags.CAN_CANFD_BLENDED
    assert DBC[palisade_2023.carFingerprint][Bus.pt] == "hyundai_palisade_2023_generated"
    assert palisade_2023.safetyConfigs[-1].safetyParam & HyundaiSafetyFlags.CAN_CANFD_BLENDED
    assert palisade_2023.safetyConfigs[-1].safetyParam & HyundaiSafetyFlags.CANCEL_BTN_ENABLE

  def test_palisade_2023_pause_resume_button_maps_to_enable(self):
    toggles = get_test_toggles()
    CP = CarInterface.get_params(CAR.HYUNDAI_PALISADE_2023, gen_empty_fingerprint(), [], True, False, False, toggles)
    FPCP = CarInterface.get_starpilot_params(CAR.HYUNDAI_PALISADE_2023, gen_empty_fingerprint(), [], CP, toggles)
    car_state = CarState(CP, FPCP)

    car_state.out.cruiseState.enabled = False
    events = car_state.create_cruise_button_events(Buttons.CANCEL, Buttons.NONE)
    assert [(be.type, be.pressed) for be in events] == [(ButtonType.accelCruise, True)]

    events = car_state.create_cruise_button_events(Buttons.NONE, Buttons.CANCEL)
    assert [(be.type, be.pressed) for be in events] == [(ButtonType.accelCruise, False)]

    car_state.out.cruiseState.enabled = True
    events = car_state.create_cruise_button_events(Buttons.CANCEL, Buttons.NONE)
    assert [(be.type, be.pressed) for be in events] == [(ButtonType.cancel, True)]

  def test_palisade_2023_cancel_release_enables_from_standby(self):
    toggles = get_test_toggles()
    CP = CarInterface.get_params(CAR.HYUNDAI_PALISADE_2023, gen_empty_fingerprint(), [], True, False, False, toggles)
    FPCP = CarInterface.get_starpilot_params(CAR.HYUNDAI_PALISADE_2023, gen_empty_fingerprint(), [], CP, toggles)
    car_state = CarState(CP, FPCP)

    car_state.out.cruiseState.enabled = False
    assert not car_state.update_button_enable([structs.CarState.ButtonEvent(pressed=True, type=ButtonType.cancel)])
    assert car_state.update_button_enable([structs.CarState.ButtonEvent(pressed=False, type=ButtonType.cancel)])

    car_state.out.cruiseState.enabled = True
    assert not car_state.update_button_enable([structs.CarState.ButtonEvent(pressed=False, type=ButtonType.cancel)])

  def test_palisade_2023_disable_failure_falls_back_to_stock_acc(self, monkeypatch):
    toggles = get_test_toggles()
    CP = CarInterface.get_params(CAR.HYUNDAI_PALISADE_2023, gen_empty_fingerprint(), [], True, False, False, toggles)

    called = {}

    def fake_disable_ecu(*args, **kwargs):
      called.update(kwargs)
      return False

    monkeypatch.setattr("opendbc.car.hyundai.interface.disable_ecu", fake_disable_ecu)
    CarInterface.init(CP, None, None)

    assert called["reset"] is True
    assert not CP.openpilotLongitudinalControl
    assert CP.pcmCruise
    assert not (CP.safetyConfigs[-1].safetyParam & HyundaiSafetyFlags.LONG)

  def test_canfd_longitudinal_params_match_family_tune(self):
    toggles = get_test_toggles()
    CP = CarInterface.get_params(CAR.KIA_EV6, gen_empty_fingerprint(), [], True, False, False, toggles)

    assert CP.vEgoStopping == pytest.approx(0.3)
    assert CP.vEgoStarting == pytest.approx(0.1)
    assert CP.stoppingDecelRate == pytest.approx(0.4)
    assert CP.longitudinalActuatorDelay == pytest.approx(0.5)
    assert CP.startingState

  def test_genesis_g90_longitudinal_params_bias_toward_earlier_stop_handoff(self):
    toggles = get_test_toggles()
    CP = CarInterface.get_params(CAR.GENESIS_G90, gen_empty_fingerprint(), [], True, False, False, toggles)

    assert CP.vEgoStopping == pytest.approx(0.8)
    assert CP.stoppingDecelRate == pytest.approx(0.55)

  def test_kia_forte_no_scc_fw_match(self):
    car_fw = [
      CarParams.CarFw(
        ecu=Ecu.eps,
        fwVersion=b'\xf1\x00BD  MDPS C 1.00 1.07 56310/M6300 4BDDC107',
        address=0x7d4,
        subAddress=0,
        brand="hyundai",
      ),
      CarParams.CarFw(
        ecu=Ecu.fwdCamera,
        fwVersion=b'\xf1\x00BD  LKAS AT USA LHD 1.00 1.02 95740-M6000 J31',
        address=0x7c4,
        subAddress=0,
        brand="hyundai",
      ),
    ]

    exact, matches = match_fw_to_car(car_fw, "3KPF34AD2LE154148", allow_exact=True, allow_fuzzy=False, log=False)
    assert exact
    assert matches == {CAR.KIA_FORTE}

  def test_kia_forte_no_scc_fca_does_not_require_scc12(self):
    toggles = get_test_toggles()
    fingerprint = gen_empty_fingerprint()
    fingerprint[0][0x38D] = 8

    CP = CarInterface.get_params(CAR.KIA_FORTE, fingerprint, [], True, False, False, toggles)
    FPCP = CarInterface.get_starpilot_params(CAR.KIA_FORTE, fingerprint, [], CP, toggles)

    car_state = CarState(CP, FPCP)
    can_parsers = car_state.get_can_parsers(CP)
    packer = CANPacker(DBC[CP.carFingerprint][Bus.pt])
    fca11_addr = packer.dbc.name_to_msg["FCA11"].address

    assert can_parsers[Bus.pt].message_states[fca11_addr].ignore_alive

    car_state.update(can_parsers, toggles)
    pt_states = {state.name for state in can_parsers[Bus.pt].message_states.values()}
    assert "FCA11" in pt_states
    assert "SCC12" not in pt_states

    for frame in range(1, 6):
      t = frame * 100_000_000
      for parser in can_parsers.values():
        required_msgs = []
        for state in parser.message_states.values():
          if state.ignore_alive:
            continue
          values = {}
          if state.name == "LVR12":
            values["CF_Lvr_CruiseSet"] = 30
          required_msgs.append(packer.make_can_msg(state.name, parser.bus, values))
        parser.update([(t, required_msgs)])

    assert all(parser.can_valid for parser in can_parsers.values())

    ret, _ = car_state.update(can_parsers, toggles)
    assert ret.cruiseState.enabled
    assert ret.cruiseState.speed > 0

  def test_alternate_limits(self):
    # Alternate lateral control limits, for high torque cars, verify Panda safety mode flag is set
    fingerprint = gen_empty_fingerprint()
    for car_model in CAR:
      CP = CarInterface.get_params(car_model, fingerprint, [], False, False, False, None)
      assert bool(CP.flags & HyundaiFlags.ALT_LIMITS) == bool(CP.safetyConfigs[-1].safetyParam & HyundaiSafetyFlags.ALT_LIMITS)

  def test_can_features(self):
    # Test no EV/HEV in any gear lists (should all use ELECT_GEAR)
    assert set.union(*CAN_GEARS.values()) & (HYBRID_CAR | EV_CAR) == set()

    # Test CAN FD car not in CAN feature lists
    can_specific_feature_list = set.union(*CAN_GEARS.values(), *CHECKSUM.values(), LEGACY_SAFETY_MODE_CAR, UNSUPPORTED_LONGITUDINAL_CAR, CAMERA_SCC_CAR)
    for car_model in CANFD_CAR:
      assert car_model not in can_specific_feature_list, "CAN FD car unexpectedly found in a CAN feature list"

  def test_hybrid_ev_sets(self):
    assert HYBRID_CAR & EV_CAR == set(), "Shared cars between hybrid and EV"
    assert CANFD_CAR & HYBRID_CAR == set(), "Hard coding CAN FD cars as hybrid is no longer supported"

  def test_canfd_ecu_whitelist(self):
    # Asserts only expected Ecus can exist in database for CAN-FD cars
    for car_model in CANFD_CAR:
      ecus = {fw[0] for fw in FW_VERSIONS[car_model].keys()}
      ecus_not_in_whitelist = ecus - CANFD_EXPECTED_ECUS
      ecu_strings = ", ".join([f"Ecu.{ecu}" for ecu in ecus_not_in_whitelist])
      assert len(ecus_not_in_whitelist) == 0, \
                       f"{car_model}: Car model has unexpected ECUs: {ecu_strings}"

  def test_canfd_blinker_signal_selection(self):
    assert CarState.get_canfd_blinker_sig_names(CAR.KIA_SPORTAGE_HEV_2026, True) == ("LEFT_LAMP_ALT", "RIGHT_LAMP_ALT")
    assert CarState.get_canfd_blinker_sig_names(CAR.HYUNDAI_KONA_EV_2ND_GEN, False) == ("LEFT_LAMP_ALT", "RIGHT_LAMP_ALT")
    assert CarState.get_canfd_blinker_sig_names(CAR.KIA_EV6, False) == ("LEFT_LAMP", "RIGHT_LAMP")

  @pytest.mark.parametrize("alpha_long", [False, True])
  def test_ioniq_6_left_paddle_button_event(self, alpha_long):
    toggles = get_test_toggles()
    fingerprint = gen_empty_fingerprint()
    CP = CarInterface.get_params(CAR.HYUNDAI_IONIQ_6, fingerprint, [], alpha_long, False, False, toggles)
    FPCP = CarInterface.get_starpilot_params(CAR.HYUNDAI_IONIQ_6, fingerprint, [], CP, toggles)

    car_state = CarState(CP, FPCP)
    can_parsers = car_state.get_can_parsers(CP)
    packer = CANPacker(DBC[CP.carFingerprint][Bus.pt])
    can_bus = CanBus(CP).ECAN

    def update(left_paddle: int, frame: int):
      msg = packer.make_can_msg("CRUISE_BUTTONS", can_bus, {
        "SET_ME_1": 1,
        "CRUISE_BUTTONS": 0,
        "ADAPTIVE_CRUISE_MAIN_BTN": 0,
        "LDA_BTN": 0,
        "LEFT_PADDLE": left_paddle,
        "RIGHT_PADDLE": 0,
      })
      can_parsers[Bus.pt].update([(frame, [msg])])
      return car_state.update(can_parsers, toggles)[0]

    update(0, 1)
    ret = update(1, 2)
    assert any(be.type == ButtonType.altButton2 and be.pressed for be in ret.buttonEvents)

    ret = update(0, 3)
    assert any(be.type == ButtonType.altButton2 and not be.pressed for be in ret.buttonEvents)

  def test_ioniq_6_ipedal_state_decode(self):
    assert decode_ioniq_6_max_regen_state(0x3C, 0x01)
    assert not decode_ioniq_6_ipedal_state(0x3C, 0x01)
    assert not decode_ioniq_6_ipedal_state(0x50, 0x01)
    assert decode_ioniq_6_ipedal_intermediate_state(0x50, 0x01)
    assert decode_ioniq_6_ipedal_state(0x50, 0x03)

  def test_ioniq_6_msla_regen_signals_decode(self):
    CP = CarParams.new_message()
    CP.carFingerprint = CAR.HYUNDAI_IONIQ_6
    CP.flags = int(HyundaiFlags.CANFD | HyundaiFlags.CANFD_LKA_STEERING)

    packer = CANPacker(DBC[CP.carFingerprint][Bus.pt])
    can_bus = CanBus(CP)
    parser = CANParser(DBC[CP.carFingerprint][Bus.pt], [("MANUAL_SPEED_LIMIT_ASSIST", 0)], can_bus.ECAN)

    msg = packer.make_can_msg("MANUAL_SPEED_LIMIT_ASSIST", can_bus.ECAN, {
      "MSLA_STATUS": 0,
      "MSLA_ENABLED": 0,
      "MAX_SPEED": 0,
      "MAX_SPEED_COPY": 0,
      "EV_REGEN_STATE": 0x50,
      "EV_REGEN_STATE_2": 0x03,
    })
    parser.update([(1, [msg])])

    assert parser.can_valid
    assert parser.vl["MANUAL_SPEED_LIMIT_ASSIST"]["EV_REGEN_STATE"] == 0x50
    assert parser.vl["MANUAL_SPEED_LIMIT_ASSIST"]["EV_REGEN_STATE_2"] == 0x03

  @pytest.mark.parametrize(("counter", "expected_hex"), [
    (0, "2100002800000000"),
    (7, "2970002800000000"),
    (14, "31e0002800000000"),
  ])
  def test_ioniq_6_left_paddle_message_matches_stock(self, counter, expected_hex):
    CP = CarParams.new_message()
    CP.carFingerprint = CAR.HYUNDAI_IONIQ_6
    CP.flags = int(HyundaiFlags.CANFD | HyundaiFlags.CANFD_LKA_STEERING)

    msg = hyundaicanfd.create_ioniq_6_paddle_buttons(CANPacker(DBC[CP.carFingerprint][Bus.pt]), CP, CanBus(CP),
                                                     counter, left_paddle=True)
    assert msg[1].hex() == expected_hex

  def test_ioniq_6_buttons_counter_wraps_like_stock(self):
    assert hyundaicanfd.get_ioniq_6_cruise_buttons_next_counter(13) == 14
    assert hyundaicanfd.get_ioniq_6_cruise_buttons_next_counter(14) == 0

  @pytest.mark.parametrize(("stock_hex", "expected_tail"), [
    ("45421440801f000000000000a865170000a000000080c071a80c120e00000000", bytes.fromhex("c00c1200")),
    ("47745840801f0000000005006e5e0e0000a000000080c071a80e070e00000000", bytes.fromhex("850e070c")),
    ("7aea8140801f000000000000b965140000a000000080c0711810070200000000", bytes.fromhex("b5100700")),
    ("32438340801f000000000000b965140000a000000080c071a810070e00000000", bytes.fromhex("b5100700")),
  ])
  def test_ioniq_6_regen_control_message_preserves_stock_frame_and_flips_only_ipedal_request_bytes(self, stock_hex, expected_tail):
    CP = CarParams.new_message()
    CP.carFingerprint = CAR.HYUNDAI_IONIQ_6
    CP.flags = int(HyundaiFlags.CANFD | HyundaiFlags.CANFD_LKA_STEERING)

    packer = CANPacker(DBC[CP.carFingerprint][Bus.pt])
    can_bus = CanBus(CP)
    parser = CANParser(DBC[CP.carFingerprint][Bus.pt], [("IONIQ_6_REGEN_CONTROL", 0)], can_bus.ECAN)
    stock_dat = bytes.fromhex(stock_hex)
    parser.update([(1, [(0x25A, stock_dat, can_bus.ECAN)])])

    msg = hyundaicanfd.create_ioniq_6_regen_control(packer, CP, can_bus, parser.vl["IONIQ_6_REGEN_CONTROL"])
    assert msg[1][2:24] == stock_dat[2:24]
    assert msg[1][24:28] == expected_tail
    assert msg[1][28:] == stock_dat[28:]
    checksum = hyundaicanfd.hkg_can_fd_checksum(msg[0], None, bytearray(msg[1]))
    assert msg[1][0] | (msg[1][1] << 8) == checksum

  def test_ioniq_6_always_ipedal_spoofs_left_paddle_in_startup_park_and_drive_until_latched(self):
    toggles = get_test_toggles()
    toggles.always_ipedal = True
    CP = CarInterface.get_params(CAR.HYUNDAI_IONIQ_6, gen_empty_fingerprint(), [], True, False, False, toggles)

    controller = CarController(DBC[CP.carFingerprint], CP)
    can_bus = CanBus(CP)
    parser_bus = can_bus.ECAN if CP.flags & HyundaiFlags.CANFD_LKA_STEERING else can_bus.CAM
    parser = CANParser(DBC[CP.carFingerprint][Bus.pt], [("CRUISE_BUTTONS", 0)], parser_bus)

    cs = SimpleNamespace(
      out=SimpleNamespace(gearShifter=structs.CarState.GearShifter.park),
      ipedal_active=False,
      buttons_counter=5,
      cruise_buttons_msg={
        "_CHECKSUM": 0,
        "COUNTER": 5,
        "CRUISE_BUTTONS": 0,
        "ADAPTIVE_CRUISE_MAIN_BTN": 0,
        "NORMAL_CRUISE_MAIN_BTN": 0,
        "LDA_BTN": 0,
        "RIGHT_PADDLE": 0,
        "LEFT_PADDLE": 0,
        "SET_ME_1": 1,
      },
      ioniq_6_regen_control_msg={},
      ioniq_6_regen_control_ts=0,
    )
    cc = SimpleNamespace(enabled=False)

    sends = controller._update_ioniq_6_always_ipedal(cc, cs, toggles)
    parser.update([(1, sends)])

    assert sends
    assert len([msg for msg in sends if msg[0] == 0x1CF]) == IONIQ_6_IPEDAL_PADDLE_BURST_COUNT
    assert sends[0][1].hex() == "4650002800000000"
    assert parser.vl["CRUISE_BUTTONS"]["LEFT_PADDLE"] == 1
    assert parser.vl["CRUISE_BUTTONS"]["COUNTER"] == 5
    assert controller._ioniq_6_always_ipedal_pending
    assert not controller._ioniq_6_always_ipedal_startup_park_done

    controller.frame = 1
    sends = controller._update_ioniq_6_always_ipedal(cc, cs, toggles)

    assert sends == []

    controller.frame = 2
    cs.out.gearShifter = structs.CarState.GearShifter.drive
    cs.buttons_counter = 6
    sends = controller._update_ioniq_6_always_ipedal(cc, cs, toggles)

    assert sends
    assert len([msg for msg in sends if msg[0] == 0x1CF]) == IONIQ_6_IPEDAL_PADDLE_BURST_COUNT
    assert sends[0][1].hex() == "9060002800000000"
    assert controller._ioniq_6_always_ipedal_pending
    assert controller._ioniq_6_always_ipedal_startup_park_done

    controller.frame = 4
    cs.ipedal_active = True
    sends = controller._update_ioniq_6_always_ipedal(cc, cs, toggles)

    assert sends == []
    assert not controller._ioniq_6_always_ipedal_pending
    assert controller._ioniq_6_always_ipedal_press_remaining == 0

  def test_ioniq_6_always_ipedal_uses_stronger_followup_pull_for_intermediate_latch_state(self):
    toggles = get_test_toggles()
    toggles.always_ipedal = True
    CP = CarInterface.get_params(CAR.HYUNDAI_IONIQ_6, gen_empty_fingerprint(), [], True, False, False, toggles)

    controller = CarController(DBC[CP.carFingerprint], CP)
    cs = SimpleNamespace(
      out=SimpleNamespace(gearShifter=structs.CarState.GearShifter.drive),
      ipedal_active=False,
      ipedal_regen_state=0x50,
      ipedal_regen_state_2=0x01,
      buttons_counter=5,
      cruise_buttons_msg={
        "_CHECKSUM": 0,
        "COUNTER": 5,
        "CRUISE_BUTTONS": 0,
        "ADAPTIVE_CRUISE_MAIN_BTN": 0,
        "NORMAL_CRUISE_MAIN_BTN": 0,
        "LDA_BTN": 0,
        "RIGHT_PADDLE": 0,
        "LEFT_PADDLE": 0,
        "SET_ME_1": 1,
      },
      ioniq_6_regen_control_msg={},
      ioniq_6_regen_control_ts=0,
    )
    cc = SimpleNamespace(enabled=False)

    controller._ioniq_6_last_gear = structs.CarState.GearShifter.reverse
    sends = controller._update_ioniq_6_always_ipedal(cc, cs, toggles)

    assert sends
    assert controller._ioniq_6_always_ipedal_press_remaining == 9

  def test_ioniq_6_always_ipedal_sends_regen_control_companion_once_max_regen_is_shown(self):
    toggles = get_test_toggles()
    toggles.always_ipedal = True
    CP = CarInterface.get_params(CAR.HYUNDAI_IONIQ_6, gen_empty_fingerprint(), [], True, False, False, toggles)

    controller = CarController(DBC[CP.carFingerprint], CP)
    cs = SimpleNamespace(
      out=SimpleNamespace(gearShifter=structs.CarState.GearShifter.drive),
      ipedal_active=False,
      ipedal_regen_state=0x3C,
      ipedal_regen_state_2=0x01,
      buttons_counter=5,
      cruise_buttons_msg={
        "_CHECKSUM": 0,
        "COUNTER": 5,
        "CRUISE_BUTTONS": 0,
        "ADAPTIVE_CRUISE_MAIN_BTN": 0,
        "NORMAL_CRUISE_MAIN_BTN": 0,
        "LDA_BTN": 0,
        "RIGHT_PADDLE": 0,
        "LEFT_PADDLE": 0,
        "SET_ME_1": 1,
      },
      ioniq_6_regen_control_msg={
        "COUNTER": 0x14,
        "BYTE3": 0x40,
        "BYTE4": 0x80,
        "BYTE5": 0x1F,
        "BYTE6": 0x00,
        "BYTE7": 0x00,
        "BYTE8": 0x00,
        "BYTE9": 0x00,
        "BYTE10": 0x00,
        "BYTE11": 0x00,
        "BYTE12": 0xA8,
        "BYTE13": 0x65,
        "BYTE14": 0x17,
        "BYTE15": 0x00,
        "BYTE16": 0x00,
        "BYTE17": 0xA0,
        "BYTE18": 0x00,
        "BYTE19": 0x00,
        "BYTE20": 0x00,
        "BYTE21": 0x80,
        "BYTE22": 0xC0,
        "BYTE23": 0x71,
        "BYTE24": 0xA8,
        "BYTE25": 0x0C,
        "BYTE26": 0x12,
        "BYTE27": 0x0E,
        "BYTE28": 0x00,
        "BYTE29": 0x00,
        "BYTE30": 0x00,
        "BYTE31": 0x00,
      },
      ioniq_6_regen_control_ts=1,
    )
    cc = SimpleNamespace(enabled=False)

    controller._ioniq_6_last_gear = structs.CarState.GearShifter.reverse
    controller._ioniq_6_last_regen_control_counter = 0x13
    sends = controller._update_ioniq_6_always_ipedal(cc, cs, toggles)

    assert len([msg for msg in sends if msg[0] == 0x1CF]) == IONIQ_6_IPEDAL_PADDLE_BURST_COUNT
    regen_cmd = next(msg for msg in sends if msg[0] == 0x25A)
    assert regen_cmd[1][24:28] == bytes.fromhex("c00c1200")
    checksum = hyundaicanfd.hkg_can_fd_checksum(regen_cmd[0], None, bytearray(regen_cmd[1]))
    assert regen_cmd[1][0] | (regen_cmd[1][1] << 8) == checksum

    controller.frame = 1
    cs.buttons_counter = 6
    cs.ioniq_6_regen_control_msg = dict(cs.ioniq_6_regen_control_msg, COUNTER=0x15)
    sends = controller._update_ioniq_6_always_ipedal(cc, cs, toggles)

    assert len([msg for msg in sends if msg[0] == 0x1CF]) == IONIQ_6_IPEDAL_PADDLE_BURST_COUNT
    assert not any(msg[0] == 0x25A for msg in sends)

  def test_ioniq_6_longitudinal_params_match_canfd_tune(self):
    toggles = get_test_toggles()
    CP = CarInterface.get_params(CAR.HYUNDAI_IONIQ_6, gen_empty_fingerprint(), [], True, False, False, toggles)

    assert CP.vEgoStopping == pytest.approx(0.3)
    assert CP.vEgoStarting == pytest.approx(0.1)
    assert CP.stoppingDecelRate == pytest.approx(0.4)
    assert CP.longitudinalActuatorDelay == pytest.approx(0.5)
    assert CP.startingState

  def test_ioniq_6_longitudinal_tuning_helper_matches_dynamic_profile(self):
    state = Ioniq6LongitudinalTuningState()

    state = update_ioniq_6_longitudinal_tuning(state, accel_cmd=1.5, v_ego=10.0, a_ego=0.0,
                                               long_control_state=LongCtrlState.pid, long_active=True)
    assert state.desired_accel == pytest.approx(1.5)
    assert state.jerk_upper == pytest.approx(3.2)
    assert state.jerk_lower == pytest.approx(0.6)
    assert state.actual_accel == pytest.approx(0.16)

    state = update_ioniq_6_longitudinal_tuning(state, accel_cmd=1.0, v_ego=10.0, a_ego=0.0,
                                               long_control_state=LongCtrlState.stopping, long_active=True)
    assert not state.stopping
    assert state.desired_accel == pytest.approx(1.0)

    for _ in range(25):
      state = update_ioniq_6_longitudinal_tuning(state, accel_cmd=1.0, v_ego=10.0, a_ego=0.0,
                                                 long_control_state=LongCtrlState.stopping, long_active=True)
    assert state.stopping
    assert state.desired_accel == pytest.approx(0.0)
    actual_accel_after_stop = state.actual_accel

    state = update_ioniq_6_longitudinal_tuning(state, accel_cmd=1.0, v_ego=10.0, a_ego=0.0,
                                               long_control_state=LongCtrlState.stopping, long_active=True)
    assert state.actual_accel < actual_accel_after_stop

    state = update_ioniq_6_longitudinal_tuning(state, accel_cmd=1.0, v_ego=10.0, a_ego=0.0,
                                               long_control_state=LongCtrlState.pid, long_active=False)
    assert state.desired_accel == pytest.approx(0.0)
    assert state.actual_accel == pytest.approx(0.0)
    assert state.jerk_upper == pytest.approx(0.0)
    assert state.jerk_lower == pytest.approx(0.0)

  def test_ioniq_6_longitudinal_tuning_helper_holds_launch_through_starting_handoff(self):
    state = Ioniq6LongitudinalTuningState()

    state = update_ioniq_6_longitudinal_tuning(state, accel_cmd=1.0, v_ego=0.0, a_ego=0.0,
                                               long_control_state=LongCtrlState.starting, long_active=True)
    assert state.launch_active
    assert state.actual_accel == pytest.approx(0.288)
    assert state.jerk_upper == pytest.approx(5.76)
    assert state.jerk_lower == pytest.approx(1.0)

    state = update_ioniq_6_longitudinal_tuning(state, accel_cmd=0.3, v_ego=0.25, a_ego=1.2,
                                               long_control_state=LongCtrlState.pid, long_active=True)
    assert state.launch_active
    assert state.desired_accel > 0.3
    assert state.actual_accel > 0.288

  def test_ioniq_6_longitudinal_tuning_helper_softens_stop_release_handoff(self):
    state = Ioniq6LongitudinalTuningState(actual_accel=-0.12, accel_last=-0.12,
                                          stopping=True, stopping_count=25,
                                          long_control_state_last=LongCtrlState.stopping)

    state = update_ioniq_6_longitudinal_tuning(state, accel_cmd=1.0, v_ego=0.0, a_ego=0.0,
                                               long_control_state=LongCtrlState.starting, long_active=True)
    assert state.actual_accel == pytest.approx(0.096)

    state = update_ioniq_6_longitudinal_tuning(state, accel_cmd=1.0, v_ego=0.0, a_ego=0.0,
                                               long_control_state=LongCtrlState.starting, long_active=True)
    assert state.actual_accel == pytest.approx(0.312)

  def test_ioniq_6_longitudinal_tuning_helper_softens_final_stop_hold(self):
    state = Ioniq6LongitudinalTuningState(actual_accel=-0.12, accel_last=-0.12,
                                          stopping=True, stopping_count=25,
                                          long_control_state_last=LongCtrlState.stopping)

    state = update_ioniq_6_longitudinal_tuning(state, accel_cmd=-1.8, v_ego=0.0, a_ego=0.0,
                                               long_control_state=LongCtrlState.stopping, long_active=True)
    assert state.desired_accel == pytest.approx(-0.09)
    assert state.jerk_upper == pytest.approx(0.42)
    assert state.actual_accel == pytest.approx(-0.099)

  def test_genesis_g90_longitudinal_tuning_softens_final_stop_hold(self):
    state = GenesisG90LongitudinalTuningState()

    state = update_genesis_g90_longitudinal_tuning(state, accel_cmd=-2.0, v_ego=0.02,
                                                   long_control_state=LongCtrlState.stopping, long_active=True)
    assert state.actual_accel == pytest.approx(-0.10)
    assert not state.release_active

  def test_genesis_g90_longitudinal_tuning_gradually_unwinds_into_stop_hold(self):
    state = GenesisG90LongitudinalTuningState(actual_accel=-2.0)

    state = update_genesis_g90_longitudinal_tuning(state, accel_cmd=-2.0, v_ego=0.5,
                                                   long_control_state=LongCtrlState.stopping, long_active=True)
    assert state.actual_accel == pytest.approx(-1.96)

    state = update_genesis_g90_longitudinal_tuning(state, accel_cmd=-2.0, v_ego=0.3,
                                                   long_control_state=LongCtrlState.stopping, long_active=True)
    assert state.actual_accel == pytest.approx(-1.9)

  def test_genesis_g90_longitudinal_tuning_caps_low_speed_stop_brake(self):
    state = GenesisG90LongitudinalTuningState(actual_accel=-1.0)

    state = update_genesis_g90_longitudinal_tuning(state, accel_cmd=-0.4, v_ego=0.3,
                                                   long_control_state=LongCtrlState.stopping, long_active=True)
    assert state.actual_accel == pytest.approx(-0.94)

    state = update_genesis_g90_longitudinal_tuning(state, accel_cmd=-0.4, v_ego=0.3,
                                                   long_control_state=LongCtrlState.stopping, long_active=True)
    assert state.actual_accel == pytest.approx(-0.88)

  def test_genesis_g90_longitudinal_tuning_ramps_out_of_stop_hold(self):
    state = GenesisG90LongitudinalTuningState(actual_accel=-0.12, long_control_state_last=LongCtrlState.stopping)

    state = update_genesis_g90_longitudinal_tuning(state, accel_cmd=0.5, v_ego=0.02,
                                                   long_control_state=LongCtrlState.pid, long_active=True)
    assert state.release_active
    assert state.actual_accel == pytest.approx(-0.06866666666666665)

    state = update_genesis_g90_longitudinal_tuning(state, accel_cmd=0.5, v_ego=0.2,
                                                   long_control_state=LongCtrlState.pid, long_active=True)
    assert state.actual_accel == pytest.approx(-0.005333333333333315)

  def test_canfd_acc_control_uses_direct_accel(self):
    CP = CarParams.new_message()
    CP.carFingerprint = CAR.KIA_EV6
    CP.flags = int(HyundaiFlags.CANFD)

    packer = CANPacker(DBC[CP.carFingerprint][Bus.pt])
    can_bus = CanBus(CP)
    parser = CANParser(DBC[CP.carFingerprint][Bus.pt], [("SCC_CONTROL", 0)], can_bus.ECAN)

    msg = hyundaicanfd.create_acc_control(packer, can_bus, enabled=True, accel_last=1.5, accel=-1.2, stopping=False,
                                          gas_override=False, set_speed=42, hud_control=SimpleNamespace(leadDistanceBars=3),
                                          main_mode_acc=0, jerk_lower=5.0, jerk_upper=1.0, direct_accel=True)
    parser.update([(1, [msg])])

    assert parser.can_valid
    assert parser.vl["SCC_CONTROL"]["MainMode_ACC"] == 0
    assert parser.vl["SCC_CONTROL"]["aReqRaw"] == pytest.approx(-1.2)
    assert parser.vl["SCC_CONTROL"]["aReqValue"] == pytest.approx(-1.2)
    assert parser.vl["SCC_CONTROL"]["JerkLowerLimit"] == pytest.approx(5.0)
    assert parser.vl["SCC_CONTROL"]["JerkUpperLimit"] == pytest.approx(1.0)

  def test_can_acc_commands_use_default_values(self):
    CP = CarParams.new_message()
    CP.carFingerprint = CAR.GENESIS_G90

    packer = CANPacker(DBC[CP.carFingerprint][Bus.pt])
    parser = CANParser(DBC[CP.carFingerprint][Bus.pt], [("SCC11", 0), ("SCC12", 0), ("SCC14", 0)], 0)

    msgs = hyundaican.create_acc_commands(packer, enabled=True, accel=-1.0, upper_jerk=2.5, idx=3,
                                          hud_control=SimpleNamespace(leadDistanceBars=3, leadVisible=False), set_speed=42,
                                          stopping=False, long_override=False, use_fca=False, CP=CP)
    parser.update([(1, msgs)])

    assert parser.can_valid
    assert parser.vl["SCC11"]["MainMode_ACC"] == 1
    assert parser.vl["SCC12"]["StopReq"] == 0
    assert parser.vl["SCC12"]["CF_VSM_ConfMode"] == 1
    assert parser.vl["SCC12"]["AEB_Status"] == 2
    assert parser.vl["SCC12"]["aReqRaw"] == pytest.approx(-1.0)
    assert parser.vl["SCC12"]["aReqValue"] == pytest.approx(-1.0)
    assert parser.vl["SCC14"]["ComfortBandUpper"] == pytest.approx(0.0)
    assert parser.vl["SCC14"]["ComfortBandLower"] == pytest.approx(0.0)
    assert parser.vl["SCC14"]["JerkLowerLimit"] == pytest.approx(5.0)

  def test_can_acc_commands_use_enabled_fca_status(self):
    CP = CarParams.new_message()
    CP.carFingerprint = CAR.GENESIS_G90

    packer = CANPacker(DBC[CP.carFingerprint][Bus.pt])
    parser = CANParser(DBC[CP.carFingerprint][Bus.pt], [("FCA11", 0)], 0)

    msgs = hyundaican.create_acc_commands(packer, enabled=True, accel=-1.0, upper_jerk=2.5, idx=3,
                                          hud_control=SimpleNamespace(leadDistanceBars=3, leadVisible=False), set_speed=42,
                                          stopping=False, long_override=False, use_fca=True, CP=CP)
    parser.update([(1, msgs)])

    assert parser.can_valid
    assert parser.vl["FCA11"]["FCA_Status"] == 2

  def test_can_canfd_blended_acc_commands_use_palisade_2023_layout(self):
    CP = CarParams.new_message()
    CP.carFingerprint = CAR.HYUNDAI_PALISADE_2023
    CP.flags = int(HyundaiFlags.CAN_CANFD_BLENDED)

    packer = CANPacker(DBC[CP.carFingerprint][Bus.pt])
    parser = CANParser(DBC[CP.carFingerprint][Bus.pt], [
      ("SCC11", 0),
      ("SCC12", 0),
      ("SCC14", 0),
      ("RADAR_0x363", 0),
      ("RADAR_0x398", 0),
    ], 0)

    msgs = hyundaican.create_acc_commands_can_canfd_blended(
      packer,
      enabled=True,
      accel=-1.0,
      upper_jerk=2.5,
      idx=3,
      hud_control=SimpleNamespace(leadDistanceBars=3),
      set_speed=42,
      stopping=False,
      long_override=False,
      use_fca=False,
      CP=CP,
    )
    msgs.extend(hyundaican.create_radar_aux_messages(packer, CanBus(CP), 10))
    parser.update([(1, msgs)])

    assert parser.can_valid
    assert parser.vl["SCC11"]["aReqRaw"] == pytest.approx(-1.0)
    assert parser.vl["SCC11"]["aReqValue"] == pytest.approx(-1.0)
    assert parser.vl["SCC12"]["ACCMode"] == 1
    assert parser.vl["SCC12"]["MainMode_ACC"] == 1
    assert parser.vl["SCC14"]["ObjStatus"] == 1
    assert parser.vl["RADAR_0x363"]["FCA_ESA"] == 1

  def test_can_acc_optional_messages_use_enabled_fca_usm(self):
    CP = CarParams.new_message()
    CP.carFingerprint = CAR.GENESIS_G90

    packer = CANPacker(DBC[CP.carFingerprint][Bus.pt])
    parser = CANParser(DBC[CP.carFingerprint][Bus.pt], [("FCA12", 0)], 0)

    msgs = hyundaican.create_acc_opt(packer, CP)
    parser.update([(1, msgs)])

    assert parser.can_valid
    assert parser.vl["FCA12"]["FCA_DrvSetState"] == 2
    assert parser.vl["FCA12"]["FCA_USM"] == 2

  def test_sportage_angle_steering_uses_adas_cmd_with_send_lfa(self):
    fingerprint = gen_empty_fingerprint()
    cam_can = CanBus(None, fingerprint).CAM
    fingerprint[cam_can][0xCB] = 24
    CP = CarInterface.get_params(CAR.KIA_SPORTAGE_HEV_2026, fingerprint, [], False, False, False, None)

    assert CP.flags & HyundaiFlags.SEND_LFA
    assert CP.flags & HyundaiFlags.CANFD_ANGLE_STEERING

    packer = CANPacker(DBC[CP.carFingerprint][Bus.pt])
    msgs = hyundaicanfd.create_steering_messages(packer, CP, CanBus(CP), True, True, 1.0, 12.3)
    assert [(addr, bus) for addr, _, bus in msgs] == [(0xCB, CanBus(CP).ECAN)]

  def test_ioniq_6_lfa_helper_preserves_stock_ui_fields(self):
    CP = CarParams.new_message()
    CP.carFingerprint = CAR.HYUNDAI_IONIQ_6
    CP.flags = int(HyundaiFlags.CANFD | HyundaiFlags.CANFD_LKA_STEERING)
    CP.openpilotLongitudinalControl = True

    packer = CANPacker(DBC[CP.carFingerprint][Bus.pt])
    can_bus = CanBus(CP)
    parser = CANParser(DBC[CP.carFingerprint][Bus.pt], [("LFA", 0)], can_bus.ECAN)

    stock_lfa = {
      "CHECKSUM": 1234,
      "COUNTER": 42,
      "LKA_MODE": 6,
      "NEW_SIGNAL_1": 3,
      "LKA_WARNING": 1,
      "LKA_ICON": 1,
      "TORQUE_REQUEST": 17,
      "STEER_REQ": 0,
      "LFA_BUTTON": 1,
      "LKA_ASSIST": 1,
      "STEER_MODE": 5,
      "NEW_SIGNAL_2": 2,
      "NEW_SIGNAL_4": 7,
      "HAS_LANE_SAFETY": 1,
      "DAMP_FACTOR": 0x77,
    }

    msgs = hyundaicanfd.create_steering_messages(packer, CP, can_bus, True, True, 123, 0.0, stock_lfa)
    lfa_msgs = [msg for msg in msgs if msg[0] == 0x12A]
    assert len(lfa_msgs) == 1

    parser.update([(1, lfa_msgs)])

    assert parser.can_valid
    assert parser.vl["LFA"]["NEW_SIGNAL_1"] == 3
    assert parser.vl["LFA"]["NEW_SIGNAL_2"] == 2
    assert parser.vl["LFA"]["HAS_LANE_SAFETY"] == 1
    assert parser.vl["LFA"]["DAMP_FACTOR"] == 0x77
    assert parser.vl["LFA"]["TORQUE_REQUEST"] == 123
    assert parser.vl["LFA"]["STEER_REQ"] == 1
    assert parser.vl["LFA"]["LKA_ICON"] == 2

  def test_ioniq_6_lkas_alt_helper_preserves_stock_camera_fields(self):
    CP = CarParams.new_message()
    CP.carFingerprint = CAR.HYUNDAI_IONIQ_6
    CP.flags = int(HyundaiFlags.CANFD | HyundaiFlags.CANFD_LKA_STEERING | HyundaiFlags.CANFD_LKA_STEERING_ALT)

    packer = CANPacker(DBC[CP.carFingerprint][Bus.pt])
    can_bus = CanBus(CP)
    parser = CANParser(DBC[CP.carFingerprint][Bus.pt], [("LKAS_ALT", 0)], can_bus.ACAN)

    stock_lkas = {
      "CHECKSUM": 1234,
      "COUNTER": 42,
      "LKA_MODE": 6,
      "LKA_AVAILABLE": 3,
      "LKA_WARNING": 1,
      "LKA_ICON": 1,
      "FCA_SYSWARN": 1,
      "TORQUE_REQUEST": 17,
      "STEER_REQ": 0,
      "LFA_BUTTON": 1,
      "LKA_ASSIST": 1,
      "STEER_MODE": 5,
      "NEW_SIGNAL_2": 2,
      "LKAS_ANGLE_ACTIVE": 1,
      "HAS_LANE_SAFETY": 1,
      "ADAS_StrAnglReqVal": 12.3,
      "ADAS_ACIAnglTqRedcGainVal": 0.42,
      "DAMP_FACTOR": 0x70,
    }

    msgs = hyundaicanfd.create_steering_messages(packer, CP, can_bus, True, True, 123, 0.0,
                                                 lkas_base_values=stock_lkas)
    lkas_msgs = [msg for msg in msgs if msg[0] == 0x110]
    assert len(lkas_msgs) == 1

    parser.update([(1, lkas_msgs)])

    assert parser.can_valid
    assert parser.vl["LKAS_ALT"]["LKA_AVAILABLE"] == 3
    assert parser.vl["LKAS_ALT"]["LKA_WARNING"] == 1
    assert parser.vl["LKAS_ALT"]["FCA_SYSWARN"] == 1
    assert parser.vl["LKAS_ALT"]["LFA_BUTTON"] == 1
    assert parser.vl["LKAS_ALT"]["HAS_LANE_SAFETY"] == 1
    assert parser.vl["LKAS_ALT"]["DAMP_FACTOR"] == 0x70
    assert parser.vl["LKAS_ALT"]["TORQUE_REQUEST"] == 123
    assert parser.vl["LKAS_ALT"]["STEER_REQ"] == 1
    assert parser.vl["LKAS_ALT"]["LKA_ICON"] == 2

  def test_ioniq_6_blindspot_status_helper_regenerates_counter_checksum(self):
    CP = CarParams.new_message()
    CP.carFingerprint = CAR.HYUNDAI_IONIQ_6
    CP.flags = int(HyundaiFlags.CANFD | HyundaiFlags.CANFD_LKA_STEERING)

    packer = CANPacker(DBC[CP.carFingerprint][Bus.pt])
    can_bus = CanBus(CP)
    parser = CANParser(DBC[CP.carFingerprint][Bus.pt], [("BLINDSPOTS_REAR_CORNERS", 0), ("BLINDSPOTS_FRONT_CORNER_1", 0)], can_bus.ECAN)

    rear = {
      "CHECKSUM": 1111,
      "COUNTER": 77,
      "BCW_Sta": 0,
      "BCW_OnOffEquipSta": 0,
      "BCW_LtIndSta": 0,
      "BCW_RtIndSta": 0,
      "BCW_LtSndWrngSta": 0,
      "BCW_RtSndWrngSta": 0,
      "FL_INDICATOR": 0,
      "FR_INDICATOR": 0,
      "BCW_SnstvtyModRetVal": 0,
      "BCW_IndSta": 0,
      "BCA_OnOffEquip2Sta": 0,
      "BCA_Sta": 0,
      "BCA_OnOffEquipSta": 0,
      "BCA_DRV_WarnSta": 0,
      "BCA_Plus_Deccel_Req": 0,
      "BCA_Plus_BrkCmdSta": 0,
      "BCA_Plus_LtWrngSta": 0,
      "BCA_Plus_RtWrngSta": 0,
      "BCA_Plus_FuncStat": 0,
      "BCA_Plus_Sta": 0,
      "Brake_Control_RL": 0,
      "Brake_Control_RR": 0,
      "OSMrrLamp_LtIndSta": 0,
      "OSMrrLamp_RtIndSta": 0,
    }
    front = {
      "CHECKSUM": 2222,
      "COUNTER": 88,
      "REVERSING": 0,
      "NEW_SIGNAL_5": 0,
      "NEW_SIGNAL_7": 0,
      "NEW_SIGNAL_8": 0,
      "NEW_SIGNAL_9": 0,
      "NEW_SIGNAL_4": 0,
      "NEW_SIGNAL_3": 1,
      "NEW_SIGNAL_2": 0,
      "NEW_SIGNAL_1": 0,
    }

    msgs = hyundaicanfd.create_blindspot_status_messages(packer, can_bus, rear, front,
                                                         left_blindspot=True, right_blindspot=False,
                                                         left_blinker=False, right_blinker=False)
    parser.update([(1, msgs)])

    assert parser.can_valid
    assert parser.vl["BLINDSPOTS_REAR_CORNERS"]["COUNTER"] == 0
    assert parser.vl["BLINDSPOTS_FRONT_CORNER_1"]["COUNTER"] == 0
    assert parser.vl["BLINDSPOTS_REAR_CORNERS"]["BCW_Sta"] == 1
    assert parser.vl["BLINDSPOTS_REAR_CORNERS"]["BCW_LtIndSta"] == 1
    assert parser.vl["BLINDSPOTS_REAR_CORNERS"]["BCW_RtIndSta"] == 0
    assert parser.vl["BLINDSPOTS_REAR_CORNERS"]["OSMrrLamp_LtIndSta"] == 1
    assert parser.vl["BLINDSPOTS_REAR_CORNERS"]["OSMrrLamp_RtIndSta"] == 0
    assert parser.vl["BLINDSPOTS_REAR_CORNERS"]["FL_INDICATOR"] == 1
    assert parser.vl["BLINDSPOTS_REAR_CORNERS"]["FR_INDICATOR"] == 0
    assert parser.vl["BLINDSPOTS_FRONT_CORNER_1"]["NEW_SIGNAL_3"] == 1

    flash_msgs = hyundaicanfd.create_blindspot_status_messages(packer, can_bus, rear, front,
                                                               left_blindspot=True, right_blindspot=False,
                                                               left_blinker=True, right_blinker=False)
    parser.update([(1, flash_msgs)])

    assert parser.vl["BLINDSPOTS_REAR_CORNERS"]["BCW_LtIndSta"] == 2
    assert parser.vl["BLINDSPOTS_REAR_CORNERS"]["OSMrrLamp_LtIndSta"] == 2

  def test_ioniq_6_blindspot_radar_state_decode(self):
    assert decode_ioniq_6_blindspot_radar_state(0x02) == (False, False)
    assert decode_ioniq_6_blindspot_radar_state(0x0A) == (False, True)
    assert decode_ioniq_6_blindspot_radar_state(0x12) == (True, False)
    assert decode_ioniq_6_blindspot_radar_state(0x1A) == (True, True)
    assert decode_ioniq_6_blindspot_radar_state(10.0) == (False, True)

  def test_ioniq_6_cluster_blindspot_helper_uses_captured_stock_sequences(self):
    CP = CarParams.new_message()
    CP.carFingerprint = CAR.HYUNDAI_IONIQ_6
    CP.flags = int(HyundaiFlags.CANFD | HyundaiFlags.CANFD_LKA_STEERING)

    can_bus = CanBus(CP)

    right_msgs = hyundaicanfd.create_ioniq_6_cluster_blindspot_messages(can_bus, 0, False, True)
    assert right_msgs == [
      (0x3B5, bytes.fromhex("caa95c00000000464600000000000000d7020000000069070000000000000000"), can_bus.ECAN),
      (0x31A, bytes.fromhex("fa7c10f0f0ffff03898aff0b0a8678ff000000007e0055550000000000000000"), can_bus.ECAN),
    ]

    left_msgs = hyundaicanfd.create_ioniq_6_cluster_blindspot_messages(can_bus, 100, True, False)
    assert left_msgs == [
      (0x3B5, bytes.fromhex("e682c600000000464600000000000000da020000000069070000000000000000"), can_bus.ECAN),
      (0x31A, bytes.fromhex("c34129f0f0ffff03898aff0a098678ff000000007e0055550000000000000000"), can_bus.ECAN),
    ]

    both_msgs = hyundaicanfd.create_ioniq_6_cluster_blindspot_messages(can_bus, 0, True, True)
    assert both_msgs == []

  def test_ioniq_6_cluster_lane_change_helper_uses_stock_trigger_and_hold(self):
    CP = CarParams.new_message()
    CP.carFingerprint = CAR.HYUNDAI_IONIQ_6
    CP.flags = int(HyundaiFlags.CANFD | HyundaiFlags.CANFD_LKA_STEERING)

    can_bus = CanBus(CP)

    assert hyundaicanfd.create_ioniq_6_cluster_lane_change_messages(can_bus, 7, "right") == []
    assert hyundaicanfd.create_ioniq_6_cluster_lane_change_messages(can_bus, 0, "right", trigger=True) == [
      (0x3C1, bytes.fromhex("e910300041000000"), can_bus.ECAN),
    ]
    assert hyundaicanfd.create_ioniq_6_cluster_lane_change_messages(can_bus, 20, "right") == [
      (0x3C1, bytes.fromhex("ab20300001000000"), can_bus.ECAN),
    ]
    assert hyundaicanfd.create_ioniq_6_cluster_lane_change_messages(can_bus, 0, "left", trigger=True) == [
      (0x3C1, bytes.fromhex("3d40304010000000"), can_bus.ECAN),
    ]
    assert hyundaicanfd.create_ioniq_6_cluster_lane_change_messages(can_bus, 20, "left") == [
      (0x3C1, bytes.fromhex("3e50300000000000"), can_bus.ECAN),
    ]

  def test_sportage_angle_jerk_override_is_scoped(self):
    sportage = CarParams.new_message()
    sportage.carFingerprint = CAR.KIA_SPORTAGE_HEV_2026
    sportage.flags = int(HyundaiFlags.CANFD | HyundaiFlags.CANFD_ANGLE_STEERING)

    comparison_angle = CarParams.new_message()
    comparison_angle.carFingerprint = CAR.KIA_EV6
    comparison_angle.flags = int(HyundaiFlags.CANFD | HyundaiFlags.CANFD_ANGLE_STEERING)

    ioniq6 = CarParams.new_message()
    ioniq6.carFingerprint = CAR.HYUNDAI_IONIQ_6
    ioniq6.flags = int(HyundaiFlags.CANFD | HyundaiFlags.CANFD_LKA_STEERING | HyundaiFlags.CANFD_LKA_STEERING_ALT)

    sportage_params = CarControllerParams(sportage)
    sportage_low_speed_params = CarControllerParams(sportage, vEgoRaw=5.0)
    sportage_high_speed_params = CarControllerParams(sportage, vEgoRaw=20.0)
    comparison_params = CarControllerParams(comparison_angle)
    ioniq6_params = CarControllerParams(ioniq6)

    assert sportage_params.ANGLE_LIMITS.MAX_LATERAL_JERK < comparison_params.ANGLE_LIMITS.MAX_LATERAL_JERK
    assert sportage_high_speed_params.ANGLE_LIMITS.MAX_LATERAL_JERK == sportage_params.ANGLE_LIMITS.MAX_LATERAL_JERK
    assert sportage_low_speed_params.ANGLE_LIMITS.MAX_LATERAL_JERK > sportage_high_speed_params.ANGLE_LIMITS.MAX_LATERAL_JERK
    assert sportage_low_speed_params.ANGLE_LIMITS.MAX_LATERAL_JERK < comparison_params.ANGLE_LIMITS.MAX_LATERAL_JERK
    assert comparison_params.ANGLE_LIMITS.MAX_LATERAL_JERK == ioniq6_params.ANGLE_LIMITS.MAX_LATERAL_JERK

  def test_ioniq_5_canfd_aux_messages_are_optional(self):
    toggles = get_test_toggles()
    fingerprint = gen_empty_fingerprint()
    CP = CarInterface.get_params(CAR.HYUNDAI_IONIQ_5, fingerprint, [], False, False, False, toggles)
    FPCP = CarInterface.get_starpilot_params(CAR.HYUNDAI_IONIQ_5, fingerprint, [], CP, toggles)

    car_state = CarState(CP, FPCP)
    can_parsers = car_state.get_can_parsers(CP)
    packer = CANPacker(DBC[CP.carFingerprint][Bus.pt])

    drive_mode_addr = packer.dbc.name_to_msg["DRIVE_MODE_EV"].address
    media_buttons_addr = packer.dbc.name_to_msg["STEERING_WHEEL_MEDIA_BUTTONS"].address

    assert can_parsers[Bus.pt].message_states[drive_mode_addr].ignore_alive
    assert can_parsers[Bus.pt].message_states[media_buttons_addr].ignore_alive

    for frame in range(1, 6):
      t = frame * 100_000_000
      for parser in can_parsers.values():
        required_msgs = [packer.make_can_msg(state.name, parser.bus, {})
                         for state in parser.message_states.values() if not state.ignore_alive]
        parser.update([(t, required_msgs)])

    assert all(parser.can_valid for parser in can_parsers.values())

  def test_blacklisted_parts(self, subtests):
    # Asserts no ECUs known to be shared across platforms exist in the database.
    # Tucson having Santa Cruz camera and EPS for example
    for car_model, ecus in FW_VERSIONS.items():
      with subtests.test(car_model=car_model.value):
        if car_model == CAR.HYUNDAI_SANTA_CRUZ_1ST_GEN:
          pytest.skip("Skip checking Santa Cruz for its parts")

        for code, _ in get_platform_codes(ecus[(Ecu.fwdCamera, 0x7c4, None)]):
          if b"-" not in code:
            continue
          part = code.split(b"-")[1]
          assert not part.startswith(b'CW'), "Car has bad part number"

  def test_correct_ecu_response_database(self, subtests):
    """
    Assert standard responses for certain ECUs, since they can
    respond to multiple queries with different data
    """
    expected_fw_prefix = HYUNDAI_VERSION_REQUEST_LONG[1:]
    for car_model, ecus in FW_VERSIONS.items():
      with subtests.test(car_model=car_model.value):
        for ecu, fws in ecus.items():
          assert all(fw.startswith(expected_fw_prefix) for fw in fws), \
                          f"FW from unexpected request in database: {(ecu, fws)}"

  @settings(max_examples=100)
  @given(data=st.data())
  def test_platform_codes_fuzzy_fw(self, data):
    """Ensure function doesn't raise an exception"""
    fw_strategy = st.lists(st.binary())
    fws = data.draw(fw_strategy)
    get_platform_codes(fws)

  def test_expected_platform_codes(self, subtests):
    # Ensures we don't accidentally add multiple platform codes for a car unless it is intentional
    for car_model, ecus in FW_VERSIONS.items():
      with subtests.test(car_model=car_model.value):
        for ecu, fws in ecus.items():
          if ecu[0] not in PLATFORM_CODE_ECUS:
            continue

          # Third and fourth character are usually EV/hybrid identifiers
          codes = {code.split(b"-")[0][:2] for code, _ in get_platform_codes(fws)}
          if car_model in (CAR.HYUNDAI_PALISADE, CAR.HYUNDAI_PALISADE_2023):
            assert codes == {b"LX", b"ON"}, f"Car has unexpected platform codes: {car_model} {codes}"
          elif car_model == CAR.HYUNDAI_KONA_EV and ecu[0] == Ecu.fwdCamera:
            assert codes == {b"OE", b"OS"}, f"Car has unexpected platform codes: {car_model} {codes}"
          else:
            assert len(codes) == 1, f"Car has multiple platform codes: {car_model} {codes}"

  # Tests for platform codes, part numbers, and FW dates which Hyundai will use to fuzzy
  # fingerprint in the absence of full FW matches:
  def test_platform_code_ecus_available(self, subtests):
    # TODO: add queries for these non-CAN FD cars to get EPS
    no_eps_platforms = CANFD_CAR | {CAR.KIA_SORENTO, CAR.KIA_OPTIMA_G4, CAR.KIA_OPTIMA_G4_FL, CAR.KIA_OPTIMA_H,
                                    CAR.KIA_OPTIMA_H_G4_FL, CAR.HYUNDAI_SONATA_LF, CAR.HYUNDAI_TUCSON, CAR.GENESIS_G90, CAR.GENESIS_G80, CAR.HYUNDAI_ELANTRA}

    # Asserts ECU keys essential for fuzzy fingerprinting are available on all platforms
    for car_model, ecus in FW_VERSIONS.items():
      with subtests.test(car_model=car_model.value):
        for platform_code_ecu in PLATFORM_CODE_ECUS:
          if platform_code_ecu in (Ecu.fwdRadar, Ecu.eps) and car_model == CAR.HYUNDAI_GENESIS:
            continue
          if platform_code_ecu == Ecu.eps and car_model in no_eps_platforms:
            continue
          assert platform_code_ecu in [e[0] for e in ecus]

  def test_fw_format(self, subtests):
    # Asserts:
    # - every supported ECU FW version returns one platform code
    # - every supported ECU FW version has a part number
    # - expected parsing of ECU FW dates

    for car_model, ecus in FW_VERSIONS.items():
      with subtests.test(car_model=car_model.value):
        for ecu, fws in ecus.items():
          if ecu[0] not in PLATFORM_CODE_ECUS:
            continue

          codes = set()
          for fw in fws:
            result = get_platform_codes([fw])
            assert 1 == len(result), f"Unable to parse FW: {fw}"
            codes |= result

          if ecu[0] not in DATE_FW_ECUS or car_model in NO_DATES_PLATFORMS:
            assert all(date is None for _, date in codes)
          else:
            assert all(date is not None for _, date in codes)

          if car_model == CAR.HYUNDAI_GENESIS:
            pytest.skip("No part numbers for car model")

          # Hyundai places the ECU part number in their FW versions, assert all parsable
          # Some examples of valid formats: b"56310-L0010", b"56310L0010", b"56310/M6300"
          if car_model != CAR.KIA_SPORTAGE_HEV_2026:
            assert all(b"-" in code for code, _ in codes), \
                            f"FW does not have part number: {fw}"

  def test_platform_codes_spot_check(self):
    # Asserts basic platform code parsing behavior for a few cases
    results = get_platform_codes([b"\xf1\x00DH LKAS 1.1 -150210"])
    assert results == {(b"DH", b"150210")}

    # Some cameras and all radars do not have dates
    results = get_platform_codes([b"\xf1\x00AEhe SCC H-CUP      1.01 1.01 96400-G2000         "])
    assert results == {(b"AEhe-G2000", None)}

    results = get_platform_codes([b"\xf1\x00CV1_ RDR -----      1.00 1.01 99110-CV000         "])
    assert results == {(b"CV1-CV000", None)}

    results = get_platform_codes([
      b"\xf1\x00DH LKAS 1.1 -150210",
      b"\xf1\x00AEhe SCC H-CUP      1.01 1.01 96400-G2000         ",
      b"\xf1\x00CV1_ RDR -----      1.00 1.01 99110-CV000         ",
    ])
    assert results == {(b"DH", b"150210"), (b"AEhe-G2000", None), (b"CV1-CV000", None)}

    results = get_platform_codes([
      b"\xf1\x00LX2 MFC  AT USA LHD 1.00 1.07 99211-S8100 220222",
      b"\xf1\x00LX2 MFC  AT USA LHD 1.00 1.08 99211-S8100 211103",
      b"\xf1\x00ON  MFC  AT USA LHD 1.00 1.01 99211-S9100 190405",
      b"\xf1\x00ON  MFC  AT USA LHD 1.00 1.03 99211-S9100 190720",
    ])
    assert results == {(b"LX2-S8100", b"220222"), (b"LX2-S8100", b"211103"),
                               (b"ON-S9100", b"190405"), (b"ON-S9100", b"190720")}

  def test_fuzzy_excluded_platforms(self):
    # Asserts a list of platforms that will not fuzzy fingerprint with platform codes due to them being shared.
    # This list can be shrunk as we combine platforms and detect features
    excluded_platforms = {
      CAR.GENESIS_G70,            # shared platform code, part number, and date
      CAR.GENESIS_G70_2020,
    }
    excluded_platforms |= CANFD_CAR - EV_CAR - CANFD_FUZZY_WHITELIST  # shared platform codes
    excluded_platforms |= NO_DATES_PLATFORMS  # date codes are required to match

    platforms_with_shared_codes = set()
    for platform, fw_by_addr in FW_VERSIONS.items():
      car_fw = []
      for ecu, fw_versions in fw_by_addr.items():
        ecu_name, addr, sub_addr = ecu
        for fw in fw_versions:
          car_fw.append(CarParams.CarFw(ecu=ecu_name, fwVersion=fw, address=addr,
                                        subAddress=0 if sub_addr is None else sub_addr))

      CP = CarParams(carFw=car_fw)
      matches = FW_QUERY_CONFIG.match_fw_to_car_fuzzy(build_fw_dict(CP.carFw), CP.carVin, FW_VERSIONS)
      if len(matches) == 1:
        assert list(matches)[0] == platform
      else:
        platforms_with_shared_codes.add(platform)

    assert platforms_with_shared_codes == excluded_platforms
