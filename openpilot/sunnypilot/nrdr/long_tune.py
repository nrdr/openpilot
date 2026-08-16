#!/usr/bin/env python3
import argparse
import json
import math
import os


NRDR_LONG_TUNE_PATH = "/data/nrdr_long_tune.json"
PERSONALITIES = ("aggressive", "standard", "relaxed")
LOW_SPEED_JERK_BP = (2.0, 5.0)

SCALAR_FIELDS = {
  "comfort_brake": (2.5, 2.0, 3.0),
  "stop_distance": (6.0, 4.5, 7.5),
  "low_speed_jerk_scale": (1.0, 1.0, 2.0),
}
LEAD_FIELDS = {
  "m1_anchor": (1.0, 0.0, 1.0),
  "m1_alead_escape": (1.0, 0.5, 2.0),
  "m2_w_max": (0.0, 0.0, 1.0),
  "m2_alead_deadband": (0.5, 0.3, 1.0),
  "m2_drel_gate": (40.0, 20.0, 80.0),
  "m3_b_eff_max": (2.5, 2.5, 4.5),
  "m3_alead_gate": (-0.5, -2.0, -0.3),
}
STOPPING_FIELDS = {
  "l2_enable": (1.0, 0.0, 1.0),
  "hold_accel": (-0.6, -1.0, -0.3),
  "phase_switch_v": (0.15, 0.05, 0.5),
  "proximity_scale_m": (8.0, 2.0, 20.0),
  "pitch_margin": (1.0, 0.0, 2.0),
}

CRUISE_SCALE_COUNT = 4
DEFAULT_CRUISE_SCALE = (1.0,) * CRUISE_SCALE_COUNT
CRUISE_SCALE_RANGE = (0.5, 1.5)
FOLLOW_OFFSET_RANGE = (-0.35, 0.5)
JERK_FACTOR_RANGE = (0.2, 3.0)
JERK_FACTOR_KEYS = ("a_change", "j_ego")


def _clamp_float(value, bounds) -> float:
  value = float(value)
  if not math.isfinite(value):
    raise ValueError("value must be finite")
  return min(max(value, bounds[0]), bounds[1])


def _field_defaults(fields) -> dict[str, float]:
  return {name: spec[0] for name, spec in fields.items()}


def _read_numeric_fields(data, fields, target, prefix: str, rejected: list[str]) -> None:
  for name, (_, low, high) in fields.items():
    if name not in data:
      continue
    try:
      target[name] = _clamp_float(data[name], (low, high))
    except (TypeError, ValueError):
      rejected.append(f"{prefix}{name}")


