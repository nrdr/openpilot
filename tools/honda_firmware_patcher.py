#!/usr/bin/env python3
"""
Honda ECU Firmware Patcher

This script combines checksum calculation and firmware patching capabilities
to safely update Honda ECU firmware with new cruise control speed settings.

Features:
- Reads and displays current cruise control speed settings
- Verifies current checksum before making changes
- Updates speed values with confirmation of expected current values
- Recalculates and updates the firmware checksum using boot ROM constants
- Creates a patched firmware file

Boot ROM Handling:
- Uses pre-calculated checksums for boot ROM area (0xa0000000-0xa000ffff)
- Boot ROM checksum constants are embedded in this script
- No need for separate boot.bin file during normal operation

Usage:
    python honda_firmware_patcher.py <input_firmware.bin> [options]

Options:
    --min-speed <kmh>     Set minimum cruise control speed (default: no change)
    --output <file>       Output filename (default: <input>_patched.bin)
    --verify-only         Only verify current firmware without patching
    --force               Skip confirmation prompts
    --verbose, -v         Enable verbose output with detailed calculation steps
"""

import sys
import struct
import argparse
from pathlib import Path

# Memory locations for cruise control speeds
CRUISE_SPEED_LOCATIONS = {
    0x8001b1c0: "CRUISE_CONTROL_MIN_SPEED_KPH",
    0x8001b1c2: "CRUISE_MIN_SPEED_KPH_ALT"
}

# Checksum storage location
CHECKSUM_LOCATION = 0x80010100

# Boot ROM checksums (calculated from boot.bin)
# These represent the checksums for memory ranges 0xa0000000-0xa000ffff
# that are not present in the main firmware file
BOOT_ROM_VALIDATION_CHECKSUM = 0xb500

def memory_address_to_file_offset(memory_addr: int) -> int:
    """
    Converts TriCore memory addresses to firmware file offsets.

    TriCore has dual address mapping where the same flash memory can be accessed
    through different address spaces:
    - 0x80010000 base (uncached/data space)
    - 0xa0010000 base (cached/program space)

    Note: Boot ROM area (0xa0000000-0xa000ffff) is handled separately using
    pre-calculated constants since it's not included in the main firmware file.

    Args:
        memory_addr: Memory address (0x80xxxxxx or 0xa0xxxxxx)

    Returns:
        File offset in the firmware binary
    """
    if 0x80010000 <= memory_addr <= 0x8fffffff:
        return memory_addr - 0x80010000
    elif 0xa0010000 <= memory_addr <= 0xafffffff:
        return memory_addr - 0xa0010000
    else:
        raise ValueError(f"Unsupported memory address: 0x{memory_addr:08x}")

def tally_words(data: bytes, start_offset: int, end_offset: int) -> int:
    """
    Implements the exact tally_words algorithm from the Honda ECM firmware.

    Processes memory in 32-byte chunks (8 x 4-byte words) and sums all
    individual bytes from each 32-bit word.

    Args:
        data: The firmware binary data
        start_offset: Starting byte offset in the data
        end_offset: Ending byte offset in the data (exclusive)

    Returns:
        16-bit checksum value (sum & 0xFFFF)
    """
    checksum = 0

    # Process in 32-byte chunks (8 words of 4 bytes each)
    for offset in range(start_offset, end_offset, 32):
        # Ensure we don't read past the end
        chunk_end = min(offset + 32, end_offset, len(data))
        chunk_size = chunk_end - offset

        # Pad with zeros if chunk is smaller than 32 bytes
        chunk = data[offset:chunk_end].ljust(32, b'\x00')

        # Process 8 words (32 bytes)
        for word_idx in range(8):
            word_offset = word_idx * 4
            if word_offset >= chunk_size:
                break

            # Read 4-byte word in little-endian format
            word_bytes = chunk[word_offset:word_offset + 4]
            if len(word_bytes) < 4:
                word_bytes = word_bytes.ljust(4, b'\x00')

            word = struct.unpack('<I', word_bytes)[0]

            # Sum all 4 bytes of the word (equivalent to the bit shifts in C code)
            checksum += (word & 0xFF)          # byte 0
            checksum += (word >> 8) & 0xFF     # byte 1
            checksum += (word >> 16) & 0xFF    # byte 2
            checksum += (word >> 24) & 0xFF    # byte 3

    return checksum & 0xFFFF


