#!/usr/bin/env python3
# Usage: python3 check_rwd.py <file.rwd> [file2.rwd ...]

import struct
import sys

DECRYPT_LOOKUP = {144: 72, 218: 55, 255: 255, 164: 1, 195: 26, 99: 2, 28: 178, 205: 158, 125: 138, 45: 118, 222: 98, 142: 78, 62: 58, 243: 38, 163: 18, 83: 254, 3: 234, 172: 214, 92: 194, 12: 174, 189: 154, 109: 134, 29: 114, 206: 94, 126: 74, 46: 54, 227: 34, 147: 14, 113: 0, 67: 250, 236: 230, 156: 210, 76: 190, 252: 170, 173: 150, 93: 130, 13: 110, 148: 253, 120: 159, 199: 148, 198: 137, 77: 126, 23: 104, 73: 83, 203: 73, 78: 62, 123: 53, 254: 42, 43: 33, 90: 23, 161: 12, 10: 3, 132: 249, 191: 239, 226: 220, 197: 201, 248: 191, 117: 181, 34: 172, 37: 161, 88: 151, 141: 142, 8: 131, 134: 121, 185: 111, 54: 101, 190: 90, 57: 79, 128: 68, 139: 57, 14: 46, 138: 35, 131: 10, 100: 241, 1: 228, 146: 200, 133: 185, 168: 171, 104: 155, 40: 139, 251: 85, 94: 66, 91: 45, 103: 124, 55: 112, 231: 156, 80: 56, 224: 92, 102: 113, 96: 60, 98: 188, 97: 252, 140: 206, 122: 31, 232: 187, 16: 40, 202: 51, 26: 7, 239: 251, 5: 153, 219: 77, 119: 128, 21: 157, 238: 102, 180: 5, 217: 119, 30: 50, 7: 100, 32: 44, 183: 144, 50: 176, 110: 70, 157: 146, 2: 164, 44: 182, 145: 8, 58: 15, 27: 29, 64: 52, 9: 67, 31: 199, 179: 22, 42: 11, 193: 20, 211: 30, 129: 4, 241: 32, 74: 19, 178: 208, 247: 160, 112: 64, 242: 224, 114: 192, 165: 193, 0: 36, 59: 37, 196: 9, 154: 39, 75: 41, 72: 147, 249: 127, 162: 204, 130: 196, 229: 209, 182: 133, 48: 48, 86: 109, 240: 96, 137: 99, 151: 136, 209: 24, 108: 198, 181: 197, 212: 13, 244: 21, 11: 25, 118: 117, 228: 17, 214: 141, 52: 229, 160: 76, 115: 6, 106: 27, 56: 143, 25: 71, 36: 225, 194: 212, 208: 88, 187: 69, 171: 65, 153: 103, 38: 97, 207: 243, 82: 184, 184: 175, 188: 218, 213: 205, 121: 95, 15: 195, 81: 248, 24: 135, 70: 105, 150: 125, 174: 86, 158: 82, 220: 226, 201: 115, 71: 116, 51: 246, 177: 16, 176: 80, 22: 93, 39: 108, 159: 231, 223: 247, 186: 47, 169: 107, 245: 213, 235: 81, 192: 84, 124: 202, 175: 235, 84: 237, 79: 211, 234: 59, 143: 227, 237: 166, 33: 236, 253: 106, 65: 244, 111: 219, 200: 179, 101: 177, 17: 232, 20: 221, 166: 129, 60: 186, 61: 122, 167: 140, 204: 222, 87: 120, 41: 75, 135: 132, 136: 163, 49: 240, 250: 63, 107: 49, 170: 43, 18: 168, 221: 162, 35: 242, 225: 28, 149: 189, 85: 173, 152: 167, 95: 215, 53: 165, 89: 87, 66: 180, 6: 89, 47: 203, 210: 216, 215: 152, 233: 123, 116: 245, 127: 223, 19: 238, 69: 169, 105: 91, 4: 217, 216: 183, 68: 233, 63: 207, 155: 61, 246: 149, 230: 145}

