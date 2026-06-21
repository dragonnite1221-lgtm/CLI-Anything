# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403

# fmt: off
from .export_p1 import _col_to_num, _content_item_to_html, _num_to_col, _split_ref  # noqa: E402,E501
# fmt: on


def _sheet_to_html(sheet: Dict[str, Any]) -> str:
    """Convert a spreadsheet sheet to HTML table."""
    cells = sheet.get("cells", {})
    if not cells:
        return "<p>(empty sheet)</p>"

    # Determine grid bounds
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

    rows = []
    for r in range(1, max_row + 1):
        row_cells = []
        for c in range(1, max_col + 1):
            ref = _num_to_col(c) + str(r)
            if ref in cells:
                val = html_module.escape(str(cells[ref].get("value", "")))
            else:
                val = ""
            row_cells.append(f"<td>{val}</td>")
        rows.append(f"<tr>{''.join(row_cells)}</tr>")

    return f"<table border='1'>{''.join(rows)}</table>"


def _build_html(project: Dict[str, Any], doc_type: str) -> str:
    """Build HTML content from a project."""
    title = project.get("metadata", {}).get("title", project.get("name", "Document"))
    parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        f'<meta charset="utf-8">',
        f"<title>{html_module.escape(title)}</title>",
        "<style>body { font-family: serif; max-width: 800px; margin: 2em auto; padding: 0 1em; }</style>",
        "</head>",
        "<body>",
    ]

    if doc_type == "writer":
        for item in project.get("content", []):
            parts.append(_content_item_to_html(item))
    elif doc_type == "calc":
        for sheet in project.get("sheets", []):
            parts.append(f"<h2>{html_module.escape(sheet.get('name', 'Sheet'))}</h2>")
            parts.append(_sheet_to_html(sheet))
    elif doc_type == "impress":
        for i, slide in enumerate(project.get("slides", [])):
            parts.append(f"<section>")
            if slide.get("title"):
                parts.append(f"<h1>{html_module.escape(slide['title'])}</h1>")
            if slide.get("content"):
                parts.append(f"<p>{html_module.escape(slide['content'])}</p>")
            parts.append("</section>")
            if i < len(project.get("slides", [])) - 1:
                parts.append("<hr>")

    parts.extend(["</body>", "</html>"])
    return "\n".join(parts)


def to_html(
    project: Dict[str, Any], path: str, overwrite: bool = False
) -> Dict[str, Any]:
    """Export to HTML format."""
    if os.path.exists(path) and not overwrite:
        raise FileExistsError(f"Output file exists: {path}. Use --overwrite.")

    doc_type = project.get("type", "writer")
    html_content = _build_html(project, doc_type)

    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return {
        "output": os.path.abspath(path),
        "format": "html",
        "file_size": os.path.getsize(path),
    }
