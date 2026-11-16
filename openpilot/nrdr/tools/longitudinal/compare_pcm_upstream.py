#!/usr/bin/env python3
"""Offline, open-loop packet oracle for Nidec PCM Off (no device or Params I/O).

Requires this checkout's opendbc dependencies. Example, from the repository root:
  python -B openpilot/nrdr/tools/longitudinal/compare_pcm_upstream.py --upstream-repo PATH

The default reference is MVL root 376c44b573's exact opendbc pin 3fec9a418a.
Sources are read with git show, never checked out or
rewritten. Upstream controller, Honda packing, helpers, limits and EPS adapter
execute unchanged; only Params and its background writer are memory substitutes.
Candidate CarParams/CarState, schema, parser and DBC encoding are shared.

Exit 1 means differences, 0 means sampled parity, 2 means setup failed. This is
NOT a closed-loop simulation, road/safety validation, or root planner oracle.
Upstream has no learning-off switch: those rows intentionally quantify the
candidate switch against untouched upstream, not a modified reference.
For governor-transition cache coverage, additionally run --learning on --seed
high --ticks 5000 --scenarios brake_at_governor swept_governor.
"""
import argparse
import ast
import builtins
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType, SimpleNamespace

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
UPSTREAM_REF = "3fec9a418a659de31d7b1f494193161697a35071"
FIELDS = {"ACC_HUD": ("PCM_SPEED", "PCM_GAS", "SET_ME_X01", "CRUISE_SPEED", "ACC_ON"),
          "BRAKE_COMMAND": ("COMPUTER_BRAKE", "COMPUTER_BRAKE_HYBRID", "COMPUTER_BRAKE_REQUEST",
                            "BRAKE_PUMP_REQUEST", "BRAKE_PUMP_REQUEST_HYBRID", "BRAKE_LIGHTS",
                            "AEB_REQ_1", "AEB_REQ_2", "CRUISE_CANCEL_CMD", "CRUISE_OVERRIDE")}
STATE = ("gas_factors", "gas_alphas", "speed_factors", "speed_alphas", "windfactor", "average_factor",
         "car_gas_per_pcm_gas", "sat_accel", "dv_launch", "gas_launch", "dv_break", "creep_factor",
         "brake_pid_factor_non_lowspeed", "prior_gas_average", "average_factor_sens", "new_accel",
         "windfactor_before_brake", "windfactor_before_gasmax")


def git(repo, *args):
  return subprocess.check_output(["git", "-C", str(repo), *args], text=True, encoding="utf-8")


class MemoryWriter:
  def __init__(self):
    self.snapshots = []

  def put_many(self, values):
    self.snapshots.append(dict(values))


def reference(repo, ref, seed):
  """Private module imports avoid replacing candidate modules in sys.modules."""
  manifest, replacements = {}, {}
  params = ModuleType("oracle_memory_params")
  params.Params = lambda: SimpleNamespace(get=lambda key: seed.get(key))
  replacements["openpilot.common.params"] = params

  def imports(name, globals_=None, locals_=None, fromlist=(), level=0):
    if level == 0 and name in replacements:
      return replacements[name]
    if level == 0 and name == "opendbc.car.honda" and "hondacan" in fromlist:
      return SimpleNamespace(hondacan=replacements["opendbc.car.honda.hondacan"])
    return builtins.__import__(name, globals_, locals_, fromlist, level)

  def load(name):
    path = name.replace(".", "/") + ".py"
    source = git(repo, "show", f"{ref}:{path}")
    manifest[path] = hashlib.sha256(source.encode()).hexdigest()
    module = ModuleType("pcm_oracle_" + name.replace(".", "_"))
    module.__file__ = f"{ref}:{path}"
    module.__dict__["__builtins__"] = dict(vars(builtins), __import__=imports)
    sys.modules[module.__name__] = module  # dataclass introspection, not candidate imports
    if name == "opendbc.car.honda.values":
      # Platform registry schemas differ. Keep the exact upstream limits class,
      # resolving its car/flag names against the candidate's shared CP schema.
      from opendbc.car.honda import values
      module.__dict__.update({key: value for key, value in vars(values).items() if not key.startswith("__")})
      node = next(node for node in ast.parse(source).body if isinstance(node, ast.ClassDef) and node.name == "CarControllerParams")
      code = ast.Module(body=[node], type_ignores=[])
    else:
      code = source
    exec(compile(code, module.__file__, "exec"), module.__dict__)
    replacements[name] = module
    return module

  for name in ("opendbc.car.honda.values", "opendbc.car.honda.nidec_long_helpers",
               "opendbc.car.honda.hondacan", "opendbc.sunnypilot.car.honda.eps_mod"):
    load(name)
  module = load("opendbc.car.honda.carcontroller")
  module.HondaParamWriter = MemoryWriter
  return module, manifest


