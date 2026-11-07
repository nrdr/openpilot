"""Offline differential replay against unmodified, Git-blob-verified MVL sources.

No vehicle connection, host Params, disk persistence, or production controller is
used to generate the oracle. The frozen donor executes its own entire update().

Personality/following profiles are parent-owned: Aggressive/Standard/Relaxed
must be fully pinned MVL (no NRDR tune-file influence), with Econ alone custom.
These tests certify the command boundary for identical host requests, not the
parent's profile selection or UI locks.
"""
import ast
import hashlib
import math
from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from types import ModuleType

import pytest

from opendbc.can import CANParser
from opendbc.car import Bus, gen_empty_fingerprint, structs
from opendbc.car.common.conversions import Conversions as CV
from opendbc.car.honda.carcontroller import CarController
from opendbc.car.honda.interface import CarInterface
from opendbc.car.honda.values import CAR, DBC, HONDA_BOSCH, HondaFlags
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from opendbc.sunnypilot.car.interfaces import setup_interfaces
from opendbc.sunnypilot.car.tests.runtime_config import make_test_car_config

REFERENCE = Path(__file__).with_name("mvl_reference")
DONOR = "3fec9a418a659de31d7b1f494193161697a35071"
BLOBS = {
  "carcontroller": "439994c8c181c9d2edc84bbe3c724b1ac744feab",
  "values": "1563253603da78c02c1527266d03145ab91cda15",
  "interface": "d4fa2361150e820c564e7c2f7f882c9822f26639",
  "nidec_long_helpers": "57cb256f35fea94fd7b783bfce1ed721cd5e407d",
  "gas_interceptor": "d8853c13e7629a75e05a65cb497f9b9629ceb11c",
  "hondacan": "3461f0d0ec280eab8b1e60a1dc327d8a959d2e24",
  "interfaces": "5c65fdcf4cc382bf961c70db02fcdb069b4ab711",
  # Last legacy controller before engine braking (2320f7e4ff87eb52ed27567d9ab8e87b2f58a939).
  "legacy_carcontroller": "c91f91d407f56e7017f77471635ca0ee36150e67",
}

# Host MvlStateStore contract, independently listed here (never derived from the
# implementation's key tables). No raw Honda*Params names may cross this boundary.
STATE_KEYS = {
  "brake_pid": "HondaBrakePIDParams", "feedforward": "HondaFeedForwardParams",
  "car_gas_scale": "HondaCarGasScaleParams", "creep_factor": "HondaCreepFactorParams",
  "wind_factor": "HondaWindFactorParams", "sat_accel": "HondaSatAccelParams",
  "launch_dv": "HondaLaunchDvParams", "launch_gas": "HondaLaunchGasParams", "launch_dv_break": "HondaLaunchDvBreakParams",
}
for channel, raw, bands in (
  ("gas_factor", "GasFactor", ("00", "10", "20", "30")),
  ("gas_alpha", "GasAlpha", ("00", "10", "20", "30")),
  ("speed_factor", "SpeedFactor", ("05", "15", "25", "35")),
  ("speed_alpha", "SpeedAlpha", ("05", "15", "25", "35")),
):
  STATE_KEYS[channel] = f"Honda{raw}Params"
  STATE_KEYS[f"{channel}_low"] = f"Honda{raw}LowParams"
  STATE_KEYS.update({f"{channel}_{band}": f"Honda{raw}{band}Params" for band in bands})
STATE_KEYS.update({f"lat_accel_factor_{speed:02d}": f"HondaLatAccelFactor{speed:02d}Params" for speed in range(5, 65, 5)})


def source(name):
  data = (REFERENCE / f"{name}.py.txt").read_bytes()
  # Git may check text out as CRLF on Windows. Compare canonical Git blob bytes.
  data = data.replace(b"\r\n", b"\n")
  assert hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == BLOBS[name], name
  return data.decode()


def load_reference(name, **injected):
  text = source(name)
  # Only a display format fix for newer NumPy. No longitudinal expression changes.
  text = text.replace('f"{speed_val:02d}"', 'f"{int(speed_val):02d}"')
  tree = ast.parse(text)
  for node in tree.body:
    if isinstance(node, ast.ImportFrom):
      node.names = [alias for alias in node.names if (alias.asname or alias.name) not in injected]
  tree.body = [node for node in tree.body if not isinstance(node, ast.ImportFrom) or node.names]
  module = ModuleType(f"frozen_mvl_{name}")
  module.__dict__.update(injected)
  exec(compile(tree, f"{DONOR}/{name}.py", "exec"), module.__dict__)
  return module


