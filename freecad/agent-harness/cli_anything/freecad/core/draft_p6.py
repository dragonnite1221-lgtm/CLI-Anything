# ruff: noqa: F403, F405, E501
from .draft_base import *  # noqa: F403

# fmt: off
from .draft_p1 import _get_draft, _next_id, _unique_name, _validate_vec3  # noqa: E402,E501
# fmt: on


def draft_move(
    project: Dict[str, Any],
    index: int,
    vector: List[float],
    copy: bool = False,
) -> Dict[str, Any]:
    """Move a draft object by *vector*, optionally creating a copy.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    index : int
        Index of the draft object.
    vector : list[float]
        ``[dx, dy, dz]`` translation vector.
    copy : bool
        If ``True`` create a moved copy instead of modifying in-place.

    Returns
    -------
    dict
        The moved (or copied) draft object.
    """
    obj = _get_draft(project, index)
    vec = _validate_vec3(vector, "vector")

    if copy:
        new_obj = deepcopy(obj)
        new_obj["id"] = _next_id(project)
        new_obj["name"] = _unique_name(project, f"{obj['name']}_Copy")
        pos = new_obj["placement"]["position"]
        new_obj["placement"]["position"] = [pos[i] + vec[i] for i in range(3)]
        ensure_collection(project, "draft_objects").append(new_obj)
        return new_obj

    pos = obj["placement"]["position"]
    obj["placement"]["position"] = [pos[i] + vec[i] for i in range(3)]
    return obj


def draft_rotate(
    project: Dict[str, Any],
    index: int,
    angle: float,
    axis: Optional[List[float]] = None,
    center: Optional[List[float]] = None,
    copy: bool = False,
) -> Dict[str, Any]:
    """Rotate a draft object by *angle* degrees around *axis*.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    index : int
        Index of the draft object.
    angle : float
        Rotation angle in degrees.
    axis : list[float] or None
        Rotation axis (default Z-axis ``[0, 0, 1]``).
    center : list[float] or None
        Center of rotation (default origin).
    copy : bool
        If ``True`` create a rotated copy.

    Returns
    -------
    dict
        The rotated (or copied) draft object.
    """
    obj = _get_draft(project, index)
    ax = _validate_vec3(axis, "axis") if axis is not None else [0.0, 0.0, 1.0]
    ctr = _validate_vec3(center, "center") if center is not None else [0.0, 0.0, 0.0]

    if copy:
        new_obj = deepcopy(obj)
        new_obj["id"] = _next_id(project)
        new_obj["name"] = _unique_name(project, f"{obj['name']}_Copy")
        rot = new_obj["placement"]["rotation"]
        new_obj["placement"]["rotation"] = [rot[0], rot[1], rot[2] + float(angle)]
        ensure_collection(project, "draft_objects").append(new_obj)
        return new_obj

    obj["placement"]["rotation"] = [
        obj["placement"]["rotation"][0],
        obj["placement"]["rotation"][1],
        obj["placement"]["rotation"][2] + float(angle),
    ]
    return obj
