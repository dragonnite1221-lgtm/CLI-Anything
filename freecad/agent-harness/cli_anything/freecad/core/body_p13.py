# ruff: noqa: F403, F405, E501
from .body_base import *  # noqa: F403

# fmt: off
from .body_p1 import _get_body, _next_feature_id, _validate_project  # noqa: E402,E501
from .body_p11 import _subtractive_primitive  # noqa: E402,E501
# fmt: on


def subtractive_wedge(
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
    """Add a subtractive wedge primitive to a body.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    xmin, xmax, ymin, ymax, zmin, zmax:
        Bounding box extents.
    x2min, x2max, z2min, z2max:
        Top face extents.

    Returns
    -------
    Dict[str, Any]
        The newly created subtractive wedge feature dictionary.
    """
    return _subtractive_primitive(
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


def draft_feature(
    project: Dict[str, Any],
    body_index: int,
    angle: float,
    faces: Union[str, List[int]] = "all",
    pull_direction: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Add a draft (taper) feature to a body.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    angle:
        Draft angle in degrees.  Must be positive.
    faces:
        ``"all"`` to draft every face, or a list of face indices.
    pull_direction:
        Pull direction vector ``[x, y, z]``.  Defaults to ``[0, 0, 1]``.

    Returns
    -------
    Dict[str, Any]
        The newly created draft feature dictionary.
    """
    _validate_project(project)
    body = _get_body(project, body_index)

    if not body["features"]:
        raise ValueError("Cannot add draft to a body with no existing features")

    angle = float(angle)
    if angle <= 0:
        raise ValueError(f"Draft angle must be positive, got {angle}")

    if pull_direction is None:
        pull_direction = [0, 0, 1]
    if not isinstance(pull_direction, (list, tuple)) or len(pull_direction) != 3:
        raise ValueError("pull_direction must be a list of 3 numbers")
    pull_direction = [float(v) for v in pull_direction]

    if faces != "all":
        if not isinstance(faces, (list, tuple)):
            raise ValueError("Faces must be 'all' or a list of face indices")
        faces = list(faces)

    feature: Dict[str, Any] = {
        "id": _next_feature_id(body),
        "type": "draft",
        "angle": angle,
        "faces": faces,
        "pull_direction": pull_direction,
    }

    body["features"].append(feature)
    return feature
