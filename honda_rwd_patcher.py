#!/usr/bin/env python3
"""
Honda RWD Firmware Patcher
Uses enhanced x5a library to read/write RWD files with optional gzip compression

This script provides a framework for modifying Honda RWD firmware files while
automatically handling encryption/decryption, CVN recalculation, and gzip compression.

Features:
- Automatic gzip detection and handling
- CVN recalculation for modified firmware
- Support for various firmware modification patterns
- Preserve original file structure and headers
- Comprehensive error handling and validation
- Verbose output for debugging

Usage:
    python honda_rwd_patcher.py input.rwd [options]
    python honda_rwd_patcher.py input.rwd.gz [options]

Examples:
    # Basic patch with default modifications
    python honda_rwd_patcher.py firmware.rwd --output patched.rwd

    # Patch with custom speed limit (example modification)
    python honda_rwd_patcher.py firmware.rwd.gz --patch-speed-limit 25.0

    # Verbose mode for debugging
    python honda_rwd_patcher.py firmware.rwd --verbose --output debug_patched.rwd

    # Apply custom byte patches
    python honda_rwd_patcher.py firmware.rwd --patch-bytes 0x1000:0xAB,0x2000:0xCD
"""

import os
import sys
import gzip
import argparse
import struct
from pathlib import Path

# Import the enhanced x5a library
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from panda.format.x5a import x5a

# ──────────────────────────────────────────────────────────────────────
# ECU firmware database
#
# Keyed by Honda ECU software ID (the part number stamped on the ECU
# label and embedded in the RWD header, e.g. "37805-RLV-L090").
#
# All offsets are byte positions within the decrypted firmware blob
# (i.e. absolute_address - firmware_base).
#
# Values determined via Ghidra reverse engineering of each firmware.
# ──────────────────────────────────────────────────────────────────────
ECU_FIRMWARE_DB = {
    "37805-RLV-L090": {
        # -- Identity --
        "description": "Honda CR-V RW1/RW2 2.0L Hybrid, Infineon AURIX TC27x",
        "firmware_base": 0xA0010000,  # RWD data start: cached PFlash + 64KB boot skip
        #   Bootloader expects 0xA0xxxxxx (cached PFlash segment).
        #   flash_lookup_sector_by_address does (addr + 0x60000000 < 0x400001),
        #   which only passes for 0xA0xxxxxx, not 0x80xxxxxx.
        #   The RWD file itself stores start=0xA0010000 (verified from real .rwd).

        # -- ACC minimum speed calibration --
        # Two constants enforce the 40 km/h floor via dual-channel checks:
        #   CRUISE_CONTROL_MIN_SPEED_KPH  - gates ACC CAN command acceptance
        #                                    and ACC permit/fault flag logic
        #                                    (compared vs. analog wheel speed ADC)
        #   CRUISE_MIN_SPEED_KPH_ALT      - gates sensor fault monitoring and
        #                                    signal integrity cross-checking
        #                                    (compared vs. CAN bus digital speed)
        #
        # All offsets are byte positions within the decrypted firmware blob
        # (i.e. absolute_address - firmware_base).
        "speed_limit_patches": [
            {
                "name": "CRUISE_CONTROL_MIN_SPEED_KPH",
                "offset": 0xB1C0,
                "expected": 0x0FA0,       # 4000 = 40.00 km/h
                "size": 2,                # ushort, little-endian
            },
            {
                "name": "CRUISE_MIN_SPEED_KPH_ALT",
                "offset": 0xB1C2,
                "expected": 0x0FA0,       # 4000 = 40.00 km/h
                "size": 2,                # short, little-endian
            },
        ],
        "speed_scale": 100,               # raw_value = km/h * 100

        # -- CVN (Calibration Verification Number) --
        # ECU computes CVN over 0xA0010000–0xA0400000 on every boot
        # (compute_calibration_verification_number @ 0x800735FE).
        # This exactly matches the RWD data range, so CVN = checksum(firmware_data).
        "cvn_block_size": 0x3F000,        # 252 KB — matches firmware's per-task scan block size

        # -- Boot flash checksum complement --
        # The boot-time flash checksum (calculate_flash_checksum @ 0x8004E162)
        # sums every byte in the 4MB flash using tally_words. The low byte
        # must equal 0x00 or the ECU triggers a fatal watchdog reset.
        #
        # We use a byte in the calibration section's zero-fill area
        # (sector 0x4000–0x8000, abs 0xA0014000–0xA0018000) so that
        # --partial only needs to flash calibration sectors (~32KB)
        # instead of spanning to the original Honda complement at
        # 0xA0309C08 (~3.2MB).
        #
        # The zero-fill area at 0xA0014002–0xA0017FFF has no xrefs from
        # either the 0xA0 (cached) or 0x80 (non-cached) PFlash mappings,
        # no disassembly operand hits, and is undefined in Ghidra.
        # Offset 0x7FFE (abs 0xA0017FFE) is deep in this dead zone,
        # at the end of the sector before the speed limit's sector.
        "flash_checksum_complement_offset": 0x7FFE,  # abs addr: a0017FFE (calibration zero-fill)

        # -- Validation --
        "expected_firmware_size": 0x3F0000,  # 4032 KB (full flash minus 64KB bootloader)

        # -- Flash sector boundaries (data-relative offsets) --
        # Extracted from bootloader sector lookup table at 0x60106C54 (55 entries).
        # Bootloader validates erase start/end addresses against this table;
        # non-aligned addresses are rejected with NRC 0x31 (requestOutOfRange).
        #
        # These are offsets within the firmware data blob (byte 0 = 0xA0010000).
        # The bootloader's first 4 sectors (0x00000000–0x0000FFFF) are not in
        # the RWD and cannot be erased via this path.
        #
        # TC29x PFlash layout (data-relative, starting after 64KB bootloader):
        "sector_boundaries": [
            # -- PFlash0 remainder (0xA0010000 – 0xA01FFFFF) --
            0x000000, 0x004000, 0x008000, 0x00C000,             # 4 × 16 KB
            0x010000, 0x018000, 0x020000, 0x028000,             # 8 × 32 KB
            0x030000, 0x038000, 0x040000, 0x048000,
            0x050000, 0x060000, 0x070000, 0x080000,             # 4 × 64 KB
            0x090000, 0x0B0000, 0x0D0000,                       # 3 × 128 KB
            0x0F0000, 0x130000, 0x170000, 0x1B0000,             # 4 × 256 KB
            # -- PFlash1 (0xA0200000 – 0xA03FFFFF) --
            0x1F0000,                                           # 8 × 16 KB
            0x1F4000, 0x1F8000, 0x1FC000,
            0x200000, 0x204000, 0x208000, 0x20C000,
            0x210000, 0x218000, 0x220000, 0x228000,             # 8 × 32 KB
            0x230000, 0x238000, 0x240000, 0x248000,
            0x250000, 0x260000, 0x270000, 0x280000,             # 4 × 64 KB
            0x290000, 0x2B0000, 0x2D0000,                       # 3 × 128 KB
            0x2F0000, 0x330000, 0x370000, 0x3B0000,             # 4 × 256 KB
            # -- End of data --
            0x3F0000,
        ],

        # -- Named flash regions for --partial-region shorthand --
        # Offsets are data-relative (byte 0 = first byte after bootloader).
        # Each region must start and end on sector boundaries from the table above.
        "flash_regions": {
            "calibration": {"offset": 0x000000, "size": 0x010000},   # 64 KB  — calibration data (first 4 data sectors)
            "application": {"offset": 0x010000, "size": 0x1E0000},   # 1920 KB — application code (PFlash0 remainder)
            "pflash1":     {"offset": 0x1F0000, "size": 0x200000},   # 2 MB   — entire PFlash1 bank
        },
    },
}


