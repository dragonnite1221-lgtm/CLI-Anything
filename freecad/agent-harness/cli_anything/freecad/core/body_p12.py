# ruff: noqa: F403, F405, E501
from .body_base import *  # noqa: F403

# fmt: off
from .body_p11 import _subtractive_primitive  # noqa: E402,E501
# fmt: on


def subtractive_sphere(
    project: Dict[str, Any],
    body_index: int,
    radius: float = 5.0,
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Add a subtractive sphere primitive to a body.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    radius:
        Sphere radius.  Must be positive.

    Returns
    -------
    Dict[str, Any]
        The newly created subtractive sphere feature dictionary.
    """
    radius = float(radius)
    if radius <= 0:
        raise ValueError(f"Sphere radius must be positive, got {radius}")
    return _subtractive_primitive(
        project,
        body_index,
        "sphere",
        {"radius": radius},
        position=position,
        rotation=rotation,
    )


def subtractive_cone(
    project: Dict[str, Any],
    body_index: int,
    radius1: float = 5.0,
    radius2: float = 0.0,
    height: float = 10.0,
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Add a subtractive cone primitive to a body.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    radius1:
        Bottom radius.  Must be non-negative.
    radius2:
        Top radius.  Must be non-negative.
    height:
        Cone height.  Must be positive.

    Returns
    -------
    Dict[str, Any]
        The newly created subtractive cone feature dictionary.
    """
    radius1, radius2, height = float(radius1), float(radius2), float(height)
    if radius1 < 0:
        raise ValueError(f"Cone radius1 must be non-negative, got {radius1}")
    if radius2 < 0:
        raise ValueError(f"Cone radius2 must be non-negative, got {radius2}")
    if height <= 0:
        raise ValueError(f"Cone height must be positive, got {height}")
    return _subtractive_primitive(
        project,
        body_index,
        "cone",
        {"radius1": radius1, "radius2": radius2, "height": height},
        position=position,
        rotation=rotation,
    )


def subtractive_torus(
    project: Dict[str, Any],
    body_index: int,
    radius1: float = 10.0,
    radius2: float = 2.0,
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Add a subtractive torus primitive to a body.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    radius1:
        Major radius.  Must be positive.
    radius2:
        Minor radius.  Must be positive.

    Returns
    -------
    Dict[str, Any]
        The newly created subtractive torus feature dictionary.
    """
    radius1, radius2 = float(radius1), float(radius2)
    if radius1 <= 0:
        raise ValueError(f"Torus major radius must be positive, got {radius1}")
    if radius2 <= 0:
        raise ValueError(f"Torus minor radius must be positive, got {radius2}")
    return _subtractive_primitive(
        project,
        body_index,
        "torus",
        {"radius1": radius1, "radius2": radius2},
        position=position,
        rotation=rotation,
    )
