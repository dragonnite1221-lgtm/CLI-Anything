# ruff: noqa: F403, F405, E501
from .body_base import *  # noqa: F403

# fmt: off
from .body_p1 import _get_body, _next_feature_id, _validate_project, _validate_sketch_index  # noqa: E402,E501
# fmt: on


def groove(
    project: Dict[str, Any],
    body_index: int,
    sketch_index: int,
    angle: float = 360.0,
    axis: str = "Z",
    reversed: bool = False,
) -> Dict[str, Any]:
    """Add a groove (subtractive revolution) feature to a body.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    sketch_index:
        Index of the sketch to revolve as a cut.
    angle:
        Revolution angle in degrees (0 exclusive, 360 inclusive).
    axis:
        Revolution axis: ``"X"``, ``"Y"``, or ``"Z"``.
    reversed:
        If ``True``, revolve in the opposite direction.

    Returns
    -------
    Dict[str, Any]
        The newly created groove feature dictionary.
    """
    _validate_project(project)
    body = _get_body(project, body_index)
    sketch = _validate_sketch_index(project, sketch_index)

    angle = float(angle)
    if angle <= 0 or angle > 360:
        raise ValueError(f"Groove angle must be in (0, 360], got {angle}")

    axis = axis.upper()
    if axis not in VALID_REVOLUTION_AXES:
        raise ValueError(
            f"Invalid groove axis '{axis}'. Must be one of: {', '.join(sorted(VALID_REVOLUTION_AXES))}"
        )

    if not body["features"]:
        raise ValueError("Cannot add groove to a body with no existing features")

    feature: Dict[str, Any] = {
        "id": _next_feature_id(body),
        "type": "groove",
        "sketch_index": sketch_index,
        "sketch_name": sketch.get("name", f"Sketch {sketch_index}"),
        "angle": angle,
        "axis": axis,
        "reversed": bool(reversed),
    }

    body["features"].append(feature)
    return feature


def subtractive_loft(
    project: Dict[str, Any],
    body_index: int,
    sketch_indices: List[int],
    solid: bool = True,
    ruled: bool = False,
) -> Dict[str, Any]:
    """Add a subtractive loft feature between two or more sketches.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    sketch_indices:
        List of sketch indices defining loft cross-sections.  Minimum 2.
    solid:
        If ``True``, create a solid loft cut.
    ruled:
        If ``True``, use ruled surfaces between sections.

    Returns
    -------
    Dict[str, Any]
        The newly created subtractive loft feature dictionary.
    """
    _validate_project(project)
    body = _get_body(project, body_index)

    if not isinstance(sketch_indices, (list, tuple)) or len(sketch_indices) < 2:
        raise ValueError("Loft requires at least 2 sketch indices")

    if not body["features"]:
        raise ValueError(
            "Cannot add subtractive loft to a body with no existing features"
        )

    sketch_names: List[str] = []
    for si in sketch_indices:
        sk = _validate_sketch_index(project, si)
        sketch_names.append(sk.get("name", f"Sketch {si}"))

    feature: Dict[str, Any] = {
        "id": _next_feature_id(body),
        "type": "subtractive_loft",
        "sketch_indices": list(sketch_indices),
        "sketch_names": sketch_names,
        "solid": bool(solid),
        "ruled": bool(ruled),
    }

    body["features"].append(feature)
    return feature
