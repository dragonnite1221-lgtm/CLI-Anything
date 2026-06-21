# ruff: noqa: F403, F405, E501
from .fem_base import *  # noqa: F403

# fmt: off
from .fem_p1 import _get_analysis  # noqa: E402,E501
# fmt: on


def add_temperature_constraint(
    project: Dict[str, Any],
    ai: int,
    references: List[Any],
    temperature: float,
) -> Dict[str, Any]:
    """Add a temperature boundary constraint.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    ai : int
        Analysis index.
    references : list
        Geometry references where temperature is fixed.
    temperature : float
        Temperature value in Kelvin.

    Returns
    -------
    dict
        The constraint entry.
    """
    analysis = _get_analysis(project, ai)

    constraint: Dict[str, Any] = {
        "type": "temperature",
        "references": list(references),
        "temperature": float(temperature),
    }

    analysis["constraints"].append(constraint)
    return constraint


def add_heatflux_constraint(
    project: Dict[str, Any],
    ai: int,
    references: List[Any],
    flux: float,
) -> Dict[str, Any]:
    """Add a heat flux boundary constraint.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    ai : int
        Analysis index.
    references : list
        Geometry references where the heat flux is applied.
    flux : float
        Heat flux value in W/m^2.

    Returns
    -------
    dict
        The constraint entry.
    """
    analysis = _get_analysis(project, ai)

    constraint: Dict[str, Any] = {
        "type": "heatflux",
        "references": list(references),
        "flux": float(flux),
    }

    analysis["constraints"].append(constraint)
    return constraint


def set_fem_material(
    project: Dict[str, Any],
    ai: int,
    material_index: int,
) -> Dict[str, Any]:
    """Assign a material from the project's materials list to an analysis.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    ai : int
        Analysis index.
    material_index : int
        Index into ``project["materials"]``.

    Returns
    -------
    dict
        The updated analysis dictionary.

    Raises
    ------
    IndexError
        If *material_index* is out of range.
    """
    analysis = _get_analysis(project, ai)

    materials = project.get("materials", [])
    if (
        not isinstance(material_index, int)
        or material_index < 0
        or material_index >= len(materials)
    ):
        raise IndexError(
            f"Material index {material_index} out of range (0..{len(materials) - 1})"
        )

    analysis["material_index"] = material_index
    return analysis