PILOT_APP_ID = b'39990-TG7-A060\x00\x00'
T6Z_APP_IDS = (
    b'39990-T6Z-A110\x00\x00',
    b'39990-TG7-A040\x00\x00',
    b'39990-TG7-A030\x00\x00',
    b'39990-TG7-A020\x00\x00',
)
T6Z_SECRETS = (b'\x00\x11\x00\x12\x10\x20',) * 4
T6Z_REFERENCE_NOTICE = "".join((
    "T6Z checksum validation is offline/catalog-only; the current ",
    "eps-update.py and guided flash.py do not support flashing this image.",
))
PILOT_KEYS = b'\x01\x02\x03'
PILOT_FLASH_START = 0x10000
PILOT_CHECKSUM_ENDS = (0xa000, 0x1d000, 0x4ff00)
T6Z_HEADER_PROFILE = (
    (b'\x00',),
    (),
    (b'0',),  # tester address byte 0x30 -> UDS address 0x18DA30F1
    T6Z_APP_IDS,
    T6Z_SECRETS,
    (PILOT_KEYS,),
)
T6Z_IDENTITY_OFFSET = 0x3438


# SH2A images end with a 16-bit word sum at length - 0x80 and a negative
# word sum at length - 2. V850 Pilot/T6Z images use the LE32 checks below.
SUM_TRAILER = 0x80
NEGATIVE_SUM_TRAILER = 2


def checksum_definitions(length):
    if length % 2 or length <= SUM_TRAILER:
        raise ValueError(f"firmware length 0x{length:x} is too short or odd for the checksum layout")
    return [(0, length - SUM_TRAILER, "sum"), (1, length - NEGATIVE_SUM_TRAILER, "negative-sum")]


# Odyssey THR-A020 and RDX TJB-A220 images also carry runtime ROM CRCs. While
# running, the EPS recomputes a CRC-32/BZIP2 over each region and compares it
# with the big-endian word at the slot; a stale word passes the two checksums
# above but faults the EPS a second or two after it starts steering. Both
# images put the app at flash 0xC000 with a 0x74000 block; regions and slots
# are (start, end, slot) flash addresses.
ROM_CRC_SOFTWARE_IDS = (b'39990-THR', b'39990-TJB')
ROM_CRC_START, ROM_CRC_LENGTH = 0xc000, 0x74000
ROM_CRC_REGIONS = ((0x40000, 0x4ff60, 0x4ff7c), (0x60000, 0x6ff60, 0x6ff7c))


# THR and TJB also keep a monitor copy of the LKAS calibration: monitors at 0x68000-0x6Bxxx re-run each stage
# from the shadow and fault the EPS when it disagrees with the primary. A primary edit with a stale shadow
# passes every checksum and CRC (once they are recomputed) and faults on the car. Fields are (label, primary
# row-0 address, THR shadow row-0 address, words); TJB's shadow sits 0x4D00 below THR's. Rows are 0x300
# apart; THR mirrors banks 1-7 (rows 0-6), TJB rows 0-4 (its rows 5-6 are erased in the primary only).
SHADOW_FIELDS = (
    ("speed_clamp_lo", 0x57b00, 0x67b00, 1), ("torque_fault_debounce", 0x57b16, 0x67b1a, 1),
    ("speed_limit_x", 0x57b2a, 0x67b2e, 9), ("speed_limit_y", 0x57b3c, 0x67b40, 9), ("tracker_2", 0x57b4e, 0x67b56, 2),
    ("override_fade_X1", 0x57b54, 0x67b5e, 8), ("override_fade_Y1", 0x57b64, 0x67b6e, 8),
    ("override_fade_X2", 0x57b74, 0x67b82, 8), ("override_fade_Y2", 0x57b84, 0x67b92, 8),
    ("command_input_clamp", 0x57bac, 0x67bc2, 1), ("target_map_x", 0x57bae, 0x67bc4, 9), ("target_map_y", 0x57bc0, 0x67bd6, 9),
    ("tracker_1", 0x57bd2, 0x67be8, 2), ("d_p_u_clamps", 0x57bd6, 0x67bec, 3),
    ("helper_E_x", 0x57bdc, 0x67bf2, 8), ("helper_E_y", 0x57bec, 0x67c02, 8), ("helper_F_x", 0x57bfc, 0x67c16, 8),
    ("helper_F_y", 0x57c0c, 0x67c26, 8), ("helper_G_x", 0x57c1c, 0x67c3a, 6), ("helper_G_y", 0x57c28, 0x67c46, 6),
    ("helper_H_x", 0x57c34, 0x67c56, 6), ("helper_H_y", 0x57c40, 0x67c62, 6),
    ("d_gain_x", 0x57c4c, 0x67c72, 9), ("d_gain_y", 0x57c5e, 0x67c84, 9), ("p_gain_x", 0x57c70, 0x67c9a, 9), ("p_gain_y", 0x57c82, 0x67cac, 9),
)
SHADOW_ROW = 0x300
SHADOW_FAMILIES = ((b'39990-THR', 0, 7), (b'39990-TJB', 0x4d00, 5))  # (software ID prefix, shadow offset below THR, rows)


