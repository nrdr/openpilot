import gzip
import os
import struct
import sys
import time
import tqdm
import traceback
from argparse import ArgumentParser
from opendbc.car.structs import CarParams
from rwd_format.x5a import x5a
from panda import Panda
from opendbc.car.uds import UdsClient, SESSION_TYPE, ACCESS_TYPE, ROUTINE_CONTROL_TYPE, ROUTINE_IDENTIFIER_TYPE, DATA_IDENTIFIER_TYPE, RESET_TYPE, NegativeResponseError
from unittest import mock

# Honda EPS firmware decryption-key DID. Not present in stock opendbc
# DATA_IDENTIFIER_TYPE (only the old flasher-branch opendbc defined it).
FLASH_DECRYPTION_KEY = 0xF101

# NRCs that mean the ECU's security-access delay timer is running — waiting and
# re-requesting the seed is the only way through. 0x35 (invalid key) is
# deliberately absent: re-sending a key increments the ECU's failed-attempt
# counter and restarts the timer, making the lockout worse.
SEED_DELAY_NRCS = {0x36: 'exceed number of attempts', 0x37: 'required time delay not expired'}
SEED_RETRY_INTERVAL_S = 10.0
DEFAULT_SEED_TIMEOUT_S = 120.0
# The EPS refuses security access for a period after power-up and immediately
# after a session change; don't send the first seed request into that window.
SESSION_SETTLE_S = 0.5

DECRYPT_LOOKUP = {144: 72, 218: 55, 255: 255, 164: 1, 195: 26, 99: 2, 28: 178, 205: 158, 125: 138, 45: 118, 222: 98, 142: 78, 62: 58, 243: 38, 163: 18, 83: 254, 3: 234, 172: 214, 92: 194, 12: 174, 189: 154, 109: 134, 29: 114, 206: 94, 126: 74, 46: 54, 227: 34, 147: 14, 113: 0, 67: 250, 236: 230, 156: 210, 76: 190, 252: 170, 173: 150, 93: 130, 13: 110, 148: 253, 120: 159, 199: 148, 198: 137, 77: 126, 23: 104, 73: 83, 203: 73, 78: 62, 123: 53, 254: 42, 43: 33, 90: 23, 161: 12, 10: 3, 132: 249, 191: 239, 226: 220, 197: 201, 248: 191, 117: 181, 34: 172, 37: 161, 88: 151, 141: 142, 8: 131, 134: 121, 185: 111, 54: 101, 190: 90, 57: 79, 128: 68, 139: 57, 14: 46, 138: 35, 131: 10, 100: 241, 1: 228, 146: 200, 133: 185, 168: 171, 104: 155, 40: 139, 251: 85, 94: 66, 91: 45, 103: 124, 55: 112, 231: 156, 80: 56, 224: 92, 102: 113, 96: 60, 98: 188, 97: 252, 140: 206, 122: 31, 232: 187, 16: 40, 202: 51, 26: 7, 239: 251, 5: 153, 219: 77, 119: 128, 21: 157, 238: 102, 180: 5, 217: 119, 30: 50, 7: 100, 32: 44, 183: 144, 50: 176, 110: 70, 157: 146, 2: 164, 44: 182, 145: 8, 58: 15, 27: 29, 64: 52, 9: 67, 31: 199, 179: 22, 42: 11, 193: 20, 211: 30, 129: 4, 241: 32, 74: 19, 178: 208, 247: 160, 112: 64, 242: 224, 114: 192, 165: 193, 0: 36, 59: 37, 196: 9, 154: 39, 75: 41, 72: 147, 249: 127, 162: 204, 130: 196, 229: 209, 182: 133, 48: 48, 86: 109, 240: 96, 137: 99, 151: 136, 209: 24, 108: 198, 181: 197, 212: 13, 244: 21, 11: 25, 118: 117, 228: 17, 214: 141, 52: 229, 160: 76, 115: 6, 106: 27, 56: 143, 25: 71, 36: 225, 194: 212, 208: 88, 187: 69, 171: 65, 153: 103, 38: 97, 207: 243, 82: 184, 184: 175, 188: 218, 213: 205, 121: 95, 15: 195, 81: 248, 24: 135, 70: 105, 150: 125, 174: 86, 158: 82, 220: 226, 201: 115, 71: 116, 51: 246, 177: 16, 176: 80, 22: 93, 39: 108, 159: 231, 223: 247, 186: 47, 169: 107, 245: 213, 235: 81, 192: 84, 124: 202, 175: 235, 84: 237, 79: 211, 234: 59, 143: 227, 237: 166, 33: 236, 253: 106, 65: 244, 111: 219, 200: 179, 101: 177, 17: 232, 20: 221, 166: 129, 60: 186, 61: 122, 167: 140, 204: 222, 87: 120, 41: 75, 135: 132, 136: 163, 49: 240, 250: 63, 107: 49, 170: 43, 18: 168, 221: 162, 35: 242, 225: 28, 149: 189, 85: 173, 152: 167, 95: 215, 53: 165, 89: 87, 66: 180, 6: 89, 47: 203, 210: 216, 215: 152, 233: 123, 116: 245, 127: 223, 19: 238, 69: 169, 105: 91, 4: 217, 216: 183, 68: 233, 63: 207, 155: 61, 246: 149, 230: 145}

