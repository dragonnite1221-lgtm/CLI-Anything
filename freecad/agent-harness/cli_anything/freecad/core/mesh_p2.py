# ruff: noqa: F403, F405, E501
from .mesh_base import *  # noqa: F403

# fmt: off
from .mesh_p1 import _get_mesh, _next_id, _unique_name, _validate_path  # noqa: E402,E501
# fmt: on


def mesh_from_shape(
    project: Dict[str, Any],
    part_index: int,
    name: Optional[str] = None,
    max_length: Optional[float] = None,
    deviation: float = 0.1,
) -> Dict[str, Any]:
    """Tessellate a solid part into a triangular mesh.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    part_index : int
        Index of the source part in ``project["parts"]``.
    name : str or None
        Label for the new mesh.  Auto-generated when *None*.
    max_length : float or None
        Maximum edge length constraint.  *None* means no constraint.
    deviation : float
        Surface deviation tolerance (default ``0.1``).

    Returns
    -------
    dict
        The newly created mesh entry.

    Raises
    ------
    IndexError
        If *part_index* is out of range.
    ValueError
        If *deviation* is not positive.
    """
    parts = project.get("parts", [])
    if not isinstance(part_index, int) or part_index < 0 or part_index >= len(parts):
        raise IndexError(f"Part index {part_index} out of range (0..{len(parts) - 1})")

    if deviation <= 0:
        raise ValueError("deviation must be a positive number")

    meshes = ensure_collection(project, "meshes")
    part = parts[part_index]

    if name is None:
        name = _unique_name(project, f"{part['name']}_Mesh")

    params: Dict[str, Any] = {"deviation": float(deviation)}
    if max_length is not None:
        if max_length <= 0:
            raise ValueError("max_length must be a positive number")
        params["max_length"] = float(max_length)

    mesh: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "source": part_index,
        "format": "tessellated",
        "vertices_count": 0,
        "faces_count": 0,
        "operations_applied": [
            {"op": "tessellate", "params": params},
        ],
    }

    meshes.append(mesh)
    return mesh


def export_mesh(
    project: Dict[str, Any],
    mesh_index: int,
    path: str,
    format: str = "stl",
) -> Dict[str, Any]:
    """Record an export request for the mesh at *mesh_index*.

    The actual file writing is performed during macro generation; this
    function validates the arguments and returns export metadata.

    Parameters
    ----------
    project : dict
        The project state dictionary.
    mesh_index : int
        Index of the mesh to export.
    path : str
        Destination file path.
    format : str
        Output format (default ``"stl"``).

    Returns
    -------
    dict
        Export metadata including mesh id, path, and format.

    Raises
    ------
    IndexError
        If *mesh_index* is out of range.
    ValueError
        If *format* is unsupported or *path* is empty.
    """
    mesh = _get_mesh(project, mesh_index)
    path = _validate_path(path, "export path")

    fmt = format.lower()
    if fmt not in MESH_FORMATS:
        valid = ", ".join(sorted(MESH_FORMATS))
        raise ValueError(f"Unsupported mesh format '{fmt}'. Valid: {valid}")

    return {
        "mesh_id": mesh["id"],
        "mesh_name": mesh["name"],
        "path": path,
        "format": fmt,
    }
