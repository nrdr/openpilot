"""
EPS CAN bus diagnostic tool for Honda/Acura EPS ECUs.

Checks whether the EPS (Electric Power Steering) ECU is alive on the CAN bus
after a potentially bad flash. Runs three checks:

  1. Passive sniff  – listen for any raw CAN traffic from the EPS physical addr
  2. UDS ping       – send Tester Present and wait for a positive response
  3. UDS session    – try Default → Extended diagnostic sessions and read the
                      Application Software ID (part number)

By default checks buses 0 and 1. Pass --bus to pin to a single bus.

Usage (on the comma device via SSH):
  python eps-diag.py            # check buses 0 and 1, address 0x18DA30F1
  python eps-diag.py -b 1       # pin to bus 1
  python eps-diag.py --scan     # brute-force scan all common Honda ECU addrs
"""

import argparse
import os
import sys
import time

from panda import Panda
from opendbc.car.structs import CarParams
from opendbc.car.uds import (
  UdsClient,
  SESSION_TYPE,
  DATA_IDENTIFIER_TYPE,
  NegativeResponseError,
)

# ── addresses ────────────────────────────────────────────────────────────────
EPS_ADDR = 0x18DA30F1   # tester → EPS  (29-bit, ISO 15765-4 physical)
DEFAULT_BUSES = (0, 1)


def response_addr_for(req_addr: int) -> int:
  """Honda ISO-TP physical response for a 29-bit request (0x18DAXXF1 → 0x18DAF1XX)."""
  return (req_addr & 0xFFFF0000) | 0x0000F100 | ((req_addr >> 8) & 0xFF)

# A handful of other Honda ECU addresses useful for --scan
HONDA_SCAN_ADDRS = [
  (0x18DA30F1, "EPS"),
  (0x18DA10F1, "PCM/ECM"),
  (0x18DA60F1, "Combination meter"),
  (0x18DA28F1, "SRS airbag"),
  (0x18DA0EF1, "VSA/ABS"),
  (0x18DA21F1, "Transmission"),
  (0x18DA3DF1, "LKAS camera"),
  (0x18DAB0F1, "LKAS camera alt"),
]

SNIFF_DURATION_S = 3.0   # seconds to passively listen
UDS_TIMEOUT_S    = 3.0   # seconds to wait for each UDS response


def connect_panda() -> Panda:
  p = Panda(disable_checks=True)
  p.set_safety_mode(CarParams.SafetyModel.elm327)
  print(f"  Connected to Panda (serial: {p.get_serial()})")
  return p


def format_app_id(data) -> str:
  if isinstance(data, (bytes, bytearray)):
    return bytes(data).decode("latin-1", "replace").strip("\x00").strip()
  return str(data).strip("\x00").strip()


def car_eps_fw_from_params():
  """EPS firmware string from CarParamsPersistent / CarParams, or None."""
  try:
    from cereal import car
  except Exception:
    if os.path.isdir("/data/openpilot"):
      sys.path.append("/data/openpilot")
    try:
      from cereal import car
    except Exception:
      return None
  for p in ("/data/params/d/CarParamsPersistent", "/data/params/d/CarParams"):
    try:
      data = open(p, "rb").read()
    except OSError:
      continue
    try:
      with car.CarParams.from_bytes(data) as CP:
        for fw in CP.carFw:
          if fw.ecu == "eps":
            v = format_app_id(bytes(fw.fwVersion))
            if v:
              return v
    except Exception:
      continue
  return None


def passive_sniff(panda: Panda, buses: list[int], resp_addr: int,
                  duration: float = SNIFF_DURATION_S) -> dict[int, bool]:
  """Listen for raw CAN frames from the EPS response address on each bus."""
  bus_list = list(buses)
  label = ", ".join(str(b) for b in bus_list)
  print(f"\n{'='*60}")
  print(f"[1/3] Passive CAN sniff on bus(es) {label} for {duration:.0f}s …")
  print(f"      Watching for frames from 0x{resp_addr:08X} (EPS response addr)")

  for bus in bus_list:
    panda.can_clear(bus)

  deadline = time.monotonic() + duration
  eps_counts = {b: 0 for b in bus_list}
  all_extended: dict[int, set[int]] = {b: set() for b in bus_list}

  while time.monotonic() < deadline:
    for addr, dat, recv_bus in panda.can_recv():
      if recv_bus not in eps_counts:
        continue
      if addr > 0x7FF:                         # 29-bit extended frame
        all_extended[recv_bus].add(addr)
      if addr == resp_addr:
        eps_counts[recv_bus] += 1
        print(f"  *** EPS frame on bus {recv_bus}! addr=0x{addr:08X}  data={dat.hex()}")

  results = {}
  for bus in bus_list:
    count = eps_counts[bus]
    results[bus] = count > 0
    if count:
      print(f"  RESULT bus {bus}: EPS responding passively ({count} frames)")
    else:
      print(f"  RESULT bus {bus}: No frames from EPS response addr")
      ext = all_extended[bus]
      if ext:
        print(f"    Other 29-bit addresses seen: " +
              ", ".join(f"0x{a:08X}" for a in sorted(ext)))
      else:
        print("    No 29-bit extended frames seen on this bus.")

  return results


