# ruff: noqa: F403, F405, E501
from .cam_base import *  # noqa: F403

# fmt: off
from .cam_p1 import _get_job  # noqa: E402,E501
# fmt: on


def set_tool(
    project: Dict[str, Any],
    job_index: int,
    tool_number: int = 1,
    diameter: float = 6.0,
    flutes: int = 2,
    type: str = "endmill",
    tool_material: Optional[str] = None,
    coating: Optional[str] = None,
) -> Dict[str, Any]:
    """Define or replace a cutting tool in a CAM job.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    job_index : int
        Index of the target job.
    tool_number : int
        Tool number in the tool table (T1, T2, etc.).
    diameter : float
        Tool diameter in project units.
    flutes : int
        Number of cutting flutes.
    type : str
        Tool type (``"endmill"``, ``"ballnose"``, ``"drill"``, etc.).
    tool_material : str or None
        Tool substrate material (e.g. ``"HSS"``, ``"carbide"``).
    coating : str or None
        Tool coating (e.g. ``"TiN"``, ``"AlTiN"``, ``"DLC"``).

    Returns
    -------
    dict
        The tool entry.

    Raises
    ------
    ValueError
        If *type* is unknown.
    """
    if type not in VALID_TOOL_TYPES:
        valid = ", ".join(sorted(VALID_TOOL_TYPES))
        raise ValueError(f"Unknown tool type '{type}'. Valid: {valid}")

    job = _get_job(project, job_index)

    tool: Dict[str, Any] = {
        "tool_number": int(tool_number),
        "diameter": float(diameter),
        "flutes": int(flutes),
        "type": type,
    }

    if tool_material is not None:
        tool["tool_material"] = str(tool_material)
    if coating is not None:
        tool["coating"] = str(coating)

    # Replace existing tool with same number, or append
    for i, existing in enumerate(job["tools"]):
        if existing["tool_number"] == tool_number:
            job["tools"][i] = tool
            return tool

    job["tools"].append(tool)
    return tool


def generate_gcode(
    project: Dict[str, Any],
    job_index: int,
) -> Dict[str, Any]:
    """Record metadata for G-code generation.

    The actual G-code generation is performed by the generated FreeCAD
    macro. This function validates the job setup and stores generation
    metadata.

    Returns
    -------
    dict
        G-code generation metadata.

    Raises
    ------
    ValueError
        If the job is missing required setup (stock, tools, operations).
    """
    job = _get_job(project, job_index)

    if job["stock"] is None:
        raise ValueError("Job has no stock defined (call set_stock first)")

    if not job["tools"]:
        raise ValueError("Job has no tools defined (call set_tool first)")

    if not job["operations"]:
        raise ValueError("Job has no operations defined")

    job["gcode"] = {
        "status": "pending",
        "operations_count": len(job["operations"]),
        "tools_count": len(job["tools"]),
    }

    return job["gcode"]