def calculate_honda_checksum(firmware_data: bytes, verbose: bool = True) -> tuple[int, dict]:
    """
    Calculates the Honda ECM checksum using the same algorithm as the firmware.

    Args:
        firmware_data: The complete firmware binary
        verbose: Whether to print detailed calculation steps

    Returns:
        Tuple of (final_checksum, intermediate_checksums)
    """

    # Memory ranges from validate_checksum function
    validation_ranges = [
        (0xa0000000, 0xa007ffff),
        (0xa0080000, 0xa00fffff),
        (0xa0100000, 0xa017ffff),
        (0xa0180000, 0xa01fffff),
    ]

    # Memory ranges from calculate_rom_checksum function
    rom_ranges = [
        (0xa0200000, 0xa027ffff),
        (0xa0280000, 0xa02fffff),
        (0xa0300000, 0xa037ffff),
        (0xa0380000, 0xa03ffffe),
    ]

    checksums = {}

    # Calculate validation checksums
    validation_checksum = 0
    for i, (start_addr, end_addr) in enumerate(validation_ranges):
        start_offset = memory_address_to_file_offset(start_addr)

        # Handle boot ROM range (0xa0000000-0xa007ffff) specially
        if start_addr == 0xa0000000:
            # This range includes boot ROM (0xa0000000-0xa000ffff) + firmware (0xa0010000-0xa007ffff)
            # Boot ROM portion: use pre-calculated constant
            boot_checksum = BOOT_ROM_VALIDATION_CHECKSUM

            # Firmware portion: 0xa0010000-0xa007ffff
            firmware_start_addr = 0xa0010000
            firmware_start_offset = memory_address_to_file_offset(firmware_start_addr)
            firmware_size = (end_addr - firmware_start_addr + 1)
            firmware_end_offset = firmware_start_offset + firmware_size

            firmware_checksum = tally_words(firmware_data, firmware_start_offset, firmware_end_offset)
            range_checksum = (boot_checksum + firmware_checksum) & 0xFFFF

            if verbose:
                print(f"Validation range {i}: 0x{start_addr:08x}-0x{end_addr:08x}")
                print(f"  Boot ROM (0xa0000000-0xa000ffff): 0x{boot_checksum:04x}")
                print(f"  Firmware (0xa0010000-0x{end_addr:08x}): 0x{firmware_checksum:04x}")
                print(f"  Combined: 0x{range_checksum:04x}")
        else:
            # Regular firmware ranges
            size = (end_addr - start_addr + 1)
            end_offset = start_offset + size
            range_checksum = tally_words(firmware_data, start_offset, end_offset)
            if verbose:
                print(f"Validation range {i}: 0x{start_addr:08x}-0x{end_addr:08x} = 0x{range_checksum:04x}")

        checksums[f'validation_range_{i}'] = range_checksum
        validation_checksum = (validation_checksum + range_checksum) & 0xFFFF

    # Calculate ROM checksums
    rom_checksum = 0
    for i, (start_addr, end_addr) in enumerate(rom_ranges):
        start_offset = memory_address_to_file_offset(start_addr)
        size = (end_addr - start_addr + 1)
        end_offset = start_offset + size

        range_checksum = tally_words(firmware_data, start_offset, end_offset)
        checksums[f'rom_range_{i}'] = range_checksum
        rom_checksum = (rom_checksum + range_checksum) & 0xFFFF
        if verbose:
            print(f"ROM range {i}: 0x{start_addr:08x}-0x{end_addr:08x} = 0x{range_checksum:04x}")

    # Combine checksums as done in validate_checksum function
    final_checksum = (validation_checksum + rom_checksum) & 0xFFFF

    checksums['validation_total'] = validation_checksum
    checksums['rom_total'] = rom_checksum
    checksums['final_checksum'] = final_checksum

    if verbose:
        print(f"\nValidation checksum: 0x{validation_checksum:04x}")
        print(f"ROM checksum: 0x{rom_checksum:04x}")
        print(f"Combined checksum: 0x{final_checksum:04x}")

    return final_checksum, checksums

