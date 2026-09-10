"""Static UI metadata for NRDR-owned parameters.

This module intentionally depends only on the Python standard library and the
standard-library-only NRDR parameter catalog. Runtime UI and Params imports
belong in adapters outside ``openpilot.nrdr.params``.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from types import MappingProxyType
from typing import Final

from openpilot.nrdr.params.generated.keys import NrdrParamKey
from openpilot.nrdr.params.specs import PARAM_SPECS_BY_KEY, ParamLifecycle, ParamType


def tr_noop(text: str) -> str:
  """Mark declarative UI text for the static translation extractor."""
  return text


class UiWidget(StrEnum):
  OPTION = "option"


class UiDescriptionSource(StrEnum):
  DESCRIPTION = "description"
  DETAILS = "details"


class UiRemoteWritePolicy(StrEnum):
  """Server-side road-state policy, separate from frontend enablement."""

  ANY_ROAD_STATE = "any_road_state"
  OFFROAD_ONLY = "offroad_only"


@dataclass(frozen=True, slots=True)
class NumericUiMetadata:
  minimum: int | float
  maximum: int | float
  step: int | float
  unit: str | None = None
  display_multiplier: int | float = 1
  display_precision: int = 0
  display_suffix: str = ""

  def format_display_value(self, value: int | float | Decimal) -> str:
    scaled = Decimal(str(value)) * Decimal(str(self.display_multiplier))
    return f"{scaled:.{self.display_precision}f}{self.display_suffix}"


@dataclass(frozen=True, slots=True)
class ParamUiMetadata:
  key: NrdrParamKey
  widget: UiWidget
  title: str
  native_title: str
  description: str
  details: str | None
  native_description_source: UiDescriptionSource
  numeric: NumericUiMetadata
  edit_policies: tuple[str, ...]
  remote_write_policy: UiRemoteWritePolicy

  @property
  def native_description(self) -> str:
    if self.native_description_source is UiDescriptionSource.DETAILS:
      if self.details is None:
        raise ValueError(f"{self.key.value}: native description selects missing details")
      return self.details
    return self.description


_PERCENT_SCALE: Final = NumericUiMetadata(
  minimum=0,
  maximum=500,
  step=5,
  unit="%",
  display_suffix="%",
)
NRDR_UI_METADATA: Final = (
  ParamUiMetadata(
    key=NrdrParamKey.NRDR_INTERPOLATED_TORQUE_LAT_ACCEL_FACTOR,
    widget=UiWidget.OPTION,
    title=tr_noop("Spoofed Lateral Acceleration Factor"),
    native_title=tr_noop("Spoofed Lateral Acceleration Factor (Default: 5.0 m/s²)"),
    description=tr_noop("Sets how much lateral acceleration the legacy torque half treats as full normalized steering torque."),
    details=tr_noop(
      "Higher values ask the torque half for less steering for the same planned curve. It scales Torque feedback error and " +
      "non-friction feedforward, but never direct friction. This is m/s², not m/s. Changes apply on the next engagement."
    ),
    native_description_source=UiDescriptionSource.DETAILS,
    numeric=NumericUiMetadata(minimum=0.1, maximum=10.0, step=0.1, unit="m/s²", display_precision=1, display_suffix=" m/s²"),
    edit_policies=(),
    remote_write_policy=UiRemoteWritePolicy.ANY_ROAD_STATE,
  ),
  ParamUiMetadata(
    key=NrdrParamKey.NRDR_INTERPOLATED_TORQUE_FRICTION,
    widget=UiWidget.OPTION,
    title=tr_noop("Low-Speed Torque Friction (Below 25mph)"),
    native_title=tr_noop("Low-Speed Torque Friction (Below 25mph) (Default: 0.12)"),
    description=tr_noop("Sets direct normalized steering torque for the legacy torque half below 25 mph."),
    details=tr_noop(
      "Helps the legacy torque half overcome rack friction. A ±1 mph handoff blends this value smoothly into Standard from " +
      "24-26 mph. It is independent of the lateral acceleration factor. Changes apply on the next engagement."
    ),
    native_description_source=UiDescriptionSource.DETAILS,
    numeric=NumericUiMetadata(minimum=0.0, maximum=1.0, step=0.01, display_precision=2),
    edit_policies=(),
    remote_write_policy=UiRemoteWritePolicy.ANY_ROAD_STATE,
  ),
  ParamUiMetadata(
    key=NrdrParamKey.NRDR_INTERPOLATED_TORQUE_FRICTION_STANDARD,
    widget=UiWidget.OPTION,
    title=tr_noop("Standard-Speed Torque Friction (25-50mph)"),
    native_title=tr_noop("Standard-Speed Torque Friction (25-50mph) (Default: 0.10)"),
    description=tr_noop("Sets direct normalized steering torque for the legacy torque half between 25 and 50 mph."),
    details=tr_noop(
      "Helps the legacy torque half overcome rack friction. ±1 mph handoffs blend Low into this value from 24-26 mph and this " +
      "value into Highway from 49-51 mph. It is independent of the lateral acceleration factor. Changes apply on the next engagement."
    ),
    native_description_source=UiDescriptionSource.DETAILS,
    numeric=NumericUiMetadata(minimum=0.0, maximum=1.0, step=0.01, display_precision=2),
    edit_policies=(),
    remote_write_policy=UiRemoteWritePolicy.ANY_ROAD_STATE,
  ),
  ParamUiMetadata(
    key=NrdrParamKey.NRDR_INTERPOLATED_TORQUE_FRICTION_HIGHWAY,
    widget=UiWidget.OPTION,
    title=tr_noop("Highway Torque Friction (50mph+)"),
    native_title=tr_noop("Highway Torque Friction (50mph+) (Default: 0.06)"),
    description=tr_noop("Sets direct normalized steering torque for the legacy torque half above 50 mph."),
    details=tr_noop(
      "Helps the legacy torque half overcome rack friction. A ±1 mph handoff blends Standard smoothly into this value from " +
      "49-51 mph. It is independent of the lateral acceleration factor. Changes apply on the next engagement."
    ),
    native_description_source=UiDescriptionSource.DETAILS,
    numeric=NumericUiMetadata(minimum=0.0, maximum=1.0, step=0.01, display_precision=2),
    edit_policies=(),
    remote_write_policy=UiRemoteWritePolicy.ANY_ROAD_STATE,
  ),
  ParamUiMetadata(
    key=NrdrParamKey.LAT_P_SCALE_LOW_SPEED,
    widget=UiWidget.OPTION,
    title=tr_noop("Low Speed Proportional Scale (Below 25mph)"),
    native_title=tr_noop("Low Speed Proportional Scale (Below 25mph) (Default: 100%)"),
    description=tr_noop("Scales the proportional (P) term below 25 mph."),
    details=tr_noop("Scales the proportional (P) term below 25 mph. Higher = more error correction (tighter, can cut corners); lower = looser with wider swings."),  # noqa: E501
    native_description_source=UiDescriptionSource.DETAILS,
    numeric=_PERCENT_SCALE,
    edit_policies=(),
    remote_write_policy=UiRemoteWritePolicy.ANY_ROAD_STATE,
  ),
  ParamUiMetadata(
    key=NrdrParamKey.LAT_I_SCALE_LOW_SPEED,
    widget=UiWidget.OPTION,
    title=tr_noop("Low Speed Integral Scale (Below 25mph)"),
    native_title=tr_noop("Low Speed Integral Scale (Below 25mph) (Default: 100%)"),
    description=tr_noop("Scales the integral (I) term below 25 mph."),
    details=tr_noop("Scales the integral (I) term below 25 mph. Builds correction over time to erase steady-state error; too high oscillates."),
    native_description_source=UiDescriptionSource.DETAILS,
    numeric=_PERCENT_SCALE,
    edit_policies=(),
    remote_write_policy=UiRemoteWritePolicy.ANY_ROAD_STATE,
  ),
  ParamUiMetadata(
    key=NrdrParamKey.LAT_P_SCALE_STANDARD,
    widget=UiWidget.OPTION,
    title=tr_noop("Standard Speed Proportional Scale (25-50mph)"),
    native_title=tr_noop("Standard Speed Proportional Scale (25-50mph) (Default: 100%)"),
    description=tr_noop("Scales the proportional (P) term between 25 and 50 mph."),
    details=None,
    native_description_source=UiDescriptionSource.DESCRIPTION,
    numeric=_PERCENT_SCALE,
    edit_policies=(),
    remote_write_policy=UiRemoteWritePolicy.ANY_ROAD_STATE,
  ),
  ParamUiMetadata(
    key=NrdrParamKey.LAT_I_SCALE_STANDARD,
    widget=UiWidget.OPTION,
    title=tr_noop("Standard Speed Integral Scale (25-50mph)"),
    native_title=tr_noop("Standard Speed Integral Scale (25-50mph) (Default: 100%)"),
    description=tr_noop("Scales the integral (I) term between 25 and 50 mph."),
    details=None,
    native_description_source=UiDescriptionSource.DESCRIPTION,
    numeric=_PERCENT_SCALE,
    edit_policies=(),
    remote_write_policy=UiRemoteWritePolicy.ANY_ROAD_STATE,
  ),
  ParamUiMetadata(
    key=NrdrParamKey.LAT_P_SCALE_HIGHWAY,
    widget=UiWidget.OPTION,
    title=tr_noop("Highway Proportional Scale (50mph+)"),
    native_title=tr_noop("Highway Proportional Scale (50mph+) (Default: 100%)"),
    description=tr_noop("Scales the proportional (P) term above 50 mph."),
    details=None,
    native_description_source=UiDescriptionSource.DESCRIPTION,
    numeric=_PERCENT_SCALE,
    edit_policies=(),
    remote_write_policy=UiRemoteWritePolicy.ANY_ROAD_STATE,
  ),
  ParamUiMetadata(
    key=NrdrParamKey.LAT_I_SCALE_HIGHWAY,
    widget=UiWidget.OPTION,
    title=tr_noop("Highway Integral Scale (50mph+)"),
    native_title=tr_noop("Highway Integral Scale (50mph+) (Default: 100%)"),
    description=tr_noop("Scales the integral (I) term above 50 mph."),
    details=None,
    native_description_source=UiDescriptionSource.DESCRIPTION,
    numeric=_PERCENT_SCALE,
    edit_policies=(),
    remote_write_policy=UiRemoteWritePolicy.ANY_ROAD_STATE,
  ),
)

NRDR_UI_METADATA_BY_KEY: Final = MappingProxyType({metadata.key.value: metadata for metadata in NRDR_UI_METADATA})


def get_ui_metadata(key: str | NrdrParamKey) -> ParamUiMetadata:
  key_value = key.value if isinstance(key, NrdrParamKey) else key
  try:
    return NRDR_UI_METADATA_BY_KEY[key_value]
  except KeyError as exc:
    raise KeyError(f"no NRDR UI metadata for {key_value!r}") from exc


def validate_ui_metadata(metadata_entries: tuple[ParamUiMetadata, ...] = NRDR_UI_METADATA) -> tuple[str, ...]:
  errors: list[str] = []
  seen: set[str] = set()
  for metadata in metadata_entries:
    key = metadata.key.value
    if key in seen:
      errors.append(f"{key}: duplicate UI metadata")
      continue
    seen.add(key)

    spec = PARAM_SPECS_BY_KEY.get(key)
    if spec is None:
      errors.append(f"{key}: missing from parameter catalog")
      continue
    if spec.lifecycle is not ParamLifecycle.SETTING:
      errors.append(f"{key}: UI metadata requires setting lifecycle, got {spec.lifecycle.value}")
    if metadata.widget is not UiWidget.OPTION:
      errors.append(f"{key}: first UI metadata slice supports option widgets only")
    if spec.param_type not in (ParamType.INT, ParamType.FLOAT):
      errors.append(f"{key}: option widget requires numeric parameter type")

    numeric = metadata.numeric
    minimum = Decimal(str(numeric.minimum))
    maximum = Decimal(str(numeric.maximum))
    step = Decimal(str(numeric.step))
    if minimum > maximum:
      errors.append(f"{key}: minimum exceeds maximum")
    if step <= 0:
      errors.append(f"{key}: step must be positive")

    if spec.default is None:
      errors.append(f"{key}: numeric UI setting is missing a registry default")
    else:
      try:
        default = Decimal(spec.default)
      except InvalidOperation:
        errors.append(f"{key}: invalid numeric registry default {spec.default!r}")
      else:
        if not minimum <= default <= maximum:
          errors.append(f"{key}: registry default is outside the UI range")
        elif step > 0 and (default - minimum) % step:
          errors.append(f"{key}: registry default is not on the UI step grid")
        expected_native_title = f"{metadata.title} (Default: {numeric.format_display_value(default)})"
        if metadata.native_title != expected_native_title:
          errors.append(f"{key}: native title default does not match the registry default")

    if metadata.native_description_source is UiDescriptionSource.DETAILS and metadata.details is None:
      errors.append(f"{key}: native description selects missing details")

  return tuple(errors)


__all__ = (
  "NRDR_UI_METADATA",
  "NRDR_UI_METADATA_BY_KEY",
  "NumericUiMetadata",
  "ParamUiMetadata",
  "UiDescriptionSource",
  "UiRemoteWritePolicy",
  "UiWidget",
  "get_ui_metadata",
  "validate_ui_metadata",
)
