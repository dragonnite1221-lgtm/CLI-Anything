# ruff: noqa: F403, F405, E501
from .body_base import *  # noqa: F403

# fmt: off
from .body_p1 import _get_body, _next_feature_id, _validate_project, _validate_sketch_index  # noqa: E402,E501
# fmt: on


def pad(
    project: Dict[str, Any],
    body_index: int,
    sketch_index: int,
    length: float = 10.0,
    symmetric: bool = False,
    reversed: bool = False,
) -> Dict[str, Any]:
    """Add a pad (extrusion) feature to a body based on a sketch.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    sketch_index:
        Index of the sketch to extrude.
    length:
        Extrusion length.  Must be positive.
    symmetric:
        If ``True``, extrude symmetrically in both directions
        (half the length each way).
    reversed:
        If ``True``, extrude in the opposite direction.

    Returns
    -------
    Dict[str, Any]
        The newly created pad feature dictionary.
    """
    _validate_project(project)
    body = _get_body(project, body_index)
    sketch = _validate_sketch_index(project, sketch_index)

    length = float(length)
    if length <= 0:
        raise ValueError(f"Pad length must be positive, got {length}")

    # Set base sketch if this is the first feature
    if body["base_sketch_index"] is None:
        body["base_sketch_index"] = sketch_index

    feature: Dict[str, Any] = {
        "id": _next_feature_id(body),
        "type": "pad",
        "sketch_index": sketch_index,
        "sketch_name": sketch.get("name", f"Sketch {sketch_index}"),
        "length": length,
        "symmetric": bool(symmetric),
        "reversed": bool(reversed),
    }

    body["features"].append(feature)
    return feature


def pocket(
    project: Dict[str, Any],
    body_index: int,
    sketch_index: int,
    length: float = 5.0,
    symmetric: bool = False,
    reversed: bool = False,
) -> Dict[str, Any]:
    """Add a pocket (cut extrusion) feature to a body based on a sketch.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    sketch_index:
        Index of the sketch defining the pocket profile.
    length:
        Cut depth.  Must be positive.
    symmetric:
        If ``True``, cut symmetrically in both directions.
    reversed:
        If ``True``, cut in the opposite direction.

    Returns
    -------
    Dict[str, Any]
        The newly created pocket feature dictionary.
    """
    _validate_project(project)
    body = _get_body(project, body_index)
    sketch = _validate_sketch_index(project, sketch_index)

    length = float(length)
    if length <= 0:
        raise ValueError(f"Pocket length must be positive, got {length}")

    feature: Dict[str, Any] = {
        "id": _next_feature_id(body),
        "type": "pocket",
        "sketch_index": sketch_index,
        "sketch_name": sketch.get("name", f"Sketch {sketch_index}"),
        "length": length,
        "symmetric": bool(symmetric),
        "reversed": bool(reversed),
    }

    body["features"].append(feature)
    return feature
