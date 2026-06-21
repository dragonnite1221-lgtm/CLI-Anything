# ruff: noqa: F403, F405, E501
from .body_base import *  # noqa: F403

# fmt: off
from .body_p1 import _get_body, _next_feature_id, _validate_project, _validate_sketch_index  # noqa: E402,E501
# fmt: on


def additive_loft(
    project: Dict[str, Any],
    body_index: int,
    sketch_indices: List[int],
    solid: bool = True,
    ruled: bool = False,
) -> Dict[str, Any]:
    """Add a loft feature between two or more sketches.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    sketch_indices:
        List of sketch indices defining loft cross-sections.  Minimum 2.
    solid:
        If ``True``, create a solid loft.
    ruled:
        If ``True``, use ruled surfaces between sections.

    Returns
    -------
    Dict[str, Any]
        The newly created additive loft feature dictionary.
    """
    _validate_project(project)
    body = _get_body(project, body_index)

    if not isinstance(sketch_indices, (list, tuple)) or len(sketch_indices) < 2:
        raise ValueError("Loft requires at least 2 sketch indices")

    sketch_names: List[str] = []
    for si in sketch_indices:
        sk = _validate_sketch_index(project, si)
        sketch_names.append(sk.get("name", f"Sketch {si}"))

    if body["base_sketch_index"] is None:
        body["base_sketch_index"] = sketch_indices[0]

    feature: Dict[str, Any] = {
        "id": _next_feature_id(body),
        "type": "additive_loft",
        "sketch_indices": list(sketch_indices),
        "sketch_names": sketch_names,
        "solid": bool(solid),
        "ruled": bool(ruled),
    }

    body["features"].append(feature)
    return feature


def additive_pipe(
    project: Dict[str, Any],
    body_index: int,
    profile_sketch_index: int,
    path_sketch_index: int,
) -> Dict[str, Any]:
    """Add a pipe (sweep) feature along a path sketch.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    profile_sketch_index:
        Index of the sketch defining the sweep profile.
    path_sketch_index:
        Index of the sketch defining the sweep path.

    Returns
    -------
    Dict[str, Any]
        The newly created additive pipe feature dictionary.
    """
    _validate_project(project)
    body = _get_body(project, body_index)

    profile = _validate_sketch_index(project, profile_sketch_index)
    path = _validate_sketch_index(project, path_sketch_index)

    if body["base_sketch_index"] is None:
        body["base_sketch_index"] = profile_sketch_index

    feature: Dict[str, Any] = {
        "id": _next_feature_id(body),
        "type": "additive_pipe",
        "profile_sketch_index": profile_sketch_index,
        "profile_sketch_name": profile.get("name", f"Sketch {profile_sketch_index}"),
        "path_sketch_index": path_sketch_index,
        "path_sketch_name": path.get("name", f"Sketch {path_sketch_index}"),
    }

    body["features"].append(feature)
    return feature
