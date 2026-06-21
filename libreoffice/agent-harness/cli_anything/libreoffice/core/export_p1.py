# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403


def list_presets() -> List[Dict[str, Any]]:
    """List available export presets."""
    result = []
    for name, p in EXPORT_PRESETS.items():
        result.append(
            {
                "name": name,
                "format": p["format"],
                "extension": p["ext"],
                "description": p["description"],
            }
        )
    return result


def get_preset_info(name: str) -> Dict[str, Any]:
    """Get details about an export preset."""
    if name not in EXPORT_PRESETS:
        raise ValueError(
            f"Unknown preset: {name}. Available: {', '.join(EXPORT_PRESETS.keys())}"
        )
    p = EXPORT_PRESETS[name]
    return {"name": name, **p}


def _export_odf(
    project: Dict[str, Any],
    path: str,
    doc_type: str,
    overwrite: bool = False,
) -> Dict[str, Any]:
    """Export to an ODF file."""
    if os.path.exists(path) and not overwrite:
        raise FileExistsError(f"Output file exists: {path}. Use --overwrite.")

    abs_path = write_odf(path, doc_type, project)

    return {
        "output": abs_path,
        "format": doc_type,
        "extension": ODF_EXTENSIONS.get(doc_type, ".odf"),
        "file_size": os.path.getsize(abs_path),
    }


def to_odt(
    project: Dict[str, Any], path: str, overwrite: bool = False
) -> Dict[str, Any]:
    """Export to ODF Writer (.odt) format."""
    return _export_odf(project, path, "writer", overwrite)


def to_ods(
    project: Dict[str, Any], path: str, overwrite: bool = False
) -> Dict[str, Any]:
    """Export to ODF Calc (.ods) format."""
    return _export_odf(project, path, "calc", overwrite)


def to_odp(
    project: Dict[str, Any], path: str, overwrite: bool = False
) -> Dict[str, Any]:
    """Export to ODF Impress (.odp) format."""
    return _export_odf(project, path, "impress", overwrite)


def _content_item_to_html(item: Dict[str, Any]) -> str:
    """Convert a single content item to HTML."""
    item_type = item.get("type", "paragraph")

    if item_type == "heading":
        level = item.get("level", 1)
        text = html_module.escape(item.get("text", ""))
        return f"<h{level}>{text}</h{level}>"
    elif item_type == "paragraph":
        text = html_module.escape(item.get("text", ""))
        return f"<p>{text}</p>"
    elif item_type == "list":
        tag = "ul" if item.get("list_style") == "bullet" else "ol"
        items = "".join(
            f"<li>{html_module.escape(str(i))}</li>" for i in item.get("items", [])
        )
        return f"<{tag}>{items}</{tag}>"
    elif item_type == "table":
        rows = item.get("data", [])
        html_rows = ""
        for row in rows:
            cells = "".join(f"<td>{html_module.escape(str(c))}</td>" for c in row)
            html_rows += f"<tr>{cells}</tr>"
        return f"<table border='1'>{html_rows}</table>"
    elif item_type == "page_break":
        return "<hr style='page-break-before: always;'>"
    return ""


def _split_ref(ref: str):
    """Split cell ref like A1 -> ('A', '1')."""
    col = ""
    row = ""
    for ch in ref:
        if ch.isalpha():
            col += ch
        else:
            row += ch
    return col.upper(), row


def _col_to_num(col: str) -> int:
    """A=1, B=2, ..., Z=26, AA=27."""
    result = 0
    for ch in col.upper():
        result = result * 26 + (ord(ch) - ord("A") + 1)
    return result


def _num_to_col(num: int) -> str:
    """1=A, 2=B, ..., 26=Z, 27=AA."""
    result = ""
    while num > 0:
        num, r = divmod(num - 1, 26)
        result = chr(65 + r) + result
    return result
