#!/usr/bin/env python3
import time

from openpilot.cereal import custom, messaging
from opendbc.car.structs import car
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.sunnypilot.nrdr.car_tune_report import CarTuneReporter
from openpilot.sunnypilot.nrdr.handcrafted_lateral import consume_handcrafted_lateral_request
from openpilot.sunnypilot.nrdr.remote_actions import RemoteActions
from openpilot.sunnypilot.nrdr.ssh_key_refresh import refresh_github_ssh_keys


POLL_INTERVAL_S = 2.0
SSH_KEY_REFRESH_RETRY_S = 60.0
SSH_KEY_REFRESH_INTERVAL_S = 24 * 60 * 60.0


def _validate_params(params) -> None:
  params.get_bool("NrdrRemoteForceUpdate")
  params.get_bool("NrdrRemoteTuneScan")


def _park() -> None:
  while True:
    time.sleep(3600)


def _consume_handcrafted_request(params: Params) -> list[str]:
  if not params.get_bool("NrdrHandcraftedLateralTune") or not params.get_bool("IsOffroad"):
    return []
  try:
    cp_bytes = params.get("CarParamsPersistent") or params.get("CarParams")
    if cp_bytes is None:
      return []
    cp_sp_bytes = params.get("CarParamsSPPersistent")
    CP_SP = messaging.log_from_bytes(cp_sp_bytes, custom.CarParamsSP) if cp_sp_bytes is not None else None
    with car.CarParams.from_bytes(cp_bytes) as CP:
      return consume_handcrafted_lateral_request(CP, CP_SP, params)
  except Exception:
    # The command stays true; keep every other remoted action and the pure
    # reporter alive while the next safe offroad retry waits.
    cloudlog.exception("nrdr_remoted: handcrafted lateral apply failed; request retained")
    return []


def main() -> None:
  params = Params()
  try:
    _validate_params(params)
  except Exception:
    cloudlog.exception("nrdr_remoted: unavailable params")
    _park()

  actions = RemoteActions(params)
  reporter = CarTuneReporter(params)
  actions.set_status("idle")
  next_ssh_key_refresh = 0.0

  while True:
    try:
      now = time.monotonic()
      if now >= next_ssh_key_refresh:
        refreshed = refresh_github_ssh_keys(params, logger=cloudlog)
        interval = SSH_KEY_REFRESH_INTERVAL_S if refreshed else SSH_KEY_REFRESH_RETRY_S
        next_ssh_key_refresh = now + interval

      _consume_handcrafted_request(params)
      reporter.publish()
      if params.get_bool("NrdrRemoteForceUpdate"):
        params.put_bool("NrdrRemoteForceUpdate", False)
        cloudlog.info("nrdr_remoted: force update triggered")
        actions.force_update()
      if params.get_bool("NrdrRemoteTuneScan"):
        params.put_bool("NrdrRemoteTuneScan", False)
        cloudlog.info("nrdr_remoted: tune scan triggered")
        actions.tune_scan()
    except Exception:
      cloudlog.exception("nrdr_remoted: loop error")
    time.sleep(POLL_INTERVAL_S)


if __name__ == "__main__":
  main()
