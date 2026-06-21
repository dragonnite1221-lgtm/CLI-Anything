# ruff: noqa: F403, F405, E501
from .timeline_base import *  # noqa: F403


def _gen_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _validate_time_range(start_ms: int, end_ms: int) -> None:
    """Validate that start_ms >= 0 and end_ms > start_ms."""
    if start_ms < 0:
        raise ValueError(f"start_ms must be >= 0, got {start_ms}")
    if end_ms <= start_ms:
        raise ValueError(f"end_ms ({end_ms}) must be > start_ms ({start_ms})")


def list_zoom_regions(session: Session) -> list[dict]:
    """List all zoom regions."""
    if not session.is_open:
        raise RuntimeError("No project is open")
    regions = session.editor.get("zoomRegions", [])
    return sorted(regions, key=lambda r: r["startMs"])


def add_zoom_region(
    session: Session,
    start_ms: int,
    end_ms: int,
    depth: int = 3,
    focus_x: float = 0.5,
    focus_y: float = 0.5,
    focus_mode: str = "manual",
) -> dict:
    """Add a zoom region to the timeline."""
    if not session.is_open:
        raise RuntimeError("No project is open")
    if depth not in ZOOM_DEPTHS:
        raise ValueError(f"Invalid depth {depth}. Valid: {list(ZOOM_DEPTHS.keys())}")
    if not 0 <= focus_x <= 1 or not 0 <= focus_y <= 1:
        raise ValueError("Focus coordinates must be 0.0-1.0")
    _validate_time_range(start_ms, end_ms)

    session.checkpoint()
    region = {
        "id": _gen_id("zoom"),
        "startMs": start_ms,
        "endMs": end_ms,
        "depth": depth,
        "focus": {"cx": focus_x, "cy": focus_y},
        "focusMode": focus_mode,
    }
    session.editor.setdefault("zoomRegions", []).append(region)
    return region


def remove_zoom_region(session: Session, region_id: str) -> dict:
    """Remove a zoom region by ID."""
    if not session.is_open:
        raise RuntimeError("No project is open")
    session.checkpoint()
    regions = session.editor.get("zoomRegions", [])
    before = len(regions)
    session.editor["zoomRegions"] = [r for r in regions if r["id"] != region_id]
    removed = before - len(session.editor["zoomRegions"])
    if removed == 0:
        raise ValueError(f"Zoom region not found: {region_id}")
    return {"status": "removed", "id": region_id}


def list_speed_regions(session: Session) -> list[dict]:
    """List all speed regions."""
    if not session.is_open:
        raise RuntimeError("No project is open")
    regions = session.editor.get("speedRegions", [])
    return sorted(regions, key=lambda r: r["startMs"])


def add_speed_region(
    session: Session,
    start_ms: int,
    end_ms: int,
    speed: float = 1.5,
) -> dict:
    """Add a speed region to the timeline."""
    if not session.is_open:
        raise RuntimeError("No project is open")
    if speed not in VALID_SPEEDS:
        raise ValueError(f"Invalid speed {speed}. Valid: {VALID_SPEEDS}")
    _validate_time_range(start_ms, end_ms)

    session.checkpoint()
    region = {
        "id": _gen_id("speed"),
        "startMs": start_ms,
        "endMs": end_ms,
        "speed": speed,
    }
    session.editor.setdefault("speedRegions", []).append(region)
    return region


def remove_speed_region(session: Session, region_id: str) -> dict:
    """Remove a speed region by ID."""
    if not session.is_open:
        raise RuntimeError("No project is open")
    session.checkpoint()
    regions = session.editor.get("speedRegions", [])
    before = len(regions)
    session.editor["speedRegions"] = [r for r in regions if r["id"] != region_id]
    if before - len(session.editor["speedRegions"]) == 0:
        raise ValueError(f"Speed region not found: {region_id}")
    return {"status": "removed", "id": region_id}


def list_trim_regions(session: Session) -> list[dict]:
    """List all trim regions."""
    if not session.is_open:
        raise RuntimeError("No project is open")
    regions = session.editor.get("trimRegions", [])
    return sorted(regions, key=lambda r: r["startMs"])


def add_trim_region(session: Session, start_ms: int, end_ms: int) -> dict:
    """Add a trim (cut) region to the timeline."""
    if not session.is_open:
        raise RuntimeError("No project is open")
    _validate_time_range(start_ms, end_ms)

    session.checkpoint()
    region = {
        "id": _gen_id("trim"),
        "startMs": start_ms,
        "endMs": end_ms,
    }
    session.editor.setdefault("trimRegions", []).append(region)
    return region


def remove_trim_region(session: Session, region_id: str) -> dict:
    """Remove a trim region by ID."""
    if not session.is_open:
        raise RuntimeError("No project is open")
    session.checkpoint()
    regions = session.editor.get("trimRegions", [])
    before = len(regions)
    session.editor["trimRegions"] = [r for r in regions if r["id"] != region_id]
    if before - len(session.editor["trimRegions"]) == 0:
        raise ValueError(f"Trim region not found: {region_id}")
    return {"status": "removed", "id": region_id}


def get_crop(session: Session) -> dict:
    """Get current crop region."""
    if not session.is_open:
        raise RuntimeError("No project is open")
    return session.editor.get("cropRegion", {"x": 0, "y": 0, "width": 1, "height": 1})


def set_crop(session: Session, x: float, y: float, w: float, h: float) -> dict:
    """Set crop region (all values normalized 0-1)."""
    if not session.is_open:
        raise RuntimeError("No project is open")
    for val, name in [(x, "x"), (y, "y"), (w, "width"), (h, "height")]:
        if not 0 <= val <= 1:
            raise ValueError(f"{name} must be 0.0-1.0, got {val}")
    if x + w > 1.001 or y + h > 1.001:
        raise ValueError("Crop region extends beyond frame boundaries")

    session.checkpoint()
    session.editor["cropRegion"] = {"x": x, "y": y, "width": w, "height": h}
    return session.editor["cropRegion"]


def list_annotations(session: Session) -> list[dict]:
    """List all annotation regions."""
    if not session.is_open:
        raise RuntimeError("No project is open")
    regions = session.editor.get("annotationRegions", [])
    return sorted(regions, key=lambda r: r["startMs"])
