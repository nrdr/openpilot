"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import json

from openpilot.common.swaglog import cloudlog
from openpilot.sunnypilot.selfdrive.car.sync_sunnylink_params import CAR_LIST_JSON_OUT

ONROAD_BRIGHTNESS_MIGRATION_VERSION: str = "1.0"
ONROAD_BRIGHTNESS_TIMER_MIGRATION_VERSION: str = "1.0"

# index → seconds mapping for OnroadScreenOffTimer (SSoT)
ONROAD_BRIGHTNESS_TIMER_VALUES = {0: 3, 1: 5, 2: 7, 3: 10, 4: 15, 5: 30, **{i: (i - 5) * 60 for i in range(6, 16)}}
VALID_TIMER_VALUES = set(ONROAD_BRIGHTNESS_TIMER_VALUES.values())

_NRDR_STEER_RATIO_MANUAL_DEFAULTS = (15.38, 10.93)
_NRDR_INTERPOLATED_TORQUE_FRICTION_LOW = "NrdrInterpolatedTorqueFriction"
_NRDR_INTERPOLATED_TORQUE_FRICTION_STANDARD = "NrdrInterpolatedTorqueFrictionStandard"
_NRDR_INTERPOLATED_TORQUE_FRICTION_HIGHWAY = "NrdrInterpolatedTorqueFrictionHighway"
_NRDR_INTERPOLATED_TORQUE_FRICTION_LOW_DEFAULT = 0.12
_NRDR_INTERPOLATED_TORQUE_FRICTION_STANDARD_DEFAULT = 0.10
_NRDR_INTERPOLATED_TORQUE_FRICTION_HIGHWAY_DEFAULT = 0.06

# These old keys are tombstones after the steer-ratio mode migration. They are
# read here only to preserve an existing owner's tune for the attached car.
_NRDR_LEGACY_STEER_RATIO_ENDPOINTS = {
  "HONDA_CLARITY": ("NrdrSteerRatioCenterClarity", "NrdrSteerRatioOuterClarity"),
  "HONDA_CIVIC": ("NrdrSteerRatioCenterCivic", "NrdrSteerRatioOuterCivic"),
  "HONDA_CIVIC_BOSCH": ("NrdrSteerRatioCenterCivic", "NrdrSteerRatioOuterCivic"),
  "HONDA_CIVIC_BOSCH_DIESEL": ("NrdrSteerRatioCenterCivic", "NrdrSteerRatioOuterCivic"),
  "HONDA_ACCORD": ("NrdrSteerRatioCenterAccord", "NrdrSteerRatioOuterAccord"),
  "HONDA_CRV_5G": ("NrdrSteerRatioCenterCrv5g", "NrdrSteerRatioOuterCrv5g"),
  "HONDA_CRV_HYBRID": ("NrdrSteerRatioCenterCrv5g", "NrdrSteerRatioOuterCrv5g"),
  "HONDA_INSIGHT": ("NrdrSteerRatioCenterInsight", "NrdrSteerRatioOuterInsight"),
}


def _resolve_brand(_params) -> str:
  bundle = _params.get("CarPlatformBundle")
  if isinstance(bundle, dict) and bundle.get("brand"):
    return str(bundle["brand"])

  # Auto-fingerprinted cars have no bundle, fall back to the last known CarParams.
  CP_bytes = _params.get("CarParamsPersistent")
  if CP_bytes is None:
    return ""

  # Never raises: callers rely on "" to mean "brand unknown, skip the migration".
  try:
    from openpilot.cereal import messaging  # lazy: avoids heavy import at module level
    from opendbc.car.structs import car
    return str(messaging.log_from_bytes(CP_bytes, car.CarParams).brand)
  except Exception as e:
    cloudlog.exception(f"params_migration: failed to resolve brand from CarParamsPersistent: {e}")
    return ""


def _resolve_car_fingerprint(_params) -> str:
  """Resolve only an exact attached platform; an unknown identity stays unknown."""
  try:
    bundle = _params.get("CarPlatformBundle")
    if isinstance(bundle, dict) and bundle.get("platform"):
      return str(bundle["platform"])
  except Exception as e:
    cloudlog.exception(f"params_migration: failed to resolve CarPlatformBundle platform: {e}")

  for key in ("CarParamsPersistent", "CarParams"):
    try:
      CP_bytes = _params.get(key)
    except Exception as e:
      cloudlog.exception(f"params_migration: failed to read {key}: {e}")
      continue
    if CP_bytes is None:
      continue
    try:
      from openpilot.cereal import messaging  # lazy: avoids heavy import at module level
      from opendbc.car.structs import car
      return str(messaging.log_from_bytes(CP_bytes, car.CarParams).carFingerprint)
    except Exception as e:
      cloudlog.exception(f"params_migration: failed to resolve fingerprint from {key}: {e}")
  return ""


def _legacy_bool(_params, key: str) -> bool:
  try:
    value = _params.get(key)
  except Exception:
    return False
  if isinstance(value, bytes):
    return value.strip().lower() not in (b"", b"0", b"false")
  if isinstance(value, str):
    return value.strip().lower() not in ("", "0", "false")
  return bool(value)


