from openpilot.common.params import UnknownKeyName


def read_bool(params, key: str, default: bool = False) -> bool:
  try:
    value = params.get(key)
  except UnknownKeyName:
    return default
  if value is None:
    return default
  if isinstance(value, bytes):
    return value.strip().lower() not in (b"", b"0", b"false")
  if isinstance(value, str):
    return value.strip().lower() not in ("", "0", "false")
  return bool(value)


def read_float(params, key: str, default: float, min_value: float | None = None,
               max_value: float | None = None, scale: float = 1.0) -> float:
  try:
    value = params.get(key)
  except UnknownKeyName:
    value = None

  try:
    value = default if value is None else float(value.decode() if isinstance(value, bytes) else value) / scale
  except (TypeError, ValueError):
    value = default

  if min_value is not None:
    value = max(min_value, value)
  if max_value is not None:
    value = min(max_value, value)
  return value