def synthetic_input(case, tick):
  """Identical recorded-like inputs, NOT a plant responding to either output."""
  speed, ego_accel, request, cruise, state = 20., 0., .6, 32., "pid"
  active, gas_pressed, brake_pressed, aeb = True, False, False, False
  if case == "steps":
    request = (.6, .15, -.3, -1.5, .8)[min(tick // 160, 4)]
  elif case == "near_set":
    speed, cruise, request = 26., 26.8, .5  # 58 mph, inside PCM governor margin
  elif case == "coast_floor":
    request, ego_accel = -.8, -.2
  elif case == "stopping_launch":
    speed = max(0., 2. - tick * .01) if tick < 350 else min(5., (tick - 350) * .025)
    request = -1.2 if tick < 350 else .8
    ego_accel = -.3 if tick < 200 else 0.
    state = "stopping" if tick < 350 else "pid"
  elif case == "override_release":
    gas_pressed = 100 <= tick < 220
    brake_pressed = 350 <= tick < 400
    aeb = 500 <= tick < 550
    active = not (gas_pressed or brake_pressed or 650 <= tick < 700)
  elif case in ("brake_at_governor", "swept_governor"):
    # Deliberate open-loop boundary step, not a physically simulated trajectory.
    # Keep set speed unchanged to exclude NRDR's wall-clock HUD speed flashing.
    speed, cruise = (24. if tick < 300 else 31.), 32.
    request = (1. if tick < 300 else
               -.4 if case == "brake_at_governor" else -.05 - .0002 * ((tick - 300) % 1500))
  else:
    raise ValueError(case)
  return {"speed": speed, "ego_accel": ego_accel, "request": request, "cruise": cruise, "state": state,
          "active": active, "gas_pressed": gas_pressed, "brake_pressed": brake_pressed, "aeb": aeb}


def state_of(controller):
  return deepcopy({name: getattr(controller, name) for name in STATE})


def make_pair(car_name, learning, seed, donor):
  from opendbc.car.honda.interface import CarInterface
  from opendbc.car.honda.values import CAR, HondaFlags
  from opendbc.sunnypilot.car.tests.runtime_config import make_test_car_config
  from openpilot.nrdr.car.mvl_state import MVL_STATE_KEYS

  interfaces = []
  for _ in range(2):
    config = make_test_car_config()
    config = replace(config, honda=replace(config.honda, nidec_pcm_mode=0, nidec_wind_brake=True))
    provider = config.honda.provider
    provider.live_tuning = replace(provider.live_tuning, live_learning_gas=learning, ecu_matched_long=False,
                                   clear_dash_faults=False, alt_dashboard_speed=0, alt_dashboard_distance=0)
    provider.load_mvl_param = lambda key, default: float(seed.get(MVL_STATE_KEYS[key], default))
    provider.load_longitudinal_factors = lambda car: (seed.get("HondaGasFactorParams", 1.), seed.get("HondaWindFactorParams", 1.))
    provider.load_gas_alpha = lambda car: seed.get("HondaGasAlphaParams", 0.)
    fingerprint = {bus: {} for bus in range(7)}
    car = CAR[car_name]
    cp = CarInterface.get_params(car, fingerprint, [], alpha_long=True, is_release=False, docs=False, interface_config=config)
    sp = CarInterface.get_params_sp(cp, car, fingerprint, [], alpha_long=True, is_release_sp=False, docs=False)
    assert cp.openpilotLongitudinalControl and cp.flags & HondaFlags.NIDEC and not sp.enableGasInterceptor
    assert not cp.flags & (HondaFlags.NIDEC_PCM_EXPERIMENTAL | HondaFlags.NIDEC_PCM_ECU_MATCHED)
    ci = CarInterface(cp, sp, config)
    ci.update([])
    interfaces.append(ci)
  candidate, upstream = interfaces
  assert candidate.CP.to_dict() == upstream.CP.to_dict()
  assert vars(candidate.CP_SP) == vars(upstream.CP_SP)
  upstream.CC = donor.CarController({bus: parser.dbc_name for bus, parser in upstream.can_parsers.items()},
                                    upstream.CP, upstream.CP_SP)
  assert state_of(candidate.CC) == state_of(upstream.CC), "unequal initial learner/model state"
  return candidate, upstream


def run_case(car, case, learning, seed, donor, ticks, *, self_check=False):
  from opendbc.can import CANParser
  from opendbc.car import Bus, structs

  candidate, upstream = make_pair(car, learning, seed, donor)
  if self_check:
    candidate.CC = donor.CarController({bus: p.dbc_name for bus, p in candidate.can_parsers.items()},
                                       candidate.CP, candidate.CP_SP)
  parsers = [CANParser(ci.can_parsers[Bus.pt].dbc_name, [(name, 0) for name in FIELDS], ci.CC.CAN.pt)
             for ci in (candidate, upstream)]
  first, counts, maximum = {}, {}, {}
  packets = 0
  for tick in range(ticks):
    data = synthetic_input(case, tick)
    decoded = []
    for ci, parser in zip((candidate, upstream), parsers, strict=True):
      cs = ci.CS
      cs.out.vEgo, cs.out.aEgo = data["speed"], data["ego_accel"]
      cs.out.vEgoCluster = data["speed"]
      cs.out.standstill = data["speed"] <= .01
      cs.out.cruiseState.speed, cs.out.cruiseState.available = data["cruise"], True
      cs.out.gasPressed, cs.out.brakePressed, cs.out.stockAeb = data["gas_pressed"], data["brake_pressed"], data["aeb"]
      cs.out.canValid = True
      cs.steer_control_active, cs.engine_rpm = True, 1500
      cs.car_gas_available, cs.car_gas = True, 12. if data["gas_pressed"] else 6.
      cc = structs.CarControl(enabled=True, longActive=data["active"])
      cc.actuators.accel = data["request"]
      cc.actuators.longControlState = getattr(structs.CarControl.Actuators.LongControlState, data["state"])
      cc.hudControl.setSpeed, cc.hudControl.speedVisible = data["cruise"], True
      cc.orientationNED = [0., 0., 0.]
      _, messages = ci.CC.update(cc.as_reader(), structs.CarControlSP(), cs, (tick + 1) * 10_000_000)
      result = {}
      for address, payload, bus in messages:
        if address not in parser.addresses or bus != parser.bus:
          continue
        updated = parser.update([((tick + 1) * 10_000_000, [(address, payload, bus)])])
        assert address in updated, f"decoder rejected {address:#x}"
        name = parser.dbc.addr_to_msg[address].name
        if name in result:
          raise AssertionError(f"duplicate packet {name}")
        result[name] = {field: float(parser.vl[name][field]) for field in FIELDS[name]}
      decoded.append(result)
    packets += len(decoded[0])
    for name in FIELDS:
      left, right = decoded[0].get(name), decoded[1].get(name)
      if left is None and right is None:
        continue
      fields = FIELDS[name] if left is not None and right is not None else ("packet_presence",)
      for field in fields:
        a, b = (left[field], right[field]) if field != "packet_presence" else (left is not None, right is not None)
        if a == b:
          continue
        key = f"{name}.{field}"
        counts[key] = counts.get(key, 0) + 1
        maximum[key] = max(maximum.get(key, 0.), abs(a - b))
        first.setdefault(key, {"tick": tick, "time_s": tick / 100., "candidate": a, "upstream": b, "input": data})
  before, after = state_of(candidate.CC), state_of(upstream.CC)
  state_diff = {key: {"candidate": before[key], "upstream": after[key]} for key in STATE if before[key] != after[key]}
  return {"car": car, "scenario": case, "learning": learning, "seed": seed, "ticks": ticks, "compared_packets": packets,
          "mismatch_counts": counts, "max_abs_delta": maximum, "first_mismatches": first, "final_state_differences": state_diff}


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--upstream-repo", type=Path, required=True, help="local opendbc Git repository containing the pin")
  parser.add_argument("--upstream-ref", default=UPSTREAM_REF)
  parser.add_argument("--cars", nargs="+", default=["HONDA_CIVIC", "HONDA_PILOT", "HONDA_CLARITY"])
  parser.add_argument("--scenarios", nargs="+", default=["steps", "near_set", "coast_floor", "stopping_launch", "override_release"])
  parser.add_argument("--ticks", type=int, default=800)
  parser.add_argument("--learning", choices=("on", "off", "both"), default="both")
  parser.add_argument("--seed", choices=("fresh", "warm", "high", "all"), default="all")
  args = parser.parse_args()
  if args.ticks < 1:
    parser.error("--ticks must be positive")
  sys.path[:0] = [str(ROOT / "opendbc_repo"), str(ROOT)]
  candidate_path = ROOT / "opendbc_repo/opendbc/car/honda/carcontroller.py"
  candidate_hash = hashlib.sha256(candidate_path.read_bytes()).hexdigest()
  ref = git(args.upstream_repo, "rev-parse", args.upstream_ref + "^{commit}").strip()
  profiles = {"fresh": {}, "warm": {"HondaFeedForwardParams": .02, "HondaSpeedFactorParams": 4.,
                                    "HondaSpeedFactorLowParams": 4., "HondaWindFactorParams": 1.4},
              "high": {"HondaSpeedFactorParams": 20., "HondaSpeedFactorLowParams": 20.}}
  results, manifest = [], {}
  donor, _ = reference(args.upstream_repo, ref, {})
  for case in args.scenarios:
    check = run_case(args.cars[0], case, True, {}, donor, args.ticks, self_check=True)
    assert not check["mismatch_counts"] and not check["final_state_differences"], "upstream/upstream harness self-check failed"
  for profile, seed in profiles.items():
    if args.seed not in ("all", profile):
      continue
    donor, manifest = reference(args.upstream_repo, ref, seed)
    for car in args.cars:
      for learning in ([True, False] if args.learning == "both" else [args.learning == "on"]):
        for case in args.scenarios:
          result = run_case(car, case, learning, seed, donor, args.ticks)
          result["profile"] = profile
          results.append(result)
  changed_during_run = candidate_hash != hashlib.sha256(candidate_path.read_bytes()).hexdigest()
  mismatches = sum(bool(row["mismatch_counts"]) for row in results)
  print(json.dumps({"upstream_ref": ref, "upstream_source_sha256": manifest, "candidate_controller_sha256": candidate_hash,
                    "upstream_self_check_passed": True, "pcm_speed_units": "km/h", "gas_brake_units": "decoded CAN counts",
                    "candidate_changed_during_run": changed_during_run, "packet_mismatch_cases": mismatches,
                    "total_cases": len(results), "results": results}, indent=2))
  return 2 if changed_during_run else int(bool(mismatches or any(r["final_state_differences"] for r in results)))


if __name__ == "__main__":
  try:
    raise SystemExit(main())
  except Exception as error:
    print(f"PCM oracle setup/execution failure: {type(error).__name__}: {error}", file=sys.stderr)
    raise SystemExit(2) from error
