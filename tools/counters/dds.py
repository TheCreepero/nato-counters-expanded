import struct

import numpy as np

HEADER_SIZE = 128
FLAGS = 0x2100F
PIXEL_FORMAT_FLAGS = 0x41
CAPS_TEXTURE = 0x1000
MASKS = (0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)


def read_rgba(path):
    data = path.read_bytes()
    if data[:4] != b"DDS ":
        raise ValueError(f"{path} is not a DDS file")
    height, width = struct.unpack_from("<II", data, 12)
    bit_count = struct.unpack_from("<I", data, 88)[0]
    four_cc = data[84:88]
    if bit_count != 32 or four_cc != b"\x00\x00\x00\x00":
        raise ValueError(f"{path} is not an uncompressed 32-bit DDS")
    pixels = np.frombuffer(data, dtype=np.uint8, count=width * height * 4, offset=HEADER_SIZE)
    return pixels.reshape(height, width, 4)[:, :, [2, 1, 0, 3]].copy()


def write_rgba(path, rgba):
    height, width = rgba.shape[:2]
    header = bytearray(HEADER_SIZE)
    header[0:4] = b"DDS "
    struct.pack_into("<7I", header, 4, 124, FLAGS, height, width, width * 4, 1, 1)
    struct.pack_into("<4I", header, 76, 32, PIXEL_FORMAT_FLAGS, 0, 32)
    struct.pack_into("<4I", header, 92, *MASKS)
    struct.pack_into("<I", header, 108, CAPS_TEXTURE)
    bgra = np.ascontiguousarray(rgba[:, :, [2, 1, 0, 3]], dtype=np.uint8)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bytes(header) + bgra.tobytes())
