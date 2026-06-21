# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403

# fmt: off
from .export_p3 import _apply_single_filter  # noqa: E402,E501
# fmt: on


def _apply_filters(img, filters):
    """Apply a chain of filters to an image (Pillow fallback path)."""
    for f in filters:
        name = f["name"]
        params = f.get("params", {})
        img = _apply_single_filter(img, name, params)
    return img


def _blend_with_mode(base, layer, mode):
    """Apply blend mode using numpy pixel math (Pillow fallback path)."""
    import numpy as np
    from PIL import Image

    base_arr = np.array(base, dtype=np.float64)
    layer_arr = np.array(layer, dtype=np.float64)

    # Extract channels
    b_rgb = base_arr[:, :, :3] / 255.0
    l_rgb = layer_arr[:, :, :3] / 255.0
    b_alpha = base_arr[:, :, 3:4] / 255.0
    l_alpha = layer_arr[:, :, 3:4] / 255.0

    # Apply blend formula to RGB channels
    if mode == "multiply":
        blended = b_rgb * l_rgb
    elif mode == "screen":
        blended = 1.0 - (1.0 - b_rgb) * (1.0 - l_rgb)
    elif mode == "overlay":
        mask = b_rgb < 0.5
        blended = np.where(mask, 2 * b_rgb * l_rgb, 1 - 2 * (1 - b_rgb) * (1 - l_rgb))
    elif mode == "soft_light":
        blended = np.where(
            l_rgb <= 0.5,
            b_rgb - (1 - 2 * l_rgb) * b_rgb * (1 - b_rgb),
            b_rgb + (2 * l_rgb - 1) * (np.sqrt(b_rgb) - b_rgb),
        )
    elif mode == "hard_light":
        mask = l_rgb < 0.5
        blended = np.where(mask, 2 * b_rgb * l_rgb, 1 - 2 * (1 - b_rgb) * (1 - l_rgb))
    elif mode == "difference":
        blended = np.abs(b_rgb - l_rgb)
    elif mode == "darken":
        blended = np.minimum(b_rgb, l_rgb)
    elif mode == "lighten":
        blended = np.maximum(b_rgb, l_rgb)
    elif mode == "color_dodge":
        blended = np.clip(b_rgb / (1.0 - l_rgb + 1e-10), 0, 1)
    elif mode == "color_burn":
        blended = np.clip(1.0 - (1.0 - b_rgb) / (l_rgb + 1e-10), 0, 1)
    elif mode == "addition":
        blended = np.clip(b_rgb + l_rgb, 0, 1)
    elif mode == "subtract":
        blended = np.clip(b_rgb - l_rgb, 0, 1)
    elif mode == "grain_merge":
        blended = np.clip(b_rgb + l_rgb - 0.5, 0, 1)
    elif mode == "grain_extract":
        blended = np.clip(b_rgb - l_rgb + 0.5, 0, 1)
    else:
        blended = l_rgb  # Fallback to normal

    # Composite: result = blended * layer_alpha + base * (1 - layer_alpha)
    result_rgb = blended * l_alpha + b_rgb * (1.0 - l_alpha)
    result_alpha = np.clip(b_alpha + l_alpha * (1.0 - b_alpha), 0, 1)

    result = np.concatenate([result_rgb, result_alpha], axis=2)
    result = np.clip(result * 255, 0, 255).astype(np.uint8)

    from PIL import Image as _Image

    return _Image.fromarray(result, "RGBA")


def _composite_layer(base, layer, offset_x, offset_y, opacity, blend_mode):
    """Composite a layer onto the base canvas (Pillow fallback path)."""
    from PIL import Image

    if base.mode != "RGBA":
        base = base.convert("RGBA")
    if layer.mode != "RGBA":
        layer = layer.convert("RGBA")

    if opacity < 1.0:
        alpha = layer.split()[3]
        alpha = alpha.point(lambda a: int(a * opacity))
        layer.putalpha(alpha)

    layer_canvas = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer_canvas.paste(layer, (offset_x, offset_y))

    if blend_mode == "normal":
        return Image.alpha_composite(base, layer_canvas)

    try:
        return _blend_with_mode(base, layer_canvas, blend_mode)
    except ImportError:
        return Image.alpha_composite(base, layer_canvas)


def _human_size(nbytes: int) -> str:
    """Convert byte count to human-readable string."""
    for unit in ("B", "KB", "MB", "GB"):
        if nbytes < 1024:
            return f"{nbytes:.1f} {unit}"
        nbytes /= 1024
    return f"{nbytes:.1f} TB"
