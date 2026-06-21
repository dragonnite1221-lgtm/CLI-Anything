# ruff: noqa: F403, F405, E501
from .cam_base import *  # noqa: F403

# fmt: off
from .cam_p1 import _get_job  # noqa: E402,E501
# fmt: on


def simulate_job(
    project: Dict[str, Any],
    job_index: int,
) -> Dict[str, Any]:
    """Simulate a CAM job and return estimated metrics.

    This is a rough estimation based on the number and type of
    operations. Actual simulation runs inside FreeCAD.

    Returns
    -------
    dict
        Simulation summary with estimated time and material removal.
    """
    job = _get_job(project, job_index)

    if not job["operations"]:
        raise ValueError("Job has no operations to simulate")

    # Rough time estimation per operation type (seconds)
    time_estimates = {
        "profile": 120.0,
        "pocket": 300.0,
        "drilling": 60.0,
        "facing": 180.0,
        "tapping": 90.0,
    }

    total_time = 0.0
    for op in job["operations"]:
        total_time += time_estimates.get(op["type"], 120.0)

    return {
        "job_name": job["name"],
        "operations_count": len(job["operations"]),
        "tools_used": len(job["tools"]),
        "estimated_time_seconds": total_time,
        "material_removal": "estimated",
    }


def export_gcode(
    project: Dict[str, Any],
    job_index: int,
    path: str,
) -> Dict[str, Any]:
    """Record metadata for exporting G-code to a file.

    The actual export is performed by the generated FreeCAD macro.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    job_index : int
        Index of the target job.
    path : str
        Output file path for the G-code.

    Returns
    -------
    dict
        Export metadata.

    Raises
    ------
    ValueError
        If *path* is invalid.
    """
    if not isinstance(path, str) or not path.strip():
        raise ValueError("Path must be a non-empty string")

    job = _get_job(project, job_index)

    return {
        "action": "export_gcode",
        "job_name": job["name"],
        "job_index": job_index,
        "path": path.strip(),
        "format": "gcode",
    }


def import_tool_library(
    project: Dict[str, Any],
    job_index: int,
    library_path: str,
) -> Dict[str, Any]:
    """Import a FreeCAD 1.1 tool library file into a CAM job.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    job_index : int
        Index of the target job.
    library_path : str
        Path to the tool library file to import.

    Returns
    -------
    dict
        Import metadata.

    Raises
    ------
    ValueError
        If *library_path* is invalid.
    """
    if not isinstance(library_path, str) or not library_path.strip():
        raise ValueError("library_path must be a non-empty string")

    job = _get_job(project, job_index)

    if "metadata" not in job:
        job["metadata"] = {}

    job["metadata"]["tool_library_path"] = library_path.strip()

    return {
        "action": "import_tool_library",
        "job_name": job["name"],
        "job_index": job_index,
        "library_path": library_path.strip(),
    }
