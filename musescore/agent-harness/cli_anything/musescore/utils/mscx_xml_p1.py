# ruff: noqa: F403, F405, E501
from .mscx_xml_base import *  # noqa: F403


def key_name_to_int(name: str) -> int:
    """Convert a key name to its integer representation.

    Accepts: "C", "C major", "Db", "Db major", "A minor", "Am", etc.

    Raises:
        ValueError: If the key name is not recognized.
    """
    normalized = name.strip().lower()
    if normalized in _KEY_NAME_TO_INT:
        return _KEY_NAME_TO_INT[normalized]

    raise ValueError(
        f"Unrecognized key name: '{name}'. Examples: C, Db major, F# minor, Bb, Am"
    )


def key_int_to_name(key_int: int, minor: bool = False) -> str:
    """Convert a key integer to its name."""
    table = KEY_INT_TO_MINOR if minor else KEY_INT_TO_MAJOR
    if key_int not in table:
        raise ValueError(f"Invalid key integer: {key_int}. Must be -7 to 7.")
    suffix = " minor" if minor else " major"
    return table[key_int] + suffix


def read_mscz(path: str) -> dict:
    """Read a .mscz file (ZIP archive).

    Returns:
        Dict with keys:
        - "mscx": ElementTree of the .mscx XML
        - "mscx_filename": name of the .mscx file inside the ZIP
        - "style": content of score_style.mss (str or None)
        - "audio_settings": content of audiosettings.json (str or None)
        - "view_settings": content of viewsettings.json (str or None)
        - "other_files": dict of other filename → bytes
    """
    result = {
        "mscx": None,
        "mscx_filename": None,
        "style": None,
        "audio_settings": None,
        "view_settings": None,
        "other_files": {},
    }

    with zipfile.ZipFile(path, "r") as zf:
        for name in zf.namelist():
            if name.endswith(".mscx"):
                result["mscx_filename"] = name
                xml_bytes = zf.read(name)
                result["mscx"] = ET.ElementTree(ET.fromstring(xml_bytes))
            elif name == "score_style.mss" or name.endswith("/score_style.mss"):
                result["style"] = zf.read(name).decode("utf-8")
            elif name == "audiosettings.json" or name.endswith("/audiosettings.json"):
                result["audio_settings"] = zf.read(name).decode("utf-8")
            elif name == "viewsettings.json" or name.endswith("/viewsettings.json"):
                result["view_settings"] = zf.read(name).decode("utf-8")
            else:
                result["other_files"][name] = zf.read(name)

    if result["mscx"] is None:
        raise ValueError(f"No .mscx file found inside {path}")

    return result


def write_mscz(path: str, data: dict) -> Path:
    """Write a .mscz file from component data.

    Args:
        path: Output .mscz path.
        data: Dict as returned by read_mscz().

    Returns:
        Path to the written file.
    """
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Write the .mscx XML
        mscx_filename = data.get("mscx_filename", "score.mscx")
        xml_str = ET.tostring(
            data["mscx"].getroot(), encoding="unicode", xml_declaration=True
        )
        zf.writestr(mscx_filename, xml_str)

        # Write style
        if data.get("style"):
            zf.writestr("score_style.mss", data["style"])

        # Write settings
        if data.get("audio_settings"):
            zf.writestr("audiosettings.json", data["audio_settings"])
        if data.get("view_settings"):
            zf.writestr("viewsettings.json", data["view_settings"])

        # Write other files
        for name, content in data.get("other_files", {}).items():
            zf.writestr(name, content)

    return Path(path)


def read_mxl(path: str) -> ET.ElementTree:
    """Read a .mxl file (compressed MusicXML).

    Returns:
        ElementTree of the MusicXML content.
    """
    with zipfile.ZipFile(path, "r") as zf:
        # Look for the MusicXML file
        for name in zf.namelist():
            if name.endswith(".xml") and not name.startswith("META-INF"):
                xml_bytes = zf.read(name)
                return ET.ElementTree(ET.fromstring(xml_bytes))

    raise ValueError(f"No MusicXML file found inside {path}")


def get_key_signature(tree: ET.ElementTree) -> int | None:
    """Extract the first key signature from a MusicXML or MSCX tree.

    Returns:
        Integer key signature (-7 to 7), or None if not found.
    """
    root = tree.getroot()

    # MusicXML: <key><fifths>-5</fifths></key>
    fifths = root.find(".//{*}fifths")
    if fifths is not None and fifths.text:
        return int(fifths.text)

    # MSCX: <KeySig><accidental>-5</accidental></KeySig>
    # or <KeySig><concertKey>-5</concertKey></KeySig>
    for tag in ["accidental", "concertKey"]:
        elem = root.find(f".//KeySig/{tag}")
        if elem is not None and elem.text:
            return int(elem.text)

    return None
