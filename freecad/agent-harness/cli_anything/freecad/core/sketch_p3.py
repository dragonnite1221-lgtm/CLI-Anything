# ruff: noqa: F403, F405, E501
from .sketch_base import *  # noqa: F403

# fmt: off
from .sketch_p1 import _get_sketch, _next_constraint_id, _next_element_id, _validate_point_2d, _validate_project  # noqa: E402,E501
# fmt: on


def add_rectangle(
    project: Dict[str, Any],
    sketch_index: int,
    corner: Optional[List[float]] = None,
    width: float = 10.0,
    height: float = 10.0,
) -> Dict[str, Any]:
    """Add a rectangle to a sketch (4 lines + 4 perpendicular constraints).

    The rectangle is axis-aligned with its bottom-left at *corner*.

    Parameters
    ----------
    project:
        The project dictionary.
    sketch_index:
        Index of the target sketch.
    corner:
        Bottom-left corner ``[x, y]``.  Defaults to ``[0, 0]``.
    width:
        Rectangle width (X extent).  Must be positive.
    height:
        Rectangle height (Y extent).  Must be positive.

    Returns
    -------
    Dict[str, Any]
        Summary containing the four line element IDs and four constraint IDs.
    """
    _validate_project(project)
    sketch = _get_sketch(project, sketch_index)

    if sketch["closed"]:
        raise ValueError("Cannot add elements to a closed sketch")

    corner = _validate_point_2d(corner if corner is not None else [0, 0], "corner")
    width = float(width)
    height = float(height)
    if width <= 0:
        raise ValueError(f"Width must be positive, got {width}")
    if height <= 0:
        raise ValueError(f"Height must be positive, got {height}")

    x, y = corner
    # Four corners: BL, BR, TR, TL
    bl = [x, y]
    br = [x + width, y]
    tr = [x + width, y + height]
    tl = [x, y + height]

    # Create four line elements
    lines: List[Dict[str, Any]] = []
    for start, end in [(bl, br), (br, tr), (tr, tl), (tl, bl)]:
        elem: Dict[str, Any] = {
            "id": _next_element_id(sketch),
            "type": "line",
            "start": list(start),
            "end": list(end),
        }
        sketch["elements"].append(elem)
        lines.append(elem)

    # Add 4 coincident constraints at the corners (each pair of adjacent lines)
    constraint_ids: List[int] = []
    for i in range(4):
        j = (i + 1) % 4
        constraint: Dict[str, Any] = {
            "id": _next_constraint_id(sketch),
            "type": "coincident",
            "elements": [lines[i]["id"], lines[j]["id"]],
            "value": None,
        }
        sketch["constraints"].append(constraint)
        constraint_ids.append(constraint["id"])

    return {
        "type": "rectangle",
        "line_ids": [line["id"] for line in lines],
        "constraint_ids": constraint_ids,
        "corner": corner,
        "width": width,
        "height": height,
    }
