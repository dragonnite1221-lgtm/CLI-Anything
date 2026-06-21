# ruff: noqa: F403, F405, E501
from .bpy_gen_base import *  # noqa: F403

# fmt: off
from .bpy_gen_p1 import _safe_var_name  # noqa: E402,E501
# fmt: on


def _gen_materials(project: Dict[str, Any]) -> List[str]:
    """Generate material creation code."""
    materials = project.get("materials", [])
    if not materials:
        return [
            "# ── Materials ───────────────────────────────────────────────",
            "# (none)",
        ]

    lines = ["# ── Materials ───────────────────────────────────────────────"]

    for mat in materials:
        name = mat.get("name", "Material")
        color = mat.get("color", [0.8, 0.8, 0.8, 1.0])
        metallic = mat.get("metallic", 0.0)
        roughness = mat.get("roughness", 0.5)
        specular = mat.get("specular", 0.5)
        emission = mat.get("emission_color", [0, 0, 0, 1])
        emission_strength = mat.get("emission_strength", 0.0)
        alpha = mat.get("alpha", 1.0)

        var_name = _safe_var_name(name)
        lines.extend(
            [
                f"mat_{var_name} = bpy.data.materials.new(name='{name}')",
                f"mat_{var_name}.use_nodes = True",
                f"bsdf_{var_name} = mat_{var_name}.node_tree.nodes.get('Principled BSDF')",
                f"if bsdf_{var_name}:",
                f"    bsdf_{var_name}.inputs['Base Color'].default_value = ({color[0]}, {color[1]}, {color[2]}, {color[3]})",
                f"    bsdf_{var_name}.inputs['Metallic'].default_value = {metallic}",
                f"    bsdf_{var_name}.inputs['Roughness'].default_value = {roughness}",
                f"    bsdf_{var_name}.inputs['Specular IOR Level'].default_value = {specular}",
                f"    bsdf_{var_name}.inputs['Alpha'].default_value = {alpha}",
            ]
        )
        if emission_strength > 0:
            lines.extend(
                [
                    f"    bsdf_{var_name}.inputs['Emission Color'].default_value = ({emission[0]}, {emission[1]}, {emission[2]}, {emission[3]})",
                    f"    bsdf_{var_name}.inputs['Emission Strength'].default_value = {emission_strength}",
                ]
            )
        lines.append("")

    return lines


def _gen_modifier(mod: Dict[str, Any]) -> List[str]:
    """Generate modifier code for an object."""
    mod_type = mod.get("type", "")
    bpy_type = mod.get("bpy_type", "")
    mod_name = mod.get("name", mod_type)
    params = mod.get("params", {})

    lines = [
        f"mod = obj.modifiers.new(name='{mod_name}', type='{bpy_type}')",
    ]

    if mod_type == "subdivision_surface":
        lines.append(f"mod.levels = {params.get('levels', 1)}")
        lines.append(f"mod.render_levels = {params.get('render_levels', 2)}")
        if params.get("use_creases"):
            lines.append("mod.use_creases = True")
    elif mod_type == "mirror":
        lines.append(f"mod.use_axis[0] = {params.get('use_axis_x', True)}")
        lines.append(f"mod.use_axis[1] = {params.get('use_axis_y', False)}")
        lines.append(f"mod.use_axis[2] = {params.get('use_axis_z', False)}")
        lines.append(f"mod.use_clip = {params.get('use_clip', True)}")
        lines.append(f"mod.merge_threshold = {params.get('merge_threshold', 0.001)}")
    elif mod_type == "array":
        lines.append(f"mod.count = {params.get('count', 2)}")
        lines.append(
            f"mod.relative_offset_displace[0] = {params.get('relative_offset_x', 1.0)}"
        )
        lines.append(
            f"mod.relative_offset_displace[1] = {params.get('relative_offset_y', 0.0)}"
        )
        lines.append(
            f"mod.relative_offset_displace[2] = {params.get('relative_offset_z', 0.0)}"
        )
    elif mod_type == "bevel":
        lines.append(f"mod.width = {params.get('width', 0.1)}")
        lines.append(f"mod.segments = {params.get('segments', 1)}")
        limit = params.get("limit_method", "NONE")
        lines.append(f"mod.limit_method = '{limit}'")
        if limit == "ANGLE":
            lines.append(f"mod.angle_limit = {params.get('angle_limit', 0.523599)}")
    elif mod_type == "solidify":
        lines.append(f"mod.thickness = {params.get('thickness', 0.01)}")
        lines.append(f"mod.offset = {params.get('offset', -1.0)}")
        lines.append(f"mod.use_even_offset = {params.get('use_even_offset', False)}")
    elif mod_type == "decimate":
        lines.append(f"mod.ratio = {params.get('ratio', 0.5)}")
        lines.append(f"mod.decimate_type = '{params.get('decimate_type', 'COLLAPSE')}'")
    elif mod_type == "boolean":
        op = params.get("operation", "DIFFERENCE")
        lines.append(f"mod.operation = '{op}'")
        operand = params.get("operand_object", "")
        if operand:
            lines.append(f"mod.object = bpy.data.objects.get('{operand}')")
        solver = params.get("solver", "EXACT")
        lines.append(f"mod.solver = '{solver}'")
    elif mod_type == "smooth":
        lines.append(f"mod.factor = {params.get('factor', 0.5)}")
        lines.append(f"mod.iterations = {params.get('iterations', 1)}")
        lines.append(f"mod.use_x = {params.get('use_x', True)}")
        lines.append(f"mod.use_y = {params.get('use_y', True)}")
        lines.append(f"mod.use_z = {params.get('use_z', True)}")

    return lines
