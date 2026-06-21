# ruff: noqa: F403, F405, E501
from .instruments_base import *  # noqa: F403


def list_instruments(path: str) -> list[dict]:
    """List instruments in a score.

    Tries mscore --score-meta first, falls back to XML parsing.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Score file not found: {path}")

    # Try mscore metadata
    try:
        meta = backend.get_score_meta(path)
        parts = meta.get("parts", [])
        return [
            {
                "index": i,
                "name": p.get("name", f"Instrument {i + 1}"),
                "instrumentId": p.get("instrumentId", ""),
                "program": p.get("program", 0),
            }
            for i, p in enumerate(parts)
        ]
    except Exception as e:
        logger.debug(
            "mscore metadata failed for instruments, falling back to XML: %s", e
        )

    # Fallback: XML parsing
    try:
        tree = xml_utils.read_score_tree(path)
        instruments = xml_utils.get_instruments(tree)
        return [
            {
                "index": i,
                "name": inst.get("name")
                or inst.get("part_name", f"Instrument {i + 1}"),
                "instrumentId": inst.get("id", ""),
            }
            for i, inst in enumerate(instruments)
        ]
    except Exception as e:
        raise RuntimeError(f"Could not list instruments: {e}")


def add_instrument(path: str, output_path: str, instrument_id: str, name: str) -> dict:
    """Add an instrument to a .mscz score via MSCX XML manipulation.

    Args:
        path: Path to input .mscz file.
        output_path: Path to output .mscz file.
        instrument_id: MuseScore instrument ID (e.g., "keyboard.piano").
        name: Display name for the instrument.

    Returns:
        Dict with result info.
    """
    fmt = xml_utils.detect_format(path)
    if fmt != "mscz":
        raise ValueError("Instrument manipulation requires .mscz format")

    data = xml_utils.read_mscz(path)
    root = data["mscx"].getroot()

    # Find or create the Score element
    score = root.find(".//Score")
    if score is None:
        raise RuntimeError("No <Score> element found in MSCX")

    # Count existing parts BEFORE adding the new one
    import xml.etree.ElementTree as ET

    staff_id = str(len(score.findall("Part")) + 1)

    part = ET.SubElement(score, "Part")
    staff = ET.SubElement(part, "Staff")
    staff.set("id", staff_id)

    instrument = ET.SubElement(part, "Instrument")
    instrument.set("id", instrument_id)
    long_name = ET.SubElement(instrument, "longName")
    long_name.text = name
    short_name = ET.SubElement(instrument, "shortName")
    short_name.text = name[:3]

    # Also add a Staff element at the score level
    score_staff = ET.SubElement(score, "Staff")
    score_staff.set("id", staff_id)

    xml_utils.write_mscz(output_path, data)

    return {
        "action": "add",
        "instrument_id": instrument_id,
        "name": name,
        "output": str(Path(output_path).resolve()),
    }