def shadow_family(fw):
    ids = [value.value for value in fw.file_headers[3].values]
    return next(((offset, rows) for prefix, offset, rows in SHADOW_FAMILIES if any(i.startswith(prefix) for i in ids)), None)


def validate_shadows(decrypted, start, offset, rows):
    for row in range(rows):
        for label, primary, shadow, n in SHADOW_FIELDS:
            p, s = primary + SHADOW_ROW * row, shadow - offset + SHADOW_ROW * row
            if decrypted[p - start:p - start + 2 * n] != decrypted[s - start:s - start + 2 * n]:
                raise ValueError(f"monitor shadow stale: {label} row {row} at 0x{p:x} differs from its shadow at 0x{s:x}")
    print(f"  Monitor shadows ({len(SHADOW_FIELDS)} fields x {rows} rows): PASS")


def _crc32_bzip2_table():
    table = []
    for i in range(256):
        c = i << 24
        for _ in range(8):
            c = ((c << 1) ^ 0x04c11db7) & 0xffffffff if c & 0x80000000 else (c << 1) & 0xffffffff
        table.append(c)
    return table


CRC32_BZIP2_TABLE = _crc32_bzip2_table()


def crc32_bzip2(data):
    c = 0xffffffff
    for b in data:
        c = ((c << 8) & 0xffffffff) ^ CRC32_BZIP2_TABLE[((c >> 24) ^ b) & 0xff]
    return c ^ 0xffffffff


def rom_crc_definitions(fw):
    """ROM CRC regions to check for this image, empty when it carries none."""
    ids = [value.value for value in fw.file_headers[3].values]
    if not any(i.startswith(prefix) for i in ids for prefix in ROM_CRC_SOFTWARE_IDS):
        return []
    block = fw.firmware_blocks[0]
    if (block["start"], block["length"]) != (ROM_CRC_START, ROM_CRC_LENGTH):
        raise ValueError(f"THR/TJB image must start at 0x{ROM_CRC_START:x} with length 0x{ROM_CRC_LENGTH:x}, "
                         f"got 0x{block['start']:x}/0x{block['length']:x}")
    return ROM_CRC_REGIONS


# Ridgeline T6Z-A110 images are a different family: a V850 (Pilot codebase) app at flash 0x10000, length
# 0x50000, encrypted with the H5 keys as out = k0 + (k1 ^ (in - k2)) (boot FUN_0000e962). Honda pads each
# bank so its little-endian 32-bit word sum is 0, and the bootloader's FF01 validate checks that the running
# LE32 sum of everything programmed (0x0..0x4FF00, the last 0x36 block being 256 bytes) is still 0. Their
# header 3 lists the dash, comma and dash-comma IDs against two seed secrets, so the 3/4 counts differ.
T6Z_SOFTWARE_IDS = (b'39990-T6Z', b'39990,T6Z')
T6Z_START, T6Z_LENGTH = 0x10000, 0x50000
T6Z_SUM_WINDOWS = ((0x00000, 0x0a000), (0x0a000, 0x1d000), (0x1d000, 0x4ff00))
T6Z_VALIDATE_END = 0x4ff00
T6Z_FLASHER = ("T6Z-A110 (V850) images are programmed through its bootloader sequence (erase/validate "
               "routines FF00/FF01), which eps-update.py does not implement")


