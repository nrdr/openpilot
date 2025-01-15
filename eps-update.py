import gzip
import os
import struct
import tqdm
import traceback
from argparse import ArgumentParser
from typing import List
from panda.format.x5a import x5a
from panda import Panda
from panda.python.uds import UdsClient, SESSION_TYPE, ACCESS_TYPE, ROUTINE_CONTROL_TYPE, ROUTINE_IDENTIFIER_TYPE, DATA_IDENTIFIER_TYPE
from unittest import mock

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

def validate_fw(fw_encrypted, cipher_ops, block_end_addrs):
  assert len(fw_encrypted.firmware_blocks) == 1 # don't know how to handle firmware with more than one section
  fw = decrypt(fw_encrypted, cipher_ops)
  s = 0 # sum at each checksum should be 0 so we don't need to reset it
  start = 0
  end = max(block_end_addrs)
  for i in range(start, end, 4):
    j = i+4
    s += struct.unpack('<I', fw[i:j])[0]
    s &= 0xFFFFFFFF
    if j in block_end_addrs:
      assert s == 0, 'Checksum failed for block ending 0x{:08X}'.format(j)
      print('Checksum passed for block ending 0x{:08X}'.format(j))

  assert s == 0, 'Checksum failed for block ending 0x{:08X}'.format(j)


def calculate_session_key(const_bytes, seed_bytes):
  k0, k1, k2 = struct.unpack('!HHH', const_bytes)
  seed = struct.unpack('!H', seed_bytes)[0]
  if k2 == 0:
    k2 = 0x10000

  key = (seed + k0) ^ (seed * k1) % k2
  return struct.pack('!H', key)

def decrypt(fw, ops):
  key = fw.keys
  assert len(key) == 3
  assert len(ops) == 3

  o0 = fw.operator_lut[ops[0]]
  o1 = fw.operator_lut[ops[1]]
  o2 = fw.operator_lut[ops[2]]
  decoder = fw._get_decoder(int(key[0]), int(key[1]), int(key[2]), o0, o1, o2)
  plain, _ = fw.decrypt(decoder)
  return plain

def get_uds_client(can_addr, debug):
  try:
    panda = Panda(disable_checks=True)
    panda.set_safety_mode(Panda.SAFETY_ELM327)
    uds_client = UdsClient(panda, can_addr, debug=False, bus = 1)
    print("Using real client")
  except Exception:
    mock_helper = mock.patch('panda.python.uds.UdsClient', autospec=True)
    uds_client = mock_helper.start()
    uds_client.security_access.return_value = b'1234'
    uds_client.request_download.return_value = 514
    uds_client.read_data_by_identifier.return_value = b'39990-TG7-A060\x00\x00'
    print("Using mock client")

  return uds_client

def get_seed_secret(fw, app_id):
  headers = fw.file_headers
  for i in range(len(headers[4].values)):
    if headers[3].values[i].value == app_id:
      return headers[4].values[i].value

  raise RuntimeError("Couldn't find software seed for software application ID {}".format(app_id))

def get_can_address(fw):
  return 0x18da00f1 | struct.unpack('!B', fw.file_headers[2].values[0].value)[0] << 8


if __name__ == "__main__":
  parser = ArgumentParser()
  parser.add_argument("rwd", help="RWD firmware file to flash")
  parser.add_argument("-o", "--cipher-ops", default="+^-", help="Operand list for firmware encryption cipher")
  parser.add_argument("-c", "--checksum-offsets", nargs="*", default=[0xa000, 0x1d000, 0x4ff00], type=auto_int)
  parser.add_argument("--debug", action="store_true", help="Enable debug output")
  parser.add_argument("--danger", action="store_true", help="Run in danger mode that actually performs mutating actions")
  args = parser.parse_args()

  fw = x5a(read_file(args.rwd))
  #validate_fw(fw, args.cipher_ops, args.checksum_offsets)

  print(fw)

  can_addr = get_can_address(fw)
  print("Connecting to CAN address 0x{:08X}".format(can_addr))
  uds_client = get_uds_client(can_addr, args.debug)

  debug_output: List[int] = list()

  print("tester present ...")
  uds_client.tester_present()

  try:
    print("Getting software version")
    app_id = uds_client.read_data_by_identifier(DATA_IDENTIFIER_TYPE.APPLICATION_SOFTWARE_IDENTIFICATION)
    print("Application Software ID = {}".format(app_id))

    print("Set diagnostic session type to 3 (extended diagnostic)")
    data = uds_client.diagnostic_session_control(SESSION_TYPE.EXTENDED_DIAGNOSTIC)
    debug_output = debug_output + [data]

    print("Security access request key for seed 1")
    data = uds_client.security_access(ACCESS_TYPE.REQUEST_SEED)
    debug_output = debug_output + [data]
    secret_key = get_seed_secret(fw, app_id)
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
    data = uds_client.write_data_by_identifier(DATA_IDENTIFIER_TYPE.FLASH_DECRYPTION_KEY, fw.keys)
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

  except Exception:
    print(traceback.format_exc())

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
    calls += [call.write_data_by_identifier(DATA_IDENTIFIER_TYPE.FLASH_DECRYPTION_KEY, fw.keys)]
    calls += [call.request_download(0x10000, 0x50000)]
    calls += [call.transfer_data(0, fw.firmware_encrypted[0][0:512])]
    calls += [call.transfer_data(1, fw.firmware_encrypted[0][512:1024])]
    uds_client.assert_has_calls(calls)

    num_blocks = -(len(fw.firmware_encrypted[0]) // -512) # sneaky math ceil
    assert uds_client.transfer_data.call_count == num_blocks

    calls = []
    calls += [call.transfer_data(num_blocks - 1, fw.firmware_encrypted[0][((num_blocks-1)*512):])]
    calls += [call.request_transfer_exit()]
    calls += [call.routine_control(ROUTINE_CONTROL_TYPE.START, ROUTINE_IDENTIFIER_TYPE.CHECK_PROGRAMMING_DEPENDENCIES)]
    uds_client.assert_has_calls(calls)

    if args.debug:
      print("\nDebug output:") 
      print(*debug_output, sep="\n")
