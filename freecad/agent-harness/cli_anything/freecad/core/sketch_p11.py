# ruff: noqa: F403, F405, E501
from .sketch_base import *  # noqa: F403

# fmt: off
from .sketch_p1 import _get_sketch, _validate_point_2d, _validate_project  # noqa: E402,E501
# fmt: on


def edit_element(
    project: Dict[str, Any],
    sketch_index: int,
    elem_id: int,
    **props: Any,
) -> Dict[str, Any]:
    """Modify properties of an existing sketch element.

    Parameters
    ----------
    project:
        The project dictionary.
    sketch_index:
        Index of the target sketch.
    elem_id:
        ID of the element to edit.
    **props:
        Key-value pairs of properties to update (e.g. ``start``, ``end``,
        ``center``, ``radius``).

    Returns
    -------
    Dict[str, Any]
        The updated element dictionary.

    Raises
    ------
    ValueError
        If the sketch is closed or no properties are provided.
    KeyError
        If the element ID is not found.
    """
    _validate_project(project)
    sketch = _get_sketch(project, sketch_index)

    if sketch["closed"]:
        raise ValueError("Cannot edit elements in a closed sketch")

    if not props:
        raise ValueError("At least one property must be provided to edit")

    for elem in sketch["elements"]:
        if elem["id"] == elem_id:
            # Validate point-like properties
            for key in ("start", "end", "center", "position"):
                if key in props:
                    props[key] = _validate_point_2d(props[key], key)
            if "radius" in props:
                props["radius"] = float(props["radius"])
                if props["radius"] <= 0:
                    raise ValueError(f"Radius must be positive, got {props['radius']}")
            elem.update(props)
            return elem

    raise KeyError(f"Element ID {elem_id} not found in sketch")


def remove_element(
    project: Dict[str, Any],
    sketch_index: int,
    elem_id: int,
) -> Dict[str, Any]:
    """Remove an element and all its associated constraints from a sketch.

    Parameters
    ----------
    project:
        The project dictionary.
    sketch_index:
        Index of the target sketch.
    elem_id:
        ID of the element to remove.

    Returns
    -------
    Dict[str, Any]
        Summary with removed element ID and list of removed constraint IDs.

    Raises
    ------
    ValueError
        If the sketch is closed.
    KeyError
        If the element ID is not found.
    """
    _validate_project(project)
    sketch = _get_sketch(project, sketch_index)

    if sketch["closed"]:
        raise ValueError("Cannot remove elements from a closed sketch")

    # Find and remove the element
    found = False
    for i, elem in enumerate(sketch["elements"]):
        if elem["id"] == elem_id:
            sketch["elements"].pop(i)
            found = True
            break

    if not found:
        raise KeyError(f"Element ID {elem_id} not found in sketch")

    # Remove constraints that reference this element
    removed_constraints: List[int] = []
    remaining: List[Dict[str, Any]] = []
    for c in sketch["constraints"]:
        if elem_id in c.get("elements", []):
            removed_constraints.append(c["id"])
        else:
            remaining.append(c)
    sketch["constraints"] = remaining

    return {
        "removed_element_id": elem_id,
        "removed_constraint_ids": removed_constraints,
    }
