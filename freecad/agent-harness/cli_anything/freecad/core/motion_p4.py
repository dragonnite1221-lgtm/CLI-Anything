# ruff: noqa: F403, F405, E501
from .motion_base import *  # noqa: F403


def _generate_motion_macro(
    project: Dict[str, Any],
    *,
    frames: List[Dict[str, Any]],
    camera: str,
    width: int,
    height: int,
    background: str,
    fit_mode: str,
) -> str:
    if camera not in CAMERA_PRESETS:
        raise ValueError(f"Unknown camera '{camera}'")
    if fit_mode not in FIT_MODES:
        raise ValueError(f"Unknown fit_mode '{fit_mode}'")

    part_object_items = []
    for part in project.get("parts", []):
        render_spec = macro_gen._render_spec_for_part(project, part)
        if render_spec is None:
            continue
        safe_name = macro_gen._safe_name(
            part.get("name", f"Part_{part.get('id', 'unknown')}")
        )
        part_object_items.append(f"    '{int(part['id'])}': obj_{safe_name},")

    lines: List[str] = []
    lines.extend(macro_gen._gen_header())
    lines.extend(macro_gen._gen_parts(project))
    lines.extend(macro_gen._gen_boolean_ops(project))
    lines.extend(macro_gen._gen_bodies(project))
    lines.extend(macro_gen._gen_placements(project))
    lines.extend(
        [
            "doc.recompute()",
            "",
            "try:",
            "    import FreeCADGui",
            "except ImportError as exc:",
            "    raise RuntimeError('FreeCADGui is required for motion rendering') from exc",
            "",
            "try:",
            "    FreeCADGui.showMainWindow()",
            "except Exception:",
            "    pass",
            "",
            "gui_doc = FreeCADGui.getDocument(doc.Name)",
            "if gui_doc is None:",
            "    raise RuntimeError(f'Could not acquire GUI document for {doc.Name}')",
            "FreeCADGui.ActiveDocument = gui_doc",
            "view = getattr(FreeCADGui.ActiveDocument, 'ActiveView', None)",
            "if view is None:",
            "    view = FreeCADGui.ActiveDocument.activeView()",
            "if view is None:",
            "    raise RuntimeError('FreeCAD active view is not available')",
            "try:",
            "    view.setAnimationEnabled(False)",
            "except Exception:",
            "    pass",
            "",
            "part_objects = {",
            *part_object_items,
            "}",
            f"frames = {repr(frames)}",
            "",
            f"getattr(view, '{CAMERA_PRESETS[camera]['method']}')()",
            "try:",
            "    view.fitAll()",
            "except Exception:",
            "    pass",
            "try:",
            "    FreeCADGui.updateGui()",
            "except Exception:",
            "    pass",
            "",
            "for frame in frames:",
            "    for part_id, placement in frame['placements'].items():",
            "        obj = part_objects.get(str(part_id))",
            "        if obj is None:",
            "            continue",
            "        pos = placement['position']",
            "        rot = placement['rotation']",
            "        obj.Placement = FreeCAD.Placement(",
            "            FreeCAD.Vector(float(pos[0]), float(pos[1]), float(pos[2])),",
            "            FreeCAD.Rotation(float(rot[2]), float(rot[1]), float(rot[0])),",
            "        )",
            "    doc.recompute()",
            "    try:",
            "        FreeCADGui.updateGui()",
            "    except Exception:",
            "        pass",
        ]
    )
    if fit_mode == "per-frame":
        lines.extend(
            [
                "    try:",
                "        view.fitAll()",
                "    except Exception:",
                "        pass",
            ]
        )
    lines.extend(
        [
            f"    view.saveImage(frame['path'], {int(width)}, {int(height)}, '{background}')",
            "",
            "try:",
            "    FreeCAD.closeDocument(doc.Name)",
            "except Exception:",
            "    pass",
            "import os as _motion_os",
            "_motion_os._exit(0)",
            "",
        ]
    )
    return "\n".join(lines)
