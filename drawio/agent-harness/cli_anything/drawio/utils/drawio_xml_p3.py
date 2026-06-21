# ruff: noqa: F403, F405, E501
from .drawio_xml_base import *  # noqa: F403

# fmt: off
from .drawio_xml_p1 import _new_id, find_cell_by_id, get_all_cells, get_root  # noqa: E402,E501
from .drawio_xml_p2 import EDGE_STYLES  # noqa: E402,E501
# fmt: on


def add_edge(
    mxfile: ET.Element,
    source_id: str,
    target_id: str,
    edge_style: str = "orthogonal",
    label: str = "",
    parent: str = "1",
    diagram_index: int = 0,
    edge_id: Optional[str] = None,
) -> str:
    """Add an edge (connector) between two cells.

    Args:
        mxfile: Root mxfile element.
        source_id: Source cell ID.
        target_id: Target cell ID.
        edge_style: Edge style preset name (see EDGE_STYLES) or raw style string.
        label: Optional edge label.
        parent: Parent cell ID.
        edge_id: Optional custom ID. Auto-generated if not provided.

    Returns:
        The new edge's ID.
    """
    root = get_root(mxfile, diagram_index)
    if edge_id is None:
        edge_id = _new_id("e")
    elif find_cell_by_id(mxfile, edge_id, diagram_index) is not None:
        raise ValueError(f"Cell ID already exists: {edge_id}")

    cell = ET.SubElement(root, "mxCell")
    cell.set("id", edge_id)
    cell.set("value", label)

    # Resolve style
    if edge_style in EDGE_STYLES:
        style = EDGE_STYLES[edge_style]
    else:
        style = edge_style if ";" in edge_style else f"{edge_style};"
    cell.set("style", style)
    cell.set("edge", "1")
    cell.set("parent", parent)
    cell.set("source", source_id)
    cell.set("target", target_id)

    geo = ET.SubElement(cell, "mxGeometry")
    geo.set("relative", "1")
    geo.set("as", "geometry")

    return edge_id


def remove_cell(mxfile: ET.Element, cell_id: str, diagram_index: int = 0) -> bool:
    """Remove a cell by ID. Also removes edges connected to it.

    Returns True if the cell was found and removed.
    """
    root = get_root(mxfile, diagram_index)
    removed = False

    # First collect edges connected to this cell
    to_remove = []
    for cell in root.findall("mxCell"):
        cid = cell.get("id", "")
        if cid == cell_id:
            to_remove.append(cell)
            removed = True
        elif cell.get("source") == cell_id or cell.get("target") == cell_id:
            to_remove.append(cell)

    for cell in to_remove:
        root.remove(cell)

    return removed


def update_cell_label(
    mxfile: ET.Element, cell_id: str, label: str, diagram_index: int = 0
) -> bool:
    """Update a cell's label. Returns True if found."""
    cell = find_cell_by_id(mxfile, cell_id, diagram_index)
    if cell is None:
        return False
    cell.set("value", label)
    return True


def move_cell(
    mxfile: ET.Element, cell_id: str, x: float, y: float, diagram_index: int = 0
) -> bool:
    """Move a cell to a new position. Returns True if found."""
    cell = find_cell_by_id(mxfile, cell_id, diagram_index)
    if cell is None:
        return False
    geo = cell.find("mxGeometry")
    if geo is None:
        return False
    geo.set("x", str(x))
    geo.set("y", str(y))
    return True


def resize_cell(
    mxfile: ET.Element,
    cell_id: str,
    width: float,
    height: float,
    diagram_index: int = 0,
) -> bool:
    """Resize a cell. Returns True if found."""
    cell = find_cell_by_id(mxfile, cell_id, diagram_index)
    if cell is None:
        return False
    geo = cell.find("mxGeometry")
    if geo is None:
        return False
    geo.set("width", str(width))
    geo.set("height", str(height))
    return True


def add_page(
    mxfile: ET.Element, name: str = "", page_width: int = 850, page_height: int = 1100
) -> str:
    """Add a new diagram page. Returns the diagram ID."""
    existing = mxfile.findall("diagram")
    index = len(existing) + 1
    page_name = name or f"Page-{index}"

    diagram_id = _new_id("diagram")
    diagram = ET.SubElement(mxfile, "diagram")
    diagram.set("id", diagram_id)
    diagram.set("name", page_name)

    model = ET.SubElement(diagram, "mxGraphModel")
    model.set("dx", "1200")
    model.set("dy", "800")
    model.set("grid", "1")
    model.set("gridSize", "10")
    model.set("guides", "1")
    model.set("tooltips", "1")
    model.set("connect", "1")
    model.set("arrows", "1")
    model.set("fold", "1")
    model.set("page", "1")
    model.set("pageScale", "1")
    model.set("pageWidth", str(page_width))
    model.set("pageHeight", str(page_height))
    model.set("math", "0")
    model.set("shadow", "0")

    root = ET.SubElement(model, "root")
    cell0 = ET.SubElement(root, "mxCell")
    cell0.set("id", "0")
    cell1 = ET.SubElement(root, "mxCell")
    cell1.set("id", "1")
    cell1.set("parent", "0")

    return diagram_id


def list_pages(mxfile: ET.Element) -> list[dict]:
    """List all diagram pages."""
    pages = []
    for i, diagram in enumerate(mxfile.findall("diagram")):
        cell_count = len(get_all_cells(mxfile, i))
        pages.append(
            {
                "index": i,
                "id": diagram.get("id", ""),
                "name": diagram.get("name", f"Page-{i + 1}"),
                "cell_count": cell_count,
            }
        )
    return pages
