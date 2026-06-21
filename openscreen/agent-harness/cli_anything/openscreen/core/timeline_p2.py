# ruff: noqa: F403, F405, E501
from .timeline_base import *  # noqa: F403

# fmt: off
from .timeline_p1 import _gen_id, _validate_time_range  # noqa: E402,E501
# fmt: on


def add_text_annotation(
    session: Session,
    start_ms: int,
    end_ms: int,
    text: str,
    x: float = 0.5,
    y: float = 0.5,
    font_size: int = 32,
    color: str = "#ffffff",
    bg_color: str = "#000000",
) -> dict:
    """Add a text annotation to the timeline."""
    if not session.is_open:
        raise RuntimeError("No project is open")
    _validate_time_range(start_ms, end_ms)

    session.checkpoint()
    region = {
        "id": _gen_id("ann"),
        "startMs": start_ms,
        "endMs": end_ms,
        "type": "text",
        "textContent": text,
        "content": text,
        "position": {"x": x, "y": y},
        "size": {"width": 0.3, "height": 0.1},
        "style": {
            "color": color,
            "backgroundColor": bg_color,
            "fontSize": font_size,
            "fontFamily": "Inter",
            "fontWeight": "normal",
            "fontStyle": "normal",
            "textDecoration": "none",
            "textAlign": "center",
        },
        "zIndex": 1,
    }
    session.editor.setdefault("annotationRegions", []).append(region)
    return region


def remove_annotation(session: Session, region_id: str) -> dict:
    """Remove an annotation by ID."""
    if not session.is_open:
        raise RuntimeError("No project is open")
    session.checkpoint()
    regions = session.editor.get("annotationRegions", [])
    before = len(regions)
    session.editor["annotationRegions"] = [r for r in regions if r["id"] != region_id]
    if before - len(session.editor["annotationRegions"]) == 0:
        raise ValueError(f"Annotation not found: {region_id}")
    return {"status": "removed", "id": region_id}


def update_zoom_region(
    session: Session,
    region_id: str,
    start_ms: Optional[int] = None,
    end_ms: Optional[int] = None,
    depth: Optional[int] = None,
    focus_x: Optional[float] = None,
    focus_y: Optional[float] = None,
) -> dict:
    """Update an existing zoom region.

    Only the keyword arguments that are provided are changed; omitted arguments
    leave the corresponding field unchanged.

    Args:
        session: Active Session instance.
        region_id: ID of the zoom region to update.
        start_ms: New start time in milliseconds.
        end_ms: New end time in milliseconds.
        depth: New zoom depth (1-6).
        focus_x: New horizontal focus center (0.0-1.0).
        focus_y: New vertical focus center (0.0-1.0).

    Returns:
        The updated region dict.

    Raises:
        RuntimeError: If no project is open.
        ValueError: If region_id is not found or parameters are invalid.
    """
    if not session.is_open:
        raise RuntimeError("No project is open")
    regions = session.editor.get("zoomRegions", [])
    region = next((r for r in regions if r.get("id") == region_id), None)
    if region is None:
        raise ValueError(f"Zoom region not found: {region_id}")

    new_start = start_ms if start_ms is not None else region["startMs"]
    new_end = end_ms if end_ms is not None else region["endMs"]
    _validate_time_range(new_start, new_end)

    new_depth = depth if depth is not None else region["depth"]
    if new_depth not in ZOOM_DEPTHS:
        raise ValueError(
            f"Invalid depth {new_depth}. Valid: {list(ZOOM_DEPTHS.keys())}"
        )

    new_fx = focus_x if focus_x is not None else region["focus"]["cx"]
    new_fy = focus_y if focus_y is not None else region["focus"]["cy"]
    if not 0 <= new_fx <= 1 or not 0 <= new_fy <= 1:
        raise ValueError("Focus coordinates must be 0.0-1.0")

    session.checkpoint()
    region["startMs"] = new_start
    region["endMs"] = new_end
    region["depth"] = new_depth
    region["focus"]["cx"] = new_fx
    region["focus"]["cy"] = new_fy
    return region
