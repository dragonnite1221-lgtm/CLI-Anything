# ruff: noqa: F403, F405, E501
from .writer_base import *  # noqa: F403


def _ensure_writer(project: Dict[str, Any]) -> None:
    """Ensure the project is a Writer document."""
    if project.get("type") != "writer":
        raise ValueError(
            f"Document type is '{project.get('type')}', expected 'writer'."
        )
    if "content" not in project:
        project["content"] = []


def add_paragraph(
    project: Dict[str, Any],
    text: str = "",
    style: Optional[Dict] = None,
    position: Optional[int] = None,
) -> Dict[str, Any]:
    """Add a paragraph to the document."""
    _ensure_writer(project)
    item = {
        "type": "paragraph",
        "text": text,
        "style": style or {},
    }
    if position is not None:
        if position < 0 or position > len(project["content"]):
            raise IndexError(
                f"Position {position} out of range (0-{len(project['content'])})"
            )
        project["content"].insert(position, item)
    else:
        project["content"].append(item)
    return item


def add_heading(
    project: Dict[str, Any],
    text: str = "",
    level: int = 1,
    style: Optional[Dict] = None,
    position: Optional[int] = None,
) -> Dict[str, Any]:
    """Add a heading to the document."""
    _ensure_writer(project)
    if level < 1 or level > 6:
        raise ValueError(f"Heading level must be 1-6, got {level}")
    item = {
        "type": "heading",
        "level": level,
        "text": text,
        "style": style or {},
    }
    if position is not None:
        if position < 0 or position > len(project["content"]):
            raise IndexError(
                f"Position {position} out of range (0-{len(project['content'])})"
            )
        project["content"].insert(position, item)
    else:
        project["content"].append(item)
    return item


def add_list(
    project: Dict[str, Any],
    items: Optional[List[str]] = None,
    list_style: str = "bullet",
    position: Optional[int] = None,
) -> Dict[str, Any]:
    """Add a list to the document."""
    _ensure_writer(project)
    if list_style not in ("bullet", "number"):
        raise ValueError(f"Invalid list style: {list_style}. Use 'bullet' or 'number'.")
    item = {
        "type": "list",
        "list_style": list_style,
        "items": items or [],
    }
    if position is not None:
        if position < 0 or position > len(project["content"]):
            raise IndexError(
                f"Position {position} out of range (0-{len(project['content'])})"
            )
        project["content"].insert(position, item)
    else:
        project["content"].append(item)
    return item
