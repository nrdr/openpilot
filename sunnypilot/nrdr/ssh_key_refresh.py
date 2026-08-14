import base64
import binascii
import re

import requests

from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog


GITHUB_KEYS_URL = "https://github.com/{username}.keys"
HTTP_TIMEOUT_S = 15
GITHUB_USERNAME_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
SUPPORTED_KEY_TYPES = {
  "ssh-ed25519",
  "ssh-rsa",
  "ecdsa-sha2-nistp256",
  "ecdsa-sha2-nistp384",
  "ecdsa-sha2-nistp521",
  "sk-ecdsa-sha2-nistp256@openssh.com",
  "sk-ssh-ed25519@openssh.com",
}


def _validated_keys(text: str) -> str:
  keys = []
  for raw_line in text.splitlines():
    line = raw_line.strip()
    parts = line.split()
    if len(parts) < 2 or parts[0] not in SUPPORTED_KEY_TYPES:
      continue
    try:
      if len(base64.b64decode(parts[1], validate=True)) < 4:
        continue
    except (binascii.Error, ValueError):
      continue
    keys.append(line)
  return "\n".join(keys)


def refresh_github_ssh_keys(params: Params, request_get=requests.get) -> bool:
  """Refresh cached SSH keys using the device's existing GitHub identity.

  GithubUsername remains the trust anchor: this never accepts a remotely supplied
  username or key. Existing keys are retained if GitHub cannot be reached or
  returns no valid OpenSSH public keys.
  """
  username = (params.get("GithubUsername") or "").strip()
  if not GITHUB_USERNAME_RE.fullmatch(username):
    cloudlog.warning("nrdr ssh key refresh skipped: missing/invalid GithubUsername")
    return False

  try:
    response = request_get(GITHUB_KEYS_URL.format(username=username), timeout=HTTP_TIMEOUT_S)
    response.raise_for_status()
    keys = _validated_keys(response.text)
    if not keys:
      cloudlog.warning("nrdr ssh key refresh skipped: GitHub returned no valid keys")
      return False

    if params.get("GithubSshKeys") != keys:
      params.put("GithubSshKeys", keys, block=True)
      cloudlog.info(f"nrdr ssh keys refreshed for GitHub user {username}")
    if not params.get_bool("SshEnabled"):
      params.put_bool("SshEnabled", True, block=True)
    return True
  except Exception:
    # Never clear working cached keys because of a transient network/GitHub error.
    cloudlog.exception("nrdr ssh key refresh failed")
    return False
