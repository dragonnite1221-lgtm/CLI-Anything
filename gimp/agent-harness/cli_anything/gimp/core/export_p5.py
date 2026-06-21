# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403

# fmt: off
from .export_p1 import _load_layer  # noqa: E402,E501
from .export_p2 import _apply_draw_ops  # noqa: E402,E501
from .export_p4 import _apply_filters, _composite_layer, _human_size  # noqa: E402,E501
# fmt: on


def _render_via_pillow(
    project: Dict[str, Any],
    output_path: str,
    preset: str = "png",
    overwrite: bool = False,
    quality: Optional[int] = None,
    format_override: Optional[str] = None,
) -> Dict[str, Any]:
    """Render the project using Pillow (fallback when GIMP is absent)."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        raise RuntimeError(
            "Neither GIMP nor Pillow is available.  Install one of:\n"
            "  apt install gimp        # recommended\n"
            "  pip install Pillow       # fallback"
        )

    if os.path.exists(output_path) and not overwrite:
        raise FileExistsError(f"Output file exists: {output_path}. Use --overwrite.")

    canvas = project["canvas"]
    cw, ch = canvas["width"], canvas["height"]
    bg_color = canvas.get("background", "#ffffff")
    mode = canvas.get("color_mode", "RGB")

    if format_override:
        fmt = format_override.upper()
        save_params = {}
    elif preset in EXPORT_PRESETS:
        p = EXPORT_PRESETS[preset]
        fmt = p["format"]
        save_params = dict(p["params"])
    else:
        raise ValueError(f"Unknown preset: {preset}")

    if quality is not None:
        save_params["quality"] = quality

    if mode in ("RGBA", "LA"):
        canvas_img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        if bg_color.lower() != "transparent":
            bg = Image.new("RGBA", (cw, ch), bg_color)
            canvas_img = Image.alpha_composite(canvas_img, bg)
    else:
        canvas_img = Image.new("RGB", (cw, ch), bg_color)

    layers = project.get("layers", [])

    for layer in reversed(layers):
        if not layer.get("visible", True):
            continue

        layer_img = _load_layer(layer, cw, ch)
        if layer_img is None:
            continue

        layer_img = _apply_filters(layer_img, layer.get("filters", []))
        layer_img = _apply_draw_ops(layer_img, layer.get("draw_ops", []))

        if "_scale_x" in layer:
            new_w = max(1, round(layer_img.width * layer["_scale_x"]))
            new_h = max(1, round(layer_img.height * layer["_scale_y"]))
            resample_map = {
                "nearest": Image.NEAREST,
                "bilinear": Image.BILINEAR,
                "bicubic": Image.BICUBIC,
                "lanczos": Image.LANCZOS,
            }
            resample = resample_map.get(
                layer.get("_resample", "lanczos"), Image.LANCZOS
            )
            layer_img = layer_img.resize((new_w, new_h), resample)

        ox = layer.get("offset_x", 0)
        oy = layer.get("offset_y", 0)
        opacity = layer.get("opacity", 1.0)

        canvas_img = _composite_layer(
            canvas_img, layer_img, ox, oy, opacity, layer.get("blend_mode", "normal")
        )

    if fmt == "JPEG":
        if canvas_img.mode == "RGBA":
            bg = Image.new("RGB", canvas_img.size, (255, 255, 255))
            bg.paste(canvas_img, mask=canvas_img.split()[3])
            canvas_img = bg
        elif canvas_img.mode != "RGB":
            canvas_img = canvas_img.convert("RGB")
    elif fmt == "GIF":
        canvas_img = canvas_img.convert("P", palette=Image.ADAPTIVE, colors=256)

    dpi = canvas.get("dpi", 72)
    save_params["dpi"] = (dpi, dpi)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    canvas_img.save(output_path, format=fmt, **save_params)

    result = {
        "output": os.path.abspath(output_path),
        "format": fmt,
        "size": f"{canvas_img.width}x{canvas_img.height}",
        "file_size": os.path.getsize(output_path),
        "file_size_human": _human_size(os.path.getsize(output_path)),
        "preset": preset,
        "method": "pillow",
        "layers_rendered": sum(1 for l in layers if l.get("visible", True)),
    }

    return result
