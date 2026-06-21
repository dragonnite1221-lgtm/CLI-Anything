# ruff: noqa: F403, F405, E501
from .layers_base import *  # noqa: F403


def _read_jpeg_dimensions(path: str) -> Optional[tuple]:
    """Scan JPEG markers for the SOF frame that carries width/height."""
    try:
        with open(path, "rb") as f:
            f.read(2)  # skip SOI
            while True:
                b = f.read(1)
                if not b:
                    break
                if b != b"\xff":
                    continue
                marker = f.read(1)
                if not marker:
                    break
                code = marker[0]
                if code == 0xD9:  # EOI
                    break
                # Restart markers and bare 0xFF padding carry no length
                if code in range(0xD0, 0xD8) or code == 0x00 or code == 0x01:
                    continue
                length_data = f.read(2)
                if len(length_data) < 2:
                    break
                seg_len = struct.unpack(">H", length_data)[0]
                # SOF0-SOF3 contain the image dimensions
                if 0xC0 <= code <= 0xC3:
                    sof_data = f.read(min(seg_len - 2, 5))
                    if len(sof_data) >= 5:
                        h, w = struct.unpack(">HH", sof_data[1:5])
                        return (w, h)
                    break
                f.seek(seg_len - 2, 1)
    except (OSError, struct.error):
        pass
    return None


def _read_webp_dimensions(path: str) -> Optional[tuple]:
    """Read WebP dimensions from the VP8/VP8L chunk header."""
    try:
        with open(path, "rb") as f:
            data = f.read(30)
        if len(data) < 30:
            return None
        chunk = data[12:16]
        if chunk == b"VP8 ":
            w = struct.unpack("<H", data[26:28])[0] & 0x3FFF
            h = struct.unpack("<H", data[28:30])[0] & 0x3FFF
            return (w, h)
        if chunk == b"VP8L":
            bits = struct.unpack("<I", data[21:25])[0]
            w = (bits & 0x3FFF) + 1
            h = ((bits >> 14) & 0x3FFF) + 1
            return (w, h)
    except (OSError, struct.error):
        pass
    return None


def _read_tiff_dimensions(path: str, header: bytes) -> Optional[tuple]:
    """Read TIFF dimensions from the first IFD."""
    try:
        big = header[:2] == b"MM"
        fmt_h, fmt_i = (">H", ">I") if big else ("<H", "<I")
        ifd_offset = struct.unpack(fmt_i, header[4:8])[0]
        with open(path, "rb") as f:
            f.seek(ifd_offset)
            (n_entries,) = struct.unpack(fmt_h, f.read(2))
            w = h = None
            for _ in range(n_entries):
                entry = f.read(12)
                if len(entry) < 12:
                    break
                tag = struct.unpack(fmt_h, entry[0:2])[0]
                typ = struct.unpack(fmt_h, entry[2:4])[0]
                if tag == 256:  # ImageWidth
                    w = struct.unpack(
                        fmt_i if typ == 4 else fmt_h, entry[8 : 12 if typ == 4 else 10]
                    )[0]
                elif tag == 257:  # ImageLength
                    h = struct.unpack(
                        fmt_i if typ == 4 else fmt_h, entry[8 : 12 if typ == 4 else 10]
                    )[0]
                if w and h:
                    return (w, h)
    except (OSError, struct.error):
        pass
    return None
