import time

from openpilot.common.swaglog import cloudlog
from openpilot.nrdr.features.services.remote_actions import RemoteActions
from openpilot.nrdr.features.services.ssh_key_refresh import refresh_github_ssh_keys


POLL_INTERVAL_S = 2.0
SSH_KEY_REFRESH_RETRY_S = 60.0
SSH_KEY_REFRESH_INTERVAL_S = 24 * 60 * 60.0


def _validate_params(params) -> None:
  params.get_bool("NrdrRemoteForceUpdate")
  params.get_bool("NrdrRemoteTuneScan")


def _park() -> None:
  while True:
    time.sleep(3600)


def run(params, reporter_factory) -> None:
  actions = RemoteActions(params)
  reporter = reporter_factory(params)
  actions.set_status("idle")
  next_ssh_key_refresh = 0.0

  while True:
    try:
      now = time.monotonic()
      if now >= next_ssh_key_refresh:
        refreshed = refresh_github_ssh_keys(params, logger=cloudlog)
        interval = SSH_KEY_REFRESH_INTERVAL_S if refreshed else SSH_KEY_REFRESH_RETRY_S
        next_ssh_key_refresh = now + interval

      reporter.consume_handcrafted_request()
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


__all__ = (
  "POLL_INTERVAL_S",
  "SSH_KEY_REFRESH_INTERVAL_S",
  "SSH_KEY_REFRESH_RETRY_S",
  "_park",
  "_validate_params",
  "run",
)
