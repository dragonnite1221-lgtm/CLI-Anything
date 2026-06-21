# ruff: noqa: F403, F405, E501
from .sources_base import *  # noqa: F403

# fmt: off
from .sources_p1 import _get_scene_sources  # noqa: E402,E501
# fmt: on


def transform_source(
    project: Dict[str, Any],
    source_index: int,
    scene_index: int = 0,
    position: Optional[Dict[str, Any]] = None,
    size: Optional[Dict[str, Any]] = None,
    crop: Optional[Dict[str, Any]] = None,
    rotation: Optional[float] = None,
) -> Dict[str, Any]:
    """Transform a source (position, size, crop, rotation)."""
    sources = _get_scene_sources(project, scene_index)
    source = get_item(sources, source_index, "source")

    if position:
        source["position"] = {
            "x": float(position.get("x", source["position"]["x"])),
            "y": float(position.get("y", source["position"]["y"])),
        }
    if size:
        w = int(size.get("width", source["size"]["width"]))
        h = int(size.get("height", source["size"]["height"]))
        if w < 1 or h < 1:
            raise ValueError(f"Size must be positive: {w}x{h}")
        source["size"] = {"width": w, "height": h}
    if crop:
        for key in ("top", "bottom", "left", "right"):
            if key in crop:
                val = int(crop[key])
                if val < 0:
                    raise ValueError(f"Crop {key} must be non-negative, got {val}")
                source["crop"][key] = val
    if rotation is not None:
        source["rotation"] = float(rotation)

    return source


def list_sources(project: Dict[str, Any], scene_index: int = 0) -> List[Dict[str, Any]]:
    """List all sources in a scene."""
    sources = _get_scene_sources(project, scene_index)
    return [
        {
            "index": i,
            "id": s.get("id", i),
            "name": s.get("name", f"Source {i}"),
            "type": s.get("type", "unknown"),
            "visible": s.get("visible", True),
            "locked": s.get("locked", False),
            "position": s.get("position", {"x": 0, "y": 0}),
            "size": s.get("size", {"width": 0, "height": 0}),
        }
        for i, s in enumerate(sources)
    ]


def get_source(
    project: Dict[str, Any], source_index: int, scene_index: int = 0
) -> Dict[str, Any]:
    """Get detailed info about a source."""
    sources = _get_scene_sources(project, scene_index)
    return get_item(sources, source_index, "source")
