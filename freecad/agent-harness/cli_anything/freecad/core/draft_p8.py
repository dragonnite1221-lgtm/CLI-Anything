# ruff: noqa: F403, F405, E501
from .draft_base import *  # noqa: F403

# fmt: off
from .draft_p1 import _get_draft, _make_draft, _next_id, _unique_name  # noqa: E402,E501
# fmt: on


def draft_offset(
    project: Dict[str, Any],
    index: int,
    distance: float = 1.0,
    copy: bool = True,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Offset a draft object by *distance*.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    index : int
        Index of the draft object.
    distance : float
        Offset distance (default ``1``).
    copy : bool
        If ``True`` (default) create an offset copy.
    name : str or None
        Label for the offset copy.

    Returns
    -------
    dict
        The offset draft object.
    """
    obj = _get_draft(project, index)
    if distance == 0:
        raise ValueError("distance must be non-zero")

    if copy:
        new_obj = deepcopy(obj)
        new_obj["id"] = _next_id(project)
        if name is None:
            name = _unique_name(project, f"{obj['name']}_Offset")
        new_obj["name"] = name
        new_obj["properties"]["_offset_distance"] = float(distance)
        ensure_collection(project, "draft_objects").append(new_obj)
        return new_obj

    obj["properties"]["_offset_distance"] = float(distance)
    return obj


def draft_array_linear(
    project: Dict[str, Any],
    index: int,
    x_count: int = 2,
    y_count: int = 1,
    x_interval: float = 20.0,
    y_interval: float = 20.0,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a linear (rectangular) array of a draft object.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    index : int
        Index of the source draft object.
    x_count : int
        Number of copies along X (default ``2``).
    y_count : int
        Number of copies along Y (default ``1``).
    x_interval : float
        Spacing along X (default ``20``).
    y_interval : float
        Spacing along Y (default ``20``).

    Returns
    -------
    dict
        The newly created array draft object.
    """
    obj = _get_draft(project, index)
    if x_count < 1 or y_count < 1:
        raise ValueError("x_count and y_count must be >= 1")
    return _make_draft(
        project,
        "array_linear",
        name,
        {
            "source_id": obj["id"],
            "x_count": int(x_count),
            "y_count": int(y_count),
            "x_interval": float(x_interval),
            "y_interval": float(y_interval),
        },
    )
