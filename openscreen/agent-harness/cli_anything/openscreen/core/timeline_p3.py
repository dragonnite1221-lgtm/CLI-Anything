# ruff: noqa: F403, F405, E501
from .timeline_base import *  # noqa: F403


def update_annotation(session: Session, region_id: str, **kwargs) -> dict:
    """Update fields on an existing annotation region.

    Supported kwargs: start_ms, end_ms, text_content, position_x, position_y,
    size, color, background_color, font_size, font_family.

    Args:
        session: Active Session instance.
        region_id: ID of the annotation to update.
        **kwargs: Fields to update (see above).

    Returns:
        The updated region dict.

    Raises:
        RuntimeError: If no project is open.
        ValueError: If region_id is not found.
    """
    if not session.is_open:
        raise RuntimeError("No project is open")
    regions = session.editor.get("annotationRegions", [])
    region = next((r for r in regions if r.get("id") == region_id), None)
    if region is None:
        raise ValueError(f"Annotation not found: {region_id}")

    session.checkpoint()

    if "start_ms" in kwargs:
        region["startMs"] = int(kwargs["start_ms"])
    if "end_ms" in kwargs:
        region["endMs"] = int(kwargs["end_ms"])
    if "text_content" in kwargs:
        region["textContent"] = str(kwargs["text_content"])
        region["content"] = str(kwargs["text_content"])
    if "position_x" in kwargs:
        region["position"]["x"] = float(kwargs["position_x"])
    if "position_y" in kwargs:
        region["position"]["y"] = float(kwargs["position_y"])
    if "size" in kwargs:
        region["size"] = kwargs["size"]
    if "color" in kwargs:
        region["style"]["color"] = str(kwargs["color"])
    if "background_color" in kwargs:
        region["style"]["backgroundColor"] = str(kwargs["background_color"])
    if "font_size" in kwargs:
        region["style"]["fontSize"] = int(kwargs["font_size"])
    if "font_family" in kwargs:
        region["style"]["fontFamily"] = str(kwargs["font_family"])

    return region


def get_timeline_boundaries(session: Session) -> list[int]:
    """Return a sorted list of all unique time boundary points (in ms).

    Includes 0 and all startMs/endMs values from zoom, speed, trim, and
    annotation regions. Useful for computing rendering segments.

    Args:
        session: Active Session instance.

    Returns:
        Sorted list of unique boundary millisecond values.

    Raises:
        RuntimeError: If no project is open.
    """
    if not session.is_open:
        raise RuntimeError("No project is open")
    ed = session.editor
    boundaries = {0}
    for region_key in (
        "zoomRegions",
        "speedRegions",
        "trimRegions",
        "annotationRegions",
    ):
        for region in ed.get(region_key, []):
            boundaries.add(region.get("startMs", 0))
            boundaries.add(region.get("endMs", 0))
    return sorted(boundaries)


def get_active_regions_at(session: Session, time_ms: int) -> dict:
    """Return all regions active at a specific time (startMs <= time_ms < endMs).

    Args:
        session: Active Session instance.
        time_ms: Query time in milliseconds.

    Returns:
        Dict with keys "zoom", "speed", "trim", "annotation", each mapping to
        a list of region dicts active at that time.

    Raises:
        RuntimeError: If no project is open.
    """
    if not session.is_open:
        raise RuntimeError("No project is open")
    ed = session.editor

    def active(regions: list) -> list:
        return [
            r for r in regions if r.get("startMs", 0) <= time_ms < r.get("endMs", 0)
        ]

    return {
        "zoom": active(ed.get("zoomRegions", [])),
        "speed": active(ed.get("speedRegions", [])),
        "trim": active(ed.get("trimRegions", [])),
        "annotation": active(ed.get("annotationRegions", [])),
    }