def uds_tester_present(uds: UdsClient, bus: int) -> bool:
  """Send a single Tester Present and check whether the EPS is present on this bus.

  A negative response still means the ECU is alive (same idea as flash.py probe).
  """
  print(f"\n{'='*60}")
  print(f"[2/3] UDS Tester Present ping (bus {bus}) …")
  try:
    uds.tester_present()
    print("  RESULT: EPS acknowledged Tester Present  ✓")
    return True
  except NegativeResponseError as e:
    print(f"  RESULT: EPS present (negative response): {e}")
    return True
  except Exception as e:
    print(f"  RESULT: No response / timeout: {e}")
    return False


def uds_session_and_id(uds: UdsClient, bus: int) -> tuple[bool, str | None]:
  """Try default → extended session and read the software part number.

  Returns (session_ok, app_id_or_None).
  """
  print(f"\n{'='*60}")
  print(f"[3/3] UDS session + Application Software ID read (bus {bus}) …")
  app_id = None

  # Default session (0x01) — most ECUs come up here even after a bad flash
  try:
    uds.diagnostic_session_control(SESSION_TYPE.DEFAULT)
    print("  Default session: OK")
  except Exception as e:
    print(f"  Default session failed: {e}")

  # Try reading the part number in default session first
  for did, label in [
    (DATA_IDENTIFIER_TYPE.APPLICATION_SOFTWARE_IDENTIFICATION, "Application SW ID (F181)"),
    (DATA_IDENTIFIER_TYPE.VIN,                                 "VIN (F190)"),
  ]:
    try:
      data = uds.read_data_by_identifier(did)
      print(f"  {label}: {data!r}")
      if did == DATA_IDENTIFIER_TYPE.APPLICATION_SOFTWARE_IDENTIFICATION:
        app_id = format_app_id(data) or app_id
    except NegativeResponseError as e:
      print(f"  {label}: negative response – {e}")
    except Exception as e:
      print(f"  {label}: timeout/error – {e}")

  # Extended diagnostic session
  try:
    uds.diagnostic_session_control(SESSION_TYPE.EXTENDED_DIAGNOSTIC)
    print("  Extended diagnostic session: OK")

    try:
      data = uds.read_data_by_identifier(DATA_IDENTIFIER_TYPE.APPLICATION_SOFTWARE_IDENTIFICATION)
      print(f"  Application SW ID (extended): {data!r}")
      app_id = format_app_id(data) or app_id
      return True, app_id
    except Exception as e:
      print(f"  Application SW ID (extended): {e}")
  except Exception as e:
    print(f"  Extended diagnostic session failed: {e}")

  return False, app_id


def scan_all(panda: Panda, bus: int):
  """Probe every common Honda ECU address with a Tester Present."""
  print(f"\n{'='*60}")
  print(f"Scanning all common Honda UDS addresses on bus {bus} …\n")
  for addr, name in HONDA_SCAN_ADDRS:
    uds = UdsClient(panda, addr, bus=bus, timeout=1.5)
    try:
      uds.tester_present()
      print(f"  0x{addr:08X}  {name:<25}  ALIVE ✓")
    except NegativeResponseError as e:
      print(f"  0x{addr:08X}  {name:<25}  negative response: {e}")
    except Exception:
      print(f"  0x{addr:08X}  {name:<25}  no response")


