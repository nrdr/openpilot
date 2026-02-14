import sys
import struct
import operator
import itertools
import re

class Base(object):
    def __init__(self, data, headers, keys, addr_blocks, encrypted):
        self._file_format = data[0:1]
        self._file_headers = headers
        self._file_checksum = struct.unpack('<L', data[-4:])[0]
        self._firmware_blocks = addr_blocks
        self._firmware_encrypted = encrypted
        self._keys = keys
        self._decoder = None
        self._encoder = None
        self._unencrypted_firmware = None  # Added for writing mode support

        self._operators = [
            { 'fn': operator.__xor__, 'sym': '^' },
            { 'fn': operator.__and__, 'sym': '&' },
            { 'fn': operator.__or__,  'sym': '|' },
            { 'fn': operator.__add__, 'sym': '+' },
            { 'fn': operator.__sub__, 'sym': '-' },
            { 'fn': operator.__mul__, 'sym': '*' },
            { 'fn': operator.__floordiv__, 'sym': '/' },  # Custom division that returns int
            { 'fn': operator.__mod__, 'sym': '%' },
        ]

        self._operator_lut = {o['sym']: o['fn'] for o in self._operators}

        self.validate_file_checksum(data)

    @property
    def operator_lut(self):
        return self._operator_lut

    @property
    def file_format(self):
        return self._file_format

    @property
    def file_checksum(self):
        return self._file_checksum

    @property
    def file_headers(self):
        return self._file_headers

    @property
    def firmware_blocks(self):
        return self._firmware_blocks

    @property
    def firmware_encrypted(self):
        return self._firmware_encrypted

    @property
    def keys(self):
        return self._keys

    @property
    def decoder(self):
        return self._decoder

    @property
    def encoder(self):
        return self._encoder

    @property
    def unencrypted_firmware(self):
        return self._unencrypted_firmware

    def calc_checksum(self, data):
        result = -sum(data)
        return chr(result & 0xFF)

    def validate_file_checksum(self, data):
        calculated = sum(data[0:-4]) & 0xFFFFFFFF
        assert calculated == self.file_checksum, "file checksum mismatch"

    def _make_decoder(self, key1, key2, key3, op1, op2, op3):
        decoder = {}
        values = set()

        for e in range(256):
            d = op3(op2(op1(e, key1), key2), key3) & 0xFF
            decoder[chr(e)] = chr(d)
            values.add(d)

        return decoder if len(values) == 256 else None

    def _find_longest_common_substring(self, strings):
        """
        Find the longest common substring among a list of strings.

        Args:
            strings: list - List of strings to find common substring in

        Returns:
            str: Longest common substring, or empty string if none found
        """
        if not strings or len(strings) < 2:
            return strings[0] if strings else ""

        # Start with the first string
        common = strings[0]

        for string in strings[1:]:
            # Find longest common substring between current common and this string
            new_common = ""
            for i in range(len(common)):
                for j in range(i + 1, len(common) + 1):
                    substring = common[i:j]
                    if substring in string and len(substring) > len(new_common):
                        new_common = substring
            common = new_common

            # If no common substring found, break early
            if not common:
                break

        return common

    def crack_optimized(self, search_value, max_attempts=None):
        """
        Optimized version of crack that uses early termination and efficient search.

        Args:
            search_value: str - Known plaintext to search for
            max_attempts: int - Maximum decoder combinations to try (None for all)

        Returns:
            list: Firmware candidates if successful
        """
        print(f"Optimized crack search for: '{search_value}'")

        keys = list()
        for i in range(len(self._keys)):
            k = self._keys[i] if isinstance(self._keys[i], int) else ord(self._keys[i])
            keys.append({'val': k, 'sym': 'k{}'.format(i)})
        assert len(keys) == 3, "exactly three keys currently required!"

        firmware_candidates = []
        attempted_decoders = []
        attempts = 0

        key_perms = list(itertools.permutations(keys))
        op_perms = list(itertools.product(self._operators, repeat=3))

        total_combinations = len(key_perms) * len(op_perms)
        actual_limit = min(total_combinations, max_attempts) if max_attempts else total_combinations

        print(f"Key permutations: {len(key_perms)}, Operator permutations: {len(op_perms)}")
        print(f"Total combinations: {total_combinations:,}, Testing up to: {actual_limit:,}")

        for k1, k2, k3 in key_perms:
            for o1, o2, o3 in op_perms:
                if max_attempts and attempts >= max_attempts:
                    break

                attempts += 1
                if attempts % 1000 == 0:
                    print(f"Tested {attempts:,}/{actual_limit:,} combinations...")

                decoder = self._make_decoder(
                    k1['val'], k2['val'], k3['val'],
                    o1['fn'], o2['fn'], o3['fn'])

                if decoder is None or decoder in attempted_decoders:
                    continue
                attempted_decoders.append(decoder)

                decrypted, candidate = self.decrypt(decoder)

                # Search for byte patterns in the decrypted firmware
                if (search_value.encode('ascii') in decrypted) and candidate not in firmware_candidates:
                    print(f"\n✓ Found working decoder at attempt {attempts}")
                    self._decoder = decoder  # Store the working decoder
                    firmware_candidates.append([''.join(c) for c in candidate])

                    cipher_desc = f"(((i {o1['sym']} {k1['sym']}) {o2['sym']} {k2['sym']}) {o3['sym']} {k3['sym']}) & 0xFF"
                    print(f"Cipher: {cipher_desc}")

                    return firmware_candidates

            if max_attempts and attempts >= max_attempts:
                break

        print(f"\nTested {attempts:,} combinations, no working decoder found")
        return firmware_candidates

    def crack(self, search_value):
        print("search:")
        print(search_value)

        keys = list()
        for i in range(len(self._keys)):
            k = self._keys[i] if isinstance(self._keys[i], int) else ord(self._keys[i])
            keys.append({'val': k, 'sym': f"k{i}"})
        assert len(keys) == 3, "exactly three keys currently required!"

        firmware_candidates = list()
        display_ciphers = list()
        attempted_decoders = list()

        key_perms = list(itertools.permutations(keys))
        op_perms = list(itertools.product(self._operators, repeat=3))

        for k1, k2, k3 in key_perms:
            for o1, o2, o3 in op_perms:
                decoder = self._make_decoder(
                    k1['val'], k2['val'], k3['val'],
                    o1['fn'], o2['fn'], o3['fn'])

                if decoder is None or decoder in attempted_decoders:
                    continue
                attempted_decoders.append(decoder)

                decrypted, candidate = self.decrypt(decoder)
                search_bytes = search_value.encode('ascii')
                if (search_bytes in decrypted) and candidate not in firmware_candidates:
                    sys.stdout.write('X')
                    firmware_candidates.append([''.join(c) for c in candidate])
                    display_ciphers.append(
                        "(((i {} {}) {} {}) {} {}) & 0xFF".format(
                            o1['sym'], k1['sym'],
                            o2['sym'], k2['sym'],
                            o3['sym'], k3['sym']))
                    # Store the working decoder and create encoder
                    self._decoder = decoder
                    self._encoder = self._create_encoder(decoder)
                else:
                    sys.stdout.write('.')
                sys.stdout.flush()

        print("")
        for cipher in display_ciphers:
            print("cipher: {}".format(cipher))
        return firmware_candidates

    def decrypt(self, decoder):
        candidate = [map(lambda x: decoder[chr(x)], e) for e in self._firmware_encrypted]
        decrypted = bytes([ord(c) for l in candidate for c in l])

        return decrypted, candidate

    def __str__(self):
        info = [
            "file format: {}".format(self.file_format),
            "file checksum: {}".format(hex(self.file_checksum)),
        ]
        info.append("headers:")
        info.extend([str(h) for h in self._file_headers])
        info.append("keys:")
        info.extend([
            "k{} = {}".format(i, hex(self._keys[i]))
            for i in range(len(self._keys))
        ])
        info.append("address blocks:")
        info.extend([
            "start = {} len = {}".format(hex(i["start"]), hex(i["length"]))
            for i in self._firmware_blocks
        ])

        return '\n'.join(info)

    def _create_encoder(self, decoder):
        """
        Create encoder lookup table from decoder

        Args:
            decoder: dict - Decryption lookup table from crack() method

        Returns:
            dict: Encoder lookup table (inverse of decoder)
        """
        encoder = {}
        for encrypted_byte, decrypted_byte in decoder.items():
            # Convert bytes to int for lookup
            enc_int = encrypted_byte[0] if isinstance(encrypted_byte, bytes) else encrypted_byte
            dec_int = decrypted_byte[0] if isinstance(decrypted_byte, bytes) else decrypted_byte
            encoder[dec_int] = enc_int
        return encoder

    def encrypt_firmware(self, unencrypted_firmware, encryption_lut):
        """
        Encrypt firmware using encryption lookup table.

        Args:
            unencrypted_firmware: list - List of unencrypted firmware byte arrays
            encryption_lut: dict - Encryption lookup table

        Returns:
            list: List of encrypted firmware byte arrays
        """
        encrypted_firmware = []
        for firmware_block in unencrypted_firmware:
            encrypted_block = bytearray()
            for byte in firmware_block:
                byte_val = byte if isinstance(byte, int) else ord(byte)
                if byte_val not in encryption_lut:
                    raise ValueError(f"Byte value {byte_val} not found in encryption lookup table")
                encrypted_block.append(encryption_lut[byte_val])
            encrypted_firmware.append(bytes(encrypted_block))
        return encrypted_firmware

    def set_decoder_from_operators(self, operator_symbols):
        """
        Set decoder using keys and operator symbols.

        Args:
            operator_symbols: str - 3-character string of operator symbols (e.g., "^+-")
                            Symbols correspond to those defined in _operators field:
                            '^' = XOR, '&' = AND, '|' = OR, '+' = ADD, '-' = SUB,
                            '*' = MUL, '/' = DIV, '%' = MOD

        Raises:
            ValueError: If operator symbols are invalid or decoder creation fails
        """
        if len(operator_symbols) != 3:
            raise ValueError("operator_symbols must be exactly 3 characters")

        if not hasattr(self, '_keys') or not self._keys or len(self._keys) != 3:
            raise ValueError("Need exactly 3 encryption keys")

        # Convert keys to integers
        k1, k2, k3 = [k if isinstance(k, int) else ord(k) for k in self._keys]

        # Get operator functions from symbols
        try:
            o1_fn = self._operator_lut[operator_symbols[0]]
            o2_fn = self._operator_lut[operator_symbols[1]]
            o3_fn = self._operator_lut[operator_symbols[2]]
        except KeyError as e:
            valid_symbols = list(self._operator_lut.keys())
            raise ValueError(f"Invalid operator symbol {e}. Valid symbols: {valid_symbols}")

        # Create decoder with specified keys and operators
        decoder = self._make_decoder(k1, k2, k3, o1_fn, o2_fn, o3_fn)

        if decoder is None:
            raise ValueError(f"Failed to create valid decoder with operators '{operator_symbols}' and given keys")

        # Store decoder and encoder
        self._decoder = decoder
        self._encoder = self._create_encoder(decoder)

    def set_unencrypted_firmware(self, unencrypted_firmware_data):
        """
        Set unencrypted firmware data for writing mode.

        This allows modifying an existing object (created from reading a file)
        to write out modified firmware.

        Args:
            unencrypted_firmware_data: bytes - New unencrypted firmware data
        """
        self._unencrypted_firmware = [unencrypted_firmware_data]

        # Update firmware blocks with new length
        if self._firmware_blocks:
            self._firmware_blocks[0]['length'] = len(unencrypted_firmware_data)

    def generate(self, cvn_data=None):
        """
        Generate file bytes from object (generic implementation).

        This method should be overridden by subclasses for format-specific generation,
        but provides a basic implementation for common functionality.

        Args:
            cvn_data: bytes - Optional CVN data

        Returns:
            bytes: Complete file data
        """
        # This is a generic implementation - subclasses should override
        # for format-specific header generation and file structure
        raise NotImplementedError("Subclasses must implement generate() method")

    def update_firmware_workflow(self, patched_firmware_data, search_value, metadata_updates=None):
        """
        Complete firmware update workflow as described:
        1) Read existing RWD file and populate fields from the file (already done in __init__)
        2) Derive the decoder by cracking using the crack method with known plaintext
        3) Update the unencrypted bytes with the patched version
        4) Update any of the metadata fields in the RWD header
        5) Write out updated RWD file (via generate method)

        Args:
            patched_firmware_data: bytes - New patched firmware data
            search_value: str - Known plaintext from header "3" entries for cracking
            metadata_updates: dict - Optional metadata updates for headers
                Format: {header_id: [(value_index, new_value), ...]}

        Returns:
            bytes: Updated RWD file data
        """
        # Step 2: Derive decoder by cracking with known plaintext
        print(f"Cracking encryption using search value: {search_value}")
        firmware_candidates = self.crack(search_value)

        if not firmware_candidates:
            raise ValueError(f"Failed to crack encryption with search value: {search_value}")

        print(f"Found {len(firmware_candidates)} firmware candidates")

        # Step 3: Update the unencrypted bytes with patched version
        print("Setting patched firmware data")
        self.set_unencrypted_firmware(patched_firmware_data)

        # Step 4: Update metadata fields in RWD header if provided
        if metadata_updates:
            print("Updating metadata fields")
            self.update_metadata_fields(metadata_updates)

        # Step 5: Generate updated RWD file with updated metadata
        print("Generating updated RWD file")
        return self.generate(search_value)

    def update_metadata_fields(self, metadata_updates):
        """
        Update metadata fields in RWD headers.

        Args:
            metadata_updates: dict - Metadata updates for headers
                Format: {header_id: [(value_index, new_value), ...]}
                Example: {1: [(0, new_cvn_data)], 3: [(0, new_version_string)]}
        """
        for header_id, updates in metadata_updates.items():
            if header_id >= len(self._file_headers):
                print(f"Warning: Header {header_id} does not exist, skipping")
                continue

            header = self._file_headers[header_id]

            for value_index, new_value in updates:
                if value_index >= len(header.values):
                    print(f"Warning: Header {header_id} value index {value_index} does not exist, skipping")
                    continue

                # Update the value
                old_value = header.values[value_index].value
                header.values[value_index]._value = new_value

                # Update the length prefix
                if isinstance(new_value, str):
                    new_value_bytes = new_value.encode()
                elif isinstance(new_value, bytes):
                    new_value_bytes = new_value
                else:
                    new_value_bytes = bytes(new_value)

                header.values[value_index]._prefix = len(new_value_bytes)

                print(f"Updated header {header_id} value {value_index}: {old_value} -> {new_value}")

    def get_header_3_values(self):
        """
        Get all values from header 3 (typically version strings) for use as known plaintext.

        Returns:
            list: List of header 3 values as strings
        """
        if len(self._file_headers) <= 3:
            return []

        header_3 = self._file_headers[3]
        values = []

        for header_value in header_3.values:
            value = header_value.value
            if isinstance(value, bytes):
                try:
                    value = value.decode('utf-8', errors='ignore')
                except:
                    value = str(value)
            values.append(str(value))

        return values

    def auto_crack_with_header_3(self):
        """
        Automatically attempt to crack encryption using header 3 values as known plaintext.
        Uses optimized approach with longest common substring.

        Returns:
            list: Firmware candidates if successful, empty list if failed
        """
        header_3_values = self.get_header_3_values()

        if not header_3_values:
            print("No header 3 values found for cracking")
            return []

        print(f"Found {len(header_3_values)} header 3 values")

        # Find longest common substring for more efficient search
        common_substring = self._find_longest_common_substring(header_3_values)

        if common_substring and len(common_substring) >= 4:
            print(f"Using longest common substring for efficient search: '{common_substring}'")
            try:
                firmware_candidates = self.crack_optimized(common_substring, max_attempts=10000)
                if firmware_candidates:
                    print(f"Successfully cracked with common substring: '{common_substring}'")
                    return firmware_candidates
            except Exception as e:
                print(f"Failed to crack with common substring '{common_substring}': {e}")

        # Fallback to individual header 3 values with optimized search
        # Try values in descending order (last to first entry)
        print("Trying individual header 3 values with optimized search...")
        for search_value in reversed(header_3_values):
            try:
                print(f"Trying search value: '{search_value}'")
                firmware_candidates = self.crack_optimized(search_value, max_attempts=5000)
                if firmware_candidates:
                    print(f"Successfully cracked with search value: '{search_value}'")
                    return firmware_candidates
            except Exception as e:
                print(f"Failed to crack with search value '{search_value}': {e}")
                continue

        print("Failed to crack with any header 3 values")
        return []
