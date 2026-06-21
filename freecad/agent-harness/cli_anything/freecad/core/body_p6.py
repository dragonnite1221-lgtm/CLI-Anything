# ruff: noqa: F403, F405, E501
from .body_base import *  # noqa: F403

# fmt: off
from .body_p1 import _get_body, _next_feature_id, _normalize_feature_placement, _validate_project, _validate_sketch_index  # noqa: E402,E501
# fmt: on


def additive_helix(
    project: Dict[str, Any],
    body_index: int,
    sketch_index: int,
    pitch: float = 5.0,
    height: float = 20.0,
    turns: Optional[float] = None,
) -> Dict[str, Any]:
    """Add a helix extrusion feature.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    sketch_index:
        Index of the sketch to extrude along the helix.
    pitch:
        Distance between helix turns.  Must be positive.
    height:
        Total helix height.  Must be positive.
    turns:
        Number of turns.  If provided, overrides height
        (``height = turns * pitch``).

    Returns
    -------
    Dict[str, Any]
        The newly created additive helix feature dictionary.
    """
    _validate_project(project)
    body = _get_body(project, body_index)
    sketch = _validate_sketch_index(project, sketch_index)

    pitch = float(pitch)
    if pitch <= 0:
        raise ValueError(f"Pitch must be positive, got {pitch}")

    if turns is not None:
        turns = float(turns)
        if turns <= 0:
            raise ValueError(f"Turns must be positive, got {turns}")
        height = turns * pitch
    else:
        height = float(height)
        if height <= 0:
            raise ValueError(f"Height must be positive, got {height}")
        turns = height / pitch

    if body["base_sketch_index"] is None:
        body["base_sketch_index"] = sketch_index

    feature: Dict[str, Any] = {
        "id": _next_feature_id(body),
        "type": "additive_helix",
        "sketch_index": sketch_index,
        "sketch_name": sketch.get("name", f"Sketch {sketch_index}"),
        "pitch": pitch,
        "height": height,
        "turns": turns,
    }

    body["features"].append(feature)
    return feature


def _additive_primitive(
    project: Dict[str, Any],
    body_index: int,
    primitive_type: str,
    params: Dict[str, Any],
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Internal helper to add an additive primitive feature."""
    _validate_project(project)
    body = _get_body(project, body_index)

    feature: Dict[str, Any] = {
        "id": _next_feature_id(body),
        "type": f"additive_{primitive_type}",
    }
    feature.update(params)
    placement = _normalize_feature_placement(position=position, rotation=rotation)
    if placement is not None:
        feature["placement"] = placement

    body["features"].append(feature)
    return feature


def additive_box(
    project: Dict[str, Any],
    body_index: int,
    length: float = 10.0,
    width: float = 10.0,
    height: float = 10.0,
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Add an additive box primitive to a body.

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
        The newly created additive box feature dictionary.
    """
    length, width, height = float(length), float(width), float(height)
    for name, val in [("length", length), ("width", width), ("height", height)]:
        if val <= 0:
            raise ValueError(f"Box {name} must be positive, got {val}")
    return _additive_primitive(
        project,
        body_index,
        "box",
        {"length": length, "width": width, "height": height},
        position=position,
        rotation=rotation,
    )
