from pathlib import Path

UNREGISTERED = "UnregisteredDevice"
ONROAD_BLOCKED_PARAMS = {
  "LongitudinalPersonality",
  "NrdrSteerRatioMode",
  "NrdrSteerRatioManualCenter",
  "NrdrSteerRatioManualFinal",
  "NrdrInterpolatedTorquePifBlend",
  "NrdrInterpolatedTorqueShare",
  "NrdrInterpolatedTorqueLatAccelFactor",
  "NrdrInterpolatedTorqueFriction",
  "NrdrInterpolatedTorqueFrictionStandard",
  "NrdrInterpolatedTorqueFrictionHighway",
}


def _identity_path() -> Path:
  from openpilot.common.hardware.hw import Paths
  return Path(Paths.persist_root()) / "comma" / "sunnylink_dongle_id"


def restore_dongle_id(params, dongle_id):
  if dongle_id not in (None, UNREGISTERED):
    return dongle_id
  try:
    restored = _identity_path().read_text().strip()
    if restored:
      params.put("SunnylinkDongleId", restored, block=True)
      return restored
  except Exception:
    pass
  return dongle_id


def persist_dongle_id(dongle_id) -> None:
  if not dongle_id or dongle_id == UNREGISTERED:
    return
  try:
    path = _identity_path()
    if not path.exists():
      path.parent.mkdir(parents=True, exist_ok=True)
      path.write_text(dongle_id)
  except Exception:
    pass


def allow_param_write(key: str, onroad: bool) -> bool:
  return not onroad or key not in ONROAD_BLOCKED_PARAMS


def inject_car_tune_details(schema: dict, walk) -> None:
  from openpilot.common.params import Params, UnknownKeyName
  try:
    details = Params().get("NrdrCarTuneDetails")
  except UnknownKeyName:
    return
  if isinstance(details, bytes):
    details = details.decode("utf-8", "replace")
  if not details:
    return

  def visitor(item: dict) -> None:
    if item.get("key") == "NrdrCarTuneInfo":
      item["details"] = str(details)

  walk(schema, visitor)
