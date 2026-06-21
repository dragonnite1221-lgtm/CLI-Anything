# ruff: noqa: F403, F405, E501
from .instruments_base import *  # noqa: F403


def remove_instrument(path: str, output_path: str, instrument_name: str) -> dict:
    """Remove an instrument from a .mscz score.

    Args:
        path: Path to input .mscz file.
        output_path: Path to output .mscz file.
        instrument_name: Name of the instrument to remove (case-insensitive).

    Returns:
        Dict with result info.
    """
    fmt = xml_utils.detect_format(path)
    if fmt != "mscz":
        raise ValueError("Instrument manipulation requires .mscz format")

    data = xml_utils.read_mscz(path)
    root = data["mscx"].getroot()

    score = root.find(".//Score")
    if score is None:
        raise RuntimeError("No <Score> element found in MSCX")

    # Find the part to remove
    removed = False
    for part in score.findall("Part"):
        inst = part.find("Instrument")
        if inst is not None:
            ln = inst.find("longName")
            name = ln.text if ln is not None else ""
            if name.lower() == instrument_name.lower():
                # Get staff ID before removing
                staff_elem = part.find("Staff")
                staff_id = staff_elem.get("id") if staff_elem is not None else None

                score.remove(part)

                # Also remove corresponding score-level Staff
                if staff_id:
                    for s in score.findall("Staff"):
                        if s.get("id") == staff_id:
                            score.remove(s)
                            break

                removed = True
                break

    if not removed:
        raise ValueError(f"Instrument '{instrument_name}' not found")

    xml_utils.write_mscz(output_path, data)

    return {
        "action": "remove",
        "instrument_name": instrument_name,
        "output": str(Path(output_path).resolve()),
    }
