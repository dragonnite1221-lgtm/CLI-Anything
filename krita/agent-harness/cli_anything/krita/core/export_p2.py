# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403

# fmt: off
from .export_p1 import _build_maindoc_xml, _layer_filename, _make_blank_png  # noqa: E402,E501
# fmt: on


def _build_documentinfo_xml(project: dict) -> bytes:
    """Build documentinfo.xml with Dublin Core metadata."""
    image_props = project.get("image", {})
    name = image_props.get("name", "Untitled")
    author = project.get("author", "CLI-Anything")

    doc = ET.Element("document-info")
    doc.set("xmlns", "http://www.calligra.org/DTD/document-info")

    about = ET.SubElement(doc, "about")
    title_el = ET.SubElement(about, "title")
    title_el.text = name
    creator_el = ET.SubElement(about, "creator")
    creator_el.text = author
    date_el = ET.SubElement(about, "date")
    date_el.text = datetime.now(timezone.utc).isoformat()

    tree = ET.ElementTree(doc)
    from io import BytesIO

    buf = BytesIO()
    tree.write(buf, encoding="UTF-8", xml_declaration=True)
    return buf.getvalue()


def build_kra_from_project(project: dict, output_path: str) -> str:
    """
    Build a minimal valid .kra file (ZIP archive) from the project JSON state.

    Creates:
    - mimetype (first entry, uncompressed): ``application/x-kra``
    - maindoc.xml with image properties and layer stack
    - documentinfo.xml with Dublin Core metadata
    - A blank RGBA PNG for each paint layer under ``<image_name>/layers/``

    Parameters
    ----------
    project : dict
        The project JSON state containing image properties and layers.
    output_path : str
        Destination path for the ``.kra`` file.

    Returns
    -------
    str
        Absolute path to the created ``.kra`` file.
    """
    output_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    image_props = project.get("image", {})
    width = image_props.get("width", 1920)
    height = image_props.get("height", 1080)
    image_name = image_props.get("name", "Untitled")

    layers = project.get("layers", [])
    if not layers:
        layers = [
            {
                "name": "Background",
                "type": "paintlayer",
                "visible": True,
                "opacity": 255,
            }
        ]

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_STORED) as zf:
        # mimetype must be the first entry, uncompressed
        zf.writestr("mimetype", "application/x-kra", compress_type=zipfile.ZIP_STORED)

        # maindoc.xml
        zf.writestr("maindoc.xml", _build_maindoc_xml(project))

        # documentinfo.xml
        zf.writestr("documentinfo.xml", _build_documentinfo_xml(project))

        # Blank pixel layer PNGs
        blank_png = _make_blank_png(width, height)
        for layer in layers:
            if layer.get("type", "paintlayer") != "paintlayer":
                continue
            layer_name = layer.get("name", "Layer")
            filename = _layer_filename(layer_name)
            layer_path = f"{image_name}/layers/{filename}"
            zf.writestr(layer_path, blank_png)

    return output_path
