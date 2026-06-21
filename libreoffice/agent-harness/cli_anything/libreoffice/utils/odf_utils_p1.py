# ruff: noqa: F403, F405, E501
from .odf_utils_base import *  # noqa: F403


def _register_namespaces():
    """Register all ODF namespaces with ElementTree to preserve prefixes."""
    for prefix, uri in ODF_NS.items():
        ET.register_namespace(prefix, uri)


def _ns(prefix: str, local: str) -> str:
    """Create a fully-qualified XML element name."""
    return f"{{{ODF_NS[prefix]}}}{local}"


def _nsattr(prefix: str, local: str) -> str:
    """Create a fully-qualified XML attribute name."""
    return f"{{{ODF_NS[prefix]}}}{local}"


def _create_text_auto_style(
    auto_styles: ET.Element, name: str, style: Dict, parent_style: str = "Standard"
) -> None:
    """Create an automatic paragraph style."""
    style_el = ET.SubElement(auto_styles, _ns("style", "style"))
    style_el.set(_nsattr("style", "name"), name)
    style_el.set(_nsattr("style", "family"), "paragraph")

    # Text properties
    tp = ET.SubElement(style_el, _ns("style", "text-properties"))
    if "font_size" in style:
        tp.set(_nsattr("fo", "font-size"), str(style["font_size"]))
    if "font_name" in style:
        tp.set(_nsattr("fo", "font-family"), str(style["font_name"]))
    if style.get("bold"):
        tp.set(_nsattr("fo", "font-weight"), "bold")
    if style.get("italic"):
        tp.set(_nsattr("fo", "font-style"), "italic")
    if style.get("underline"):
        tp.set(_nsattr("style", "text-underline-style"), "solid")
        tp.set(_nsattr("style", "text-underline-width"), "auto")
    if "color" in style:
        tp.set(_nsattr("fo", "color"), str(style["color"]))

    # Paragraph properties
    pp = ET.SubElement(style_el, _ns("style", "paragraph-properties"))
    if "alignment" in style:
        pp.set(_nsattr("fo", "text-align"), str(style["alignment"]))


def _add_heading_element(
    parent: ET.Element, auto_styles: ET.Element, item: Dict, style_counter: list
) -> None:
    """Add a heading element to the content."""
    heading = ET.SubElement(parent, _ns("text", "h"))
    heading.set(_nsattr("text", "outline-level"), str(item.get("level", 1)))
    style = item.get("style", {})

    if style:
        style_name = f"H_auto{style_counter[0]}"
        style_counter[0] += 1
        heading.set(_nsattr("text", "style-name"), style_name)
        _create_text_auto_style(auto_styles, style_name, style, parent_style="Heading")
    heading.text = item.get("text", "")


def _create_char_auto_style(auto_styles: ET.Element, name: str, style: Dict) -> None:
    """Create an automatic character style for spans."""
    style_el = ET.SubElement(auto_styles, _ns("style", "style"))
    style_el.set(_nsattr("style", "name"), name)
    style_el.set(_nsattr("style", "family"), "text")

    tp = ET.SubElement(style_el, _ns("style", "text-properties"))
    if "font_size" in style:
        tp.set(_nsattr("fo", "font-size"), str(style["font_size"]))
    if "font_name" in style:
        tp.set(_nsattr("fo", "font-family"), str(style["font_name"]))
    if style.get("bold"):
        tp.set(_nsattr("fo", "font-weight"), "bold")
    if style.get("italic"):
        tp.set(_nsattr("fo", "font-style"), "italic")
    if style.get("underline"):
        tp.set(_nsattr("style", "text-underline-style"), "solid")
        tp.set(_nsattr("style", "text-underline-width"), "auto")
    if "color" in style:
        tp.set(_nsattr("fo", "color"), str(style["color"]))
