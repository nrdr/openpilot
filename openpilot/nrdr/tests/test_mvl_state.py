"""MVL persistence remains bounded, host-owned, and off the control thread."""
import pytest

from openpilot.nrdr.car.mvl_state import MVL_STATE_KEYS, MvlStateStore


class MemoryParams(dict):
  def __init__(self, **values):
    super().__init__(values)
    self.writes = []
    self.fail = False

  def put(self, key, value, block=False):
    assert block
    if self.fail:
      raise OSError("test write failure")
    self.writes.append((key, value))
    self[key] = value


def test_only_known_domain_keys_can_cross_the_boundary():
  params = MemoryParams()
  store = MvlStateStore(params, start_worker=False)
  with pytest.raises(ValueError):
    store.load("ExperimentalMode", 0)
  with pytest.raises(ValueError):
    store.put_many({"ExperimentalMode": 1})
  assert not params.writes


@pytest.mark.parametrize("raw", [None, b"invalid", float("nan"), float("inf")])
def test_invalid_load_uses_default(raw):
  store = MvlStateStore(MemoryParams(HondaGasFactorParams=raw), start_worker=False)
  assert store.load("gas_factor", 1.0) == 1.0


def test_coalesces_without_writes_until_flushed_and_skips_unchanged():
  params = MemoryParams()
  store = MvlStateStore(params, start_worker=False)
  for value in range(100):
    store.put_many({key: value for key in MVL_STATE_KEYS})
  assert len(store._pending) == len(MVL_STATE_KEYS)
  assert not params.writes
  assert store.flush_one()
  assert len(params.writes) == 1
  assert params.writes[0][1] == 99
  while store.flush_one():
    pass
  assert len(params.writes) == len(MVL_STATE_KEYS)
  store.put_many({key: 99 for key in MVL_STATE_KEYS})
  assert not store.flush_one()
  assert len(params.writes) == len(MVL_STATE_KEYS)


def test_failed_write_retries_latest_snapshot_and_nonfinite_is_ignored():
  params = MemoryParams()
  store = MvlStateStore(params, start_worker=False)
  store.put_many({"gas_factor": 2, "wind_factor": float("nan")})
  params.fail = True
  assert store.flush_one()
  store.put_many({"gas_factor": 3})
  params.fail = False
  assert store.flush_one()
  assert params.writes == [("HondaGasFactorParams", 3.0)]
  assert not store.flush_one()
