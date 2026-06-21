# ruff: noqa: F403, F405, E501
from .body_base import *  # noqa: F403

# fmt: off
from .body_p1 import _get_body, _next_feature_id, _normalize_feature_placement, _validate_project  # noqa: E402,E501
# fmt: on


def _subtractive_primitive(
    project: Dict[str, Any],
    body_index: int,
    primitive_type: str,
    params: Dict[str, Any],
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Internal helper to add a subtractive primitive feature."""
    _validate_project(project)
    body = _get_body(project, body_index)

    if not body["features"]:
        raise ValueError(
            f"Cannot add subtractive {primitive_type} to a body with no existing features"
        )

    feature: Dict[str, Any] = {
        "id": _next_feature_id(body),
        "type": f"subtractive_{primitive_type}",
    }
    feature.update(params)
    placement = _normalize_feature_placement(position=position, rotation=rotation)
    if placement is not None:
        feature["placement"] = placement

    body["features"].append(feature)
    return feature


def subtractive_box(
    project: Dict[str, Any],
    body_index: int,
    length: float = 10.0,
    width: float = 10.0,
    height: float = 10.0,
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Add a subtractive box primitive to a body.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    length:
        Box length (X).  Must be positive.
    width:
        Box width (Y).  Must be positive.
    height:
        Box height (Z).  Must be positive.

    Returns
    -------
    Dict[str, Any]
        The newly created subtractive box feature dictionary.
    """
    length, width, height = float(length), float(width), float(height)
    for name, val in [("length", length), ("width", width), ("height", height)]:
        if val <= 0:
            raise ValueError(f"Box {name} must be positive, got {val}")
    return _subtractive_primitive(
        project,
        body_index,
        "box",
        {"length": length, "width": width, "height": height},
        position=position,
        rotation=rotation,
    )


def subtractive_cylinder(
    project: Dict[str, Any],
    body_index: int,
    radius: float = 5.0,
    height: float = 10.0,
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Add a subtractive cylinder primitive to a body.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    radius:
        Cylinder radius.  Must be positive.
    height:
        Cylinder height.  Must be positive.

    Returns
    -------
    Dict[str, Any]
        The newly created subtractive cylinder feature dictionary.
    """
    radius, height = float(radius), float(height)
    if radius <= 0:
        raise ValueError(f"Cylinder radius must be positive, got {radius}")
    if height <= 0:
        raise ValueError(f"Cylinder height must be positive, got {height}")
    return _subtractive_primitive(
        project,
        body_index,
        "cylinder",
        {"radius": radius, "height": height},
        position=position,
        rotation=rotation,
    )