def _migrate_nrdr_steer_ratio_mode(_params) -> None:
  """Create the atomic mode/manual contract without replacing new-format values."""
  try:
    old_mode = _params.get("NrdrSteerRatioMode")
    old_center = _params.get("NrdrSteerRatioManualCenter")
    old_final = _params.get("NrdrSteerRatioManualFinal")
    if old_mode is not None and old_center is not None and old_final is not None:
      return

    fingerprint = _resolve_car_fingerprint(_params) if old_center is None or old_final is None else ""
    center, final = _NRDR_STEER_RATIO_MANUAL_DEFAULTS
    if legacy := _NRDR_LEGACY_STEER_RATIO_ENDPOINTS.get(fingerprint):
      center_key, final_key = legacy
      # Registry defaults are not evidence that an owner chose the legacy tune.
      # Preserve only values which were actually persisted before this migration.
      legacy_center = _params.get(center_key)
      legacy_final = _params.get(final_key)
      center = center if legacy_center is None else legacy_center
      final = final if legacy_final is None else legacy_final

    # Each key is independently guarded so an interrupted migration can be
    # retried safely and a user-entered new-format value is never overwritten.
    migrated = []
    if old_center is None:
      _params.put("NrdrSteerRatioManualCenter", center, block=True)
      migrated.append("center")
    if old_final is None:
      _params.put("NrdrSteerRatioManualFinal", final, block=True)
      migrated.append("final")
    if old_mode is None:
      mode = 1 if _legacy_bool(_params, "NrdrLearnSteerRatio") else 0
      _params.put("NrdrSteerRatioMode", mode, block=True)
      migrated.append("mode")

    cloudlog.info(
      f"params_migration: initialized nrdr steer-ratio {','.join(migrated)} for {fingerprint or 'unknown platform'}"
    )
  except Exception as e:
    cloudlog.exception(f"Error migrating nrdr steer-ratio settings: {e}")


def _migrate_interpolated_torque_friction(_params) -> None:
  """Seed fresh split defaults or preserve an existing legacy Low tune."""
  try:
    low = _params.get(_NRDR_INTERPOLATED_TORQUE_FRICTION_LOW)
    standard = _params.get(_NRDR_INTERPOLATED_TORQUE_FRICTION_STANDARD)
    highway = _params.get(_NRDR_INTERPOLATED_TORQUE_FRICTION_HIGHWAY)
  except Exception as e:
    cloudlog.exception(f"Error reading interpolated Torque friction settings for migration: {e}")
    return

  def write_verified(key: str, value: float, label: str) -> bool:
    try:
      _params.put(key, value, block=True)
      readback = _params.get(key)
      if type(readback) is not type(value) or readback != value:
        cloudlog.error(f"Interpolated Torque friction migration could not verify {label}-speed value")
        return False
      return True
    except Exception as e:
      cloudlog.exception(f"Error seeding {label}-speed interpolated Torque friction: {e}")
      return False

  if low is None:
    # Low is the durable discriminator between a fresh install and an upgrade.
    # Seed/verify the split bands independently, then write Low LAST. An
    # interrupted retry therefore cannot misclassify a fresh split as a legacy
    # Low-only tune and collapse it to .12/.12/.12.
    standard_ready = standard is not None or write_verified(
      _NRDR_INTERPOLATED_TORQUE_FRICTION_STANDARD,
      _NRDR_INTERPOLATED_TORQUE_FRICTION_STANDARD_DEFAULT,
      "standard",
    )
    highway_ready = highway is not None or write_verified(
      _NRDR_INTERPOLATED_TORQUE_FRICTION_HIGHWAY,
      _NRDR_INTERPOLATED_TORQUE_FRICTION_HIGHWAY_DEFAULT,
      "highway",
    )
    if standard_ready and highway_ready and write_verified(
      _NRDR_INTERPOLATED_TORQUE_FRICTION_LOW,
      _NRDR_INTERPOLATED_TORQUE_FRICTION_LOW_DEFAULT,
      "low",
    ):
      cloudlog.info("params_migration: initialized fresh interpolated Torque friction defaults 0.12/0.10/0.06")
    return

  migrated = []
  for key, current, label in (
    (_NRDR_INTERPOLATED_TORQUE_FRICTION_STANDARD, standard, "standard"),
    (_NRDR_INTERPOLATED_TORQUE_FRICTION_HIGHWAY, highway, "highway"),
  ):
    if current is None and write_verified(key, low, label):
      migrated.append(label)
  if migrated:
    cloudlog.info(
      f"params_migration: initialized interpolated Torque friction {','.join(migrated)} from low-speed value {low}"
    )


