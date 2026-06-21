# ruff: noqa: F403, F405, E501
from .freecad_macro_gen_base import *  # noqa: F403
# fmt: off
from .freecad_macro_gen_p1 import _RENDERABLE_PRIMITIVES, _emit_primitive, _mirror_render_spec, _safe_name  # noqa: E402,E501
# fmt: on


def _render_spec_for_part(project: dict, part: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Return the renderable primitive spec for *part*, if supported."""
    part_type = str(part.get("type", "")).lower()
    if part_type in _RENDERABLE_PRIMITIVES:
        return {
            "type": part_type,
            "params": dict(part.get("params") or {}),
            "placement": dict(part.get("placement") or {}),
        }
    if part_type == "mirror":
        return _mirror_render_spec(project, part)
    return None
def _gen_parts(project: dict) -> List[str]:
    """Generate Part primitives (Box, Cylinder, Sphere, Cone, Torus)."""
    lines: List[str] = []
    parts = project.get("parts", [])

    for part in parts:
        part_type = str(part.get("type", "box")).lower()
        name = _safe_name(part.get("name", f"Part_{part_type}"))
        render_spec = _render_spec_for_part(project, part)
        props = render_spec["params"] if render_spec else part.get("params", part.get("properties", {}))

        if render_spec and _emit_primitive(lines, render_spec["type"], name, props):
            pass
        else:
            lines.append(f"# WARNING: Unknown part type '{part_type}' for '{name}'")

        lines.append("")

    return lines
def _gen_boolean_ops(project: dict) -> List[str]:
    """Generate boolean operations (Cut, Fuse, Common)."""
    lines: List[str] = []
    boolean_ops = project.get("boolean_ops", [])

    # Map user-friendly names to FreeCAD object types
    op_type_map = {
        "cut": "Part::Cut",
        "subtract": "Part::Cut",
        "fuse": "Part::Fuse",
        "union": "Part::Fuse",
        "common": "Part::Common",
        "intersect": "Part::Common",
        "intersection": "Part::Common",
    }

    for op in boolean_ops:
        op_type = op.get("type", "fuse").lower()
        name = _safe_name(op.get("name", f"BoolOp_{op_type}"))
        base_name = _safe_name(op.get("base", ""))
        tool_name = _safe_name(op.get("tool", ""))
        fc_type = op_type_map.get(op_type, "Part::Fuse")

        lines.append(f"obj_{name} = doc.addObject('{fc_type}', '{name}')")
        lines.append(f"obj_{name}.Base = doc.getObject('{base_name}')")
        lines.append(f"obj_{name}.Tool = doc.getObject('{tool_name}')")
        lines.append("")

    return lines
def _placement_expr(placement: Optional[Dict[str, Any]]) -> Optional[str]:
    """Return a FreeCAD placement expression for a stored placement payload."""
    if not placement:
        return None
    position = placement.get("position") or [0.0, 0.0, 0.0]
    rotation = placement.get("rotation") or [0.0, 0.0, 0.0]
    x = float(position[0] if len(position) > 0 else 0.0)
    y = float(position[1] if len(position) > 1 else 0.0)
    z = float(position[2] if len(position) > 2 else 0.0)
    rx = float(rotation[0] if len(rotation) > 0 else 0.0)
    ry = float(rotation[1] if len(rotation) > 1 else 0.0)
    rz = float(rotation[2] if len(rotation) > 2 else 0.0)
    return (
        "FreeCAD.Placement("
        f"FreeCAD.Vector({x}, {y}, {z}), "
        f"FreeCAD.Rotation({rz}, {ry}, {rx}))"
    )
def _dominant_axis(direction: Any) -> tuple[str, bool, bool]:
    """Resolve a direction vector to the closest body-origin axis."""
    if not isinstance(direction, (list, tuple)) or len(direction) != 3:
        return ("X", False, False)
    values = [float(component) for component in direction]
    axis_index = max(range(3), key=lambda idx: abs(values[idx]))
    axis_name = "XYZ"[axis_index]
    reversed_axis = values[axis_index] < 0
    off_axis = any(abs(value) > 1e-9 for idx, value in enumerate(values) if idx != axis_index)
    return (axis_name, reversed_axis, off_axis)
def _gen_bodies_header(lines):
    lines.extend(
        [
            "def _body_origin_ref(body_obj, role):",
            "    for origin_obj in body_obj.Origin.OriginFeatures:",
            "        if getattr(origin_obj, 'Role', None) == role:",
            "            return origin_obj",
            "    raise RuntimeError(f'Could not resolve body origin role: {role}')",
            "",
        ]
    )
