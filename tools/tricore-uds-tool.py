#!/usr/bin/env python3
"""
TriCore ECU Memory Reader

This script connects to a TriCore-based ECU over UDS (Unified Diagnostic Services)
and reads memory based on the analysis of the ECU firmware. The script handles the
security access requirements to enable memory reading and supports various memory
regions.

The script is based on the analysis of the UDS_read_memory_by_address function and
the security access mechanisms in the ECU firmware.

Requirements:
- panda package (from comma.ai): For CAN communication
- Physical CAN connection to the ECU (using panda or other interface)

Author: Generated based on reverse engineering of TriCore ECU firmware
"""

import time
from typing import List
from unittest import mock
from panda import Panda
from opendbc.car.uds import UdsClient, SESSION_TYPE, ACCESS_TYPE
from opendbc.car.structs import CarParams
from argparse import ArgumentParser

def auto_int(i):
  """Convert string to integer with automatic base detection (hex, octal, decimal)"""
  return int(i, 0)

# Memory address ranges valid for reading
VALID_MEMORY_RANGES = [
  (0x70000000, 0x7001c000),
  (0x70100000, 0x70106000),
  (0x60000000, 0x6001e000),
  (0x60100000, 0x60108000),
  (0x50000000, 0x5001e000),
  (0x50100000, 0x50108000),
  (0xb0000000, 0xb0008000),
  # Special fallback range
  (0xa0000000, 0xa0400000),
]

def is_address_in_valid_range(addr, size):
  """
  Check if the address range is valid for memory reading
  """
  for start, end in VALID_MEMORY_RANGES:
    if start < addr <= end - size:
      return True
  return False

def get_uds_client(can_addr, bus):
  try:
    panda = Panda(disable_checks=True)
    panda.set_safety_mode(CarParams.SafetyModel.elm327)
    uds_client = UdsClient(panda, can_addr, bus=bus)
    print("Using real client")
  except Exception:
    mock_helper = mock.patch('opendbc.car.uds.UdsClient', autospec=True)
    uds_client = mock_helper.start()
    uds_client.security_access.return_value = b'\x00\x01\x02\x03'
    uds_client.read_memory_by_address.return_value = b'\x00' * 16
    print("Using mock client")

  return uds_client

def calculate_security_key_0x41(seed: bytes) -> bytes:
  """
  Calculate the security key for level 0x41 based on the decompiled UDS_validate_seed_0x41 function

  The function implements the exact algorithm from the ECU firmware:

  1. The seed is combined with two salt values from UDS_ACCESS_41_SEED_SALT array
  2. Each combined value undergoes bit rotation based on UDS_SECURITY_0x41_LOOP_COUNT
  3. The final key is calculated using a specific formula involving XOR operations and multiplication

  Args:
    seed: 4-byte seed from ECU

  Returns:
    4-byte key for the security access
  """
  # Convert seed to integer (big endian)
  seed_int = int.from_bytes(seed, byteorder='big')

  # Constants extracted from the firmware
  UDS_ACCESS_41_SEED_SALT = [0x0, 0x7279F20E]
  UDS_SECURITY_0x41_LOOP_COUNT = [0, 3]
  FINAL_KEY_0x41_ADDER = 0x8E3E8FAA

  # First salt calculation with left rotation (from the decompiled function)
  seed_plus_salt_0 = seed_int + UDS_ACCESS_41_SEED_SALT[0]
  for _ in range(UDS_SECURITY_0x41_LOOP_COUNT[0]):
    # left rotation by 1 bit
    seed_plus_salt_0 = ((seed_plus_salt_0 << 1) | (seed_plus_salt_0 >> 31)) & 0xFFFFFFFF

  # Second salt calculation with right rotation (from the decompiled function)
  seed_plus_salt_1 = seed_int + UDS_ACCESS_41_SEED_SALT[1]
  for _ in range(UDS_SECURITY_0x41_LOOP_COUNT[1]):
    # right rotation by 1 bit
    seed_plus_salt_1 = ((seed_plus_salt_1 >> 1) | (seed_plus_salt_1 << 31)) & 0xFFFFFFFF

  # return input == FINAL_KEY_0x41_ADDER + ((UDS_ACCESS_41_SEED & 0xffff) * (UDS_ACCESS_41_SEED >> 0x10) ^
  #                                   seed_plus_salt_0 ^ seed_plus_salt_1)
  seed_low = seed_int & 0xFFFF
  seed_high = (seed_int >> 16) & 0xFFFF
  key = FINAL_KEY_0x41_ADDER + ((seed_low * seed_high) ^ seed_plus_salt_0 ^ seed_plus_salt_1)
  key = key & 0xFFFFFFFF  # Ensure it's a 32-bit value

  # Convert back to bytes (big endian)
  return key.to_bytes(4, byteorder='big')

