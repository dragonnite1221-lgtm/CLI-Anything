# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403

# fmt: off
from .export_p1 import _col_to_num, _num_to_col, _split_ref  # noqa: E402,E501
# fmt: on


def _content_item_to_text(item: Dict[str, Any]) -> str:
    """Convert a content item to plain text."""
    item_type = item.get("type", "paragraph")

    if item_type == "heading":
        text = item.get("text", "")
        level = item.get("level", 1)
        prefix = "#" * level + " "
        return prefix + text
    elif item_type == "paragraph":
        return item.get("text", "")
    elif item_type == "list":
        items = item.get("items", [])
        is_numbered = item.get("list_style") == "number"
        lines = []
        for i, li in enumerate(items):
            if is_numbered:
                lines.append(f"  {i + 1}. {li}")
            else:
                lines.append(f"  - {li}")
        return "\n".join(lines)
    elif item_type == "table":
        rows = item.get("data", [])
        lines = []
        for row in rows:
            lines.append("\t".join(str(c) for c in row))
        return "\n".join(lines)
    elif item_type == "page_break":
        return "\n--- Page Break ---\n"
    return ""


def _sheet_to_text(sheet: Dict[str, Any]) -> str:
    """Convert a sheet to plain text."""
    cells = sheet.get("cells", {})
    if not cells:
        return "(empty)"

    max_row = 0
    max_col = 0
    for ref in cells:
        col, row = _split_ref(ref)
        col_num = _col_to_num(col)
        row_num = int(row)
        if row_num > max_row:
            max_row = row_num
        if col_num > max_col:
            max_col = col_num

    lines = []
    for r in range(1, max_row + 1):
        row_vals = []
        for c in range(1, max_col + 1):
            ref = _num_to_col(c) + str(r)
            if ref in cells:
                row_vals.append(str(cells[ref].get("value", "")))
            else:
                row_vals.append("")
        lines.append("\t".join(row_vals))

    return "\n".join(lines)


def _build_text(project: Dict[str, Any], doc_type: str) -> str:
    """Build plain text content from a project."""
    lines = []

    if doc_type == "writer":
        for item in project.get("content", []):
            lines.append(_content_item_to_text(item))
    elif doc_type == "calc":
        for sheet in project.get("sheets", []):
            lines.append(f"=== {sheet.get('name', 'Sheet')} ===")
            lines.append(_sheet_to_text(sheet))
            lines.append("")
    elif doc_type == "impress":
        for i, slide in enumerate(project.get("slides", [])):
            lines.append(f"--- Slide {i + 1} ---")
            if slide.get("title"):
                lines.append(slide["title"])
            if slide.get("content"):
                lines.append(slide["content"])
            lines.append("")

    return "\n".join(lines)


def to_text(
    project: Dict[str, Any], path: str, overwrite: bool = False
) -> Dict[str, Any]:
    """Export to plain text format."""
    if os.path.exists(path) and not overwrite:
        raise FileExistsError(f"Output file exists: {path}. Use --overwrite.")

    doc_type = project.get("type", "writer")
    text_content = _build_text(project, doc_type)

    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text_content)

    return {
        "output": os.path.abspath(path),
        "format": "text",
        "file_size": os.path.getsize(path),
    }
