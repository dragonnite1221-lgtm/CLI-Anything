# ruff: noqa: F403, F405, E501
from .odf_utils_base import *  # noqa: F403

# fmt: off
from .odf_utils_p1 import _create_char_auto_style, _create_text_auto_style, _ns, _nsattr  # noqa: E402,E501
# fmt: on


def _add_paragraph_element(
    parent: ET.Element, auto_styles: ET.Element, item: Dict, style_counter: list
) -> None:
    """Add a paragraph element to the content."""
    para = ET.SubElement(parent, _ns("text", "p"))
    style = item.get("style", {})

    if style:
        style_name = f"P_auto{style_counter[0]}"
        style_counter[0] += 1
        para.set(_nsattr("text", "style-name"), style_name)
        _create_text_auto_style(auto_styles, style_name, style)

    text = item.get("text", "")

    # Handle styled spans within text
    spans = item.get("spans", [])
    if spans:
        last_end = 0
        for span_info in spans:
            start = span_info.get("start", 0)
            end = span_info.get("end", len(text))
            span_style = span_info.get("style", {})

            # Text before span
            if start > last_end:
                if para.text is None:
                    para.text = text[last_end:start]
                else:
                    # Add as tail of last sub-element
                    children = list(para)
                    if children:
                        if children[-1].tail is None:
                            children[-1].tail = text[last_end:start]
                        else:
                            children[-1].tail += text[last_end:start]
                    else:
                        para.text = (para.text or "") + text[last_end:start]

            # Span element
            span_style_name = f"S_auto{style_counter[0]}"
            style_counter[0] += 1
            span = ET.SubElement(para, _ns("text", "span"))
            span.set(_nsattr("text", "style-name"), span_style_name)
            span.text = text[start:end]
            _create_char_auto_style(auto_styles, span_style_name, span_style)

            last_end = end

        # Text after last span
        if last_end < len(text):
            children = list(para)
            if children:
                if children[-1].tail is None:
                    children[-1].tail = text[last_end:]
                else:
                    children[-1].tail += text[last_end:]
            else:
                para.text = (para.text or "") + text[last_end:]
    else:
        para.text = text


def _add_list_element(
    parent: ET.Element, auto_styles: ET.Element, item: Dict, style_counter: list
) -> None:
    """Add a list element to the content."""
    list_style = item.get("style", "bullet")
    list_elem = ET.SubElement(parent, _ns("text", "list"))

    for list_item in item.get("items", []):
        li = ET.SubElement(list_elem, _ns("text", "list-item"))
        para = ET.SubElement(li, _ns("text", "p"))
        para.text = str(list_item)


def _add_table_element(
    parent: ET.Element, auto_styles: ET.Element, item: Dict, style_counter: list
) -> None:
    """Add a table element to the content."""
    table_name = f"Table{style_counter[0]}"
    style_counter[0] += 1

    table = ET.SubElement(parent, _ns("table", "table"))
    table.set(_nsattr("table", "name"), table_name)

    cols = item.get("cols", 0)
    rows_data = item.get("data", [])

    # Columns
    for c in range(cols):
        col = ET.SubElement(table, _ns("table", "table-column"))

    # Rows
    for row_data in rows_data:
        row = ET.SubElement(table, _ns("table", "table-row"))
        for cell_value in row_data:
            cell = ET.SubElement(row, _ns("table", "table-cell"))
            para = ET.SubElement(cell, _ns("text", "p"))
            para.text = str(cell_value)


def _add_page_break_element(
    parent: ET.Element, auto_styles: ET.Element, style_counter: list
) -> None:
    """Add a page break element."""
    style_name = f"PB_auto{style_counter[0]}"
    style_counter[0] += 1

    # Create a style with page-break-before
    style_el = ET.SubElement(auto_styles, _ns("style", "style"))
    style_el.set(_nsattr("style", "name"), style_name)
    style_el.set(_nsattr("style", "family"), "paragraph")
    pp = ET.SubElement(style_el, _ns("style", "paragraph-properties"))
    pp.set(_nsattr("fo", "break-before"), "page")

    para = ET.SubElement(parent, _ns("text", "p"))
    para.set(_nsattr("text", "style-name"), style_name)
