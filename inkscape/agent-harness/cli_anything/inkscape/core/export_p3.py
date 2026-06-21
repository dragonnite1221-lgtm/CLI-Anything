# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403

# fmt: off
from .export_p2 import _render_object  # noqa: E402,E501
# fmt: on


def render_to_png(
    project: Dict[str, Any],
    output_path: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    dpi: int = 96,
    background: Optional[str] = None,
    overwrite: bool = False,
) -> Dict[str, Any]:
    """Render the SVG document to a PNG file using Pillow.

    This renders basic shapes (rect, circle, ellipse, line, text, polygon)
    using Pillow's drawing API. For complex SVG features (filters, gradients,
    clip paths), Inkscape's CLI would be needed.
    """
    if os.path.exists(output_path) and not overwrite:
        raise FileExistsError(f"Output file already exists: {output_path}")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    doc = project.get("document", {})
    doc_width = int(doc.get("width", 1920))
    doc_height = int(doc.get("height", 1080))

    # Use specified dimensions or document dimensions
    img_width = width or doc_width
    img_height = height or doc_height
    bg = background or doc.get("background", "#ffffff")

    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        # If Pillow is not available, generate an SVG + Inkscape command
        svg_path = output_path.rsplit(".", 1)[0] + ".svg"
        save_svg(project, svg_path)
        inkscape_cmd = (
            f"inkscape {svg_path} --export-filename={output_path} --export-dpi={dpi}"
        )
        return {
            "status": "svg_generated",
            "svg_path": svg_path,
            "inkscape_command": inkscape_cmd,
            "message": "Pillow not available. Use Inkscape to render.",
        }

    # Create image
    img = Image.new("RGBA", (img_width, img_height), bg)
    draw = ImageDraw.Draw(img)

    # Scale factor if rendering at different size
    sx = img_width / doc_width if doc_width else 1
    sy = img_height / doc_height if doc_height else 1

    # Render visible objects from bottom layer to top
    for layer in project.get("layers", []):
        if not layer.get("visible", True):
            continue

        layer_obj_ids = set(layer.get("objects", []))
        for obj in project.get("objects", []):
            if obj.get("id") in layer_obj_ids or obj.get("layer") == layer.get("id"):
                _render_object(draw, obj, sx, sy)

    # Save
    img.save(output_path, "PNG")

    return {
        "output": output_path,
        "format": "png",
        "width": img_width,
        "height": img_height,
        "dpi": dpi,
        "size_bytes": os.path.getsize(output_path),
    }
