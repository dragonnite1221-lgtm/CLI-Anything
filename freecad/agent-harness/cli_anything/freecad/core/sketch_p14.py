# ruff: noqa: F403, F405, E501
from .sketch_base import *  # noqa: F403

# fmt: off
from .sketch_p1 import _get_sketch, _validate_project  # noqa: E402,E501
# fmt: on


def trim_element(
    project: Dict[str, Any],
    sketch_index: int,
    elem_id: int,
    keep_side: str = "start",
) -> Dict[str, Any]:
    """Trim an element at its intersection point.

    This is a simplified trim that marks the element with a trim point
    indicator and the side to keep.

    Parameters
    ----------
    project:
        The project dictionary.
    sketch_index:
        Index of the target sketch.
    elem_id:
        ID of the element to trim.
    keep_side:
        Which side to keep: ``"start"`` or ``"end"``.

    Returns
    -------
    Dict[str, Any]
        The updated element dictionary with trim metadata.
    """
    _validate_project(project)
    sketch = _get_sketch(project, sketch_index)

    if sketch["closed"]:
        raise ValueError("Cannot trim elements in a closed sketch")

    keep_side = keep_side.lower()
    if keep_side not in ("start", "end"):
        raise ValueError(f"keep_side must be 'start' or 'end', got '{keep_side}'")

    for elem in sketch["elements"]:
        if elem["id"] == elem_id:
            elem["trimmed"] = True
            elem["trim_keep_side"] = keep_side
            return elem

    raise KeyError(f"Element ID {elem_id} not found in sketch")


def extend_element(
    project: Dict[str, Any],
    sketch_index: int,
    elem_id: int,
    target_elem_id: int,
) -> Dict[str, Any]:
    """Extend an element to reach a target element.

    Marks the element with extension metadata referencing the target.

    Parameters
    ----------
    project:
        The project dictionary.
    sketch_index:
        Index of the target sketch.
    elem_id:
        ID of the element to extend.
    target_elem_id:
        ID of the target element to extend towards.

    Returns
    -------
    Dict[str, Any]
        The updated element dictionary with extension metadata.
    """
    _validate_project(project)
    sketch = _get_sketch(project, sketch_index)

    if sketch["closed"]:
        raise ValueError("Cannot extend elements in a closed sketch")

    existing_ids = {el["id"] for el in sketch["elements"]}
    if elem_id not in existing_ids:
        raise KeyError(f"Element ID {elem_id} not found in sketch")
    if target_elem_id not in existing_ids:
        raise KeyError(f"Target element ID {target_elem_id} not found in sketch")
    if elem_id == target_elem_id:
        raise ValueError("Element and target must be different")

    for elem in sketch["elements"]:
        if elem["id"] == elem_id:
            elem["extended"] = True
            elem["extend_target_id"] = target_elem_id
            return elem

    raise KeyError(f"Element ID {elem_id} not found in sketch")
