# ruff: noqa: F403, F405, E501
from .fem_base import *  # noqa: F403

# fmt: off
from .fem_p1 import _get_analysis  # noqa: E402,E501
# fmt: on


def generate_fem_mesh(
    project: Dict[str, Any],
    ai: int,
    max_size: Optional[float] = None,
    min_size: Optional[float] = None,
    element_type: str = "Tet10",
    mesher: str = "gmsh",
    gmsh_verbosity: int = 1,
    second_order_linear: bool = False,
    local_refinement: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Configure mesh generation parameters for an analysis.

    The actual mesh generation is performed by the generated FreeCAD
    macro. This function stores the meshing parameters.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    ai : int
        Analysis index.
    max_size : float or None
        Maximum element size. When *None*, FreeCAD uses automatic sizing.
    min_size : float or None
        Minimum element size. When *None*, FreeCAD uses automatic sizing.
    element_type : str
        Element type (e.g. ``"Tet4"``, ``"Tet10"``, ``"Hex8"``).
    mesher : str
        Meshing backend (``"gmsh"`` or ``"netgen"``).
    gmsh_verbosity : int
        Gmsh verbosity level (only relevant when *mesher* is ``"gmsh"``).
    second_order_linear : bool
        Enable Netgen Second Order Linear elements.
    local_refinement : dict or None
        Mapping of geometry references to local mesh sizes.

    Returns
    -------
    dict
        The mesh parameters dictionary.

    Raises
    ------
    ValueError
        If *element_type* or *mesher* is unknown.
    """
    if element_type not in VALID_ELEMENT_TYPES:
        valid = ", ".join(sorted(VALID_ELEMENT_TYPES))
        raise ValueError(f"Unknown element_type '{element_type}'. Valid: {valid}")

    if mesher not in VALID_MESHERS:
        valid = ", ".join(sorted(VALID_MESHERS))
        raise ValueError(f"Unknown mesher '{mesher}'. Valid: {valid}")

    analysis = _get_analysis(project, ai)

    mesh_params: Dict[str, Any] = {
        "max_size": float(max_size) if max_size is not None else None,
        "min_size": float(min_size) if min_size is not None else None,
        "element_type": element_type,
        "mesher": mesher,
        "gmsh_verbosity": int(gmsh_verbosity),
        "second_order_linear": bool(second_order_linear),
        "local_refinement": dict(local_refinement)
        if local_refinement is not None
        else None,
    }

    analysis["mesh_params"] = mesh_params
    return mesh_params
