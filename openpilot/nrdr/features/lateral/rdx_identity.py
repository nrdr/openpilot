"""Exact hardware/transport checks plus an explicit, vehicle-bound owner receipt.

The diagnostic version identifies the family, NOT the contents of the flash.
No control, UI, backup or discovery path creates a receipt.
"""
from functools import lru_cache
import hashlib
import re

RDX_CARS = ("ACURA_RDX_3G", "ACURA_RDX_3G_MMR")
# James publishes only the eight-character RWD prefix (3dd8b91b). Never match a prefix.
# Leave admission closed until the original Route-A Trk1641 RomCRC RWD is independently pinned.
RDX_ROUTE_A_SHA256: str | None = None


@lru_cache(maxsize=1)
def _owner_receipt() -> bytes | None:
  # Read once per process, not in the per-frame control loop. Offroad changes require restart.
  try:
    from openpilot.common.params import Params, UnknownKeyName
  except (ImportError, OSError):
    return None
  try:
    return Params().get_raw("NrdrRdxRouteAConfirmation")
  except (UnknownKeyName, OSError, ValueError):
    return None


def confirmed_rdx(CP) -> bool:
  fp = str(getattr(CP, "carFingerprint", ""))
  if fp not in RDX_CARS or getattr(CP, "brand", None) != "honda":
    return False
  digest = RDX_ROUTE_A_SHA256
  if digest is None or re.fullmatch(r"3dd8b91b[0-9a-f]{56}", digest) is None:
    return False
  vin = getattr(CP, "carVin", "")
  if not isinstance(vin, str) or re.fullmatch(r"[A-HJ-NPR-Z0-9]{17}", vin) is None or vin == "0" * 17:
    return False
  if (getattr(CP, "dashcamOnly", True) or getattr(CP, "passive", True) or getattr(CP, "notCar", True)
      or getattr(CP, "fuzzyFingerprint", True) or str(getattr(CP, "fingerprintSource", "")) != "fw"):
    return False
  params = getattr(CP, "lateralParams", None)
  if getattr(getattr(CP, "lateralTuning", None), "which", lambda: None)() != "pid":
    return False
  if tuple(getattr(params, "torqueBP", ())) != (0, 4096) or tuple(getattr(params, "torqueV", ())) != (0, 4096):
    return False
  # Same query contract as opendbc's transport gate. Never normalize stock hyphens, trailing
  # bytes or conflicting diagnostic replies into a positive match, even with a stale SP flag.
  images = [(getattr(fw, "address", None), getattr(fw, "subAddress", None), getattr(fw, "fwVersion", None),
             getattr(fw, "logging", None)) for fw in getattr(CP, "carFw", ()) if fw.ecu == "eps" and not getattr(fw, "logging", False)]
  if not images or not all(image == (0x18DA30F1, 0, b"39990-TJB,A220\x00\x00", False) for image in images):
    return False
  vehicle = hashlib.sha256(vin.encode("ascii")).hexdigest()
  return _owner_receipt() == f"route-a-v1:{fp}:{vehicle}:{digest}".encode("ascii")
