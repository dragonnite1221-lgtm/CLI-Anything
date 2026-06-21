# ruff: noqa: F403, F405, E501
from .scene_base import *  # noqa: F403

# fmt: off
from .scene_p5 import _flatten_objects, load_scene  # noqa: E402,E501
from .scene_p11 import _resolve_component_type  # noqa: E402,E501
# fmt: on


def _object_has_component(obj: Dict[str, Any], component_type: str) -> bool:
    """Check whether obj has any component matching component_type (exact match)."""
    for comp in obj.get("Components", []):
        if comp.get("__type") == component_type:
            return True
    return False


def _object_has_tag(obj: Dict[str, Any], tag: str) -> bool:
    """Check whether the object's Tags string contains *tag* as a token."""
    raw = obj.get("Tags", "")
    if not raw:
        return False
    tokens = [t.strip() for t in raw.split(",")]
    return tag in tokens


def _parse_position_bounds(
    bounds: str,
) -> "tuple[tuple[float,float,float], tuple[float,float,float]]":
    """Parse a bounds string ``"x_min,y_min,z_min,x_max,y_max,z_max"`` into two tuples."""
    parts = [p.strip() for p in bounds.split(",")]
    if len(parts) != 6:
        raise ValueError(
            "bounds must be 6 comma-separated numbers: x_min,y_min,z_min,x_max,y_max,z_max"
        )
    nums = tuple(float(p) for p in parts)
    return nums[:3], nums[3:]


def _object_in_bounds(obj: Dict[str, Any], bounds: str) -> bool:
    """Check whether obj.Position lies inside the given AABB bounds string."""
    pos_str = obj.get("Position", "0,0,0")
    try:
        pos = tuple(float(p.strip()) for p in pos_str.split(","))
    except (ValueError, AttributeError):
        return False
    if len(pos) != 3:
        return False
    lo, hi = _parse_position_bounds(bounds)
    return all(lo[i] <= pos[i] <= hi[i] for i in range(3))


def query_objects(
    scene_path: str,
    has_component: Optional[str] = None,
    has_tag: Optional[str] = None,
    name_match: Optional[str] = None,
    name_regex: Optional[str] = None,
    in_bounds: Optional[str] = None,
    enabled: Optional[bool] = None,
) -> List[Dict[str, Any]]:
    """Find GameObjects matching the given criteria.

    All provided filters are AND-combined. Searches all objects (top-level and
    nested children).  Component filter accepts either a preset key (e.g.
    ``"rigidbody"``) or a fully qualified type (e.g. ``"Sandbox.Rigidbody"``).

    Args:
        scene_path: Path to the .scene file.
        has_component: Match objects that have at least one component of this type.
        has_tag: Match objects whose Tags include this tag.
        name_match: Substring match on Name.
        name_regex: Regex pattern match on Name.
        in_bounds: AABB filter "x_min,y_min,z_min,x_max,y_max,z_max" on Position.
        enabled: If set, match only objects with this Enabled value.

    Returns:
        List of dicts with guid, name, position, tags, component_types.
    """
    import re

    data = load_scene(scene_path)
    flat = _flatten_objects(data.get("GameObjects", []))

    resolved_component = (
        _resolve_component_type(has_component) if has_component else None
    )
    compiled_regex = re.compile(name_regex) if name_regex else None

    results: List[Dict[str, Any]] = []
    for obj in flat:
        if resolved_component and not _object_has_component(obj, resolved_component):
            continue
        if has_tag and not _object_has_tag(obj, has_tag):
            continue
        if name_match and name_match not in obj.get("Name", ""):
            continue
        if compiled_regex and not compiled_regex.search(obj.get("Name", "")):
            continue
        if in_bounds and not _object_in_bounds(obj, in_bounds):
            continue
        if enabled is not None and obj.get("Enabled", True) != enabled:
            continue

        comp_types = [
            c.get("__type", "") for c in obj.get("Components", []) if c.get("__type")
        ]
        results.append(
            {
                "guid": obj.get("__guid", ""),
                "name": obj.get("Name", ""),
                "position": obj.get("Position", "0,0,0"),
                "tags": obj.get("Tags", ""),
                "component_types": comp_types,
            }
        )

    return results
