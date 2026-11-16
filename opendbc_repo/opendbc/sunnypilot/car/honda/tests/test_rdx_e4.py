"""RDX rack admission and signed E4 transport; all CAN frames stay in memory."""
from dataclasses import replace

import pytest

from opendbc.car import gen_empty_fingerprint, structs
from opendbc.car.fw_versions import match_fw_to_car_exact
from opendbc.car.honda.fingerprints import FW_VERSIONS
from opendbc.car.honda.interface import CarInterface
from opendbc.car.honda.values import CAR
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from opendbc.sunnypilot.car.interfaces import setup_interfaces
from opendbc.sunnypilot.car.tests.runtime_config import make_test_car_config


PTM = b"39990-TJB,A220\x00\x00"
STOCK = b"39990-TJB-A220\x00\x00"
CHASSIS = [(CAR.ACURA_RDX_3G, 4095), (CAR.ACURA_RDX_3G_MMR, 4076)]


def reply(version=PTM, **fields):
  return structs.CarParams.CarFw(**({"ecu": "eps", "address": 0x18DA30F1, "fwVersion": version} | fields))


def params(car, replies, alpha_long=False, *, bench=False, host=True, can_recv=None, can_send=None, inherited_limit=None):
  cfg = make_test_car_config()
  if bench is not False:
    cfg = replace(cfg, honda=replace(cfg.honda, rdx_tjb_a220_transport_bench=bench))
  cfg.honda.provider.live_tuning = replace(cfg.honda.provider.live_tuning, override_fade_up_s=0.0)
  fp = gen_empty_fingerprint()
  cp = CarInterface.get_params(car, fp, replies, alpha_long=alpha_long, is_release=False, docs=False, interface_config=cfg if host else None)
  cp.carFw = replies  # get_car attaches the diagnostic replies before setup_interfaces
  sp = CarInterface.get_params_sp(cp, car, fp, replies, alpha_long=alpha_long, is_release_sp=False, docs=False)
  if inherited_limit is not None:
    cp.lateralParams.torqueBP = cp.lateralParams.torqueV = [0, inherited_limit]
  setup_interfaces(CarInterface, cp, sp, cfg if host else None, can_recv, can_send)
  return cp, sp, cfg


@pytest.mark.parametrize("car,stock_max", CHASSIS)
@pytest.mark.parametrize("replies", [
  pytest.param([], id="missing"),
  pytest.param([reply(STOCK)], id="stock-a220"),
  pytest.param([reply(b"39990-TJB,A130\x00\x00")], id="unknown-mod"),
  pytest.param([reply(PTM.rstrip(b"\x00"))], id="missing-padding"),
  pytest.param([reply(PTM + b"\x00")], id="extra-padding"),
  pytest.param([reply(ecu="fwdCamera")], id="wrong-ecu"),
  pytest.param([reply(address=0x18DAB5F1)], id="wrong-address"),
  pytest.param([reply(subAddress=1)], id="wrong-subaddress"),
  pytest.param([reply(logging=True)], id="logging-only"),
  pytest.param([reply(STOCK), reply(b"other,version")], id="split-evidence"),
  pytest.param([reply(), reply(STOCK)], id="conflicting-stock"),
  pytest.param([reply(b"unknown"), reply()], id="conflicting-unknown"),
])
def test_unverified_rack_keeps_stock_map(car, stock_max, replies):
  cp, _, _ = params(car, replies, bench=True)
  assert list(cp.lateralParams.torqueBP) == list(cp.lateralParams.torqueV) == [0, stock_max]


def test_exact_reply_on_older_rdx_keeps_stock_map():
  cp, _, _ = params(CAR.ACURA_RDX, [reply()], bench=True)
  assert list(cp.lateralParams.torqueBP) == list(cp.lateralParams.torqueV) == [0, 1000]


def no_io(*args):
  pytest.fail("no CAN I/O is allowed")


@pytest.mark.parametrize("car,stock_max", CHASSIS)
@pytest.mark.parametrize("options", [
  {"host": False}, {"bench": "false"}, {"bench": 1}, {"bench": True, "can_recv": no_io},
  {"bench": True, "can_send": no_io}, {"bench": True, "can_recv": no_io, "can_send": no_io},
])
def test_missing_host_malformed_opt_in_or_live_callbacks_keep_stock_map(car, stock_max, options):
  cp, _, _ = params(car, [reply()], **options)
  assert list(cp.lateralParams.torqueBP) == list(cp.lateralParams.torqueV) == [0, stock_max]


