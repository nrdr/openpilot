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

def calculate_honda_cvn(firmware_data: bytes, verbose: bool = False) -> bytes:
    """
    Calculate Honda ECU Calibration Verification Number from firmware data.

    Args:
        firmware_data: Raw firmware binary data
        verbose: Enable verbose output

    Returns:
        4-byte CVN value
    """
    if verbose:
        print("Calculating CVN for modified firmware...")

    # Initialize checksums (16-bit values)
    additive_checksum = 0
    xor_checksum = 0

    # Firmware scanning parameters
    BLOCK_SIZE = 0x3F000  # 258,048 bytes per block
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

def apply_firmware_patches(firmware_data: bytearray, patch_config: dict, verbose: bool = False) -> bool:
    """
    Apply patches to firmware data based on configuration.

    Args:
        firmware_data: Firmware data to modify (mutable)
        patch_config: Dictionary containing patch configuration
        verbose: Enable verbose output

    Returns:
        True if any patches were applied, False otherwise
    """
    patches_applied = False

    if verbose:
        print("Applying firmware patches...")

    # Example: Speed limit patch
    if 'speed_limit_kmh' in patch_config:
        speed_limit = patch_config['speed_limit_kmh']
        if verbose:
            print(f"Applying speed limit patch: {speed_limit} km/h")

        # Example addresses for speed limits (these would need to be determined
        # for specific firmware versions through reverse engineering)
        speed_addresses = [0x1B1C0, 0x1B1C2]  # Example offsets

        for addr in speed_addresses:
            if addr < len(firmware_data) - 1:
                # Convert km/h to raw value (typically * 100 for Honda)
                raw_value = int(speed_limit * 100)
                if raw_value <= 0xFFFF:
                    old_value = struct.unpack('<H', firmware_data[addr:addr+2])[0]
                    firmware_data[addr:addr+2] = struct.pack('<H', raw_value)
                    if verbose:
                        print(f"  Address 0x{addr:06X}: {old_value/100:.1f} -> {speed_limit:.1f} km/h")
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

            if verbose and count > 0:
                print(f"  Replaced pattern {old_pattern} -> {new_pattern} ({count} occurrences)")
                patches_applied = True

    if verbose:
        if patches_applied:
            print("Firmware patches applied successfully")
        else:
            print("No patches were applied")

    return patches_applied

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
        """
    )

    parser.add_argument('input', help='Input RWD file (.rwd or .rwd.gz)')
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

    # Operation modes
    mode_group = parser.add_argument_group('Operation Modes')
    mode_group.add_argument('--extract-only', action='store_true',
                          help='Extract firmware without patching')
    mode_group.add_argument('--verify-only', action='store_true',
                          help='Verify RWD file structure without modification')
    mode_group.add_argument('--search-value', default='',
                          help='Search value for encryption decoder (default: auto-detect)')

    args = parser.parse_args()

    try:
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

        # Extract-only mode
        if args.extract_only:
            output_path = args.output or args.input.replace('.rwd', '_extracted.bin').replace('.gz', '')
            with open(output_path, 'wb') as f:
                f.write(decrypted_firmware)
            print(f"Extracted firmware saved to: {output_path}")
            return 0

        # Prepare patch configuration
        patch_config = {}
        patches_to_apply = False

        if args.patch_speed_limit:
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

        # Apply firmware modifications
        firmware_modified = False
        if patches_to_apply:
            firmware_data = bytearray(decrypted_firmware)
            firmware_modified = apply_firmware_patches(firmware_data, patch_config, args.verbose)
            decrypted_firmware = bytes(firmware_data)

        # Calculate CVN for modified firmware
        cvn_data = None
        if firmware_modified:
            if args.verbose:
                print("\nRecalculating CVN for modified firmware...")
            cvn_data = calculate_honda_cvn(decrypted_firmware, args.verbose)

        # Use the new firmware update workflow if we have modifications
        if firmware_modified:
            if args.verbose:
                print("\nUsing enhanced firmware update workflow...")

            # Validate firmware before applying
            validation = rwd_obj.validate_firmware_update(decrypted_firmware)
            if args.verbose:
                print("Firmware validation:")
                print(f"  Valid: {validation['valid']}")
                for warning in validation['warnings']:
                    print(f"  Warning: {warning}")
                for error in validation['errors']:
                    print(f"  Error: {error}")

            if not validation['valid']:
                print("Firmware validation failed, aborting")
                return 1

            # Use the complete firmware update workflow
            output_data = rwd_obj.update_firmware_workflow(
                patched_firmware_data=decrypted_firmware,
                search_value=search_value,
                metadata_updates=None,  # Could add metadata updates here
                cvn_data=cvn_data
            )
        else:
            # No modifications - just regenerate with original firmware
            if args.verbose:
                print("\nNo modifications applied, regenerating original RWD file...")

            rwd_obj.set_unencrypted_firmware(decrypted_firmware)
            output_data = rwd_obj.generate(cvn_data)

        # Determine output path
        if args.output:
            output_path = args.output
        else:
            input_path = Path(args.input)
            if was_compressed:
                output_path = str(input_path).replace('.rwd.gz', '_modified.rwd.gz')
            else:
                output_path = str(input_path).replace('.rwd', '_modified.rwd')

        # Write output file
        final_output_path = write_rwd_file(output_path, output_data, was_compressed, args.verbose)

        print(f"\nOutput RWD file saved to: {final_output_path}")

        if firmware_modified and args.verbose:
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
