# ruff: noqa: F403, F405, E501
from .techdraw_base import *  # noqa: F403

# fmt: off
from .techdraw_p1 import _get_page, _get_view, _validate_vec2, _validate_vec3  # noqa: E402,E501
# fmt: on


def add_section_view(
    project: Dict[str, Any],
    page_index: int,
    view_index: int,
    section_normal: Optional[List[float]] = None,
    section_origin: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Add a section view derived from an existing view.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    page_index : int
        Index of the target page.
    view_index : int
        Index of the parent view within the page.
    section_normal : list[float] or None
        Normal vector of the section plane. Defaults to ``[1, 0, 0]``.
    section_origin : list[float] or None
        Origin point of the section plane. Defaults to ``[0, 0, 0]``.

    Returns
    -------
    dict
        The section view entry.
    """
    page = _get_page(project, page_index)
    # Validate parent view exists
    _get_view(project, page_index, view_index)

    if section_normal is not None:
        section_normal = _validate_vec3(section_normal, "section_normal")
    else:
        section_normal = [1.0, 0.0, 0.0]

    if section_origin is not None:
        section_origin = _validate_vec3(section_origin, "section_origin")
    else:
        section_origin = [0.0, 0.0, 0.0]

    section: Dict[str, Any] = {
        "type": "section",
        "parent_view_index": view_index,
        "section_normal": section_normal,
        "section_origin": section_origin,
        "scale": 1.0,
        "position": [0.0, 0.0],
    }

    page["views"].append(section)
    return section


def add_detail_view(
    project: Dict[str, Any],
    page_index: int,
    view_index: int,
    center: Optional[List[float]] = None,
    radius: float = 20.0,
) -> Dict[str, Any]:
    """Add a detail (magnified) view of part of an existing view.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    page_index : int
        Index of the target page.
    view_index : int
        Index of the parent view within the page.
    center : list[float] or None
        Center of the detail circle ``[x, y]``. Defaults to ``[0, 0]``.
    radius : float
        Radius of the detail circle.

    Returns
    -------
    dict
        The detail view entry.
    """
    page = _get_page(project, page_index)
    _get_view(project, page_index, view_index)

    if center is not None:
        center = _validate_vec2(center, "center")
    else:
        center = [0.0, 0.0]

    detail: Dict[str, Any] = {
        "type": "detail",
        "parent_view_index": view_index,
        "center": center,
        "radius": float(radius),
        "scale": 2.0,
        "position": [0.0, 0.0],
    }

    page["views"].append(detail)
    return detail
