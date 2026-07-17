"""
EPS CAN bus diagnostic tool for Honda CR-V (TLA platform).

Checks whether the EPS (Electric Power Steering) ECU is alive on the CAN bus
after a potentially bad flash. Runs three checks:

  1. Passive sniff  – listen for any raw CAN traffic from the EPS physical addr
  2. UDS ping       – send Tester Present and wait for a positive response
  3. UDS session    – try Default → Extended diagnostic sessions and read the
                      Application Software ID (part number)

Usage (on the comma device via SSH):
  python eps-diag.py            # uses default bus 1, address 0x18DA30F1
  python eps-diag.py -b 0       # try bus 0 instead
  python eps-diag.py --scan     # brute-force scan all common Honda ECU addrs
"""

import argparse
import struct
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
EPS_ADDR      = 0x18DA30F1   # tester → EPS  (29-bit, ISO 15765-4 physical)
EPS_RESP_ADDR = 0x18DAF130   # EPS → tester  (response)

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


def passive_sniff(panda: Panda, bus: int, duration: float = SNIFF_DURATION_S):
  """Listen for any raw CAN frames from the EPS response address."""
  print(f"\n{'='*60}")
  print(f"[1/3] Passive CAN sniff on bus {bus} for {duration:.0f}s …")
  print(f"      Watching for frames from 0x{EPS_RESP_ADDR:08X} (EPS response addr)")

  panda.can_clear(bus)
  deadline = time.monotonic() + duration
  eps_frames: list[tuple] = []
  all_extended: set[int] = set()

  while time.monotonic() < deadline:
    for addr, _, dat, recv_bus in panda.can_recv():
      if recv_bus != bus:
        continue
      if addr > 0x7FF:                         # 29-bit extended frame
        all_extended.add(addr)
      if addr == EPS_RESP_ADDR:
        eps_frames.append((addr, dat))
        print(f"  *** EPS frame seen! addr=0x{addr:08X}  data={dat.hex()}")

  if eps_frames:
    print(f"  RESULT: EPS is responding passively ({len(eps_frames)} frames)")
  else:
    print(f"  RESULT: No frames from EPS response addr during sniff")
    if all_extended:
      print(f"  Other 29-bit addresses seen: " +
            ", ".join(f"0x{a:08X}" for a in sorted(all_extended)))
    else:
      print("  No 29-bit extended frames seen at all on this bus.")

  return bool(eps_frames)


def uds_tester_present(uds: UdsClient) -> bool:
  """Send a single Tester Present and check whether the EPS ACKs it."""
  print(f"\n{'='*60}")
  print(f"[2/3] UDS Tester Present ping …")
  try:
    uds.tester_present()
    print("  RESULT: EPS acknowledged Tester Present  ✓")
    return True
  except NegativeResponseError as e:
    print(f"  RESULT: EPS sent negative response: {e}")
    return False
  except Exception as e:
    print(f"  RESULT: No response / timeout: {e}")
    return False


def uds_session_and_id(uds: UdsClient) -> bool:
  """Try default → extended session and read the software part number."""
  print(f"\n{'='*60}")
  print(f"[3/3] UDS session + Application Software ID read …")

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
    except NegativeResponseError as e:
      print(f"  {label}: negative response – {e}")
    except Exception as e:
      print(f"  {label}: timeout/error – {e}")

  # Extended diagnostic session
  try:
    uds.diagnostic_session_control(SESSION_TYPE.EXTENDED_DIAGNOSTIC)
    print("  Extended diagnostic session: OK")

    # Try the part number again in extended session
    try:
      data = uds.read_data_by_identifier(DATA_IDENTIFIER_TYPE.APPLICATION_SOFTWARE_IDENTIFICATION)
      print(f"  Application SW ID (extended): {data!r}")
      return True
    except Exception as e:
      print(f"  Application SW ID (extended): {e}")
  except Exception as e:
    print(f"  Extended diagnostic session failed: {e}")

  return False


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


def main():
  ap = argparse.ArgumentParser(description="Honda EPS CAN bus diagnostic")
  ap.add_argument("-b", "--bus",  default=1, type=lambda x: int(x, 0),
                  help="CAN bus number (default: 1)")
  ap.add_argument("--addr", default=EPS_ADDR, type=lambda x: int(x, 0),
                  help=f"EPS UDS address (default: 0x{EPS_ADDR:08X})")
  ap.add_argument("--scan", action="store_true",
                  help="Scan all common Honda ECU addresses")
  ap.add_argument("--sniff-only", action="store_true",
                  help="Only run the passive sniff, skip UDS probes")
  args = ap.parse_args()

  print(f"Honda EPS diagnostic")
  print(f"  Bus:        {args.bus}")
  print(f"  EPS addr:   0x{args.addr:08X}")

  try:
    panda = connect_panda()
  except Exception as e:
    print(f"\nFailed to connect to Panda: {e}")
    print("Make sure the Panda is connected via USB and the car is in ACC ON / ignition.")
    return

  if args.scan:
    scan_all(panda, args.bus)
    return

  # ── check 1: passive sniff ─────────────────────────────────────────────────
  eps_alive_passive = passive_sniff(panda, args.bus)

  if args.sniff_only:
    return

  # ── checks 2 & 3: UDS probes ───────────────────────────────────────────────
  uds = UdsClient(panda, args.addr, bus=args.bus, timeout=UDS_TIMEOUT_S)

  eps_alive_ping    = uds_tester_present(uds)
  eps_alive_session = uds_session_and_id(uds)

  # ── summary ────────────────────────────────────────────────────────────────
  print(f"\n{'='*60}")
  print("SUMMARY")
  print(f"  Passive CAN frames seen:   {'YES' if eps_alive_passive else 'NO'}")
  print(f"  Tester Present response:   {'YES' if eps_alive_ping    else 'NO'}")
  print(f"  UDS session/ID read:       {'YES' if eps_alive_session else 'NO'}")

  if not any([eps_alive_passive, eps_alive_ping, eps_alive_session]):
    print("""
DIAGNOSIS: EPS is not responding at all on this bus.
  Possible causes:
    - Wrong bus — try: python eps-diag.py -b 0
    - Ignition/ACC not on — EPS needs power (key in ON position)
    - EPS is bricked (bad flash left it in bootloader with no CAN output)
    - Wiring / Panda connection issue

  Next steps:
    1. Confirm ignition is ON (not just ACC) — some Bosch EPS needs full ON
    2. Try bus 0:   python eps-diag.py -b 0
    3. Run a full scan:  python eps-diag.py --scan
    4. If completely unresponsive, the EPS may need a bench flash via OBD2
       with the ECU powered independently from the car battery.
""")
  elif eps_alive_passive and not eps_alive_ping:
    print("""
DIAGNOSIS: EPS is broadcasting CAN frames but not responding to UDS.
  This is consistent with a bad flash that left the bootloader active
  but the application layer non-functional. The ECU is alive but stuck.
  Try reflashing immediately with:
    python eps-update.py 39990-TLA-A040-stock.rwd -b 1 --skip-checksum --danger
  The bootloader may still accept a download request even without a valid app.
""")
  else:
    print("""
DIAGNOSIS: EPS is responding — try the flash again.
  The previous timeout may have been transient. Retry:
    python eps-update.py 39990-TLA-A040-stock.rwd -b 1 --skip-checksum --danger
""")


if __name__ == "__main__":
  main()
