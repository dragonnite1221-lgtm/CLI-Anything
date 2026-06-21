# ruff: noqa: F403, F405, E501
from .sketch_base import *  # noqa: F403

# fmt: off
from .sketch_p1 import _get_sketch, _next_constraint_id, _next_element_id, _validate_project  # noqa: E402,E501
# fmt: on


def mirror_elements(
    project: Dict[str, Any],
    sketch_index: int,
    elem_ids: List[int],
    axis_elem_id: int,
) -> Dict[str, Any]:
    """Mirror sketch elements about an axis element.

    Creates mirrored copies of the specified elements and adds symmetric
    constraints linking originals to their mirrors.

    Parameters
    ----------
    project:
        The project dictionary.
    sketch_index:
        Index of the target sketch.
    elem_ids:
        List of element IDs to mirror.
    axis_elem_id:
        ID of the line element to use as mirror axis.

    Returns
    -------
    Dict[str, Any]
        Summary with original IDs, mirrored element IDs, and constraint IDs.
    """
    _validate_project(project)
    sketch = _get_sketch(project, sketch_index)

    if sketch["closed"]:
        raise ValueError("Cannot mirror elements in a closed sketch")

    existing_ids = {el["id"] for el in sketch["elements"]}
    if axis_elem_id not in existing_ids:
        raise ValueError(f"Axis element ID {axis_elem_id} not found in sketch")
    for eid in elem_ids:
        if eid not in existing_ids:
            raise ValueError(f"Element ID {eid} not found in sketch")

    mirrored_ids: List[int] = []
    constraint_ids: List[int] = []

    for eid in elem_ids:
        # Find original element and create a shallow copy
        original = next(el for el in sketch["elements"] if el["id"] == eid)
        mirrored = dict(original)
        mirrored["id"] = _next_element_id(sketch)
        mirrored["mirrored_from"] = eid
        sketch["elements"].append(mirrored)
        mirrored_ids.append(mirrored["id"])

        # Add symmetric constraint (original, mirror, axis)
        constraint: Dict[str, Any] = {
            "id": _next_constraint_id(sketch),
            "type": "symmetric",
            "elements": [eid, mirrored["id"], axis_elem_id],
            "value": None,
        }
        sketch["constraints"].append(constraint)
        constraint_ids.append(constraint["id"])

    return {
        "original_ids": list(elem_ids),
        "mirrored_ids": mirrored_ids,
        "constraint_ids": constraint_ids,
        "axis_elem_id": axis_elem_id,
    }


def offset_wire(
    project: Dict[str, Any],
    sketch_index: int,
    elem_ids: List[int],
    distance: float,
) -> Dict[str, Any]:
    """Offset a wire of elements by a given distance.

    Creates offset copies of the specified elements in the sketch.

    Parameters
    ----------
    project:
        The project dictionary.
    sketch_index:
        Index of the target sketch.
    elem_ids:
        List of element IDs forming the wire to offset.
    distance:
        Offset distance.  Positive offsets outward, negative inward.

    Returns
    -------
    Dict[str, Any]
        Summary with original IDs and new offset element IDs.
    """
    _validate_project(project)
    sketch = _get_sketch(project, sketch_index)

    if sketch["closed"]:
        raise ValueError("Cannot offset elements in a closed sketch")

    distance = float(distance)
    if distance == 0:
        raise ValueError("Offset distance must be non-zero")

    existing_ids = {el["id"] for el in sketch["elements"]}
    for eid in elem_ids:
        if eid not in existing_ids:
            raise ValueError(f"Element ID {eid} not found in sketch")

    offset_ids: List[int] = []
    for eid in elem_ids:
        original = next(el for el in sketch["elements"] if el["id"] == eid)
        offset_elem = dict(original)
        offset_elem["id"] = _next_element_id(sketch)
        offset_elem["offset_from"] = eid
        offset_elem["offset_distance"] = distance
        sketch["elements"].append(offset_elem)
        offset_ids.append(offset_elem["id"])

    return {
        "original_ids": list(elem_ids),
        "offset_ids": offset_ids,
        "distance": distance,
    }
