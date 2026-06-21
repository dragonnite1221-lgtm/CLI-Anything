# ruff: noqa: F403, F405, E501
from .body_base import *  # noqa: F403

# fmt: off
from .body_p1 import _get_body, _next_feature_id, _validate_project  # noqa: E402,E501
# fmt: on


def polar_pattern(
    project: Dict[str, Any],
    body_index: int,
    axis: str = "Z",
    angle: float = 360.0,
    occurrences: int = 6,
) -> Dict[str, Any]:
    """Add a polar (circular) pattern feature to a body.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    axis:
        Rotation axis: ``"X"``, ``"Y"``, or ``"Z"``.
    angle:
        Total angular span in degrees.  Must be in (0, 360].
    occurrences:
        Number of occurrences (including the original).  Must be >= 2.

    Returns
    -------
    Dict[str, Any]
        The newly created polar pattern feature dictionary.
    """
    _validate_project(project)
    body = _get_body(project, body_index)

    if not body["features"]:
        raise ValueError("Cannot add polar pattern to a body with no existing features")

    axis = axis.upper()
    if axis not in VALID_REVOLUTION_AXES:
        raise ValueError(
            f"Invalid axis '{axis}'. Must be one of: {', '.join(sorted(VALID_REVOLUTION_AXES))}"
        )

    angle = float(angle)
    if angle <= 0 or angle > 360:
        raise ValueError(f"Pattern angle must be in (0, 360], got {angle}")

    occurrences = int(occurrences)
    if occurrences < 2:
        raise ValueError(f"Occurrences must be at least 2, got {occurrences}")

    feature: Dict[str, Any] = {
        "id": _next_feature_id(body),
        "type": "polar_pattern",
        "axis": axis,
        "angle": angle,
        "occurrences": occurrences,
    }

    body["features"].append(feature)
    return feature


def mirrored_feature(
    project: Dict[str, Any],
    body_index: int,
    plane: str = "XY",
) -> Dict[str, Any]:
    """Add a mirrored feature to a body.

    Mirrors the last feature across the specified plane.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    plane:
        Mirror plane: ``"XY"``, ``"XZ"``, or ``"YZ"``.

    Returns
    -------
    Dict[str, Any]
        The newly created mirrored feature dictionary.
    """
    _validate_project(project)
    body = _get_body(project, body_index)

    if not body["features"]:
        raise ValueError("Cannot add mirror to a body with no existing features")

    plane = plane.upper()
    if plane not in VALID_PATTERN_PLANES:
        raise ValueError(
            f"Invalid mirror plane '{plane}'. Must be one of: {', '.join(sorted(VALID_PATTERN_PLANES))}"
        )

    feature: Dict[str, Any] = {
        "id": _next_feature_id(body),
        "type": "mirrored",
        "plane": plane,
    }

    body["features"].append(feature)
    return feature