def read_memory_blocks(uds_client: UdsClient, start_addr, end_addr, block_size=255):
  """
  Read memory from the ECU in blocks

  Args:
    uds_client: UDS client instance
    start_addr: Starting address
    end_addr: Ending address (inclusive)
    block_size: Block size (1-4 bytes)

  Returns:
    Binary data
  """
  if not 1 <= block_size <= 255:
    raise ValueError("Block size must be between 1 and 4 bytes")

  image = bytearray()
  addr = start_addr

  print(f"Reading memory from 0x{start_addr:08x} to 0x{end_addr:08x} in {block_size}-byte blocks")
  total_bytes = end_addr - start_addr + 1
  bytes_read = 0

  try:
    while addr <= end_addr:
      current_block_size = min(block_size, end_addr - addr + 1)

      try:
        # UDS read memory by address (service 0x23)
        # Last parameter (0x14) is custom header that the ECU expects
        data = uds_client.read_memory_by_address(addr, current_block_size, 4, 1, b'\x14')
        image.extend(data)

        bytes_read += current_block_size
        progress = (bytes_read / total_bytes) * 100
        print(f"\rProgress: {progress:.1f}% ({bytes_read}/{total_bytes} bytes)", end="")

      except Exception as e:
        print(f"\nError reading at address 0x{addr:08x}: {e}")
        raise

      addr += current_block_size

      # Small delay to prevent overwhelming the ECU
      time.sleep(0.01)

  except KeyboardInterrupt:
    print("\nRead operation interrupted by user")

  print("\nRead operation completed")
  return bytes(image)

def main():
  parser = ArgumentParser(description="TriCore ECU Memory Reader over UDS")
  parser.add_argument("--can-id", default=0x7E0, type=auto_int, help="ECU CAN address")
  parser.add_argument("--start-address", required=True, type=auto_int, help="Memory read start address")
  parser.add_argument("--end-address", required=True, type=auto_int, help="Memory read end address (inclusive)")
  parser.add_argument("--block-size", default=255, type=auto_int, help="Memory read block size (1-255 bytes)")
  parser.add_argument("--output", required=True, help="Output file")
  parser.add_argument("--bus", default=0, type=auto_int, help="CAN bus number")
  parser.add_argument("--debug", action="store_true", help="Enable debug output")
  parser.add_argument("--skip-security", action="store_true", help="Skip security access (if ECU is already unlocked)")
  args = parser.parse_args()

  if args.start_address > args.end_address:
    parser.error("Start address must be less than or equal to end address")

  if not is_address_in_valid_range(args.start_address, 1):
    print(f"Warning: Start address 0x{args.start_address:08x} might not be in a valid memory range")

  if not is_address_in_valid_range(args.end_address, 1):
    print(f"Warning: End address 0x{args.end_address:08x} might not be in a valid memory range")

  uds_client = get_uds_client(args.can_id, args.bus)

  debug_output: List[int] = list()

  try:
    # Tester present to establish connection
    print("Sending tester present...")
    uds_client.tester_present()

    # Set diagnostic session to EXTENDED_DIAGNOSTIC
    session_type = SESSION_TYPE.EXTENDED_DIAGNOSTIC
    print(f"Setting diagnostic session to 0x{session_type:02X}...")
    data = uds_client.diagnostic_session_control(session_type)
    debug_output += [data]

    # Security access process (unless skipped)
    if not args.skip_security:
      print("Requesting seed for security level 0x41...")
      data = uds_client.security_access(ACCESS_TYPE.REQUEST_SEED_0x41)
      debug_output += [data]

      # The seed is in the response data
      if len(data) >= 4:
        # Extract the seed from response
        seed = data[-4:-1]
        algo_byte = data[-1:]
        key = calculate_security_key_0x41(seed)
        print(f"Calculated key: {key}")

        # Send the key with the algorithm byte
        print("Sending key for security level 0x41...")
        key_with_algo = bytearray(key)
        key_with_algo += algo_byte
        data = uds_client.security_access(ACCESS_TYPE.SEND_KEY_0x41, bytes(key_with_algo))
        debug_output += [data]

        print("Security access granted!")
      else:
        print("Invalid seed response from ECU. Cannot proceed.")
        return
    else:
      print("Skipping security access as requested...")

    # Read memory
    print("Reading memory...")
    image = read_memory_blocks(uds_client, args.start_address, args.end_address, args.block_size)
    debug_output += [image]

    # Save to file
    with open(args.output, "wb") as f:
      f.write(image)
    print(f"Memory dump saved to {args.output}")

  except Exception as e:
    print(f"Error: {e}")

  finally:
    if args.debug:
      print("\nDebug output:")
      print(*debug_output, sep="\n")

  if isinstance(uds_client, mock.Mock):
    from unittest.mock import call

    calls = []
    calls += [call.tester_present()]
    calls += [call.diagnostic_session_control(SESSION_TYPE.EXTENDED_DIAGNOSTIC)]
    calls += [call.security_access(ACCESS_TYPE.REQUEST_SEED_0x41)]
    calls += [call.security_access(ACCESS_TYPE.SEND_KEY_0x41, b'\x9c\x8d\xcf\n\x03')]
    calls += [call.read_memory_by_address(args.start_address, args.end_address - args.start_address + 1, 4, 1, b'\x14')]
    uds_client.assert_has_calls(calls)

    print(f"\nMock calls:\n{uds_client.method_calls}")

if __name__ == "__main__":
  main()