def _migrate_car_platform_bundle(_params):
  bundle = _params.get("CarPlatformBundle")
  if bundle is None:
    return

  old_platform = bundle.get("platform")
  if not old_platform:
    return

  from opendbc.car.fingerprints import MIGRATION  # lazy: avoids heavy import at module level
  if old_platform not in MIGRATION:
    return

  new_platform = str(MIGRATION[old_platform])

  with open(CAR_LIST_JSON_OUT) as f:
    car_list = json.load(f)

  candidates = [(k, v) for k, v in car_list.items() if v.get("platform") == new_platform]
  if candidates:
    old_model = bundle.get("model")
    key, data = next(((k, v) for k, v in candidates if v.get("model") == old_model), candidates[0])
    bundle = {**data, "name": key}
  else:
    bundle["platform"] = new_platform

  _params.put("CarPlatformBundle", bundle, block=True)
  cloudlog.info(f"params_migration: CarPlatformBundle migrated {old_platform!r} -> {new_platform!r}")


def _migrate_tesla_mads_screen_button(_params):
  # TeslaMadsScreenButton defaults to Off for fresh installs, but the screen button was previously always
  # active on Teslas with a vehicle bus. Seed existing Tesla installs with 3-finger to preserve that.
  try:
    if _params.get("TeslaMadsScreenButton") is not None:
      return

    if _resolve_brand(_params) != "tesla":
      return

    from opendbc.sunnypilot.car.tesla.values import MadsScreenButtonType  # lazy: avoids heavy import at module level
    _params.put("TeslaMadsScreenButton", MadsScreenButtonType.THREE_FINGER, block=True)
    cloudlog.info("params_migration: seeded TeslaMadsScreenButton with 3-finger to preserve existing behavior")
  except Exception as e:
    cloudlog.exception(f"Error migrating TeslaMadsScreenButton: {e}")


def _migrate_model_bundle_slots(_params):
  # Pre-split, a chestnut user's big-model selection lived in the single
  # ActiveBundle. Seed both slots; validation drops whichever does not match
  # its own manifest.
  try:
    if _params.get("ModelManager_ActiveBundleChestnut") is not None:
      return
    if (chestnut_bundle := _params.get("ModelManager_ActiveBundleUSBGPU")) is not None:
      _params.put("ModelManager_ActiveBundleChestnut", chestnut_bundle, block=True)
      cloudlog.info("params_migration: seeded ModelManager_ActiveBundleChestnut from ModelManager_ActiveBundleUSBGPU")
      return
    if (bundle := _params.get("ModelManager_ActiveBundle")) is None:
      return
    _params.put("ModelManager_ActiveBundleChestnut", bundle, block=True)
    cloudlog.info("params_migration: seeded ModelManager_ActiveBundleChestnut from ModelManager_ActiveBundle")
  except Exception as e:
    cloudlog.exception(f"Error migrating model bundle slots: {e}")


def run_migration(_params):
  # migrate OnroadScreenOffBrightness
  if _params.get("OnroadScreenOffBrightnessMigrated") != ONROAD_BRIGHTNESS_MIGRATION_VERSION:
    try:
      val = _params.get("OnroadScreenOffBrightness", return_default=True)
      if val >= 2:  # old: 5%, new: Screen Off
        new_val = val + 1
        _params.put("OnroadScreenOffBrightness", new_val, block=True)
        log_str = f"Successfully migrated OnroadScreenOffBrightness from {val} to {new_val}."
      else:
        log_str = "Migration not required for OnroadScreenOffBrightness."

      _params.put("OnroadScreenOffBrightnessMigrated", ONROAD_BRIGHTNESS_MIGRATION_VERSION, block=True)
      cloudlog.info(log_str + f" Setting OnroadScreenOffBrightnessMigrated to {ONROAD_BRIGHTNESS_MIGRATION_VERSION}")
    except Exception as e:
      cloudlog.exception(f"Error migrating OnroadScreenOffBrightness: {e}")

  # migrate OnroadScreenOffTimer
  if _params.get("OnroadScreenOffTimerMigrated") != ONROAD_BRIGHTNESS_TIMER_MIGRATION_VERSION:
    try:
      val = _params.get("OnroadScreenOffTimer", return_default=True)
      if val not in VALID_TIMER_VALUES:
        _params.put("OnroadScreenOffTimer", 15, block=True)
        log_str = f"Successfully migrated OnroadScreenOffTimer from {val} to 15 (default)."
      else:
        log_str = "Migration not required for OnroadScreenOffTimer."

      _params.put("OnroadScreenOffTimerMigrated", ONROAD_BRIGHTNESS_TIMER_MIGRATION_VERSION, block=True)
      cloudlog.info(log_str + f" Setting OnroadScreenOffTimerMigrated to {ONROAD_BRIGHTNESS_TIMER_MIGRATION_VERSION}")
    except Exception as e:
      cloudlog.exception(f"Error migrating OnroadScreenOffTimer: {e}")

  _migrate_car_platform_bundle(_params)

  # Replace the legacy boolean + per-family endpoint matrix with one atomic
  # mode and one global manual pair, preserving an attached car's old values.
  _migrate_nrdr_steer_ratio_mode(_params)

  # Preserve the legacy single friction tune by copying it into each new
  # speed band before ordinary registry defaults are materialized.
  _migrate_interpolated_torque_friction(_params)

  # seed TeslaMadsScreenButton for existing Tesla installs
  _migrate_tesla_mads_screen_button(_params)

  # seed the chestnut model slot from the pre-split single slot
  _migrate_model_bundle_slots(_params)
