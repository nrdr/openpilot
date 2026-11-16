"""Opt-in PTM experimentation, initially identical to the timing-off baseline.

Keep experimental overrides here; do not retune the shared production core to
change this controller. Admission, driver override, inactivity, command limits
and model timing remain inherited from PTM. Offline findings are not a tune.
"""
from openpilot.common.swaglog import cloudlog
from openpilot.nrdr.features.lateral.latcontrol_fw import LatControlFirmware
from openpilot.nrdr.features.lateral.vfn_eps_core import HondaEpsFirmwareFeedforward, HondaEpsLateralCore


class PtmTestingFeedforward(HondaEpsFirmwareFeedforward):
  """Testing-only feedforward extension point; no experimental changes yet."""


class PtmTestingCore(HondaEpsLateralCore):
  """Testing-only feedback/filter extension point; production defaults intact."""


class LatControlPtmTesting(LatControlFirmware):
  core_type = PtmTestingCore
  feedforward_type = PtmTestingFeedforward

  def __init__(self, CP, CP_SP, CI, dt):
    super().__init__(CP, CP_SP, CI, dt)
    cloudlog.info("PTM Testing selected: baseline timing-off behavior, no experimental tuning")
