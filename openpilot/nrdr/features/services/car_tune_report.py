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
    requested = self.params.get_bool("NrdrInterpolatedTorquePifBlend")
    cp_sp = self._cp_sp()
    supported = cp_sp is not None and supports_interpolated_torque_pif(CP, cp_sp)
    enabled = requested and supported
    share = int(max(0.0, min(100.0, float(self._value("NrdrInterpolatedTorqueShare")))))
    configured = " | ".join((
      f"Torque {share}% / P/I/F {100 - share}%",
      f"LAF {float(self._value('NrdrInterpolatedTorqueLatAccelFactor')):g} m/s²",
      "friction " + " / ".join((
        f"Low {float(self._value('NrdrInterpolatedTorqueFriction')):g}",
        f"Standard {float(self._value('NrdrInterpolatedTorqueFrictionStandard')):g}",
        f"Highway {float(self._value('NrdrInterpolatedTorqueFrictionHighway')):g}",
      )),
    ))
    if enabled:
      return (
        f"ON | {configured} | P/I/F angle feedback | Torque angle→yaw 2-5 m/s, calibrated yaw >=5 m/s | " +
        "invalid required yaw: exact P/I/F output + Torque state held | generic f13 yaw branch (not Honda road-proven) | " +
        "engagement-latched | NNLC bypassed/reset",
        True,
      )
    if requested:
      return (
        f"requested ON but unavailable for this car | Torque 0% / P/I/F 100% | P/I/F unchanged | stored: {configured}",
        False,
      )
    return f"OFF | Torque 0% / P/I/F 100% | P/I/F unchanged | stored next engagement: {configured}", False

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
    return "PID/NNLC" if str(CP.carFingerprint) == "HONDA_CLARITY" else CP.lateralTuning.which().upper()

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
    if selection.effective_mode is SteerRatioMode.MANUAL:
      return (f"{prefix} | {selection.manual_center:.2f} center -> {selection.manual_final:.2f} final " +
              f"by {selection.manual_outer_angle_deg:g} deg | no lane fade")
    if selection.effective_mode is SteerRatioMode.COMMA:
      return (f"{prefix} | last valid live vehicleParameters.steerRatio scalar | " +
              f"CP {selection.cp_ratio:g} until the first valid sample")
    if selection.effective_mode is SteerRatioMode.NRDR_RAW:
      return (f"{prefix} | {selection.raw_profile.name} | audited near-lock anchor 435.7 deg " +
              f"(VM ratio {selection.raw_profile.ratio_at(435.7):.6f}), endpoint-clamped | " +
              f"source {selection.raw_profile.provenance}")
    return (f"{prefix} | {selection.firmware_profile.name} relative Table-A shape | " +
            f"immutable CP center anchor {selection.cp_ratio:g} | no lane fade")

  def _controller_info(self, controller: str, steer_ratio: SteerRatioSelection) -> str:
    if controller == "PID/NNLC":
      if steer_ratio.firmware_vgr_selected:
        nnlc = "PID only | NNLC unavailable in firmware EPS mode"
      else:
        nnlc = "PID/NNLC hybrid | PID for lane changes" if self._state("NrdrNnlcEnabled") == "ON" \
          else "PID only | NNLC disabled"
    else:
      nnlc = controller
    return nnlc

  def _build(self, CP) -> dict[str, str]:
    eps = self._eps_firmware(CP)
    eps_short = eps.rsplit(",", 1)[-1].strip() if "," in eps else eps
    interceptor = self._gas_interceptor()
    controller = self._controller_name(CP)
    steer_ratio_selection = resolve_steer_ratio_selection(CP, self.params)
    handcrafted = handcrafted_lateral_profile_status(CP, self._cp_sp(), self.params)
    controller_info = self._controller_info(controller, steer_ratio_selection)
    interpolated, interpolated_enabled = self._interpolated_torque_pif_info(CP)
    if interpolated_enabled:
      controller_info += f" | {interpolated}"

    pid_base, pid_feedforward, pid_speeds = self._pid_info(CP)
    longitudinal = CP.longitudinalTuning
    long_base = _longitudinal_pid_info(longitudinal)

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
    if steer_ratio_selection.firmware_vgr_selected:
      nnlc += " | inactive in firmware EPS mode"
    if interpolated_enabled:
      nnlc += " | inactive while Interpolated Torque/PIF Blend is active"
    steer_ratio = self._steer_ratio_info(steer_ratio_selection)
    learning = f"stiffness {self._state('NrdrLearnStiffness')} | angle {self._state('NrdrLearnAngleOffset')}"
    helpers = f"stiction {self._state('NrdrLatStiction')} | StarPilot {self._state('NrdrStarPilotPid')} | {interpolated}"
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
      # The durable request intentionally stays true for the next safe retry.
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
