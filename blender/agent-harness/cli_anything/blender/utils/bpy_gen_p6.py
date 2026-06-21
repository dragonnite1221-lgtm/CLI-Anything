# ruff: noqa: F403, F405, E501
from .bpy_gen_base import *  # noqa: F403


def _gen_render_output(
    project: Dict[str, Any],
    output_path: str,
    frame: Optional[int],
    animation: bool,
) -> List[str]:
    """Generate render execution code."""
    render = project.get("render", {})
    scene = project.get("scene", {})
    fmt = render.get("output_format", "PNG")

    # Map format names to Blender format strings
    format_map = {
        "PNG": "PNG",
        "JPEG": "JPEG",
        "BMP": "BMP",
        "TIFF": "TIFF",
        "OPEN_EXR": "OPEN_EXR",
        "HDR": "HDR",
        "FFMPEG": "FFMPEG",
    }
    bpy_format = format_map.get(fmt, "PNG")

    lines = [
        "# ── Render Output ───────────────────────────────────────────",
        f"scene.render.image_settings.file_format = '{bpy_format}'",
        f"scene.render.filepath = r'{output_path}'",
    ]

    if animation:
        lines.extend(
            [
                "",
                "# Render animation",
                "bpy.ops.render.render(animation=True)",
            ]
        )
    else:
        target_frame = frame or scene.get("frame_current", 1)
        lines.extend(
            [
                f"scene.frame_set({target_frame})",
                "",
                "# Render single frame",
                "bpy.ops.render.render(write_still=True)",
            ]
        )

    lines.extend(
        [
            "",
            f"print('Render complete: {output_path}')",
        ]
    )

    return lines