def get_ecu_id_from_rwd(rwd_obj, verbose=False):
    """
    Extract the ECU software ID from the parsed RWD file headers.

    Header 3 lists the firmware versions this RWD can update from,
    with the last entry being the target version (e.g. "37805-RLV-L090").
    Values are null-padded strings.
    """
    header_3_values = rwd_obj.get_header_3_values()
    if not header_3_values:
        return None

    ecu_id = header_3_values[-1].strip('\x00').strip()
    if verbose:
        print(f"Detected ECU software ID from header 3: {ecu_id}")
        print(f"  Update path: {' -> '.join(v.strip(chr(0)).strip() for v in header_3_values)}")
    return ecu_id


def lookup_ecu_config(ecu_id, verbose=False):
    """
    Look up ECU-specific configuration from the firmware database.

    Returns the config dict or raises ValueError if the ECU is unknown.
    """
    if ecu_id is None:
        raise ValueError(
            "Could not detect ECU software ID from the RWD headers.\n" +
            "Use --ecu-id to specify it manually (e.g. --ecu-id 37805-RLV-L090)."
        )
    config = ECU_FIRMWARE_DB.get(ecu_id)
    if config is None:
        known = ", ".join(sorted(ECU_FIRMWARE_DB.keys())) or "(none)"
        raise ValueError(
            f"Unknown ECU software ID: {ecu_id}\n" +
            f"Known firmware IDs: {known}\n" +
            "Add this ECU to ECU_FIRMWARE_DB before patching."
        )
    if verbose:
        print(f"Using firmware profile: {ecu_id} — {config['description']}")
    return config

def read_rwd_file(filepath: str, verbose: bool = False) -> tuple[bytes, bool]:
    """
    Read RWD file with automatic gzip detection.

    Args:
        filepath: Path to RWD file
        verbose: Enable verbose output

    Returns:
        Tuple of (file_data, was_compressed)
    """
    file_path = Path(filepath)

    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    # Check if file is gzip compressed by extension or magic bytes
    is_compressed = file_path.suffix.lower() == '.gz'

    if verbose:
        print(f"Reading input file: {file_path}")
        print(f"File size: {file_path.stat().st_size:,} bytes")

    try:
        if is_compressed:
            if verbose:
                print("Detected gzip compression by file extension")
            with gzip.open(file_path, 'rb') as f:
                data = f.read()
        else:
            # Check for gzip magic bytes even without .gz extension
            with open(file_path, 'rb') as f:
                magic = f.read(2)
                f.seek(0)

                if magic == b'\x1f\x8b':  # gzip magic bytes
                    if verbose:
                        print("Detected gzip compression by magic bytes")
                    is_compressed = True
                    with gzip.open(file_path, 'rb') as gz_f:
                        data = gz_f.read()
                else:
                    if verbose:
                        print("Reading uncompressed file")
                    data = f.read()

    except Exception as e:
        raise RuntimeError(f"Error reading file {file_path}: {e}") from e

    if verbose:
        print(f"Decompressed size: {len(data):,} bytes")
        print(f"Compression detected: {is_compressed}")

    # Validate RWD file format
    if len(data) < 3 or data[:3] != b'\x5A\x0D\x0A':
        raise ValueError("Invalid RWD file format - missing magic bytes")

    return data, is_compressed

def write_rwd_file(filepath: str, data: bytes, compress: bool = False, verbose: bool = False) -> str:
    """
    Write RWD file with optional gzip compression.

    Args:
        filepath: Output file path
        data: RWD file data to write
        compress: Whether to compress with gzip
        verbose: Enable verbose output

    Returns:
        Path to written file
    """
    file_path = Path(filepath)

    # Adjust extension based on compression
    if compress and not str(file_path).endswith('.gz'):
        file_path = file_path.with_suffix(file_path.suffix + '.gz')
    elif not compress and str(file_path).endswith('.gz'):
        file_path = file_path.with_suffix('')

    if verbose:
        print(f"Writing output file: {file_path}")
        print(f"Data size: {len(data):,} bytes")
        print(f"Compression: {'enabled' if compress else 'disabled'}")

    try:
        # Create parent directories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)

        if compress:
            with gzip.open(file_path, 'wb') as f:
                f.write(data)
        else:
            with open(file_path, 'wb') as f:
                f.write(data)

        if verbose:
            written_size = file_path.stat().st_size
            print(f"Written file size: {written_size:,} bytes")
            if compress:
                compression_ratio = (1 - written_size / len(data)) * 100
                print(f"Compression ratio: {compression_ratio:.1f}%")

    except Exception as e:
        raise RuntimeError(f"Error writing file {file_path}: {e}") from e

    return str(file_path)