# Checksum offsets embedded in decrypted firmware, keyed by firmware data length.
# Each entry is (checksum_func_index, offset, label):
#   0 = sum of 16-bit BE words from 0..offset must equal value stored at offset
#   1 = negative-sum variant (same range, negated)
FIRMWARE_CHECKSUM_OFFSETS = {
  0x6c000: [(0, 0x6bf80, "sum"), (1, 0x6bffe, "negative-sum")],  # CR-V TLA, Insight TXM (524288 byte bin)
  0x4c000: [(0, 0x4bf80, "sum"), (1, 0x4bffe, "negative-sum")],  # Civic TBA/TEA/TGG/TGN, Clarity TRW (393216 byte bin)
}

def auto_int(i):
  return int(i, 0)

def read_file(fn):
  f_name, f_ext = os.path.splitext(fn)
  open_fn = open
  if f_ext == ".gz":
    open_fn = gzip.open
  f_name, f_ext = os.path.splitext(f_name)

  with open_fn(fn, 'rb') as f:
    f_data = f.read()

  return f_data

def validate_fw(fw_encrypted):
  assert len(fw_encrypted.firmware_blocks) == 1
  fw_len = fw_encrypted.firmware_blocks[0]["length"]

  print(f"\n  [1] Firmware checksums")
  print(f"      Firmware length: 0x{fw_len:x} ({fw_len} bytes)")

  cs_defs = FIRMWARE_CHECKSUM_OFFSETS.get(fw_len)
  if cs_defs is None:
    print(f"      WARNING: unknown firmware length 0x{fw_len:x} — checksums not verified")
    return

  decrypted = bytes(DECRYPT_LOOKUP[b] for b in fw_encrypted.firmware_encrypted[0])

  all_passed = True
  for func_idx, off, label in cs_defs:
    stored = struct.unpack('!H', decrypted[off:off+2])[0]
    if func_idx == 0:
      calc = sum(struct.unpack('!H', decrypted[i:i+2])[0] for i in range(0, off, 2)) & 0xFFFF
    else:
      calc = sum(-struct.unpack('!H', decrypted[i:i+2])[0] for i in range(0, off, 2)) & 0xFFFF
    ok = stored == calc
    all_passed = all_passed and ok
    status = 'PASS ✓' if ok else f'FAIL ✗  (expected 0x{calc:04x})'
    print(f"      0x{off:05x}  {label:<14}  stored: 0x{stored:04x}  {status}")

  print(f"\n  {'='*40}")
  print(f"  Firmware checksum: {'PASS ✓' if all_passed else 'FAIL ✗'}")

  assert all_passed, "Firmware checksum validation failed — do not flash this file"


def calculate_session_key(const_bytes, seed_bytes):
  k0, k1, k2 = struct.unpack('!HHH', const_bytes)
  seed = struct.unpack('!H', seed_bytes)[0]
  if k2 == 0:
    k2 = 0x10000

  key = ((seed + k0) ^ (seed * k1) % k2) & 0xFFFF
  return struct.pack('!H', key)

def get_uds_client(can_addr, bus):
  try:
    panda = Panda(disable_checks=True)
    panda.set_safety_mode(CarParams.SafetyModel.elm327)
    uds_client = UdsClient(panda, can_addr, bus=bus)
    print("Using real client")
  except Exception:
    mock_helper = mock.patch('opendbc.car.uds.UdsClient', autospec=True)
    uds_client = mock_helper.start()
    uds_client.security_access.return_value = b'1234'
    uds_client.request_download.return_value = 514
    uds_client.read_data_by_identifier.return_value = b'39990-TG7-A060\x00\x00'
    print("Using mock client")

  return uds_client

def _normalize_app_id(value):
  # TRW/Honda software IDs use '-' and ',' interchangeably as field separators,
  # and the ECU reports them differently than they're stored in the .rwd headers
  # (e.g. ECU 'b39990,TRW,A020' or a modded 'b39990-TLA,A040' vs header
  # 'b39990-TLA-A040'). Normalize both separators to ',' and drop trailing NULs
  # so the seed lookup matches on content.
  return value.replace(b'-', b',').rstrip(b'\x00')

