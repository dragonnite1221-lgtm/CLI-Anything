# ruff: noqa: F403, F405, E501
from .gimp_backend_base import *  # noqa: F403

# fmt: off
from .gimp_backend_p1 import _script_fu_escape, batch_script_fu, find_gimp  # noqa: E402,E501
# fmt: on


def apply_filter_and_export(
    input_path: str,
    output_path: str,
    script_fu_filter: str = "",
    timeout: int = 120,
) -> dict:
    """Load an image in GIMP, apply a Script-Fu filter, and export.

    Args:
        input_path: Path to input image
        output_path: Path for output image
        script_fu_filter: Script-Fu commands to apply (uses 'image' and 'drawable' vars)
        timeout: Max seconds
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    abs_input = os.path.abspath(input_path)
    abs_output = os.path.abspath(output_path)
    safe_abs_input = _script_fu_escape(abs_input)
    safe_abs_output = _script_fu_escape(abs_output)
    os.makedirs(os.path.dirname(abs_output), exist_ok=True)

    ext = os.path.splitext(output_path)[1].lower()
    if ext == ".png":
        export_cmd = (
            f"(file-png-save RUN-NONINTERACTIVE image drawable "
            f'"{safe_abs_output}" "{safe_abs_output}" 0 9 1 1 1 1 1)'
        )
    elif ext in (".jpg", ".jpeg"):
        export_cmd = (
            f"(file-jpeg-save RUN-NONINTERACTIVE image drawable "
            f'"{safe_abs_output}" "{safe_abs_output}" 0.85 0.0 0 0 "" 0 1 0 2)'
        )
    else:
        export_cmd = (
            f"(gimp-file-overwrite RUN-NONINTERACTIVE image drawable "
            f'"{safe_abs_output}" "{safe_abs_output}")'
        )

    script = (
        f"(let* ("
        f'(image (car (gimp-file-load RUN-NONINTERACTIVE "{safe_abs_input}" "{safe_abs_input}")))'
        f"(drawable (car (gimp-image-flatten image)))"
        f")"
        f"{script_fu_filter}"
        f"(set! drawable (car (gimp-image-flatten image)))"
        f"{export_cmd}"
        f"(gimp-image-delete image))"
    )

    result = batch_script_fu(script, timeout=timeout)

    if not os.path.exists(abs_output):
        raise RuntimeError(
            f"GIMP filter+export produced no output.\n"
            f"  stderr: {result['stderr'][-500:]}"
        )

    return {
        "output": abs_output,
        "format": ext.lstrip("."),
        "method": "gimp-batch",
        "file_size": os.path.getsize(abs_output),
    }


def is_available() -> bool:
    """Return True if GIMP is installed and reachable on $PATH."""
    try:
        find_gimp()
        return True
    except RuntimeError:
        return False


GIMP_BLEND_MODES: Dict[str, str] = {
    "normal": "LAYER-MODE-NORMAL",
    "multiply": "LAYER-MODE-MULTIPLY",
    "screen": "LAYER-MODE-SCREEN",
    "overlay": "LAYER-MODE-OVERLAY",
    "soft_light": "LAYER-MODE-SOFTLIGHT",
    "hard_light": "LAYER-MODE-HARDLIGHT",
    "difference": "LAYER-MODE-DIFFERENCE",
    "darken": "LAYER-MODE-DARKEN-ONLY",
    "lighten": "LAYER-MODE-LIGHTEN-ONLY",
    "color_dodge": "LAYER-MODE-DODGE",
    "color_burn": "LAYER-MODE-BURN",
    "addition": "LAYER-MODE-ADDITION",
    "subtract": "LAYER-MODE-SUBTRACT",
    "grain_merge": "LAYER-MODE-GRAIN-MERGE",
    "grain_extract": "LAYER-MODE-GRAIN-EXTRACT",
}
_EXPORT_COMMANDS: Dict[str, str] = {
    "PNG": '(file-png-save RUN-NONINTERACTIVE {img} {drw} "{path}" "{path}" 0 {compress} 1 1 1 1 1)',
    "JPEG": '(file-jpeg-save RUN-NONINTERACTIVE {img} {drw} "{path}" "{path}" {quality} 0.0 0 0 "" 0 1 0 2)',
    "BMP": '(file-bmp-save RUN-NONINTERACTIVE {img} {drw} "{path}" "{path}" 0)',
    "TIFF": '(file-tiff-save RUN-NONINTERACTIVE {img} {drw} "{path}" "{path}" 1)',
    "GIF": '(file-gif-save RUN-NONINTERACTIVE {img} {drw} "{path}" "{path}" 0 0 0 0)',
}