def is_t6z(fw):
    return any(v.value.startswith(T6Z_SOFTWARE_IDS) for v in fw.file_headers[3].values)


def t6z_decrypt(encrypted, keys):
    k0, k1, k2 = keys[0], keys[1], keys[2]
    return bytes((k0 + (k1 ^ ((b - k2) & 0xff))) & 0xff for b in encrypted)


def le32_sum(data, start, end):
    return sum(struct.unpack_from(f'<{(end - start) // 4}I', data, start)) & 0xffffffff


def validate_t6z_firmware(fw):
    # Preserve the exact legacy four-ID profile while also accepting the newer
    # three-ID/two-seed format validated by the donor.
    ids = tuple(v.value for v in fw.file_headers[3].values)
    if len(ids) == 4:
        headers = tuple(tuple(v.value for v in h.values) for h in fw.file_headers)
        if headers != T6Z_HEADER_PROFILE:
            raise ValueError("unexpected T6Z header, CAN address, software secret, or encryption key")
    block = fw.firmware_blocks[0]
    if (block["start"], block["length"]) != (T6Z_START, T6Z_LENGTH):
        raise ValueError(f"T6Z image must start at 0x{T6Z_START:x} with length 0x{T6Z_LENGTH:x}, "
                         f"got 0x{block['start']:x}/0x{block['length']:x}")
    plain = t6z_decrypt(fw.firmware_encrypted[0], fw.keys)
    if b'HNAB' not in plain or not any(i in plain for i in T6Z_SOFTWARE_IDS):
        raise ValueError("T6Z image does not decrypt to a T6Z application (wrong keys or not this ECU)")
    if len(ids) == 4 and plain[T6Z_IDENTITY_OFFSET:T6Z_IDENTITY_OFFSET + len(T6Z_APP_IDS[0])] != T6Z_APP_IDS[0]:
        raise ValueError("decrypted T6Z payload identity does not match 39990-T6Z-A110")
    for start, end in T6Z_SUM_WINDOWS:
        total = le32_sum(plain, start, end)
        if total:
            raise ValueError(f"T6Z bank sum failed: LE32 [0x{start:x},0x{end:x}) = {total:08x}, must be 0")
        print(f"  T6Z bank LE32 sum [0x{start:x},0x{end:x}): PASS")
    total = le32_sum(plain, 0, T6Z_VALIDATE_END)
    if total:
        raise ValueError(f"T6Z validate sum failed: LE32 [0,0x{T6Z_VALIDATE_END:x}) = {total:08x}, must be 0")
    print(f"  T6Z validate (FF01) sum [0,0x{T6Z_VALIDATE_END:x}): PASS")


def validate_pilot_firmware(fw):
    """Keep the existing Pilot LE32 checksum path; A040 is offline-only."""
    ids = [v.value for v in fw.file_headers[3].values]
    block = fw.firmware_blocks[0]
    if ids not in ([PILOT_APP_ID], [b'39990-TG7-A040\x00\x00']) or bytes(fw.keys) != PILOT_KEYS or block["start"] != PILOT_FLASH_START:
        raise ValueError("Unexpected 0x50000 firmware identity, layout, or encryption keys")
    k0, k1, k2 = PILOT_KEYS
    plain = bytes(((((b + k0) ^ k1) - k2) & 0xff) for b in fw.firmware_encrypted[0])
    total, start = 0, 0
    for end in PILOT_CHECKSUM_ENDS:
        total = (total + le32_sum(plain, start, end)) & 0xffffffff
        if total:
            raise ValueError(f"Pilot checksum failed at 0x{end:x}")
        print(f"  Pilot cumulative LE32 [0,0x{end:x}): PASS")
        start = end


