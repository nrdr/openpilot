import struct
from .base import Base
from .header import Header
from .header_value import HeaderValue

class x5a(Base):
    def __init__(self, data):
        """
        Initialize x5a object for reading existing RWD files.

        Args:
            data: bytes - RWD file data to parse
        """
        # Reading mode - parse existing RWD file
        start_idx = 3 # skip file type indicator bytes
        headers, header_data_len = self._parse_file_headers(data[start_idx:])
        keys = self._get_keys(headers)

        start_idx += header_data_len
        addr_blocks, encrypted = self._get_firmware(data[start_idx:-4]) # exclude file checksum

        Base.__init__(self, data, headers, keys, addr_blocks, encrypted)
        self._encoder = None
        self._decoder = None
        self._unencrypted_firmware = None  # Will be set when firmware is decrypted


    def _parse_file_headers(self, data):
        headers = list()
        d_idx = 0

        for h_idx in range(6):
            h_prefix = data[d_idx]
            d_idx += 1

            # first byte is number of values
            cnt = h_prefix

            f_header = Header(h_idx, h_prefix, "")
            for v_idx in range(cnt):
                v_prefix = data[d_idx]
                d_idx += 1

                # first byte is length of value
                length = v_prefix
                v_data = data[d_idx:d_idx+length]
                d_idx += length

                h_value = HeaderValue(v_prefix, "", v_data)
                f_header.values.append(h_value)

            headers.append(f_header)

        return headers, d_idx

    def _get_keys(self, headers):
        for header in headers:
            if header.id == 5:
                assert len(header.values) == 1, "encryption key header does not have exactly one value!"
                assert len(header.values[0].value) == 3, "encryption key header not three bytes!"
                return header.values[0].value

        raise Exception("could not find encryption key header!")

    def _get_firmware(self, data):
        blocks = []
        encrypted = []
        idx = 0

        while idx + 8 <= len(data):
            start = struct.unpack('!I', data[idx:idx+4])[0]
            length = struct.unpack('!I', data[idx+4:idx+8])[0]
            if length == 0 or idx + 8 + length > len(data):
                break
            blocks.append({"start": start, "length": length})
            encrypted.append(data[idx+8:idx+8+length])
            idx += 8 + length

        assert len(blocks) > 0, "no firmware blocks found!"
        return blocks, encrypted

    def _generate_file_header(self, indicator, headers):
        """
        Generate file header bytes from indicator and headers.

        Args:
            indicator: bytes - 3-byte file type indicator
            headers: list - List of Header objects

        Returns:
            bytes: Generated header bytes
        """
        header_bytes = indicator
        for header in headers:
            # Add count of values in this header
            header_bytes += bytes([len(header.values)])

            # Add each value with its length prefix
            for header_value in header.values:
                value_data = header_value.value
                if isinstance(value_data, str):
                    value_data = value_data.encode()
                elif not isinstance(value_data, bytes):
                    value_data = bytes(value_data)

                header_bytes += bytes([len(value_data)]) + value_data

        return header_bytes

    def generate(self, cvn_data=None):
        """
        Generate RWD file bytes from x5a object.

        Args:
            cvn_data: bytes - Optional CVN data, if None will calculate from firmware

        Returns:
            bytes: Complete RWD file data
        """
        # CVN calculation should be done externally (e.g., in honda_firmware_patcher)
        # and passed as cvn_data parameter

        # Update Header 1 with CVN if provided
        if cvn_data is not None and len(self._file_headers) > 1:
            # Clear existing CVN values and add new one
            self._file_headers[1].values.clear()
            if cvn_data:  # Only add if not empty
                cvn_header_value = HeaderValue(len(cvn_data), "", cvn_data)
                self._file_headers[1].values.append(cvn_header_value)

        # Generate file header
        indicator = b'\x5A\x0D\x0A'  # Standard RWD indicator
        header_bytes = self._generate_file_header(indicator, self._file_headers)

        # Get encryption lookup table
        if hasattr(self, '_unencrypted_firmware') and self._unencrypted_firmware is not None:
            # For writing mode - encoder must exist (from crack or explicit decoder)
            if not hasattr(self, '_encoder') or self._encoder is None:
                raise ValueError("Cannot encrypt firmware without a valid encoder. "
                               "LUT must be created from a known good decoder using crack() method "
                               "or by explicitly setting decoder with set_decoder_from_operators().")
            encryption_lut = self._encoder
            encrypted_firmware = self.encrypt_firmware(self._unencrypted_firmware, encryption_lut)
        else:
            # For reading mode - use existing encrypted firmware and get LUT from cracking
            encryption_lut = self.encoder
            encrypted_firmware = self._firmware_encrypted

        # Generate address/length section
        addr_len_bytes = b''
        for i, block in enumerate(self._firmware_blocks):
            start_bytes = struct.pack('!I', block['start'])
            length_bytes = struct.pack('!I', block['length'])
            addr_len_bytes += start_bytes + length_bytes

        # Combine encrypted firmware
        firmware_bytes = b''.join(encrypted_firmware)

        # Calculate file checksum (sum of all preceding bytes)
        checksum_data = header_bytes + addr_len_bytes + firmware_bytes
        file_checksum = sum(checksum_data) & 0xFFFFFFFF
        checksum_bytes = struct.pack('<L', file_checksum)

        # Combine all parts
        rwd_data = header_bytes + addr_len_bytes + firmware_bytes + checksum_bytes

        return rwd_data

    def set_unencrypted_firmware(self, unencrypted_firmware_data):
        """
        Set unencrypted firmware data for writing mode.

        This allows modifying an existing x5a object (created from reading an RWD file)
        to write out modified firmware.

        Args:
            unencrypted_firmware_data: bytes - New unencrypted firmware data
        """
        self._unencrypted_firmware = [unencrypted_firmware_data]

        # Update firmware blocks with new length
        if self._firmware_blocks:
            self._firmware_blocks[0]['length'] = len(unencrypted_firmware_data)

    def update_firmware_workflow(self, patched_firmware_data, search_value, metadata_updates=None, cvn_data=None):
        """
        Complete firmware update workflow for x5a/RWD files:
        1) Read existing RWD file and populate fields from the file (already done in __init__)
        2) Derive the decoder by cracking using the crack method with known plaintext
        3) Update the unencrypted bytes with the patched version
        4) Update any of the metadata fields in the RWD header (including CVNs)
        5) Write out updated RWD file with updated checksums

        Args:
            patched_firmware_data: bytes - New patched firmware data
            search_value: str - Known plaintext for cracking (if None, will use header 3 values)
            metadata_updates: dict - Optional metadata updates for headers
            cvn_data: bytes - Optional new CVN data for header 1

        Returns:
            bytes: Updated RWD file data
        """
        # Step 2: Derive decoder by cracking with known plaintext
        if search_value is None or search_value == "":
            print("No search value provided, attempting auto-crack with header 3 values")
            firmware_candidates = self.auto_crack_with_header_3()
            # Get a valid search value for generate() method
            header_3_values = self.get_header_3_values()
            search_value = header_3_values[0] if header_3_values else ""
        else:
            print(f"Cracking encryption using search value: {search_value}")
            # Use longest common substring approach like the optimized method
            header_3_values = self.get_header_3_values()
            if header_3_values and len(header_3_values) > 1:
                # Find longest common substring for efficient search
                common_substring = self._find_longest_common_substring(header_3_values)
                if len(common_substring) >= 4:  # Use common substring if meaningful
                    print(f"Using longest common substring for search: '{common_substring}'")
                    search_value = common_substring
            firmware_candidates = self.crack(search_value)

        if not firmware_candidates:
            raise ValueError("Failed to crack encryption - no valid decoder found")

        print(f"Found {len(firmware_candidates)} firmware candidates")

        # Step 3: Update the unencrypted bytes with patched version
        print("Setting patched firmware data")
        self.set_unencrypted_firmware(patched_firmware_data)

        # Step 4: Update metadata fields in RWD header
        if cvn_data is not None:
            print("Updating CVN data in header 1")
            self.update_cvn(cvn_data)

        if metadata_updates:
            print("Updating additional metadata fields")
            self.update_metadata_fields(metadata_updates)

        # Step 5: Generate updated RWD file with updated checksums
        print("Generating updated RWD file")
        return self.generate(search_value or "", cvn_data)

    def update_cvn(self, cvn_data):
        """
        Update CVN data in header 1.

        Args:
            cvn_data: bytes - New CVN data
        """
        if len(self._file_headers) <= 1:
            raise ValueError("Header 1 (CVN header) does not exist")

        header_1 = self._file_headers[1]

        # Clear existing CVN values
        header_1.values.clear()
        header_1._prefix = 0

        # Add new CVN if provided
        if cvn_data:
            if isinstance(cvn_data, str):
                cvn_data = cvn_data.encode()
            elif not isinstance(cvn_data, bytes):
                cvn_data = bytes(cvn_data)

            cvn_header_value = HeaderValue(len(cvn_data), "", cvn_data)
            header_1.values.append(cvn_header_value)
            header_1._prefix = 1

            print(f"Updated CVN data: {cvn_data}")
        else:
            print("Cleared CVN data (empty)")

    def calculate_and_update_cvn(self, cvn_calculator_func=None):
        """
        Calculate CVN from current firmware and update header 1.

        Args:
            cvn_calculator_func: callable - Function to calculate CVN from firmware bytes
                                 Should take firmware bytes and return CVN bytes
                                 If None, will skip CVN calculation

        Returns:
            bytes: Calculated CVN data or None if no calculator provided
        """
        if cvn_calculator_func is None:
            print("No CVN calculator provided, skipping CVN calculation")
            return None

        if not hasattr(self, '_unencrypted_firmware') or not self._unencrypted_firmware:
            raise ValueError("No unencrypted firmware available for CVN calculation")

        firmware_data = self._unencrypted_firmware[0]
        cvn_data = cvn_calculator_func(firmware_data)

        if cvn_data:
            self.update_cvn(cvn_data)
            print(f"Calculated and updated CVN: {cvn_data}")

        return cvn_data

    def get_firmware_info(self):
        """
        Get information about the current firmware state.

        Returns:
            dict: Firmware information including addresses, lengths, encryption status
        """
        info = {
            'firmware_blocks': self._firmware_blocks,
            'has_encrypted_firmware': bool(self._firmware_encrypted),
            'has_unencrypted_firmware': bool(hasattr(self, '_unencrypted_firmware') and self._unencrypted_firmware),
            'has_decoder': bool(hasattr(self, '_decoder') and self._decoder),
            'has_encoder': bool(hasattr(self, '_encoder') and self._encoder),
            'header_count': len(self._file_headers),
            'encryption_keys': self._keys
        }

        if self._firmware_blocks:
            info['total_firmware_size'] = sum(block['length'] for block in self._firmware_blocks)

        return info

    def validate_firmware_update(self, patched_firmware_data):
        """
        Validate that patched firmware data is compatible with current RWD structure.

        Args:
            patched_firmware_data: bytes - New firmware data to validate

        Returns:
            dict: Validation results
        """
        results = {
            'valid': True,
            'warnings': [],
            'errors': []
        }

        if not self._firmware_blocks:
            results['valid'] = False
            results['errors'].append("No firmware blocks defined")
            return results

        expected_size = self._firmware_blocks[0]['length']
        actual_size = len(patched_firmware_data)

        if actual_size != expected_size:
            results['warnings'].append(f"Firmware size mismatch: expected {expected_size}, got {actual_size}")
            # This is a warning, not an error, as we can update the block length

        if not hasattr(self, '_keys') or not self._keys:
            results['valid'] = False
            results['errors'].append("No encryption keys available")

        if len(self._keys) != 3:
            results['valid'] = False
            results['errors'].append(f"Expected 3 encryption keys, got {len(self._keys)}")

        return results

    def create_backup_info(self):
        """
        Create backup information for the current RWD state.

        Returns:
            dict: Backup information that can be used to restore state
        """
        backup = {
            'file_format': self._file_format,
            'file_checksum': self._file_checksum,
            'firmware_blocks': self._firmware_blocks.copy(),
            'keys': self._keys,
            'headers': []
        }

        # Deep copy headers
        for header in self._file_headers:
            header_backup = {
                'id': header.id,
                'prefix': header.prefix,
                'suffix': header.suffix,
                'values': []
            }

            for value in header.values:
                value_backup = {
                    'prefix': value.prefix,
                    'suffix': value.suffix,
                    'value': value.value
                }
                header_backup['values'].append(value_backup)

            backup['headers'].append(header_backup)

        return backup
