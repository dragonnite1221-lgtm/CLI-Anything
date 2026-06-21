# ruff: noqa: F403, F405, E501
from .draft_base import *  # noqa: F403

# fmt: off
from .draft_p1 import _get_draft, _next_id, _unique_name, _validate_vec3  # noqa: E402,E501
# fmt: on


def draft_scale(
    project: Dict[str, Any],
    index: int,
    scale: Union[float, List[float]] = 2.0,
    center: Optional[List[float]] = None,
    copy: bool = False,
) -> Dict[str, Any]:
    """Scale a draft object.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    index : int
        Index of the draft object.
    scale : float or list[float]
        Uniform scale factor, or ``[sx, sy, sz]`` anisotropic scale.
    center : list[float] or None
        Center of scaling (default origin).
    copy : bool
        If ``True`` create a scaled copy.

    Returns
    -------
    dict
        The scaled (or copied) draft object.
    """
    obj = _get_draft(project, index)
    ctr = _validate_vec3(center, "center") if center is not None else [0.0, 0.0, 0.0]

    if isinstance(scale, (int, float)):
        if scale == 0:
            raise ValueError("scale must be non-zero")
        scale_vec = [float(scale)] * 3
    else:
        scale_vec = _validate_vec3(scale, "scale")
        if any(s == 0 for s in scale_vec):
            raise ValueError("scale components must be non-zero")

    if copy:
        new_obj = deepcopy(obj)
        new_obj["id"] = _next_id(project)
        new_obj["name"] = _unique_name(project, f"{obj['name']}_Scaled")
        new_obj["properties"]["_scale"] = scale_vec
        new_obj["properties"]["_scale_center"] = ctr
        ensure_collection(project, "draft_objects").append(new_obj)
        return new_obj

    obj["properties"]["_scale"] = scale_vec
    obj["properties"]["_scale_center"] = ctr
    return obj


def draft_mirror(
    project: Dict[str, Any],
    index: int,
    point: Optional[List[float]] = None,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a mirrored copy of a draft object.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    index : int
        Index of the draft object to mirror.
    point : list[float] or None
        Mirror reference point (default origin).
    name : str or None
        Label for the mirrored copy.

    Returns
    -------
    dict
        The newly created mirrored draft object.
    """
    obj = _get_draft(project, index)
    pt = _validate_vec3(point, "point") if point is not None else [0.0, 0.0, 0.0]

    new_obj = deepcopy(obj)
    new_obj["id"] = _next_id(project)
    if name is None:
        name = _unique_name(project, f"{obj['name']}_Mirror")
    new_obj["name"] = name
    new_obj["properties"]["_mirror_point"] = pt

    ensure_collection(project, "draft_objects").append(new_obj)
    return new_obj
