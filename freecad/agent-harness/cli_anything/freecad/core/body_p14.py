# ruff: noqa: F403, F405, E501
from .body_base import *  # noqa: F403

# fmt: off
from .body_p1 import _get_body, _next_feature_id, _validate_project  # noqa: E402,E501
# fmt: on


def thickness_feature(
    project: Dict[str, Any],
    body_index: int,
    thickness: float,
    faces: Union[str, List[int]] = "all",
    join: str = "arc",
) -> Dict[str, Any]:
    """Add a thickness (shell) feature to a body.

    Hollows out the solid, leaving walls of the specified thickness.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    thickness:
        Wall thickness.  Must be positive.
    faces:
        ``"all"`` to shell all faces, or a list of face indices to
        remove (open faces).
    join:
        Join type for corners: ``"arc"``, ``"tangent"``, or
        ``"intersection"``.

    Returns
    -------
    Dict[str, Any]
        The newly created thickness feature dictionary.
    """
    _validate_project(project)
    body = _get_body(project, body_index)

    if not body["features"]:
        raise ValueError("Cannot add thickness to a body with no existing features")

    thickness = float(thickness)
    if thickness <= 0:
        raise ValueError(f"Thickness must be positive, got {thickness}")

    valid_joins = {"arc", "tangent", "intersection"}
    join = join.lower()
    if join not in valid_joins:
        raise ValueError(
            f"Invalid join type '{join}'. Must be one of: {', '.join(sorted(valid_joins))}"
        )

    if faces != "all":
        if not isinstance(faces, (list, tuple)):
            raise ValueError("Faces must be 'all' or a list of face indices")
        faces = list(faces)

    feature: Dict[str, Any] = {
        "id": _next_feature_id(body),
        "type": "thickness",
        "thickness": thickness,
        "faces": faces,
        "join": join,
    }

    body["features"].append(feature)
    return feature


def linear_pattern(
    project: Dict[str, Any],
    body_index: int,
    direction: Optional[List[float]] = None,
    length: float = 50.0,
    occurrences: int = 3,
) -> Dict[str, Any]:
    """Add a linear pattern feature to a body.

    Repeats the last feature along a direction.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    direction:
        Pattern direction vector ``[x, y, z]``.  Defaults to ``[1, 0, 0]``.
    length:
        Total pattern length.  Must be positive.
    occurrences:
        Number of occurrences (including the original).  Must be >= 2.

    Returns
    -------
    Dict[str, Any]
        The newly created linear pattern feature dictionary.
    """
    _validate_project(project)
    body = _get_body(project, body_index)

    if not body["features"]:
        raise ValueError(
            "Cannot add linear pattern to a body with no existing features"
        )

    if direction is None:
        direction = [1, 0, 0]
    if not isinstance(direction, (list, tuple)) or len(direction) != 3:
        raise ValueError("Direction must be a list of 3 numbers")
    direction = [float(v) for v in direction]

    length = float(length)
    if length <= 0:
        raise ValueError(f"Pattern length must be positive, got {length}")

    occurrences = int(occurrences)
    if occurrences < 2:
        raise ValueError(f"Occurrences must be at least 2, got {occurrences}")

    feature: Dict[str, Any] = {
        "id": _next_feature_id(body),
        "type": "linear_pattern",
        "direction": direction,
        "length": length,
        "occurrences": occurrences,
    }

    body["features"].append(feature)
    return feature