def test_unconfirmed_setup_preserves_an_incoming_3840_mmr_map_on_wire():
  # James' MMR baseline uses 3840; the NRDR base uses 4076. Default setup must not hard-code either fallback.
  ci = CarInterface(*params(CAR.ACURA_RDX_3G_MMR, [reply()], inherited_limit=3840))
  assert ci.CP.lateralTuning.which() == "pid"
  assert list(ci.CP.lateralParams.torqueBP) == list(ci.CP.lateralParams.torqueV) == [0, 3840]
  ci.update([])
  ci.CS.out.vEgo = 25.0
  ci.CS.steer_control_active = True
  cc = structs.CarControl(enabled=True, latActive=True)
  cc.actuators.torque = 0.5
  out, frames = ci.apply(cc.as_reader(), structs.CarControlSP(), 0)
  (wire,) = [int.from_bytes(d[:2], "big", signed=True) for a, d, _ in frames if a == 0xE4]
  assert wire == out.torqueOutputCan == -1920


@pytest.mark.parametrize("car", [car for car, _ in CHASSIS])
def test_rack_requires_an_independent_exact_chassis_match(car):
  ep = (0x18DA30F1, None)
  live = {key[1:]: {versions[0]} for key, versions in FW_VERSIONS[car].items()}
  assert match_fw_to_car_exact(live, "honda") == {car}  # stock fingerprint
  live[ep] = {PTM}
  assert match_fw_to_car_exact(live, "honda") == {car}
  assert not match_fw_to_car_exact({ep: {PTM}}, "honda")
  if car == CAR.ACURA_RDX_3G:
    live[ep] = {b"39990-TJB,A130\x00\x00"}
    assert car not in match_fw_to_car_exact(live, "honda")
  else:
    # MMR identifies from its original camera/radar; adding a new required EPS record would break stock cars.
    assert (structs.CarParams.Ecu.eps, *ep) not in FW_VERSIONS[car]


@pytest.mark.parametrize("car,stock_max", CHASSIS)
@pytest.mark.parametrize("alpha_long", [False, True])
@pytest.mark.parametrize("bench", [False, True], ids=["production-pif", "bench"])
def test_exact_rack_changes_only_mapping_and_existing_modified_flag(car, stock_max, alpha_long, bench):
  stock_cp, stock_sp, _ = params(car, [reply(STOCK)], alpha_long)
  cp, sp, _ = params(car, [reply(), reply(b"serial", logging=True), reply(), reply(STOCK, ecu="fwdCamera")], alpha_long, bench=bench)
  expected = stock_cp.to_dict()
  expected["carFw"] = cp.to_dict()["carFw"]
  assert expected["lateralParams"] == {"torqueBP": [0, stock_max], "torqueV": [0, stock_max]}
  if bench:
    expected["lateralParams"] = {"torqueBP": [0, 4096], "torqueV": [0, 4096]}
  # Includes lateral tuning, safety configs, minSteerSpeed, longitudinal and standstill policy.
  assert cp.to_dict() == expected
  assert sp == replace(stock_sp, flags=stock_sp.flags | HondaFlagsSP.EPS_MODIFIED)


@pytest.mark.parametrize("car,stock_max", CHASSIS)
@pytest.mark.parametrize("alpha_long", [False, True])
@pytest.mark.parametrize("bench", [False, True], ids=["production-pif", "bench"])
def test_controller_packs_signed_e4_and_keeps_inactive_heartbeat(car, stock_max, alpha_long, bench):
  def make_interface(version):
    ci = CarInterface(*params(car, [reply(version)], alpha_long, bench=bench))
    ci.update([])
    ci.CS.out.vEgo = 25.0
    ci.CS.out.standstill = False
    ci.CS.steer_control_active = True
    return ci

  def apply(controller, limit, tick, enabled, active, output):
    cc = structs.CarControl(enabled=enabled, latActive=active)
    cc.actuators.torque = output
    out, frames = controller.apply(cc.as_reader(), structs.CarControlSP(), tick * 10_000_000)
    (bus, data), = [(b, d) for a, d, b in frames if a == 0xE4]
    assert bus == int(controller.CP.openpilotLongitudinalControl)
    assert bool(data[2] & 0x80) == active  # DBC STEER_TORQUE_REQUEST
    assert int.from_bytes(data[:2], "big", signed=True) == out.torqueOutputCan == (int(-output * limit) if active else 0)
    return frames

  ci, stock = make_interface(PTM), make_interface(STOCK)
  cases = [(True, True, 1.0), (True, True, -1.0), (True, True, 0.5), (True, False, 1.0), (False, False, -1.0)]
  for tick, (enabled, active, output) in enumerate(cases):
    mod_frames = apply(ci, 4096 if bench else stock_max, tick, enabled, active, output)
    stock_frames = apply(stock, stock_max, tick, enabled, active, output)
    assert [(a, b) for a, _, b in mod_frames] == [(a, b) for a, _, b in stock_frames]
    if not bench or not active:
      assert mod_frames == stock_frames
