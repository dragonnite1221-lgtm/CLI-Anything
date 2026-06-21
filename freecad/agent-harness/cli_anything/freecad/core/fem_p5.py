# ruff: noqa: F403, F405, E501
from .fem_base import *  # noqa: F403

# fmt: off
from .fem_p1 import _get_analysis  # noqa: E402,E501
# fmt: on


def add_beam_section(
    project: Dict[str, Any],
    analysis_index: int,
    section_type: str = "rectangular",
    references: Optional[List[str]] = None,
    width: Optional[float] = None,
    height: Optional[float] = None,
    radius: Optional[float] = None,
) -> Dict[str, Any]:
    """Add an ElementGeometry1D beam section (FreeCAD 1.1: box_beam, elliptical).

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    analysis_index : int
        Analysis index.
    section_type : str
        Beam cross-section type (``"rectangular"``, ``"circular"``,
        ``"box_beam"``, ``"elliptical"``, ``"pipe"``).
    references : list[str] or None
        Geometry references (edges) where the section applies.
    width : float or None
        Section width (relevant for rectangular / box_beam / elliptical).
    height : float or None
        Section height (relevant for rectangular / box_beam / elliptical).
    radius : float or None
        Section radius (relevant for circular / pipe).

    Returns
    -------
    dict
        The constraint entry.

    Raises
    ------
    ValueError
        If *section_type* is unknown.
    """
    if section_type not in VALID_BEAM_SECTIONS:
        valid = ", ".join(sorted(VALID_BEAM_SECTIONS))
        raise ValueError(f"Unknown section_type '{section_type}'. Valid: {valid}")

    analysis = _get_analysis(project, analysis_index)

    constraint: Dict[str, Any] = {
        "type": "beam_section",
        "section_type": section_type,
        "references": list(references) if references is not None else [],
        "width": float(width) if width is not None else None,
        "height": float(height) if height is not None else None,
        "radius": float(radius) if radius is not None else None,
    }

    analysis["constraints"].append(constraint)
    return constraint


def add_tie_constraint(
    project: Dict[str, Any],
    analysis_index: int,
    master_refs: List[str],
    slave_refs: List[str],
) -> Dict[str, Any]:
    """Add a tie constraint between shell faces (FreeCAD 1.1).

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    analysis_index : int
        Analysis index.
    master_refs : list[str]
        Geometry references for the master surface.
    slave_refs : list[str]
        Geometry references for the slave surface.

    Returns
    -------
    dict
        The constraint entry.
    """
    analysis = _get_analysis(project, analysis_index)

    constraint: Dict[str, Any] = {
        "type": "tie",
        "master_refs": list(master_refs),
        "slave_refs": list(slave_refs),
    }

    analysis["constraints"].append(constraint)
    return constraint


def purge_results(
    project: Dict[str, Any],
    analysis_index: int,
) -> Dict[str, Any]:
    """Delete all result objects from an analysis (FreeCAD 1.1).

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    analysis_index : int
        Analysis index.

    Returns
    -------
    dict
        The updated analysis dictionary.
    """
    analysis = _get_analysis(project, analysis_index)
    analysis["results"] = None
    return analysis
