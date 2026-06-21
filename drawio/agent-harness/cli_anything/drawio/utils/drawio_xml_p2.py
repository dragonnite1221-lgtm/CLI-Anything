# ruff: noqa: F403, F405, E501
from .drawio_xml_base import *  # noqa: F403

# fmt: off
from .drawio_xml_p1 import _new_id, find_cell_by_id, get_root  # noqa: E402,E501
# fmt: on


def parse_style(style_str: str) -> dict:
    """Parse a draw.io style string into a dict.

    Style format: "key1=value1;key2=value2;baseStyle;"
    Keys without values are treated as base style names (value="").
    """
    result = {}
    if not style_str:
        return result
    for part in style_str.split(";"):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            k, v = part.split("=", 1)
            result[k] = v
        else:
            result[part] = ""
    return result


def build_style(style_dict: dict) -> str:
    """Build a draw.io style string from a dict."""
    parts = []
    for k, v in style_dict.items():
        if v == "":
            parts.append(k)
        else:
            parts.append(f"{k}={v}")
    return ";".join(parts) + ";"


def set_style_property(cell: ET.Element, key: str, value: str) -> None:
    """Set a single style property on a cell."""
    style = parse_style(cell.get("style", ""))
    style[key] = value
    cell.set("style", build_style(style))


def remove_style_property(cell: ET.Element, key: str) -> None:
    """Remove a style property from a cell."""
    style = parse_style(cell.get("style", ""))
    style.pop(key, None)
    cell.set("style", build_style(style))


SHAPE_STYLES = {
    "rectangle": "rounded=0;whiteSpace=wrap;html=1;",
    "rounded": "rounded=1;whiteSpace=wrap;html=1;",
    "ellipse": "ellipse;whiteSpace=wrap;html=1;",
    "diamond": "rhombus;whiteSpace=wrap;html=1;",
    "triangle": "triangle;whiteSpace=wrap;html=1;",
    "hexagon": "shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;",
    "cylinder": "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;",
    "cloud": "ellipse;shape=cloud;whiteSpace=wrap;html=1;",
    "parallelogram": "shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;",
    "process": "shape=process;whiteSpace=wrap;html=1;backgroundOutline=1;",
    "document": "shape=document;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=0.27;",
    "callout": "shape=callout;whiteSpace=wrap;html=1;perimeter=calloutPerimeter;size=30;position=0.5;",
    "note": "shape=note;whiteSpace=wrap;html=1;backgroundOutline=1;size=15;",
    "actor": "shape=mxgraph.basic.person;whiteSpace=wrap;html=1;",
    "text": "text;html=1;align=center;verticalAlign=middle;resizable=0;points=[];autosize=1;",
}
EDGE_STYLES = {
    "straight": "edgeStyle=none;",
    "orthogonal": "edgeStyle=orthogonalEdgeStyle;rounded=0;",
    "curved": "edgeStyle=orthogonalEdgeStyle;curved=1;rounded=1;",
    "entity-relation": "edgeStyle=entityRelationEdgeStyle;",
}


def add_vertex(
    mxfile: ET.Element,
    shape_type: str,
    x: float,
    y: float,
    width: float,
    height: float,
    label: str = "",
    parent: str = "1",
    diagram_index: int = 0,
    cell_id: Optional[str] = None,
) -> str:
    """Add a shape (vertex) to the diagram.

    Args:
        mxfile: Root mxfile element.
        shape_type: Shape preset name (see SHAPE_STYLES) or raw style string.
        x, y: Position.
        width, height: Dimensions.
        label: Text label for the shape.
        parent: Parent cell ID (default "1" = default layer).
        cell_id: Optional custom ID. Auto-generated if not provided.

    Returns:
        The new cell's ID.
    """
    root = get_root(mxfile, diagram_index)
    if cell_id is None:
        cell_id = _new_id("v")
    elif find_cell_by_id(mxfile, cell_id, diagram_index) is not None:
        raise ValueError(f"Cell ID already exists: {cell_id}")

    cell = ET.SubElement(root, "mxCell")
    cell.set("id", cell_id)
    cell.set("value", label)

    # Resolve style
    if shape_type in SHAPE_STYLES:
        style = SHAPE_STYLES[shape_type]
    else:
        style = shape_type if ";" in shape_type else f"{shape_type};"
    cell.set("style", style)
    cell.set("vertex", "1")
    cell.set("parent", parent)

    geo = ET.SubElement(cell, "mxGeometry")
    geo.set("x", str(x))
    geo.set("y", str(y))
    geo.set("width", str(width))
    geo.set("height", str(height))
    geo.set("as", "geometry")

    return cell_id
