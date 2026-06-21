# ruff: noqa: F403, F405, E501
from .cam_base import *  # noqa: F403

# fmt: off
from .cam_p1 import _get_job  # noqa: E402,E501
# fmt: on


def add_profile_op(
    project: Dict[str, Any],
    job_index: int,
    faces: str = "all",
    depth: Optional[float] = None,
    step_down: float = 1.0,
    passes: Optional[int] = None,
    finishing_pass: bool = False,
) -> Dict[str, Any]:
    """Add a profile (contour) machining operation.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    job_index : int
        Index of the target job.
    faces : str
        Face selection (``"all"`` or specific face references).
    depth : float or None
        Total cut depth. When *None*, derived from part geometry.
    step_down : float
        Depth of cut per pass.
    passes : int or None
        Explicit number of passes. When provided, overrides automatic
        calculation from *step_down*.
    finishing_pass : bool
        When *True*, adds a light finishing pass after roughing.

    Returns
    -------
    dict
        The operation entry.
    """
    job = _get_job(project, job_index)

    op: Dict[str, Any] = {
        "type": "profile",
        "faces": faces,
        "depth": float(depth) if depth is not None else None,
        "step_down": float(step_down),
        "passes": int(passes) if passes is not None else None,
        "finishing_pass": finishing_pass,
    }

    job["operations"].append(op)
    return op


def add_pocket_op(
    project: Dict[str, Any],
    job_index: int,
    faces: str = "all",
    depth: Optional[float] = None,
    step_down: float = 1.0,
    step_over: float = 0.5,
) -> Dict[str, Any]:
    """Add a pocket machining operation.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    job_index : int
        Index of the target job.
    faces : str
        Face selection (``"all"`` or specific face references).
    depth : float or None
        Total pocket depth. When *None*, derived from part geometry.
    step_down : float
        Depth of cut per pass.
    step_over : float
        Lateral step-over as a fraction of tool diameter (0.0 to 1.0).

    Returns
    -------
    dict
        The operation entry.
    """
    job = _get_job(project, job_index)

    op: Dict[str, Any] = {
        "type": "pocket",
        "faces": faces,
        "depth": float(depth) if depth is not None else None,
        "step_down": float(step_down),
        "step_over": float(step_over),
    }

    job["operations"].append(op)
    return op


def add_drilling_op(
    project: Dict[str, Any],
    job_index: int,
    holes: str = "all",
    depth: Optional[float] = None,
    peck_depth: Optional[float] = None,
) -> Dict[str, Any]:
    """Add a drilling operation.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    job_index : int
        Index of the target job.
    holes : str
        Hole selection (``"all"`` or specific hole references).
    depth : float or None
        Total drill depth. When *None*, derived from part geometry.
    peck_depth : float or None
        Peck drilling increment. When *None*, drilling is continuous.

    Returns
    -------
    dict
        The operation entry.
    """
    job = _get_job(project, job_index)

    op: Dict[str, Any] = {
        "type": "drilling",
        "holes": holes,
        "depth": float(depth) if depth is not None else None,
        "peck_depth": float(peck_depth) if peck_depth is not None else None,
    }

    job["operations"].append(op)
    return op
