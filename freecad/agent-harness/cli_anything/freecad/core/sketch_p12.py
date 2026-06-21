# ruff: noqa: F403, F405, E501
from .sketch_base import *  # noqa: F403

# fmt: off
from .sketch_p1 import _get_sketch, _validate_project  # noqa: E402,E501
# fmt: on


def remove_constraint(
    project: Dict[str, Any],
    sketch_index: int,
    constraint_id: int,
) -> Dict[str, Any]:
    """Remove a specific constraint from a sketch.

    Parameters
    ----------
    project:
        The project dictionary.
    sketch_index:
        Index of the target sketch.
    constraint_id:
        ID of the constraint to remove.

    Returns
    -------
    Dict[str, Any]
        The removed constraint dictionary.

    Raises
    ------
    ValueError
        If the sketch is closed.
    KeyError
        If the constraint ID is not found.
    """
    _validate_project(project)
    sketch = _get_sketch(project, sketch_index)

    if sketch["closed"]:
        raise ValueError("Cannot remove constraints from a closed sketch")

    for i, c in enumerate(sketch["constraints"]):
        if c["id"] == constraint_id:
            return sketch["constraints"].pop(i)

    raise KeyError(f"Constraint ID {constraint_id} not found in sketch")


def edit_constraint(
    project: Dict[str, Any],
    sketch_index: int,
    constraint_id: int,
    value: Optional[float] = None,
) -> Dict[str, Any]:
    """Change the value of an existing constraint.

    Parameters
    ----------
    project:
        The project dictionary.
    sketch_index:
        Index of the target sketch.
    constraint_id:
        ID of the constraint to edit.
    value:
        New numeric value for the constraint.

    Returns
    -------
    Dict[str, Any]
        The updated constraint dictionary.

    Raises
    ------
    ValueError
        If the sketch is closed or the constraint is not a valued type.
    KeyError
        If the constraint ID is not found.
    """
    _validate_project(project)
    sketch = _get_sketch(project, sketch_index)

    if sketch["closed"]:
        raise ValueError("Cannot edit constraints in a closed sketch")

    for c in sketch["constraints"]:
        if c["id"] == constraint_id:
            if c["type"] not in VALUED_CONSTRAINTS:
                raise ValueError(
                    f"Constraint type '{c['type']}' does not accept a numeric value"
                )
            if value is not None:
                value = float(value)
            c["value"] = value
            return c

    raise KeyError(f"Constraint ID {constraint_id} not found in sketch")
