# ruff: noqa: F403, F405, E501
from .assembly_base import *  # noqa: F403

# fmt: off
from .assembly_p1 import _get_assembly  # noqa: E402,E501
# fmt: on


def remove_part_from_assembly(
    project: Dict[str, Any],
    asm_index: int,
    component_index: int,
) -> Dict[str, Any]:
    """Remove a component from an assembly by its component index.

    Returns the removed component dictionary.

    Raises ``IndexError`` when either index is out of range.
    """
    assembly = _get_assembly(project, asm_index)
    components = assembly["components"]

    if (
        not isinstance(component_index, int)
        or component_index < 0
        or component_index >= len(components)
    ):
        raise IndexError(
            f"Component index {component_index} out of range (0..{len(components) - 1})"
        )

    assembly["solved"] = False
    return components.pop(component_index)


def list_assemblies(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return all assemblies in the project."""
    return project.get(_COLLECTION_KEY, [])


def get_assembly(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Return the assembly at *index* without removing it.

    Raises ``IndexError`` when the index is out of range.
    """
    return _get_assembly(project, index)


def add_assembly_constraint(
    project: Dict[str, Any],
    asm_index: int,
    constraint_type: str,
    component_indices: List[int],
    **params: Any,
) -> Dict[str, Any]:
    """Add a constraint between components in an assembly.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    asm_index : int
        Index of the target assembly.
    constraint_type : str
        One of :data:`VALID_CONSTRAINTS`.
    component_indices : list[int]
        Indices of components involved in the constraint.
    **params
        Extra parameters depending on the constraint type (e.g.
        ``distance``, ``angle``, ``axis``).

    Returns
    -------
    dict
        The newly created constraint entry.

    Raises
    ------
    ValueError
        If *constraint_type* is unknown or *component_indices* is invalid.
    IndexError
        If *asm_index* or any component index is out of range.
    """
    if constraint_type not in VALID_CONSTRAINTS:
        valid = ", ".join(sorted(VALID_CONSTRAINTS))
        raise ValueError(f"Unknown constraint_type '{constraint_type}'. Valid: {valid}")

    assembly = _get_assembly(project, asm_index)

    if not isinstance(component_indices, (list, tuple)) or len(component_indices) == 0:
        raise ValueError("component_indices must be a non-empty list of integers")

    num_components = len(assembly["components"])
    for ci in component_indices:
        if not isinstance(ci, int) or ci < 0 or ci >= num_components:
            raise IndexError(
                f"Component index {ci} out of range (0..{num_components - 1})"
            )

    constraint: Dict[str, Any] = {
        "type": constraint_type,
        "component_indices": list(component_indices),
        "params": dict(params),
    }

    assembly["constraints"].append(constraint)
    assembly["solved"] = False
    return constraint


def solve_assembly(
    project: Dict[str, Any],
    asm_index: int,
) -> Dict[str, Any]:
    """Mark the assembly as solved and return a DOF estimate.

    In the CLI harness the actual constraint solving happens in the
    generated FreeCAD macro. This function records the intent and
    provides a rough degrees-of-freedom estimate.

    Returns
    -------
    dict
        ``{"solved": True, "dof": <int>}``
    """
    assembly = _get_assembly(project, asm_index)
    assembly["solved"] = True

    num_components = len(assembly["components"])
    num_constraints = len(assembly["constraints"])
    dof = max(0, 6 * num_components - num_constraints)

    return {"solved": True, "dof": dof}
