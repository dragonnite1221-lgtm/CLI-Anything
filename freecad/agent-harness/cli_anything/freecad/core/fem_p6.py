# ruff: noqa: F403, F405, E501
from .fem_base import *  # noqa: F403

# fmt: off
from .fem_p1 import _get_analysis  # noqa: E402,E501
# fmt: on


def suppress_object(
    project: Dict[str, Any],
    analysis_index: int,
    constraint_index: int,
) -> Dict[str, Any]:
    """Toggle suppressed state on a constraint (FreeCAD 1.1).

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    analysis_index : int
        Analysis index.
    constraint_index : int
        Index of the constraint to toggle.

    Returns
    -------
    dict
        The updated constraint dictionary.

    Raises
    ------
    IndexError
        If *constraint_index* is out of range.
    """
    analysis = _get_analysis(project, analysis_index)
    constraints = analysis["constraints"]

    if (
        not isinstance(constraint_index, int)
        or constraint_index < 0
        or constraint_index >= len(constraints)
    ):
        raise IndexError(
            f"Constraint index {constraint_index} out of range "
            f"(0..{len(constraints) - 1})"
        )

    constraint = constraints[constraint_index]
    constraint["suppressed"] = not constraint.get("suppressed", False)
    return constraint


def solve_fem(
    project: Dict[str, Any],
    ai: int,
    solver: str = "calculix",
    output_format: Optional[str] = None,
    buckling_accuracy: Optional[float] = None,
) -> Dict[str, Any]:
    """Configure the FEM solver for an analysis.

    The actual solving is performed by the generated FreeCAD macro.
    This function stores the solver configuration and validates that
    the analysis has the minimum required setup.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    ai : int
        Analysis index.
    solver : str
        Solver backend name (``"calculix"``, ``"elmer"``, ``"z88"``).
    output_format : str or None
        Result output format (``"vtu"``, ``"vtk"``, ``"result"``).
        When *None*, the solver default is used.
    buckling_accuracy : float or None
        Buckling accuracy parameter for CalculiX solver.

    Returns
    -------
    dict
        Solver configuration summary.

    Raises
    ------
    ValueError
        If *solver* is unknown, *output_format* is invalid, or the
        analysis is missing constraints or mesh parameters.
    """
    if solver not in VALID_SOLVERS:
        valid = ", ".join(sorted(VALID_SOLVERS))
        raise ValueError(f"Unknown solver '{solver}'. Valid: {valid}")

    if output_format is not None and output_format not in VALID_OUTPUT_FORMATS:
        valid = ", ".join(sorted(VALID_OUTPUT_FORMATS))
        raise ValueError(f"Unknown output_format '{output_format}'. Valid: {valid}")

    analysis = _get_analysis(project, ai)

    if not analysis["constraints"]:
        raise ValueError("Analysis has no constraints defined")

    if analysis["mesh_params"] is None:
        raise ValueError(
            "Mesh parameters must be set before solving (call generate_fem_mesh first)"
        )

    analysis["solver"] = solver
    analysis["results"] = {
        "status": "pending",
        "solver": solver,
        "constraints_count": len(analysis["constraints"]),
        "output_format": output_format,
        "buckling_accuracy": float(buckling_accuracy)
        if buckling_accuracy is not None
        else None,
    }

    return analysis["results"]


def get_fem_results(
    project: Dict[str, Any],
    ai: int,
) -> Dict[str, Any]:
    """Return the results of an analysis.

    Returns
    -------
    dict
        The results dictionary, or a status indicator if not yet solved.
    """
    analysis = _get_analysis(project, ai)

    if analysis["results"] is None:
        return {"status": "not_run", "message": "Analysis has not been solved yet"}

    return analysis["results"]
