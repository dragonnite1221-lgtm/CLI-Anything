# ruff: noqa: F403, F405, E501
from .blender_orbital_relay_drone_demo_base import *  # noqa: F403
# fmt: off
from .blender_orbital_relay_drone_demo_p1 import _render_live_html  # noqa: E402,E501
from .blender_orbital_relay_drone_demo_p5 import _capture_stage  # noqa: E402,E501
# fmt: on


def _build_demo_part0(live_started, output_dir, preview_root, project, project_path, session, stage_log, use_live_preview):
    if use_live_preview:
        live_started = _capture_stage(
            session,
            "07_motion_ready",
            stage_log,
            preview_root,
            live_started,
            label="Author hover, spin, and beacon motion",
            story="Hover motion, dish spin, ring rotation, and beacon pulses prepare the final presentation state.",
            display_cmd="add_keyframe DroneRoot / DishPivot / DockRing / BeaconCore / NavLights",
            duration_s=1.0,
        )
        set_current_frame(project, 1)
        save_scene(project, str(project_path))
        live_payload = preview_mod.live_stop(session, recipe="quick", root_dir=str(preview_root))
        live_html = _render_live_html(Path(live_payload["_session_dir"]), output_dir / "live.html")
    else:
        set_current_frame(project, 1)
        save_scene(project, str(project_path))
        live_payload = None
        live_html = None
    return live_html, live_payload
def _build_demo_part1(live_started, preview_root, session, stage_log, use_live_preview):
    if use_live_preview:
        live_started = _capture_stage(
            session,
            "00_launch_platform",
            stage_log,
            preview_root,
            live_started,
            label="Build launch platform",
            story="Deck floor, display base, raised launch pad, stripe ring, and center lift column.",
            display_cmd="add DeckFloor / DisplayBase / LaunchPad / PadStripeRing / LiftColumn",
            duration_s=0.9,
        )
    return live_started
