from decimal import Decimal

from openpilot.cereal import custom, messaging
from opendbc.car.structs import car
from opendbc.car.car_helpers import interfaces
from openpilot.common.swaglog import cloudlog
from openpilot.nrdr.params import (
  consume_handcrafted_lateral_request,
  handcrafted_lateral_profile_status,
)
from openpilot.nrdr.features.lateral.steer_ratio_tuning import (
  SteerRatioMode,
  SteerRatioSelection,
  resolve_steer_ratio_selection,
)
from openpilot.nrdr.features.lateral.interpolated_torque_pif import supports_interpolated_torque_pif
from openpilot.sunnypilot.selfdrive.car.opendbc_config import build_sunnypilot_car_config


def _format_values(values) -> str:
  return "/".join(f"{float(value):g}" for value in values)


def _format_decimal(value) -> str:
  number = Decimal(f"{float(value):g}")
  return "0" if number == 0 else format(number, "f")


def _format_decimal_values(values) -> str:
  return "/".join(_format_decimal(value) for value in values)


def _longitudinal_pid_info(longitudinal) -> str:
  deprecated = longitudinal.deprecated
  return f"P {_format_values(deprecated.kpV)} | I {_format_values(longitudinal.kiV)} | F {_format_decimal(deprecated.kf)}"


