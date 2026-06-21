# ruff: noqa: F403, F405, E501
from .draft_base import *  # noqa: F403

# fmt: off
from .draft_p1 import _get_draft, _make_draft, _validate_vec3  # noqa: E402,E501
# fmt: on


def draft_dimension(
    project: Dict[str, Any],
    start: List[float],
    end: List[float],
    dim_line: Optional[List[float]] = None,
    name: Optional[str] = None,
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Create a linear dimension annotation.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    start : list[float]
        ``[x, y, z]`` start point.
    end : list[float]
        ``[x, y, z]`` end point.
    dim_line : list[float] or None
        Point through which the dimension line passes.

    Returns
    -------
    dict
        The newly created draft object.
    """
    s = _validate_vec3(start, "start")
    e = _validate_vec3(end, "end")
    dl = (
        _validate_vec3(dim_line, "dim_line")
        if dim_line is not None
        else [0.0, 0.0, 0.0]
    )
    return _make_draft(
        project,
        "dimension",
        name,
        {
            "start": s,
            "end": e,
            "dim_line": dl,
        },
        position,
        rotation,
    )


def draft_label(
    project: Dict[str, Any],
    target_point: List[float],
    text: str = "",
    name: Optional[str] = None,
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Create a label annotation pointing to *target_point*.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    target_point : list[float]
        ``[x, y, z]`` point the label arrow targets.
    text : str
        Label text content.

    Returns
    -------
    dict
        The newly created draft object.
    """
    tp = _validate_vec3(target_point, "target_point")
    return _make_draft(
        project,
        "label",
        name,
        {
            "target_point": tp,
            "text": text,
        },
        position,
        rotation,
    )


def draft_hatch(
    project: Dict[str, Any],
    target_index: int,
    pattern: str = "ANSI31",
    scale: float = 1.0,
    name: Optional[str] = None,
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Apply a hatch pattern to a draft object face.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    target_index : int
        Index of the draft object to hatch.
    pattern : str
        Hatch pattern name (default ``"ANSI31"``).
    scale : float
        Pattern scale factor (default ``1``).

    Returns
    -------
    dict
        The newly created draft object.
    """
    _get_draft(project, target_index)  # validate
    if scale <= 0:
        raise ValueError("scale must be a positive number")
    return _make_draft(
        project,
        "hatch",
        name,
        {
            "target_index": target_index,
            "pattern": pattern,
            "scale": float(scale),
        },
        position,
        rotation,
    )
