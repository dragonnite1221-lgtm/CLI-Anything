# ruff: noqa: F403, F405, E501
from .svg_utils_base import *  # noqa: F403


def _ns(prefix: str, local: str) -> str:
    """Build a Clark-notation tag like {http://...}local."""
    return f"{{{NSMAP[prefix]}}}{local}"


def create_svg_element(
    width: float = 1920,
    height: float = 1080,
    units: str = "px",
    viewbox: Optional[str] = None,
) -> ET.Element:
    """Create a root <svg> element with Inkscape namespaces."""
    if viewbox is None:
        viewbox = f"0 0 {width} {height}"

    # Do NOT include xmlns attributes manually -- ET.register_namespace
    # handles namespace declarations automatically during serialization.
    # Including them as attributes causes "duplicate attribute" parse errors.
    attribs = {
        "width": f"{width}{units}",
        "height": f"{height}{units}",
        "viewBox": viewbox,
        "version": "1.1",
        _ns("inkscape", "version"): "inkscape-cli 1.0",
    }

    svg = ET.Element(f"{{{SVG_NS}}}svg", attribs)

    # Add <defs> element for gradients, symbols, etc.
    ET.SubElement(svg, f"{{{SVG_NS}}}defs")

    # Add sodipodi:namedview for Inkscape-specific metadata
    ET.SubElement(
        svg,
        _ns("sodipodi", "namedview"),
        {
            "id": "namedview1",
            _ns("inkscape", "document-units"): units,
            "pagecolor": "#ffffff",
            "bordercolor": "#666666",
        },
    )

    return svg


def parse_svg(svg_string: str) -> ET.Element:
    """Parse an SVG string into an ElementTree Element."""
    return ET.fromstring(svg_string)


def parse_svg_file(path: str) -> ET.Element:
    """Parse an SVG file into an ElementTree Element."""
    tree = ET.parse(path)
    return tree.getroot()


def serialize_svg(svg_element: ET.Element, xml_declaration: bool = True) -> str:
    """Serialize an SVG element to a string."""
    # Use ET.tostring and add XML declaration manually
    raw = ET.tostring(svg_element, encoding="unicode")

    if xml_declaration:
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + raw
    return raw


def write_svg_file(svg_element: ET.Element, path: str) -> str:
    """Write an SVG element to a file."""
    content = serialize_svg(svg_element)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def parse_style(style_str: str) -> Dict[str, str]:
    """Parse a CSS style string into a dict.

    Example: "fill:#ff0000;stroke:#000;stroke-width:2" ->
             {"fill": "#ff0000", "stroke": "#000", "stroke-width": "2"}
    """
    if not style_str or not style_str.strip():
        return {}
    result = {}
    for part in style_str.split(";"):
        part = part.strip()
        if not part or ":" not in part:
            continue
        key, _, value = part.partition(":")
        result[key.strip()] = value.strip()
    return result


def serialize_style(style_dict: Dict[str, str]) -> str:
    """Serialize a style dict into a CSS style string.

    Example: {"fill": "#ff0000", "stroke": "#000"} ->
             "fill:#ff0000;stroke:#000"
    """
    if not style_dict:
        return ""
    return ";".join(f"{k}:{v}" for k, v in style_dict.items())


def get_element_style(element: ET.Element) -> Dict[str, str]:
    """Get the parsed style of an SVG element."""
    return parse_style(element.get("style", ""))


def set_element_style(element: ET.Element, style_dict: Dict[str, str]) -> None:
    """Set the style of an SVG element from a dict."""
    element.set("style", serialize_style(style_dict))


def update_element_style(
    element: ET.Element, updates: Dict[str, str]
) -> Dict[str, str]:
    """Update specific style properties on an element; returns the full new style dict."""
    current = get_element_style(element)
    current.update(updates)
    set_element_style(element, current)
    return current


_id_counter = 0


def generate_id(prefix: str = "obj") -> str:
    """Generate a unique ID for an SVG element."""
    global _id_counter
    _id_counter += 1
    return f"{prefix}{_id_counter}"


def reset_id_counter() -> None:
    """Reset the ID counter (useful for tests)."""
    global _id_counter
    _id_counter = 0


def find_defs(svg: ET.Element) -> ET.Element:
    """Find or create the <defs> element in an SVG root."""
    defs = svg.find(f"{{{SVG_NS}}}defs")
    if defs is None:
        defs = ET.SubElement(svg, f"{{{SVG_NS}}}defs")
    return defs


def find_all_shapes(svg: ET.Element) -> list:
    """Find all shape elements in an SVG (rect, circle, ellipse, line, etc.)."""
    shape_tags = [
        "rect",
        "circle",
        "ellipse",
        "line",
        "polyline",
        "polygon",
        "path",
        "text",
        "image",
    ]
    result = []
    for tag in shape_tags:
        result.extend(svg.iter(f"{{{SVG_NS}}}{tag}"))
    return result


def find_element_by_id(svg: ET.Element, element_id: str) -> Optional[ET.Element]:
    """Find an element by its 'id' attribute anywhere in the SVG tree."""
    for elem in svg.iter():
        if elem.get("id") == element_id:
            return elem
    return None
