# ruff: noqa: F403, F405, E501
from .bpy_gen_base import *  # noqa: F403


def _gen_object_parenting(project: Dict[str, Any]) -> List[str]:
    """Generate object parenting relationships after all objects exist."""
    objects = project.get("objects", [])
    if not objects:
        return [
            "# ── Object Parenting ───────────────────────────────────────",
            "# (none)",
        ]

    id_to_name = {
        obj.get("id", index): obj.get("name", f"Object_{index}")
        for index, obj in enumerate(objects)
    }
    parent_pairs = []
    for index, obj in enumerate(objects):
        parent_id = obj.get("parent")
        if parent_id is None:
            continue
        child_name = obj.get("name", f"Object_{index}")
        parent_name = id_to_name.get(parent_id)
        if not parent_name:
            continue
        parent_pairs.append((child_name, parent_name))

    if not parent_pairs:
        return [
            "# ── Object Parenting ───────────────────────────────────────",
            "# (none)",
        ]

    lines = ["# ── Object Parenting ───────────────────────────────────────"]
    for child_name, parent_name in parent_pairs:
        lines.extend(
            [
                f"child_obj = bpy.data.objects.get('{child_name}')",
                f"parent_obj = bpy.data.objects.get('{parent_name}')",
                "if child_obj and parent_obj:",
                "    child_obj.parent = parent_obj",
                "    child_obj.matrix_parent_inverse = parent_obj.matrix_world.inverted()",
                "",
            ]
        )
    return lines


def _gen_cameras(project: Dict[str, Any]) -> List[str]:
    """Generate camera creation code."""
    cameras = project.get("cameras", [])
    if not cameras:
        return [
            "# ── Cameras ─────────────────────────────────────────────────",
            "# (none)",
        ]

    lines = ["# ── Cameras ─────────────────────────────────────────────────"]

    for cam in cameras:
        name = cam.get("name", "Camera")
        loc = cam.get("location", [0, 0, 5])
        rot = cam.get("rotation", [0, 0, 0])
        cam_type = cam.get("type", "PERSP")
        focal = cam.get("focal_length", 50.0)
        sensor = cam.get("sensor_width", 36.0)
        clip_s = cam.get("clip_start", 0.1)
        clip_e = cam.get("clip_end", 1000.0)

        lines.extend(
            [
                f"cam_data = bpy.data.cameras.new(name='{name}')",
                f"cam_data.type = '{cam_type}'",
                f"cam_data.lens = {focal}",
                f"cam_data.sensor_width = {sensor}",
                f"cam_data.clip_start = {clip_s}",
                f"cam_data.clip_end = {clip_e}",
            ]
        )

        if cam.get("dof_enabled"):
            lines.extend(
                [
                    "cam_data.dof.use_dof = True",
                    f"cam_data.dof.focus_distance = {cam.get('dof_focus_distance', 10.0)}",
                    f"cam_data.dof.aperture_fstop = {cam.get('dof_aperture', 2.8)}",
                ]
            )

        lines.extend(
            [
                f"cam_obj = bpy.data.objects.new('{name}', cam_data)",
                "bpy.context.collection.objects.link(cam_obj)",
                f"cam_obj.location = ({loc[0]}, {loc[1]}, {loc[2]})",
                f"cam_obj.rotation_euler = (math.radians({rot[0]}), math.radians({rot[1]}), math.radians({rot[2]}))",
            ]
        )

        if cam.get("is_active", False):
            lines.append("scene.camera = cam_obj")

        lines.append("")

    return lines
