# ruff: noqa: F403, F405, E501
from .draft_base import *  # noqa: F403

# fmt: off
from .draft_p1 import _get_draft  # noqa: E402,E501
# fmt: on


def draft_to_sketch(
    project: Dict[str, Any],
    index: int,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Convert a draft object to a sketch in ``project["sketches"]``.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    index : int
        Index of the draft object to convert.
    name : str or None
        Label for the resulting sketch.

    Returns
    -------
    dict
        The newly created sketch entry.
    """
    obj = _get_draft(project, index)
    sketches = ensure_collection(project, "sketches")

    if name is None:
        base = f"{obj['name']}_Sketch"
        existing = {s["name"] for s in sketches}
        if base in existing:
            counter = 2
            while f"{base}_{counter}" in existing:
                counter += 1
            base = f"{base}_{counter}"
        name = base

    sketch_id = max((s["id"] for s in sketches), default=0) + 1

    sketch: Dict[str, Any] = {
        "id": sketch_id,
        "name": name,
        "type": "from_draft",
        "source_draft_id": obj["id"],
        "elements": [],
        "constraints": [],
    }

    sketches.append(sketch)
    return sketch


def list_draft_objects(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return all draft objects in the project.

    Parameters
    ----------
    project : dict
        The project state dictionary.

    Returns
    -------
    list[dict]
        List of draft object dictionaries.
    """
    return project.get("draft_objects", [])


def get_draft_object(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Return the draft object at *index* without removing it.

    Parameters
    ----------
    project : dict
        The project state dictionary.
    index : int
        Index of the draft object.

    Returns
    -------
    dict
        The draft object dictionary.
    """
    return _get_draft(project, index)


def remove_draft_object(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Remove and return the draft object at *index*.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    index : int
        Index of the draft object to remove.

    Returns
    -------
    dict
        The removed draft object.
    """
    objs = project.get("draft_objects", [])
    if not isinstance(index, int) or index < 0 or index >= len(objs):
        raise IndexError(
            f"Draft object index {index} out of range (0..{len(objs) - 1})"
        )
    return objs.pop(index)
