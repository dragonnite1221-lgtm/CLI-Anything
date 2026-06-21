# ruff: noqa: F403, F405, E501
from .body_base import *  # noqa: F403

# fmt: off
from .body_p1 import _get_body, _next_feature_id, _validate_project  # noqa: E402,E501
# fmt: on


def datum_plane(
    project: Dict[str, Any],
    body_index: int,
    offset: float = 0.0,
    reference: str = "XY",
    attachment_mode: Optional[str] = None,
    attachment_refs: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Add a datum plane to a body.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    offset:
        Offset distance from the reference plane.
    reference:
        Reference plane: ``"XY"``, ``"XZ"``, or ``"YZ"``.

    Returns
    -------
    Dict[str, Any]
        The newly created datum plane feature dictionary.
    """
    _validate_project(project)
    body = _get_body(project, body_index)

    reference = reference.upper()
    if reference not in VALID_PATTERN_PLANES:
        raise ValueError(
            f"Invalid reference plane '{reference}'. "
            f"Must be one of: {', '.join(sorted(VALID_PATTERN_PLANES))}"
        )

    feature: Dict[str, Any] = {
        "id": _next_feature_id(body),
        "type": "datum_plane",
        "offset": float(offset),
        "reference": reference,
    }

    if attachment_mode is not None:
        if attachment_mode not in VALID_ATTACHMENT_MODES:
            raise ValueError(
                f"Invalid attachment_mode '{attachment_mode}'. Valid: {sorted(VALID_ATTACHMENT_MODES)}"
            )
        feature["attachment_mode"] = attachment_mode
    if attachment_refs is not None:
        feature["attachment_refs"] = attachment_refs

    body["features"].append(feature)
    return feature


def datum_line(
    project: Dict[str, Any],
    body_index: int,
    point: Optional[List[float]] = None,
    direction: Optional[List[float]] = None,
    attachment_mode: Optional[str] = None,
    attachment_refs: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Add a datum line to a body.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    point:
        Base point ``[x, y, z]``.  Defaults to ``[0, 0, 0]``.
    direction:
        Direction vector ``[x, y, z]``.  Defaults to ``[0, 0, 1]``.

    Returns
    -------
    Dict[str, Any]
        The newly created datum line feature dictionary.
    """
    _validate_project(project)
    body = _get_body(project, body_index)

    if point is None:
        point = [0, 0, 0]
    if not isinstance(point, (list, tuple)) or len(point) != 3:
        raise ValueError("Point must be a list of 3 numbers")
    point = [float(v) for v in point]

    if direction is None:
        direction = [0, 0, 1]
    if not isinstance(direction, (list, tuple)) or len(direction) != 3:
        raise ValueError("Direction must be a list of 3 numbers")
    direction = [float(v) for v in direction]

    feature: Dict[str, Any] = {
        "id": _next_feature_id(body),
        "type": "datum_line",
        "point": point,
        "direction": direction,
    }

    if attachment_mode is not None:
        if attachment_mode not in VALID_ATTACHMENT_MODES:
            raise ValueError(
                f"Invalid attachment_mode '{attachment_mode}'. Valid: {sorted(VALID_ATTACHMENT_MODES)}"
            )
        feature["attachment_mode"] = attachment_mode
    if attachment_refs is not None:
        feature["attachment_refs"] = attachment_refs

    body["features"].append(feature)
    return feature
