# ruff: noqa: F403, F405, E501
from .fem_base import *  # noqa: F403

# fmt: off
from .fem_p1 import _get_analysis, _validate_vec3  # noqa: E402,E501
# fmt: on


def add_force_constraint(
    project: Dict[str, Any],
    ai: int,
    references: List[Any],
    magnitude: float,
    direction: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Add a force constraint to the analysis.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    ai : int
        Analysis index.
    references : list
        Geometry references where the force is applied.
    magnitude : float
        Force magnitude in Newtons.
    direction : list[float] or None
        Force direction vector ``[x, y, z]``. Defaults to ``[0, 0, -1]``.

    Returns
    -------
    dict
        The constraint entry.
    """
    analysis = _get_analysis(project, ai)

    if direction is not None:
        direction = _validate_vec3(direction, "direction")
    else:
        direction = [0.0, 0.0, -1.0]

    constraint: Dict[str, Any] = {
        "type": "force",
        "references": list(references),
        "magnitude": float(magnitude),
        "direction": direction,
    }

    analysis["constraints"].append(constraint)
    return constraint


def add_pressure_constraint(
    project: Dict[str, Any],
    ai: int,
    references: List[Any],
    pressure: float,
) -> Dict[str, Any]:
    """Add a pressure constraint to the analysis.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    ai : int
        Analysis index.
    references : list
        Geometry references (faces) where pressure is applied.
    pressure : float
        Pressure value in MPa.

    Returns
    -------
    dict
        The constraint entry.
    """
    analysis = _get_analysis(project, ai)

    constraint: Dict[str, Any] = {
        "type": "pressure",
        "references": list(references),
        "pressure": float(pressure),
    }

    analysis["constraints"].append(constraint)
    return constraint


def add_displacement_constraint(
    project: Dict[str, Any],
    ai: int,
    references: List[Any],
    displacement: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Add a prescribed displacement constraint.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    ai : int
        Analysis index.
    references : list
        Geometry references where the displacement is prescribed.
    displacement : list[float] or None
        Displacement vector ``[dx, dy, dz]``. Defaults to ``[0, 0, 0]``.

    Returns
    -------
    dict
        The constraint entry.
    """
    analysis = _get_analysis(project, ai)

    if displacement is not None:
        displacement = _validate_vec3(displacement, "displacement")
    else:
        displacement = [0.0, 0.0, 0.0]

    constraint: Dict[str, Any] = {
        "type": "displacement",
        "references": list(references),
        "displacement": displacement,
    }

    analysis["constraints"].append(constraint)
    return constraint
