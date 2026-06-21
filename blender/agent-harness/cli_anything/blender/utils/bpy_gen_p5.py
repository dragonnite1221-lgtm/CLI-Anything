# ruff: noqa: F403, F405, E501
from .bpy_gen_base import *  # noqa: F403


def _gen_lights(project: Dict[str, Any]) -> List[str]:
    """Generate light creation code."""
    lights = project.get("lights", [])
    if not lights:
        return [
            "# ── Lights ──────────────────────────────────────────────────",
            "# (none)",
        ]

    lines = ["# ── Lights ──────────────────────────────────────────────────"]

    for light in lights:
        name = light.get("name", "Light")
        light_type = light.get("type", "POINT")
        loc = light.get("location", [0, 0, 3])
        rot = light.get("rotation", [0, 0, 0])
        color = light.get("color", [1, 1, 1])
        power = light.get("power", 1000)

        lines.extend(
            [
                f"light_data = bpy.data.lights.new(name='{name}', type='{light_type}')",
                f"light_data.energy = {power}",
                f"light_data.color = ({color[0]}, {color[1]}, {color[2]})",
            ]
        )

        if light_type == "POINT":
            lines.append(f"light_data.shadow_soft_size = {light.get('radius', 0.25)}")
        elif light_type == "SUN":
            lines.append(f"light_data.angle = {light.get('angle', 0.00918)}")
        elif light_type == "SPOT":
            lines.append(f"light_data.shadow_soft_size = {light.get('radius', 0.25)}")
            lines.append(f"light_data.spot_size = {light.get('spot_size', 0.785398)}")
            lines.append(f"light_data.spot_blend = {light.get('spot_blend', 0.15)}")
        elif light_type == "AREA":
            lines.append(f"light_data.size = {light.get('size', 1.0)}")
            lines.append(f"light_data.size_y = {light.get('size_y', 1.0)}")
            lines.append(f"light_data.shape = '{light.get('shape', 'RECTANGLE')}'")

        lines.extend(
            [
                f"light_obj = bpy.data.objects.new('{name}', light_data)",
                "bpy.context.collection.objects.link(light_obj)",
                f"light_obj.location = ({loc[0]}, {loc[1]}, {loc[2]})",
                f"light_obj.rotation_euler = (math.radians({rot[0]}), math.radians({rot[1]}), math.radians({rot[2]}))",
                "",
            ]
        )

    return lines


def _gen_keyframes(project: Dict[str, Any]) -> List[str]:
    """Generate keyframe animation code."""
    objects = project.get("objects", [])
    has_keyframes = any(obj.get("keyframes") for obj in objects)

    if not has_keyframes:
        return [
            "# ── Keyframes ───────────────────────────────────────────────",
            "# (none)",
        ]

    lines = ["# ── Keyframes ───────────────────────────────────────────────"]

    for obj in objects:
        keyframes = obj.get("keyframes", [])
        if not keyframes:
            continue

        name = obj.get("name", "Object")
        lines.append(f"obj = bpy.data.objects.get('{name}')")
        lines.append("if obj:")

        for kf in keyframes:
            frame = kf["frame"]
            prop = kf["property"]
            value = kf["value"]
            interp = kf.get("interpolation", "BEZIER")

            if prop == "location":
                lines.append(f"    obj.location = ({value[0]}, {value[1]}, {value[2]})")
                lines.append(
                    f"    obj.keyframe_insert(data_path='location', frame={frame})"
                )
            elif prop == "rotation":
                lines.append(
                    f"    obj.rotation_euler = (math.radians({value[0]}), math.radians({value[1]}), math.radians({value[2]}))"
                )
                lines.append(
                    f"    obj.keyframe_insert(data_path='rotation_euler', frame={frame})"
                )
            elif prop == "scale":
                lines.append(f"    obj.scale = ({value[0]}, {value[1]}, {value[2]})")
                lines.append(
                    f"    obj.keyframe_insert(data_path='scale', frame={frame})"
                )
            elif prop == "visible":
                hide_val = "False" if value else "True"
                lines.append(f"    obj.hide_render = {hide_val}")
                lines.append(
                    f"    obj.keyframe_insert(data_path='hide_render', frame={frame})"
                )

        lines.append("")

    return lines
