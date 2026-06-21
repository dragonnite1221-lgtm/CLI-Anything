# ruff: noqa: F403, F405, E501
from .odf_utils_base import *  # noqa: F403

# fmt: off
from .odf_utils_p1 import _ns, _nsattr  # noqa: E402,E501
from .odf_utils_p3 import _col_letter, _get_grid_bounds  # noqa: E402,E501
# fmt: on


def _build_calc_content(
    root: ET.Element, auto_styles: ET.Element, project: Dict[str, Any]
) -> None:
    """Build Calc content.xml body."""
    body = ET.SubElement(root, _ns("office", "body"))
    spreadsheet = ET.SubElement(body, _ns("office", "spreadsheet"))

    sheets = project.get("sheets", [])
    for sheet_data in sheets:
        table = ET.SubElement(spreadsheet, _ns("table", "table"))
        table.set(_nsattr("table", "name"), sheet_data.get("name", "Sheet1"))

        cells = sheet_data.get("cells", {})
        if not cells:
            # Empty sheet with at least one row/cell
            row = ET.SubElement(table, _ns("table", "table-row"))
            cell = ET.SubElement(row, _ns("table", "table-cell"))
            continue

        # Determine the grid bounds
        max_row, max_col = _get_grid_bounds(cells)

        for r in range(1, max_row + 1):
            row_elem = ET.SubElement(table, _ns("table", "table-row"))
            for c in range(1, max_col + 1):
                cell_ref = _col_letter(c) + str(r)
                cell_elem = ET.SubElement(row_elem, _ns("table", "table-cell"))

                if cell_ref in cells:
                    cell_data = cells[cell_ref]
                    if "formula" in cell_data:
                        cell_elem.set(
                            _nsattr("table", "formula"), f"of:{cell_data['formula']}"
                        )
                        cell_elem.set(_nsattr("office", "value-type"), "float")
                    elif cell_data.get("type") == "float":
                        cell_elem.set(_nsattr("office", "value-type"), "float")
                        cell_elem.set(
                            _nsattr("office", "value"), str(cell_data.get("value", 0))
                        )
                    else:
                        cell_elem.set(_nsattr("office", "value-type"), "string")

                    para = ET.SubElement(cell_elem, _ns("text", "p"))
                    para.text = str(cell_data.get("value", ""))


def _build_impress_content(
    root: ET.Element, auto_styles: ET.Element, project: Dict[str, Any]
) -> None:
    """Build Impress content.xml body."""
    body = ET.SubElement(root, _ns("office", "body"))
    pres = ET.SubElement(body, _ns("office", "presentation"))

    slides = project.get("slides", [])
    for i, slide_data in enumerate(slides):
        page = ET.SubElement(pres, _ns("draw", "page"))
        page.set(_nsattr("draw", "name"), slide_data.get("title", f"Slide {i + 1}"))
        page.set(_nsattr("draw", "master-page-name"), "Default")

        # Title text box
        if slide_data.get("title"):
            frame = ET.SubElement(page, _ns("draw", "frame"))
            frame.set(_nsattr("svg", "x"), "2cm")
            frame.set(_nsattr("svg", "y"), "1cm")
            frame.set(_nsattr("svg", "width"), "22cm")
            frame.set(_nsattr("svg", "height"), "3cm")
            frame.set(_nsattr("presentation", "class"), "title")
            tb = ET.SubElement(frame, _ns("draw", "text-box"))
            para = ET.SubElement(tb, _ns("text", "p"))
            para.text = slide_data["title"]

        # Content text box
        if slide_data.get("content"):
            frame = ET.SubElement(page, _ns("draw", "frame"))
            frame.set(_nsattr("svg", "x"), "2cm")
            frame.set(_nsattr("svg", "y"), "5cm")
            frame.set(_nsattr("svg", "width"), "22cm")
            frame.set(_nsattr("svg", "height"), "13cm")
            frame.set(_nsattr("presentation", "class"), "subtitle")
            tb = ET.SubElement(frame, _ns("draw", "text-box"))
            para = ET.SubElement(tb, _ns("text", "p"))
            para.text = slide_data["content"]

        # Additional elements
        for elem in slide_data.get("elements", []):
            if elem.get("type") == "text_box":
                frame = ET.SubElement(page, _ns("draw", "frame"))
                frame.set(_nsattr("svg", "x"), elem.get("x", "2cm"))
                frame.set(_nsattr("svg", "y"), elem.get("y", "2cm"))
                frame.set(_nsattr("svg", "width"), elem.get("width", "10cm"))
                frame.set(_nsattr("svg", "height"), elem.get("height", "5cm"))
                tb = ET.SubElement(frame, _ns("draw", "text-box"))
                para = ET.SubElement(tb, _ns("text", "p"))
                para.text = elem.get("text", "")


def _xml_to_string(root: ET.Element) -> str:
    """Convert an ElementTree element to a string with XML declaration."""
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(
        root, encoding="unicode", xml_declaration=False
    )
