# ruff: noqa: F403, F405, E501
from .odf_utils_base import *  # noqa: F403

# fmt: off
from .odf_utils_p1 import _add_heading_element, _ns, _nsattr  # noqa: E402,E501
from .odf_utils_p2 import _add_list_element, _add_page_break_element, _add_paragraph_element, _add_table_element  # noqa: E402,E501
# fmt: on


def _add_image_ref_element(
    parent: ET.Element, auto_styles: ET.Element, item: Dict, style_counter: list
) -> None:
    """Add an image reference (frame) element."""
    para = ET.SubElement(parent, _ns("text", "p"))
    frame = ET.SubElement(para, _ns("draw", "frame"))
    frame.set(_nsattr("draw", "name"), item.get("name", "Image"))
    frame.set(_nsattr("svg", "width"), item.get("width", "10cm"))
    frame.set(_nsattr("svg", "height"), item.get("height", "10cm"))
    image = ET.SubElement(frame, _ns("draw", "image"))
    image.set(_nsattr("xlink", "href"), item.get("path", ""))
    image.set(_nsattr("xlink", "type"), "simple")
    image.set(_nsattr("xlink", "show"), "embed")
    image.set(_nsattr("xlink", "actuate"), "onLoad")


def _build_writer_content(
    root: ET.Element, auto_styles: ET.Element, project: Dict[str, Any]
) -> None:
    """Build Writer content.xml body."""
    body = ET.SubElement(root, _ns("office", "body"))
    text_elem = ET.SubElement(body, _ns("office", "text"))

    content_items = project.get("content", [])
    style_counter = [0]

    for item in content_items:
        item_type = item.get("type", "paragraph")

        if item_type == "heading":
            _add_heading_element(text_elem, auto_styles, item, style_counter)
        elif item_type == "paragraph":
            _add_paragraph_element(text_elem, auto_styles, item, style_counter)
        elif item_type == "list":
            _add_list_element(text_elem, auto_styles, item, style_counter)
        elif item_type == "table":
            _add_table_element(text_elem, auto_styles, item, style_counter)
        elif item_type == "page_break":
            _add_page_break_element(text_elem, auto_styles, style_counter)
        elif item_type == "image_ref":
            _add_image_ref_element(text_elem, auto_styles, item, style_counter)


def _col_letter(col_num: int) -> str:
    """Convert column number to letter(s): 1=A, 2=B, ..., 26=Z, 27=AA."""
    result = ""
    while col_num > 0:
        col_num, remainder = divmod(col_num - 1, 26)
        result = chr(65 + remainder) + result
    return result


def _split_cell_ref(ref: str) -> tuple:
    """Split a cell reference like 'A1' into ('A', '1')."""
    col = ""
    row = ""
    for ch in ref:
        if ch.isalpha():
            col += ch
        else:
            row += ch
    return col.upper(), row


def _col_number(col_str: str) -> int:
    """Convert column letter(s) to number: A=1, B=2, ..., Z=26, AA=27."""
    result = 0
    for ch in col_str:
        result = result * 26 + (ord(ch.upper()) - ord("A") + 1)
    return result


def _get_grid_bounds(cells: Dict[str, Any]) -> tuple:
    """Get the maximum row and column from a cells dictionary."""
    max_row = 0
    max_col = 0
    for ref in cells:
        col_str, row_str = _split_cell_ref(ref)
        row_num = int(row_str)
        col_num = _col_number(col_str)
        if row_num > max_row:
            max_row = row_num
        if col_num > max_col:
            max_col = col_num
    return max_row, max_col