class NoEpsMod:
  def __init__(self, CP, CP_SP):
    self.eps_mod_lookup = None


class MemoryWriter:
  def __init__(self):
    self.written = []

  def put_many(self, values):
    self.written.append(dict(values))


@pytest.fixture
def donor():
  # Use the actual donor constants, not the new implementation's curves.
  tree = ast.parse(source("values"))
  cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "CarControllerParams")
  namespace = {"CAR": CAR, "CV": CV}
  exec(compile(ast.Module(body=[cls], type_ignores=[]), "donor-values", "exec"), namespace)
  params = namespace["CarControllerParams"]
  # Frozen interface supplies its own per-platform gas-curve selection.
  interface = load_reference("interface", CarController=CarController, CarControllerParams=params)
  base = next(node for node in ast.parse(source("interfaces")).body
              if isinstance(node, ast.ClassDef) and node.name == "CarInterfaceBase")
  defaults = next(node for node in base.body if isinstance(node, ast.FunctionDef) and node.name == "get_std_params")
  defaults.decorator_list = []
  default_namespace = {"structs": structs, "get_torque_params": CarInterface.get_std_params.__globals__["get_torque_params"]}
  exec(compile(ast.Module(body=[defaults], type_ignores=[]), "donor-defaults", "exec"), default_namespace)
  interface.CarInterface.get_std_params = staticmethod(default_namespace["get_std_params"])
  helper = load_reference("nidec_long_helpers")
  pedal = load_reference("gas_interceptor")
  can = load_reference("hondacan")

  class MemoryParams:
    values = {}

    def get(self, key):
      return self.values.get(key)

  controller = load_reference(
    "carcontroller", Params=MemoryParams, HondaParamWriter=MemoryWriter, CarControllerParams=params,
    EpsModCarController=NoEpsMod, GasInterceptorCarController=pedal.GasInterceptorCarController,
    hondacan=can, nidec_speed_lead_mps=helper.nidec_speed_lead_mps,
    nidec_speed_channel_pinned=helper.nidec_speed_channel_pinned, nidec_set_speed_governed=helper.nidec_set_speed_governed,
  )
  # Replace only persistence. Never instantiate the donor's on-disk writer.
  controller.HondaParamWriter = MemoryWriter
  return controller, interface.CarInterface, MemoryParams


def build(car=CAR.HONDA_CIVIC, interceptor=False, *, mvl=True, hostile=False, stock=False, alpha=True, saved=None, clarity_bench=False):
  config = make_test_car_config(honda_stock_longitudinal=stock)
  config = replace(config, honda=replace(
    config.honda, mvl_longitudinal=mvl, nidec_pcm_mode=2 if hostile else 0,
    nidec_wind_brake=not hostile, civic_pcm_wind_credit_bench=hostile,
    clarity_interceptor_brake_bench=clarity_bench,
  ))
  provider = config.honda.provider
  provider.live_tuning = replace(provider.live_tuning, live_learning_gas=not hostile,
                                 full_brake_authority=hostile, roen_acceleration_limits=hostile,
                                 ecu_matched_long=hostile, stopping_decel_rate=0.001 if hostile else 3.0)

  def load(key, default):
    assert key in STATE_KEYS, f"Unsupported MVL learner key: {key}"
    return (saved or {}).get(key, default)

  def persist(values):
    assert set(values) <= STATE_KEYS.keys()
    provider.persisted.append(dict(values))

  provider.load_mvl_param = load
  provider.persist_mvl_state = persist
  fp = gen_empty_fingerprint()
  if interceptor:
    fp[0][0x201] = 6
  if clarity_bench:
    fp[0][0x184] = 8
  cp = CarInterface.get_params(car, fp, [], alpha, False, False, config)
  sp = CarInterface.get_params_sp(cp, car, fp, [], alpha, False, False)
  setup_interfaces(CarInterface, cp, sp, config)
  ci = CarInterface(cp, sp, config)
  ci.update([])
  ci.CS.out.canValid = True
  ci.CS.out.cruiseState.available = True
  ci.CS.out.cruiseState.speed = 30.0
  ci.CS.steer_control_active = True
  return ci, config, fp


