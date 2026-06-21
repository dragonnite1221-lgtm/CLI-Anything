# ruff: noqa: F403, F405, E501
from .document_base import *  # noqa: F403


def _object_to_svg_element(obj: Dict[str, Any]):
    """Convert a JSON object dict to an SVG element."""
    import xml.etree.ElementTree as ET
    from cli_anything.inkscape.core.text import layout_text_lines, text_anchor_x

    obj_type = obj.get("type", "")
    obj_id = obj.get("id", "")
    style = obj.get("style", "")
    transform = obj.get("transform", "")

    attribs = {"id": obj_id}
    if style:
        attribs["style"] = style
    if transform:
        attribs["transform"] = transform

    tag = None

    if obj_type == "rect":
        tag = f"{{{SVG_NS}}}rect"
        for attr in ("x", "y", "width", "height", "rx", "ry"):
            if attr in obj:
                attribs[attr] = str(obj[attr])

    elif obj_type == "circle":
        tag = f"{{{SVG_NS}}}circle"
        for attr in ("cx", "cy", "r"):
            if attr in obj:
                attribs[attr] = str(obj[attr])

    elif obj_type == "ellipse":
        tag = f"{{{SVG_NS}}}ellipse"
        for attr in ("cx", "cy", "rx", "ry"):
            if attr in obj:
                attribs[attr] = str(obj[attr])

    elif obj_type == "line":
        tag = f"{{{SVG_NS}}}line"
        for attr in ("x1", "y1", "x2", "y2"):
            if attr in obj:
                attribs[attr] = str(obj[attr])

    elif obj_type == "polygon":
        tag = f"{{{SVG_NS}}}polygon"
        if "points" in obj:
            attribs["points"] = obj["points"]

    elif obj_type == "polyline":
        tag = f"{{{SVG_NS}}}polyline"
        if "points" in obj:
            attribs["points"] = obj["points"]

    elif obj_type == "path":
        tag = f"{{{SVG_NS}}}path"
        if "d" in obj:
            attribs["d"] = obj["d"]

    elif obj_type == "text":
        tag = f"{{{SVG_NS}}}text"
        anchor_x = text_anchor_x(obj)
        attribs["x"] = str(anchor_x)
        if "y" in obj:
            attribs["y"] = str(obj["y"])
        elem = ET.Element(tag, attribs)
        lines = layout_text_lines(obj)
        if len(lines) == 1:
            elem.text = lines[0]
            return elem
        font_size = float(obj.get("font_size", 24) or 24)
        line_height = float(obj.get("line_height", 1.2) or 1.2)
        y = float(obj.get("y", 0))
        for idx, line in enumerate(lines):
            tspan_attribs = {"x": str(anchor_x)}
            if idx == 0:
                tspan_attribs["y"] = str(y)
            else:
                tspan_attribs["dy"] = str(font_size * line_height)
            tspan = ET.SubElement(elem, f"{{{SVG_NS}}}tspan", tspan_attribs)
            tspan.text = line
        return elem

    elif obj_type == "image":
        tag = f"{{{SVG_NS}}}image"
        for attr in ("x", "y", "width", "height"):
            if attr in obj:
                attribs[attr] = str(obj[attr])
        if "href" in obj:
            attribs[f"{{{INKSCAPE_NS}}}href"] = obj["href"]
            attribs["href"] = obj["href"]

    elif obj_type == "star":
        # Stars are represented as paths in SVG
        tag = f"{{{SVG_NS}}}path"
        if "d" in obj:
            attribs["d"] = obj["d"]
        attribs[_ns("sodipodi", "type")] = "star"

    else:
        return None

    if tag is None:
        return None

    return ET.Element(tag, attribs)
