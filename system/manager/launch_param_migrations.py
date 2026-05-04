#!/usr/bin/env python3
from __future__ import annotations

import sys

from pathlib import Path
from typing import Protocol

LONG_PITCH_KEY = "LongPitch"
STEER_KP_KEY = "SteerKP"
STEER_KP_STOCK_KEY = "SteerKPStock"

DEFAULT_STEER_KP = 0.6
LEGACY_STEER_KP = 0.7
QT_STEER_KP_PLACEHOLDER = 1.0

LAUNCH_PARAM_MIGRATION_MARKER = ".starpilot_launch_param_migrations_v2"
BRANCH_DEFAULTS_MIGRATION_MARKER = ".starpilot_branch_defaults_migrations_v1"
ACCELERATION_PROFILE_MIGRATION_MARKER = ".starpilot_acceleration_profile_default_v1"
MARKER_DIRNAME = ".starpilot_param_migrations"

LEGACY_CE_STOPPED_LEAD_DEFAULT = True
LEGACY_FORCE_STOPS_DEFAULT = False
LEGACY_AGGRESSIVE_FOLLOW_HIGH_DEFAULT = 1.25
LEGACY_STANDARD_FOLLOW_HIGH_DEFAULT = 1.45
LEGACY_RELAXED_FOLLOW_DEFAULT = 1.75
LEGACY_RELAXED_FOLLOW_HIGH_DEFAULT = 1.75
LEGACY_JERK_DEFAULT = 50.0
LEGACY_ACCELERATION_PROFILE_DEFAULT = 2

STANDARD_ACCELERATION_PROFILE = 0

BRANCH_BOOL_MIGRATIONS = {
  "CEStoppedLead": (LEGACY_CE_STOPPED_LEAD_DEFAULT, False),
  "ForceStops": (LEGACY_FORCE_STOPS_DEFAULT, True),
}

BRANCH_FLOAT_MIGRATIONS = {
  "AggressiveFollowHigh": (LEGACY_AGGRESSIVE_FOLLOW_HIGH_DEFAULT, 1.0),
  "StandardFollowHigh": (LEGACY_STANDARD_FOLLOW_HIGH_DEFAULT, 1.2),
  "StandardJerkAcceleration": (LEGACY_JERK_DEFAULT, 100.0),
  "StandardJerkDeceleration": (LEGACY_JERK_DEFAULT, 100.0),
  "StandardJerkSpeed": (LEGACY_JERK_DEFAULT, 100.0),
  "StandardJerkSpeedDecrease": (LEGACY_JERK_DEFAULT, 100.0),
  "RelaxedFollow": (LEGACY_RELAXED_FOLLOW_DEFAULT, 1.6),
  "RelaxedFollowHigh": (LEGACY_RELAXED_FOLLOW_HIGH_DEFAULT, 1.4),
  "RelaxedJerkAcceleration": (LEGACY_JERK_DEFAULT, 100.0),
  "RelaxedJerkDeceleration": (LEGACY_JERK_DEFAULT, 100.0),
  "RelaxedJerkSpeed": (LEGACY_JERK_DEFAULT, 100.0),
  "RelaxedJerkSpeedDecrease": (LEGACY_JERK_DEFAULT, 100.0),
}

ACCELERATION_PROFILE_MIGRATION = {
  "AccelerationProfile": (LEGACY_ACCELERATION_PROFILE_DEFAULT, STANDARD_ACCELERATION_PROFILE),
}


class ParamsLike(Protocol):
  def get_param_path(self, key: str = "") -> str: ...
  def get_bool(self, key: str) -> bool: ...
  def get_int(self, key: str) -> int: ...
  def get_float(self, key: str) -> float: ...
  def put_bool(self, key: str, value: bool) -> None: ...
  def put_int(self, key: str, value: int) -> None: ...
  def put_float(self, key: str, value: float) -> None: ...


def _approx_equal(lhs: float, rhs: float, tolerance: float = 1e-6) -> bool:
  return abs(lhs - rhs) <= tolerance


def _default_marker_path(params: ParamsLike) -> Path:
  return _marker_dir_path(params) / LAUNCH_PARAM_MIGRATION_MARKER


def _branch_defaults_marker_path(params: ParamsLike) -> Path:
  return _marker_dir_path(params) / BRANCH_DEFAULTS_MIGRATION_MARKER


