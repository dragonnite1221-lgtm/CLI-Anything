# ruff: noqa: F403, F405, E501
from .sketch_base import *  # noqa: F403

# fmt: off
from .sketch_p1 import _get_sketch, _next_element_id, _validate_point_2d, _validate_project  # noqa: E402,E501
# fmt: on


def list_sketches(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return a summary list of all sketches in the project.

    Parameters
    ----------
    project:
        The project dictionary.

    Returns
    -------
    List[Dict[str, Any]]
        List of sketch summaries with index, id, name, plane, element
        count, constraint count, and closed status.
    """
    _validate_project(project)

    result: List[Dict[str, Any]] = []
    for i, sk in enumerate(project["sketches"]):
        result.append(
            {
                "index": i,
                "id": sk.get("id", i),
                "name": sk.get("name", f"Sketch {i}"),
                "plane": sk.get("plane", "XY"),
                "offset": sk.get("offset", 0.0),
                "element_count": len(sk.get("elements", [])),
                "constraint_count": len(sk.get("constraints", [])),
                "closed": sk.get("closed", False),
            }
        )
    return result


def get_sketch(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Return the full sketch dictionary at the given index.

    Parameters
    ----------
    project:
        The project dictionary.
    index:
        Sketch index.

    Returns
    -------
    Dict[str, Any]
        The complete sketch dictionary.
    """
    _validate_project(project)
    return _get_sketch(project, index)


def add_point(
    project: Dict[str, Any],
    sketch_index: int,
    position: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Add a point element to a sketch.

    Parameters
    ----------
    project:
        The project dictionary.
    sketch_index:
        Index of the target sketch.
    position:
        Point position ``[x, y]``.  Defaults to ``[0, 0]``.

    Returns
    -------
    Dict[str, Any]
        The newly created point element.
    """
    _validate_project(project)
    sketch = _get_sketch(project, sketch_index)

    if sketch["closed"]:
        raise ValueError("Cannot add elements to a closed sketch")

    position = _validate_point_2d(
        position if position is not None else [0, 0], "position"
    )

    element: Dict[str, Any] = {
        "id": _next_element_id(sketch),
        "type": "point",
        "position": position,
    }

    sketch["elements"].append(element)
    return element
