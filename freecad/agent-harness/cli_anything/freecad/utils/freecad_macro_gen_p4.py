# ruff: noqa: F403, F405, E501
from .freecad_macro_gen_base import *  # noqa: F403
# fmt: off
from .freecad_macro_gen_p1 import _safe_name  # noqa: E402,E501
from .freecad_macro_gen_p2 import _render_spec_for_part  # noqa: E402,E501
# fmt: on


def _gen_placements(project: dict) -> List[str]:
    """Generate placement (position and rotation) commands for parts."""
    lines: List[str] = []
    parts = project.get("parts", [])

    for part in parts:
        name = _safe_name(part.get("name", ""))
        render_spec = _render_spec_for_part(project, part)
        if render_spec is None:
            lines.append(f"# WARNING: Skipping placement for unsupported part '{name}'")
            lines.append("")
            continue
        placement = render_spec.get("placement", {})

        if not placement:
            continue

        position = placement.get("position", {})
        rotation = placement.get("rotation", {})

        # Support both list [x, y, z] and dict {"x": ..., "y": ..., "z": ...}
        if isinstance(position, (list, tuple)):
            x = position[0] if len(position) > 0 else 0.0
            y = position[1] if len(position) > 1 else 0.0
            z = position[2] if len(position) > 2 else 0.0
        else:
            x = position.get("x", 0.0)
            y = position.get("y", 0.0)
            z = position.get("z", 0.0)

        # Rotation: support list [rx, ry, rz] (Euler) or dict formats
        if isinstance(rotation, (list, tuple)):
            rx = rotation[0] if len(rotation) > 0 else 0.0
            ry = rotation[1] if len(rotation) > 1 else 0.0
            rz = rotation[2] if len(rotation) > 2 else 0.0
            if rx != 0.0 or ry != 0.0 or rz != 0.0:
                lines.append(
                    f"obj_{name}.Placement = FreeCAD.Placement("
                    f"FreeCAD.Vector({x}, {y}, {z}), "
                    f"FreeCAD.Rotation({rz}, {ry}, {rx}))"
                )
            else:
                lines.append(
                    f"obj_{name}.Placement.Base = FreeCAD.Vector({x}, {y}, {z})"
                )
        elif "axis" in rotation and "angle" in rotation:
            axis = rotation["axis"]
            ax = axis.get("x", 0.0)
            ay = axis.get("y", 0.0)
            az = axis.get("z", 1.0)
            angle = rotation["angle"]
            lines.append(
                f"obj_{name}.Placement = FreeCAD.Placement("
                f"FreeCAD.Vector({x}, {y}, {z}), "
                f"FreeCAD.Rotation(FreeCAD.Vector({ax}, {ay}, {az}), {angle}))"
            )
        elif any(k in rotation for k in ("yaw", "pitch", "roll")):
            yaw = rotation.get("yaw", 0.0)
            pitch = rotation.get("pitch", 0.0)
            roll = rotation.get("roll", 0.0)
            lines.append(
                f"obj_{name}.Placement = FreeCAD.Placement("
                f"FreeCAD.Vector({x}, {y}, {z}), "
                f"FreeCAD.Rotation({yaw}, {pitch}, {roll}))"
            )
        else:
            # Position only, no rotation
            lines.append(
                f"obj_{name}.Placement.Base = FreeCAD.Vector({x}, {y}, {z})"
            )

        lines.append("")

    return lines