def calculate_honda_cvn(firmware_data: bytes, ecu_config: dict = None, verbose: bool = False) -> bytes:
    """
    Calculate Honda ECU Calibration Verification Number from firmware data.

    Args:
        firmware_data: Raw firmware binary data
        ecu_config: ECU-specific config from ECU_FIRMWARE_DB (optional)
        verbose: Enable verbose output

    Returns:
        4-byte CVN value
    """
    if verbose:
        print("Calculating CVN for modified firmware...")

    # Initialize checksums (16-bit values)
    additive_checksum = 0
    xor_checksum = 0

    # Firmware scanning parameters — use ECU-specific block size if available
    BLOCK_SIZE = (ecu_config or {}).get('cvn_block_size', 0x3F000)
    CHUNK_SIZE = 32       # 32 bytes per iteration (8 × 32-bit words)

    # Calculate total firmware size and number of blocks
    firmware_size = len(firmware_data)
    total_blocks = (firmware_size + BLOCK_SIZE - 1) // BLOCK_SIZE

    if verbose:
        print(f"Firmware size: {firmware_size:,} bytes ({firmware_size:#x})")
        print(f"Processing {total_blocks} blocks of {BLOCK_SIZE:#x} bytes each")

    # Process firmware in blocks
    for block_index in range(total_blocks):
        block_start = block_index * BLOCK_SIZE
        block_end = min(block_start + BLOCK_SIZE, firmware_size)
        block_data = firmware_data[block_start:block_end]

        if verbose and total_blocks > 1:
            print(f"Processing block {block_index}: {block_start:#x} - {block_end:#x}")

        # Process each block in 32-byte chunks
        for chunk_offset in range(0, len(block_data), CHUNK_SIZE):
            chunk_end = min(chunk_offset + CHUNK_SIZE, len(block_data))
            chunk = block_data[chunk_offset:chunk_end]

            # Pad chunk to 32 bytes if needed
            if len(chunk) < CHUNK_SIZE:
                chunk = chunk.ljust(CHUNK_SIZE, b'\x00')

            # Read 8 consecutive 32-bit words (little-endian)
            words = struct.unpack('<8I', chunk)

            # Process each 32-bit word
            for word in words:
                # Split into high and low 16-bit values
                low_16 = word & 0xFFFF
                high_16 = (word >> 16) & 0xFFFF

                # Update checksums with both 16-bit values
                additive_checksum = (additive_checksum + low_16 + high_16) & 0xFFFF
                xor_checksum = (xor_checksum ^ low_16 ^ high_16) & 0xFFFF

    if verbose:
        print(f"Final checksums: additive=0x{additive_checksum:04x}, xor=0x{xor_checksum:04x}")

    # Calculate CVN components
    checksum_sum = (additive_checksum + xor_checksum) & 0xFFFF
    checksum_difference = ((additive_checksum - xor_checksum) + 0x10000) & 0xFFFF

    if verbose:
        print(f"CVN components: sum=0x{checksum_sum:04x}, diff=0x{checksum_difference:04x}")

    # Pack CVN as 4 bytes: [sum_hi, sum_lo, diff_hi, diff_lo]
    cvn_bytes = struct.pack('BBBB',
        (checksum_sum >> 8) & 0xFF,     # sum high byte
        checksum_sum & 0xFF,            # sum low byte
        (checksum_difference >> 8) & 0xFF,  # difference high byte
        checksum_difference & 0xFF      # difference low byte
    )

    if verbose:
        cvn_hex = ' '.join(f'{b:02X}' for b in cvn_bytes)
        print(f"Calculated CVN: {cvn_hex}")

    return cvn_bytes

def apply_firmware_patches(firmware_data: bytearray, patch_config: dict,
                          ecu_config: dict = None, verbose: bool = False) -> bool:
    """
    Apply patches to firmware data based on configuration.

    Args:
        firmware_data: Firmware data to modify (mutable)
        patch_config: Dictionary containing patch configuration
        ecu_config: ECU-specific config from ECU_FIRMWARE_DB
        verbose: Enable verbose output

    Returns:
        True if any patches were applied, False otherwise
    """
    patches_applied = False

    if verbose:
        print("Applying firmware patches...")

    # Speed limit patch — uses ECU-specific offsets and validates expected values
    if 'speed_limit_kmh' in patch_config:
        speed_limit = patch_config['speed_limit_kmh']
        if verbose:
            print(f"Applying speed limit patch: {speed_limit} km/h")

        if ecu_config is None:
            raise ValueError("Cannot apply speed limit patch without ECU firmware profile")

        speed_patches = ecu_config['speed_limit_patches']
        scale = ecu_config['speed_scale']
        raw_value = int(speed_limit * scale)

        if raw_value < 0 or raw_value > 0xFFFF:
            raise ValueError(f"Speed {speed_limit} km/h out of range (raw={raw_value})")

        for patch in speed_patches:
            addr = patch['offset']
            expected = patch['expected']
            name = patch['name']

            if addr + 1 >= len(firmware_data):
                raise ValueError(f"Offset 0x{addr:06X} ({name}) is beyond firmware size")

            actual = struct.unpack('<H', firmware_data[addr:addr+2])[0]
            if actual != expected:
                raise ValueError(
                    f"Unexpected value at 0x{addr:06X} ({name}): " +
                    f"found 0x{actual:04X} ({actual/scale:.1f} km/h), " +
                    f"expected 0x{expected:04X} ({expected/scale:.1f} km/h). " +
                    "Wrong firmware version?"
                )

            firmware_data[addr:addr+2] = struct.pack('<H', raw_value)
            if verbose:
                print(f"  {name} @ 0x{addr:06X}: {actual/scale:.1f} -> {speed_limit:.1f} km/h")
            patches_applied = True

    # Example: Byte patches
    if 'byte_patches' in patch_config:
        byte_patches = patch_config['byte_patches']
        if verbose:
            print(f"Applying {len(byte_patches)} byte patches")

        for addr, value in byte_patches.items():
            if addr < len(firmware_data):
                old_value = firmware_data[addr]
                firmware_data[addr] = value
                if verbose:
                    print(f"  Address 0x{addr:06X}: 0x{old_value:02X} -> 0x{value:02X}")
                patches_applied = True

    # Example: Pattern replacement
    if 'pattern_replacements' in patch_config:
        replacements = patch_config['pattern_replacements']
        if verbose:
            print(f"Applying {len(replacements)} pattern replacements")

        for old_pattern, new_pattern in replacements.items():
            old_bytes = bytes.fromhex(old_pattern) if isinstance(old_pattern, str) else old_pattern
            new_bytes = bytes.fromhex(new_pattern) if isinstance(new_pattern, str) else new_pattern

            # Find and replace all occurrences
            pos = 0
            count = 0
            while True:
                pos = firmware_data.find(old_bytes, pos)
                if pos == -1:
                    break
                firmware_data[pos:pos+len(old_bytes)] = new_bytes
                pos += len(new_bytes)
                count += 1

            if count > 0:
                patches_applied = True
                if verbose:
                    print(f"  Replaced pattern {old_pattern} -> {new_pattern} ({count} occurrences)")

    if verbose:
        if patches_applied:
            print("Firmware patches applied successfully")
        else:
            print("No patches were applied")

    return patches_applied


