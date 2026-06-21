# ruff: noqa: F403, F405, E501
from .body_base import *  # noqa: F403

# fmt: off
from .body_p6 import _additive_primitive  # noqa: E402,E501
# fmt: on


def additive_torus(
    project: Dict[str, Any],
    body_index: int,
    radius1: float = 10.0,
    radius2: float = 2.0,
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Add an additive torus primitive to a body.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    radius1:
        Major radius (center of tube to center of torus).  Must be positive.
    radius2:
        Minor radius (tube radius).  Must be positive.

    Returns
    -------
    Dict[str, Any]
        The newly created additive torus feature dictionary.
    """
    radius1, radius2 = float(radius1), float(radius2)
    if radius1 <= 0:
        raise ValueError(f"Torus major radius must be positive, got {radius1}")
    if radius2 <= 0:
        raise ValueError(f"Torus minor radius must be positive, got {radius2}")
    return _additive_primitive(
        project,
        body_index,
        "torus",
        {"radius1": radius1, "radius2": radius2},
        position=position,
        rotation=rotation,
    )


def additive_wedge(
    project: Dict[str, Any],
    body_index: int,
    xmin: float = 0.0,
    xmax: float = 10.0,
    ymin: float = 0.0,
    ymax: float = 10.0,
    zmin: float = 0.0,
    zmax: float = 10.0,
    x2min: float = 2.0,
    x2max: float = 8.0,
    z2min: float = 2.0,
    z2max: float = 8.0,
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Add an additive wedge primitive to a body.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    xmin, xmax, ymin, ymax, zmin, zmax:
        Bounding box extents.
    x2min, x2max, z2min, z2max:
        Top face extents (for the tapered wedge shape).

    Returns
    -------
    Dict[str, Any]
        The newly created additive wedge feature dictionary.
    """
    return _additive_primitive(
        project,
        body_index,
        "wedge",
        {
            "xmin": float(xmin),
            "xmax": float(xmax),
            "ymin": float(ymin),
            "ymax": float(ymax),
            "zmin": float(zmin),
            "zmax": float(zmax),
            "x2min": float(x2min),
            "x2max": float(x2max),
            "z2min": float(z2min),
            "z2max": float(z2max),
        },
        position=position,
        rotation=rotation,
    )
