"""June 2026 engagement chimes and their original automatic volume curve."""

import math


def june_engagement_files(device_type: str) -> dict[str, str]:
  suffix = "_tizi" if device_type == "tizi" else ""
  return {"engage": f"engage{suffix}.wav", "disengage": f"disengage{suffix}.wav", "refuse": "refuse.wav"}


def june_engagement_volume(weighted_db: float, device_type: str) -> float:
  ambient_db, volume_base = (30, 10) if device_type == "tizi" else (24, 20)
  volume = (weighted_db - ambient_db) / 30 * 0.9 + 0.1
  return math.pow(volume_base, min(1.0, max(0.1, volume)) - 1)
