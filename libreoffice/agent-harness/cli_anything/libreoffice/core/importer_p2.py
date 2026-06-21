# ruff: noqa: F403, F405, E501
from .importer_base import *  # noqa: F403
# fmt: off
from .importer_p1 import _children_by_local, _int_attr, _local_name, _parse_list_items, _q, _text_content  # noqa: E402,E501
# fmt: on


def _parse_table_row_values(row_elem: ET.Element) -> List[str]:
    values = []
    for cell_elem in list(row_elem):
        if _local_name(cell_elem.tag) not in ("table-cell", "covered-table-cell"):
            continue
        repeat = max(1, _int_attr(cell_elem, "table", "number-columns-repeated", 1))
        text = _text_content(cell_elem)
        for _ in range(min(repeat, 1000)):
            values.append(text)
    return values
def _parse_writer_table(table_elem: ET.Element) -> Optional[Dict[str, Any]]:
    rows = []
    max_cols = 0
    for row_elem in _children_by_local(table_elem, "table-row"):
        row_values = _parse_table_row_values(row_elem)
        if any(value != "" for value in row_values):
            rows.append(row_values)
            max_cols = max(max_cols, len(row_values))

    if not rows:
        return None

    for row in rows:
        row.extend([""] * (max_cols - len(row)))

    return {
        "type": "table",
        "rows": len(rows),
        "cols": max_cols,
        "data": rows,
    }
def _parse_writer_content(root: ET.Element) -> List[Dict[str, Any]]:
    body = root.find(_q("office", "body"))
    text_root = body.find(_q("office", "text")) if body is not None else None
    if text_root is None:
        return []

    content = []
    for child in list(text_root):
        local = _local_name(child.tag)
        if local == "h":
            text = _text_content(child)
            if text:
                level = _int_attr(child, "text", "outline-level", default=1)
                content.append({
                    "type": "heading",
                    "level": max(1, min(level, 6)),
                    "text": text,
                    "style": {},
                })
        elif local == "p":
            text = _text_content(child)
            if text:
                content.append({"type": "paragraph", "text": text, "style": {}})
        elif local == "list":
            items = _parse_list_items(child)
            if items:
                content.append({
                    "type": "list",
                    "list_style": "bullet",
                    "items": items,
                })
        elif local == "table":
            table = _parse_writer_table(child)
            if table is not None:
                content.append(table)

    return content
def _split_ref(ref: str) -> Tuple[str, str]:
    col = ""
    row = ""
    for ch in ref:
        if ch.isalpha():
            col += ch
        else:
            row += ch
    return col, row
def _num_to_col(num: int) -> str:
    result = ""
    while num > 0:
        num, rem = divmod(num - 1, 26)
        result = chr(ord("A") + rem) + result
    return result
def _normalize_formula(formula: Optional[str]) -> Optional[str]:
    """Strip ODF formula namespace prefixes before storing project state."""
    if formula is None:
        return None
    for prefix in ("of:", "oooc:"):
        if formula.startswith(prefix):
            return formula[len(prefix):]
    return formula
