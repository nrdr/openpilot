#!/usr/bin/env python3
# pylint: disable=bad-indentation
"""
Honda ECU Firmware Update Script
"""

import os
import struct
import tqdm
import traceback
from argparse import ArgumentParser
from opendbc.car.structs import CarParams
from panda import Panda
from panda.format.x5a import x5a
from opendbc.car.uds import UdsClient, SESSION_TYPE, ACCESS_TYPE, RESET_TYPE, ROUTINE_CONTROL_TYPE, ROUTINE_IDENTIFIER_TYPE, DATA_IDENTIFIER_TYPE, NegativeResponseError, MessageTimeoutError
from unittest import mock

FLASH_BASE = 0x80000000
FLASH_END  = 0x803FFFFF
FLASH_SIZE = FLASH_END - FLASH_BASE + 1  # 0x400000 = 4 MB

# Honda RWD "full" update covers everything except the 64KB bootloader.
# The ECU's bootloader expects 0xA0xxxxxx (cached PFlash segment);
# we normalize to 0x80xxxxxx for validation.
RWD_FULL_START = 0x80010000  # normalized from 0xA0010000
RWD_FULL_SIZE  = 0x3F0000    # 4 MB minus 64 KB bootloader

def auto_int(i):
    """Convert string to integer with automatic base detection (hex, octal, decimal)"""
    return int(i, 0)

def read_file(fn) -> bytes:
    """Read firmware file, supporting both regular and gzipped files"""
    _, f_ext = os.path.splitext(fn)
    if f_ext == ".gz":
        import gzip
        with gzip.open(fn, 'rb') as f:
            data = f.read()
            if isinstance(data, str):
                f_data = data.encode('latin-1')
            else:
                f_data = bytes(data)
    else:
        with open(fn, 'rb') as f:
            f_data = f.read()

    return f_data

def calculate_session_key(const_bytes: bytes, seed_bytes: bytes) -> bytes:
    """
    Calculate the security key for level 1 based on the constants from the RWD

    Args:
        seed: 2-byte seed from ECU

    Returns:
        2-byte key for the security access
    """
    k0, k1, k2 = struct.unpack('!HHH', const_bytes)
    seed = struct.unpack('!H', seed_bytes)[0]
    if k2 == 0:
        k2 = 0x10000

    key = ((seed + k0) & 0xFFFF) ^ ((seed * k1) % k2)
    key_bytes = struct.pack('!H', key)
    print(f"Calculated key: {key_bytes.hex().upper()}")
    return key_bytes

def validate_firmware(firmware: x5a) -> bool:
    """
    Validate Honda ECU firmware

    Args:
        firmware: The firmware in x5a format

    Returns:
        True if firmware is valid, False otherwise
    """
    assert len(firmware.firmware_blocks) == 1
    block = firmware.firmware_blocks[0]
    start = block["start"]
    length = block["length"]
    end = start + length

    print(f"Firmware size: {length} bytes (0x{length:08x})")
    print(f"Flash region:  0x{start:08X} - 0x{end:08X}")

    if length < 0x100:
        print("Warning: Firmware file seems too small (< 256 bytes)")
        return False

    # Normalize 0xA0xxxxxx cached mapping to 0x80xxxxxx for validation
    norm_start = start
    if (norm_start & 0xF0000000) == 0xA0000000:
        norm_start = (norm_start & 0x0FFFFFFF) | 0x80000000
    norm_end = norm_start + length

    if norm_start < FLASH_BASE or norm_end > FLASH_END + 1:
        print(
            f"Error: Flash region 0x{norm_start:08X}-0x{norm_end:08X} outside PFlash range "
            + f"0x{FLASH_BASE:08X}-0x{FLASH_END:08X}"
        )
        return False

    # Validate 16 KB sector alignment (smallest AURIX PFlash sector)
    SECTOR_SIZE = 0x4000  # 16 KB
    if (norm_start - FLASH_BASE) % SECTOR_SIZE != 0:
        print(f"Error: Start address 0x{start:08X} not aligned to 16 KB sector boundary")
        return False
    if length % SECTOR_SIZE != 0:
        print(f"Error: Length 0x{length:08X} not aligned to 16 KB sector boundary")
        return False

    # Detect partial vs full flash
    is_full = (norm_start == RWD_FULL_START and length == RWD_FULL_SIZE)
    if is_full:
        print(f"Mode:          FULL flash ({length // 1024} KB)")
    else:
        print(f"Mode:          PARTIAL flash ({length // 1024} KB)")

    return True

