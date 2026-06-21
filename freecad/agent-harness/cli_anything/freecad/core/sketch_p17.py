# ruff: noqa: F403, F405, E501
from .sketch_base import *  # noqa: F403

# fmt: off
from .sketch_p1 import _get_sketch, _next_element_id, _validate_project  # noqa: E402,E501
# fmt: on


def add_external_from_face(
    project: Dict[str, Any],
    sketch_index: int,
    part_index: int,
    face_ref: str,
) -> Dict[str, Any]:
    """Create external geometry from a face selection (FreeCAD 1.1).

    Projects the boundary of the referenced face onto the sketch plane.

    Parameters
    ----------
    project:
        The project dictionary.
    sketch_index:
        Index of the target sketch.
    part_index:
        Index of the body/part containing the face.
    face_ref:
        Face reference identifier (e.g. ``"Face1"``).

    Returns
    -------
    Dict[str, Any]
        The newly created face reference element.
    """
    _validate_project(project)
    sketch = _get_sketch(project, sketch_index)

    if sketch["closed"]:
        raise ValueError("Cannot add elements to a closed sketch")

    element: Dict[str, Any] = {
        "id": _next_element_id(sketch),
        "type": "face_reference",
        "part_index": int(part_index),
        "face_ref": face_ref,
        "construction": True,
    }

    sketch["elements"].append(element)
    return element
