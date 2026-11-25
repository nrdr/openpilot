"""One-shot parked reset. Only manager may clear state, between card lifetimes."""
import json
from pathlib import Path

from openpilot.nrdr.car.mvl_state import LEARNER_META_PATH, MVL_STATE_KEYS
from openpilot.nrdr.features.longitudinal.bosch_a.learning_params import LEARNER_META_PATH as BOSCH_A_LEARNER_PATH
from openpilot.nrdr.params import confirmed_vehicle_identity, get_selected_car_identity

REQUEST = "NrdrResetLiveGas"
STATUS = "NrdrLiveGasResetStatus"
# The high/low legacy nodes also seed the newer speed bands. Do not include
# the independent speed servo, brake, launch or lateral learners.
GAS_KEYS = tuple(MVL_STATE_KEYS[name + suffix] for name in ("gas_factor", "gas_alpha")
                 for suffix in ("", "_low", "_00", "_10", "_20", "_30")) + (MVL_STATE_KEYS["wind_factor"],)


def honda_fingerprint(params, cp):
  present, platform, brand = get_selected_car_identity(params)
  identity = confirmed_vehicle_identity(cp, platform, brand, selection_present=present)
  return identity[0] if identity and identity[1] == "honda" else None


def stored_cp(params):
  from opendbc.car.structs import car
  from openpilot.cereal import messaging

  raw = params.get("CarParamsPersistent")
  return messaging.log_from_bytes(raw, car.CarParams) if raw else None


def request_reset(params, cp):
  fingerprint = honda_fingerprint(params, cp)
  if not fingerprint or not params.get_bool("IsOffroad"):
    raise ValueError("Park and turn off the confirmed Honda before requesting a reset.")
  if not params.get_bool(REQUEST):
    pending = f"Requested: {fingerprint}"
    params.put(STATUS, pending, block=True)
    if params.get(STATUS) != pending:
      raise OSError("Could not bind the reset request to this Honda.")
    params.put_bool(REQUEST, True, block=True)
    if not params.get_bool(REQUEST) and params.get(STATUS) == pending:
      raise OSError("Could not queue the reset request.")


def consume_reset(params, sm, card, *, read_cp=stored_cp, meta_path=LEARNER_META_PATH, bosch_a_path=BOSCH_A_LEARNER_PATH):
  if not params.get_bool(REQUEST):
    return
  result = "Not reset: park, turn ignition off and request again."
  try:
    pandas = sm["pandaStates"]
    if (not sm.all_checks(["deviceState", "pandaStates"]) or sm["deviceState"].started or not params.get_bool("IsOffroad") or
        not pandas or any(str(p.pandaType) == "unknown" or p.ignitionLine or p.ignitionCan or p.controlsAllowed or
                          str(p.safetyModel) not in ("silent", "noOutput") for p in pandas) or card.proc is not None):
      return
    fingerprint = honda_fingerprint(params, read_cp(params))
    live_cp = sm["carParams"]
    if (not fingerprint or params.get(STATUS) != f"Requested: {fingerprint}" or
        (live_cp.carFingerprint and honda_fingerprint(params, live_cp) != fingerprint)):
      result = "Not reset: vehicle or request changed."
      return
    if meta_path.exists():
      result = "Not reset: could not match the saved learner metadata to this Honda."
      if json.loads(meta_path.read_text(encoding="utf-8")).get("car_fingerprint") != fingerprint:
        return

    # Invalidate the scalar learner's commit marker first. Its writer and the
    # multiband writer live in card, which manager cannot restart mid-reset.
    result = "Reset incomplete: check storage before requesting again."
    params.put(STATUS, "Resetting", block=True)
    if params.get(STATUS) != "Resetting":
      return
    meta_path.unlink(missing_ok=True)
    # The Bosch-A learner keeps its factors in its own file, not in GAS_KEYS (bosch_a/learning_params.py).
    bosch_a_path = Path(bosch_a_path)
    bosch_a_path.unlink(missing_ok=True)
    for key in GAS_KEYS:
      params.remove(key)
    if not meta_path.exists() and not bosch_a_path.exists() and all(params.get_raw(key) is None for key in GAS_KEYS):
      result = "Reset complete."
  finally:
    # Publish the outcome before dropping the switch; never replay a failed
    # or unsafe command on a later drive. Both keys are cleared at startup.
    try:
      params.put(STATUS, result, block=True)
    finally:
      params.put_bool(REQUEST, False, block=True)
    params.put("ParamsVersion", int(params.get("ParamsVersion") or 0) + 1, block=True)