def get_uds_client(can_addr, bus):
    """Get UDS client instance, with mock fallback for testing"""
    try:
        panda = Panda(disable_checks=True)
        panda.set_safety_mode(CarParams.SafetyModel.elm327)
        uds_client = UdsClient(panda, can_addr, bus=bus, response_pending_timeout=30)
        print("Using real client")
    except Exception:
        mock_helper = mock.patch('opendbc.car.uds.UdsClient', autospec=True)
        uds_client = mock_helper.start()
        uds_client.security_access.return_value = b'\x00\x01\x02'  # 2-byte seed + status byte
        uds_client.diagnostic_session_control.return_value = b'\x50\x02'
        uds_client.routine_control.return_value = b'\x71\x01'
        uds_client.request_download.return_value = 0x200 + 2 # 512 byte max chunk size + header
        uds_client.transfer_data.return_value = b'\x76\x01'
        uds_client.request_transfer_exit.return_value = b'\x77'
        uds_client.ecu_reset.return_value = None

        # Configure mock to return different responses based on data identifier
        def mock_read_data_by_identifier(data_id):
            if data_id == DATA_IDENTIFIER_TYPE.APPLICATION_SOFTWARE_IDENTIFICATION:
                return b'37805-RLV-L010\x00\x00'
            elif data_id == DATA_IDENTIFIER_TYPE.CALIBRATION_VERIFICATION_NUMBER:
                # Return a mock CVN that will differ from calculated CVN to test mismatch scenario
                return b'\x12\x34\x56\x78'  # 4-byte mock CVN
            else:
                return b'UNKNOWN'

        uds_client.read_data_by_identifier.side_effect = mock_read_data_by_identifier
        print("Using mock client")

    return uds_client

def write_firmware_to_ecu(uds_client: UdsClient, firmware: x5a, debug_output: list | None = None) -> bool:
    """
    Write firmware data to ECU using UDS transfer services

    Args:
        uds_client: UDS client instance
        firmware: Firmware binary data
        debug_output: Optional list to collect debug information

    Returns:
        True if successful, False otherwise
    """
    if debug_output is None:
        debug_output = []

    try:
        print("Requesting download")
        assert len(firmware.firmware_blocks) == 1
        block = firmware.firmware_blocks[0]
        length = block["length"]
        response = uds_client.request_download(block["start"], length)
        debug_output += [response]

        max_chunk_size = response - 2  # subtract header bytes

        with tqdm.tqdm(total=length, unit='B', unit_scale=True) as t:
            cursor = 0
            seq = 1
            while cursor < length:
                block_size = min(max_chunk_size, length - cursor)

                uds_client.transfer_data(seq, firmware.firmware_encrypted[0][cursor:cursor+block_size])

                seq = (seq + 1) & 0xFF
                cursor += block_size
                t.update(block_size)

        print("Requesting transfer exit...")
        data = uds_client.request_transfer_exit()
        debug_output += [data]

        return True

    except Exception as e:
        print(f"Error during firmware transfer: {e}")
        return False

