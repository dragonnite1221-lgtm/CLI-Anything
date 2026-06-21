# ruff: noqa: F403, F405, E501
from .fem_base import *  # noqa: F403

# fmt: off
from .fem_p1 import _get_analysis  # noqa: E402,E501
# fmt: on


def export_fem_results(
    project: Dict[str, Any],
    ai: int,
    path: str,
    format: str = "vtk",
) -> Dict[str, Any]:
    """Record metadata for exporting FEM results.

    The actual export is performed by the generated FreeCAD macro.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    ai : int
        Analysis index.
    path : str
        Output file path.
    format : str
        Export format (``"vtk"``, ``"csv"``, ``"json"``).

    Returns
    -------
    dict
        Export metadata.

    Raises
    ------
    ValueError
        If *format* is unknown or *path* is invalid.
    """
    if not isinstance(path, str) or not path.strip():
        raise ValueError("Path must be a non-empty string")

    if format not in VALID_EXPORT_FORMATS:
        valid = ", ".join(sorted(VALID_EXPORT_FORMATS))
        raise ValueError(f"Unknown format '{format}'. Valid: {valid}")

    analysis = _get_analysis(project, ai)

    return {
        "action": "export_fem_results",
        "analysis_name": analysis["name"],
        "analysis_index": ai,
        "path": path.strip(),
        "format": format,
    }