def calculate_required_stored_checksum(firmware_data: bytes, verbose: bool) -> bytes:
    """
    Calculates what should be stored at 0x80010100 to make validation pass.

    The validation checks if (total_checksum & 0xFF) == 0.
    The stored bytes contribute to the checksum calculation, so we need to
    find bytes that make the total sum's LSB equal to zero.

    Args:
        firmware_data: The firmware binary data
        verbose: Whether to print detailed calculation steps

    Returns:
        4-byte array that should be stored at 0x80010100
    """
    firmware_copy = bytearray(firmware_data)
    checksum_offset = memory_address_to_file_offset(CHECKSUM_LOCATION)

    # Zero out the checksum location
    firmware_copy[checksum_offset:checksum_offset + 4] = b'\x00\x00\x00\x00'

    # Calculate checksum without the checksum bytes
    calculated_checksum, _ = calculate_honda_checksum(firmware_copy, verbose=verbose)

    # We need: (calculated_checksum + sum_of_stored_bytes) & 0xFF == 0
    # So: sum_of_stored_bytes = (0x100 - (calculated_checksum & 0xFF)) & 0xFF
    required_sum = (0x100 - (calculated_checksum & 0xFF)) & 0xFF

    # We can put the entire required sum in one byte and zero the others
    # Let's put it in byte 2 (bits 16-23) to match the original pattern
    stored_bytes = struct.pack('<I', required_sum << 16)

    if verbose:
        print(f"Calculated checksum (without checksum bytes): 0x{calculated_checksum:04x}")
        print(f"Required sum of stored bytes: 0x{required_sum:02x}")
        print(f"Stored checksum bytes: {stored_bytes.hex().upper()}")

    return stored_bytes

def read_current_cruise_speeds(firmware_data: bytes, verbose: bool) -> dict:
    """
    Reads the current cruise control speed settings from the firmware.

    Args:
        firmware_data: The firmware binary data
        verbose: Whether to print detailed information

    Returns:
        Dictionary mapping location names to speed values in km/h
    """
    print("Current cruise control speed settings:")
    speeds = {}

    for memory_addr, name in CRUISE_SPEED_LOCATIONS.items():
        try:
            file_offset = memory_address_to_file_offset(memory_addr)
            if file_offset + 2 <= len(firmware_data):
                speed_bytes = firmware_data[file_offset:file_offset + 2]
                speed_value = struct.unpack('<H', speed_bytes)[0]
                speed_kmh = speed_value / 100.0
                speeds[name] = speed_kmh

                if verbose:
                    print(f"  {name}:")
                    print(f"    Address: 0x{memory_addr:08x} -> File offset: 0x{file_offset:08x}")
                    print(f"    Raw value: 0x{speed_value:04X} ({speed_value})")
                    print(f"    Speed: {speed_kmh:.1f} km/h")
                else:
                    print(f"  {name}: {speed_kmh:.1f} km/h")
            else:
                print(f"  {name}: Offset beyond file size")
                speeds[name] = None

        except ValueError as e:
            print(f"  {name}: Error - {e}")
            speeds[name] = None

    return speeds

