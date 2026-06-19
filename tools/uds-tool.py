#/usr/bin/env python3

import struct
import tqdm
from panda import Panda
from opendbc.car.structs import CarParams
from opendbc.car.uds import UdsClient, SESSION_TYPE, ACCESS_TYPE, DATA_IDENTIFIER_TYPE
from argparse import ArgumentParser

def auto_int(i):
  return int(i, 0)

def calculate_session_key(uds_client, data):
  app_id = uds_client.read_data_by_identifier(DATA_IDENTIFIER_TYPE.APPLICATION_SOFTWARE_IDENTIFICATION)

  if app_id.startswith(b'39990-TG7'):
    seed = data[-4:]
    seed1 = seed[0:2]
    seed2 = seed[2:4]
    key = int.from_bytes(seed1, "big") << 16 | int.from_bytes(seed2, "big") + 0x3039
    return key.to_bytes(4, "big")
  elif app_id.startswith(b'37805-RLV'):
    seed = data[-2:]
    key = (seed * 0x21) >> 2
    return struct.pack('!H', key)

if __name__ == "__main__":
  parser = ArgumentParser()
  parser.add_argument("--can-id", default=0x30, type=auto_int, help="ECU CAN address")
  parser.add_argument("--start-address", default=0, type=auto_int, help="Memory read start address")
  parser.add_argument("--end-address", default=0x5FFFF, type=auto_int, help="Memory read end address (inclusive)")
  parser.add_argument("--output", required=True, help="output file")
  parser.add_argument("--bus", default=0, type=auto_int, help="CAN bus number")
  parser.add_argument("--debug", action="store_true", help="Enable debug output")
  args = parser.parse_args()

  p = Panda()
  p.set_safety_mode(CarParams.SafetyModel.elm327)

  can_address = 0x18da00f1 | (args.can_id << 8)
  uds_client = UdsClient(p, can_address, bus=args.bus)
  print("tester present ...")
  uds_client.tester_present()

  try:
    print("Set diagnostic session type to 3 (extended diagnostic)")
    uds_client.diagnostic_session_control(SESSION_TYPE.EXTENDED_DIAGNOSTIC)

    print("Security access request key for seed 61")
    data = uds_client.security_access(ACCESS_TYPE.ADVANCED_SEED)
    print(data)
    key = calculate_session_key(uds_client, data)
    print("key = ", key)

    print("Security access send key for seed 61")
    data = uds_client.security_access(ACCESS_TYPE.ADVANCED_KEY, key)
    print(data)

    print("Set diagnostic session type to 0x60 (god mode)")
    uds_client.diagnostic_session_control(SESSION_TYPE.GOD_MODE)

    start_addr = args.start_address
    end_addr = args.end_address
    total = end_addr - start_addr + 1
    print("Reading memory from 0x{:08x} to 0x{:08x}".format(start_addr, end_addr))
    DEFAULT_BLOCK_SIZE = 512
    image = bytes()
    with tqdm.tqdm(total=total, unit='B', unit_scale=True) as t:
      while start_addr <= end_addr:
        block_size = min(DEFAULT_BLOCK_SIZE, end_addr - start_addr + 1)
        #uds_client.routine_control(ROUTINE_CONTROL_TYPE.START, ROUTINE_IDENTIFIER_TYPE.READ_MEMORY, struct.pack('!IH', start_addr, block_size))
        #image += uds_client.routine_control(ROUTINE_CONTROL_TYPE.START, ROUTINE_IDENTIFIER_TYPE.READ_MEMORY, struct.pack('!IH', start_addr, block_size))
        image += uds_client.read_memory_by_address(start_addr, block_size, 4, 2)
        start_addr += block_size
        t.update(block_size)

    with open(args.output, "wb") as f:
      f.write(image)

  except BaseException as e:
    print(e)

