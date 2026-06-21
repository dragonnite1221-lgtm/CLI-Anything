# ruff: noqa: F403, F405, E501
from .blender_orbital_relay_drone_demo_base import *  # noqa: F403


REPO_ROOT = Path(__file__).resolve().parents[2]
BLENDER_HARNESS_ROOT = REPO_ROOT / "blender" / "agent-harness"
sys.path.insert(0, str(BLENDER_HARNESS_ROOT))
def _object_index(project: Dict, name: str) -> int:
    for index, obj in enumerate(project.get("objects", [])):
        if obj.get("name") == name:
            return index
    raise KeyError(f"Object not found: {name}")
def _material_index(project: Dict, name: str) -> int:
    for index, material in enumerate(project.get("materials", [])):
        if material.get("name") == name:
            return index
    raise KeyError(f"Material not found: {name}")
def _assign(project: Dict, material_name: str, object_name: str) -> None:
    assign_material(project, _material_index(project, material_name), _object_index(project, object_name))
def _set_parent(project: Dict, child_name: str, parent_name: str) -> None:
    child = project["objects"][_object_index(project, child_name)]
    parent = project["objects"][_object_index(project, parent_name)]
    child["parent"] = parent["id"]
def _render_via_script(project: Dict, output_path: Path, *, frame: int | None = None, animation: bool = False, timeout: int = 900) -> Dict:
    render_job = render_scene(project, str(output_path), frame=frame, animation=animation, overwrite=True)
    backend_result = blender_backend.render_script(render_job["script_path"], timeout=timeout)
    if backend_result["returncode"] != 0:
        raise RuntimeError(
            f"Blender render failed for {output_path} (exit {backend_result['returncode']}):\n"
            f"{backend_result['stderr'][-1000:]}"
        )
    payload = dict(render_job)
    payload["backend"] = backend_result
    return payload
def _encode_video(frames_dir: Path, video_path: Path, fps: int) -> Dict:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg not found on PATH")
    video_path.parent.mkdir(parents=True, exist_ok=True)
    pattern = str(frames_dir / "frame_%04d.png")
    command = [
        ffmpeg,
        "-y",
        "-framerate",
        str(fps),
        "-i",
        pattern,
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-crf",
        "18",
        str(video_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg encoding failed:\n{result.stderr[-1200:]}")
    return {
        "command": command,
        "video_path": str(video_path),
        "bytes": video_path.stat().st_size if video_path.exists() else 0,
    }
def _copy_motion_stills(frames: List[Path], output_dir: Path) -> Dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    picks = {
        "start": frames[0],
        "mid": frames[len(frames) // 2],
        "final": frames[-1],
    }
    exported: Dict[str, str] = {}
    for label, source in picks.items():
        target = output_dir / f"{label}.png"
        shutil.copy2(source, target)
        exported[label] = str(target)
    return exported
def _render_live_html(session_dir: Path, output_path: Path) -> str | None:
    hub = shutil.which("cli-hub")
    if not hub:
        return None
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [hub, "previews", "html", str(session_dir), "-o", str(output_path)]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"cli-hub previews html failed:\n{result.stderr[-1200:]}")
    return str(output_path)
def _add_materials(project: Dict) -> None:
    create_material(project, name="DeckGraphite", color=[0.18, 0.2, 0.24, 1.0], metallic=0.12, roughness=0.74)
    create_material(project, name="DeckStripe", color=[0.9, 0.52, 0.14, 1.0], metallic=0.05, roughness=0.46)
    create_material(project, name="HullWhite", color=[0.88, 0.9, 0.93, 1.0], metallic=0.18, roughness=0.2)
    create_material(project, name="SignalOrange", color=[0.94, 0.44, 0.12, 1.0], metallic=0.12, roughness=0.3)
    create_material(project, name="PanelBlue", color=[0.12, 0.34, 0.72, 1.0], metallic=0.0, roughness=0.16)
    create_material(project, name="EngineDark", color=[0.07, 0.08, 0.11, 1.0], metallic=0.55, roughness=0.2)
    create_material(project, name="GlowCyan", color=[0.38, 0.86, 1.0, 1.0], metallic=0.0, roughness=0.06)
    set_material_property(project, _material_index(project, "GlowCyan"), "emission_color", [0.38, 0.86, 1.0, 1.0])
    set_material_property(project, _material_index(project, "GlowCyan"), "emission_strength", 7.2)
def _configure_scene(project: Dict) -> None:
    project["world"]["background_color"] = [0.08, 0.1, 0.16]
    set_render_settings(project, preset="eevee_preview")
    add_camera(
        project,
        name="HeroCam",
        location=[9.6, -7.6, 5.7],
        rotation=[71, 0, 52],
        focal_length=40,
        set_active=True,
    )
    add_light(project, light_type="SUN", name="SunKey", rotation=[-42, 0, 26], power=3.4)
    add_light(project, light_type="AREA", name="RimFill", location=[-5.6, 5.1, 5.0], rotation=[56, 0, -34], power=2600)
    add_light(project, light_type="POINT", name="FrontBounce", location=[2.8, -3.6, 3.9], power=620)
    add_light(project, light_type="POINT", name="BeaconBounce", location=[0.0, 0.0, 3.35], power=180)