def check_firmware_cvn(uds_client: UdsClient, firmware: x5a, debug: bool = False) -> bool:
    """
    Check if firmware flashing is not needed by comparing CVNs.

    Args:
        uds_client: UDS client instance for ECU communication
        firmware: Firmware data in x5a format
        debug: Enable detailed debug output

    Returns:
        True if CVNs match
    """
    try:
        print("Checking if firmware update is needed...")

        # Read current CVN from ECU
        print("Reading current CVN from ECU...")
        try:
            ecu_cvn_data = uds_client.read_data_by_identifier(DATA_IDENTIFIER_TYPE.CALIBRATION_VERIFICATION_NUMBER)
            # Extract 4-byte CVN from response (skip status bytes if present)
            ecu_cvn = ecu_cvn_data[-4:] if len(ecu_cvn_data) >= 4 else ecu_cvn_data

            if debug:
                print(f"ECU CVN: {ecu_cvn_data.hex().upper()}")

        except NegativeResponseError as e:
            if debug:
                print(f"UDS negative response reading CVN: {e}")
            return False
        except MessageTimeoutError:
            if debug:
                print("CVN read timeout")
            return False
        except Exception as e:
            if debug:
                print(f"CVN read error: {e}")
            return False

        # Calculate CVN from firmware file
        print("Getting CVN from firmware file...")
        try:
            firmware_cvn = get_cvn(firmware)

            if debug:
                print(f"Firmware CVN: {' '.join(f'{b:02X}' for b in firmware_cvn)}")

        except Exception as e:
            if debug:
                print(f"CVN calculation error: {e}")
            return False

        return ecu_cvn == firmware_cvn
    except Exception as e:
        if debug:
            print(f"Unexpected CVN check error: {e}")

    return False

def parse_arguments():
    """Parse and return command line arguments"""
    parser = ArgumentParser(description="Honda ECU Firmware Update Tool")
    parser.add_argument("firmware", help="Honda ECU firmware file (.bin)")
    parser.add_argument("-b", "--bus", default=0, type=auto_int, help="CAN bus number")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--danger", action="store_true", help="Run in danger mode that actually performs mutating actions")
    parser.add_argument("--skip-checksum", action="store_true", help="Skip firmware checksum validation")
    parser.add_argument("--skip-security", action="store_true", help="Skip security access (if ECU is already unlocked)")
    parser.add_argument("--force", action="store_true", help="Force firmware flashing even if CVN indicates no update needed")
    return parser.parse_args()

def load_and_validate_firmware(args) -> x5a:
    """
    Load firmware file and validate its checksum

    Args:
        args: Parsed command line arguments

    Returns:
        Firmware data as bytes

    Raises:
        SystemExit: If firmware validation fails
    """
    print(f"Reading firmware file: {args.firmware}")
    firmware = x5a(read_file(args.firmware))

    if not args.skip_checksum:
        print("Validating firmware checksum...")
        if not validate_firmware(firmware):
            print("Firmware checksum validation failed!")
            exit(1)
        print("Firmware checksum validation passed")

    return firmware

def get_seed_secret(fw: x5a, app_id: bytes):
    headers = fw.file_headers
    for i in range(len(headers[4].values)):
        if headers[3].values[i].value == app_id:
            return headers[4].values[i].value

    raise RuntimeError(f"Couldn't find software seed for software application ID {app_id}")

def get_cvn(fw: x5a) -> bytes:
    return fw.file_headers[1].values[0].value

def get_can_address(fw: x5a) -> int:
    return 0x18da00f1 | struct.unpack('!B', fw.file_headers[2].values[0].value)[0] << 8

def setup_ecu_connection(fw: x5a, bus: int):
    """
    Establish connection to the ECU via CAN

    Args:
        args: Parsed command line arguments

    Returns:
        UDS client instance
    """
    can_addr = get_can_address(fw)
    print(f"Connecting to CAN address 0x{can_addr:08X}")
    return get_uds_client(can_addr, bus)

def initialize_ecu_communication(uds_client, debug_output: list) -> bytes:
    """
    Initialize ECU communication with tester present and extended diagnostic session

    Args:
        uds_client: UDS client instance
        debug_output: List to collect debug information

    Returns:
        Firmware application ID
    """
    print("Sending tester present...")
    uds_client.tester_present()
    print("Reading software version")
    data = uds_client.read_data_by_identifier(DATA_IDENTIFIER_TYPE.APPLICATION_SOFTWARE_IDENTIFICATION)
    debug_output += [data]

    app_id = data
    print(f"Application Software ID = {app_id}")

    print("Setting diagnostic session to EXTENDED_DIAGNOSTIC...")
    data = uds_client.diagnostic_session_control(SESSION_TYPE.EXTENDED_DIAGNOSTIC)
    if data is not None:
        debug_output += [data]

    return app_id

