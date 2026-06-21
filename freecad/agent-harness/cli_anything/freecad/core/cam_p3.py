# ruff: noqa: F403, F405, E501
from .cam_base import *  # noqa: F403

# fmt: off
from .cam_p1 import _get_job  # noqa: E402,E501
# fmt: on


def add_facing_op(
    project: Dict[str, Any],
    job_index: int,
    depth: float = 1.0,
    step_over: float = 0.5,
) -> Dict[str, Any]:
    """Add a facing (surface levelling) operation.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    job_index : int
        Index of the target job.
    depth : float
        Total material to remove from the top surface.
    step_over : float
        Lateral step-over as a fraction of tool diameter (0.0 to 1.0).

    Returns
    -------
    dict
        The operation entry.
    """
    job = _get_job(project, job_index)

    op: Dict[str, Any] = {
        "type": "facing",
        "depth": float(depth),
        "step_over": float(step_over),
    }

    job["operations"].append(op)
    return op


def add_tapping_op(
    project: Dict[str, Any],
    job_index: int,
    holes: str = "all",
    depth: Optional[float] = None,
    thread_pitch: float = 1.5,
    right_hand: bool = True,
) -> Dict[str, Any]:
    """Add a tapping operation (G84 right-hand / G74 left-hand).

    FreeCAD 1.1 introduces native tapping cycle support.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    job_index : int
        Index of the target job.
    holes : str
        Hole selection (``"all"`` or specific hole references).
    depth : float or None
        Total tap depth. When *None*, derived from part geometry.
    thread_pitch : float
        Thread pitch in project units.
    right_hand : bool
        When *True*, uses G84 (right-hand thread). When *False*,
        uses G74 (left-hand thread).

    Returns
    -------
    dict
        The operation entry.
    """
    job = _get_job(project, job_index)

    op: Dict[str, Any] = {
        "type": "tapping",
        "holes": holes,
        "depth": float(depth) if depth is not None else None,
        "thread_pitch": float(thread_pitch),
        "right_hand": right_hand,
        "g_code": "G84" if right_hand else "G74",
    }

    job["operations"].append(op)
    return op