def read_current_checksum(firmware_data: bytes, verbose: bool) -> int | None:
    """
    Reads the current checksum from the firmware.

    Args:
        firmware_data: The firmware binary data
        verbose: Whether to print detailed information

    Returns:
        Current checksum value or None if error
    """
    print("\nCurrent checksum:")

    try:
        checksum_offset = memory_address_to_file_offset(CHECKSUM_LOCATION)
        if checksum_offset + 4 <= len(firmware_data):
            checksum_bytes = firmware_data[checksum_offset:checksum_offset + 4]
            checksum_value = struct.unpack('<I', checksum_bytes)[0]

            if verbose:
                print(f"  Address: 0x{CHECKSUM_LOCATION:08x} -> File offset: 0x{checksum_offset:08x}")
                print(f"  Raw bytes: {checksum_bytes.hex().upper()}")
                print(f"  Value: 0x{checksum_value:08x}")
                print(f"  Individual bytes: {[f'0x{b:02x}' for b in checksum_bytes]}")
            else:
                print(f"  Value: 0x{checksum_value:08x}")
            return checksum_value
        else:
            print("  Checksum location beyond file size")
            return None

    except ValueError as e:
        print(f"  Error reading checksum: {e}")
        return None

def verify_firmware_checksum(firmware_data: bytes, verbose: bool) -> bool:
    """
    Verifies that the current firmware checksum is correct.

    Args:
        firmware_data: The firmware binary
        verbose: Whether to print detailed calculation steps

    Returns:
        True if checksum validation passes, False otherwise
    """
    print("Verifying current firmware checksum...")

    # Read the stored checksum from 0x80010100
    try:
        checksum_offset = memory_address_to_file_offset(CHECKSUM_LOCATION)
        if checksum_offset + 4 > len(firmware_data):
            print("Error: Checksum location is beyond firmware file size")
            return False

        stored_checksum_bytes = firmware_data[checksum_offset:checksum_offset + 4]
        stored_checksum = struct.unpack('<I', stored_checksum_bytes)[0]
        if verbose:
            print(f"Stored checksum at 0x{CHECKSUM_LOCATION:08x}: {stored_checksum_bytes.hex().upper()} (0x{stored_checksum:08x})")

    except ValueError as e:
        print(f"Error reading stored checksum: {e}")
        return False

    # Calculate the current checksum
    calculated_checksum, details = calculate_honda_checksum(firmware_data, verbose=verbose)

    # Verify validation logic: (calculated + stored_validation_byte) & 0xFF should be 0
    # The Honda ECU uses byte 2 (bits 16-23) of the stored checksum for validation
    stored_validation_byte = (stored_checksum >> 16) & 0xFF
    validation_result = (calculated_checksum + stored_validation_byte) & 0xFF
    passed = validation_result == 0

    print(f"Calculated checksum: 0x{calculated_checksum:04x}")
    if verbose:
        print(f"Stored validation byte: 0x{stored_validation_byte:02x}")
        print(f"Validation result: (0x{calculated_checksum:04x} + 0x{stored_validation_byte:02x}) & 0xFF = 0x{validation_result:02x}")
    print(f"Checksum validation: {'PASS' if passed else 'FAIL'}")

    return passed

