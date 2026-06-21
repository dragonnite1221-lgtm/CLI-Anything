# ruff: noqa: F403, F405, E501
from .draft_base import *  # noqa: F403

# fmt: off
from .draft_p1 import _make_draft  # noqa: E402,E501
# fmt: on


def draft_rectangle(
    project: Dict[str, Any],
    length: float = 10.0,
    height: float = 10.0,
    name: Optional[str] = None,
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Create a 2D rectangle.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    length : float
        X-dimension (default ``10``).
    height : float
        Y-dimension (default ``10``).

    Returns
    -------
    dict
        The newly created draft object.
    """
    if length <= 0 or height <= 0:
        raise ValueError("length and height must be positive numbers")
    return _make_draft(
        project,
        "rectangle",
        name,
        {
            "length": float(length),
            "height": float(height),
        },
        position,
        rotation,
    )


def draft_circle(
    project: Dict[str, Any],
    radius: float = 5.0,
    name: Optional[str] = None,
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Create a 2D circle.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    radius : float
        Circle radius (default ``5``).

    Returns
    -------
    dict
        The newly created draft object.
    """
    if radius <= 0:
        raise ValueError("radius must be a positive number")
    return _make_draft(
        project,
        "circle",
        name,
        {
            "radius": float(radius),
        },
        position,
        rotation,
    )


def draft_ellipse(
    project: Dict[str, Any],
    major_radius: float = 10.0,
    minor_radius: float = 5.0,
    name: Optional[str] = None,
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Create a 2D ellipse.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    major_radius : float
        Semi-major axis (default ``10``).
    minor_radius : float
        Semi-minor axis (default ``5``).

    Returns
    -------
    dict
        The newly created draft object.
    """
    if major_radius <= 0 or minor_radius <= 0:
        raise ValueError("major_radius and minor_radius must be positive")
    if minor_radius > major_radius:
        raise ValueError("minor_radius must not exceed major_radius")
    return _make_draft(
        project,
        "ellipse",
        name,
        {
            "major_radius": float(major_radius),
            "minor_radius": float(minor_radius),
        },
        position,
        rotation,
    )
