# ruff: noqa: F403, F405, E501
from .freecad_macro_gen_base import *  # noqa: F403
# fmt: off
from .freecad_macro_gen_p1 import _gen_header  # noqa: E402,E501
from .freecad_macro_gen_p2 import _gen_boolean_ops, _gen_parts  # noqa: E402,E501
from .freecad_macro_gen_p3 import _gen_bodies  # noqa: E402,E501
from .freecad_macro_gen_p4 import _gen_placements  # noqa: E402,E501
# fmt: on


def _gen_export(
    project: dict,
    output_path: str,
    export_format: str,
) -> List[str]:
    """Generate export commands for the specified format.

    Supported formats:
      - ``step`` / ``iges``: via ``Part.export()``
      - ``stl``: via ``Mesh.export()``
      - ``obj``: via ``Mesh.export()``
      - ``brep``: via ``Part.export()``
      - ``fcstd``: via ``doc.saveAs()``
    """
    lines: List[str] = []

    # Escape backslashes for Windows paths in the generated Python script
    safe_path = output_path.replace("\\", "/")

    # Recompute the document before exporting
    lines.append("doc.recompute()")
    lines.append("")

    # Collect all visible shape objects for export
    lines.append("# Collect all shape objects for export")
    lines.append("export_objects = []")
    lines.append("for obj in doc.Objects:")
    lines.append("    if hasattr(obj, 'Shape') and obj.Shape.isValid():")
    lines.append("        export_objects.append(obj)")
    lines.append("")

    fmt = export_format.lower()

    if fmt in ("step", "iges", "brep"):
        lines.append(f"Part.export(export_objects, '{safe_path}')")

    elif fmt in ("stl", "obj"):
        lines.append("import Mesh")
        lines.append(f"Mesh.export(export_objects, '{safe_path}')")

    elif fmt == "fcstd":
        lines.append(f"doc.saveAs('{safe_path}')")

    else:
        # Fallback to Part.export for unknown formats
        lines.append(f"# Unknown format '{fmt}', attempting Part.export")
        lines.append(f"Part.export(export_objects, '{safe_path}')")

    lines.append("")
    lines.append("print('Export complete:', os.path.abspath('{safe_path}'))")
    lines.append("")

    return lines
def generate_macro(
    project: dict,
    output_path: str,
    export_format: str = "step",
) -> str:
    """Generate a complete FreeCAD Python macro script from project state.

    The generated script, when executed by ``FreeCADCmd``, will:
      1. Create a new FreeCAD document.
      2. Add all parts/primitives defined in the project.
      3. Apply boolean operations.
      4. Create PartDesign bodies with features.
      5. Set placements (positions and rotations).
      6. Export to the requested format.

    Parameters
    ----------
    project : dict
        Project JSON state.  Expected top-level keys:

        - ``parts``: list of part definitions (type, name, properties,
          placement).
        - ``boolean_ops``: list of boolean operation definitions.
        - ``bodies``: list of PartDesign body definitions with features.

    output_path : str
        Destination file path for the export.
    export_format : str
        Target format: ``"step"``, ``"iges"``, ``"stl"``, ``"obj"``,
        ``"brep"``, or ``"fcstd"``.

    Returns
    -------
    str
        Complete Python macro script ready for execution by FreeCADCmd.
    """
    sections: List[List[str]] = [
        _gen_header(),
        _gen_parts(project),
        _gen_boolean_ops(project),
        _gen_bodies(project),
        _gen_placements(project),
        _gen_export(project, output_path, export_format),
    ]

    # Flatten all sections and join with newlines
    all_lines: List[str] = []
    for section in sections:
        all_lines.extend(section)

    return "\n".join(all_lines)
