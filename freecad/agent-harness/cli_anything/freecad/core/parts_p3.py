# ruff: noqa: F403, F405, E501
from .parts_base import *  # noqa: F403

# fmt: off
from .parts_p1 import _next_id, _unique_name, _validate_vec3  # noqa: E402,E501
# fmt: on


def add_part(
    project: Dict[str, Any],
    part_type: str = "box",
    name: Optional[str] = None,
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
    params: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Create a new primitive part and append it to ``project["parts"]``.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary. Must contain a ``"parts"``
        list (created automatically if missing).
    part_type : str
        One of the keys in :data:`PRIMITIVES`.
    name : str or None
        Human-readable label. When *None* a unique name is derived from
        *part_type* (e.g. ``"Box"``, ``"Cylinder_2"``).
    position : list[float] or None
        ``[x, y, z]`` translation. Defaults to ``[0, 0, 0]``.
    rotation : list[float] or None
        ``[x, y, z]`` Euler rotation in degrees. Defaults to ``[0, 0, 0]``.
    params : dict or None
        Parameter overrides merged on top of the primitive defaults.

    Returns
    -------
    dict
        The newly created part dictionary.

    Raises
    ------
    ValueError
        If *part_type* is unknown or vector arguments are invalid.
    """
    # Validate part type
    if part_type not in PRIMITIVES:
        valid = ", ".join(sorted(PRIMITIVES))
        raise ValueError(f"Unknown part_type '{part_type}'. Valid types: {valid}")

    # Ensure the parts list exists
    if "parts" not in project:
        project["parts"] = []

    # Validate / default placement vectors
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

    # Merge parameters
    merged_params = deepcopy(PRIMITIVES[part_type])
    if params:
        unknown = set(params) - set(merged_params)
        if unknown:
            raise ValueError(
                f"Unknown parameter(s) for '{part_type}': {', '.join(sorted(unknown))}. "
                f"Valid: {', '.join(sorted(merged_params))}"
            )
        for k, v in params.items():
            try:
                merged_params[k] = float(v)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Parameter '{k}' must be numeric: {exc}") from exc

    # Build the name
    if name is None:
        base = part_type.capitalize()
        name = _unique_name(project, base)

    part: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "type": part_type,
        "params": merged_params,
        "placement": {
            "position": pos,
            "rotation": rot,
        },
        "material_index": None,
        "visible": True,
    }

    project["parts"].append(part)
    return part


def remove_part(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Remove and return the part at *index* in ``project["parts"]``.

    Raises ``IndexError`` when the index is out of range.
    """
    parts = project.get("parts", [])
    if not isinstance(index, int) or index < 0 or index >= len(parts):
        raise IndexError(f"Part index {index} out of range (0..{len(parts) - 1})")
    return parts.pop(index)


def list_parts(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return all parts in the project."""
    return project.get("parts", [])


def get_part(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Return the part at *index* without removing it.

    Raises ``IndexError`` when the index is out of range.
    """
    parts = project.get("parts", [])
    if not isinstance(index, int) or index < 0 or index >= len(parts):
        raise IndexError(f"Part index {index} out of range (0..{len(parts) - 1})")
    return parts[index]
