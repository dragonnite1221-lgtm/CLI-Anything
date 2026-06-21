# ruff: noqa: F403, F405, E501
from .gimp_backend_base import *  # noqa: F403


def _filter_to_script_fu(
    name: str, params: Dict[str, Any], img_var: str, drw_var: str
) -> Optional[str]:
    """Convert a CLI filter name + params into a Script-Fu expression.

    Returns None when there is no GIMP-native equivalent for *name*.
    """
    p = params or {}
    i, d = img_var, drw_var

    if name == "brightness":
        val = int((p.get("factor", 1.0) - 1.0) * 127)
        return f"(gimp-brightness-contrast {d} {val} 0)"
    if name == "contrast":
        val = int((p.get("factor", 1.0) - 1.0) * 127)
        return f"(gimp-brightness-contrast {d} 0 {val})"
    if name == "saturation":
        val = int((p.get("factor", 1.0) - 1.0) * 100)
        return f"(gimp-drawable-hue-saturation {d} HUE-RANGE-ALL 0 0 {val} 0)"
    if name == "sharpness":
        amt = max(0.0, p.get("factor", 1.0) - 1.0)
        return f"(plug-in-unsharp-mask RUN-NONINTERACTIVE {i} {d} 3.0 {amt:.2f} 0)"
    if name == "gaussian_blur":
        r = p.get("radius", 2.0)
        return f"(plug-in-gauss RUN-NONINTERACTIVE {i} {d} {r} {r} 0)"
    if name == "box_blur":
        r = p.get("radius", 2.0)
        return f"(plug-in-gauss RUN-NONINTERACTIVE {i} {d} {r} {r} 1)"
    if name == "unsharp_mask":
        r = p.get("radius", 2.0)
        pct = p.get("percent", 150) / 100.0
        t = p.get("threshold", 3)
        return f"(plug-in-unsharp-mask RUN-NONINTERACTIVE {i} {d} {r} {pct:.2f} {t})"
    if name == "smooth":
        return f"(plug-in-gauss RUN-NONINTERACTIVE {i} {d} 3 3 0)"
    if name == "invert":
        return f"(gimp-drawable-invert {d} FALSE)"
    if name == "grayscale":
        return f"(gimp-drawable-desaturate {d} DESATURATE-AVERAGE)"
    if name == "posterize":
        bits = p.get("bits", 4)
        return f"(gimp-drawable-posterize {d} {bits})"
    if name == "equalize":
        return f"(gimp-drawable-equalize {d} FALSE)"
    if name == "autocontrast":
        return f"(gimp-drawable-levels {d} HISTOGRAM-VALUE 0.0 1.0 FALSE 1.0 0.0 1.0 FALSE)"
    if name == "find_edges":
        return f"(plug-in-edge RUN-NONINTERACTIVE {i} {d} 1 0 0)"
    if name == "emboss":
        return f"(plug-in-emboss RUN-NONINTERACTIVE {i} {d} 315.0 45.0 7 TRUE)"
    if name == "contour":
        return f"(plug-in-edge RUN-NONINTERACTIVE {i} {d} 1 0 0)"
    if name == "detail":
        return f"(plug-in-unsharp-mask RUN-NONINTERACTIVE {i} {d} 3.0 0.3 0)"
    if name == "sepia":
        return f"(gimp-drawable-desaturate {d} DESATURATE-AVERAGE) (gimp-drawable-colorize-hsl {d} 35 40 0)"
    if name == "solarize":
        t = p.get("threshold", 128) / 255.0
        return f"(gimp-drawable-threshold {d} HISTOGRAM-VALUE {t:.3f} 1.0)"
    if name == "rotate":
        angle = p.get("angle", 0.0) * 0.017453292519943295  # deg→rad
        return f"(gimp-item-transform-rotate-default {d} {angle:.6f} TRUE 0 0)"
    if name == "flip_h":
        return f"(gimp-item-transform-flip-simple {d} ORIENTATION-HORIZONTAL TRUE 0)"
    if name == "flip_v":
        return f"(gimp-item-transform-flip-simple {d} ORIENTATION-VERTICAL TRUE 0)"
    if name == "resize":
        w = p.get("width", 100)
        h = p.get("height", 100)
        return f"(gimp-layer-scale {d} {w} {h} TRUE)"
    if name == "crop":
        l, t_, r, b = (
            p.get("left", 0),
            p.get("top", 0),
            p.get("right", 0),
            p.get("bottom", 0),
        )
        new_w, new_h = r - l, b - t_
        if new_w > 0 and new_h > 0:
            return (
                f"(gimp-layer-resize {d} {new_w} {new_h} {-l} {-t_})"
                f" (gimp-layer-flatten-image {i})"
            )
        return None

    return None


def _hex_to_rgb(color: str) -> str:
    """'#rrggbb' → 'r g b' (space-separated decimal) for Script-Fu palettes."""
    c = color.lstrip("#")
    if len(c) == 6:
        return f"{int(c[0:2], 16)} {int(c[2:4], 16)} {int(c[4:6], 16)}"
    return "255 255 255"


_NAMED_COLORS = {
    "white": "255 255 255",
    "black": "0 0 0",
    "red": "255 0 0",
    "green": "0 255 0",
    "blue": "0 0 255",
}
