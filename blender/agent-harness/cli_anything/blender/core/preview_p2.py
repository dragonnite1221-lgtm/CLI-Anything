# ruff: noqa: F403, F405, E402, F401, E501
from .preview_base import *
from .preview_p1 import (
    _merge_nested_dict,
    _now_iso,
    _read_json,
    _with_live_refs,
    _write_json,
)

from . import preview_base as _coupbase  # noqa: E402


def _load_existing_live_session(session_dir: Path) -> Dict[str, Any]:
    session_path = session_dir / "session.json"
    if session_path.is_file():
        return _read_json(session_path)
    return {}


def _write_live_session_updates(
    session_dir: Path, updates: Dict[str, Any]
) -> Dict[str, Any]:
    payload = _load_existing_live_session(session_dir)
    if not payload:
        raise FileNotFoundError(f"Live preview session not found: {session_dir}")
    _merge_nested_dict(payload, updates)
    payload["updated_at"] = updates.get(
        "updated_at", _coupbase._COUP_GLOBALS["_now_iso"]()
    )
    _write_json(session_dir / "session.json", payload)
    return _with_live_refs(session_dir, payload)


def _update_current_symlink(session_dir: Path, bundle_dir: str) -> Path:
    current_link = session_dir / "current"
    if current_link.is_symlink() or current_link.exists():
        if current_link.is_dir() and (not current_link.is_symlink()):
            raise RuntimeError(
                f"Live preview current path is unexpectedly a directory: {current_link}"
            )
        current_link.unlink()
    target = os.path.relpath(Path(bundle_dir).resolve(), session_dir)
    os.symlink(target, current_link, target_is_directory=True)
    return current_link


def _history_item(bundle_manifest: Dict[str, Any]) -> Dict[str, Any]:
    return build_live_history_item(bundle_manifest)


def _ensure_preview_rig(project: Dict[str, Any]) -> List[str]:
    warnings: List[str] = []
    cameras = project.setdefault("cameras", [])
    if not cameras:
        add_camera(
            project,
            name="PreviewCamera",
            location=[6.5, -6.5, 4.75],
            rotation=[63.0, 0.0, 46.0],
            focal_length=45.0,
            set_active=True,
        )
        warnings.append("No camera found; injected PreviewCamera for bundle capture.")
    elif not any((camera.get("is_active") for camera in cameras)):
        cameras[0]["is_active"] = True
        warnings.append(
            f"No active camera set; using {cameras[0]['name']} as the preview camera."
        )
    lights = project.setdefault("lights", [])
    if not lights:
        add_light(
            project,
            light_type="SUN",
            name="PreviewSun",
            rotation=[42.0, 0.0, 32.0],
            power=2.2,
        )
        warnings.append("No light found; injected PreviewSun for preview legibility.")
    return warnings


def _render_image(
    project: Dict[str, Any],
    output_path: str,
    *,
    preset: str,
    frame: int,
    timeout: int,
    resolution_percentage: Optional[int] = None,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    render_project = copy.deepcopy(project)
    kwargs: Dict[str, Any] = {
        "preset": preset,
        "output_format": "PNG",
        "film_transparent": False,
    }
    if resolution_percentage is not None:
        kwargs["resolution_percentage"] = resolution_percentage
    render_mod.set_render_settings(render_project, **kwargs)
    script = render_mod.generate_bpy_script(
        render_project, output_path, frame=frame, animation=False
    )
    backend_result = blender_backend.render_scene_headless(
        script, output_path, timeout=timeout
    )
    settings = render_mod.get_render_settings(render_project)
    return (backend_result, settings)