def require_uds_flashable(fw):
    """Refuse images eps-update.py's UDS sequence must not program."""
    if is_t6z(fw):
        raise ValueError(T6Z_FLASHER)
    if fw.firmware_blocks[0]["length"] == 0x50000 and [v.value for v in fw.file_headers[3].values] != [PILOT_APP_ID]:
        raise ValueError("Pilot A040 is reference-only; its flashing procedure has not been verified")
    if fw.file_headers[2].values[0].value != b'0':
        raise ValueError("not an EPS image at CAN address 0x18DA30F1")


def validate_container(fw):
    """Check the headers the flasher reads."""
    headers = fw.file_headers
    if len(headers[2].values) != 1 or len(headers[2].values[0].value) != 1:
        raise ValueError("header 2 must hold exactly one 1-byte ECU address")
    ids, secrets = headers[3].values, headers[4].values
    if not ids or not secrets or (len(ids) != len(secrets) and not is_t6z(fw)):
        raise ValueError(f"header 3/4 mismatch: {len(ids)} software IDs, {len(secrets)} seed secrets")
    if any(len(s.value) != 6 for s in secrets):
        raise ValueError("seed secrets in header 4 must be 6 bytes")
    if len(fw.firmware_blocks) != 1:
        raise ValueError("exactly one firmware block is required")


def validate_firmware(fw):
    """Validate the container headers, both firmware checksums and any THR/TJB ROM CRCs and monitor shadows."""
    validate_container(fw)
    length = fw.firmware_blocks[0]["length"]
    encrypted = fw.firmware_encrypted[0]
    if len(encrypted) != length:
        raise ValueError("firmware length incorrect")
    if is_t6z(fw):
        validate_t6z_firmware(fw)
        return
    if length == 0x50000:
        validate_pilot_firmware(fw)
        return
    if length not in (0x4c000, 0x6c000, ROM_CRC_LENGTH):
        raise ValueError(f"unsupported firmware length 0x{length:x}")
    if length == ROM_CRC_LENGTH and not rom_crc_definitions(fw):
        raise ValueError("0x74000 images require a known THR/TJB ROM CRC layout")
    if bytes(fw.keys) != PILOT_KEYS:
        raise ValueError("unsupported SH2A encryption keys")
    definitions = checksum_definitions(length)
    decrypted = bytes(DECRYPT_LOOKUP[b] for b in encrypted)
    for func, offset, label in definitions:
        stored = struct.unpack('!H', decrypted[offset:offset + 2])[0]
        words = struct.unpack(f'!{offset // 2}H', decrypted[:offset])
        calculated = (sum(words) * (-1 if func else 1)) & 0xffff
        if stored != calculated:
            raise ValueError(f"firmware checksum failed: {label} at 0x{offset:x}")
        print(f"  Firmware {label} checksum: PASS")
    start = fw.firmware_blocks[0]["start"]
    for region_start, region_end, slot in rom_crc_definitions(fw):
        stored = struct.unpack('!I', decrypted[slot - start:slot - start + 4])[0]
        calculated = crc32_bzip2(decrypted[region_start - start:region_end - start])
        if stored != calculated:
            raise ValueError(f"ROM CRC failed: [0x{region_start:x},0x{region_end:x}) at 0x{slot:x} "
                             f"stores {stored:08x}, image gives {calculated:08x}")
        print(f"  ROM CRC at 0x{slot:x}: PASS")
    family = shadow_family(fw)
    if family is not None:
        validate_shadows(decrypted, start, *family)


def check(path):
    from rwd_format.x5a import x5a
    print(f"\nChecking {path}")
    try:
        with open(path, 'rb') as stream:
            fw = x5a(stream.read())
        print("  Container and file checksum: PASS")
        validate_firmware(fw)
    except (OSError, ValueError) as e:
        print(f"  NOT VALIDATED: {e}")
        return False
    print("  ALL GOOD: container and firmware validation PASS")
    if is_t6z(fw):
        print(f"  Note: {T6Z_REFERENCE_NOTICE} {T6Z_FLASHER}.")
    return True


def main(argv=None):
    paths = sys.argv[1:] if argv is None else argv
    if not paths:
        print("Usage: python3 check_rwd.py <file.rwd> [file2.rwd ...]")
        return 1
    results = [check(path) for path in paths]
    return 0 if all(results) else 1


if __name__ == '__main__':
    sys.exit(main())
