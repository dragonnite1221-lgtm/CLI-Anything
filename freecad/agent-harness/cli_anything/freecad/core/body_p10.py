# ruff: noqa: F403, F405, E501
from .body_base import *  # noqa: F403

# fmt: off
from .body_p1 import _get_body, _next_feature_id, _validate_project, _validate_sketch_index  # noqa: E402,E501
# fmt: on


def subtractive_pipe(
    project: Dict[str, Any],
    body_index: int,
    profile_sketch_index: int,
    path_sketch_index: int,
) -> Dict[str, Any]:
    """Add a subtractive pipe (sweep cut) feature along a path sketch.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    profile_sketch_index:
        Index of the sketch defining the cut profile.
    path_sketch_index:
        Index of the sketch defining the sweep path.

    Returns
    -------
    Dict[str, Any]
        The newly created subtractive pipe feature dictionary.
    """
    _validate_project(project)
    body = _get_body(project, body_index)

    if not body["features"]:
        raise ValueError(
            "Cannot add subtractive pipe to a body with no existing features"
        )

    profile = _validate_sketch_index(project, profile_sketch_index)
    path = _validate_sketch_index(project, path_sketch_index)

    feature: Dict[str, Any] = {
        "id": _next_feature_id(body),
        "type": "subtractive_pipe",
        "profile_sketch_index": profile_sketch_index,
        "profile_sketch_name": profile.get("name", f"Sketch {profile_sketch_index}"),
        "path_sketch_index": path_sketch_index,
        "path_sketch_name": path.get("name", f"Sketch {path_sketch_index}"),
    }

    body["features"].append(feature)
    return feature


def subtractive_helix(
    project: Dict[str, Any],
    body_index: int,
    sketch_index: int,
    pitch: float = 5.0,
    height: float = 20.0,
    turns: Optional[float] = None,
) -> Dict[str, Any]:
    """Add a subtractive helix feature.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    sketch_index:
        Index of the sketch to extrude along the helix as a cut.
    pitch:
        Distance between helix turns.  Must be positive.
    height:
        Total helix height.  Must be positive.
    turns:
        Number of turns.  If provided, overrides height.

    Returns
    -------
    Dict[str, Any]
        The newly created subtractive helix feature dictionary.
    """
    _validate_project(project)
    body = _get_body(project, body_index)
    sketch = _validate_sketch_index(project, sketch_index)

    if not body["features"]:
        raise ValueError(
            "Cannot add subtractive helix to a body with no existing features"
        )

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

    feature: Dict[str, Any] = {
        "id": _next_feature_id(body),
        "type": "subtractive_helix",
        "sketch_index": sketch_index,
        "sketch_name": sketch.get("name", f"Sketch {sketch_index}"),
        "pitch": pitch,
        "height": height,
        "turns": turns,
    }

    body["features"].append(feature)
    return feature
