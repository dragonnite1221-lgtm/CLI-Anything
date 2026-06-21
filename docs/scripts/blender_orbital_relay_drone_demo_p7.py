# ruff: noqa: F403, F405, E501
from .blender_orbital_relay_drone_demo_base import *  # noqa: F403
# fmt: off
from .blender_orbital_relay_drone_demo_p1 import _add_materials, _configure_scene, _copy_motion_stills, _encode_video, _render_via_script  # noqa: E402,E501
from .blender_orbital_relay_drone_demo_p2 import _build_stage_00_launch_platform, _build_stage_01_hull_blockout, _build_stage_02_wing_structure  # noqa: E402,E501
from .blender_orbital_relay_drone_demo_p3 import _build_stage_03_solar_arrays, _build_stage_04_propulsion  # noqa: E402,E501
from .blender_orbital_relay_drone_demo_p4 import _assign_materials, _build_stage_05_sensor_payload, _build_stage_06_service_rig  # noqa: E402,E501
from .blender_orbital_relay_drone_demo_p5 import _add_motion, _capture_stage, _rig_parents  # noqa: E402,E501
from .blender_orbital_relay_drone_demo_p6 import _build_demo_part0, _build_demo_part1  # noqa: E402,E501
# fmt: on


def build_demo(output_dir: Path, use_live_preview: bool = True) -> Dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    preview_root = output_dir / "live-root"
    project_path = output_dir / "orbital_relay_drone.blend-cli.json"
    manifest_path = output_dir / "build_manifest.json"
    final_render_path = output_dir / "renders" / "orbital_relay_drone_final.png"
    frames_dir = output_dir / "motion" / "frames"
    video_path = output_dir / "motion" / "orbital_relay_drone_turntable.mp4"
    stills_dir = output_dir / "motion" / "stills"

    project = create_scene(name="orbital-relay-drone", profile="preview")
    _configure_scene(project)
    _add_materials(project)

    session = Session()
    stage_log: List[Dict] = []
    live_started = False

    _build_stage_00_launch_platform(project)
    _assign_materials(project)
    print("[demo] Stage 00: launch platform")
    save_scene(project, str(project_path))
    session.set_project(project, str(project_path))
    live_started = _build_demo_part1(live_started, preview_root, session, stage_log, use_live_preview)

    _build_stage_01_hull_blockout(project)
    _assign_materials(project)
    print("[demo] Stage 01: hull blockout")
    save_scene(project, str(project_path))
    if use_live_preview:
        live_started = _capture_stage(
            session,
            "01_hull_blockout",
            stage_log,
            preview_root,
            live_started,
            label="Block out the hull and docking silhouette",
            story="Drone root, main hull cylinder, nose cone, bridge pod, docking ring, and service cabin.",
            display_cmd="add DroneRoot / HullCore / NoseCone / BridgePod / DockRing / ServiceCabin",
            duration_s=1.0,
        )

    _build_stage_02_wing_structure(project)
    _assign_materials(project)
    print("[demo] Stage 02: wing structure")
    save_scene(project, str(project_path))
    if use_live_preview:
        live_started = _capture_stage(
            session,
            "02_wing_structure",
            stage_log,
            preview_root,
            live_started,
            label="Add wing spar and panel arms",
            story="The drone starts reading as a spacecraft once the lateral wing spar and panel hinges appear.",
            display_cmd="add WingSpar / PanelArmLeft / PanelArmRight",
            duration_s=0.8,
        )

    _build_stage_03_solar_arrays(project)
    _assign_materials(project)
    print("[demo] Stage 03: solar arrays")
    save_scene(project, str(project_path))
    if use_live_preview:
        live_started = _capture_stage(
            session,
            "03_solar_arrays",
            stage_log,
            preview_root,
            live_started,
            label="Add solar panels and rib arrays",
            story="Blue panel slabs and rib arrays turn the side arms into readable power modules.",
            display_cmd="add SolarPanelLeft/Right / array SolarRibLeft/Right",
            duration_s=0.9,
        )

    _build_stage_04_propulsion(project)
    _assign_materials(project)
    print("[demo] Stage 04: propulsion")
    save_scene(project, str(project_path))
    if use_live_preview:
        live_started = _capture_stage(
            session,
            "04_propulsion",
            stage_log,
            preview_root,
            live_started,
            label="Add engine block and thruster pack",
            story="The rear engine block and clustered nozzles complete the propulsion silhouette.",
            display_cmd="add EngineBlock / thrusters / nozzle cones",
            duration_s=0.9,
        )

    _build_stage_05_sensor_payload(project)
    _assign_materials(project)
    print("[demo] Stage 05: sensor payload")
    save_scene(project, str(project_path))
    if use_live_preview:
        live_started = _capture_stage(
            session,
            "05_sensor_payload",
            stage_log,
            preview_root,
            live_started,
            label="Add radar dish and navigation payloads",
            story="Dish pivot, radar plate, beacon core, and nav lights add the recognizable inspection payloads.",
            display_cmd="add DishPivot / SensorMast / RadarDish / BeaconCore / NavLightLeft/Right",
            duration_s=0.9,
        )

    _build_stage_06_service_rig(project)
    _assign_materials(project)
    _rig_parents(project)
    print("[demo] Stage 06: service rig")
    save_scene(project, str(project_path))
    if use_live_preview:
        live_started = _capture_stage(
            session,
            "06_service_rig",
            stage_log,
            preview_root,
            live_started,
            label="Add service arm and parenting rig",
            story="Service arm, comm fin, and object parenting wire the drone into an assembled, animatable artifact.",
            display_cmd="add ServiceArmBase / ServiceArmReach / ServiceTool / CommFin / set parent hierarchy",
            duration_s=1.0,
        )

    _add_motion(project)
    print("[demo] Stage 07: motion ready")
    set_current_frame(project, 18)
    save_scene(project, str(project_path))
    live_html, live_payload = _build_demo_part0(live_started, output_dir, preview_root, project, project_path, session, stage_log, use_live_preview)

    final_project = copy.deepcopy(project)
    set_render_settings(final_project, preset="eevee_high", resolution_x=1440, resolution_y=810, samples=48, output_format="PNG")
    set_current_frame(final_project, 1)
    print(f"[demo] Rendering final still -> {final_render_path}")
    final_render = _render_via_script(final_project, final_render_path, frame=1, animation=False, timeout=720)
    if not final_render_path.exists():
        raise RuntimeError(f"Final render missing: {final_render_path}")
    final_render["output"] = str(final_render_path)
    final_render["file_size"] = final_render_path.stat().st_size
    final_render["blender_version"] = blender_backend.get_version()

    motion_project = copy.deepcopy(project)
    set_render_settings(motion_project, preset="eevee_default", resolution_x=640, resolution_y=360, samples=8, output_format="PNG")
    print(f"[demo] Rendering motion frames -> {frames_dir}")
    motion_job = _render_via_script(motion_project, frames_dir / "frame_", animation=True, timeout=1200)
    frame_files = sorted(frames_dir.glob("frame_*.png"))
    if not frame_files:
        raise RuntimeError(f"Animation render produced no frames under {frames_dir}")
    print(f"[demo] Encoding motion video -> {video_path}")
    motion_video = _encode_video(frames_dir, video_path, fps=int(motion_project["scene"]["fps"]))
    motion_stills = _copy_motion_stills(frame_files, stills_dir)

    payload = {
        "project_path": str(project_path),
        "preview_root": str(preview_root),
        "stage_log": stage_log,
        "live_session": live_payload,
        "live_html": live_html,
        "final_render": final_render,
        "motion": {
            "frames_dir": str(frames_dir),
            "frame_count": len(frame_files),
            "first_frame": str(frame_files[0]),
            "last_frame": str(frame_files[-1]),
            "render_job": motion_job,
            "video": motion_video,
            "stills": motion_stills,
        },
    }
    manifest_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload
