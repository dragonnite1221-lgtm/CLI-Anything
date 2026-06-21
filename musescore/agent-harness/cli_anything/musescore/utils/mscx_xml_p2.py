# ruff: noqa: F403, F405, E501
from .mscx_xml_base import *  # noqa: F403


def get_time_signature(tree: ET.ElementTree) -> str | None:
    """Extract the first time signature.

    Returns:
        String like "4/4", "3/4", etc., or None.
    """
    root = tree.getroot()

    # MusicXML: <time><beats>4</beats><beat-type>4</beat-type></time>
    beats = root.find(".//{*}beats")
    beat_type = root.find(".//{*}beat-type")
    if beats is not None and beat_type is not None:
        return f"{beats.text}/{beat_type.text}"

    # MSCX: <TimeSig><sigN>4</sigN><sigD>4</sigD></TimeSig>
    sig_n = root.find(".//TimeSig/sigN")
    sig_d = root.find(".//TimeSig/sigD")
    if sig_n is not None and sig_d is not None:
        return f"{sig_n.text}/{sig_d.text}"

    return None


def get_instruments(tree: ET.ElementTree) -> list[dict]:
    """Extract instrument info from a MusicXML or MSCX tree.

    Returns:
        List of dicts with 'id', 'name', 'part_name' keys.
    """
    root = tree.getroot()
    instruments = []

    # MusicXML: <score-part id="P1"><part-name>Piano</part-name>
    #            <score-instrument id="P1-I1"><instrument-name>Piano</instrument-name>
    for sp in root.findall(".//{*}score-part"):
        inst = {"id": sp.get("id", ""), "name": "", "part_name": ""}
        pn = sp.find("{*}part-name")
        if pn is None:
            pn = sp.find("part-name")
        if pn is not None:
            inst["part_name"] = pn.text or ""
        sin = sp.find(".//{*}instrument-name")
        if sin is not None:
            inst["name"] = sin.text or ""
        else:
            inst["name"] = inst["part_name"]
        instruments.append(inst)

    if instruments:
        return instruments

    # MSCX: <Part><Instrument id="keyboard.piano"><longName>Piano</longName>
    for part in root.findall(".//Part"):
        inst_elem = part.find("Instrument")
        if inst_elem is not None:
            inst = {
                "id": inst_elem.get("id", ""),
                "name": "",
                "part_name": "",
            }
            ln = inst_elem.find("longName")
            if ln is not None:
                inst["name"] = ln.text or ""
            sn = inst_elem.find("shortName")
            if sn is not None:
                inst["part_name"] = sn.text or inst["name"]
            else:
                inst["part_name"] = inst["name"]
            instruments.append(inst)

    return instruments


def get_score_title(tree: ET.ElementTree) -> str:
    """Extract score title from XML."""
    root = tree.getroot()

    # MusicXML: <work><work-title>...</work-title></work>
    # or <movement-title>...</movement-title>
    wt = root.find(".//{*}work-title")
    if wt is not None and wt.text:
        return wt.text
    mt = root.find(".//{*}movement-title")
    if mt is not None and mt.text:
        return mt.text

    # MSCX: <metaTag name="workTitle">...</metaTag>
    for meta in root.findall(".//metaTag"):
        if meta.get("name") == "workTitle" and meta.text:
            return meta.text

    return ""


def count_measures(tree: ET.ElementTree) -> int:
    """Count the number of measures in a score."""
    root = tree.getroot()

    # MusicXML: count <measure> elements in the first part
    measures = root.findall(".//{*}measure")
    if measures:
        # Each part has its own measures; count the first part's
        first_part = root.find(".//{*}part")
        if first_part is not None:
            return len(first_part.findall("{*}measure"))
        return len(measures)

    # MSCX: count <Measure> elements in the first staff
    mscx_measures = root.findall(".//Measure")
    if mscx_measures:
        first_staff = root.find(".//Staff")
        if first_staff is not None:
            return len(first_staff.findall("Measure"))
        return len(mscx_measures)

    return 0


def count_notes(tree: ET.ElementTree) -> int:
    """Count the number of notes in a score."""
    root = tree.getroot()

    # MusicXML
    notes = root.findall(".//{*}note")
    if notes:
        return len(notes)

    # MSCX
    return len(root.findall(".//Note"))


def detect_format(path: str) -> str:
    """Detect score file format from extension.

    Returns:
        One of: "mscz", "mxl", "musicxml", "mid", "unknown"
    """
    ext = Path(path).suffix.lower()
    return {
        ".mscz": "mscz",
        ".mxl": "mxl",
        ".musicxml": "musicxml",
        ".xml": "musicxml",
        ".mid": "mid",
        ".midi": "mid",
    }.get(ext, "unknown")
