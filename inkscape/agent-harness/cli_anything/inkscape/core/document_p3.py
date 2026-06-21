# ruff: noqa: F403, F405, E501
from .document_base import *  # noqa: F403

# fmt: off
from .document_p1 import _add_gradient_to_defs  # noqa: E402,E501
from .document_p2 import _object_to_svg_element  # noqa: E402,E501
# fmt: on


def project_to_svg(project: Dict[str, Any]):
    """Convert project JSON to an SVG ElementTree Element."""
    import xml.etree.ElementTree as ET

    doc = project.get("document", {})
    width = doc.get("width", 1920)
    height = doc.get("height", 1080)
    units = doc.get("units", "px")

    svg = create_svg_element(width=width, height=height, units=units)

    # Add background rect if not transparent
    bg = doc.get("background", "#ffffff")
    if bg and bg.lower() not in ("none", "transparent"):
        bg_rect = ET.SubElement(
            svg,
            f"{{{SVG_NS}}}rect",
            {
                "id": "background",
                "width": str(width),
                "height": str(height),
                "x": "0",
                "y": "0",
                "style": f"fill:{bg};stroke:none",
            },
        )

    # Add gradient definitions
    defs = svg.find(f"{{{SVG_NS}}}defs")
    if defs is None:
        defs = ET.SubElement(svg, f"{{{SVG_NS}}}defs")

    for grad in project.get("gradients", []):
        _add_gradient_to_defs(defs, grad)

    # Add layers as <g> elements with Inkscape groupmode
    for layer in project.get("layers", []):
        layer_g = ET.SubElement(
            svg,
            f"{{{SVG_NS}}}g",
            {
                "id": layer.get("id", "layer1"),
                _ns("inkscape", "groupmode"): "layer",
                _ns("inkscape", "label"): layer.get("name", "Layer"),
            },
        )
        if not layer.get("visible", True):
            layer_g.set("style", "display:none")
        elif layer.get("opacity", 1.0) < 1.0:
            layer_g.set("style", f"opacity:{layer['opacity']}")

        # Add objects belonging to this layer
        layer_obj_ids = set(layer.get("objects", []))
        for obj in project.get("objects", []):
            if obj.get("id") in layer_obj_ids or (obj.get("layer") == layer.get("id")):
                elem = _object_to_svg_element(obj)
                if elem is not None:
                    layer_g.append(elem)

    # Add objects not in any layer directly to SVG root
    all_layer_ids = set()
    for layer in project.get("layers", []):
        all_layer_ids.update(layer.get("objects", []))
        all_layer_ids.add(layer.get("id", ""))

    for obj in project.get("objects", []):
        obj_id = obj.get("id", "")
        obj_layer = obj.get("layer", "")
        if obj_id not in all_layer_ids and obj_layer not in [
            l.get("id") for l in project.get("layers", [])
        ]:
            elem = _object_to_svg_element(obj)
            if elem is not None:
                svg.append(elem)

    return svg


def save_svg(project: Dict[str, Any], path: str) -> str:
    """Generate and save a valid SVG file from the project state."""
    svg = project_to_svg(project)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    write_svg_file(svg, path)
    return path
