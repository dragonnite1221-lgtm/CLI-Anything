# ruff: noqa: F403, F405, E501
from .techdraw_base import *  # noqa: F403

# fmt: off
from .techdraw_p1 import _get_page, _validate_vec2, _validate_vec3  # noqa: E402,E501
# fmt: on


def add_view(
    project: Dict[str, Any],
    page_index: int,
    source_index: int,
    direction: Optional[List[float]] = None,
    scale: float = 1.0,
    position: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Add a standard view of a part/body to a TechDraw page.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    page_index : int
        Index of the target page.
    source_index : int
        Index of the source object in ``project["parts"]``.
    direction : list[float] or None
        View projection direction ``[x, y, z]``. Defaults to ``[0, 0, 1]``.
    scale : float
        View scale factor.
    position : list[float] or None
        Position on the page ``[x, y]``. Defaults to ``[0, 0]``.

    Returns
    -------
    dict
        The newly created view entry.
    """
    page = _get_page(project, page_index)

    if direction is not None:
        direction = _validate_vec3(direction, "direction")
    else:
        direction = [0.0, 0.0, 1.0]

    if position is not None:
        position = _validate_vec2(position, "position")
    else:
        position = [0.0, 0.0]

    view: Dict[str, Any] = {
        "type": "standard",
        "source_index": source_index,
        "direction": direction,
        "scale": float(scale),
        "position": position,
    }

    page["views"].append(view)
    return view


def add_projection_group(
    project: Dict[str, Any],
    page_index: int,
    source_index: int,
    directions: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Add a projection group (front, right, top, etc.) to a page.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    page_index : int
        Index of the target page.
    source_index : int
        Index of the source object in ``project["parts"]``.
    directions : list[str] or None
        Projection names. Defaults to ``["front", "right", "top"]``.

    Returns
    -------
    dict
        The projection group view entry.
    """
    page = _get_page(project, page_index)

    if directions is None:
        directions = ["front", "right", "top"]

    group: Dict[str, Any] = {
        "type": "projection_group",
        "source_index": source_index,
        "directions": list(directions),
        "scale": 1.0,
        "position": [0.0, 0.0],
    }

    page["views"].append(group)
    return group
