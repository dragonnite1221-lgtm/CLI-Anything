# ruff: noqa: F403, F405, E501
from .draft_base import *  # noqa: F403

# fmt: off
from .draft_p1 import _get_draft, _make_draft, _validate_vec3  # noqa: E402,E501
# fmt: on


def draft_join(
    project: Dict[str, Any],
    indices: List[int],
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Join multiple draft wires into one.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    indices : list[int]
        Indices of the draft objects to join.
    name : str or None
        Label for the joined result.

    Returns
    -------
    dict
        The newly created joined draft object.

    Raises
    ------
    ValueError
        If fewer than two indices are provided.
    """
    if not isinstance(indices, (list, tuple)) or len(indices) < 2:
        raise ValueError("At least two draft object indices are required for join")
    source_ids = []
    for idx in indices:
        obj = _get_draft(project, idx)
        source_ids.append(obj["id"])
    return _make_draft(
        project,
        "join",
        name,
        {
            "source_ids": source_ids,
        },
    )


def draft_extrude(
    project: Dict[str, Any],
    index: int,
    vector: Optional[List[float]] = None,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Extrude a 2D draft object into a 3D solid along *vector*.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    index : int
        Index of the draft object to extrude.
    vector : list[float] or None
        Extrusion direction and magnitude (default ``[0, 0, 10]``).
    name : str or None
        Label for the extruded result.

    Returns
    -------
    dict
        The newly created extrusion draft object.
    """
    obj = _get_draft(project, index)
    vec = _validate_vec3(vector, "vector") if vector is not None else [0.0, 0.0, 10.0]
    return _make_draft(
        project,
        "extrude",
        name,
        {
            "source_id": obj["id"],
            "vector": vec,
        },
    )


def draft_fillet_2d(
    project: Dict[str, Any],
    index: int,
    radius: float = 1.0,
    edges: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """Apply a 2D fillet (rounding) to the vertices of a draft object.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    index : int
        Index of the draft object.
    radius : float
        Fillet radius (default ``1``).
    edges : list[int] or None
        When provided, fillet only these edge indices instead of all vertices.

    Returns
    -------
    dict
        The updated draft object.
    """
    if radius <= 0:
        raise ValueError("radius must be a positive number")
    obj = _get_draft(project, index)
    obj["properties"]["_fillet_radius"] = float(radius)
    if edges is not None:
        obj["properties"]["_fillet_edges"] = list(edges)
    return obj
