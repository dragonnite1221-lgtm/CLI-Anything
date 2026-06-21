# ruff: noqa: E501
"""MSCX/MusicXML parsing utilities.

Handles reading and writing .mscz (ZIP containing .mscx XML) and
.mxl (ZIP containing MusicXML) files, plus XML inspection helpers.
"""

import os
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


# ── Key Signature Mapping ─────────────────────────────────────────────

# Integer key signatures: -7 (Cb) to +7 (C#)
# Negative = flats, positive = sharps, 0 = C major / A minor
KEY_INT_TO_MAJOR = {
    -7: "Cb",
    -6: "Gb",
    -5: "Db",
    -4: "Ab",
    -3: "Eb",
    -2: "Bb",
    -1: "F",
    0: "C",
    1: "G",
    2: "D",
    3: "A",
    4: "E",
    5: "B",
    6: "F#",
    7: "C#",
}

KEY_INT_TO_MINOR = {
    -7: "Ab",
    -6: "Eb",
    -5: "Bb",
    -4: "F",
    -3: "C",
    -2: "G",
    -1: "D",
    0: "A",
    1: "E",
    2: "B",
    3: "F#",
    4: "C#",
    5: "G#",
    6: "D#",
    7: "A#",
}

# Reverse: name → integer (case-insensitive, supports "C major", "C", "Cm", "C minor")
_KEY_NAME_TO_INT: dict[str, int] = {}
for _i, _name in KEY_INT_TO_MAJOR.items():
    _KEY_NAME_TO_INT[_name.lower()] = _i
    _KEY_NAME_TO_INT[f"{_name.lower()} major"] = _i
    _KEY_NAME_TO_INT[f"{_name.lower()}maj"] = _i
for _i, _name in KEY_INT_TO_MINOR.items():
    _KEY_NAME_TO_INT[f"{_name.lower()} minor"] = _i
    _KEY_NAME_TO_INT[f"{_name.lower()}m"] = _i
    _KEY_NAME_TO_INT[f"{_name.lower()}min"] = _i

__all__ = [
    "ET",
    "KEY_INT_TO_MAJOR",
    "KEY_INT_TO_MINOR",
    "Path",
    "_KEY_NAME_TO_INT",
    "_name",
    "os",
    "zipfile",
]
