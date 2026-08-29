from openpilot.nrdr.features.services.ssh_key_refresh import refresh_github_ssh_keys


VALID_KEYS = "\n".join((
  "ssh-rsa YWJjZA== first",
  "ssh-ed25519 ZWZnaA== second",
))


class FakeResponse:
  def __init__(self, text=VALID_KEYS, error=None):
    self.text = text
    self.error = error

  def raise_for_status(self):
    if self.error is not None:
      raise self.error


class FakeParams:
  def __init__(self, username="Aragon7777", keys="old-key", ssh_enabled=False):
    self.values = {
      "GithubUsername": username,
      "GithubSshKeys": keys,
      "SshEnabled": ssh_enabled,
    }
    self.writes = []

  def get(self, key):
    return self.values.get(key)

  def get_bool(self, key):
    return bool(self.values.get(key))

  def put(self, key, value, block=False):
    self.values[key] = value
    self.writes.append((key, value, block))

  def put_bool(self, key, value, block=False):
    self.put(key, value, block)


def test_refreshes_keys_for_existing_username_and_enables_ssh():
  params = FakeParams()
  requests = []

  def get(url, timeout):
    requests.append((url, timeout))
    return FakeResponse()

  assert refresh_github_ssh_keys(params, request_get=get)
  assert requests == [("https://github.com/Aragon7777.keys", 15)]
  assert params.values["GithubUsername"] == "Aragon7777"
  assert params.values["GithubSshKeys"] == VALID_KEYS
  assert params.values["SshEnabled"] is True


def test_keeps_cached_keys_when_refresh_fails():
  params = FakeParams()

  assert not refresh_github_ssh_keys(params, request_get=lambda *_args, **_kwargs: FakeResponse(error=RuntimeError("offline")))
  assert params.values["GithubSshKeys"] == "old-key"
  assert params.writes == []


def test_rejects_missing_or_invalid_username_without_request():
  for username in ("", "not/a/user", "-leading-dash", "trailing-dash-"):
    params = FakeParams(username=username)

    def unexpected_request(*_args, **_kwargs):
      raise AssertionError("request should not run")

    assert not refresh_github_ssh_keys(params, request_get=unexpected_request)
    assert params.values["GithubSshKeys"] == "old-key"


def test_rejects_response_without_valid_openssh_keys():
  params = FakeParams()
  response = FakeResponse("not-a-key\nssh-rsa !!! invalid")

  assert not refresh_github_ssh_keys(params, request_get=lambda *_args, **_kwargs: response)
  assert params.values["GithubSshKeys"] == "old-key"
