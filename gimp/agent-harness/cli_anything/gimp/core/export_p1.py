# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403


def list_presets() -> list:
    """List available export presets."""
    result = []
    for name, p in EXPORT_PRESETS.items():
        result.append(
            {
                "name": name,
                "format": p["format"],
                "extension": p["ext"],
                "params": p["params"],
            }
        )
    return result


def get_preset_info(name: str) -> Dict[str, Any]:
    """Get details about an export preset."""
    if name not in EXPORT_PRESETS:
        raise ValueError(
            f"Unknown preset: {name}. Available: {list(EXPORT_PRESETS.keys())}"
        )
    p = EXPORT_PRESETS[name]
    return {
        "name": name,
        "format": p["format"],
        "extension": p["ext"],
        "params": p["params"],
    }


def _project_has_draw_ops(project):
    """Check whether any layer includes deferred draw operations."""
    return any(layer.get("draw_ops") for layer in project.get("layers", []))


def _render_text_layer(layer, canvas_w, canvas_h):
    """Render a text layer to an image (Pillow fallback path)."""
    from PIL import Image, ImageDraw, ImageFont

    text = layer.get("text", "")
    font_size = layer.get("font_size", 24)
    color = layer.get("color", "#000000")
    w = layer.get("width", canvas_w)
    h = layer.get("height", canvas_h)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size
        )
    except (OSError, IOError):
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except (OSError, IOError):
            font = ImageFont.load_default()

    draw.text((0, 0), text, fill=color, font=font)
    return img


def _load_layer(layer, canvas_w, canvas_h):
    """Load a layer's content as a PIL Image (Pillow fallback path)."""
    from PIL import Image

    layer_type = layer.get("type", "image")

    if layer_type == "image":
        source = layer.get("source")
        if source and os.path.exists(source):
            img = Image.open(source).convert("RGBA")
            return img
        fill = layer.get("fill", "transparent")
        w = layer.get("width", canvas_w)
        h = layer.get("height", canvas_h)
        if fill == "transparent":
            return Image.new("RGBA", (w, h), (0, 0, 0, 0))
        elif fill == "white":
            return Image.new("RGBA", (w, h), (255, 255, 255, 255))
        elif fill == "black":
            return Image.new("RGBA", (w, h), (0, 0, 0, 255))
        else:
            return Image.new("RGBA", (w, h), fill)

    elif layer_type == "solid":
        fill = layer.get("fill", "#ffffff")
        w = layer.get("width", canvas_w)
        h = layer.get("height", canvas_h)
        return Image.new("RGBA", (w, h), fill)

    elif layer_type == "text":
        return _render_text_layer(layer, canvas_w, canvas_h)

    return None


def _load_font(font_name, font_size):
    """Best-effort font loading for Pillow rendering."""
    from PIL import ImageFont

    candidate_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
        "arial.ttf",
        font_name,
    ]
    for candidate in candidate_paths:
        try:
            return ImageFont.truetype(candidate, font_size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()
