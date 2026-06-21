# ruff: noqa: F403, F405, E501
from .surface_base import *  # noqa: F403


def _next_id(project: Dict[str, Any]) -> int:
    """Return the next available integer ID for surfaces."""
    items = project.get("surfaces", [])
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


def _unique_name(project: Dict[str, Any], base: str) -> str:
    """Return a unique name derived from *base* inside ``project["surfaces"]``."""
    existing = {item["name"] for item in project.get("surfaces", [])}
    if base not in existing:
        return base
    counter = 2
    while f"{base}_{counter}" in existing:
        counter += 1
    return f"{base}_{counter}"


def _get_surface(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Return the surface at *index*, raising ``IndexError`` if out of range."""
    surfaces = project.get("surfaces", [])
    if not isinstance(index, int) or index < 0 or index >= len(surfaces):
        raise IndexError(f"Surface index {index} out of range (0..{len(surfaces) - 1})")
    return surfaces[index]


def _validate_index_list(indices: Any, label: str, min_count: int = 1) -> List[int]:
    """Validate that *indices* is a list of non-negative integers."""
    if not isinstance(indices, (list, tuple)):
        raise ValueError(f"{label} must be a list of indices")
    if len(indices) < min_count:
        raise ValueError(
            f"{label} requires at least {min_count} index(es), got {len(indices)}"
        )
    for i, v in enumerate(indices):
        if not isinstance(v, int) or v < 0:
            raise ValueError(f"{label}[{i}] must be a non-negative integer, got {v!r}")
    return list(indices)


def surface_filling(
    project: Dict[str, Any],
    edge_indices: List[int],
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a surface that fills a boundary defined by edges.

    The filling surface interpolates through the specified boundary
    edges, producing a smooth G1/G2 surface patch.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    edge_indices : list[int]
        Indices referencing boundary edges (from parts or sketches).
    name : str or None
        Label for the surface.  Auto-generated when *None*.

    Returns
    -------
    dict
        The newly created surface entry.

    Raises
    ------
    ValueError
        If *edge_indices* has fewer than 1 entry or contains invalid values.
    """
    refs = _validate_index_list(edge_indices, "edge_indices", min_count=1)
    surfaces = ensure_collection(project, "surfaces")

    if name is None:
        name = _unique_name(project, "Filling")

    surface: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "type": "filling",
        "params": {},
        "source_refs": refs,
    }

    surfaces.append(surface)
    return surface


def surface_sections(
    project: Dict[str, Any],
    section_indices: List[int],
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a loft-like surface through cross-section profiles.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    section_indices : list[int]
        Indices referencing cross-section profiles (edges, wires, or
        sketches).  At least two sections are required.
    name : str or None
        Label for the surface.  Auto-generated when *None*.

    Returns
    -------
    dict
        The newly created surface entry.

    Raises
    ------
    ValueError
        If fewer than two sections are provided.
    """
    refs = _validate_index_list(section_indices, "section_indices", min_count=2)
    surfaces = ensure_collection(project, "surfaces")

    if name is None:
        name = _unique_name(project, "Sections")

    surface: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "type": "sections",
        "params": {},
        "source_refs": refs,
    }

    surfaces.append(surface)
    return surface
