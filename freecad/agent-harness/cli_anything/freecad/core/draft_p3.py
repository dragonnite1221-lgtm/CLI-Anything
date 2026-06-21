# ruff: noqa: F403, F405, E501
from .draft_base import *  # noqa: F403

# fmt: off
from .draft_p1 import _make_draft, _validate_vec3  # noqa: E402,E501
# fmt: on


def draft_polygon(
    project: Dict[str, Any],
    sides: int = 6,
    radius: float = 5.0,
    name: Optional[str] = None,
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Create a regular polygon.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    sides : int
        Number of sides (default ``6``).  Must be >= 3.
    radius : float
        Circumscribed radius (default ``5``).

    Returns
    -------
    dict
        The newly created draft object.
    """
    if not isinstance(sides, int) or sides < 3:
        raise ValueError("sides must be an integer >= 3")
    if radius <= 0:
        raise ValueError("radius must be a positive number")
    return _make_draft(
        project,
        "polygon",
        name,
        {
            "sides": sides,
            "radius": float(radius),
        },
        position,
        rotation,
    )


def draft_bspline(
    project: Dict[str, Any],
    points: List[List[float]],
    closed: bool = False,
    name: Optional[str] = None,
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Create a B-spline curve through a list of points.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    points : list[list[float]]
        Control / through-points (minimum 2).
    closed : bool
        Whether to close the spline (default ``False``).

    Returns
    -------
    dict
        The newly created draft object.
    """
    if not isinstance(points, (list, tuple)) or len(points) < 2:
        raise ValueError("bspline requires at least 2 points")
    validated = [_validate_vec3(p, f"points[{i}]") for i, p in enumerate(points)]
    return _make_draft(
        project,
        "bspline",
        name,
        {
            "points": validated,
            "closed": bool(closed),
        },
        position,
        rotation,
    )


def draft_bezier(
    project: Dict[str, Any],
    points: List[List[float]],
    name: Optional[str] = None,
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Create a Bezier curve from control points.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    points : list[list[float]]
        Control points (minimum 2).

    Returns
    -------
    dict
        The newly created draft object.
    """
    if not isinstance(points, (list, tuple)) or len(points) < 2:
        raise ValueError("bezier requires at least 2 control points")
    validated = [_validate_vec3(p, f"points[{i}]") for i, p in enumerate(points)]
    return _make_draft(
        project,
        "bezier",
        name,
        {
            "points": validated,
        },
        position,
        rotation,
    )
