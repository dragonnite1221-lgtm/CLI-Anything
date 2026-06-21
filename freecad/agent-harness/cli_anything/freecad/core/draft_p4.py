# ruff: noqa: F403, F405, E501
from .draft_base import *  # noqa: F403

# fmt: off
from .draft_p1 import _make_draft, _validate_vec3  # noqa: E402,E501
# fmt: on


def draft_point(
    project: Dict[str, Any],
    point: Optional[List[float]] = None,
    name: Optional[str] = None,
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Create a single draft point.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    point : list[float] or None
        ``[x, y, z]`` coordinate.  Defaults to ``[0, 0, 0]``.

    Returns
    -------
    dict
        The newly created draft object.
    """
    pt = _validate_vec3(point, "point") if point is not None else [0.0, 0.0, 0.0]
    return _make_draft(
        project,
        "point",
        name,
        {
            "point": pt,
        },
        position,
        rotation,
    )


def draft_text(
    project: Dict[str, Any],
    text: str,
    name: Optional[str] = None,
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Create a draft text annotation.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    text : str
        The text content to display.

    Returns
    -------
    dict
        The newly created draft object.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("text must be a non-empty string")
    return _make_draft(
        project,
        "text",
        name,
        {
            "text": text.strip(),
        },
        position,
        rotation,
    )


def draft_shapestring(
    project: Dict[str, Any],
    text: str,
    font_file: str,
    size: float = 10.0,
    font_path_relative: bool = False,
    name: Optional[str] = None,
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Create a ShapeString (text extruded into wire outlines).

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    text : str
        The text content.
    font_file : str
        Path to the TrueType font file.
    size : float
        Font height (default ``10``).
    font_path_relative : bool
        Whether *font_file* is a relative path (default ``False``).

    Returns
    -------
    dict
        The newly created draft object.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("text must be a non-empty string")
    if not isinstance(font_file, str) or not font_file.strip():
        raise ValueError("font_file must be a non-empty string")
    if size <= 0:
        raise ValueError("size must be a positive number")
    return _make_draft(
        project,
        "shapestring",
        name,
        {
            "text": text.strip(),
            "font_file": font_file.strip(),
            "size": float(size),
            "font_path_relative": bool(font_path_relative),
        },
        position,
        rotation,
    )
