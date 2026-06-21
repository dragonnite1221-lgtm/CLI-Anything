# ruff: noqa: F403, F405, E501
from .importer_base import *  # noqa: F403
# fmt: off
from .importer_p1 import _attr, _children_by_local, _int_attr, _local_name, _q, _text_content  # noqa: E402,E501
from .importer_p2 import _normalize_formula, _num_to_col, _split_ref  # noqa: E402,E501
# fmt: on


def _cell_data(cell_elem: ET.Element) -> Optional[Dict[str, Any]]:
    value_type = _attr(cell_elem, "office", "value-type") or "string"
    formula = _normalize_formula(_attr(cell_elem, "table", "formula"))
    text = _text_content(cell_elem)
    numeric_value = _attr(cell_elem, "office", "value")

    if not formula and not numeric_value and not text:
        return None

    if value_type in ("float", "currency", "percentage") and numeric_value is not None:
        try:
            value: Any = float(numeric_value)
            cell_type = "float"
        except ValueError:
            value = numeric_value
            cell_type = "string"
    elif value_type == "boolean":
        value = (_attr(cell_elem, "office", "boolean-value") or text).lower() == "true"
        cell_type = "boolean"
    else:
        value = text if text != "" else (numeric_value or "")
        cell_type = "string"

    data = {"value": value, "type": cell_type}
    if formula:
        data["formula"] = formula
    return data
def _parse_calc_row(row_elem: ET.Element, row_index: int) -> Dict[str, Dict[str, Any]]:
    row_cells: Dict[str, Dict[str, Any]] = {}
    col_index = 1

    for cell_elem in list(row_elem):
        if _local_name(cell_elem.tag) not in ("table-cell", "covered-table-cell"):
            continue

        col_repeat = max(1, _int_attr(cell_elem, "table", "number-columns-repeated", 1))
        cell_data = _cell_data(cell_elem)
        if cell_data is not None:
            for repeat_offset in range(min(col_repeat, 1000)):
                ref = f"{_num_to_col(col_index + repeat_offset)}{row_index}"
                row_cells[ref] = dict(cell_data)
        col_index += col_repeat

    return row_cells
def _parse_calc_cells(table_elem: ET.Element) -> Dict[str, Dict[str, Any]]:
    cells: Dict[str, Dict[str, Any]] = {}
    row_index = 1

    for row_elem in _children_by_local(table_elem, "table-row"):
        row_repeat = max(1, _int_attr(row_elem, "table", "number-rows-repeated", 1))
        row_cells = _parse_calc_row(row_elem, row_index)
        if row_cells:
            for repeat_offset in range(min(row_repeat, 1000)):
                for ref, cell in row_cells.items():
                    col, row = _split_ref(ref)
                    repeated_ref = f"{col}{int(row) + repeat_offset}"
                    cells[repeated_ref] = dict(cell)
        row_index += row_repeat

    return cells
def _parse_calc_content(root: ET.Element) -> List[Dict[str, Any]]:
    body = root.find(_q("office", "body"))
    spreadsheet = body.find(_q("office", "spreadsheet")) if body is not None else None
    if spreadsheet is None:
        return []

    sheets = []
    for i, table_elem in enumerate(_children_by_local(spreadsheet, "table")):
        name = _attr(table_elem, "table", "name") or f"Sheet{i + 1}"
        cells = _parse_calc_cells(table_elem)
        sheets.append({"name": name, "cells": cells})
    return sheets
def _parse_impress_content(root: ET.Element) -> List[Dict[str, Any]]:
    body = root.find(_q("office", "body"))
    presentation = body.find(_q("office", "presentation")) if body is not None else None
    if presentation is None:
        return []

    slides = []
    for page in _children_by_local(presentation, "page"):
        texts = [_text_content(elem) for elem in page.iter() if _local_name(elem.tag) in ("h", "p")]
        texts = [text for text in texts if text]
        title = texts[0] if texts else (_attr(page, "draw", "name") or "")
        content = "\n".join(texts[1:]) if len(texts) > 1 else ""
        slides.append({
            "title": title,
            "content": content,
            "elements": [],
        })
    return slides