def _acceleration_profile_marker_path(params: ParamsLike) -> Path:
  return _marker_dir_path(params) / ACCELERATION_PROFILE_MIGRATION_MARKER


def _marker_dir_path(params: ParamsLike) -> Path:
  params_path = Path(params.get_param_path())
  # Params.clear_all() removes unknown files inside the params directory, so
  # one-time migration markers must live alongside it, not inside it.
  return params_path.parent / MARKER_DIRNAME / params_path.name


def _param_file_exists(params: ParamsLike, key: str) -> bool:
  return Path(params.get_param_path(key)).exists()


def _should_migrate_bool_param(params: ParamsLike, key: str, legacy_default: bool) -> bool:
  return not _param_file_exists(params, key) or params.get_bool(key) == legacy_default


def _should_migrate_int_param(params: ParamsLike, key: str, legacy_default: int) -> bool:
  return not _param_file_exists(params, key) or params.get_int(key) == legacy_default


def _should_migrate_float_param(params: ParamsLike, key: str, legacy_default: float) -> bool:
  return not _param_file_exists(params, key) or _approx_equal(params.get_float(key), legacy_default)


def _apply_legacy_launch_param_migrations(params: ParamsLike, marker: Path) -> None:
  if marker.exists():
    return

  marker.parent.mkdir(parents=True, exist_ok=True)

  if not params.get_bool(LONG_PITCH_KEY):
    params.put_bool(LONG_PITCH_KEY, True)

  steer_kp = params.get_float(STEER_KP_KEY)
  if _approx_equal(steer_kp, 0.0) or _approx_equal(steer_kp, LEGACY_STEER_KP):
    params.put_float(STEER_KP_KEY, DEFAULT_STEER_KP)

  steer_kp_stock = params.get_float(STEER_KP_STOCK_KEY)
  if (_approx_equal(steer_kp_stock, 0.0) or
      _approx_equal(steer_kp_stock, LEGACY_STEER_KP) or
      _approx_equal(steer_kp_stock, QT_STEER_KP_PLACEHOLDER)):
    params.put_float(STEER_KP_STOCK_KEY, DEFAULT_STEER_KP)

  # Initialize UsePrebuilt to True if never explicitly set, so the UI default
  # matches the shell script's default of USE_PREBUILT=1.
  if not Path(params.get_param_path("UsePrebuilt")).exists():
    params.put_bool("UsePrebuilt", True)

  marker.touch()


def _apply_branch_default_migration(params: ParamsLike, marker: Path) -> None:
  if marker.exists():
    return

  marker.parent.mkdir(parents=True, exist_ok=True)

  for key, (legacy_default, new_default) in BRANCH_BOOL_MIGRATIONS.items():
    if _should_migrate_bool_param(params, key, legacy_default):
      params.put_bool(key, new_default)

  for key, (legacy_default, new_default) in BRANCH_FLOAT_MIGRATIONS.items():
    if _should_migrate_float_param(params, key, legacy_default):
      params.put_float(key, new_default)

  marker.touch()


def _apply_acceleration_profile_default_migration(params: ParamsLike, marker: Path) -> None:
  if marker.exists():
    return

  marker.parent.mkdir(parents=True, exist_ok=True)

  for key, (legacy_default, new_default) in ACCELERATION_PROFILE_MIGRATION.items():
    if _should_migrate_int_param(params, key, legacy_default):
      params.put_int(key, new_default)

  marker.touch()


def apply_launch_param_migrations(params: ParamsLike, marker_path: Path | None = None,
                                  branch_defaults_marker_path: Path | None = None,
                                  acceleration_profile_marker_path: Path | None = None) -> None:
  _apply_legacy_launch_param_migrations(params, marker_path or _default_marker_path(params))
  # Keep branch-default rollout on its own marker so older installs that already
  # have the legacy marker still receive this one-time param reset.
  _apply_branch_default_migration(params, branch_defaults_marker_path or _branch_defaults_marker_path(params))
  _apply_acceleration_profile_default_migration(
    params, acceleration_profile_marker_path or _acceleration_profile_marker_path(params)
  )


def main() -> int:
  try:
    from openpilot.common.params import Params

    apply_launch_param_migrations(Params())
  except Exception as exc:
    print(f"launch_param_migrations.py failed: {exc}", file=sys.stderr)
    return 1
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
