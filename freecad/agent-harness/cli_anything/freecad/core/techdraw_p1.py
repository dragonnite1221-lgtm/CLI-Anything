# ruff: noqa: F403, F405, E501
from .techdraw_base import *  # noqa: F403


def _next_id(project: Dict[str, Any]) -> int:
    """Return the next available integer ID for TechDraw pages."""
    items = project.get(_COLLECTION_KEY, [])
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


def _unique_name(project: Dict[str, Any], base: str) -> str:
    """Return a unique name derived from *base* inside the pages list."""
    existing = {item["name"] for item in project.get(_COLLECTION_KEY, [])}
    if base not in existing:
        return base
    counter = 2
    while f"{base}_{counter}" in existing:
        counter += 1
    return f"{base}_{counter}"


def _validate_vec2(value: Any, label: str) -> List[float]:
    """Validate that *value* is a list of exactly two numbers."""
    if not isinstance(value, (list, tuple)):
        raise ValueError(
            f"{label} must be a list of 2 numbers, got {type(value).__name__}"
        )
    if len(value) != 2:
        raise ValueError(f"{label} must have exactly 2 elements, got {len(value)}")
    try:
        return [float(v) for v in value]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} elements must be numeric: {exc}") from exc


def _validate_vec3(value: Any, label: str) -> List[float]:
    """Validate that *value* is a list of exactly three numbers."""
    if not isinstance(value, (list, tuple)):
        raise ValueError(
            f"{label} must be a list of 3 numbers, got {type(value).__name__}"
        )
    if len(value) != 3:
        raise ValueError(f"{label} must have exactly 3 elements, got {len(value)}")
    try:
        return [float(v) for v in value]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} elements must be numeric: {exc}") from exc


def _get_page(project: Dict[str, Any], page_index: int) -> Dict[str, Any]:
    """Internal accessor with bounds checking."""
    items = ensure_collection(project, _COLLECTION_KEY)
    if not isinstance(page_index, int) or page_index < 0 or page_index >= len(items):
        raise IndexError(f"Page index {page_index} out of range (0..{len(items) - 1})")
    return items[page_index]


def _get_view(
    project: Dict[str, Any], page_index: int, view_index: int
) -> Dict[str, Any]:
    """Internal accessor for a view within a page."""
    page = _get_page(project, page_index)
    views = page["views"]
    if not isinstance(view_index, int) or view_index < 0 or view_index >= len(views):
        raise IndexError(f"View index {view_index} out of range (0..{len(views) - 1})")
    return views[view_index]


def new_page(
    project: Dict[str, Any],
    name: Optional[str] = None,
    template: str = "A4_LandscapeTD",
) -> Dict[str, Any]:
    """Create a new TechDraw page and append it to the project.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    name : str or None
        Human-readable label. Auto-generated when *None*.
    template : str
        Drawing template name (e.g. ``"A4_LandscapeTD"``, ``"A3_LandscapeTD"``).

    Returns
    -------
    dict
        The newly created page dictionary.
    """
    items = ensure_collection(project, _COLLECTION_KEY)

    if name is None:
        name = _unique_name(project, "Page")

    page: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "template": template,
        "views": [],
        "dimensions": [],
        "annotations": [],
    }

    items.append(page)
    return page


def set_template(
    project: Dict[str, Any],
    page_index: int,
    template: str,
) -> Dict[str, Any]:
    """Change the template of an existing page.

    Returns the updated page dictionary.
    """
    if not isinstance(template, str) or not template.strip():
        raise ValueError("Template must be a non-empty string")

    page = _get_page(project, page_index)
    page["template"] = template.strip()
    return page
