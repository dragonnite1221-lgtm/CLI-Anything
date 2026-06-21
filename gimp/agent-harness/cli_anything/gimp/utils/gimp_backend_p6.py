# ruff: noqa: F403, F405, E501
from .gimp_backend_base import *  # noqa: F403

# fmt: off
from .gimp_backend_p1 import _script_fu_escape, batch_script_fu  # noqa: E402,E501
from .gimp_backend_p4 import _NAMED_COLORS, _hex_to_rgb  # noqa: E402,E501
from .gimp_backend_p5 import _build_export_cmd, _build_layer_script, _human_size  # noqa: E402,E501
# fmt: on


def render_project(
    project: Dict[str, Any],
    output_path: str,
    preset: str = "png",
    overwrite: bool = False,
    quality: Optional[int] = None,
    format_override: Optional[str] = None,
    timeout: int = 300,
) -> Dict[str, Any]:
    """Render a complete GIMP CLI project using GIMP's Script-Fu batch mode.

    Builds a single Script-Fu expression that creates the canvas, inserts all
    visible layers with their blend modes / opacities / filters, flattens the
    image, and exports to the requested format.
    """
    from cli_anything.gimp.core.export import EXPORT_PRESETS

    if os.path.exists(output_path) and not overwrite:
        raise FileExistsError(f"Output file exists: {output_path}. Use --overwrite.")

    abs_output = os.path.abspath(output_path).replace("\\", "/")
    safe_output = _script_fu_escape(abs_output)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    canvas = project["canvas"]
    cw, ch = canvas["width"], canvas["height"]
    bg_color = canvas.get("background", "#ffffff")

    if format_override:
        fmt = format_override.upper()
    elif preset in EXPORT_PRESETS:
        fmt = EXPORT_PRESETS[preset]["format"]
    else:
        raise ValueError(f"Unknown preset: {preset}")

    # --- build Script-Fu ---
    s = []
    s.append(f"(let* ((image (car (gimp-image-new {cw} {ch} RGB))))")

    # Background layer
    if bg_color.lower() != "transparent":
        rgb = _NAMED_COLORS.get(bg_color.lower(), _hex_to_rgb(bg_color))
        s.append(
            f'(let* ((bg (car (gimp-layer-new image {cw} {ch} RGB-IMAGE "Background" 100 LAYER-MODE-NORMAL))))'
        )
        s.append(f"(gimp-image-insert-layer image bg 0 -1)")
        s.append(f"(gimp-palette-set-foreground '({rgb}))")
        s.append(f"(gimp-edit-fill bg FILL-FOREGROUND))")

    # Composite layers bottom → top
    layers = project.get("layers", [])
    for idx, layer in enumerate(reversed(layers)):
        if not layer.get("visible", True):
            continue
        _build_layer_script(s, layer, idx, cw, ch)

    # Flatten
    s.append("(gimp-image-flatten image)")

    # Export
    _build_export_cmd(s, safe_output, fmt, preset, quality)

    # Cleanup
    s.append("(gimp-image-delete image))")  # closes outer let*

    script = " ".join(s)
    result = batch_script_fu(script, timeout=timeout)

    if not os.path.exists(abs_output):
        raise RuntimeError(
            f"GIMP rendering produced no output file.\n"
            f"  Expected: {abs_output}\n"
            f"  stderr: {result['stderr'][-500:]}\n"
            f"  stdout: {result['stdout'][-500:]}"
        )

    file_size = os.path.getsize(abs_output)
    return {
        "output": abs_output,
        "format": fmt,
        "size": f"{cw}x{ch}",
        "file_size": file_size,
        "file_size_human": _human_size(file_size),
        "preset": preset,
        "method": "gimp-batch",
        "layers_rendered": sum(1 for l in layers if l.get("visible", True)),
    }
