#!/usr/bin/env python3
import time

import requests

from cereal import messaging
from openpilot.common.params import ParamKeyType
from openpilot.common.realtime import Ratekeeper
from openpilot.common.time import system_time_valid

from openpilot.frogpilot.common.frogpilot_utilities import get_frogpilot_api_info, is_url_pingable
from openpilot.frogpilot.common.frogpilot_variables import EXCLUDED_KEYS, FROGPILOT_API, frogpilot_default_params, params, update_frogpilot_toggles

POND_PRESENCE_INTERVAL_ACTIVE = 60
POND_PRESENCE_INTERVAL_IDLE = 240

REMOTE_TOGGLE_CHECK_INTERVAL_ACTIVE = 10
REMOTE_TOGGLE_CHECK_INTERVAL_IDLE = 60


def check_toggles(started, sm=None, boot_run=False):
  if not params.get_bool("PondPaired"):
    return None

  if not is_url_pingable(FROGPILOT_API):
    return None

  if not boot_run and sm is not None:
    if started and not sm["frogpilotCarState"].isParked:
      return None
    if sm["deviceState"].screenBrightnessPercent == 0:
      return None

  try:
    api_token, _, device_type, dongle_id = get_frogpilot_api_info()
    if not dongle_id or not api_token:
      return None

    response = requests.get(
      f"{FROGPILOT_API}/pond/toggles/pending",
      params={"dongle_id": dongle_id, "api_token": api_token},
      headers={"Content-Type": "application/json", "User-Agent": "frogpilot-api/1.0"},
      timeout=10,
    )
    response.raise_for_status()

    data = response.json()
    pond_active = data.get("pond_active") is True

    if data.get("paired") is False:
      params.put_bool("PondPaired", False)
      print("Device was unpaired remotely")
      return False

    toggles = data.get("toggles")
    if not toggles:
      return pond_active

    for key, value in toggles.items():
      if key in EXCLUDED_KEYS:
        continue

      try:
        if not params.check_key(key):
          print(f"Skipping unknown param key: {key}")
          continue
      except Exception:
        print(f"Skipping unknown param key: {key}")
        continue

      if value is None:
        continue

      try:
        params.put(key, value)
      except Exception as exception:
        print(f"Skipping remote toggle {key}: {exception}")
        continue

    update_frogpilot_toggles()

    requests.post(
      f"{FROGPILOT_API}/pond/toggles/ack",
      json={
        "api_token": api_token,
        "device": device_type,
        "frogpilot_dongle_id": dongle_id,
      },
      headers={"Content-Type": "application/json", "User-Agent": "frogpilot-api/1.0"},
      timeout=10,
    ).raise_for_status()

    print(f"Successfully applied {len(toggles)} remote toggles")
    return pond_active

  except Exception as exception:
    print(f"Failed to check remote toggles: {exception}")
    return None


def ping_pond_presence(interval, parked, started, state_changed):
  last_ping = getattr(ping_pond_presence, "_last_ping", 0.0)
  now = time.monotonic()
  if not state_changed and (now - last_ping) < interval:
    return

  try:
    api_token, build_metadata, device_type, dongle_id = get_frogpilot_api_info()
    if not dongle_id or not api_token:
      return

    payload = {
      "api_token": api_token,
      "build_metadata": build_metadata,
      "device": device_type,
      "dongle_id": dongle_id,
      "frogpilot_dongle_id": dongle_id,
      "is_onroad": bool(started),
      "is_parked": bool(parked),
    }

    response = requests.post(
      f"{FROGPILOT_API}/pond/presence/device",
      json=payload,
      headers={"Content-Type": "application/json", "User-Agent": "frogpilot-api/1.0"},
      timeout=10,
    )
    response.raise_for_status()
    ping_pond_presence._last_ping = now

  except Exception as exception:
    print(f"Failed to update Pond presence: {exception}")


def upload_toggles():
  if not is_url_pingable(FROGPILOT_API):
    return False

  try:
    api_token, build_metadata, device_type, dongle_id = get_frogpilot_api_info()
    if not dongle_id or not api_token:
      return False

    toggles = {}
    for key, _, _, _ in frogpilot_default_params:
      if key in EXCLUDED_KEYS or params.get_key_flag(key) & ParamKeyType.DONT_LOG:
        continue

      value = params.get(key)
      if value is None:
        continue

      toggles[key] = value.decode("utf-8", "replace") if isinstance(value, (bytes, bytearray)) else value

    if not toggles:
      return False

    payload = {
      "api_token": api_token,
      "build_metadata": build_metadata,
      "device": device_type,
      "dongle_id": dongle_id,
      "frogpilot_dongle_id": dongle_id,
      "toggles": toggles,
    }

    requests.post(
      f"{FROGPILOT_API}/pond/toggles/sync",
      json=payload,
      headers={"Content-Type": "application/json", "User-Agent": "frogpilot-api/1.0"},
      timeout=10,
    ).raise_for_status()

    print("Successfully uploaded toggles to FrogPilot.com")
    return True

  except Exception as exception:
    print(f"Failed to upload toggles: {exception}")
    return False


def sync_thread():
  rate_keeper = Ratekeeper(1, None)

  sm = messaging.SubMaster(["deviceState", "frogpilotCarState"])

  boot_sync_complete = False
  pond_active = False
  previous_parked = False
  previous_started = False
  next_toggle_check_at = 0.0

  while True:
    sm.update(0)

    parked = sm["frogpilotCarState"].isParked
    started = sm["deviceState"].started
    state_changed = started != previous_started or parked != previous_parked

    if params.get_bool("PondPaired"):
      presence_interval = POND_PRESENCE_INTERVAL_ACTIVE if started or pond_active else POND_PRESENCE_INTERVAL_IDLE
      ping_pond_presence(presence_interval, parked, started, state_changed)

    if not boot_sync_complete and system_time_valid():
      boot_pond_active = check_toggles(False, boot_run=True)
      if boot_pond_active is not None:
        pond_active = boot_pond_active
      boot_sync_complete = True

    now = time.monotonic()
    if state_changed and parked:
      next_toggle_check_at = 0.0

    if boot_sync_complete and now >= next_toggle_check_at:
      latest_pond_active = check_toggles(started, sm)
      if latest_pond_active is not None:
        pond_active = latest_pond_active
      next_toggle_check_at = now + REMOTE_TOGGLE_CHECK_INTERVAL_ACTIVE if pond_active else REMOTE_TOGGLE_CHECK_INTERVAL_IDLE

    if params.get_bool("PondUploadPending"):
      if not params.get_bool("PondPaired"):
        params.put_bool("PondUploadPending", False)
      elif upload_toggles():
        params.put_bool("PondUploadPending", False)

    previous_parked = parked
    previous_started = started

    rate_keeper.keep_time()


def main():
  sync_thread()


if __name__ == "__main__":
  main()
