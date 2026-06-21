# ruff: noqa: F403, F405, E501
from .draft_base import *  # noqa: F403

# fmt: off
from .draft_p1 import _get_draft, _make_draft, _unique_name, _validate_vec3  # noqa: E402,E501
# fmt: on


def draft_clone(
    project: Dict[str, Any],
    index: int,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a clone (linked copy) of a draft object.

    Unlike :func:`draft_copy`, a clone maintains a parametric reference
    to the source object.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    index : int
        Index of the source draft object.
    name : str or None
        Label for the clone.

    Returns
    -------
    dict
        The newly created clone draft object.
    """
    obj = _get_draft(project, index)
    if name is None:
        name = _unique_name(project, f"{obj['name']}_Clone")
    return _make_draft(
        project,
        "clone",
        name,
        {
            "source_id": obj["id"],
        },
    )


def draft_upgrade(
    project: Dict[str, Any],
    index: int,
) -> Dict[str, Any]:
    """Upgrade a draft object (e.g. wires -> face).

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    index : int
        Index of the draft object to upgrade.

    Returns
    -------
    dict
        The updated draft object.
    """
    obj = _get_draft(project, index)
    obj["properties"]["_upgraded"] = True
    return obj


def draft_downgrade(
    project: Dict[str, Any],
    index: int,
) -> Dict[str, Any]:
    """Downgrade a draft object (e.g. face -> wires).

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    index : int
        Index of the draft object to downgrade.

    Returns
    -------
    dict
        The updated draft object.
    """
    obj = _get_draft(project, index)
    obj["properties"]["_downgraded"] = True
    return obj


def draft_trim(
    project: Dict[str, Any],
    index: int,
    point: List[float],
) -> Dict[str, Any]:
    """Trim a draft object at the given point.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    index : int
        Index of the draft object to trim.
    point : list[float]
        ``[x, y, z]`` trim location.

    Returns
    -------
    dict
        The updated draft object.
    """
    obj = _get_draft(project, index)
    pt = _validate_vec3(point, "point")
    obj["properties"]["_trim_point"] = pt
    return obj
