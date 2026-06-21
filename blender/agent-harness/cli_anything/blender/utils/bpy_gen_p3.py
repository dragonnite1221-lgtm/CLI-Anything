# ruff: noqa: F403, F405, E501
from .bpy_gen_base import *  # noqa: F403

# fmt: off
from .bpy_gen_p1 import _safe_var_name  # noqa: E402,E501
from .bpy_gen_p2 import _gen_modifier  # noqa: E402,E501
# fmt: on


def _gen_objects(project: Dict[str, Any]) -> List[str]:
    """Generate object creation code."""
    objects = project.get("objects", [])
    if not objects:
        return [
            "# ── Objects ─────────────────────────────────────────────────",
            "# (none)",
        ]

    lines = ["# ── Objects ─────────────────────────────────────────────────"]
    materials = project.get("materials", [])
    mat_id_to_name = {m["id"]: m["name"] for m in materials}

    for i, obj in enumerate(objects):
        mesh_type = obj.get("mesh_type", "cube")
        name = obj.get("name", f"Object_{i}")
        loc = obj.get("location", [0, 0, 0])
        rot = obj.get("rotation", [0, 0, 0])
        scl = obj.get("scale", [1, 1, 1])
        params = obj.get("mesh_params", {})

        lines.append(f"# Object: {name}")

        # Create mesh primitive
        if mesh_type == "cube":
            size = params.get("size", 2.0)
            lines.append(
                f"bpy.ops.mesh.primitive_cube_add(size={size}, location=({loc[0]}, {loc[1]}, {loc[2]}))"
            )
        elif mesh_type == "sphere":
            radius = params.get("radius", 1.0)
            segments = params.get("segments", 32)
            rings = params.get("rings", 16)
            lines.append(
                f"bpy.ops.mesh.primitive_uv_sphere_add(radius={radius}, segments={segments}, ring_count={rings}, location=({loc[0]}, {loc[1]}, {loc[2]}))"
            )
        elif mesh_type == "cylinder":
            radius = params.get("radius", 1.0)
            depth = params.get("depth", 2.0)
            vertices = params.get("vertices", 32)
            lines.append(
                f"bpy.ops.mesh.primitive_cylinder_add(radius={radius}, depth={depth}, vertices={vertices}, location=({loc[0]}, {loc[1]}, {loc[2]}))"
            )
        elif mesh_type == "cone":
            r1 = params.get("radius1", 1.0)
            r2 = params.get("radius2", 0.0)
            depth = params.get("depth", 2.0)
            vertices = params.get("vertices", 32)
            lines.append(
                f"bpy.ops.mesh.primitive_cone_add(radius1={r1}, radius2={r2}, depth={depth}, vertices={vertices}, location=({loc[0]}, {loc[1]}, {loc[2]}))"
            )
        elif mesh_type == "plane":
            size = params.get("size", 2.0)
            lines.append(
                f"bpy.ops.mesh.primitive_plane_add(size={size}, location=({loc[0]}, {loc[1]}, {loc[2]}))"
            )
        elif mesh_type == "torus":
            major = params.get("major_radius", 1.0)
            minor = params.get("minor_radius", 0.25)
            maj_seg = params.get("major_segments", 48)
            min_seg = params.get("minor_segments", 12)
            lines.append(
                f"bpy.ops.mesh.primitive_torus_add(major_radius={major}, minor_radius={minor}, major_segments={maj_seg}, minor_segments={min_seg}, location=({loc[0]}, {loc[1]}, {loc[2]}))"
            )
        elif mesh_type == "monkey":
            lines.append(
                f"bpy.ops.mesh.primitive_monkey_add(location=({loc[0]}, {loc[1]}, {loc[2]}))"
            )
        elif mesh_type == "empty":
            lines.append(
                f"bpy.ops.object.empty_add(location=({loc[0]}, {loc[1]}, {loc[2]}))"
            )
        else:
            lines.append(f"# Unknown mesh type: {mesh_type}")
            continue

        lines.append("obj = bpy.context.active_object")
        lines.append(f"obj.name = '{name}'")
        lines.append(
            f"obj.rotation_euler = (math.radians({rot[0]}), math.radians({rot[1]}), math.radians({rot[2]}))"
        )
        lines.append(f"obj.scale = ({scl[0]}, {scl[1]}, {scl[2]})")

        if not obj.get("visible", True):
            lines.append("obj.hide_render = True")
            lines.append("obj.hide_viewport = True")

        # Assign material
        mat_id = obj.get("material")
        if mat_id is not None and mat_id in mat_id_to_name:
            mat_name = mat_id_to_name[mat_id]
            var_name = _safe_var_name(mat_name)
            lines.append(f"if 'mat_{var_name}' in dir():")
            lines.append(f"    obj.data.materials.append(mat_{var_name})")

        # Add modifiers
        for mod in obj.get("modifiers", []):
            lines.extend(_gen_modifier(mod))

        lines.append("")

    return lines
