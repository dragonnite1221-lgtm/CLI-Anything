# ruff: noqa: F403, F405, E501
from .techdraw_base import *  # noqa: F403

# fmt: off
from .techdraw_p1 import _get_page, _get_view  # noqa: E402,E501
# fmt: on


def export_page_pdf(
    project: Dict[str, Any],
    page_index: int,
    path: str,
) -> Dict[str, Any]:
    """Record metadata for exporting a page to PDF.

    The actual export is performed by the generated FreeCAD macro.

    Returns
    -------
    dict
        Export metadata including page name and output path.
    """
    if not isinstance(path, str) or not path.strip():
        raise ValueError("Path must be a non-empty string")

    page = _get_page(project, page_index)

    return {
        "action": "export_pdf",
        "page_name": page["name"],
        "page_index": page_index,
        "path": path.strip(),
        "format": "pdf",
    }


def export_page_svg(
    project: Dict[str, Any],
    page_index: int,
    path: str,
) -> Dict[str, Any]:
    """Record metadata for exporting a page to SVG.

    The actual export is performed by the generated FreeCAD macro.

    Returns
    -------
    dict
        Export metadata including page name and output path.
    """
    if not isinstance(path, str) or not path.strip():
        raise ValueError("Path must be a non-empty string")

    page = _get_page(project, page_index)

    return {
        "action": "export_svg",
        "page_name": page["name"],
        "page_index": page_index,
        "path": path.strip(),
        "format": "svg",
    }


def list_views(
    project: Dict[str, Any],
    page_index: int,
) -> List[Dict[str, Any]]:
    """Return all views on a page."""
    page = _get_page(project, page_index)
    return page["views"]


def get_view(
    project: Dict[str, Any],
    page_index: int,
    view_index: int,
) -> Dict[str, Any]:
    """Return a specific view from a page.

    Raises ``IndexError`` when either index is out of range.
    """
    return _get_view(project, page_index, view_index)
