# ruff: noqa: F403, F405, E501
from .instruments_base import *  # noqa: F403


def reorder_instruments(path: str, output_path: str, new_order: list[str]) -> dict:
    """Reorder instruments in a .mscz score.

    Args:
        path: Path to input .mscz file.
        output_path: Path to output .mscz file.
        new_order: List of instrument names in desired order.

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

    # Collect parts by name
    parts_by_name = {}
    for part in score.findall("Part"):
        inst = part.find("Instrument")
        if inst is not None:
            ln = inst.find("longName")
            name = ln.text if ln is not None else ""
            parts_by_name[name.lower()] = part

    # Validate: new_order must contain all instruments
    provided = {n.lower() for n in new_order}
    existing = set(parts_by_name.keys())
    missing = existing - provided
    if missing:
        missing_names = [n for n in parts_by_name if n in missing]
        raise ValueError(
            f"new_order is missing instruments: {missing_names}. "
            f"All instruments must be included to prevent data loss."
        )
    unknown = provided - existing
    if unknown:
        raise ValueError(f"Instruments not found in score: {list(unknown)}")

    # Remove all parts
    for part in score.findall("Part"):
        score.remove(part)

    # Re-add in new order
    for name in new_order:
        score.append(parts_by_name[name.lower()])

    xml_utils.write_mscz(output_path, data)

    return {
        "action": "reorder",
        "new_order": new_order,
        "output": str(Path(output_path).resolve()),
    }
