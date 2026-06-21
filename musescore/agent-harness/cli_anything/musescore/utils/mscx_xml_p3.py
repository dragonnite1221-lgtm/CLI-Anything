# ruff: noqa: F403, F405, E501
from .mscx_xml_base import *  # noqa: F403

# fmt: off
from .mscx_xml_p1 import read_mscz, read_mxl  # noqa: E402,E501
from .mscx_xml_p2 import detect_format  # noqa: E402,E501
# fmt: on


def read_score_tree(path: str) -> ET.ElementTree:
    """Read a score file and return its XML tree.

    Supports .mscz, .mxl, .musicxml, .xml formats.
    """
    fmt = detect_format(path)
    if fmt == "mscz":
        data = read_mscz(path)
        return data["mscx"]
    elif fmt == "mxl":
        return read_mxl(path)
    elif fmt == "musicxml":
        return ET.parse(path)
    else:
        raise ValueError(f"Cannot read XML tree from format: {fmt} ({path})")
