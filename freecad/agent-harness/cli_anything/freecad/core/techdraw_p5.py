# ruff: noqa: F403, F405, E501
from .techdraw_base import *  # noqa: F403

# fmt: off
from .techdraw_p1 import _get_page, _get_view, _validate_vec2  # noqa: E402,E501
# fmt: on


def add_leader(
    project: Dict[str, Any],
    page_index: int,
    points: List[List[float]],
    text: str = "",
) -> Dict[str, Any]:
    """Add a leader line with optional text to a page.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    page_index : int
        Index of the target page.
    points : list[list[float]]
        List of ``[x, y]`` waypoints for the leader line.
    text : str
        Optional text label at the end of the leader.

    Returns
    -------
    dict
        The leader entry.
    """
    page = _get_page(project, page_index)

    validated_points: List[List[float]] = []
    for i, pt in enumerate(points):
        validated_points.append(_validate_vec2(pt, f"points[{i}]"))

    leader: Dict[str, Any] = {
        "type": "leader",
        "points": validated_points,
        "text": str(text),
    }

    page["annotations"].append(leader)
    return leader


def add_centerline(
    project: Dict[str, Any],
    page_index: int,
    view_index: int,
    references: List[Any],
) -> Dict[str, Any]:
    """Add a centerline to a view on a page.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    page_index : int
        Index of the target page.
    view_index : int
        Index of the view within the page.
    references : list
        Geometry references (edges, faces) that define the centerline.

    Returns
    -------
    dict
        The centerline entry.
    """
    page = _get_page(project, page_index)
    _get_view(project, page_index, view_index)

    centerline: Dict[str, Any] = {
        "type": "centerline",
        "view_index": view_index,
        "references": list(references),
    }

    page["annotations"].append(centerline)
    return centerline


def add_hatch(
    project: Dict[str, Any],
    page_index: int,
    view_index: int,
    pattern: str = "steel",
    scale: float = 1.0,
) -> Dict[str, Any]:
    """Add a hatch pattern to a view on a page.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    page_index : int
        Index of the target page.
    view_index : int
        Index of the view within the page.
    pattern : str
        Hatch pattern name (e.g. ``"steel"``, ``"aluminum"``).
    scale : float
        Pattern scale factor.

    Returns
    -------
    dict
        The hatch entry.
    """
    page = _get_page(project, page_index)
    _get_view(project, page_index, view_index)

    hatch: Dict[str, Any] = {
        "type": "hatch",
        "view_index": view_index,
        "pattern": str(pattern),
        "scale": float(scale),
    }

    page["annotations"].append(hatch)
    return hatch
