# ruff: noqa: F403, F405, E501
from .gimp_backend_base import *  # noqa: F403

# fmt: off
from .gimp_backend_p1 import _script_fu_escape, batch_script_fu, get_version  # noqa: E402,E501
# fmt: on


def create_and_export(
    width: int,
    height: int,
    output_path: str,
    fill_color: str = "white",
    timeout: int = 120,
) -> dict:
    """Create a new image in GIMP and export it."""
    abs_output = os.path.abspath(output_path)
    safe_abs_output = _script_fu_escape(abs_output)
    os.makedirs(os.path.dirname(abs_output), exist_ok=True)

    ext = os.path.splitext(output_path)[1].lower()

    # Build the export command based on format
    if ext == ".png":
        export_cmd = (
            f"(file-png-save RUN-NONINTERACTIVE image layer "
            f'"{safe_abs_output}" "{safe_abs_output}" 0 9 1 1 1 1 1)'
        )
    elif ext in (".jpg", ".jpeg"):
        export_cmd = (
            f"(file-jpeg-save RUN-NONINTERACTIVE image layer "
            f'"{safe_abs_output}" "{safe_abs_output}" 0.85 0.0 0 0 "" 0 1 0 2)'
        )
    elif ext == ".bmp":
        export_cmd = (
            f"(file-bmp-save RUN-NONINTERACTIVE image layer "
            f'"{safe_abs_output}" "{safe_abs_output}" 0)'
        )
    else:
        export_cmd = (
            f"(gimp-file-overwrite RUN-NONINTERACTIVE image layer "
            f'"{safe_abs_output}" "{safe_abs_output}")'
        )

    # Color mapping
    color_map = {
        "white": "255 255 255",
        "black": "0 0 0",
        "red": "255 0 0",
        "green": "0 255 0",
        "blue": "0 0 255",
    }
    rgb = color_map.get(fill_color, "255 255 255")

    # Build Script-Fu — use plain strings, subprocess handles quoting
    script = (
        f"(let* ("
        f"(image (car (gimp-image-new {width} {height} RGB)))"
        f"(layer (car (gimp-layer-new image {width} {height} "
        f'RGB-IMAGE "BG" 100 LAYER-MODE-NORMAL)))'
        f")"
        f"(gimp-image-insert-layer image layer 0 -1)"
        f"(gimp-image-set-active-layer image layer)"
        f"(gimp-palette-set-foreground '({rgb}))"
        f"(gimp-edit-fill layer FILL-FOREGROUND)"
        f"{export_cmd}"
        f"(gimp-image-delete image))"
    )

    result = batch_script_fu(script, timeout=timeout)

    if not os.path.exists(abs_output):
        raise RuntimeError(
            f"GIMP export produced no output file.\n"
            f"  Expected: {abs_output}\n"
            f"  stderr: {result['stderr'][-500:]}\n"
            f"  stdout: {result['stdout'][-500:]}"
        )

    return {
        "output": abs_output,
        "format": ext.lstrip("."),
        "method": "gimp-batch",
        "gimp_version": get_version(),
        "file_size": os.path.getsize(abs_output),
    }