def command(tick):
  cc = structs.CarControl(enabled=True, longActive=True)
  cc.actuators.accel = [0.4, 1.3, -0.25, -2.0, 0., 0.8, -0.5, 1.9][(tick // 100) % 8]
  cc.actuators.longControlState = "pid"
  if 300 <= tick % 800 < 400:
    cc.actuators.longControlState = "stopping"
  if 400 <= tick % 800 < 450:
    cc.longActive = False
  cc.orientationNED = [0., 0.035 * math.sin(tick / 80.), 0.]
  cc.hudControl.setSpeed = 30.
  cc.hudControl.speedVisible = True
  return cc


def drive_state(cs, tick):
  cs.out.vEgo = [0., 0.5, 2., 8., 16., 27., 29., 35.][(tick // 100) % 8]
  cs.out.aEgo = 0.2 * math.sin(tick / 30.)
  cs.out.standstill = cs.out.vEgo == 0
  cs.out.gasPressed = 450 <= tick % 800 < 470
  cs.out.brakePressed = 470 <= tick % 800 < 480
  cs.out.stockAeb = 480 <= tick % 800 < 500
  cs.car_gas_available = tick % 800 < 650
  cs.car_gas = 20. + 15. * math.sin(tick / 21.)
  cs.engine_rpm = 0 if tick % 800 < 50 else 1500


STATE = (
  "gasfactor", "windfactor", "gasalpha", "brake_pid_factor", "nidec_pid_factor",
  "brake_pid_factor_non_lowspeed", "average_factor", "average_factor_sens", "prior_gas_average",
  "car_gas_per_pcm_gas", "creep_factor", "sat_accel", "gas_factors", "gas_alphas",
  "speed_factors", "speed_alphas", "gas_factors_nomaxspeed", "gas_alphas_nomaxspeed",
  "gas_factors_before_gasmax", "windfactor_before_gasmax", "windfactor_before_brake",
  "gasfactor_before_gasmax", "a_ego_filt", "sat_deficit_frames", "sat_excess_frames",
  "dv_launch", "gas_launch", "dv_break", "launch_active", "launch_ticks",
  "gas_recovery_ticks", "gasint_nolearn_ticks", "last_gasint", "new_accel",
  "brake_last", "brake_steady", "last_applied_brake", "apply_brake_last", "last_pump_ts",
  "accel", "bosch_last_gas", "stopping_counter",
)


def state(controller):
  result = {name: deepcopy(getattr(controller, name)) for name in STATE}
  result["speed_cmd_hist"] = list(controller.speed_cmd_hist)
  result["pid_i"] = (controller.nidec_pid.i, controller.nidec_brake_pid.i, controller.brake_pid.i)
  return result


def longitudinal_packets(controller, messages):
  names = {"BRAKE_COMMAND", "GAS_COMMAND", "ACC_CONTROL", "ACC_CONTROL_ON"}
  return [(addr, bytes(dat), bus) for addr, dat, bus in messages
          if addr in controller.packer.dbc.addr_to_msg and controller.packer.dbc.addr_to_msg[addr].name in names]


@pytest.mark.parametrize("name", BLOBS)
def test_frozen_donor_git_blobs(name):
  source(name)


@pytest.mark.parametrize("car,interceptor", [
  (CAR.HONDA_CIVIC, False), (CAR.HONDA_CLARITY, False), (CAR.HONDA_CRV, False),
  (CAR.HONDA_CIVIC, True), (CAR.ACURA_ILX, True), (CAR.HONDA_CLARITY, True),
  (CAR.HONDA_CIVIC_BOSCH, False), (CAR.HONDA_INSIGHT, False),
  (CAR.ACURA_RDX_3G, False), (CAR.ACURA_RDX_3G_MMR, False),
  (CAR.HONDA_CIVIC_2022, False), (CAR.HONDA_PILOT_4G, False),
])
@pytest.mark.parametrize("seeded", [False, True])
def test_pinned_donor_replay(donor, car, interceptor, seeded):
  module, donor_interface, memory_params = donor
  saved = {"gas_alpha_low": .12, "gas_factor": 1.3, "wind_factor": .8, "gas_alpha": .07,
           "feedforward": .06, "speed_factor": 7., "speed_factor_low": 5., "launch_gas": 121.} if seeded else {}
  memory_params.values = {STATE_KEYS[key]: value for key, value in saved.items()}
  ci, config, fp = build(car, interceptor, saved=saved)
  # Calling the frozen interface selects the donor's actual model-specific curve.
  donor_cp = donor_interface.get_params(car, fp, [], True, False, False)
  oracle = module.CarController(DBC[car], ci.CP, ci.CP_SP)
  assert list(ci.CP.longitudinalTuning.kiV) == list(donor_cp.longitudinalTuning.kiV)
  assert list(ci.CP.longitudinalTuning.kiBP) == list(donor_cp.longitudinalTuning.kiBP)
  assert ci.CP.stopAccel == donor_cp.stopAccel
  assert ci.CP.longitudinalActuatorDelay == donor_cp.longitudinalActuatorDelay
  for name in ("NIDEC_ACCEL_MIN", "NIDEC_ACCEL_MAX", "NIDEC_MAX_ACCEL_V", "NIDEC_MAX_ACCEL_BP",
               "NIDEC_GAS_MAX", "NIDEC_BRAKE_MAX", "BOSCH_ACCEL_MIN", "BOSCH_ACCEL_MAX", "BOSCH_GAS_LOOKUP_BP", "BOSCH_GAS_LOOKUP_V"):
    assert getattr(ci.CC.params, name) == getattr(oracle.params, name)
  decoder_a = CANParser(DBC[car][Bus.pt], [("ACC_HUD", 10)], ci.CC.CAN.pt)
  decoder_b = CANParser(DBC[car][Bus.pt], [("ACC_HUD", 10)], ci.CC.CAN.pt)
  assert state(ci.CC) == state(oracle)
  # Include the second persistence boundary, with settled learning windows.
  duration = 6200 if car in (CAR.HONDA_CIVIC, CAR.HONDA_CIVIC_BOSCH, CAR.ACURA_ILX) else 1600
  for tick in range(duration):
    drive_state(ci.CS, tick)
    cc = command(tick).as_reader()
    now = tick * 10_000_000
    actual = ci.CC.update(cc, structs.CarControlSP(), ci.CS, now)[1]
    expected = oracle.update(cc, structs.CarControlSP(), ci.CS, now)[1]
    assert state(ci.CC) == state(oracle), (car, interceptor, tick)
    assert longitudinal_packets(ci.CC, actual) == longitudinal_packets(oracle, expected), (car, tick)
    decoder_a.update([(now, actual)])
    decoder_b.update([(now, expected)])
    if not ci.CP.flags & HondaFlags.BOSCH and tick % 10 == 0:
      # Custom HUD/CMBS display fields deliberately remain host-owned. The
      # propulsion fields and launch/rail bit must be donor-identical.
      for field in ("PCM_SPEED", "PCM_GAS", "SET_ME_X01"):
        assert decoder_a.vl["ACC_HUD"][field] == decoder_b.vl["ACC_HUD"][field], (car, tick, field)
  assert oracle.param_writer.written
  assert config.honda.provider.persisted
  actual_persisted = [{STATE_KEYS[key]: value for key, value in snapshot.items()} for snapshot in config.honda.provider.persisted]
  assert actual_persisted == oracle.param_writer.written


@pytest.mark.parametrize("car,interceptor", [(CAR.HONDA_CIVIC, False), (CAR.HONDA_CIVIC_BOSCH, False), (CAR.ACURA_ILX, True)])
def test_hostile_custom_settings_and_mid_drive_toggle_cannot_change_mvl(car, interceptor):
  normal, config, _ = build(car, interceptor)
  hostile, bad_config, _ = build(car, interceptor, hostile=True)
  assert normal.CC.nrdr.learner is hostile.CC.nrdr.learner is None
  assert not hostile.CC.civic_pcm and not hostile.CC.ecu_matched_pcm
  assert hostile.CC.nidec_wind_brake
  sp = structs.CarControlSP(civicPcmEnabled=True, civicPcmReferenceSpeed=0.1, civicPcmReferenceMonoTime=1,
                           pcmEngineBrakeAllowed=True, pcmEngineBrakeRequest=True, pcmEngineBrakeMonoTime=1)
  for tick in range(1000):
    drive_state(normal.CS, tick)
    drive_state(hostile.CS, tick)
    cc = command(tick).as_reader()
    if tick == 400:
      config.honda.provider.live_tuning = replace(config.honda.provider.live_tuning, live_learning_gas=False)
      bad_config.honda.provider.live_tuning = replace(bad_config.honda.provider.live_tuning, live_learning_gas=True)
    now = tick * 10_000_000
    a = normal.CC.update(cc, structs.CarControlSP(), normal.CS, now)
    b = hostile.CC.update(cc, sp, hostile.CS, now)
    assert a[1] == b[1], tick
    assert state(normal.CC) == state(hostile.CC), tick
    assert normal.CC.nrdr.live_tuning().live_learning_gas
  assert config.honda.provider.persisted == bad_config.honda.provider.persisted


@pytest.mark.parametrize("car", list(CAR))
def test_all_honda_startup_flags_and_safety_are_isolated(car):
  for interceptor in (False, True) if car not in HONDA_BOSCH else (False,):
    legacy, _, _ = build(car, interceptor, mvl=False)
    ci, config, fp = build(car, interceptor, hostile=True)
    assert ci.CP.flags & HondaFlags.MVL_LONGITUDINAL
    assert not ci.CP.flags & (HondaFlags.NIDEC_PCM_ECU_MATCHED | HondaFlags.NIDEC_PCM_EXPERIMENTAL)
    assert ci.CC.mvl_longitudinal
    assert [s.to_dict() for s in ci.CP.safetyConfigs] == [s.to_dict() for s in legacy.CP.safetyConfigs]
    assert ci.CP_SP.safetyParam == legacy.CP_SP.safetyParam
    assert ci.CP.lateralTuning.to_dict() == legacy.CP.lateralTuning.to_dict()
    assert ci.CP.lateralParams.to_dict() == legacy.CP.lateralParams.to_dict()
    with pytest.raises(FrozenInstanceError):
      config.honda.mvl_longitudinal = False
    ci.CP_SP.flags |= HondaFlagsSP.STOCK_LONGITUDINAL
    CarInterface._get_params_sp(ci.CP, ci.CP_SP, car, fp, [], True, False, False)
    assert not ci.CP.flags & HondaFlags.MVL_LONGITUDINAL
  stock, _, _ = build(car, stock=True)
  assert not stock.CP.flags & HondaFlags.MVL_LONGITUDINAL
  if car in HONDA_BOSCH:
    stock, _, _ = build(car, alpha=False)
    assert not stock.CP.flags & HondaFlags.MVL_LONGITUDINAL


@pytest.mark.parametrize("car,interceptor", [(CAR.HONDA_CIVIC, False), (CAR.HONDA_CIVIC_BOSCH, False), (CAR.ACURA_ILX, True)])
def test_interface_accel_limits_match_frozen_donor(donor, car, interceptor):
  _, donor_interface, _ = donor
  ci, _, _ = build(car, interceptor, hostile=True)
  for speed in (0., 5., 20., 28., 28.1, 29.8, 30., 35.):
    assert CarInterface.get_pid_accel_limits(ci.CP, ci.CP_SP, speed, 30.) == donor_interface.get_pid_accel_limits(ci.CP, ci.CP_SP, speed, 30.)


def test_legacy_engine_fields_are_inert_in_both_modes():
  for mvl in (False, True):
    plain, _, _ = build(mvl=mvl)
    retired, _, _ = build(mvl=mvl)
    for tick in range(300):
      cc = command(tick).as_reader()
      drive_state(plain.CS, tick)
      drive_state(retired.CS, tick)
      now = tick * 10_000_000
      sp = structs.CarControlSP(pcmEngineBrakeAllowed=True, pcmEngineBrakeRequest=True, pcmEngineBrakeMonoTime=now)
      assert plain.CC.update(cc, structs.CarControlSP(), plain.CS, now)[1] == retired.CC.update(cc, sp, retired.CS, now)[1]
    assert not hasattr(plain.CC, "engine_brake_fade")


def test_saved_values_are_loaded_without_reset_or_legacy_learner():
  saved = {"gas_factor": 2.3, "wind_factor": 1.7, "gas_alpha": .17, "gas_alpha_low": .13, "speed_factor": 7.,
           "speed_factor_low": 5., "launch_gas": 125., "feedforward": .08, "brake_pid": .7}
  original = dict(saved)
  for car, interceptor in ((CAR.HONDA_CIVIC, False), (CAR.HONDA_CIVIC_BOSCH, False), (CAR.ACURA_ILX, True)):
    ci, config, _ = build(car, interceptor, saved=saved)
    assert ci.CC.gasfactor == saved["gas_factor"]
    assert ci.CC.gasalpha == saved["gas_alpha"]
    assert ci.CC.gas_alphas["low"] == saved["gas_alpha_low"]
    assert ci.CC.windfactor == saved["wind_factor"]
    assert ci.CC.speed_factors["high"] == saved["speed_factor"]
    assert ci.CC.speed_factors["low"] == saved["speed_factor_low"]
    assert ci.CC.gas_launch == saved["launch_gas"]
    assert ci.CC.average_factor == saved["feedforward"]
    assert ci.CC.brake_pid_factor_non_lowspeed == saved["brake_pid"]
    assert not config.honda.provider.persisted
    assert saved == original


@pytest.mark.parametrize("car", [CAR.HONDA_CIVIC_BOSCH, CAR.HONDA_CIVIC_2022])
def test_exact_pin_does_not_import_newer_bosch_stopping_guard(donor, car):
  module, _, _ = donor
  ci, _, _ = build(car)
  oracle = module.CarController(DBC[car], ci.CP, ci.CP_SP)
  ci.CS.out.vEgo = 10.
  cc = command(0)
  cc.actuators.accel = .25
  ci.CC.update(cc.as_reader(), structs.CarControlSP(), ci.CS, 0)
  oracle.update(cc.as_reader(), structs.CarControlSP(), ci.CS, 0)
  ci.CC.frame = oracle.frame = 2
  cc.actuators.accel = -.1
  cc.actuators.longControlState = "stopping"
  a = ci.CC.update(cc.as_reader(), structs.CarControlSP(), ci.CS, 20_000_000)[1]
  b = oracle.update(cc.as_reader(), structs.CarControlSP(), ci.CS, 20_000_000)[1]
  assert ci.CC.accel > 0
  assert ci.CC.stopping_counter == oracle.stopping_counter == 1
  assert longitudinal_packets(ci.CC, a) == longitudinal_packets(oracle, b)


def test_qualified_clarity_hardware_hold_and_override_protections():
  ci, _, _ = build(CAR.HONDA_CLARITY, True, hostile=True, clarity_bench=True)
  assert ci.CC.keep_pcm_acc
  ci.CS.out.vEgo = 0.
  ci.CS.out.standstill = True
  cc = command(0)
  cc.actuators.accel = 0.
  cc.actuators.longControlState = "stopping"
  for tick in range(60):
    ci.CC.update(cc.as_reader(), structs.CarControlSP(), ci.CS, tick * 10_000_000)
  assert ci.CC.clarity_hold.latched
  assert ci.CC.apply_brake_last == 97
  assert ci.CC.gas == 0.
  for reason in ("gas", "brake", "cancel", "inactive", "aeb"):
    ci.CS.out.gasPressed = reason == "gas"
    ci.CS.out.brakePressed = reason == "brake"
    ci.CS.out.stockAeb = reason == "aeb"
    cc.longActive = reason != "inactive"
    cc.cruiseControl.cancel = reason == "cancel"
    cc.actuators.accel = .5
    cc.actuators.longControlState = "pid"
    for tick in range(60, 80):
      ci.CC.update(cc.as_reader(), structs.CarControlSP(), ci.CS, tick * 10_000_000)
    assert ci.CC.gas == 0., reason
    if reason != "aeb":
      assert ci.CC.apply_brake_last == 0, reason


@pytest.mark.parametrize("car,interceptor,mode", [
  (CAR.HONDA_CIVIC, False, 0), (CAR.HONDA_CIVIC, False, 1), (CAR.HONDA_CIVIC, False, 2),
  (CAR.HONDA_CLARITY, False, 0), (CAR.ACURA_ILX, True, 0), (CAR.HONDA_CLARITY, True, 0),
  (CAR.HONDA_CIVIC_BOSCH, False, 0), (CAR.HONDA_CIVIC_2022, False, 0),
])
@pytest.mark.parametrize("learning", [False, True])
def test_off_matches_frozen_pre_engine_controller(car, interceptor, mode, learning):
  from opendbc.car.honda.tests.test_civic_pcm import interface
  frozen = load_reference("legacy_carcontroller").CarController
  ci, config = interface(car, interceptor=interceptor, pcm_mode=mode, learning=learning)
  oracle = frozen(DBC[car], ci.CP, ci.CP_SP, config.honda)
  for tick in range(800):
    drive_state(ci.CS, tick)
    cc = command(tick).as_reader()
    now = tick * 10_000_000
    sp = structs.CarControlSP(civicPcmEnabled=mode == 2, civicPcmReferenceSpeed=25., civicPcmReferenceMonoTime=now)
    a = ci.CC.update(cc, sp, ci.CS, now)
    b = oracle.update(cc, sp, ci.CS, now)
    assert a[0].to_dict() == b[0].to_dict(), (car, mode, tick)
    assert a[1] == b[1], (car, mode, tick)
