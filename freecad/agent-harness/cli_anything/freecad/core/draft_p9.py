# ruff: noqa: F403, F405, E501
from .draft_base import *  # noqa: F403

# fmt: off
from .draft_p1 import _get_draft, _make_draft, _next_id, _unique_name, _validate_vec3  # noqa: E402,E501
# fmt: on


def draft_array_polar(
    project: Dict[str, Any],
    index: int,
    count: int = 6,
    angle: float = 360.0,
    center: Optional[List[float]] = None,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a polar (circular) array of a draft object.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    index : int
        Index of the source draft object.
    count : int
        Number of copies (default ``6``).
    angle : float
        Total sweep angle in degrees (default ``360``).
    center : list[float] or None
        Center of the array (default origin).

    Returns
    -------
    dict
        The newly created array draft object.
    """
    obj = _get_draft(project, index)
    if count < 2:
        raise ValueError("count must be >= 2")
    ctr = _validate_vec3(center, "center") if center is not None else [0.0, 0.0, 0.0]
    return _make_draft(
        project,
        "array_polar",
        name,
        {
            "source_id": obj["id"],
            "count": int(count),
            "angle": float(angle),
            "center": ctr,
        },
    )


def draft_array_path(
    project: Dict[str, Any],
    index: int,
    path_index: int,
    count: int = 4,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Create an array of a draft object along a path.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    index : int
        Index of the source draft object.
    path_index : int
        Index of the path draft object (wire, bspline, etc.).
    count : int
        Number of copies along the path (default ``4``).

    Returns
    -------
    dict
        The newly created array draft object.
    """
    obj = _get_draft(project, index)
    path_obj = _get_draft(project, path_index)
    if count < 2:
        raise ValueError("count must be >= 2")
    return _make_draft(
        project,
        "array_path",
        name,
        {
            "source_id": obj["id"],
            "path_id": path_obj["id"],
            "count": int(count),
        },
    )


def draft_copy(
    project: Dict[str, Any],
    index: int,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a simple copy of a draft object.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    index : int
        Index of the draft object to copy.
    name : str or None
        Label for the copy.

    Returns
    -------
    dict
        The newly created copy.
    """
    obj = _get_draft(project, index)
    new_obj = deepcopy(obj)
    new_obj["id"] = _next_id(project)
    if name is None:
        name = _unique_name(project, f"{obj['name']}_Copy")
    new_obj["name"] = name

    ensure_collection(project, "draft_objects").append(new_obj)
    return new_obj
