# ruff: noqa: F403, F405, E501
from .mesh_base import *  # noqa: F403

# fmt: off
from .mesh_p1 import _get_mesh  # noqa: E402,E501
# fmt: on


def remesh_mesh(
    project: Dict[str, Any],
    mesh_index: int,
    target_length: float = 1.0,
) -> Dict[str, Any]:
    """Remesh the mesh at *mesh_index* with uniform edge lengths.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    mesh_index : int
        Index of the mesh to remesh.
    target_length : float
        Target edge length for the remeshed output.

    Returns
    -------
    dict
        The updated mesh entry.

    Raises
    ------
    IndexError
        If *mesh_index* is out of range.
    ValueError
        If *target_length* is not positive.
    """
    if target_length <= 0:
        raise ValueError("target_length must be a positive number")

    mesh = _get_mesh(project, mesh_index)
    mesh["operations_applied"].append(
        {
            "op": "remesh",
            "params": {"target_length": float(target_length)},
        }
    )
    return mesh


def smooth_mesh(
    project: Dict[str, Any],
    mesh_index: int,
    iterations: int = 3,
    factor: float = 0.5,
) -> Dict[str, Any]:
    """Apply Laplacian smoothing to the mesh at *mesh_index*.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    mesh_index : int
        Index of the mesh to smooth.
    iterations : int
        Number of smoothing passes (default ``3``).
    factor : float
        Smoothing intensity factor between 0 and 1 (default ``0.5``).

    Returns
    -------
    dict
        The updated mesh entry.

    Raises
    ------
    IndexError
        If *mesh_index* is out of range.
    ValueError
        If *iterations* or *factor* is invalid.
    """
    if not isinstance(iterations, int) or iterations <= 0:
        raise ValueError("iterations must be a positive integer")
    if not (0.0 < factor <= 1.0):
        raise ValueError("factor must be between 0 (exclusive) and 1 (inclusive)")

    mesh = _get_mesh(project, mesh_index)
    mesh["operations_applied"].append(
        {
            "op": "smooth",
            "params": {"iterations": iterations, "factor": float(factor)},
        }
    )
    return mesh


def repair_mesh(project: Dict[str, Any], mesh_index: int) -> Dict[str, Any]:
    """Record a repair operation for the mesh at *mesh_index*.

    Repair includes fixing degenerate faces, removing duplicates,
    harmonising normals, and filling small holes.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    mesh_index : int
        Index of the mesh to repair.

    Returns
    -------
    dict
        The updated mesh entry.
    """
    mesh = _get_mesh(project, mesh_index)
    mesh["operations_applied"].append(
        {
            "op": "repair",
            "params": {},
        }
    )
    return mesh