def update_flash_checksum_complement(firmware_data: bytearray,
                                     ecu_config: dict,
                                     original_firmware: bytes,
                                     verbose: bool = False) -> None:
    """
    Update the flash checksum complement byte to maintain boot integrity.

    The boot-time flash checksum (calculate_flash_checksum @ 0x8004E162) runs
    on every boot across the entire 4MB flash (a0000000-a03fffff), including
    the 64KB bootloader. It uses the tally_words algorithm which sums
    w + (w>>8) + (w>>16) + (w>>24) for each 32-bit word. The low byte of
    the final result must equal 0x00 or the ECU triggers a fatal watchdog
    reset.

    The low byte of the tally_words result equals the sum of all individual
    bytes mod 256. Since the boot check covers bootloader + firmware and we
    only control firmware bytes, we must preserve the original firmware's
    byte sum (which the factory set so that boot + firmware sums to 0).

    Args:
        firmware_data: Full firmware data to modify (mutable bytearray)
        ecu_config: ECU-specific config with flash_checksum_complement_offset
        original_firmware: Original unmodified firmware (used to derive target byte sum)
        verbose: Enable verbose output
    """
    complement_offset = ecu_config.get('flash_checksum_complement_offset')
    if complement_offset is None:
        if verbose:
            print("  No flash_checksum_complement_offset in ECU config — skipping")
        return

    if complement_offset >= len(firmware_data):
        raise ValueError(
            f"Checksum complement offset 0x{complement_offset:06X} exceeds "
            f"firmware size 0x{len(firmware_data):06X}"
        )

    # The original firmware + bootloader sums to 0 mod 256. We must keep
    # sum(patched_firmware) == sum(original_firmware) so the invariant holds.
    target_sum = sum(original_firmware) & 0xFF

    # Zero out the complement byte, sum everything else, then set it
    # to the value that brings the total to target_sum mod 256.
    old_value = firmware_data[complement_offset]
    firmware_data[complement_offset] = 0
    byte_sum = sum(firmware_data) & 0xFF
    new_value = (target_sum - byte_sum) & 0xFF
    firmware_data[complement_offset] = new_value

    if verbose:
        abs_addr = ecu_config['firmware_base'] + complement_offset
        print(f"  FLASH_CHECKSUM_COMPLEMENT @ 0x{abs_addr:08X} "
              f"(offset 0x{complement_offset:06X}): "
              f"0x{old_value:02X} -> 0x{new_value:02X}")


def parse_byte_patches(patch_string: str) -> dict[int, int]:
    """
    Parse byte patch string into dictionary.

    Format: "addr1:value1,addr2:value2,..."
    Example: "0x1000:0xAB,0x2000:0xCD"

    Args:
        patch_string: Comma-separated list of address:value pairs

    Returns:
        Dictionary mapping addresses to values
    """
    patches = {}

    if not patch_string:
        return patches

    try:
        for patch in patch_string.split(','):
            addr_str, value_str = patch.strip().split(':')
            addr = int(addr_str, 0)  # Auto-detect hex/decimal
            value = int(value_str, 0) & 0xFF  # Ensure single byte
            patches[addr] = value
    except ValueError as e:
        raise ValueError(f"Invalid byte patch format: {e}") from e

    return patches

def parse_partial_region(region_str: str, ecu_config: dict) -> tuple[int, int]:
    """
    Parse a --partial-region argument into (offset, size).

    Accepts either a named region from the ECU's flash_regions dict (e.g. "calibration")
    or an explicit "offset:size" pair (e.g. "0x10000:0x10000").

    Returns:
        Tuple of (region_offset, region_size) as integers.
    """
    flash_regions = ecu_config.get('flash_regions', {})

    # Try named region first
    if region_str in flash_regions:
        region = flash_regions[region_str]
        return region['offset'], region['size']

    # Try explicit offset:size
    if ':' in region_str:
        try:
            offset_str, size_str = region_str.split(':', 1)
            return int(offset_str, 0), int(size_str, 0)
        except ValueError:
            pass

    known = ', '.join(sorted(flash_regions.keys())) if flash_regions else '(none)'
    raise ValueError(
        f"Invalid --partial-region: '{region_str}'\n"
        f"Use a named region ({known}) or explicit offset:size (e.g. 0x10000:0x10000)"
    )


def validate_sector_alignment(offset: int, size: int, ecu_config: dict, verbose: bool = False):
    """
    Validate that both start and end offsets align to sector boundaries.

    The bootloader's flash_lookup_sector_by_address rejects non-aligned addresses
    with NRC 0x31 (requestOutOfRange). This pre-validates before generating the RWD.
    """
    boundaries = set(ecu_config.get('sector_boundaries', []))
    if not boundaries:
        raise ValueError("ECU config has no sector_boundaries — cannot validate alignment")

    end_offset = offset + size
    errors = []

    if offset not in boundaries:
        # Find nearest boundaries for helpful error message
        below = max((b for b in boundaries if b <= offset), default=None)
        above = min((b for b in boundaries if b >= offset), default=None)
        errors.append(
            f"Start offset 0x{offset:06X} is not a sector boundary. "
            f"Nearest: 0x{below:06X} (below), 0x{above:06X} (above)"
        )

    if end_offset not in boundaries:
        below = max((b for b in boundaries if b <= end_offset), default=None)
        above = min((b for b in boundaries if b >= end_offset), default=None)
        errors.append(
            f"End offset 0x{end_offset:06X} is not a sector boundary. "
            f"Nearest: 0x{below:06X} (below), 0x{above:06X} (above)"
        )

    if errors:
        raise ValueError(
            "Partial region does not align to flash sector boundaries:\n  " +
            "\n  ".join(errors)
        )

    if verbose:
        # Count sectors in range
        sectors_in_range = sorted(b for b in boundaries if offset <= b < end_offset)
        print(f"Sector alignment validated: 0x{offset:06X}–0x{end_offset:06X} "
              f"({len(sectors_in_range)} sectors, {size // 1024}K)")


