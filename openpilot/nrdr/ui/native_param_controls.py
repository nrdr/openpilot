"""Thin native-UI adapter for declarative NRDR parameter metadata."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from openpilot.nrdr.params import NrdrParamKey, NumericUiMetadata, ParamUiMetadata, UiWidget, get_ui_metadata
from openpilot.nrdr.params.specs import PARAM_SPECS_BY_KEY, ParamType

if TYPE_CHECKING:
  from openpilot.system.ui.sunnypilot.widgets.list_view import ListItemSP


@dataclass(frozen=True, slots=True)
class NativeOptionSpec:
  param: str
  title: str
  description: str
  min_value: int
  max_value: int
  value_change_step: int
  use_float_scaling: bool
  numeric: NumericUiMetadata
  native_scale: int

  def format_label(self, native_value: int) -> str:
    stored_value = Decimal(native_value) / self.native_scale
    return self.numeric.format_display_value(stored_value)


def _native_tick(value: int | float, scale: int, key: str) -> int:
  scaled = Decimal(str(value)) * scale
  integral = scaled.to_integral_value()
  if scaled != integral:
    raise ValueError(f"{key}: {value!r} cannot be represented at native scale {scale}")
  return int(integral)


def get_native_option_spec(key: str | NrdrParamKey) -> NativeOptionSpec:
  metadata: ParamUiMetadata = get_ui_metadata(key)
  if metadata.widget is not UiWidget.OPTION:
    raise ValueError(f"{metadata.key.value}: native option adapter requires an option widget")

  param_type = PARAM_SPECS_BY_KEY[metadata.key.value].param_type
  native_scale = 100 if param_type is ParamType.FLOAT else 1
  numeric = metadata.numeric
  return NativeOptionSpec(
    param=metadata.key.value,
    title=metadata.native_title,
    description=metadata.native_description,
    min_value=_native_tick(numeric.minimum, native_scale, metadata.key.value),
    max_value=_native_tick(numeric.maximum, native_scale, metadata.key.value),
    value_change_step=_native_tick(numeric.step, native_scale, metadata.key.value),
    use_float_scaling=param_type is ParamType.FLOAT,
    numeric=numeric,
    native_scale=native_scale,
  )


def option_item_from_metadata(key: str | NrdrParamKey) -> ListItemSP:
  # Keep runtime UI dependencies out of module import so build/validation tools
  # can inspect the adapter before pyray and native Params are available.
  from openpilot.system.ui.lib.multilang import tr
  from openpilot.system.ui.sunnypilot.widgets.list_view import option_item_sp

  spec = get_native_option_spec(key)
  return option_item_sp(
    param=spec.param,
    title=lambda: tr(spec.title),
    min_value=spec.min_value,
    max_value=spec.max_value,
    value_change_step=spec.value_change_step,
    description=lambda: tr(spec.description),
    label_callback=spec.format_label,
    use_float_scaling=spec.use_float_scaling,
  )


__all__ = ("NativeOptionSpec", "get_native_option_spec", "option_item_from_metadata")