def _schedule_label(value_count: int) -> str:
  return {
    1: "all speeds",
    3: "0 / 25 / 50 mph",
    4: "0 / <25 / 25 / 50 mph",
  }.get(value_count, "custom breakpoints")


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
    cp_sp = self._cp_sp()
    if cp_sp is None:
      return "n/a"
    return str(bool(cp_sp.enableGasInterceptor)).lower()

  def _cp_sp(self):
    cp_sp_bytes = self.params.get("CarParamsSPPersistent")
    return messaging.log_from_bytes(cp_sp_bytes, custom.CarParamsSP) if cp_sp_bytes else None

  def _interpolated_torque_pif_info(self, CP) -> tuple[str, bool]:
    supported = supports_interpolated_torque_pif(CP, self._cp_sp())
    enabled = supported and self.params.get("NrdrLateralController") != 1
    return ("Fixed 1% torque / 99% PIF | LAF 10 | friction 1/1/1 | optimized lane changes bypass blend"
            if enabled else "PIF blend inactive"), enabled

  def _pid_source(self, CP):
    if CP.lateralTuning.which() == "pid":
      return CP
    CarInterface = interfaces[CP.carFingerprint]
    # Reconstructing CarParams requires opendbc's complete host-owned multi-brand config.
    reconstructed = CarInterface.get_non_essential_params(
      CP.carFingerprint,
      build_sunnypilot_car_config(self.params, start_worker=False),
    )
    CarInterface.get_non_essential_params_sp(reconstructed, CP.carFingerprint)
    return reconstructed if reconstructed.lateralTuning.which() == "pid" else CP

  def _controller_name(self, CP) -> str:
    return "PIF Control" if str(CP.carFingerprint) == "HONDA_CLARITY" else CP.lateralTuning.which().upper()

  def _pid_info(self, CP) -> tuple[str, str, str]:
    source = self._pid_source(CP)
    if source.lateralTuning.which() != "pid":
      return f"{CP.lateralTuning.which().upper()} (no PID base)", "n/a", "n/a"

    pid = source.lateralTuning.pid
    gains = f"P {_format_values(pid.kpV)} | I {_format_values(pid.kiV)}"
    feedforward = (
      _format_decimal_values(pid.kfV)
      if len(pid.kfV)
      else _format_decimal(pid.kf)
    )
    p_speeds = _schedule_label(len(pid.kpV))
    i_speeds = _schedule_label(len(pid.kiV))
    f_speeds = _schedule_label(len(pid.kfV)) if len(pid.kfV) else "all speeds"
    if p_speeds == i_speeds == f_speeds:
      speeds = p_speeds
    elif p_speeds == i_speeds:
      speeds = f"P/I {p_speeds} | F {f_speeds}"
    else:
      speeds = f"P {p_speeds} | I {i_speeds} | F {f_speeds}"
    return gains, feedforward, speeds

  @staticmethod
  def _steer_ratio_info(selection: SteerRatioSelection) -> str:
    prefix = f"selected {selection.requested_label} | effective {selection.effective_label}"
    if not selection.available:
      return f"{prefix} | {selection.unavailable_reason} | CP {selection.cp_ratio:g}"
    if selection.hybrid is not None:
      return (f"{prefix} | equivalent angle-to-curvature blend | fixed 5-degree transition | " +
              "no speed-based switch | experimental, not road-validated | configured snapshot, not a live-consumption acknowledgement")
    if selection.effective_mode is SteerRatioMode.MANUAL:
      return (f"{prefix} | {selection.manual_center:.2f} center -> {selection.manual_final:.2f} final " +
              f"by {selection.manual_outer_angle_deg:g} deg | no lane fade")
    if selection.effective_mode is SteerRatioMode.COMMA:
      return (f"{prefix} | last valid live vehicleParameters.steerRatio scalar | " +
              f"CP {selection.cp_ratio:g} until the first valid sample")
    if selection.effective_mode is SteerRatioMode.NRDR_RAW:
      if selection.raw_profile.provisional:
        profile = selection.raw_profile
        lower, upper = profile.observed_angle_range
        return (f"{prefix} | {profile.name} | provisional data anchors {lower:g}-{upper:g} deg | " +
                f"VM ratio {profile.ratios[0]:.4f}->{profile.ratios[-1]:.4f} | linear interpolation | " +
                "outside range: nearest anchor held, unmeasured | no live learning or fitted speed correction | " +
                f"not road-validated | source {profile.provenance}")
      return (f"{prefix} | {selection.raw_profile.name} | audited near-lock anchor 435.7 deg " +
              f"(VM ratio {selection.raw_profile.ratio_at(435.7):.6f}), endpoint-clamped | " +
              f"source {selection.raw_profile.provenance}")
    return (f"{prefix} | {selection.firmware_profile.name} relative Table-A shape | " +
            f"immutable CP center anchor {selection.cp_ratio:g} | no lane fade")

  def _controller_info(self, controller: str, steer_ratio: SteerRatioSelection, CP) -> str:
    from openpilot.nrdr.features.lateral.controller_selection import yaw_controller_available
    if self.params.get("NrdrLateralController") == 1 and yaw_controller_available(CP, self._cp_sp()):
      return "Yaw Control (VFN EPS)"
    return controller.replace("PID/NNLC", "PIF Control")

  def _build(self, CP) -> dict[str, str]:
    eps = self._eps_firmware(CP)
    eps_short = eps.rsplit(",", 1)[-1].strip() if "," in eps else eps
    interceptor = self._gas_interceptor()
    controller = self._controller_name(CP)
    steer_ratio_selection = resolve_steer_ratio_selection(CP, self.params)
    handcrafted = handcrafted_lateral_profile_status(CP, self._cp_sp(), self.params)
    controller_info = self._controller_info(controller, steer_ratio_selection, CP)
    interpolated, interpolated_enabled = self._interpolated_torque_pif_info(CP)
    if interpolated_enabled:
      controller_info += f" | {interpolated}"

    pid_base, pid_feedforward, pid_speeds = self._pid_info(CP)
    longitudinal = CP.longitudinalTuning
    long_base = _longitudinal_pid_info(longitudinal)

    pid_low = f"P {self._value('LatPScaleLowSpeed')}% | I {self._value('LatIScaleLowSpeed')}% | F {self._value('LatFScaleLowSpeed')}%"
    pid_mid = f"P {self._value('LatPScaleStandard')}% | I {self._value('LatIScaleStandard')}% | F {self._value('LatFScaleStandard')}%"
    pid_high = f"P {self._value('LatPScaleHighway')}% | I {self._value('LatIScaleHighway')}% | F {self._value('LatFScaleHighway')}%"
    damping = " | ".join(f"{band} {self._value('NrdrLatRateDamping' + band)}%" for band in ("LowSpeed", "Standard", "Highway"))
    center = "".join((
      f"P-only {float(self._value('HondaCenterScale')) * 100.0:g}% | ",
      f"+/-{float(self._value('HondaCenterBoostThreshold')):g} deg | ",
      f"above {self._value('HondaCenterBoostMinSpeed')} mph",
    ))
    steer_ratio = self._steer_ratio_info(steer_ratio_selection)
    learning = f"stiffness {self._state('NrdrLearnStiffness')} | angle {self._state('NrdrLearnAngleOffset')}"
    helpers = f"stiction {self._state('NrdrLatStiction')} | {interpolated}"
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

  def consume_handcrafted_request(self) -> None:
    """Complete one pending offroad request; never reconcile a completed profile."""
    if not self.params.get_bool("NrdrHandcraftedLateralTune") or not self.params.get_bool("IsOffroad"):
      return
    try:
      cp_bytes = self.params.get("CarParamsPersistent") or self.params.get("CarParams")
      cp_sp = self._cp_sp()
      if not cp_bytes:
        return
      with car.CarParams.from_bytes(cp_bytes) as CP:
        fingerprint = str(CP.carFingerprint)
        written = consume_handcrafted_lateral_request(CP, cp_sp, self.params)
      if not written:
        return
      cloudlog.warning({
        "event": "handcrafted lateral profile applied once",
        "carFingerprint": fingerprint,
        "writtenParams": written,
      })
    except Exception:
      # I/O/verification failures retain the durable request for a safe retry;
      # identity and capability deferrals return quietly above.
      cloudlog.exception("nrdr_remoted: handcrafted lateral apply failed; request retained")

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


__all__ = ("CarTuneReporter", "_format_values")
