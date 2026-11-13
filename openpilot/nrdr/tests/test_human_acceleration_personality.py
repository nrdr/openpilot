from openpilot.cereal import log
from openpilot.nrdr.features.longitudinal.bosch_a import human_acceleration

P = log.LongitudinalPersonality


def test_applies_relaxed_standard_and_econ_only():
  assert human_acceleration.applies(P.relaxed)
  assert human_acceleration.applies(P.standard)
  assert human_acceleration.applies(P.econ)
  assert not human_acceleration.applies(P.aggressive)


def test_applies_takes_raw_ints_and_rejects_junk():
  assert human_acceleration.applies(1) and human_acceleration.applies(2)
  assert not human_acceleration.applies(0)
  assert human_acceleration.applies(3)  # Econ
  for junk in (None, True, 7, -1, "standard"):
    assert not human_acceleration.applies(junk), junk


def test_cap_unchanged():
  # 30 mph set speed, 15 mph ego: between half and full max accel, ramp-off not reached.
  assert abs(human_acceleration.cap(2.0, 13.4, 6.7) - (1.0 + 1.0 * (13.4 - 12.5) / 12.5)) < 1e-6
