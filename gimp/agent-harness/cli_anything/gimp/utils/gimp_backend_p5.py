# ruff: noqa: F403, F405, E501
from .gimp_backend_base import *  # noqa: F403

# fmt: off
from .gimp_backend_p1 import _script_fu_escape  # noqa: E402,E501
from .gimp_backend_p3 import GIMP_BLEND_MODES  # noqa: E402,E501
from .gimp_backend_p4 import _NAMED_COLORS, _filter_to_script_fu, _hex_to_rgb  # noqa: E402,E501
# fmt: on


def _build_layer_script(
    s: List[str],
    layer: Dict[str, Any],
    idx: int,
    canvas_w: int,
    canvas_h: int,
) -> None:
    """Append Script-Fu expressions for a single layer."""
    var = f"l{idx}"
    ltype = layer.get("type", "image")
    opacity = int(layer.get("opacity", 1.0) * 100)
    blend = GIMP_BLEND_MODES.get(layer.get("blend_mode", "normal"), "LAYER-MODE-NORMAL")
    w = layer.get("width", canvas_w)
    h = layer.get("height", canvas_h)

    if ltype == "image" and layer.get("source") and os.path.exists(layer["source"]):
        src = _script_fu_escape(os.path.abspath(layer["source"]).replace("\\", "/"))
        s.append(
            f'(let* (({var} (car (gimp-file-load-layer RUN-NONINTERACTIVE image "{src}"))))'
        )
    elif ltype == "text":
        text = _script_fu_escape(layer.get("text", ""))
        font_size = layer.get("font_size", 24)
        font = _script_fu_escape(layer.get("font", "Sans"))
        s.append(
            f'(let* (({var} (car (gimp-text-fontname image -1 0 0 "{text}" 0 TRUE {font_size} UNIT-PIXEL "{font}"))))'
        )
    else:
        fill = layer.get("fill", "transparent")
        img_type = "RGBA-IMAGE" if fill == "transparent" else "RGB-IMAGE"
        name_safe = _script_fu_escape(layer.get("name", f"Layer {idx}"))
        s.append(
            f'(let* (({var} (car (gimp-layer-new image {w} {h} {img_type} "{name_safe}" {opacity} {blend}))))'
        )
        s.append(f"(gimp-image-insert-layer image {var} 0 -1)")
        if fill != "transparent":
            rgb = _NAMED_COLORS.get(fill, _hex_to_rgb(fill))
            s.append(f"(gimp-palette-set-foreground '({rgb}))")
            s.append(f"(gimp-edit-fill {var} FILL-FOREGROUND)")

    # For file/text layers, insert into image and configure
    if ltype == "image" and layer.get("source") and os.path.exists(layer["source"]):
        s.append(f"(gimp-image-insert-layer image {var} 0 -1)")
    # Text layers are auto-inserted by gimp-text-fontname

    # Offsets
    ox, oy = layer.get("offset_x", 0), layer.get("offset_y", 0)
    if ox or oy:
        s.append(f"(gimp-layer-set-offsets {var} {ox} {oy})")

    # Opacity & blend mode (set explicitly for file/text layers)
    if ltype in ("image", "text"):
        s.append(f"(gimp-layer-set-opacity {var} {opacity})")
        s.append(f"(gimp-layer-set-mode {var} {blend})")

    # Filters
    for filt in layer.get("filters", []):
        sf = _filter_to_script_fu(filt["name"], filt.get("params", {}), "image", var)
        if sf:
            s.append(sf)

    s.append(")")  # close this layer's let*


def _build_export_cmd(
    s: List[str],
    safe_path: str,
    fmt: str,
    preset: str,
    quality: Optional[int],
) -> None:
    """Append the Script-Fu export call."""
    from cli_anything.gimp.core.export import EXPORT_PRESETS

    s.append("(let* ((drawable (car (gimp-image-get-active-drawable image))))")

    if fmt == "JPEG":
        q = (
            quality
            or EXPORT_PRESETS.get(preset, {}).get("params", {}).get("quality", 85)
        ) / 100.0
        s.append(
            f'(file-jpeg-save RUN-NONINTERACTIVE image drawable "{safe_path}" "{safe_path}" {q:.2f} 0.0 0 0 "" 0 1 0 2)'
        )
    elif fmt == "PNG":
        comp = EXPORT_PRESETS.get(preset, {}).get("params", {}).get("compress_level", 6)
        s.append(
            f'(file-png-save RUN-NONINTERACTIVE image drawable "{safe_path}" "{safe_path}" 0 {comp} 1 1 1 1 1)'
        )
    elif fmt == "BMP":
        s.append(
            f'(file-bmp-save RUN-NONINTERACTIVE image drawable "{safe_path}" "{safe_path}" 0)'
        )
    elif fmt == "TIFF":
        s.append(
            f'(file-tiff-save RUN-NONINTERACTIVE image drawable "{safe_path}" "{safe_path}" 1)'
        )
    elif fmt == "GIF":
        s.append(
            f'(gimp-image-convert-indexed image CONVERT-DITHER-TYPE-NO-DITHER CONVERT-PALETTE-TYPE-GENERATE 256 FALSE FALSE "")'
        )
        s.append(f"(set! drawable (car (gimp-image-get-active-drawable image)))")
        s.append(
            f'(file-gif-save RUN-NONINTERACTIVE image drawable "{safe_path}" "{safe_path}" 0 0 0 0)'
        )
    else:
        s.append(
            f'(gimp-file-overwrite RUN-NONINTERACTIVE image drawable "{safe_path}" "{safe_path}")'
        )

    s.append(")")  # close export let*


def _human_size(nbytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if nbytes < 1024:
            return f"{nbytes:.1f} {unit}"
        nbytes /= 1024
    return f"{nbytes:.1f} TB"