def extract_partial_firmware(firmware_data: bytes, region_offset: int, region_size: int,
                             ecu_config: dict, verbose: bool = False) -> tuple[bytes, int]:
    """
    Extract a sector-aligned partial region from decrypted firmware.

    Args:
        firmware_data: Full decrypted firmware image
        region_offset: Start offset within firmware (must be sector-aligned)
        region_size: Size of region to extract (end must be sector-aligned)
        ecu_config: ECU config with sector_boundaries
        verbose: Enable verbose output

    Returns:
        Tuple of (partial_firmware_bytes, absolute_start_address)
    """
    firmware_base = ecu_config['firmware_base']

    # Validate region fits within firmware
    if region_offset + region_size > len(firmware_data):
        raise ValueError(
            f"Partial region 0x{region_offset:06X}+0x{region_size:06X} exceeds "
            f"firmware size 0x{len(firmware_data):06X}"
        )

    # Validate sector alignment
    validate_sector_alignment(region_offset, region_size, ecu_config, verbose)

    # Extract the region
    partial_fw = firmware_data[region_offset:region_offset + region_size]
    abs_start = firmware_base + region_offset

    if verbose:
        print(f"Extracted partial firmware:")
        print(f"  Region: 0x{region_offset:06X} – 0x{region_offset + region_size:06X} "
              f"({region_size:,} bytes)")
        print(f"  Absolute flash address: 0x{abs_start:08X} – 0x{abs_start + region_size:08X}")

    return partial_fw, abs_start


def compute_minimal_partial_region(original_fw: bytes, patched_fw: bytes,
                                    ecu_config: dict, verbose: bool = False) -> tuple[int, int]:
    """
    Compare original and patched firmware to find the minimal sector-aligned
    region that covers all modified bytes.

    Scans for byte-level differences, then expands the range to include any
    known CVN storage locations (since the CVN will also change when firmware
    is modified). The result is snapped outward to flash sector boundaries.

    Args:
        original_fw: Original (unpatched) firmware data
        patched_fw: Firmware data after patches have been applied
        ecu_config: ECU config with sector_boundaries
        verbose: Enable verbose output

    Returns:
        Tuple of (region_offset, region_size), sector-aligned.

    Raises:
        ValueError: If no bytes differ or sector boundaries are missing.
    """
    if len(original_fw) != len(patched_fw):
        raise ValueError(
            f"Firmware size mismatch: original={len(original_fw)}, patched={len(patched_fw)}"
        )

    # Scan for first/last modified byte and total count
    first_modified = None
    last_modified = None
    diff_count = 0
    for i in range(len(original_fw)):
        if original_fw[i] != patched_fw[i]:
            if first_modified is None:
                first_modified = i
            last_modified = i
            diff_count += 1

    if first_modified is None:
        raise ValueError(
            "No bytes differ between original and patched firmware — "
            "nothing to generate a partial RWD for"
        )

    if verbose:
        fw_base = ecu_config['firmware_base']
        print(f"\nAuto-partial: found {diff_count} modified byte(s)")
        print(f"  First modified: 0x{first_modified:06X} (abs 0x{fw_base + first_modified:08X})")
        print(f"  Last modified:  0x{last_modified:06X} (abs 0x{fw_base + last_modified:08X})")

    # Snap outward to sector boundaries
    boundaries = sorted(ecu_config.get('sector_boundaries', []))
    if not boundaries:
        raise ValueError("ECU config has no sector_boundaries — cannot compute partial region")

    # Find the sector boundary at or before first_modified
    region_start = boundaries[0]
    for b in boundaries:
        if b <= first_modified:
            region_start = b
        else:
            break

    # Find the sector boundary strictly after last_modified
    region_end = boundaries[-1]
    for b in boundaries:
        if b > last_modified:
            region_end = b
            break

    region_size = region_end - region_start

    if verbose:
        sectors_in_range = [b for b in boundaries if region_start <= b < region_end]
        print(f"  Sector-aligned region: 0x{region_start:06X}–0x{region_end:06X} "
              f"({region_size // 1024}K, {len(sectors_in_range)} sector(s))")

    # Validate (should always pass since we derived from sector_boundaries)
    validate_sector_alignment(region_start, region_size, ecu_config, verbose=False)

    return region_start, region_size


