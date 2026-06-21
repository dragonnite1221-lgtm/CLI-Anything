# ruff: noqa: F403, F405, E501
from .odf_utils_base import *  # noqa: F403

# fmt: off
from .odf_utils_p1 import _ns, _nsattr, _register_namespaces  # noqa: E402,E501
from .odf_utils_p3 import _build_writer_content  # noqa: E402,E501
from .odf_utils_p4 import _build_calc_content, _build_impress_content, _xml_to_string  # noqa: E402,E501
# fmt: on


def create_content_xml(doc_type: str, project: Dict[str, Any]) -> str:
    """Create content.xml for an ODF document from a project dict."""
    _register_namespaces()

    # Root element
    root = ET.Element(_ns("office", "document-content"))
    root.set(_nsattr("office", "version"), "1.2")

    # Automatic styles
    auto_styles = ET.SubElement(root, _ns("office", "automatic-styles"))

    if doc_type == "writer":
        _build_writer_content(root, auto_styles, project)
    elif doc_type == "calc":
        _build_calc_content(root, auto_styles, project)
    elif doc_type == "impress":
        _build_impress_content(root, auto_styles, project)

    return _xml_to_string(root)


def _apply_text_properties(tp: ET.Element, props: Dict) -> None:
    """Apply text properties from a style dict to an XML element."""
    if "font_size" in props:
        tp.set(_nsattr("fo", "font-size"), str(props["font_size"]))
    if "font_name" in props:
        tp.set(_nsattr("fo", "font-family"), str(props["font_name"]))
    if props.get("bold"):
        tp.set(_nsattr("fo", "font-weight"), "bold")
    if props.get("italic"):
        tp.set(_nsattr("fo", "font-style"), "italic")
    if props.get("underline"):
        tp.set(_nsattr("style", "text-underline-style"), "solid")
    if "color" in props:
        tp.set(_nsattr("fo", "color"), str(props["color"]))


def _apply_paragraph_properties(pp: ET.Element, props: Dict) -> None:
    """Apply paragraph properties from a style dict to an XML element."""
    if "alignment" in props:
        pp.set(_nsattr("fo", "text-align"), str(props["alignment"]))
    if "line_height" in props:
        pp.set(_nsattr("fo", "line-height"), str(props["line_height"]))
    if "margin_top" in props:
        pp.set(_nsattr("fo", "margin-top"), str(props["margin_top"]))
    if "margin_bottom" in props:
        pp.set(_nsattr("fo", "margin-bottom"), str(props["margin_bottom"]))


def create_styles_xml(doc_type: str, project: Dict[str, Any]) -> str:
    """Create styles.xml for an ODF document."""
    _register_namespaces()

    root = ET.Element(_ns("office", "document-styles"))
    root.set(_nsattr("office", "version"), "1.2")

    styles = ET.SubElement(root, _ns("office", "styles"))

    # Default paragraph style
    default_style = ET.SubElement(styles, _ns("style", "default-style"))
    default_style.set(_nsattr("style", "family"), "paragraph")
    tp = ET.SubElement(default_style, _ns("style", "text-properties"))
    tp.set(_nsattr("fo", "font-size"), "12pt")
    tp.set(_nsattr("fo", "font-family"), "Liberation Serif")

    # User-defined styles
    user_styles = project.get("styles", {})
    for style_name, style_def in user_styles.items():
        family = style_def.get("family", "paragraph")
        style_el = ET.SubElement(styles, _ns("style", "style"))
        style_el.set(_nsattr("style", "name"), style_name)
        style_el.set(_nsattr("style", "family"), family)
        if "parent" in style_def:
            style_el.set(_nsattr("style", "parent-style-name"), style_def["parent"])

        props = style_def.get("properties", {})
        if family == "paragraph":
            tp = ET.SubElement(style_el, _ns("style", "text-properties"))
            _apply_text_properties(tp, props)
            pp = ET.SubElement(style_el, _ns("style", "paragraph-properties"))
            _apply_paragraph_properties(pp, props)
        elif family == "text":
            tp = ET.SubElement(style_el, _ns("style", "text-properties"))
            _apply_text_properties(tp, props)

    # Automatic styles
    auto_styles = ET.SubElement(root, _ns("office", "automatic-styles"))

    # Page layout for writer
    if doc_type == "writer":
        settings = project.get("settings", {})
        pl = ET.SubElement(auto_styles, _ns("style", "page-layout"))
        pl.set(_nsattr("style", "name"), "PM1")
        plp = ET.SubElement(pl, _ns("style", "page-layout-properties"))
        plp.set(_nsattr("fo", "page-width"), settings.get("page_width", "21cm"))
        plp.set(_nsattr("fo", "page-height"), settings.get("page_height", "29.7cm"))
        plp.set(_nsattr("fo", "margin-top"), settings.get("margin_top", "2cm"))
        plp.set(_nsattr("fo", "margin-bottom"), settings.get("margin_bottom", "2cm"))
        plp.set(_nsattr("fo", "margin-left"), settings.get("margin_left", "2cm"))
        plp.set(_nsattr("fo", "margin-right"), settings.get("margin_right", "2cm"))

    # Master styles
    master_styles = ET.SubElement(root, _ns("office", "master-styles"))
    mp = ET.SubElement(master_styles, _ns("style", "master-page"))
    mp.set(_nsattr("style", "name"), "Default")
    if doc_type == "writer":
        mp.set(_nsattr("style", "page-layout-name"), "PM1")

    return _xml_to_string(root)