def print_recovery_advice(kind: str, detected_eps: str | None):
  """Print next-step guidance without inventing a specific .rwd filename."""
  if kind == "dead":
    print("""
DIAGNOSIS: EPS is not responding at all on the checked bus(es).
  Possible causes:
    - Ignition/ACC not on — EPS needs power (key in ON position)
    - EPS is bricked (bad flash left it in bootloader with no CAN output)
    - Wiring / Panda connection issue
    - Wrong bus (if you pinned --bus, try without it to check 0 and 1)

  Next steps:
    1. Confirm ignition is ON (not just ACC) — some Bosch EPS needs full ON
    2. Re-run without --bus to check buses 0 and 1
    3. Run a full scan:  python3 eps-diag.py --scan
    4. If completely unresponsive, the EPS may need a bench flash via OBD2
       with the ECU powered independently from the car battery.
""")
    return

  if kind == "bootloader":
    print("""
DIAGNOSIS: EPS is broadcasting CAN frames but not responding to UDS.
  This is consistent with a bad flash that left the bootloader active
  but the application layer non-functional. The ECU is alive but stuck.
""")
  else:
    print("""
DIAGNOSIS: EPS is responding — try the flash again.
  The previous timeout may have been transient.
""")

  if detected_eps:
    print(f"  Detected EPS: {detected_eps}")
  print("""  Next step: python3 flash.py
  For recovery, choose the stock image matching your EPS part number
  (not a modified/linear-max image). flash.py will list compatible options.
  Manual path: re-run eps-update.py with the same .rwd you were already using
  (or the matching stock image) and --danger.
""")


def main():
  ap = argparse.ArgumentParser(description="Honda/Acura EPS CAN bus diagnostic")
  ap.add_argument("-b", "--bus", default=None, type=lambda x: int(x, 0),
                  help="Pin to a single CAN bus (default: check buses 0 and 1)")
  ap.add_argument("--addr", default=EPS_ADDR, type=lambda x: int(x, 0),
                  help=f"EPS UDS address (default: 0x{EPS_ADDR:08X})")
  ap.add_argument("--scan", action="store_true",
                  help="Scan all common Honda ECU addresses")
  ap.add_argument("--sniff-only", action="store_true",
                  help="Only run the passive sniff, skip UDS probes")
  args = ap.parse_args()

  buses = [args.bus] if args.bus is not None else list(DEFAULT_BUSES)
  resp_addr = response_addr_for(args.addr)

  print("Honda/Acura EPS diagnostic")
  print(f"  Bus(es):    {', '.join(str(b) for b in buses)}")
  print(f"  EPS addr:   0x{args.addr:08X}  (response 0x{resp_addr:08X})")

  try:
    panda = connect_panda()
  except Exception as e:
    print(f"\nFailed to connect to Panda: {e}")
    print("Make sure the Panda is connected via USB and the car is in ACC ON / ignition.")
    return

  if args.scan:
    for bus in buses:
      scan_all(panda, bus)
    return

  # ── check 1: passive sniff ─────────────────────────────────────────────────
  sniff_by_bus = passive_sniff(panda, buses, resp_addr)
  eps_alive_passive = any(sniff_by_bus.values())

  if args.sniff_only:
    return

  # ── checks 2 & 3: UDS probes (per bus) ─────────────────────────────────────
  ping_by_bus: dict[int, bool] = {}
  session_by_bus: dict[int, bool] = {}
  app_id = None

  for bus in buses:
    uds = UdsClient(panda, args.addr, bus=bus, timeout=UDS_TIMEOUT_S)
    ping_by_bus[bus] = uds_tester_present(uds, bus)
    ok, found_id = uds_session_and_id(uds, bus)
    session_by_bus[bus] = ok
    if found_id and not app_id:
      app_id = found_id

  eps_alive_ping = any(ping_by_bus.values())
  eps_alive_session = any(session_by_bus.values())
  detected_eps = app_id or car_eps_fw_from_params()

  # ── summary ────────────────────────────────────────────────────────────────
  print(f"\n{'='*60}")
  print("SUMMARY")
  for bus in buses:
    print(f"  Bus {bus}:")
    print(f"    Passive CAN frames:      {'YES' if sniff_by_bus.get(bus) else 'NO'}")
    print(f"    Tester Present:          {'YES' if ping_by_bus.get(bus) else 'NO'}")
    print(f"    UDS session/ID read:     {'YES' if session_by_bus.get(bus) else 'NO'}")
  responding = [b for b in buses if sniff_by_bus.get(b) or ping_by_bus.get(b) or session_by_bus.get(b)]
  if responding:
    print(f"  EPS activity seen on bus(es): {', '.join(str(b) for b in responding)}")
  if detected_eps:
    print(f"  Detected EPS part number:   {detected_eps}")

  if not any([eps_alive_passive, eps_alive_ping, eps_alive_session]):
    print_recovery_advice("dead", detected_eps)
  elif eps_alive_passive and not eps_alive_ping:
    print_recovery_advice("bootloader", detected_eps)
  else:
    print_recovery_advice("alive", detected_eps)


if __name__ == "__main__":
  main()