def update_cruise_speed(firmware_data: bytearray, memory_addr: int, new_speed_kmh: float,
                       verbose: bool, expected_current_kmh: float | None = None) -> bool:
    """
    Updates a cruise control speed value in the firmware.

    Args:
        firmware_data: The firmware binary data (mutable)
        memory_addr: Memory address of the speed value
        new_speed_kmh: New speed value in km/h
        expected_current_kmh: Expected current speed (for verification)
        verbose: Whether to print detailed information

    Returns:
        True if update was successful, False otherwise
    """
    try:
        file_offset = memory_address_to_file_offset(memory_addr)
        if file_offset + 2 > len(firmware_data):
            print(f"Error: Speed location 0x{memory_addr:08x} is beyond firmware file size")
            return False

        # Read current value
        current_bytes = firmware_data[file_offset:file_offset + 2]
        current_value = struct.unpack('<H', current_bytes)[0]
        current_kmh = current_value / 100.0

        # Verify expected current value if provided
        if expected_current_kmh is not None:
            if abs(current_kmh - expected_current_kmh) > 0.1:  # Allow small floating point differences
                print(f"Error: Expected current speed {expected_current_kmh:.1f} km/h, but found {current_kmh:.1f} km/h")
                print(f"       at address 0x{memory_addr:08x}")
                return False

        # Calculate new raw value
        new_value = int(new_speed_kmh * 100)
        if new_value > 0xFFFF:
            print(f"Error: New speed value {new_speed_kmh} km/h is too large (max 655.35 km/h)")
            return False

        # Update the firmware
        new_bytes = struct.pack('<H', new_value)
        firmware_data[file_offset:file_offset + 2] = new_bytes

        if verbose:
            print(f"Updated speed at 0x{memory_addr:08x}:")
            print(f"  Old: {current_kmh:.1f} km/h (0x{current_value:04X})")
            print(f"  New: {new_speed_kmh:.1f} km/h (0x{new_value:04X})")
        else:
            print(f"Updated speed at 0x{memory_addr:08x}: {current_kmh:.1f} -> {new_speed_kmh:.1f} km/h")

        return True

    except ValueError as e:
        print(f"Error updating speed at 0x{memory_addr:08x}: {e}")
        return False

def update_checksum(firmware_data: bytearray, verbose: bool) -> bool:
    """
    Recalculates and updates the firmware checksum.

    Args:
        firmware_data: The firmware binary data (mutable)
        verbose: Whether to print detailed calculation steps

    Returns:
        True if update was successful, False otherwise
    """
    try:
        # Calculate required stored checksum
        print("\nRecalculating checksum...")
        required_bytes = calculate_required_stored_checksum(firmware_data, verbose=verbose)

        # Update the checksum in firmware
        checksum_offset = memory_address_to_file_offset(CHECKSUM_LOCATION)
        if checksum_offset + 4 > len(firmware_data):
            print("Error: Checksum location is beyond firmware file size")
            return False

        # Read old checksum
        old_bytes = firmware_data[checksum_offset:checksum_offset + 4]
        old_value = struct.unpack('<I', old_bytes)[0]

        # Write new checksum
        firmware_data[checksum_offset:checksum_offset + 4] = required_bytes
        new_value = struct.unpack('<I', required_bytes)[0]

        if verbose:
            print(f"\nUpdated checksum at 0x{CHECKSUM_LOCATION:08x}:")
            print(f"  Old: {old_bytes.hex().upper()} (0x{old_value:08x})")
            print(f"  New: {required_bytes.hex().upper()} (0x{new_value:08x})")
        else:
            print(f"Updated checksum: 0x{old_value:08x} -> 0x{new_value:08x}")

        return True

    except ValueError as e:
        print(f"Error updating checksum: {e}")
        return False

