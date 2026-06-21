# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403

# fmt: off
from .preview_p1 import _load_existing_live_session, _merge_nested_dict, _now_iso, _safe_path, _with_live_refs, _write_json  # noqa: E402,E501
# fmt: on


def _write_live_session_updates(
    session_dir: Path, updates: Dict[str, Any]
) -> Dict[str, Any]:
    payload = _load_existing_live_session(session_dir)
    if not payload:
        raise FileNotFoundError(f"Live preview session not found: {session_dir}")
    _merge_nested_dict(payload, updates)
    payload["updated_at"] = updates.get("updated_at", _now_iso())
    _write_json(session_dir / "session.json", payload)
    return _with_live_refs(session_dir, payload)


def _update_current_symlink(session_dir: Path, bundle_dir: str) -> Path:
    current_link = session_dir / "current"
    if current_link.is_symlink() or current_link.exists():
        if current_link.is_dir() and not current_link.is_symlink():
            raise RuntimeError(
                f"Live preview current path is unexpectedly a directory: {current_link}"
            )
        current_link.unlink()
    target = os.path.relpath(Path(bundle_dir).resolve(), session_dir)
    os.symlink(target, current_link, target_is_directory=True)
    return current_link


def _history_item(bundle_manifest: Dict[str, Any]) -> Dict[str, Any]:
    return build_live_history_item(bundle_manifest)


def _generate_preview_macro(
    project: Dict[str, Any],
    outputs: List[Dict[str, str]],
    *,
    width: int,
    height: int,
    background: str,
) -> str:
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
            "    raise RuntimeError('FreeCADGui is required for preview capture') from exc",
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
            "def _capture(method_name, path):",
            "    getattr(view, method_name)()",
            "    try:",
            "        view.fitAll()",
            "    except Exception:",
            "        pass",
            "    try:",
            "        FreeCADGui.updateGui()",
            "    except Exception:",
            "        pass",
            f"    view.saveImage(path, {width}, {height}, '{background}')",
            "",
        ]
    )
    for output in outputs:
        lines.append(f"_capture('{output['method']}', '{_safe_path(output['path'])}')")
    lines.extend(
        [
            "",
            "try:",
            "    FreeCAD.closeDocument(doc.Name)",
            "except Exception:",
            "    pass",
            "",
            "# FreeCAD AppImage + GUI teardown is unstable in headless CI; exit",
            "# immediately after the images are flushed to disk.",
            "import os as _preview_os",
            "_preview_os._exit(0)",
            "",
        ]
    )
    return "\n".join(lines)
