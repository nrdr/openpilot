import struct

class Base(object):
    def __init__(self, data, headers, keys, addr_blocks, encrypted):
        self._file_format = data[0:1]
        self._file_headers = headers
        self._file_checksum = struct.unpack('<L', data[-4:])[0]
        self._firmware_blocks = addr_blocks
        self._firmware_encrypted = encrypted
        self._keys = keys

        self.validate_file_checksum(data)

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

    def validate_file_checksum(self, data):
        calculated = sum(data[0:-4]) & 0xFFFFFFFF
        assert calculated == self.file_checksum, "file checksum mismatch"

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
