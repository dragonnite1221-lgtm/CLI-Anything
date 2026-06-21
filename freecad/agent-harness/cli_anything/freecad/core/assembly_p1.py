# ruff: noqa: F403, F405, E501
from .assembly_base import *  # noqa: F403


def _next_id(project: Dict[str, Any]) -> int:
    """Return the next available integer ID for assemblies."""
    items = project.get(_COLLECTION_KEY, [])
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


def _unique_name(project: Dict[str, Any], base: str) -> str:
    """Return a unique name derived from *base* inside the assemblies list."""
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


def _get_assembly(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Internal accessor with bounds checking."""
    items = ensure_collection(project, _COLLECTION_KEY)
    if not isinstance(index, int) or index < 0 or index >= len(items):
        raise IndexError(f"Assembly index {index} out of range (0..{len(items) - 1})")
    return items[index]


def create_assembly(
    project: Dict[str, Any],
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new empty assembly and append it to the project.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    name : str or None
        Human-readable label. Auto-generated when *None*.

    Returns
    -------
    dict
        The newly created assembly dictionary.
    """
    items = ensure_collection(project, _COLLECTION_KEY)

    if name is None:
        name = _unique_name(project, "Assembly")

    assembly: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "components": [],
        "constraints": [],
        "solved": False,
    }

    items.append(assembly)
    return assembly


def add_part_to_assembly(
    project: Dict[str, Any],
    asm_index: int,
    part_index: int,
    transform: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Add a part reference to an assembly as a component.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    asm_index : int
        Index of the target assembly.
    part_index : int
        Index of the part in ``project["parts"]``.
    transform : list[float] or None
        Optional ``[x, y, z]`` placement offset. Defaults to ``[0, 0, 0]``.

    Returns
    -------
    dict
        The newly created component entry.

    Raises
    ------
    IndexError
        If *asm_index* or *part_index* is out of range.
    """
    assembly = _get_assembly(project, asm_index)

    parts = project.get("parts", [])
    if not isinstance(part_index, int) or part_index < 0 or part_index >= len(parts):
        raise IndexError(f"Part index {part_index} out of range (0..{len(parts) - 1})")

    if transform is not None:
        transform = _validate_vec3(transform, "transform")
    else:
        transform = [0.0, 0.0, 0.0]

    part = parts[part_index]
    component: Dict[str, Any] = {
        "part_index": part_index,
        "transform": transform,
        "name": part["name"],
    }

    assembly["components"].append(component)
    assembly["solved"] = False
    return component
