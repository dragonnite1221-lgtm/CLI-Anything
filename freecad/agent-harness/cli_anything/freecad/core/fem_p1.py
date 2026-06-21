# ruff: noqa: F403, F405, E501
from .fem_base import *  # noqa: F403


def _next_id(project: Dict[str, Any]) -> int:
    """Return the next available integer ID for FEM analyses."""
    items = project.get(_COLLECTION_KEY, [])
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


def _unique_name(project: Dict[str, Any], base: str) -> str:
    """Return a unique name derived from *base* inside the analyses list."""
    existing = {item["name"] for item in project.get(_COLLECTION_KEY, [])}
    if base not in existing:
        return base
    counter = 2
    while f"{base}_{counter}" in existing:
        counter += 1
    return f"{base}_{counter}"


def _validate_vec3(value: Any, label: str) -> List[float]:
    """Validate that *value* is a list of exactly three numbers."""
    if not isinstance(value, (list, tuple)):
        raise ValueError(
            f"{label} must be a list of 3 numbers, got {type(value).__name__}"
        )
    if len(value) != 3:
        raise ValueError(f"{label} must have exactly 3 elements, got {len(value)}")
    try:
        return [float(v) for v in value]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} elements must be numeric: {exc}") from exc


def _get_analysis(project: Dict[str, Any], ai: int) -> Dict[str, Any]:
    """Internal accessor with bounds checking.

    Parameters
    ----------
    ai : int
        Analysis index.
    """
    items = ensure_collection(project, _COLLECTION_KEY)
    if not isinstance(ai, int) or ai < 0 or ai >= len(items):
        raise IndexError(f"Analysis index {ai} out of range (0..{len(items) - 1})")
    return items[ai]


def new_analysis(
    project: Dict[str, Any],
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new FEM analysis and append it to the project.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    name : str or None
        Human-readable label. Auto-generated when *None*.

    Returns
    -------
    dict
        The newly created analysis dictionary.
    """
    items = ensure_collection(project, _COLLECTION_KEY)

    if name is None:
        name = _unique_name(project, "FEMAnalysis")

    analysis: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "constraints": [],
        "material_index": None,
        "mesh_params": None,
        "solver": None,
        "results": None,
    }

    items.append(analysis)
    return analysis


def add_fixed_constraint(
    project: Dict[str, Any],
    ai: int,
    references: List[Any],
) -> Dict[str, Any]:
    """Add a fixed (zero-displacement) boundary constraint.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    ai : int
        Analysis index.
    references : list
        Geometry references (faces, edges, vertices) to fix.

    Returns
    -------
    dict
        The constraint entry.
    """
    analysis = _get_analysis(project, ai)

    constraint: Dict[str, Any] = {
        "type": "fixed",
        "references": list(references),
    }

    analysis["constraints"].append(constraint)
    return constraint
