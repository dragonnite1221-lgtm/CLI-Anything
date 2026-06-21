# ruff: noqa: F403, F405, E501
from .mesh_base import *  # noqa: F403

# fmt: off
from .mesh_p1 import _get_mesh, _next_id, _unique_name  # noqa: E402,E501
# fmt: on


def fill_holes(
    project: Dict[str, Any],
    mesh_index: int,
    max_hole_size: int = 10,
) -> Dict[str, Any]:
    """Fill holes in the mesh at *mesh_index*.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    mesh_index : int
        Index of the mesh.
    max_hole_size : int
        Maximum number of edges bounding a hole to fill (default ``10``).

    Returns
    -------
    dict
        The updated mesh entry.

    Raises
    ------
    ValueError
        If *max_hole_size* is not a positive integer.
    """
    if not isinstance(max_hole_size, int) or max_hole_size <= 0:
        raise ValueError("max_hole_size must be a positive integer")

    mesh = _get_mesh(project, mesh_index)
    mesh["operations_applied"].append(
        {
            "op": "fill_holes",
            "params": {"max_hole_size": max_hole_size},
        }
    )
    return mesh


def flip_normals(project: Dict[str, Any], mesh_index: int) -> Dict[str, Any]:
    """Flip all face normals on the mesh at *mesh_index*.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    mesh_index : int
        Index of the mesh.

    Returns
    -------
    dict
        The updated mesh entry.
    """
    mesh = _get_mesh(project, mesh_index)
    mesh["operations_applied"].append(
        {
            "op": "flip_normals",
            "params": {},
        }
    )
    return mesh


def merge_meshes(
    project: Dict[str, Any],
    indices: List[int],
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Merge multiple meshes into a single mesh.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    indices : list[int]
        Indices of the meshes to merge.
    name : str or None
        Label for the merged mesh.

    Returns
    -------
    dict
        The newly created merged mesh entry.

    Raises
    ------
    ValueError
        If fewer than two indices are supplied or any index is invalid.
    """
    if not isinstance(indices, (list, tuple)) or len(indices) < 2:
        raise ValueError("At least two mesh indices are required for merging")

    source_ids = []
    for idx in indices:
        mesh = _get_mesh(project, idx)
        source_ids.append(mesh["id"])

    meshes = ensure_collection(project, "meshes")

    if name is None:
        name = _unique_name(project, "MergedMesh")

    result: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "source": "merged",
        "format": "computed",
        "vertices_count": 0,
        "faces_count": 0,
        "operations_applied": [
            {"op": "merge", "params": {"source_ids": source_ids}},
        ],
    }

    meshes.append(result)
    return result