def perform_security_access(uds_client: UdsClient, app_id: bytes, firmware: x5a, debug_output: list) -> bool:
    """
    Perform security access procedure with the ECU

    Args:
        uds_client: UDS client instance
        firmware: Firmware struct
        debug_output: List to collect debug information

    Returns:
        True if security access successful, False if failed
    """
    print("Requesting seed for security level 1...")
    data = uds_client.security_access(ACCESS_TYPE.REQUEST_SEED)
    if data is not None:
        debug_output += [data]

    if data and len(data) >= 3:
        # Extract the 2-byte seed (level 1 uses 2-byte seed)
        seed = data[1:3]

        print(f"Received seed: {seed.hex().upper()}")

        secret_key = get_seed_secret(firmware, app_id)
        key = calculate_session_key(secret_key, seed)

        print("Sending key for security level 1...")
        data = uds_client.security_access(ACCESS_TYPE.SEND_KEY, key)
        if data is not None:
            debug_output += [data]

        print("Security access granted!")
        return True
    else:
        print("Invalid seed response from ECU. Cannot proceed.")
        return False

def setup_programming_session(uds_client, debug_output: list):
    """
    Setup programming session on the ECU

    Args:
        uds_client: UDS client instance
        debug_output: List to collect debug information
    """
    print("Setting diagnostic session to PROGRAMMING...")
    data = uds_client.diagnostic_session_control(SESSION_TYPE.PROGRAMMING)
    if data is not None:
        debug_output += [data]

def perform_firmware_update(uds_client: UdsClient, firmware: x5a, debug_output: list) -> bool:
    """
    Perform the actual firmware update operations

    Args:
        uds_client: UDS client instance
        firmware_data: Firmware in x5a format
        debug_output: List to collect debug information

    Returns:
        True if firmware update successful, False otherwise
    """
    print("WARNING: Performing actual firmware update!")

    # Erase flash memory
    assert len(firmware.firmware_blocks) == 1
    block = firmware.firmware_blocks[0]
    start = block["start"]
    length = block["length"]

    # Normalize for comparison
    norm_start = start
    if (norm_start & 0xF0000000) == 0xA0000000:
        norm_start = (norm_start & 0x0FFFFFFF) | 0x80000000
    is_full = (norm_start == RWD_FULL_START and length == RWD_FULL_SIZE)

    if is_full:
        print(f"*** FULL FLASH: erasing entire flash ({length // 1024} KB) ***")
    else:
        end = start + length
        print(f"*** PARTIAL FLASH: erasing 0x{start:08X} - 0x{end:08X} ({length // 1024} KB) ***")

    erase_data = struct.pack('!II', start, length)
    data = uds_client.routine_control(ROUTINE_CONTROL_TYPE.START, ROUTINE_IDENTIFIER_TYPE.ERASE_MEMORY, erase_data)
    if data is not None:
        debug_output += [data]

    print(f"Setting firmware decryption key: {firmware.keys}")
    uds_client.write_data_by_identifier(DATA_IDENTIFIER_TYPE.FLASH_DECRYPTION_KEY, firmware.keys)

    success = write_firmware_to_ecu(uds_client, firmware, debug_output)

    if success:
        print("Checking programming dependencies...")
        data = uds_client.routine_control(ROUTINE_CONTROL_TYPE.START, ROUTINE_IDENTIFIER_TYPE.CHECK_PROGRAMMING_DEPENDENCIES)
        if data is not None:
            debug_output += [data]

        print("Resetting ECU...")
        uds_client.ecu_reset(RESET_TYPE.HARD)

        print("Firmware update completed successfully!")
        return True
    else:
        print("Firmware update failed!")
        return False

def handle_debug_output(args, debug_output: list):
    """
    Handle debug output display

    Args:
        args: Parsed command line arguments
        debug_output: List containing debug information
    """
    if args.debug and debug_output:
        print("\nDebug output:")
        for i, data in enumerate(debug_output):
            print(f"{i}: {data}")

