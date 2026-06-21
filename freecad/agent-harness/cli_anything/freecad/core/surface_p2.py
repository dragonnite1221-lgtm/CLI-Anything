# ruff: noqa: F403, F405, E501
from .surface_base import *  # noqa: F403

# fmt: off
from .surface_p1 import _get_surface, _next_id, _unique_name  # noqa: E402,E501
# fmt: on


def surface_extend(
    project: Dict[str, Any],
    surface_index: int,
    length: float = 10.0,
    direction: str = "normal",
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Extend an existing surface by *length* along *direction*.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    surface_index : int
        Index of the surface to extend.
    length : float
        Extension distance (default ``10``).
    direction : str
        Extension direction — ``"normal"`` (default), ``"u"``, or ``"v"``.
    name : str or None
        Label for the new surface.  Auto-generated when *None*.

    Returns
    -------
    dict
        The newly created extended surface entry.

    Raises
    ------
    IndexError
        If *surface_index* is out of range.
    ValueError
        If *length* is not positive or *direction* is invalid.
    """
    source = _get_surface(project, surface_index)

    if length <= 0:
        raise ValueError("length must be a positive number")

    valid_dirs = {"normal", "u", "v"}
    if direction not in valid_dirs:
        raise ValueError(
            f"direction must be one of {', '.join(sorted(valid_dirs))}, got '{direction}'"
        )

    surfaces = ensure_collection(project, "surfaces")

    if name is None:
        name = _unique_name(project, f"{source['name']}_Extended")

    surface: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "type": "extend",
        "params": {
            "length": float(length),
            "direction": direction,
            "source_surface_id": source["id"],
        },
        "source_refs": [surface_index],
    }

    surfaces.append(surface)
    return surface


def surface_blend_curve(
    project: Dict[str, Any],
    edge_index1: int,
    edge_index2: int,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a blend surface between two edges.

    The blend surface smoothly connects two boundary edges with
    tangency continuity.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    edge_index1 : int
        Index referencing the first boundary edge.
    edge_index2 : int
        Index referencing the second boundary edge.
    name : str or None
        Label for the surface.  Auto-generated when *None*.

    Returns
    -------
    dict
        The newly created surface entry.

    Raises
    ------
    ValueError
        If edge indices are equal or negative.
    """
    if not isinstance(edge_index1, int) or edge_index1 < 0:
        raise ValueError("edge_index1 must be a non-negative integer")
    if not isinstance(edge_index2, int) or edge_index2 < 0:
        raise ValueError("edge_index2 must be a non-negative integer")
    if edge_index1 == edge_index2:
        raise ValueError("edge_index1 and edge_index2 must differ")

    surfaces = ensure_collection(project, "surfaces")

    if name is None:
        name = _unique_name(project, "BlendCurve")

    surface: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "type": "blend_curve",
        "params": {},
        "source_refs": [edge_index1, edge_index2],
    }

    surfaces.append(surface)
    return surface
