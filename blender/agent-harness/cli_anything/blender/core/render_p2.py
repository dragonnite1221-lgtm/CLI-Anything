# ruff: noqa: F403, F405, E501
from .render_base import *  # noqa: F403

# fmt: off
from .render_p1 import generate_bpy_script  # noqa: E402,E501
# fmt: on


def render_scene(
    project: Dict[str, Any],
    output_path: str,
    frame: Optional[int] = None,
    animation: bool = False,
    overwrite: bool = False,
) -> Dict[str, Any]:
    """Render the scene by generating a bpy script.

    Since we cannot call Blender directly in all environments, this generates
    a Python script that can be run with `blender --background --python script.py`.

    Args:
        project: The scene dict
        output_path: Output file or directory path
        frame: Specific frame to render (None = current frame)
        animation: If True, render the full animation range
        overwrite: Allow overwriting existing files

    Returns:
        Dict with render info and script path
    """
    if os.path.exists(output_path) and not overwrite and not animation:
        raise FileExistsError(f"Output file exists: {output_path}. Use --overwrite.")

    render_settings = project.get("render", {})
    scene_settings = project.get("scene", {})

    # Determine output directory for the script
    script_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(script_dir, exist_ok=True)

    script_path = os.path.join(script_dir, "_render_script.py")
    # Ensure output_path is absolute before passing it to the script generator
    # as Blender's background process may have a different CWD.
    abs_output_path = os.path.abspath(output_path)
    script_content = generate_bpy_script(
        project, abs_output_path, frame=frame, animation=animation
    )

    with open(script_path, "w") as f:
        f.write(script_content)

    result = {
        "script_path": os.path.abspath(script_path),
        "output_path": os.path.abspath(output_path),
        "engine": render_settings.get("engine", "CYCLES"),
        "resolution": f"{render_settings.get('resolution_x', 1920)}x{render_settings.get('resolution_y', 1080)}",
        "samples": render_settings.get("samples", 128),
        "format": render_settings.get("output_format", "PNG"),
        "animation": animation,
        "command": f"blender --background --python {os.path.abspath(script_path)}",
    }

    if animation:
        result["frame_range"] = (
            f"{scene_settings.get('frame_start', 1)}-{scene_settings.get('frame_end', 250)}"
        )
    else:
        result["frame"] = frame or scene_settings.get("frame_current", 1)

    return result