def main():
    """
    Main function to handle command line arguments and coordinate the patching process.
    """
    parser = argparse.ArgumentParser(
        description="Honda RWD Firmware Patcher - Modify RWD files with automatic CVN recalculation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic patch with default modifications
  python honda_rwd_patcher.py firmware.rwd --output patched.rwd

  # Patch compressed file with speed limit modification
  python honda_rwd_patcher.py firmware.rwd.gz --patch-speed-limit 25.0

  # Apply custom byte patches
  python honda_rwd_patcher.py firmware.rwd --patch-bytes 0x1000:0xAB,0x2000:0xCD

  # Verbose mode for debugging
  python honda_rwd_patcher.py firmware.rwd --verbose --output debug_patched.rwd

  # Extract and examine firmware without patching
  python honda_rwd_patcher.py firmware.rwd.gz --extract-only --output extracted.bin

  # Auto-calculate minimal partial RWD (only flash the sectors that changed)
  python honda_rwd_patcher.py firmware.rwd --partial --patch-speed-limit 25.0

  # Generate partial RWD that flashes only calibration sectors
  python honda_rwd_patcher.py firmware.rwd --partial-region calibration --patch-speed-limit 25.0

  # Partial RWD with explicit sector range (offset:size)
  python honda_rwd_patcher.py firmware.rwd --partial-region 0x10000:0x10000 --patch-speed-limit 25.0

  # List available named flash regions for an ECU
  python honda_rwd_patcher.py firmware.rwd --list-regions
        """
    )

    parser.add_argument('input', nargs='?', default=None,
                       help='Input RWD file (.rwd or .rwd.gz)')
    parser.add_argument('--output', '-o', help='Output file path (auto-detects compression)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output with detailed steps')

    # Patch options
    patch_group = parser.add_argument_group('Patch Options')
    patch_group.add_argument('--patch-speed-limit', type=float, metavar='KMH',
                           help='Set speed limit in km/h (example patch)')
    patch_group.add_argument('--patch-bytes', metavar='ADDR:VAL,...',
                           help='Apply byte patches (format: 0x1000:0xAB,0x2000:0xCD)')
    patch_group.add_argument('--patch-pattern', metavar='OLD:NEW', action='append',
                           help='Replace hex patterns (format: DEADBEEF:CAFEBABE)')

    # Partial RWD options
    partial_group = parser.add_argument_group('Partial Flash Options')
    partial_exclusive = partial_group.add_mutually_exclusive_group()
    partial_exclusive.add_argument('--partial', action='store_true',
                              help='Auto-calculate the minimal partial flash region. '
                                   'Diffs patched vs original firmware to find modified bytes, '
                                   'includes CVN storage (if known), and snaps to sector boundaries.')
    partial_exclusive.add_argument('--partial-region', metavar='REGION',
                              help='Generate RWD for a specific flash subset. '
                                   'Use a named region (e.g. "calibration") or '
                                   'explicit offset:size (e.g. "0x10000:0x10000"). '
                                   'Addresses must align to sector boundaries.')
    partial_group.add_argument('--list-regions', action='store_true',
                              help='List named flash regions for the detected ECU and exit')

    # Operation modes
    mode_group = parser.add_argument_group('Operation Modes')
    mode_group.add_argument('--extract-only', action='store_true',
                          help='Extract firmware without patching')
    mode_group.add_argument('--verify-only', action='store_true',
                          help='Verify RWD file structure without modification')
    mode_group.add_argument('--search-value', default='',
                          help='Search value for encryption decoder (default: auto-detect)')
    mode_group.add_argument('--ecu-id', default='',
                          help='ECU software ID override (default: auto-detect from header 3)')
    mode_group.add_argument('--list-ecus', action='store_true',
                          help='List all supported ECU firmware IDs and exit')

    args = parser.parse_args()

    # Handle --list-ecus before anything else
    if args.list_ecus:
        print("Supported ECU firmware IDs:")
        for ecu_id, cfg in sorted(ECU_FIRMWARE_DB.items()):
            print(f"  {ecu_id}  — {cfg['description']}")
            for p in cfg.get('speed_limit_patches', []):
                print(f"    {p['name']} @ 0x{p['offset']:06X} = 0x{p['expected']:04X}" +
                      f" ({p['expected'] / cfg['speed_scale']:.1f} km/h)")
            regions = cfg.get('flash_regions', {})
            if regions:
                print(f"    Flash regions: {', '.join(sorted(regions.keys()))}")
        return 0

    # Handle --list-regions (needs ECU identification)
    if args.list_regions:
        ecu_id_arg = args.ecu_id
        if not ecu_id_arg:
            # Try to auto-detect from the input file if provided
            if hasattr(args, 'input') and args.input:
                try:
                    rwd_data, _ = read_rwd_file(args.input, False)
                    rwd_obj = x5a(data=rwd_data)
                    ecu_id_arg = get_ecu_id_from_rwd(rwd_obj, False)
                except Exception:
                    pass
            if not ecu_id_arg:
                print("Error: Cannot detect ECU. Use --ecu-id or provide an input RWD file.")
                return 1

        cfg = ECU_FIRMWARE_DB.get(ecu_id_arg)
        if not cfg:
            print(f"Error: Unknown ECU '{ecu_id_arg}'. Use --list-ecus to see supported IDs.")
            return 1

        regions = cfg.get('flash_regions', {})
        boundaries = cfg.get('sector_boundaries', [])
        print(f"Flash regions for {ecu_id_arg} ({cfg['description']}):")
        print(f"  Firmware base: 0x{cfg['firmware_base']:08X}")
        print(f"  Total flash: {cfg['expected_firmware_size'] // 1024}K")
        print(f"  Sector boundaries: {len(boundaries)} entries")
        print()
        for name, region in sorted(regions.items(), key=lambda x: x[1]['offset']):
            offset, size = region['offset'], region['size']
            abs_start = cfg['firmware_base'] + offset
            abs_end = abs_start + size
            print(f"  {name:15s}  offset=0x{offset:06X}  size=0x{size:06X} ({size // 1024:>5d}K)  "
                  f"abs=0x{abs_start:08X}–0x{abs_end:08X}")
        return 0

    try:
        # Require input file for all operations beyond list commands
        if args.input is None:
            parser.error("the following arguments are required: input")

        # Read input RWD file
        if args.verbose:
            print("=" * 60)
            print("Honda RWD Firmware Patcher")
            print("=" * 60)

        rwd_data, was_compressed = read_rwd_file(args.input, args.verbose)

        # Parse RWD file with enhanced x5a class
        if args.verbose:
            print("\nParsing RWD file structure...")

        rwd_obj = x5a(data=rwd_data)

        if args.verbose:
            print("RWD file parsed successfully")
            if rwd_obj.file_headers:
                print(f"Headers: {len(rwd_obj.file_headers)}")
            if rwd_obj.firmware_blocks:
                print(f"Firmware blocks: {len(rwd_obj.firmware_blocks)}")
            if rwd_obj.keys:
                print(f"Encryption keys: {len(rwd_obj.keys)} bytes")

            # Display header information
            if rwd_obj.file_headers:
                for i, header in enumerate(rwd_obj.file_headers):
                    if hasattr(header, 'values') and header.values:
                        print(f"Header {i}: {len(header.values)} values")
                        for j, value in enumerate(header.values):
                            if hasattr(value, 'value') and value.value and len(value.value) <= 16:  # Only show short values
                                val_hex = value.value.hex().upper() if isinstance(value.value, bytes) else str(value.value)
                                print(f"  Value {j}: {val_hex}")

        # Identify the ECU firmware
        ecu_id = args.ecu_id or get_ecu_id_from_rwd(rwd_obj, args.verbose)
        ecu_config = None
        if ecu_id:
            ecu_config = ECU_FIRMWARE_DB.get(ecu_id)
            if ecu_config and args.verbose:
                print(f"Matched firmware profile: {ecu_id} — {ecu_config['description']}")
            elif not ecu_config and args.verbose:
                print(f"Warning: ECU {ecu_id} not in firmware database (raw patches still work)")

        # Verify-only mode
        if args.verify_only:
            print("\nRWD file verification completed successfully")
            return 0

        # Get firmware info for debugging
        if args.verbose:
            print("\nRWD file information:")
            firmware_info = rwd_obj.get_firmware_info()
            for key, value in firmware_info.items():
                print(f"  {key}: {value}")

        # Find working decoder and decrypt firmware
        search_value = args.search_value
        if not search_value:
            if args.verbose:
                print("\nAttempting auto-crack with header 3 values...")
            # Only use header 3 values for cracking
            firmware_candidates = rwd_obj.auto_crack_with_header_3()
            if firmware_candidates:
                # Get the search value that worked
                header_3_values = rwd_obj.get_header_3_values()
                search_value = header_3_values[0] if header_3_values else ""
                if args.verbose:
                    print(f"Successfully cracked with header 3 value: '{search_value}'")
            else:
                print("Error: Could not crack encryption with header 3 values.")
                print("You must specify --search-value with a valid header 3 value.")
                return 1
        else:
            # Use provided search value
            if args.verbose:
                print(f"Using provided search value: '{search_value}'")
            firmware_candidates = rwd_obj.crack(search_value)
            if not firmware_candidates:
                print(f"Error: Could not crack encryption with search value: '{search_value}'")
                return 1

        # Get decrypted firmware
        decrypted_firmware, _ = rwd_obj.decrypt(rwd_obj.decoder)

        if args.verbose:
            print(f"Decrypted firmware size: {len(decrypted_firmware):,} bytes")

        # Save unmodified full firmware (used by --partial for diffing)
        original_full_firmware = decrypted_firmware

        # Assert input RWD is a full firmware image.
        # CVN is computed over the entire flash (0xA0010000–0xA0400000), so even
        # when producing a partial output RWD we need the full image as input.
        if ecu_config:
            rwd_start = rwd_obj.firmware_blocks[0]['start']
            rwd_length = rwd_obj.firmware_blocks[0]['length']
            expected_base = ecu_config['firmware_base']
            expected_size = ecu_config['expected_firmware_size']

            if rwd_start != expected_base:
                raise ValueError(
                    f"Input RWD start address 0x{rwd_start:08X} does not match "
                    f"expected firmware base 0x{expected_base:08X} for {ecu_id}.\n"
                    f"The patcher requires a full firmware image as input."
                )
            if rwd_length != expected_size:
                raise ValueError(
                    f"Input RWD size 0x{rwd_length:X} ({rwd_length:,} bytes) does not match "
                    f"expected 0x{expected_size:X} ({expected_size:,} bytes) for {ecu_id}.\n"
                    f"The patcher requires a full firmware image as input."
                )

        # Extract-only mode
        if args.extract_only:
            output_path = args.output or args.input.replace('.rwd', '_extracted.bin').replace('.gz', '')
            with open(output_path, 'wb') as f:
                f.write(decrypted_firmware)
            print(f"Extracted firmware saved to: {output_path}")
            return 0

        # ── Partial region handling ──────────────────────────────
        # If --partial-region is specified, we slice the decrypted firmware
        # to just the target region BEFORE patching. Patches are applied to
        # the partial slice, and offsets are translated accordingly.
        partial_mode = False
        region_offset = 0
        region_size = len(decrypted_firmware)

        if args.partial_region:
            if ecu_config is None:
                raise ValueError(
                    "--partial-region requires a known ECU profile.\n"
                    "Use --ecu-id or ensure the RWD header matches a known ECU."
                )
            partial_mode = True
            region_offset, region_size = parse_partial_region(
                args.partial_region, ecu_config)

            # Reject if this ECU has a flash checksum complement — the boot
            # checksum sums every byte in flash, so we can't compute the
            # correct complement from a partial slice alone.
            if ecu_config.get('flash_checksum_complement_offset') is not None:
                raise ValueError(
                    "--partial-region cannot update the flash checksum complement\n"
                    "(the boot checksum covers all of flash, not just this region).\n"
                    "Use --partial instead, which auto-includes the complement's sector."
                )

            if args.verbose:
                print(f"\nPartial mode: extracting region '{args.partial_region}'")

            # Keep the full firmware for CVN calculation, extract the partial slice
            full_firmware = decrypted_firmware
            partial_fw, abs_start = extract_partial_firmware(
                decrypted_firmware, region_offset, region_size,
                ecu_config, args.verbose)

            # The partial slice is what we'll patch and embed in the RWD
            decrypted_firmware = partial_fw

        # ── Prepare patch configuration ──────────────────────────
        patch_config = {}
        patches_to_apply = False

        if args.patch_speed_limit is not None:
            if ecu_config is None:
                raise ValueError(
                    f"ECU '{ecu_id or '(unknown)'}' is not in the firmware database.\n" +
                    "--patch-speed-limit requires a known ECU profile.\n" +
                    "Use --list-ecus to see supported firmware IDs, or add this ECU to ECU_FIRMWARE_DB."
                )
            patch_config['speed_limit_kmh'] = args.patch_speed_limit
            patches_to_apply = True

        if args.patch_bytes:
            patch_config['byte_patches'] = parse_byte_patches(args.patch_bytes)
            patches_to_apply = True

        if args.patch_pattern:
            pattern_replacements = {}
            for pattern_pair in args.patch_pattern:
                try:
                    old_pattern, new_pattern = pattern_pair.split(':')
                    pattern_replacements[old_pattern] = new_pattern
                except ValueError:
                    print(f"Warning: Invalid pattern format: {pattern_pair}")
            if pattern_replacements:
                patch_config['pattern_replacements'] = pattern_replacements
                patches_to_apply = True

        # In partial mode, translate patch offsets from full-image to region-relative
        if partial_mode and patches_to_apply:
            if 'speed_limit_kmh' in patch_config and ecu_config:
                # Validate that speed limit patch offsets fall within the partial region
                for patch in ecu_config['speed_limit_patches']:
                    if not (region_offset <= patch['offset'] < region_offset + region_size):
                        raise ValueError(
                            f"Patch {patch['name']} at offset 0x{patch['offset']:06X} falls outside "
                            f"partial region 0x{region_offset:06X}–0x{region_offset + region_size:06X}.\n"
                            f"Choose a region that includes the patch target, or omit --partial-region."
                        )
            if 'byte_patches' in patch_config:
                # Translate absolute offsets to region-relative
                translated = {}
                for addr, value in patch_config['byte_patches'].items():
                    if not (region_offset <= addr < region_offset + region_size):
                        raise ValueError(
                            f"Byte patch at 0x{addr:06X} falls outside "
                            f"partial region 0x{region_offset:06X}–0x{region_offset + region_size:06X}"
                        )
                    translated[addr - region_offset] = value
                patch_config['byte_patches'] = translated

        # Apply firmware modifications
        firmware_modified = False
        if patches_to_apply:
            firmware_data = bytearray(decrypted_firmware)
            # In partial mode, create a temporary ecu_config with adjusted offsets
            patch_ecu_config = ecu_config
            if partial_mode and ecu_config:
                patch_ecu_config = dict(ecu_config)
                patch_ecu_config['speed_limit_patches'] = [
                    dict(p, offset=p['offset'] - region_offset)
                    for p in ecu_config['speed_limit_patches']
                ]
            firmware_modified = apply_firmware_patches(
                firmware_data, patch_config, ecu_config=patch_ecu_config, verbose=args.verbose)
            decrypted_firmware = bytes(firmware_data)

        # ── Update flash checksum complement ─────────────────────
        # The boot checksum sums every byte in flash; low byte must be 0x00.
        # After patching, adjust the complement byte so the total byte sum
        # stays ≡ 0 (mod 256). Must happen BEFORE auto-partial diffing so
        # the complement byte's sector is included in the minimal region.
        if firmware_modified and ecu_config and 'flash_checksum_complement_offset' in ecu_config:
            if args.verbose:
                print("\nUpdating flash checksum complement...")
            update_flash_checksum_complement(firmware_data, ecu_config, original_full_firmware, args.verbose)
            decrypted_firmware = bytes(firmware_data)

            # Sanity check: patched firmware must preserve the byte-sum invariant.
            original_byte_sum = sum(original_full_firmware) & 0xFF
            patched_byte_sum = sum(firmware_data) & 0xFF
            assert patched_byte_sum == original_byte_sum, (
                f"Flash byte-sum invariant violated: "
                f"original=0x{original_byte_sum:02X}, patched=0x{patched_byte_sum:02X}"
            )

        # ── Auto-partial: compute minimal region from diffs ──────
        # When --partial is used, patches were applied to the full firmware
        # above. Now diff against the original to find the minimal
        # sector-aligned region that covers all modified bytes.
        if args.partial:
            if not patches_to_apply:
                raise ValueError(
                    "--partial requires at least one patch option.\n"
                    "Use --patch-speed-limit, --patch-bytes, or --patch-pattern."
                )
            if not firmware_modified:
                raise ValueError(
                    "--partial specified but patches did not modify any bytes.\n"
                    "The patched values may already match the target values."
                )
            if ecu_config is None:
                raise ValueError(
                    "--partial requires a known ECU profile.\n"
                    "Use --ecu-id or ensure the RWD header matches a known ECU."
                )

            full_patched = decrypted_firmware
            region_offset, region_size = compute_minimal_partial_region(
                original_full_firmware, full_patched, ecu_config, args.verbose)

            partial_mode = True
            abs_start = ecu_config['firmware_base'] + region_offset
            # full_firmware is used by the CVN path to reconstitute
            # the full image; here it's already the full patched image
            full_firmware = full_patched
            decrypted_firmware = full_patched[region_offset:region_offset + region_size]

            if args.verbose:
                print(f"  Partial slice: {len(decrypted_firmware):,} bytes "
                      f"(0x{abs_start:08X}–0x{abs_start + region_size:08X})")
                full_size = len(full_patched)
                saving = (1 - region_size / full_size) * 100
                print(f"  Flash reduction: {full_size // 1024}K -> {region_size // 1024}K "
                      f"({saving:.0f}% less to flash)")

        # ── CVN calculation ──────────────────────────────────────
        # The ECU always computes CVN over the entire flash minus bootloader
        # (0xA0010000–0xA0400000) on every boot — there is no partial CVN.
        # So even for partial RWDs, we must compute CVN over the full
        # firmware data with patches applied.
        cvn_data = None
        if firmware_modified:
            if args.verbose:
                print("\nRecalculating CVN for modified firmware...")
            if partial_mode:
                # Reconstitute full firmware with the patched partial region overlaid
                full_for_cvn = bytearray(full_firmware)
                full_for_cvn[region_offset:region_offset + region_size] = decrypted_firmware
                if args.verbose:
                    fw_base = ecu_config['firmware_base']
                    print(f"  CVN computed over full firmware ({len(full_for_cvn):,} bytes, "
                          f"0x{fw_base:08X}–0x{fw_base + len(full_for_cvn):08X})")
                cvn_data = calculate_honda_cvn(bytes(full_for_cvn), ecu_config=ecu_config, verbose=args.verbose)
            else:
                cvn_data = calculate_honda_cvn(decrypted_firmware, ecu_config=ecu_config, verbose=args.verbose)

        # ── Generate output RWD ──────────────────────────────────
        if partial_mode:
            # Update block metadata so the RWD carries the partial start
            # address and size. The flash tool will send RoutineControl
            # 0xFF00 with these values, triggering a range erase.
            rwd_obj.firmware_blocks[0]['start'] = abs_start
            rwd_obj.firmware_blocks[0]['length'] = len(decrypted_firmware)

            if args.verbose:
                orig_start = ecu_config['firmware_base']
                orig_size = ecu_config['expected_firmware_size']
                print(f"\nGenerating partial RWD:")
                print(f"  Original block: 0x{orig_start:08X}, {orig_size:,} bytes")
                print(f"  Partial block:  0x{abs_start:08X}, {len(decrypted_firmware):,} bytes")
                print(f"  CVN: {' '.join(f'{b:02X}' for b in cvn_data) if cvn_data else '(unchanged)'}")

            rwd_obj.set_unencrypted_firmware(decrypted_firmware)
            output_data = rwd_obj.generate(cvn_data)

        elif firmware_modified:
            if args.verbose:
                print("\nGenerating modified RWD...")

            rwd_obj.set_unencrypted_firmware(decrypted_firmware)
            output_data = rwd_obj.generate(cvn_data)
        else:
            # No modifications - just regenerate with original firmware
            if args.verbose:
                print("\nNo modifications applied, regenerating original RWD file...")

            rwd_obj.set_unencrypted_firmware(decrypted_firmware)
            output_data = rwd_obj.generate(cvn_data)

        # ── Determine output path ────────────────────────────────
        if args.output:
            output_path = args.output
        else:
            input_path = Path(args.input)
            suffix = '_partial' if partial_mode else '_modified'
            if was_compressed:
                output_path = str(input_path).replace('.rwd.gz', f'{suffix}.rwd.gz')
            else:
                output_path = str(input_path).replace('.rwd', f'{suffix}.rwd')

        # Write output file
        final_output_path = write_rwd_file(output_path, output_data, was_compressed, args.verbose)

        print(f"\nOutput RWD file saved to: {final_output_path}")

        if partial_mode:
            print(f"Partial flash region: 0x{abs_start:08X} – 0x{abs_start + region_size:08X} "
                  f"({region_size // 1024}K)")
            if firmware_modified:
                print("Firmware modifications applied and CVN recalculated")
        elif firmware_modified and args.verbose:
            print("Firmware modifications applied and CVN recalculated")

        return 0

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
