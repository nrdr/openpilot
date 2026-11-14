import base64
import binascii
import logging
import re
from typing import Protocol

import requests

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


class ParamStore(Protocol):
  def get(self, key: str): ...
  def get_bool(self, key: str) -> bool: ...
  def put(self, key: str, value, block: bool = False): ...
  def put_bool(self, key: str, value: bool, block: bool = False): ...


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


def refresh_github_ssh_keys(params: ParamStore, request_get=requests.get, logger=None) -> bool:
  logger = logger or logging.getLogger(__name__)
  username = (params.get("GithubUsername") or "").strip()
  if not GITHUB_USERNAME_RE.fullmatch(username):
    logger.warning("nrdr ssh key refresh skipped: missing/invalid GithubUsername")
    return False

  try:
    response = request_get(GITHUB_KEYS_URL.format(username=username), timeout=HTTP_TIMEOUT_S)
    response.raise_for_status()
    keys = _validated_keys(response.text)
    if not keys:
      logger.warning("nrdr ssh key refresh skipped: GitHub returned no valid keys")
      return False

    if params.get("GithubSshKeys") != keys:
      params.put("GithubSshKeys", keys, block=True)
      logger.info(f"nrdr ssh keys refreshed for GitHub user {username}")
    if not params.get_bool("SshEnabled"):
      params.put_bool("SshEnabled", True, block=True)
    return True
  except Exception:
    logger.exception("nrdr ssh key refresh failed")
    return False


__all__ = (
  "GITHUB_KEYS_URL",
  "GITHUB_USERNAME_RE",
  "HTTP_TIMEOUT_S",
  "SUPPORTED_KEY_TYPES",
  "ParamStore",
  "_validated_keys",
  "refresh_github_ssh_keys",
)
