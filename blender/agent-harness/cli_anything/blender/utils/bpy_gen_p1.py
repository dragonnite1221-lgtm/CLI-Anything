# ruff: noqa: F403, F405, E501
from .bpy_gen_base import *  # noqa: F403


def _gen_scene_settings(project: Dict[str, Any]) -> List[str]:
    """Generate scene settings code."""
    scene = project.get("scene", {})
    lines = [
        "# ── Scene Settings ──────────────────────────────────────────",
        "scene = bpy.context.scene",
        f"scene.unit_settings.system = '{scene.get('unit_system', 'METRIC').upper()}'",
        f"scene.unit_settings.scale_length = {scene.get('unit_scale', 1.0)}",
        f"scene.frame_start = {scene.get('frame_start', 1)}",
        f"scene.frame_end = {scene.get('frame_end', 250)}",
        f"scene.frame_current = {scene.get('frame_current', 1)}",
        f"scene.render.fps = {scene.get('fps', 24)}",
    ]
    return lines


def _engine_to_bpy(engine: str) -> str:
    """Convert engine name to bpy enum value."""
    mapping = {
        "CYCLES": "CYCLES",
        "EEVEE": "BLENDER_EEVEE",
        "WORKBENCH": "BLENDER_WORKBENCH",
    }
    return mapping.get(engine, "CYCLES")


def _gen_render_settings(project: Dict[str, Any]) -> List[str]:
    """Generate render settings code."""
    render = project.get("render", {})
    engine = render.get("engine", "CYCLES")

    lines = [
        "# ── Render Settings ─────────────────────────────────────────",
        f"scene.render.engine = '{_engine_to_bpy(engine)}'",
        f"scene.render.resolution_x = {render.get('resolution_x', 1920)}",
        f"scene.render.resolution_y = {render.get('resolution_y', 1080)}",
        f"scene.render.resolution_percentage = {render.get('resolution_percentage', 100)}",
        f"scene.render.film_transparent = {render.get('film_transparent', False)}",
    ]

    if engine == "CYCLES":
        lines.append(f"scene.cycles.samples = {render.get('samples', 128)}")
        lines.append(
            f"scene.cycles.use_denoising = {render.get('use_denoising', True)}"
        )
    elif engine == "EEVEE":
        lines.append(f"scene.eevee.taa_render_samples = {render.get('samples', 64)}")

    return lines


def _gen_world_settings(project: Dict[str, Any]) -> List[str]:
    """Generate world/environment settings code."""
    world = project.get("world", {})
    bg = world.get("background_color", [0.05, 0.05, 0.05])

    lines = [
        "# ── World Settings ──────────────────────────────────────────",
        "world = bpy.data.worlds.get('World')",
        "if world is None:",
        "    world = bpy.data.worlds.new('World')",
        "    scene.world = world",
        "world.use_nodes = True",
        "bg_node = world.node_tree.nodes.get('Background')",
        "if bg_node:",
        f"    bg_node.inputs[0].default_value = ({bg[0]}, {bg[1]}, {bg[2]}, 1.0)",
    ]

    if world.get("use_hdri") and world.get("hdri_path"):
        hdri_path = world["hdri_path"]
        strength = world.get("hdri_strength", 1.0)
        lines.extend(
            [
                "",
                "# HDRI environment",
                "env_tex = world.node_tree.nodes.new('ShaderNodeTexEnvironment')",
                f"env_tex.image = bpy.data.images.load(r'{hdri_path}')",
                f"bg_node.inputs[1].default_value = {strength}",
                "world.node_tree.links.new(env_tex.outputs[0], bg_node.inputs[0])",
            ]
        )

    return lines


def _safe_var_name(name: str) -> str:
    """Convert a name to a safe Python variable name."""
    result = name.replace(" ", "_").replace(".", "_").replace("-", "_")
    result = "".join(c for c in result if c.isalnum() or c == "_")
    if result and result[0].isdigit():
        result = "_" + result
    return result or "unnamed"
