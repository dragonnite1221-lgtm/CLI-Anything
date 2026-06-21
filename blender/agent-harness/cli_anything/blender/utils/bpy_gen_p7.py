# ruff: noqa: F403, F405, E501
from .bpy_gen_base import *  # noqa: F403

# fmt: off
from .bpy_gen_p1 import _gen_render_settings, _gen_scene_settings, _gen_world_settings  # noqa: E402,E501
from .bpy_gen_p2 import _gen_materials  # noqa: E402,E501
from .bpy_gen_p3 import _gen_objects  # noqa: E402,E501
from .bpy_gen_p4 import _gen_cameras, _gen_object_parenting  # noqa: E402,E501
from .bpy_gen_p5 import _gen_keyframes, _gen_lights  # noqa: E402,E501
from .bpy_gen_p6 import _gen_render_output  # noqa: E402,E501
# fmt: on


def generate_full_script(
    project: Dict[str, Any],
    output_path: str,
    frame: Optional[int] = None,
    animation: bool = False,
) -> str:
    """Generate a complete bpy script from scene JSON.

    Args:
        project: The scene dict
        output_path: Render output path
        frame: Specific frame to render
        animation: Render full animation

    Returns:
        Complete Python script string
    """
    lines = []
    lines.append("#!/usr/bin/env python3")
    lines.append('"""Auto-generated Blender Python script from blender-cli."""')
    lines.append("")
    lines.append("import bpy")
    lines.append("import math")
    lines.append("import os")
    lines.append("")
    lines.append("# ── Clear Default Scene ──────────────────────────────────────")
    lines.append("bpy.ops.object.select_all(action='SELECT')")
    lines.append("bpy.ops.object.delete(use_global=False)")
    lines.append("")

    # Scene settings
    lines.extend(_gen_scene_settings(project))
    lines.append("")

    # Render settings
    lines.extend(_gen_render_settings(project))
    lines.append("")

    # World settings
    lines.extend(_gen_world_settings(project))
    lines.append("")

    # Materials
    lines.extend(_gen_materials(project))
    lines.append("")

    # Objects
    lines.extend(_gen_objects(project))
    lines.append("")

    # Object parenting
    lines.extend(_gen_object_parenting(project))
    lines.append("")

    # Cameras
    lines.extend(_gen_cameras(project))
    lines.append("")

    # Lights
    lines.extend(_gen_lights(project))
    lines.append("")

    # Keyframes
    lines.extend(_gen_keyframes(project))
    lines.append("")

    # Render output
    lines.extend(_gen_render_output(project, output_path, frame, animation))

    return "\n".join(lines)
