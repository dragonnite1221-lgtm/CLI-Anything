# ruff: noqa: F403, F405, E501
from .surface_base import *  # noqa: F403

# fmt: off
from .surface_p1 import _get_surface, _next_id, _unique_name, _validate_index_list  # noqa: E402,E501
# fmt: on


def surface_sew(
    project: Dict[str, Any],
    surface_indices: List[int],
    tolerance: float = 0.01,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Sew multiple surfaces into a single shell.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    surface_indices : list[int]
        Indices of the surfaces to sew together.  At least two required.
    tolerance : float
        Sewing tolerance (default ``0.01``).
    name : str or None
        Label for the resulting surface.  Auto-generated when *None*.

    Returns
    -------
    dict
        The newly created sewn surface entry.

    Raises
    ------
    ValueError
        If fewer than two surfaces or tolerance is invalid.
    IndexError
        If any surface index is out of range.
    """
    if tolerance <= 0:
        raise ValueError("tolerance must be a positive number")

    refs = _validate_index_list(surface_indices, "surface_indices", min_count=2)

    # Validate that each referenced surface exists
    source_ids = []
    for idx in refs:
        s = _get_surface(project, idx)
        source_ids.append(s["id"])

    surfaces = ensure_collection(project, "surfaces")

    if name is None:
        name = _unique_name(project, "SewnSurface")

    surface: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "type": "sew",
        "params": {
            "tolerance": float(tolerance),
            "source_surface_ids": source_ids,
        },
        "source_refs": refs,
    }

    surfaces.append(surface)
    return surface


def surface_cut(
    project: Dict[str, Any],
    surface_index: int,
    cutting_index: int,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Cut a surface with another surface or shape.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    surface_index : int
        Index of the surface to cut.
    cutting_index : int
        Index of the cutting surface or shape reference.
    name : str or None
        Label for the resulting surface.  Auto-generated when *None*.

    Returns
    -------
    dict
        The newly created cut surface entry.

    Raises
    ------
    IndexError
        If *surface_index* is out of range.
    ValueError
        If indices are equal.
    """
    source = _get_surface(project, surface_index)

    if surface_index == cutting_index:
        raise ValueError("surface_index and cutting_index must differ")

    surfaces = ensure_collection(project, "surfaces")

    if name is None:
        name = _unique_name(project, f"{source['name']}_Cut")

    surface: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "type": "cut",
        "params": {
            "source_surface_id": source["id"],
            "cutting_index": cutting_index,
        },
        "source_refs": [surface_index, cutting_index],
    }

    surfaces.append(surface)
    return surface
