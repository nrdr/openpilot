"""Startup-only host seam. No SunnyPilot service, custom planner or Params polling."""
from openpilot.common.swaglog import cloudlog
from openpilot.nrdr.params import read_settings
from openpilot.nrdr.features.lateral.controller_selection import firmware_controller_profile
from openpilot.nrdr.features.lateral.latcontrol_fw import LatControlFirmware
from openpilot.nrdr.features.lateral.yaw_control_timing import prediction_delay


def create_firmware_controller(CP, CI, dt, settings):
  profile = firmware_controller_profile(CP, settings)
  if profile is None:
    return None
  cloudlog.info("Bare Firmware Controller: %s, image acknowledgement=%s, provisional=%s",
                profile.name, profile.firmware_image, profile.provisional)
  return LatControlFirmware(CP, CI, dt, profile, settings)


def apply_startup_policy(CP, settings):
  modified = str(CP.brand) == "honda" and any(
    fw.ecu == "eps" and b"," in bytes(fw.fwVersion) for fw in CP.carFw)
  if modified and firmware_controller_profile(CP, settings) is None:
    # Stock openpilot refuses unknown EPS mods. Keep that boundary if the owner
    # has not acknowledged the actual image, rather than running stock PID on it.
    CP.dashcamOnly = True
    cloudlog.warning("Bare: modified EPS has no admitted firmware/image selection; no actuation")


__all__ = ("create_firmware_controller", "read_settings", "firmware_controller_profile", "apply_startup_policy",
           "LatControlFirmware", "prediction_delay")