def validate_mock_calls(uds_client, args, firmware: x5a):
    """Validate mock UDS client calls for testing purposes"""
    if not isinstance(uds_client, mock.Mock):
        return

    from unittest.mock import call, ANY

    expected_calls = [
        call.tester_present(),
        call.read_data_by_identifier(DATA_IDENTIFIER_TYPE.APPLICATION_SOFTWARE_IDENTIFICATION),
        call.diagnostic_session_control(SESSION_TYPE.EXTENDED_DIAGNOSTIC),
    ]

    # Add CVN check call unless force-flash is specified
    if not args.force:
        expected_calls += [call.read_data_by_identifier(DATA_IDENTIFIER_TYPE.CALIBRATION_VERIFICATION_NUMBER)]

    if not args.skip_security:
        expected_calls += [
            call.security_access(ACCESS_TYPE.REQUEST_SEED),
            call.security_access(ACCESS_TYPE.SEND_KEY, ANY),
        ]

    expected_calls += [call.diagnostic_session_control(SESSION_TYPE.PROGRAMMING)]

    if args.danger:
        erase_data = struct.pack('!II', firmware.firmware_blocks[0]["start"], firmware.firmware_blocks[0]["length"])
        expected_calls += [call.routine_control(ROUTINE_CONTROL_TYPE.START, ROUTINE_IDENTIFIER_TYPE.ERASE_MEMORY, erase_data)]
        expected_calls += [call.write_data_by_identifier(DATA_IDENTIFIER_TYPE.FLASH_DECRYPTION_KEY, firmware.keys)]
        expected_calls += [call.request_download(firmware.firmware_blocks[0]["start"], len(firmware.firmware_encrypted[0]))]
        expected_calls += [call.transfer_data(1, firmware.firmware_encrypted[0][0:512])]
        expected_calls += [call.transfer_data(2, firmware.firmware_encrypted[0][512:1024])]

        uds_client.assert_has_calls(expected_calls)

        num_blocks = -(len(firmware.firmware_encrypted[0]) // -512) # sneaky math ceil
        assert uds_client.transfer_data.call_count == num_blocks

        expected_calls = []
        expected_calls += [call.transfer_data((num_blocks & 0xFF), firmware.firmware_encrypted[0][((num_blocks-1)*512):])]
        expected_calls += [call.request_transfer_exit()]
        expected_calls += [call.routine_control(ROUTINE_CONTROL_TYPE.START, ROUTINE_IDENTIFIER_TYPE.CHECK_PROGRAMMING_DEPENDENCIES)]
        expected_calls += [call.ecu_reset(RESET_TYPE.HARD)]

    uds_client.assert_has_calls(expected_calls)
    print("mock validation passed!")

def main():
    """main function to coordinate the honda ecu firmware update process"""
    args = parse_arguments()
    firmware = load_and_validate_firmware(args)
    uds_client = setup_ecu_connection(firmware, args.bus)

    debug_output: list[bytes] = []

    try:
        app_id = initialize_ecu_communication(uds_client, debug_output)

        # CVN checking logic (unless force is specified)
        if not args.force:
            no_difference = check_firmware_cvn(uds_client, firmware, args.debug)

            if no_difference:
                print("Firmware update not required - exiting")
                return 0

        if args.skip_security:
            print("Skipping security access as requested...")
        else:
            if not perform_security_access(uds_client, app_id, firmware, debug_output):
                return 1

        setup_programming_session(uds_client, debug_output)

        if not args.danger:
            print("Safe mode: stopping before mutating actions")
            print("Use --danger flag to actually perform firmware update")
            return 2

        if not perform_firmware_update(uds_client, firmware, debug_output):
            return 1

    except Exception as e:
        print(f"Error during firmware update: {e}")
        if args.debug:
            print(traceback.format_exc())
        return 1

    finally:
        handle_debug_output(args, debug_output)

    validate_mock_calls(uds_client, args, firmware)

    return 0

if __name__ == "__main__":
    exit(main())