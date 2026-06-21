# ruff: noqa: F403, F405, E501
from .parts_base import *  # noqa: F403

# fmt: off
from .parts_p1 import _next_id, _unique_name, _validate_vec3  # noqa: E402,E501
from .parts_p3 import get_part  # noqa: E402,E501
# fmt: on


def transform_part(
    project: Dict[str, Any],
    index: int,
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Update the placement of the part at *index*.

    Only the supplied vectors are changed; the other is left untouched.

    Returns the updated part dictionary.
    """
    part = get_part(project, index)

    if position is not None:
        part["placement"]["position"] = _validate_vec3(position, "position")
    if rotation is not None:
        part["placement"]["rotation"] = _validate_vec3(rotation, "rotation")

    return part


def boolean_op(
    project: Dict[str, Any],
    op: str,
    base_index: int,
    tool_index: int,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Perform a boolean operation between two parts.

    Creates a new part of ``type=op`` that references the *base* and *tool*
    parts by their IDs. Both source parts are marked ``visible=False``.

    Parameters
    ----------
    op : str
        One of ``"cut"``, ``"fuse"``, or ``"common"``.
    base_index : int
        Index of the base (kept) shape in ``project["parts"]``.
    tool_index : int
        Index of the tool shape in ``project["parts"]``.
    name : str or None
        Label for the result. Auto-generated when *None*.

    Returns
    -------
    dict
        The newly created boolean-result part.

    Raises
    ------
    ValueError
        If *op* is unknown or indices are equal.
    IndexError
        If either index is out of range.
    """
    if op not in BOOLEAN_OPS:
        valid = ", ".join(sorted(BOOLEAN_OPS))
        raise ValueError(f"Unknown boolean op '{op}'. Valid: {valid}")

    if base_index == tool_index:
        raise ValueError("base_index and tool_index must differ")

    base_part = get_part(project, base_index)
    tool_part = get_part(project, tool_index)

    # Mark operands as hidden
    base_part["visible"] = False
    tool_part["visible"] = False

    # Ensure the parts list exists
    if "parts" not in project:
        project["parts"] = []

    if name is None:
        base_name = op.capitalize()
        name = _unique_name(project, base_name)

    result: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "type": op,
        "params": {
            "base_id": base_part["id"],
            "tool_id": tool_part["id"],
        },
        "placement": {
            "position": [0.0, 0.0, 0.0],
            "rotation": [0.0, 0.0, 0.0],
        },
        "material_index": None,
        "visible": True,
    }

    project["parts"].append(result)
    return result
