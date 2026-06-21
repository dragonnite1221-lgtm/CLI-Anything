# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403


def _make_png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    """Build a single PNG chunk with correct CRC."""
    chunk_body = chunk_type + data
    crc = struct.pack(">I", zlib.crc32(chunk_body) & 0xFFFFFFFF)
    length = struct.pack(">I", len(data))
    return length + chunk_body + crc


def _make_blank_png(width: int, height: int) -> bytes:
    """Create a minimal valid RGBA PNG of the given dimensions (fully transparent)."""
    png_signature = b"\x89PNG\r\n\x1a\n"

    # IHDR: width, height, bit depth 8, color type 6 (RGBA)
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    ihdr = _make_png_chunk(b"IHDR", ihdr_data)

    # IDAT: zlib-compressed scanlines (filter byte 0 + 4 zero bytes per pixel)
    raw_scanlines = b""
    for _ in range(height):
        raw_scanlines += b"\x00" + (b"\x00" * width * 4)
    compressed = zlib.compress(raw_scanlines)
    idat = _make_png_chunk(b"IDAT", compressed)

    # IEND
    iend = _make_png_chunk(b"IEND", b"")

    return png_signature + ihdr + idat + iend


def _layer_filename(layer_name: str) -> str:
    """Derive a safe filename for a layer inside the .kra archive."""
    safe = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in layer_name)
    return safe


def _build_maindoc_xml(project: dict) -> bytes:
    """Build maindoc.xml content from project state."""
    image_props = project.get("image", {})
    width = image_props.get("width", 1920)
    height = image_props.get("height", 1080)
    colorspace = image_props.get("colorspace", "RGBA")
    color_depth = image_props.get("color_depth", "U8")
    name = image_props.get("name", "Untitled")
    resolution = image_props.get("resolution", 72.0)

    doc = ET.Element("DOC")
    doc.set("xmlns", "http://www.calligra.org/DTD/krita")
    doc.set("editor", "CLI-Anything Krita Harness")
    doc.set("syntaxVersion", "2.0")

    image_el = ET.SubElement(doc, "IMAGE")
    image_el.set("name", name)
    image_el.set("width", str(width))
    image_el.set("height", str(height))
    image_el.set("colorspacename", colorspace)
    image_el.set("x-res", str(resolution))
    image_el.set("y-res", str(resolution))
    image_el.set("mime", "application/x-kra")

    layers_el = ET.SubElement(image_el, "layers")

    layers = project.get("layers", [])
    if not layers:
        # Create a default paint layer
        layers = [
            {
                "name": "Background",
                "type": "paintlayer",
                "visible": True,
                "opacity": 255,
                "uuid": "00000000-0000-0000-0000-000000000001",
            }
        ]

    for layer in layers:
        layer_type = layer.get("type", "paintlayer")
        if layer_type != "paintlayer":
            continue
        layer_el = ET.SubElement(layers_el, "layer")
        layer_el.set("name", layer.get("name", "Layer"))
        layer_el.set("nodetype", "paintlayer")
        layer_el.set("visible", "1" if layer.get("visible", True) else "0")
        layer_el.set("opacity", str(layer.get("opacity", 255)))
        layer_el.set("colorspacename", colorspace)
        layer_el.set("filename", _layer_filename(layer.get("name", "Layer")))
        uuid_val = layer.get("uuid", "")
        if uuid_val:
            layer_el.set("uuid", str(uuid_val))

    tree = ET.ElementTree(doc)
    from io import BytesIO

    buf = BytesIO()
    tree.write(buf, encoding="UTF-8", xml_declaration=True)
    return buf.getvalue()
