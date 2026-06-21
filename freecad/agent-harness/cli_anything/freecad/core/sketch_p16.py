# ruff: noqa: F403, F405, E501
from .sketch_base import *  # noqa: F403

# fmt: off
from .sketch_p1 import _get_sketch, _next_element_id, _validate_project  # noqa: E402,E501
# fmt: on


def set_construction(
    project: Dict[str, Any],
    sketch_index: int,
    elem_id: int,
    flag: bool = True,
) -> Dict[str, Any]:
    """Toggle the construction geometry flag on an element.

    Construction geometry is used as reference and does not form part of
    the sketch profile.

    Parameters
    ----------
    project:
        The project dictionary.
    sketch_index:
        Index of the target sketch.
    elem_id:
        ID of the element.
    flag:
        ``True`` to mark as construction, ``False`` to unmark.

    Returns
    -------
    Dict[str, Any]
        The updated element dictionary.
    """
    _validate_project(project)
    sketch = _get_sketch(project, sketch_index)

    for elem in sketch["elements"]:
        if elem["id"] == elem_id:
            elem["construction"] = bool(flag)
            return elem

    raise KeyError(f"Element ID {elem_id} not found in sketch")


def project_external(
    project: Dict[str, Any],
    sketch_index: int,
    part_index: int,
    edge_ref: Optional[str] = None,
    mode: str = "projection",
) -> Dict[str, Any]:
    """Project external geometry into the sketch as a reference element.

    Parameters
    ----------
    project:
        The project dictionary.
    sketch_index:
        Index of the target sketch.
    part_index:
        Index of the body/part containing the external geometry.
    edge_ref:
        Optional edge reference identifier (e.g. ``"Edge1"``).
        If ``None``, the entire shape is projected.
    mode:
        External geometry mode: ``"projection"`` or ``"reference"``
        (FreeCAD 1.1).

    Returns
    -------
    Dict[str, Any]
        The newly created external reference element.
    """
    _validate_project(project)
    sketch = _get_sketch(project, sketch_index)

    if sketch["closed"]:
        raise ValueError("Cannot add elements to a closed sketch")

    valid_modes = {"projection", "reference"}
    if mode not in valid_modes:
        raise ValueError(
            f"Invalid mode '{mode}'. Must be one of: {', '.join(sorted(valid_modes))}"
        )

    element: Dict[str, Any] = {
        "id": _next_element_id(sketch),
        "type": "external_reference",
        "part_index": int(part_index),
        "edge_ref": edge_ref,
        "mode": mode,
        "construction": True,
    }

    sketch["elements"].append(element)
    return element


def intersection_external(
    project: Dict[str, Any],
    sketch_index: int,
    body_index: int,
) -> Dict[str, Any]:
    """Create external geometry from sketch-plane intersection with a body (FreeCAD 1.1).

    Generates external geometry elements at the intersection of the sketch
    plane with the specified body geometry.

    Parameters
    ----------
    project:
        The project dictionary.
    sketch_index:
        Index of the target sketch.
    body_index:
        Index of the body to intersect with the sketch plane.

    Returns
    -------
    Dict[str, Any]
        The newly created intersection reference element.
    """
    _validate_project(project)
    sketch = _get_sketch(project, sketch_index)

    if sketch["closed"]:
        raise ValueError("Cannot add elements to a closed sketch")

    element: Dict[str, Any] = {
        "id": _next_element_id(sketch),
        "type": "intersection_reference",
        "body_index": int(body_index),
        "construction": True,
    }

    sketch["elements"].append(element)
    return element
