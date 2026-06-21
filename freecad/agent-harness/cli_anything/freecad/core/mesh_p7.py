# ruff: noqa: F403, F405, E501
from .mesh_base import *  # noqa: F403

# fmt: off
from .mesh_p1 import _get_mesh  # noqa: E402,E501
# fmt: on


def split_mesh(project: Dict[str, Any], mesh_index: int) -> Dict[str, Any]:
    """Split a mesh into its disconnected components.

    Records the split operation.  The actual component separation is
    performed by the FreeCAD macro; this function returns metadata
    about the request.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    mesh_index : int
        Index of the mesh to split.

    Returns
    -------
    dict
        Metadata describing the split request.
    """
    mesh = _get_mesh(project, mesh_index)
    mesh["operations_applied"].append(
        {
            "op": "split",
            "params": {},
        }
    )
    return {
        "mesh_id": mesh["id"],
        "name": mesh["name"],
        "status": "split_pending_macro_execution",
    }


def mesh_to_shape(
    project: Dict[str, Any],
    mesh_index: int,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Convert a mesh to a solid shape and add it to ``project["parts"]``.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    mesh_index : int
        Index of the source mesh.
    name : str or None
        Label for the resulting part.

    Returns
    -------
    dict
        The newly created part entry in ``project["parts"]``.
    """
    mesh = _get_mesh(project, mesh_index)
    parts = ensure_collection(project, "parts")

    if name is None:
        base = f"{mesh['name']}_Solid"
        existing = {p["name"] for p in parts}
        if base in existing:
            counter = 2
            while f"{base}_{counter}" in existing:
                counter += 1
            base = f"{base}_{counter}"
        name = base

    # Compute next part id
    part_id = max((p["id"] for p in parts), default=0) + 1

    part: Dict[str, Any] = {
        "id": part_id,
        "name": name,
        "type": "mesh_to_shape",
        "params": {
            "source_mesh_id": mesh["id"],
        },
        "placement": {
            "position": [0.0, 0.0, 0.0],
            "rotation": [0.0, 0.0, 0.0],
        },
        "material_index": None,
        "visible": True,
    }

    parts.append(part)
    return part
