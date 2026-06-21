# ruff: noqa: F403, F405, E501
from .sketch_base import *  # noqa: F403

# fmt: off
from .sketch_p1 import _get_sketch, _next_constraint_id, _validate_project  # noqa: E402,E501
# fmt: on


def add_constraint(
    project: Dict[str, Any],
    sketch_index: int,
    constraint_type: str,
    elements: List[int],
    value: Optional[float] = None,
) -> Dict[str, Any]:
    """Add a geometric or dimensional constraint to a sketch.

    Parameters
    ----------
    project:
        The project dictionary.
    sketch_index:
        Index of the target sketch.
    constraint_type:
        One of: ``"coincident"``, ``"horizontal"``, ``"vertical"``,
        ``"parallel"``, ``"perpendicular"``, ``"equal"``, ``"fixed"``,
        ``"distance"``, ``"angle"``, ``"radius"``, ``"tangent"``.
    elements:
        List of element IDs (indices within the sketch's ``elements``
        list) that participate in the constraint.
    value:
        Numeric value for dimensional constraints (``"distance"``,
        ``"angle"``, ``"radius"``).

    Returns
    -------
    Dict[str, Any]
        The newly created constraint dictionary.

    Raises
    ------
    ValueError
        If the constraint type is unknown, required value is missing,
        or element references are invalid.
    """
    _validate_project(project)
    sketch = _get_sketch(project, sketch_index)

    if sketch["closed"]:
        raise ValueError("Cannot add constraints to a closed sketch")

    constraint_type = constraint_type.lower()
    if constraint_type not in VALID_CONSTRAINT_TYPES:
        raise ValueError(
            f"Unknown constraint type '{constraint_type}'. "
            f"Valid types: {', '.join(sorted(VALID_CONSTRAINT_TYPES))}"
        )

    if not isinstance(elements, (list, tuple)) or len(elements) == 0:
        raise ValueError("Elements must be a non-empty list of element IDs")

    # Validate minimum element count
    min_elements = CONSTRAINT_MIN_ELEMENTS[constraint_type]
    if len(elements) < min_elements:
        raise ValueError(
            f"Constraint '{constraint_type}' requires at least {min_elements} "
            f"element(s), got {len(elements)}"
        )

    # Validate element IDs exist in the sketch
    existing_ids = {el["id"] for el in sketch["elements"]}
    for eid in elements:
        if eid not in existing_ids:
            raise ValueError(
                f"Element ID {eid} not found in sketch. "
                f"Existing IDs: {sorted(existing_ids)}"
            )

    # Validate value for dimensional constraints
    if constraint_type in VALUED_CONSTRAINTS:
        if value is None:
            raise ValueError(f"Constraint '{constraint_type}' requires a numeric value")
        value = float(value)
        if constraint_type == "radius" and value <= 0:
            raise ValueError(f"Radius constraint value must be positive, got {value}")
        if constraint_type == "distance" and value < 0:
            raise ValueError(
                f"Distance constraint value must be non-negative, got {value}"
            )
    else:
        # Geometric constraints ignore value
        value = None

    constraint: Dict[str, Any] = {
        "id": _next_constraint_id(sketch),
        "type": constraint_type,
        "elements": list(elements),
        "value": value,
    }

    sketch["constraints"].append(constraint)
    return constraint


def close_sketch(
    project: Dict[str, Any],
    sketch_index: int,
) -> Dict[str, Any]:
    """Mark a sketch as closed, preventing further modifications.

    Parameters
    ----------
    project:
        The project dictionary.
    sketch_index:
        Index of the target sketch.

    Returns
    -------
    Dict[str, Any]
        The closed sketch dictionary.
    """
    _validate_project(project)
    sketch = _get_sketch(project, sketch_index)

    if sketch["closed"]:
        raise ValueError(f"Sketch '{sketch['name']}' is already closed")

    sketch["closed"] = True
    return sketch