class LongTune:
  REFRESH_INTERVAL = 20

  def __init__(self, path=NRDR_LONG_TUNE_PATH, log_fn=None):
    self._path = path
    self._log_fn = log_fn
    self._frame = 0
    self._file_signature = ()
    self._last_log = None
    self._set_defaults()

  def _set_defaults(self) -> None:
    for name, (default, _, _) in SCALAR_FIELDS.items():
      setattr(self, name, default)
    self.a_cruise_max_scale = DEFAULT_CRUISE_SCALE
    self.t_follow_offsets = {}
    self._jerk_overrides = {}
    self.lead_consumption = _field_defaults(LEAD_FIELDS)
    self.stopping = _field_defaults(STOPPING_FIELDS)
    self.active = False

  def t_follow_offset(self, personality_name):
    return self.t_follow_offsets.get(personality_name, 0.0)

  def jerk_factors(self, personality_name, default):
    overrides = self._jerk_overrides.get(personality_name)
    if overrides is None:
      return default
    return tuple(overrides.get(key, default[index]) for index, key in enumerate(JERK_FACTOR_KEYS))

  def refresh(self) -> None:
    if self._frame % self.REFRESH_INTERVAL == 0:
      self._check_file()
    self._frame += 1

  def _check_file(self) -> None:
    try:
      stat = os.stat(self._path)
      signature = (stat.st_mtime_ns, stat.st_size)
    except OSError:
      signature = None

    if signature == self._file_signature:
      return

    was_loaded = self._file_signature not in ((), None)
    self._file_signature = signature
    if signature is None:
      self._set_defaults()
      if was_loaded:
        self._warn("tune file removed; reverted to compiled defaults")
      return

    try:
      with open(self._path, encoding="utf-8") as tune_file:
        data = json.load(tune_file)
      if not isinstance(data, dict):
        raise ValueError("top level must be an object")
    except (OSError, ValueError) as error:
      self._set_defaults()
      self._warn(f"unreadable tune file ({error}); using compiled defaults")
      return
    self._apply(data)

  def _apply(self, data) -> None:
    self._set_defaults()
    rejected = []

    scalar_values = _field_defaults(SCALAR_FIELDS)
    _read_numeric_fields(data, SCALAR_FIELDS, scalar_values, "", rejected)
    for name, value in scalar_values.items():
      setattr(self, name, value)

    self._apply_cruise_scale(data, rejected)
    self._apply_follow_offsets(data, rejected)
    self._apply_jerk_factors(data, rejected)
    self._apply_group(data, "lead_consumption", LEAD_FIELDS, self.lead_consumption, rejected)
    self._apply_group(data, "stopping", STOPPING_FIELDS, self.stopping, rejected)

    self.active = True
    summary = self.describe()
    if rejected:
      summary += f" (rejected: {', '.join(rejected)})"
    self._warn(f"loaded {summary}")

  def _apply_cruise_scale(self, data, rejected: list[str]) -> None:
    if "a_cruise_max_scale" not in data:
      return
    try:
      values = data["a_cruise_max_scale"]
      if not isinstance(values, (list, tuple)) or len(values) != CRUISE_SCALE_COUNT:
        raise ValueError("expected four values")
      self.a_cruise_max_scale = tuple(_clamp_float(value, CRUISE_SCALE_RANGE) for value in values)
    except (TypeError, ValueError):
      rejected.append("a_cruise_max_scale")

  def _apply_follow_offsets(self, data, rejected: list[str]) -> None:
    if "t_follow_offsets" not in data:
      return
    values = data["t_follow_offsets"]
    if not isinstance(values, dict):
      rejected.append("t_follow_offsets")
      return
    for personality in PERSONALITIES:
      if personality not in values:
        continue
      try:
        self.t_follow_offsets[personality] = _clamp_float(values[personality], FOLLOW_OFFSET_RANGE)
      except (TypeError, ValueError):
        rejected.append(f"t_follow_offsets.{personality}")

  def _apply_jerk_factors(self, data, rejected: list[str]) -> None:
    if "jerk_factors" not in data:
      return
    values = data["jerk_factors"]
    if not isinstance(values, dict):
      rejected.append("jerk_factors")
      return
    for personality in PERSONALITIES:
      if personality not in values:
        continue
      personality_values = values[personality]
      if not isinstance(personality_values, dict):
        rejected.append(f"jerk_factors.{personality}")
        continue
      overrides = {}
      for key in JERK_FACTOR_KEYS:
        if key not in personality_values:
          continue
        try:
          overrides[key] = _clamp_float(personality_values[key], JERK_FACTOR_RANGE)
        except (TypeError, ValueError):
          rejected.append(f"jerk_factors.{personality}.{key}")
      if overrides:
        self._jerk_overrides[personality] = overrides

  @staticmethod
  def _apply_group(data, name: str, fields, target, rejected: list[str]) -> None:
    if name not in data:
      return
    values = data[name]
    if not isinstance(values, dict):
      rejected.append(name)
      return
    _read_numeric_fields(values, fields, target, f"{name}.", rejected)

  def describe(self) -> str:
    values = []
    for name, (default, _, _) in SCALAR_FIELDS.items():
      value = getattr(self, name)
      if value != default:
        values.append(f"{name}={value:g}")
    if self.a_cruise_max_scale != DEFAULT_CRUISE_SCALE:
      values.append(f"a_cruise_max_scale={list(self.a_cruise_max_scale)}")
    if self.t_follow_offsets:
      values.append(f"t_follow_offsets={self.t_follow_offsets}")
    if self._jerk_overrides:
      values.append(f"jerk_factors={self._jerk_overrides}")

    lead_changes = self._changed_values(self.lead_consumption, LEAD_FIELDS)
    if lead_changes:
      values.append(f"lead_consumption={lead_changes}")
    stopping_changes = self._changed_values(self.stopping, STOPPING_FIELDS)
    if stopping_changes:
      values.append(f"stopping={stopping_changes}")
    return "; ".join(values) if values else "all-defaults"

  @staticmethod
  def _changed_values(values, fields):
    return {name: values[name] for name, (default, _, _) in fields.items() if values[name] != default}

  def _warn(self, message: str) -> None:
    if self._log_fn is not None and message != self._last_log:
      self._last_log = message
      self._log_fn(f"nrdr_long_tune: {message}")


def write_tune(values, path=NRDR_LONG_TUNE_PATH) -> None:
  temporary_path = f"{path}.tmp"
  with open(temporary_path, "w", encoding="utf-8") as tune_file:
    json.dump(values, tune_file, indent=2, sort_keys=True)
    tune_file.write("\n")
    tune_file.flush()
    os.fsync(tune_file.fileno())
  os.replace(temporary_path, path)


def _set_dotted(values, dotted_key: str, value) -> None:
  target = values
  parts = dotted_key.split(".")
  for part in parts[:-1]:
    target = target.setdefault(part, {})
    if not isinstance(target, dict):
      raise ValueError(f"{dotted_key}: {part} is not an object")
  target[parts[-1]] = value


def _load_for_edit(path: str) -> dict:
  try:
    with open(path, encoding="utf-8") as tune_file:
      values = json.load(tune_file)
    return values if isinstance(values, dict) else {}
  except (OSError, ValueError):
    return {}


def main() -> None:
  parser = argparse.ArgumentParser(description="Edit the nrdr live longitudinal tune")
  parser.add_argument("--path", default=NRDR_LONG_TUNE_PATH)
  commands = parser.add_subparsers(dest="command", required=True)
  commands.add_parser("show")
  set_command = commands.add_parser("set")
  set_command.add_argument("assignments", nargs="+")
  commands.add_parser("reset")
  args = parser.parse_args()

  if args.command == "show":
    tune = LongTune(path=args.path, log_fn=print)
    tune.refresh()
    print(f"file: {args.path} active={tune.active}")
    print(tune.describe())
  elif args.command == "set":
    values = _load_for_edit(args.path)
    for assignment in args.assignments:
      key, separator, raw_value = assignment.partition("=")
      if not separator or not key:
        raise SystemExit(f"invalid assignment: {assignment!r}; expected key=value")
      try:
        value = json.loads(raw_value)
      except ValueError:
        value = raw_value
      _set_dotted(values, key, value)
    write_tune(values, path=args.path)
    tune = LongTune(path=args.path, log_fn=print)
    tune.refresh()
    print(f"wrote {args.path}; planner will see: {tune.describe()}")
  else:
    try:
      os.remove(args.path)
      print(f"removed {args.path}")
    except FileNotFoundError:
      print("no tune file; already at compiled defaults")


if __name__ == "__main__":
  main()
