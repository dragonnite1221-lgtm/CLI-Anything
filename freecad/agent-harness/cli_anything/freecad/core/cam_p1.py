# ruff: noqa: F403, F405, E501
from .cam_base import *  # noqa: F403


def _next_id(project: Dict[str, Any]) -> int:
    """Return the next available integer ID for CAM jobs."""
    items = project.get(_COLLECTION_KEY, [])
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


def _unique_name(project: Dict[str, Any], base: str) -> str:
    """Return a unique name derived from *base* inside the jobs list."""
    existing = {item["name"] for item in project.get(_COLLECTION_KEY, [])}
    if base not in existing:
        return base
    counter = 2
    while f"{base}_{counter}" in existing:
        counter += 1
    return f"{base}_{counter}"


def _get_job(project: Dict[str, Any], job_index: int) -> Dict[str, Any]:
    """Internal accessor with bounds checking."""
    items = ensure_collection(project, _COLLECTION_KEY)
    if not isinstance(job_index, int) or job_index < 0 or job_index >= len(items):
        raise IndexError(f"Job index {job_index} out of range (0..{len(items) - 1})")
    return items[job_index]


def new_job(
    project: Dict[str, Any],
    part_index: int,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new CAM job for a part and append it to the project.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    part_index : int
        Index of the source part in ``project["parts"]``.
    name : str or None
        Human-readable label. Auto-generated when *None*.

    Returns
    -------
    dict
        The newly created job dictionary.

    Raises
    ------
    IndexError
        If *part_index* is out of range.
    """
    items = ensure_collection(project, _COLLECTION_KEY)

    parts = project.get("parts", [])
    if not isinstance(part_index, int) or part_index < 0 or part_index >= len(parts):
        raise IndexError(f"Part index {part_index} out of range (0..{len(parts) - 1})")

    if name is None:
        name = _unique_name(project, "Job")

    job: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "source_part_index": part_index,
        "stock": None,
        "tools": [],
        "operations": [],
        "gcode": None,
    }

    items.append(job)
    return job


def set_stock(
    project: Dict[str, Any],
    job_index: int,
    stock_type: str = "box",
    extra_x: float = 2.0,
    extra_y: float = 2.0,
    extra_z: float = 2.0,
) -> Dict[str, Any]:
    """Define the raw stock material for a CAM job.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    job_index : int
        Index of the target job.
    stock_type : str
        Stock shape type (``"box"``, ``"cylinder"``, ``"from_part"``).
    extra_x : float
        Extra material on the X axis (each side).
    extra_y : float
        Extra material on the Y axis (each side).
    extra_z : float
        Extra material on the Z axis (each side).

    Returns
    -------
    dict
        The stock definition.

    Raises
    ------
    ValueError
        If *stock_type* is unknown.
    """
    if stock_type not in VALID_STOCK_TYPES:
        valid = ", ".join(sorted(VALID_STOCK_TYPES))
        raise ValueError(f"Unknown stock_type '{stock_type}'. Valid: {valid}")

    job = _get_job(project, job_index)

    stock: Dict[str, Any] = {
        "type": stock_type,
        "extra_x": float(extra_x),
        "extra_y": float(extra_y),
        "extra_z": float(extra_z),
    }

    job["stock"] = stock
    return stock
