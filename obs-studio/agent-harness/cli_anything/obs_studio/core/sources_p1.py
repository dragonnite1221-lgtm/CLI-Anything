# ruff: noqa: F403, F405, E501
from .sources_base import *  # noqa: F403


def _get_scene_sources(
    project: Dict[str, Any], scene_index: int
) -> List[Dict[str, Any]]:
    """Get sources for a scene."""
    scenes = project.get("scenes", [])
    scene = get_item(scenes, scene_index, "scene")
    return scene.setdefault("sources", [])


def _default_source(name: str, source_type: str) -> Dict[str, Any]:
    """Create a default source dict."""
    type_info = SOURCE_TYPES.get(source_type, {})
    default_settings = copy.deepcopy(type_info.get("default_settings", {}))
    return {
        "id": 0,
        "name": name,
        "type": source_type,
        "visible": True,
        "locked": False,
        "position": {"x": 0, "y": 0},
        "size": {"width": 1920, "height": 1080},
        "crop": {"top": 0, "bottom": 0, "left": 0, "right": 0},
        "rotation": 0,
        "opacity": 1.0,
        "filters": [],
        "settings": default_settings,
    }


def add_source(
    project: Dict[str, Any],
    source_type: str,
    scene_index: int = 0,
    name: Optional[str] = None,
    position: Optional[Dict[str, Any]] = None,
    size: Optional[Dict[str, Any]] = None,
    visible: bool = True,
    settings: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Add a source to a scene."""
    if source_type not in SOURCE_TYPES:
        raise ValueError(
            f"Unknown source type: {source_type}. Valid: {', '.join(sorted(SOURCE_TYPES.keys()))}"
        )

    sources = _get_scene_sources(project, scene_index)
    if name is None:
        name = SOURCE_TYPES[source_type]["label"]
    name = unique_name(name, sources)

    src = _default_source(name, source_type)
    src["id"] = generate_id(sources)
    src["visible"] = visible

    if position:
        src["position"] = {
            "x": float(position.get("x", 0)),
            "y": float(position.get("y", 0)),
        }
    if size:
        w = int(size.get("width", 1920))
        h = int(size.get("height", 1080))
        if w < 1 or h < 1:
            raise ValueError(f"Size must be positive: {w}x{h}")
        src["size"] = {"width": w, "height": h}
    if settings:
        src["settings"].update(settings)

    sources.append(src)
    return src


def remove_source(
    project: Dict[str, Any], source_index: int, scene_index: int = 0
) -> Dict[str, Any]:
    """Remove a source from a scene."""
    sources = _get_scene_sources(project, scene_index)
    source = get_item(sources, source_index, "source")
    return sources.pop(source_index)


def duplicate_source(
    project: Dict[str, Any], source_index: int, scene_index: int = 0
) -> Dict[str, Any]:
    """Duplicate a source within a scene."""
    sources = _get_scene_sources(project, scene_index)
    original = get_item(sources, source_index, "source")
    dup = copy.deepcopy(original)
    dup["id"] = generate_id(sources)
    dup["name"] = unique_name(original["name"] + " (Copy)", sources)
    sources.append(dup)
    return dup


def set_source_property(
    project: Dict[str, Any],
    source_index: int,
    prop: str,
    value: Any,
    scene_index: int = 0,
) -> Dict[str, Any]:
    """Set a property on a source."""
    sources = _get_scene_sources(project, scene_index)
    source = get_item(sources, source_index, "source")

    valid_props = ("name", "visible", "locked", "opacity", "rotation")
    if prop not in valid_props:
        raise ValueError(
            f"Unknown source property: {prop}. Valid: {', '.join(valid_props)}"
        )

    if prop == "visible":
        if isinstance(value, str):
            value = value.lower() in ("true", "1", "yes")
        source["visible"] = bool(value)
    elif prop == "locked":
        if isinstance(value, str):
            value = value.lower() in ("true", "1", "yes")
        source["locked"] = bool(value)
    elif prop == "opacity":
        source["opacity"] = validate_range(value, 0.0, 1.0, "Opacity")
    elif prop == "rotation":
        source["rotation"] = float(value)
    elif prop == "name":
        source["name"] = str(value)

    return source
