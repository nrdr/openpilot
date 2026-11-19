"""Clarity angle mode on the openpilot side: the 39990+TRW+A020 ID resolves like 39990-TRW,A020, and an angle-mode
Clarity is never handed to the PTM torque controllers (it steers through LatControlAngle)."""
from types import SimpleNamespace

from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from openpilot.nrdr.features.lateral.controller_selection import firmware_controller_profile
from openpilot.nrdr.features.lateral.yaw_control_timing import prediction_delay_schedule
from openpilot.nrdr.features.lateral.honda_vgr import get_honda_vgr_profile, normalize_honda_eps_firmware


def _cp(fw):
  return SimpleNamespace(brand="honda", carFingerprint="HONDA_CLARITY", steerRatio=16.5,
                         carFw=[SimpleNamespace(ecu="eps", fwVersion=fw)],
                         lateralTuning=SimpleNamespace(which=lambda: "pid"))


def test_ptm2_id_normalizes_and_gets_the_same_vgr_profile():
  assert normalize_honda_eps_firmware(b"39990+TRW+A020\x00\x00") == normalize_honda_eps_firmware(b"39990-TRW,A020\x00\x00")
  assert get_honda_vgr_profile(_cp(b"39990+TRW+A020\x00\x00")) == get_honda_vgr_profile(_cp(b"39990-TRW,A020\x00\x00")) is not None


def test_angle_mode_is_excluded_from_the_ptm_controller():
  cp = _cp(b"39990-TRW,A020\x00\x00")
  torque = SimpleNamespace(flags=int(HondaFlagsSP.EPS_MODIFIED))
  angle = SimpleNamespace(flags=int(HondaFlagsSP.EPS_MODIFIED | HondaFlagsSP.CLARITY_ANGLE_MODE))
  assert firmware_controller_profile(cp, torque) is not None
  assert firmware_controller_profile(cp, angle) is None


def test_angle_mode_uses_lagd_not_the_ptm_delay_schedule():
  # modeld and controlsd take the PTM prediction-delay schedule only from the PTM controller profile; angle mode gets
  # none, so both use lagd's learned delay (get_lat_delay with delay_schedule=None)
  cp = _cp(b"39990-TRW,A020\x00\x00")
  torque = SimpleNamespace(flags=int(HondaFlagsSP.EPS_MODIFIED))
  angle = SimpleNamespace(flags=int(HondaFlagsSP.EPS_MODIFIED | HondaFlagsSP.CLARITY_ANGLE_MODE))
  assert prediction_delay_schedule(firmware_controller_profile(cp, torque)) is not None
  assert prediction_delay_schedule(firmware_controller_profile(cp, angle)) is None
