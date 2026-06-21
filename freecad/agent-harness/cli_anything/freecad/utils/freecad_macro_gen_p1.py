# ruff: noqa: F403, F405, E501
from .freecad_macro_gen_base import *  # noqa: F403


def _safe_name(name: str) -> str:
    """Convert a user-supplied name into a valid FreeCAD object label.

    Replaces non-alphanumeric characters with underscores and ensures the
    name does not start with a digit.
    """
    safe = re.sub(r"[^A-Za-z0-9_]", "_", name)
    if safe and safe[0].isdigit():
        safe = f"_{safe}"
    return safe or "Unnamed"
def _gen_header() -> List[str]:
    """Generate import statements and document creation."""
    return [
        "# Auto-generated FreeCAD macro by CLI-Anything FreeCAD harness",
        "import sys",
        "import os",
        "import FreeCAD",
        "import Part",
        "",
        "doc = FreeCAD.newDocument('ExportDoc')",
        "",
    ]
_RENDERABLE_PRIMITIVES = {"box", "cylinder", "sphere", "cone", "torus"}
def _emit_primitive(lines: List[str], part_type: str, name: str, props: Dict[str, Any]) -> bool:
    """Append FreeCAD object creation lines for a supported primitive."""
    if part_type == "box":
        length = props.get("length", props.get("Length", 10.0))
        width = props.get("width", props.get("Width", 10.0))
        height = props.get("height", props.get("Height", 10.0))
        lines.append(f"obj_{name} = doc.addObject('Part::Box', '{name}')")
        lines.append(f"obj_{name}.Length = {length}")
        lines.append(f"obj_{name}.Width = {width}")
        lines.append(f"obj_{name}.Height = {height}")
        return True

    if part_type == "cylinder":
        radius = props.get("radius", props.get("Radius", 5.0))
        height = props.get("height", props.get("Height", 10.0))
        lines.append(f"obj_{name} = doc.addObject('Part::Cylinder', '{name}')")
        lines.append(f"obj_{name}.Radius = {radius}")
        lines.append(f"obj_{name}.Height = {height}")
        return True

    if part_type == "sphere":
        radius = props.get("radius", props.get("Radius", 5.0))
        lines.append(f"obj_{name} = doc.addObject('Part::Sphere', '{name}')")
        lines.append(f"obj_{name}.Radius = {radius}")
        return True

    if part_type == "cone":
        radius1 = props.get("radius1", props.get("Radius1", 5.0))
        radius2 = props.get("radius2", props.get("Radius2", 0.0))
        height = props.get("height", props.get("Height", 10.0))
        lines.append(f"obj_{name} = doc.addObject('Part::Cone', '{name}')")
        lines.append(f"obj_{name}.Radius1 = {radius1}")
        lines.append(f"obj_{name}.Radius2 = {radius2}")
        lines.append(f"obj_{name}.Height = {height}")
        return True

    if part_type == "torus":
        radius1 = props.get("radius1", props.get("Radius1", 10.0))
        radius2 = props.get("radius2", props.get("Radius2", 2.0))
        lines.append(f"obj_{name} = doc.addObject('Part::Torus', '{name}')")
        lines.append(f"obj_{name}.Radius1 = {radius1}")
        lines.append(f"obj_{name}.Radius2 = {radius2}")
        return True

    return False
def _part_by_id(project: dict, part_id: Any) -> Optional[Dict[str, Any]]:
    """Return the part payload matching *part_id*, if present."""
    for part in project.get("parts", []):
        if part.get("id") == part_id:
            return part
    return None
def _mirrored_position(position: Any, plane: str) -> List[float]:
    """Return a mirrored position vector for a simple plane reflection."""
    if isinstance(position, (list, tuple)):
        coords = [float(position[idx]) if len(position) > idx else 0.0 for idx in range(3)]
    else:
        coords = [
            float(position.get("x", 0.0)),
            float(position.get("y", 0.0)),
            float(position.get("z", 0.0)),
        ]
    axis_index = {"YZ": 0, "XZ": 1, "XY": 2}.get(plane.upper())
    if axis_index is not None:
        coords[axis_index] *= -1.0
    return coords
def _mirror_render_spec(project: dict, part: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Resolve a mirrored part into a renderable primitive approximation."""
    params = part.get("params", {})
    original = _part_by_id(project, params.get("original_id"))
    if not original:
        return None
    original_type = str(original.get("type", "")).lower()
    if original_type not in _RENDERABLE_PRIMITIVES:
        return None

    placement = dict(original.get("placement") or {})
    placement["position"] = _mirrored_position(
        placement.get("position") or [0.0, 0.0, 0.0],
        str(params.get("mirror_plane", "XZ")),
    )
    return {
        "type": original_type,
        "params": dict(original.get("params") or {}),
        "placement": placement,
    }