def main():
    """
    Main function to handle command line arguments and coordinate the patching process.
    """
    parser = argparse.ArgumentParser(
        description="Honda ECU Firmware Patcher - Updates cruise control speeds and checksums",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify current firmware only
  python honda_firmware_patcher.py firmware.bin --verify-only

  # Set minimum cruise speed to 25 km/h
  python honda_firmware_patcher.py firmware.bin --min-speed 25.0

  # Set speed with custom output filename
  python honda_firmware_patcher.py firmware.bin --min-speed 30.0 --output custom_patched.bin

  # Enable verbose output for detailed calculation steps
  python honda_firmware_patcher.py firmware.bin --verify-only --verbose
        """
    )

    parser.add_argument('firmware', help='Input firmware file (.bin)')
    parser.add_argument('--min-speed', type=float, metavar='KMH',
                       help='Set minimum cruise control speed in km/h')
    parser.add_argument('--output', metavar='FILE',
                       help='Output filename (default: <input>_patched.bin)')
    parser.add_argument('--verify-only', action='store_true',
                       help='Only verify current firmware without patching')
    parser.add_argument('--force', action='store_true',
                       help='Skip confirmation prompts')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output with detailed calculation steps')

    args = parser.parse_args()

    # Validate input file
    firmware_file = Path(args.firmware)
    if not firmware_file.exists():
        print(f"Error: Firmware file '{firmware_file}' not found")
        return 1

    # Set output filename
    if args.output:
        output_file = Path(args.output)
    else:
        output_file = firmware_file.with_stem(firmware_file.stem + '_patched')

    print("Honda ECU Firmware Patcher")
    print("=" * 50)
    print(f"Input file: {firmware_file}")
    if not args.verify_only:
        print(f"Output file: {output_file}")
    print()

    # Load firmware
    print("Loading firmware...")
    try:
        with open(firmware_file, 'rb') as f:
            firmware_data = bytearray(f.read())
    except Exception as e:
        print(f"Error loading firmware: {e}")
        return 1

    print(f"Firmware size: {len(firmware_data):,} bytes (0x{len(firmware_data):x})")
    print()

    current_speeds = read_current_cruise_speeds(firmware_data, verbose=args.verbose)

    print("\n" + "=" * 50)
    checksum_valid = verify_firmware_checksum(firmware_data, verbose=args.verbose)

    if not checksum_valid:
        print("\nWARNING: Current firmware checksum validation failed!")
        print("This may indicate corrupted firmware or an incorrect algorithm.")
        if not args.force:
            response = input("Continue anyway? (y/N): ").strip().lower()
            if response != 'y':
                print("Aborted.")
                return 1

    if args.verify_only:
        print("\nVerification complete!")
        return 0 if checksum_valid else 1

    if args.min_speed is None:
        print("\nNo changes requested. Use --min-speed to specify new speed value.")
        return 0

    print("\n" + "=" * 50)
    print("PROPOSED CHANGES:")
    if args.min_speed is not None:
        print(f"  Minimum cruise speed: {args.min_speed:.1f} km/h")

    if not args.force:
        print(f"\nThis will create a patched firmware file: {output_file}")
        response = input("Proceed with patching? (y/N): ").strip().lower()
        if response != 'y':
            print("Aborted.")
            return 0

    print("\n" + "=" * 50)
    print("APPLYING PATCHES:")

    success = True

    if args.min_speed is not None:
        current_min_speed = current_speeds.get("CRUISE_CONTROL_MIN_SPEED_KPH")

        for addr, _name in CRUISE_SPEED_LOCATIONS.items():
            if not update_cruise_speed(firmware_data, addr, args.min_speed, args.verbose, current_min_speed):
                success = False
                break

    if not success:
        print("\nPatching failed!")
        return 1

    # Update checksum
    if not update_checksum(firmware_data, verbose=args.verbose):
        print("\nChecksum update failed!")
        return 1

    # Verify the patched firmware
    print("\n" + "=" * 50)
    print("VERIFYING PATCHED FIRMWARE:")
    if not verify_firmware_checksum(firmware_data, verbose=args.verbose):
        print("\nWARNING: Patched firmware checksum validation failed!")
        print("There may be an error in the patching process.")
        if not args.force:
            response = input("Save anyway? (y/N): ").strip().lower()
            if response != 'y':
                print("Patched firmware not saved.")
                return 1

    # Save patched firmware
    try:
        with open(output_file, 'wb') as f:
            f.write(firmware_data)
        print(f"\nPatched firmware saved to: {output_file}")
        print(f"File size: {len(firmware_data):,} bytes")
    except Exception as e:
        print(f"\nError saving patched firmware: {e}")
        return 1

    print("\nPatching completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