def get_seed_secret(fw, app_id):
  headers = fw.file_headers
  target = _normalize_app_id(app_id)
  for i in range(len(headers[4].values)):
    if _normalize_app_id(headers[3].values[i].value) == target:
      return headers[4].values[i].value

  raise RuntimeError(f"Couldn't find software seed for software application ID {app_id}")

def get_can_address(fw):
  return 0x18da00f1 | struct.unpack('!B', fw.file_headers[2].values[0].value)[0] << 8

def request_seed(uds_client, timeout_s):
  """Request a security-access seed, waiting out the ECU's delay timer.

  Per ISO 14229 the ECU restarts its security-access delay timer at power-up if
  the failed-attempt counter was non-zero when it lost power, so a seed request
  made seconds after ignition-on can be refused with NRC 0x37 even on the first
  attempt of a session. Retry on a slow interval until the timer expires.
  """
  deadline = time.monotonic() + timeout_s
  started = time.monotonic()
  attempt = 0
  while True:
    attempt += 1
    try:
      seed = uds_client.security_access(ACCESS_TYPE.REQUEST_SEED)
      if attempt > 1:
        print(f"  seed granted after {time.monotonic() - started:.0f}s ({attempt} attempts)")
      return seed
    except NegativeResponseError as e:
      if e.error_code not in SEED_DELAY_NRCS:
        raise
      reason = SEED_DELAY_NRCS[e.error_code]
      remaining = deadline - time.monotonic()
      if remaining <= 0:
        print(f"  still refused ({reason}) after {timeout_s:.0f}s over {attempt} attempts.")
        print("  The EPS security-access lockout has not expired. Leave the car in")
        print("  accessory mode and retry with a longer --seed-timeout.")
        raise
      wait = min(SEED_RETRY_INTERVAL_S, remaining)
      print(f"  attempt {attempt}: {reason} — waiting {wait:.0f}s "
            f"({remaining:.0f}s of {timeout_s:.0f}s budget left)")
      time.sleep(wait)

def leave_diagnostic_session(uds_client):
  """Drop back to the default session so the EPS isn't left in extended/programming."""
  try:
    uds_client.diagnostic_session_control(SESSION_TYPE.DEFAULT)
    print("Returned EPS to default diagnostic session.")
  except Exception as e:
    print(f"Could not return EPS to default session ({e}) — power-cycle the car.")


