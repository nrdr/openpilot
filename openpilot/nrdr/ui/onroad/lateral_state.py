"""Readiness and union selection for read-only developer steering displays."""


def lateral_control_kind(sm, started_frame: int) -> str | None:
  received = sm.recv_frame["controlsState"]
  if received <= 0 or received < started_frame or not sm.alive["controlsState"] or not sm.valid["controlsState"]:
    return None
  try:
    return sm["controlsState"].lateralControlState.which()
  except (AttributeError, ValueError):
    # A future/unrecognized union discriminant is unavailable display data.
    return None
