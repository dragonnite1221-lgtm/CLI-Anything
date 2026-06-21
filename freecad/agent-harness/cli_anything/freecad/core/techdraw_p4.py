# ruff: noqa: F403, F405, E501
from .techdraw_base import *  # noqa: F403

# fmt: off
from .techdraw_p1 import _get_page, _get_view, _validate_vec2  # noqa: E402,E501
# fmt: on


def add_dimension(
    project: Dict[str, Any],
    page_index: int,
    view_index: int,
    dim_type: str,
    references: List[Any],
    value: Optional[float] = None,
) -> Dict[str, Any]:
    """Add a dimension annotation to a page.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    page_index : int
        Index of the target page.
    view_index : int
        Index of the view the dimension references.
    dim_type : str
        One of ``"length"``, ``"distance"``, ``"radius"``,
        ``"diameter"``, ``"angle"``.
    references : list
        Geometry references (edges, vertices) for the dimension.
    value : float or None
        Explicit override value. When *None* the value is derived from
        the referenced geometry during macro execution.

    Returns
    -------
    dict
        The dimension entry.

    Raises
    ------
    ValueError
        If *dim_type* is unknown.
    """
    if dim_type not in VALID_DIM_TYPES:
        valid = ", ".join(sorted(VALID_DIM_TYPES))
        raise ValueError(f"Unknown dim_type '{dim_type}'. Valid: {valid}")

    page = _get_page(project, page_index)
    _get_view(project, page_index, view_index)

    dimension: Dict[str, Any] = {
        "type": dim_type,
        "view_index": view_index,
        "references": list(references),
        "value": float(value) if value is not None else None,
    }

    page["dimensions"].append(dimension)
    return dimension


def add_annotation(
    project: Dict[str, Any],
    page_index: int,
    text: str,
    position: Optional[List[float]] = None,
    area_mode: bool = False,
    shape_validation: bool = True,
) -> Dict[str, Any]:
    """Add a text annotation to a page.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    page_index : int
        Index of the target page.
    text : str
        Annotation text content.
    position : list[float] or None
        Position on the page ``[x, y]``. Defaults to ``[0, 0]``.
    area_mode : bool
        When ``True``, computes area accounting for face holes (default ``False``).
    shape_validation : bool
        Enables shape validation (default ``True``).

    Returns the annotation entry.
    """
    page = _get_page(project, page_index)

    if position is not None:
        position = _validate_vec2(position, "position")
    else:
        position = [0.0, 0.0]

    annotation: Dict[str, Any] = {
        "type": "annotation",
        "text": str(text),
        "position": position,
        "area_mode": bool(area_mode),
        "shape_validation": bool(shape_validation),
    }

    page["annotations"].append(annotation)
    return annotation
