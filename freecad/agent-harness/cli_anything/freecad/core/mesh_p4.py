# ruff: noqa: F403, F405, E501
from .mesh_base import *  # noqa: F403

# fmt: off
from .mesh_p1 import _get_mesh, _next_id, _unique_name  # noqa: E402,E501
# fmt: on


def mesh_boolean(
    project: Dict[str, Any],
    op: str,
    base_index: int,
    tool_index: int,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Perform a boolean operation between two meshes.

    Creates a new mesh entry representing the result.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    op : str
        One of ``"union"``, ``"difference"``, or ``"intersection"``.
    base_index : int
        Index of the base mesh.
    tool_index : int
        Index of the tool mesh.
    name : str or None
        Label for the result mesh.

    Returns
    -------
    dict
        The newly created result mesh entry.

    Raises
    ------
    ValueError
        If *op* is unknown or indices are equal.
    IndexError
        If either index is out of range.
    """
    if op not in MESH_BOOLEAN_OPS:
        valid = ", ".join(sorted(MESH_BOOLEAN_OPS))
        raise ValueError(f"Unknown mesh boolean op '{op}'. Valid: {valid}")

    if base_index == tool_index:
        raise ValueError("base_index and tool_index must differ")

    base_mesh = _get_mesh(project, base_index)
    tool_mesh = _get_mesh(project, tool_index)

    meshes = ensure_collection(project, "meshes")

    if name is None:
        name = _unique_name(project, f"MeshBool_{op.capitalize()}")

    result: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "source": f"boolean:{op}",
        "format": "computed",
        "vertices_count": 0,
        "faces_count": 0,
        "operations_applied": [
            {
                "op": f"boolean_{op}",
                "params": {
                    "base_id": base_mesh["id"],
                    "tool_id": tool_mesh["id"],
                },
            },
        ],
    }

    meshes.append(result)
    return result


def decimate_mesh(
    project: Dict[str, Any],
    mesh_index: int,
    target_faces: int = 1000,
) -> Dict[str, Any]:
    """Decimate (simplify) the mesh at *mesh_index*.

    Records a decimation operation targeting *target_faces* triangles.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    mesh_index : int
        Index of the mesh to decimate.
    target_faces : int
        Target number of faces after decimation.

    Returns
    -------
    dict
        The updated mesh entry.

    Raises
    ------
    IndexError
        If *mesh_index* is out of range.
    ValueError
        If *target_faces* is not a positive integer.
    """
    if not isinstance(target_faces, int) or target_faces <= 0:
        raise ValueError("target_faces must be a positive integer")

    mesh = _get_mesh(project, mesh_index)
    mesh["operations_applied"].append(
        {
            "op": "decimate",
            "params": {"target_faces": target_faces},
        }
    )
    return mesh
