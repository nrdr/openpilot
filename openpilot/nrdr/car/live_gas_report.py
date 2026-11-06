"""Read-only saved learner values for Sunnylink's Live Learning Gas info panel."""
from datetime import UTC, datetime
import math

from openpilot.nrdr.car.mvl_state import MVL_STATE_KEYS


# Includes the original 10/16 m/s nodes between the newer mph nodes. This is
# display metadata only; it must not import or construct a vehicle controller.
GAS_NODES = (("00", "0"), ("10", "10"), ("20", "20"), ("low", "22.4"), ("30", "30"), ("", "35.8+"))


def _saved_number(params, name: str) -> str:
  try:
    raw = params.get_raw(MVL_STATE_KEYS[name])
    if raw is None or raw in ("", b""):
      return "not saved"
    # A corrupt bool is not a learned floating-point value.
    value = float(raw) if not isinstance(raw, bool) else math.nan
  except (TypeError, ValueError, OverflowError):
    return "invalid"
  return f"{value:.4g}" if math.isfinite(value) else "invalid"


def live_gas_details(params, *, now: datetime | None = None) -> str:
  """Report stored values, not active gains, training time, or convergence.

  PCM snapshots are queued roughly once a minute and written one key/second.
  The scalar Bosch/interceptor learner shares some keys but not these bands;
  label the table explicitly rather than infer the active platform from it.
  No Params writes, fallback defaults, mtime guesses, or arbitrary raw strings.
  """
  timestamp = (now or datetime.now(UTC)).astimezone(UTC).strftime("%b %d, %H:%M UTC")
  lines = [
    f"Saved snapshot: {timestamp}. Reload page to refresh.",
    "Training time: not recorded. No completion score.",
    "Shared Honda PCM values; these may be from another car.",
    "",
    "PCM gas gain / offset (m/s²), by speed:",
  ]
  for suffix, speed in GAS_NODES:
    suffix = f"_{suffix}" if suffix else ""
    gain = _saved_number(params, f"gas_factor{suffix}")
    offset = _saved_number(params, f"gas_alpha{suffix}")
    lines.append(f"{speed} mph: {gain} / {offset}")
  lines += [
    f"Drag factor: {_saved_number(params, 'wind_factor')}",
    f"PCM response coefficient: {_saved_number(params, 'feedforward')}",
    "",
    "Gas values shape demand, not pedal position. Drag is an estimate, not measured wind. "
    + "Response models PCM smoothing, not PID feedforward.",
    "Saved values lag driving. Full MVL mode ignores custom PCM shaping and wind-brake choices. "
    + "This PCM table does not describe Bosch/interceptor learning. Reset clears gas/wind only.",
  ]
  # Sunnylink's info modal preserves <br>, not plain newlines or Markdown.
  return "<br>".join(lines)