if __name__ == "__main__":
  parser = ArgumentParser()
  parser.add_argument("rwd", help="RWD firmware file to flash")
  parser.add_argument("-b", "--bus", default=1, type=auto_int, help="CAN bus number (default 1)")
  parser.add_argument("--debug", action="store_true", help="Enable debug output")
  parser.add_argument("--danger", action="store_true", help="Run in danger mode that actually performs mutating actions")
  parser.add_argument("--skip-checksum", action="store_true", help="Skip firmware checksum validation (not recommended — a bad checksum will cause the EPS to reject the flash)")
  parser.add_argument("--seed-timeout", default=DEFAULT_SEED_TIMEOUT_S, type=float,
                      help=f"Seconds to keep retrying the security-access seed request while the EPS "
                           f"reports a delay/lockout (default {DEFAULT_SEED_TIMEOUT_S:.0f})")
  args = parser.parse_args()

  fw = x5a(read_file(args.rwd))
  if not args.skip_checksum:
    validate_fw(fw)

  print(fw)

  can_addr = get_can_address(fw)
  print(f"Connecting to CAN address 0x{can_addr:08X}")
  uds_client = get_uds_client(can_addr, args.bus)
  # --danger must never proceed on the mock fallback — it would "succeed" without
  # programming the EPS.
  if args.danger and isinstance(uds_client, mock.Mock):
    raise SystemExit("ERROR: --danger requires a real Panda connection (got mock client)")

  debug_output: list[bytes | None] = list()

  print("tester present ...")
  uds_client.tester_present()

  try:
    print("Getting software version")
    app_id = uds_client.read_data_by_identifier(DATA_IDENTIFIER_TYPE.APPLICATION_SOFTWARE_IDENTIFICATION)
    print(f"Application Software ID = {app_id}")

    print("Set diagnostic session type to 3 (extended diagnostic)")
    data = uds_client.diagnostic_session_control(SESSION_TYPE.EXTENDED_DIAGNOSTIC)
    debug_output = debug_output + [data]
    time.sleep(SESSION_SETTLE_S)

    print("Security access request key for seed 1")
    data = request_seed(uds_client, args.seed_timeout)
    debug_output = debug_output + [data]
    secret_key = get_seed_secret(fw, app_id)
    if data is None:
      raise ValueError("Security access request returned no seed data")
    key = calculate_session_key(secret_key, data[-2:])
    print("key = ", key)

    print("Security access send key for seed 1")
    data = uds_client.security_access(ACCESS_TYPE.SEND_KEY, key)
    debug_output = debug_output + [data]

    print("Set diagnostic session type to programming")
    data = uds_client.diagnostic_session_control(SESSION_TYPE.PROGRAMMING)
    debug_output = debug_output + [data]

    if not args.danger:
      raise RuntimeError('Safe mode: aborting before mutating actions')

    print("Erasing flash")
    data = uds_client.routine_control(ROUTINE_CONTROL_TYPE.START, ROUTINE_IDENTIFIER_TYPE.ERASE_MEMORY)
    debug_output = debug_output + [data]

    print("Setting firmware decryption key")
    data = uds_client.write_data_by_identifier(FLASH_DECRYPTION_KEY, fw.keys)
    debug_output = debug_output + [data]

    print("Requesting download")
    assert len(fw.firmware_blocks) == 1
    block = fw.firmware_blocks[0]
    length = block["length"]
    max_chunk_size = uds_client.request_download(block["start"], length)
    max_chunk_size -= 2 # subtract header bytes

    with tqdm.tqdm(total=length, unit='B', unit_scale=True) as t:
      cursor = 0x0
      seq = 1
      while cursor < length:
        block_size = min(max_chunk_size, length - cursor)
        data = uds_client.transfer_data(seq, fw.firmware_encrypted[0][cursor:cursor+block_size])
        debug_output = debug_output + [data]
        seq = (seq + 1) & 0xFF
        cursor += block_size
        t.update(block_size)

    print("Requesting transfer exit")
    data = uds_client.request_transfer_exit()
    debug_output = debug_output + [data]

    print("Checking programming dependencies")
    data = uds_client.routine_control(ROUTINE_CONTROL_TYPE.START, ROUTINE_IDENTIFIER_TYPE.CHECK_PROGRAMMING_DEPENDENCIES)
    debug_output = debug_output + [data]

    print("Resetting ECU")
    data = uds_client.ecu_reset(RESET_TYPE.HARD)
    debug_output = debug_output + [data]

  except Exception as e:
    print(traceback.format_exc())
    if not isinstance(uds_client, mock.Mock):
      leave_diagnostic_session(uds_client)
    # Dry-run intentionally raises here; treat that as success. Any other failure
    # must be a non-zero exit so callers (e.g. flash.py) don't treat it as done.
    if isinstance(e, RuntimeError) and str(e) == "Safe mode: aborting before mutating actions":
      pass
    else:
      sys.exit(1)

  if isinstance(uds_client, mock.Mock):
    from unittest.mock import ANY, call

    #print(uds_client.method_calls)

    calls = []
    calls += [call.read_data_by_identifier(DATA_IDENTIFIER_TYPE.APPLICATION_SOFTWARE_IDENTIFICATION)]
    calls += [call.diagnostic_session_control(SESSION_TYPE.EXTENDED_DIAGNOSTIC)]
    calls += [call.security_access(ACCESS_TYPE.REQUEST_SEED)]
    calls += [call.security_access(ACCESS_TYPE.SEND_KEY, ANY)]
    calls += [call.diagnostic_session_control(SESSION_TYPE.PROGRAMMING)]
    calls += [call.routine_control(ROUTINE_CONTROL_TYPE.START, ROUTINE_IDENTIFIER_TYPE.ERASE_MEMORY)]
    calls += [call.write_data_by_identifier(FLASH_DECRYPTION_KEY, fw.keys)]
    calls += [call.request_download(0x10000, 0x50000)]
    calls += [call.transfer_data(1, fw.firmware_encrypted[0][0:512])]
    calls += [call.transfer_data(2, fw.firmware_encrypted[0][512:1024])]
    uds_client.assert_has_calls(calls)

    num_blocks = -(len(fw.firmware_encrypted[0]) // -512) # sneaky math ceil
    assert uds_client.transfer_data.call_count == num_blocks

    calls = []
    calls += [call.transfer_data(num_blocks & 0xFF - 1, fw.firmware_encrypted[0][((num_blocks-1)*512):])]
    calls += [call.request_transfer_exit()]
    calls += [call.routine_control(ROUTINE_CONTROL_TYPE.START, ROUTINE_IDENTIFIER_TYPE.CHECK_PROGRAMMING_DEPENDENCIES)]
    calls += [call.ecu_reset(RESET_TYPE.HARD)]
    uds_client.assert_has_calls(calls)

    if args.debug:
      print("\nDebug output:")
      print(*debug_output, sep="\n")
