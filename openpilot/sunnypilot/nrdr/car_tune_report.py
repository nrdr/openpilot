from openpilot.cereal import custom, messaging
from opendbc.car.structs import car
from opendbc.car.car_helpers import interfaces
from openpilot.common.swaglog import cloudlog
from openpilot.sunnypilot.nrdr.handcrafted_lateral import (
  apply_handcrafted_lateral_profile,
  get_handcrafted_lateral_profile,
  is_handcrafted_lateral_enabled,
)
from openpilot.sunnypilot.nrdr.honda_vgr import get_honda_vgr_profile
from openpilot.sunnypilot.nrdr.steer_ratio_tuning import get_steer_ratio_endpoint_profile


def _format_values(values) -> str:
  return "/".join(f"{float(value):g}" for value in values)


class CarTuneReporter:
  def __init__(self, params):
    self.params = params
    self.cache = {}

  def _value(self, key):
    return self.params.get(key, return_default=True)

  def _state(self, key: str) -> str:
    return "ON" if self.params.get_bool(key) else "OFF"

  def _publish(self, values: dict[str, str]) -> None:
    for key, value in values.items():
      if self.cache.get(key) == value:
        continue
      self.params.put(key, value)
      self.cache[key] = value

  def _eps_firmware(self, CP) -> str:
    return next(
      (
        bytes(firmware.fwVersion).decode("latin-1", "replace").strip("\x00").strip()
        for firmware in CP.carFw
        if firmware.ecu == "eps"
      ),
      "",
    ) or "n/a"

  def _gas_interceptor(self) -> str:
    cp_sp_bytes = self.params.get("CarParamsSPPersistent")
    if not cp_sp_bytes:
      return "n/a"
    cp_sp = messaging.log_from_bytes(cp_sp_bytes, custom.CarParamsSP)
    return str(bool(cp_sp.enableGasInterceptor)).lower()

  def _pid_source(self, CP):
    if CP.lateralTuning.which() == "pid":
      return CP
    CarInterface = interfaces[CP.carFingerprint]
    reconstructed = CarInterface.get_non_essential_params(CP.carFingerprint)
    CarInterface.get_non_essential_params_sp(reconstructed, CP.carFingerprint)
    return reconstructed if reconstructed.lateralTuning.which() == "pid" else CP

  def _controller_name(self, CP) -> str:
    return "PID/NNLC" if str(CP.carFingerprint) == "HONDA_CLARITY" else CP.lateralTuning.which().upper()

  def _pid_info(self, CP) -> tuple[str, str, str]:
    source = self._pid_source(CP)
    if source.lateralTuning.which() != "pid":
      return f"{CP.lateralTuning.which().upper()} (no PID base)", "n/a", "n/a"

    pid = source.lateralTuning.pid
    gains = f"P {_format_values(pid.kpV)} | I {_format_values(pid.kiV)}"
    feedforward = (
      f"{_format_values(float(value) * 1e6 for value in pid.kfV)} x10^-6"
      if len(pid.kfV)
      else f"{float(pid.kf):g}"
    )
    speeds = "0 / <25 / 25 / 50 mph" if len(pid.kpV) == 4 else "0 / 25 / 50 mph"
    return gains, feedforward, speeds

  def _steer_ratio_info(self, CP) -> str:
    profile = get_steer_ratio_endpoint_profile(CP.carFingerprint)
    if profile is None:
      return f"Auto {self._state('NrdrLearnSteerRatio')} | base {float(CP.steerRatio):g}"
    center = float(self._value(profile.center_param))
    outer = float(self._value(profile.outer_param))
    firmware_profile = get_honda_vgr_profile(CP)
    if self.params.get_bool("NrdrLegacyDualBpSteerRatio"):
      mode = "legacy dual-BP"
    elif firmware_profile is not None:
      mode = f"experimental EPS map {firmware_profile.name}"
    else:
      mode = "firmware unavailable -> legacy dual-BP"
    lane_change = self._state("NrdrLaneChangeEndpointSteerRatio")
    if firmware_profile is not None and not self.params.get_bool("NrdrLegacyDualBpSteerRatio"):
      return f"{mode} | {center:.2f} center anchor | {outer:.2f} fallback/lane-change outer | lane endpoint {lane_change}"
    return f"{mode} | {center:.2f} center -> {outer:.2f} outer | lane endpoint {lane_change}"

  def _controller_info(self, CP, controller: str, handcrafted_enabled: bool, profile) -> str:
    if controller == "PID/NNLC":
      firmware_pid_only = not self.params.get_bool("NrdrLegacyDualBpSteerRatio") and get_honda_vgr_profile(CP) is not None
      if firmware_pid_only:
        nnlc = "PID only | NNLC unavailable in firmware EPS mode"
      else:
        nnlc = "PID/NNLC hybrid | PID for lane changes" if self._state("NrdrNnlcEnabled") == "ON" \
          else "PID only | NNLC disabled"
    else:
      nnlc = controller
    return f"Handcrafted v{profile.version} | {nnlc}" if handcrafted_enabled else nnlc

  def _build(self, CP) -> dict[str, str]:
    changed = apply_handcrafted_lateral_profile(CP.carFingerprint, self.params)
    if changed:
      cloudlog.warning({
        "event": "handcrafted lateral profile restored offroad",
        "carFingerprint": str(CP.carFingerprint),
        "changedParams": changed,
      })

    eps = self._eps_firmware(CP)
    eps_short = eps.rsplit(",", 1)[-1].strip() if "," in eps else eps
    interceptor = self._gas_interceptor()
    controller = self._controller_name(CP)
    profile = get_handcrafted_lateral_profile(CP.carFingerprint)
    handcrafted_enabled = is_handcrafted_lateral_enabled(CP.carFingerprint, self.params)
    handcrafted = f"{profile.name} (v{profile.version})" if handcrafted_enabled and profile is not None else "OFF"
    controller_info = self._controller_info(CP, controller, handcrafted_enabled, profile)

    pid_base, pid_feedforward, pid_speeds = self._pid_info(CP)
    longitudinal = CP.longitudinalTuning
    long_base = f"P {_format_values(longitudinal.kpV)} | I {_format_values(longitudinal.kiV)}"
    if hasattr(longitudinal, "kf"):
      long_base += f" | F {float(longitudinal.kf):g}"

    pid_low = f"P {self._value('LatPScaleLowSpeed')}% | I {self._value('LatIScaleLowSpeed')}% | F {self._value('LatFScaleLowSpeed')}%"
    pid_mid = f"P {self._value('LatPScaleStandard')}% | I {self._value('LatIScaleStandard')}% | F {self._value('LatFScaleStandard')}%"
    pid_high = f"P {self._value('LatPScaleHighway')}% | I {self._value('LatIScaleHighway')}% | F {self._value('LatFScaleHighway')}%"
    damping = f"{self._value('NrdrLatRateDamping')}% | fades by {self._value('NrdrLatRateDampingFadeSpeed')} mph"
    center = "".join((
      f"P-only {float(self._value('HondaCenterScale')) * 100.0:g}% | ",
      f"+/-{float(self._value('HondaCenterBoostThreshold')):g} deg | ",
      f"above {self._value('HondaCenterBoostMinSpeed')} mph",
    ))
    nnlc = "".join((
      f"{self._state('NrdrNnlcEnabled')} | {self._value('NrdrNnlcActivationSpeed')} mph | ",
      f"KP {float(self._value('NrdrNnlcKpGain')) / 100.0:g} | ",
      f"KF {float(self._value('NrdrNnlcKfGain')) / 100.0:g} | ",
      f"KI {float(self._value('NrdrNnlcKiGain')) / 100.0:g}",
    ))
    if not self.params.get_bool("NrdrLegacyDualBpSteerRatio") and get_honda_vgr_profile(CP) is not None:
      nnlc += " | inactive in firmware EPS mode"
    steer_ratio = self._steer_ratio_info(CP)
    learning = f"stiffness {self._state('NrdrLearnStiffness')} | angle {self._state('NrdrLearnAngleOffset')}"
    helpers = f"stiction {self._state('NrdrLatStiction')} | StarPilot {self._state('NrdrStarPilotPid')}"
    gas = "gas" if interceptor == "true" else "no gas"
    radar = "radar" if not CP.radarUnavailable else "no radar"

    rows = {
      "NrdrCarTuneInfo": " | ".join((str(CP.carFingerprint), f"EPS {eps_short}", gas, radar, controller)),
      "NrdrCarControllerInfo": controller_info,
      "NrdrCarHandcraftedInfo": handcrafted,
      "NrdrCarPidLowInfo": pid_low,
      "NrdrCarPidMidInfo": pid_mid,
      "NrdrCarPidHighInfo": pid_high,
      "NrdrCarDampingInfo": damping,
      "NrdrCarCenterInfo": center,
      "NrdrCarNnlcInfo": nnlc,
      "NrdrCarSteerRatioInfo": steer_ratio,
      "NrdrCarLearningInfo": learning,
      "NrdrCarHelpersInfo": helpers,
    }
    rows["NrdrCarTuneDetails"] = "\n".join((
      "VEHICLE",
      f"Fingerprint: {CP.carFingerprint}",
      f"EPS firmware: {eps}",
      f"Gas pedal interceptor: {interceptor}",
      f"Radar messages used: {str(not CP.radarUnavailable).lower()}",
      "",
      "CONTROLLER",
      controller_info,
      f"Handcrafted profile: {handcrafted}",
      f"NNLC: {nnlc}",
      "",
      f"LATERAL PID BASE ({pid_speeds})",
      pid_base,
      f"F {pid_feedforward}",
      "",
      "LIVE TUNING KNOBS",
      f"PID low: {pid_low}",
      f"PID mid: {pid_mid}",
      f"PID highway: {pid_high}",
      f"Damping: {damping}",
      f"Center: {center}",
      f"Steer ratio: {steer_ratio}",
      f"Learning: {learning}",
      f"Helpers: {helpers}",
      "",
      "LONGITUDINAL PID",
      long_base,
      "",
      "GEOMETRY",
      f"Steer ratio base: {float(CP.steerRatio):g}",
      f"Actuator delay: {float(CP.steerActuatorDelay):g} s",
      f"Wheelbase: {float(CP.wheelbase):g} m | mass: {float(CP.mass):.0f} kg",
    ))
    return rows

  def publish(self) -> None:
    try:
      cp_bytes = self.params.get("CarParamsPersistent") or self.params.get("CarParams")
      if not cp_bytes:
        return
      with car.CarParams.from_bytes(cp_bytes) as CP:
        values = self._build(CP)
      self._publish(values)
    except Exception:
      cloudlog.exception("nrdr_remoted: failed to publish car tune report")
