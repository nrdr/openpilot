from openpilot.sunnypilot.nrdr.sunnylink import allow_param_write


def test_steer_ratio_contract_cannot_be_written_onroad():
  for key in ("NrdrSteerRatioMode", "NrdrSteerRatioManualCenter", "NrdrSteerRatioManualFinal"):
    assert not allow_param_write(key, onroad=True)
    assert allow_param_write(key, onroad=False)


def test_unrelated_param_write_policy_is_unchanged():
  assert allow_param_write("NrdrLearnStiffness", onroad=True)
  assert not allow_param_write("LongitudinalPersonality", onroad=True)
