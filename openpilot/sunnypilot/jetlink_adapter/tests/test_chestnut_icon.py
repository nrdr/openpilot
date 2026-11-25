import pytest

from openpilot.sunnypilot.jetlink_adapter import chestnut_icon

VALID = ('disconnected', 'uncompiled', 'ready', 'loading', 'active', 'failed')


class FakeStatus:
  def __init__(self, result=None, exc=None):
    self.result, self.exc, self.calls = result, exc, []

  def icon(self, *args):
    self.calls.append(args)
    if self.exc:
      raise self.exc
    return self.result


def test_none_status_is_disconnected():
  assert chestnut_icon(None, True, True, True, 'running') == 'disconnected'


@pytest.mark.parametrize('value', VALID)
def test_valid_values_pass_through(value):
  assert chestnut_icon(FakeStatus(value), True, False, False, '') == value


def test_waiting_is_loading():
  assert chestnut_icon(FakeStatus('waiting'), True, True, False, 'ready') == 'loading'


def test_unknown_is_disconnected():
  assert chestnut_icon(FakeStatus('bogus'), True, True, True, 'x') == 'disconnected'


def test_raising_icon_is_disconnected():
  assert chestnut_icon(FakeStatus(exc=RuntimeError('boom')), True, True, True, 'x') == 'disconnected'


def test_arguments_pass_through():
  st = FakeStatus('ready')
  chestnut_icon(st, True, False, True, 'joining')
  assert st.calls == [(True, False, True, 'joining')]


def test_empty_state_accepted():
  st = FakeStatus('loading')
  assert chestnut_icon(st, True, False, False, '') == 'loading'
  assert st.calls == [(True, False, False, '')]
