# ruff: noqa: F403, F405, E501
from .body_base import *  # noqa: F403

# fmt: off
from .body_p1 import _get_body, _next_feature_id, _validate_project, _validate_sketch_index  # noqa: E402,E501
# fmt: on


def multi_transform(
    project: Dict[str, Any],
    body_index: int,
    transformations: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Add a multi-transform feature combining multiple pattern operations.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    transformations:
        List of transformation dictionaries, each describing a pattern
        operation (e.g. ``{"type": "linear_pattern", "direction": [1,0,0],
        "length": 50, "occurrences": 3}``).

    Returns
    -------
    Dict[str, Any]
        The newly created multi-transform feature dictionary.
    """
    _validate_project(project)
    body = _get_body(project, body_index)

    if not body["features"]:
        raise ValueError(
            "Cannot add multi-transform to a body with no existing features"
        )

    if not isinstance(transformations, (list, tuple)) or len(transformations) == 0:
        raise ValueError("Transformations must be a non-empty list of pattern dicts")

    feature: Dict[str, Any] = {
        "id": _next_feature_id(body),
        "type": "multi_transform",
        "transformations": list(transformations),
    }

    body["features"].append(feature)
    return feature


def hole_feature(
    project: Dict[str, Any],
    body_index: int,
    sketch_index: int,
    diameter: float = 5.0,
    depth: float = 10.0,
    threaded: bool = False,
    thread_pitch: Optional[float] = None,
    thread_standard: str = "metric",
    tapered: bool = False,
    taper_angle: Optional[float] = None,
) -> Dict[str, Any]:
    """Add a hole feature to a body based on a sketch with point positions.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    sketch_index:
        Index of the sketch containing hole center points.
    diameter:
        Hole diameter.  Must be positive.
    depth:
        Hole depth.  Must be positive.
    threaded:
        If ``True``, create a threaded hole.
    thread_pitch:
        Thread pitch (only used when *threaded* is ``True``).

    Returns
    -------
    Dict[str, Any]
        The newly created hole feature dictionary.
    """
    _validate_project(project)
    body = _get_body(project, body_index)
    sketch = _validate_sketch_index(project, sketch_index)

    if not body["features"]:
        raise ValueError("Cannot add hole to a body with no existing features")

    diameter = float(diameter)
    if diameter <= 0:
        raise ValueError(f"Hole diameter must be positive, got {diameter}")

    depth = float(depth)
    if depth <= 0:
        raise ValueError(f"Hole depth must be positive, got {depth}")

    if thread_standard not in VALID_THREAD_STANDARDS:
        raise ValueError(
            f"Invalid thread_standard '{thread_standard}'. Valid: {sorted(VALID_THREAD_STANDARDS)}"
        )

    if tapered and taper_angle is None:
        if thread_standard == "NPT":
            taper_angle = 1.7899  # ASME B1.20.1
        elif thread_standard == "BSP":
            taper_angle = 1.7899  # ISO 7-1

    feature: Dict[str, Any] = {
        "id": _next_feature_id(body),
        "type": "hole",
        "sketch_index": sketch_index,
        "sketch_name": sketch.get("name", f"Sketch {sketch_index}"),
        "diameter": diameter,
        "depth": depth,
        "threaded": bool(threaded),
        "thread_standard": thread_standard,
        "tapered": bool(tapered),
        "taper_angle": taper_angle,
    }

    if threaded and thread_pitch is not None:
        thread_pitch = float(thread_pitch)
        if thread_pitch <= 0:
            raise ValueError(f"Thread pitch must be positive, got {thread_pitch}")
        feature["thread_pitch"] = thread_pitch

    body["features"].append(feature)
    return feature
