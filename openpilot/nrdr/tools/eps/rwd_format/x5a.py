import struct
from .base import Base
from .header import Header
from .header_value import HeaderValue

class x5a(Base):
    def __init__(self, data):
        if len(data) < 7 or data[:1] != b"\x5a":
            raise ValueError("not a complete 0x5A RWD container")
        start_idx = 3 # skip file type indicator bytes
        headers, header_data_len = self._parse_file_headers(data[start_idx:-4])
        keys = self._get_keys(headers)

        start_idx += header_data_len
        addr_blocks, encrypted = self._get_firmware(data[start_idx:-4]) # exclude file checksum

        Base.__init__(self, data, headers, keys, addr_blocks, encrypted)

    def _parse_file_headers(self, data):
        headers = list()
        d_idx = 0

        for h_idx in range(6):
            if d_idx >= len(data):
                raise ValueError("truncated RWD header")
            h_prefix = data[d_idx]
            d_idx += 1

            # first byte is number of values
            cnt = h_prefix

            f_header = Header(h_idx, h_prefix, "")
            for _v_idx in range(cnt):
                if d_idx >= len(data):
                    raise ValueError("truncated RWD header value")
                v_prefix = data[d_idx]
                d_idx += 1

                # first byte is length of value
                length = v_prefix
                if d_idx + length > len(data):
                    raise ValueError("truncated RWD header value payload")
                v_data = data[d_idx:d_idx+length]
                d_idx += length

                h_value = HeaderValue(v_prefix, "", v_data)
                f_header.values.append(h_value)

            headers.append(f_header)

        return headers, d_idx

    def _get_keys(self, headers):
        for header in headers:
            if header.id == 5:
                if len(header.values) != 1:
                    raise ValueError("encryption key header does not have exactly one value")
                if len(header.values[0].value) != 3:
                    raise ValueError("encryption key header not three bytes")
                return header.values[0].value

        raise ValueError("could not find encryption key header")

    def _get_firmware(self, data):
        if len(data) < 8:
            raise ValueError("truncated firmware block header")
        start = struct.unpack('!I', data[0:4])[0]
        length = struct.unpack('!I', data[4:8])[0]

        firmware = data[8:]
        if not length or len(firmware) != length:
            raise ValueError("firmware length incorrect or empty")
        return [{"start": start, "length": length}], [firmware]
