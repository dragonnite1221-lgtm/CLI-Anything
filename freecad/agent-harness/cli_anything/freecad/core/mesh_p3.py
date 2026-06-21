# ruff: noqa: F403, F405, E501
from .mesh_base import *  # noqa: F403

# fmt: off
from .mesh_p1 import _get_mesh  # noqa: E402,E501
# fmt: on


def mesh_info(project: Dict[str, Any], mesh_index: int) -> Dict[str, Any]:
    """Return a summary of the mesh at *mesh_index*.

    Parameters
    ----------
    project : dict
        The project state dictionary.
    mesh_index : int
        Index of the mesh.

    Returns
    -------
    dict
        Copy of the mesh entry.
    """
    mesh = _get_mesh(project, mesh_index)
    return deepcopy(mesh)


def analyze_mesh(project: Dict[str, Any], mesh_index: int) -> Dict[str, Any]:
    """Return stored analysis results for the mesh at *mesh_index*.

    Analysis covers vertex/face counts, bounding-box estimation, and
    volume/area placeholders.  Actual numerical analysis happens in the
    FreeCAD macro; this records the intent and returns current metadata.

    Parameters
    ----------
    project : dict
        The project state dictionary.
    mesh_index : int
        Index of the mesh.

    Returns
    -------
    dict
        Analysis result dictionary.
    """
    mesh = _get_mesh(project, mesh_index)
    return {
        "mesh_id": mesh["id"],
        "name": mesh["name"],
        "vertices_count": mesh["vertices_count"],
        "faces_count": mesh["faces_count"],
        "format": mesh["format"],
        "operations_applied": list(mesh["operations_applied"]),
        "analysis": "pending_macro_execution",
    }


def check_mesh(project: Dict[str, Any], mesh_index: int) -> Dict[str, Any]:
    """Check the mesh at *mesh_index* for common problems.

    Returns a diagnostic dictionary.  The actual checks (non-manifold
    edges, self-intersections, degenerate faces) are performed by the
    FreeCAD macro; this function records the request.

    Parameters
    ----------
    project : dict
        The project state dictionary.
    mesh_index : int
        Index of the mesh.

    Returns
    -------
    dict
        Diagnostic placeholder with mesh metadata.
    """
    mesh = _get_mesh(project, mesh_index)
    return {
        "mesh_id": mesh["id"],
        "name": mesh["name"],
        "checks": [
            "non_manifold_edges",
            "self_intersections",
            "degenerate_faces",
            "duplicate_faces",
            "duplicate_points",
            "orientation",
        ],
        "status": "pending_macro_execution",
    }
