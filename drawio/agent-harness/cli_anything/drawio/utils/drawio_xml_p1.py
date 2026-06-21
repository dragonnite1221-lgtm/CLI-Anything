# ruff: noqa: F403, F405, E501
from .drawio_xml_base import *  # noqa: F403


def parse_drawio(path: str) -> ET.Element:
    """Parse a .drawio XML file. Returns the root <mxfile> element."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    tree = ET.parse(path)
    return tree.getroot()


def write_drawio(root: ET.Element, path: str) -> None:
    """Write an XML tree to a .drawio file."""
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(path, xml_declaration=True, encoding="utf-8")


def xml_to_string(root: ET.Element) -> str:
    """Serialize an XML tree to a UTF-8 string."""
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="unicode")


def _new_id(prefix: str = "cell") -> str:
    """Generate a unique ID."""
    return f"{prefix}_{int(time.time() * 1000000)}"


def create_blank_diagram(
    page_width: int = 850, page_height: int = 1100, grid_size: int = 10
) -> ET.Element:
    """Create a new blank draw.io diagram XML.

    Args:
        page_width: Page width in pixels.
        page_height: Page height in pixels.
        grid_size: Grid snap size.

    Returns:
        Root <mxfile> element.
    """
    mxfile = ET.Element("mxfile")
    mxfile.set("host", "cli-anything")
    mxfile.set("agent", "cli-anything-drawio/1.0.0")
    mxfile.set("version", "24.0.0")

    diagram = ET.SubElement(mxfile, "diagram")
    diagram.set("id", _new_id("diagram"))
    diagram.set("name", "Page-1")

    model = ET.SubElement(diagram, "mxGraphModel")
    model.set("dx", "1200")
    model.set("dy", "800")
    model.set("grid", "1")
    model.set("gridSize", str(grid_size))
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

    # Default system cells (always present)
    cell0 = ET.SubElement(root, "mxCell")
    cell0.set("id", "0")

    cell1 = ET.SubElement(root, "mxCell")
    cell1.set("id", "1")
    cell1.set("parent", "0")

    return mxfile


def get_diagram(mxfile: ET.Element, index: int = 0) -> ET.Element:
    """Get a <diagram> element by index."""
    diagrams = mxfile.findall("diagram")
    if not diagrams:
        raise RuntimeError("No diagram found in file")
    if index >= len(diagrams):
        raise IndexError(f"Diagram index {index} out of range (have {len(diagrams)})")
    return diagrams[index]


def get_model(mxfile: ET.Element, diagram_index: int = 0) -> ET.Element:
    """Get the <mxGraphModel> element."""
    diagram = get_diagram(mxfile, diagram_index)
    model = diagram.find("mxGraphModel")
    if model is None:
        raise RuntimeError("No mxGraphModel found in diagram")
    return model


def get_root(mxfile: ET.Element, diagram_index: int = 0) -> ET.Element:
    """Get the <root> element containing all cells."""
    model = get_model(mxfile, diagram_index)
    root = model.find("root")
    if root is None:
        raise RuntimeError("No root element found in mxGraphModel")
    return root


def get_all_cells(mxfile: ET.Element, diagram_index: int = 0) -> list[ET.Element]:
    """Get all user mxCell elements (excluding system cells id=0 and id=1)."""
    root = get_root(mxfile, diagram_index)
    cells = []
    for cell in root.findall("mxCell"):
        cid = cell.get("id", "")
        if cid not in ("0", "1"):
            cells.append(cell)
    return cells


def get_vertices(mxfile: ET.Element, diagram_index: int = 0) -> list[ET.Element]:
    """Get all shape (vertex) cells."""
    return [c for c in get_all_cells(mxfile, diagram_index) if c.get("vertex") == "1"]


def get_edges(mxfile: ET.Element, diagram_index: int = 0) -> list[ET.Element]:
    """Get all edge (connector) cells."""
    return [c for c in get_all_cells(mxfile, diagram_index) if c.get("edge") == "1"]


def find_cell_by_id(
    mxfile: ET.Element, cell_id: str, diagram_index: int = 0
) -> Optional[ET.Element]:
    """Find a cell by its ID."""
    root = get_root(mxfile, diagram_index)
    for cell in root.iter("mxCell"):
        if cell.get("id") == cell_id:
            return cell
    return None


def get_cell_geometry(cell: ET.Element) -> dict:
    """Get the geometry of a cell as a dict."""
    geo = cell.find("mxGeometry")
    if geo is None:
        return {}
    return {
        "x": float(geo.get("x", "0")),
        "y": float(geo.get("y", "0")),
        "width": float(geo.get("width", "0")),
        "height": float(geo.get("height", "0")),
    }


def get_cell_info(cell: ET.Element) -> dict:
    """Get summary info for a cell."""
    info = {
        "id": cell.get("id", ""),
        "value": cell.get("value", ""),
        "style": cell.get("style", ""),
    }
    if cell.get("vertex") == "1":
        info["type"] = "vertex"
        info.update(get_cell_geometry(cell))
    elif cell.get("edge") == "1":
        info["type"] = "edge"
        info["source"] = cell.get("source", "")
        info["target"] = cell.get("target", "")
    return info
