from decimal import Decimal

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
from openpilot.sunnypilot.models.helpers import get_active_bundle
from openpilot.sunnypilot.nrdr.steer_ratio_tuning import (
  CLARITY_RAW_NEAR_LOCK_ANGLE_DEG,
  CLARITY_RAW_NEAR_LOCK_LEFT_COUNT,
  CLARITY_RAW_NEAR_LOCK_RIGHT_COUNT,
  CLARITY_RAW_NEAR_LOCK_SAMPLE_COUNT,
  CLARITY_RAW_SOURCE_BLOB,
  CLARITY_RAW_SOURCE_COMMIT,
  SteerRatioMode,
  SteerRatioResolver,
  clarity_raw_steer_ratio_at,
  parse_steer_ratio_mode,
)


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
  def _model_identity(bundle) -> str:
    display_name = str(getattr(bundle, "displayName", "")).strip() if bundle is not None else ""
    internal_name = str(getattr(bundle, "internalName", "")).strip() if bundle is not None else ""
    name = display_name or internal_name or "default/unidentified model"
    if internal_name and internal_name not in name:
      name += f" [{internal_name}]"
    try:
      artifact_sha256 = str(bundle.models[0].artifact.downloadUri.sha256).strip()
    except (AttributeError, IndexError, TypeError):
      artifact_sha256 = ""
    artifact = artifact_sha256[:12] if artifact_sha256 else "no artifact SHA"
    return f"{name} @ {artifact}"

  def _steer_ratio_mode(self) -> SteerRatioMode:
    return parse_steer_ratio_mode(self._value("NrdrSteerRatioMode"))

  def _steer_ratio_info(self, CP) -> str:
    selection = SteerRatioResolver(CP, self.params)
    mode = selection.mode
    base = selection.cp_steer_ratio
    if mode is SteerRatioMode.COMMA:
      return f"Comma learner scalar | CP {base:g} until first valid sample, then holds last good value through validity flickers"
    if mode is SteerRatioMode.NRDR_RAW:
      if selection.available:
        old_tail_effective = clarity_raw_steer_ratio_at(247.5)
        near_lock_effective = clarity_raw_steer_ratio_at(CLARITY_RAW_NEAR_LOCK_ANGLE_DEG)
        return " ".join((
          "NRDR Raw | original non-monotonic Clarity atan-domain medians preserved |",
          f"bilateral {CLARITY_RAW_NEAR_LOCK_ANGLE_DEG:g} deg anchor",
          f"n={CLARITY_RAW_NEAR_LOCK_SAMPLE_COUNT}",
          f"L/R={CLARITY_RAW_NEAR_LOCK_LEFT_COUNT}/{CLARITY_RAW_NEAR_LOCK_RIGHT_COUNT} |",
          "interpolate raw, then VehicleModel conversion |",
          f"effective 247.5={old_tail_effective:.6f}, {CLARITY_RAW_NEAR_LOCK_ANGLE_DEG:g}={near_lock_effective:.6f} |",
          f"clamps at {CLARITY_RAW_NEAR_LOCK_ANGLE_DEG:g} deg | no smoothing or lane fade |",
          f"source {CLARITY_RAW_SOURCE_COMMIT}@{CLARITY_RAW_SOURCE_BLOB} + audited bilateral tail",
        ))
      return f"NRDR Raw unavailable for {CP.carFingerprint} -> CP static {base:g}"
    if mode is SteerRatioMode.FIRMWARE:
      if selection.available:
        return f"Firmware | exact {selection.vgr_profile.name} relative map | immutable CP anchor {base:g} | no lane fade"
      return f"Firmware map unavailable/mismatched -> CP static {base:g}"

    if not selection.available:
      return f"Manual overrides unavailable for {CP.carFingerprint} -> CP static {base:g}"
    outer_angle = selection.outer_angle
    center = selection.settings.manual_center
    final = selection.settings.manual_final
    return f"Manual | {center:.2f} center -> {final:.2f} final by {outer_angle:.1f} deg | no lane fade"

  def _controller_info(self, CP, controller: str, handcrafted_enabled: bool, profile) -> str:
    if controller == "PID/NNLC":
      firmware_pid_only = self._steer_ratio_mode() is SteerRatioMode.FIRMWARE and get_honda_vgr_profile(CP) is not None
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
    model = get_active_bundle(self.params)
    profile = get_handcrafted_lateral_profile(CP.carFingerprint)
    handcrafted_enabled = is_handcrafted_lateral_enabled(CP.carFingerprint, self.params)
    handcrafted = f"{profile.name} (v{profile.version})" if handcrafted_enabled and profile is not None else "OFF"
    controller_info = self._controller_info(CP, controller, handcrafted_enabled, profile)

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
    if self._steer_ratio_mode() is SteerRatioMode.FIRMWARE and get_honda_vgr_profile(CP) is not None:
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
      f"Driving model: {self._model_identity(model)}",
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
