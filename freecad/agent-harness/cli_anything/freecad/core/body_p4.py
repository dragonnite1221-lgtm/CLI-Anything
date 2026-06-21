# ruff: noqa: F403, F405, E501
from .body_base import *  # noqa: F403

# fmt: off
from .body_p1 import _get_body, _next_feature_id, _validate_project, _validate_sketch_index  # noqa: E402,E501
# fmt: on


def revolution(
    project: Dict[str, Any],
    body_index: int,
    sketch_index: int,
    angle: float = 360.0,
    axis: str = "Z",
    reversed: bool = False,
) -> Dict[str, Any]:
    """Add a revolution feature to a body based on a sketch.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    sketch_index:
        Index of the sketch to revolve.
    angle:
        Revolution angle in degrees (0 exclusive, 360 inclusive).
    axis:
        Revolution axis: ``"X"``, ``"Y"``, or ``"Z"``.
    reversed:
        If ``True``, revolve in the opposite direction.

    Returns
    -------
    Dict[str, Any]
        The newly created revolution feature dictionary.
    """
    _validate_project(project)
    body = _get_body(project, body_index)
    sketch = _validate_sketch_index(project, sketch_index)

    angle = float(angle)
    if angle <= 0 or angle > 360:
        raise ValueError(f"Revolution angle must be in (0, 360], got {angle}")

    axis = axis.upper()
    if axis not in VALID_REVOLUTION_AXES:
        raise ValueError(
            f"Invalid revolution axis '{axis}'. Must be one of: {', '.join(sorted(VALID_REVOLUTION_AXES))}"
        )

    # Set base sketch if this is the first feature
    if body["base_sketch_index"] is None:
        body["base_sketch_index"] = sketch_index

    feature: Dict[str, Any] = {
        "id": _next_feature_id(body),
        "type": "revolution",
        "sketch_index": sketch_index,
        "sketch_name": sketch.get("name", f"Sketch {sketch_index}"),
        "angle": angle,
        "axis": axis,
        "reversed": bool(reversed),
    }

    body["features"].append(feature)
    return feature


def list_bodies(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return a summary list of all bodies in the project.

    Parameters
    ----------
    project:
        The project dictionary.

    Returns
    -------
    List[Dict[str, Any]]
        List of body summaries with index, id, name, feature count,
        and base sketch index.
    """
    _validate_project(project)

    result: List[Dict[str, Any]] = []
    for i, body in enumerate(project["bodies"]):
        result.append(
            {
                "index": i,
                "id": body.get("id", i),
                "name": body.get("name", f"Body {i}"),
                "feature_count": len(body.get("features", [])),
                "base_sketch_index": body.get("base_sketch_index"),
            }
        )
    return result


def get_body(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Return the full body dictionary at the given index.

    Parameters
    ----------
    project:
        The project dictionary.
    index:
        Body index.

    Returns
    -------
    Dict[str, Any]
        The complete body dictionary.
    """
    _validate_project(project)
    return _get_body(project, index)
