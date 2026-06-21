# ruff: noqa: F403, F405, E501
from .draft_base import *  # noqa: F403


def _next_id(project: Dict[str, Any]) -> int:
    """Return the next available integer ID for draft objects."""
    items = project.get("draft_objects", [])
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


def _unique_name(project: Dict[str, Any], base: str) -> str:
    """Return a unique name derived from *base* inside ``project["draft_objects"]``."""
    existing = {item["name"] for item in project.get("draft_objects", [])}
    if base not in existing:
        return base
    counter = 2
    while f"{base}_{counter}" in existing:
        counter += 1
    return f"{base}_{counter}"


def _validate_vec3(value: Any, label: str) -> List[float]:
    """Validate that *value* is a list of exactly three numbers."""
    if not isinstance(value, (list, tuple)):
        raise ValueError(
            f"{label} must be a list of 3 numbers, got {type(value).__name__}"
        )
    if len(value) != 3:
        raise ValueError(f"{label} must have exactly 3 elements, got {len(value)}")
    try:
        return [float(v) for v in value]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} elements must be numeric: {exc}") from exc


def _validate_vec2(value: Any, label: str) -> List[float]:
    """Validate that *value* is a list of exactly two numbers."""
    if not isinstance(value, (list, tuple)):
        raise ValueError(
            f"{label} must be a list of 2 numbers, got {type(value).__name__}"
        )
    if len(value) != 2:
        raise ValueError(f"{label} must have exactly 2 elements, got {len(value)}")
    try:
        return [float(v) for v in value]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} elements must be numeric: {exc}") from exc


def _get_draft(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Return the draft object at *index*, raising ``IndexError`` if out of range."""
    objs = project.get("draft_objects", [])
    if not isinstance(index, int) or index < 0 or index >= len(objs):
        raise IndexError(
            f"Draft object index {index} out of range (0..{len(objs) - 1})"
        )
    return objs[index]


def _make_draft(
    project: Dict[str, Any],
    obj_type: str,
    name: Optional[str],
    properties: Dict[str, Any],
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Create a draft object, append it, and return it."""
    objs = ensure_collection(project, "draft_objects")

    if name is None:
        name = _unique_name(project, obj_type.capitalize())

    pos = (
        _validate_vec3(position, "position")
        if position is not None
        else [0.0, 0.0, 0.0]
    )
    rot = (
        _validate_vec3(rotation, "rotation")
        if rotation is not None
        else [0.0, 0.0, 0.0]
    )

    draft_obj: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "type": obj_type,
        "properties": properties,
        "placement": {
            "position": pos,
            "rotation": rot,
        },
        "visible": True,
    }

    objs.append(draft_obj)
    return draft_obj


def draft_wire(
    project: Dict[str, Any],
    points: List[List[float]],
    closed: bool = False,
    name: Optional[str] = None,
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Create a polyline (wire) from a list of 3D points.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    points : list[list[float]]
        Ordered list of ``[x, y, z]`` vertices.
    closed : bool
        Whether to close the wire (default ``False``).
    name : str or None
        Label for the object.
    position, rotation : list[float] or None
        Placement overrides.

    Returns
    -------
    dict
        The newly created draft object.
    """
    if not isinstance(points, (list, tuple)) or len(points) < 2:
        raise ValueError("wire requires at least 2 points")
    validated = [_validate_vec3(p, f"points[{i}]") for i, p in enumerate(points)]
    return _make_draft(
        project,
        "wire",
        name,
        {
            "points": validated,
            "closed": bool(closed),
        },
        position,
        rotation,
    )
