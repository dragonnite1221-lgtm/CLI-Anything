# ruff: noqa: F403, F405, E501
from .blender_orbital_relay_drone_demo_base import *  # noqa: F403
# fmt: off
from .blender_orbital_relay_drone_demo_p1 import _object_index, _set_parent  # noqa: E402,E501
# fmt: on


def _rig_parents(project: Dict) -> None:
    root_children = [
        "HullCore",
        "NoseCone",
        "BridgePod",
        "DockRing",
        "ServiceCabin",
        "WingSpar",
        "PanelArmLeft",
        "PanelArmRight",
        "SolarPanelLeft",
        "SolarPanelRight",
        "SolarRibLeft",
        "SolarRibRight",
        "EngineBlock",
        "ThrusterTopLeft",
        "ThrusterBottomLeft",
        "ThrusterTopRight",
        "ThrusterBottomRight",
        "NozzleTopLeft",
        "NozzleBottomLeft",
        "NozzleTopRight",
        "NozzleBottomRight",
        "SensorMast",
        "BeaconCore",
        "NavLightLeft",
        "NavLightRight",
        "ServiceArmBase",
        "ServiceArmReach",
        "ServiceTool",
        "CommFin",
        "DishPivot",
    ]
    for child_name in root_children:
        if any(obj.get("name") == child_name for obj in project["objects"]):
            _set_parent(project, child_name, "DroneRoot")

    for child_name in ("RadarDish",):
        if any(obj.get("name") == child_name for obj in project["objects"]):
            _set_parent(project, child_name, "DishPivot")
def _add_motion(project: Dict) -> None:
    set_frame_range(project, 1, 36)
    set_fps(project, 12)

    add_keyframe(project, _object_index(project, "DroneRoot"), 1, "location", [0, 0, 0], interpolation="BEZIER")
    add_keyframe(project, _object_index(project, "DroneRoot"), 18, "location", [0, 0, 0.14], interpolation="BEZIER")
    add_keyframe(project, _object_index(project, "DroneRoot"), 36, "location", [0, 0, 0], interpolation="BEZIER")
    add_keyframe(project, _object_index(project, "DroneRoot"), 1, "rotation", [0, 0, 18], interpolation="LINEAR")
    add_keyframe(project, _object_index(project, "DroneRoot"), 36, "rotation", [0, 0, 378], interpolation="LINEAR")

    add_keyframe(project, _object_index(project, "DishPivot"), 1, "rotation", [0, 0, 0], interpolation="LINEAR")
    add_keyframe(project, _object_index(project, "DishPivot"), 36, "rotation", [0, 0, 540], interpolation="LINEAR")

    add_keyframe(project, _object_index(project, "DockRing"), 1, "rotation", [0, 90, 0], interpolation="LINEAR")
    add_keyframe(project, _object_index(project, "DockRing"), 36, "rotation", [0, 90, 360], interpolation="LINEAR")

    add_keyframe(project, _object_index(project, "BeaconCore"), 1, "scale", [0.22, 0.22, 0.22], interpolation="BEZIER")
    add_keyframe(project, _object_index(project, "BeaconCore"), 12, "scale", [0.33, 0.33, 0.33], interpolation="BEZIER")
    add_keyframe(project, _object_index(project, "BeaconCore"), 24, "scale", [0.22, 0.22, 0.22], interpolation="BEZIER")
    add_keyframe(project, _object_index(project, "BeaconCore"), 36, "scale", [0.31, 0.31, 0.31], interpolation="BEZIER")

    add_keyframe(project, _object_index(project, "NavLightLeft"), 1, "scale", [0.11, 0.11, 0.11], interpolation="BEZIER")
    add_keyframe(project, _object_index(project, "NavLightLeft"), 18, "scale", [0.16, 0.16, 0.16], interpolation="BEZIER")
    add_keyframe(project, _object_index(project, "NavLightLeft"), 36, "scale", [0.11, 0.11, 0.11], interpolation="BEZIER")
    add_keyframe(project, _object_index(project, "NavLightRight"), 1, "scale", [0.11, 0.11, 0.11], interpolation="BEZIER")
    add_keyframe(project, _object_index(project, "NavLightRight"), 18, "scale", [0.16, 0.16, 0.16], interpolation="BEZIER")
    add_keyframe(project, _object_index(project, "NavLightRight"), 36, "scale", [0.11, 0.11, 0.11], interpolation="BEZIER")

    set_current_frame(project, 1)
def _capture_stage(
    session: Session,
    stage_name: str,
    stage_log: List[Dict],
    preview_root: Path,
    started: bool,
    *,
    label: str,
    story: str,
    display_cmd: str,
    duration_s: float,
) -> bool:
    if not started:
        live_payload = preview_mod.live_start(
            session,
            recipe="quick",
            root_dir=str(preview_root),
            force=True,
            refresh_hint_ms=1000,
            live_mode="manual",
            publish_reason=f"stage:{stage_name}",
            command=f"blender_demo.py --stage {stage_name}",
        )
    else:
        live_payload = preview_mod.live_push(
            session,
            recipe="quick",
            root_dir=str(preview_root),
            force=True,
            refresh_hint_ms=1000,
            publish_reason=f"stage:{stage_name}",
            command=f"blender_demo.py --stage {stage_name}",
        )
    stage_log.append(
        {
            "stage": stage_name,
            "bundle_id": live_payload.get("current_bundle_id"),
            "bundle_count": live_payload.get("bundle_count"),
            "session_path": live_payload.get("_session_path"),
            "current_manifest_path": live_payload.get("current_manifest_path"),
            "current_bundle_dir": live_payload.get("current_bundle_dir"),
            "label": label,
            "story": story,
            "display_cmd": display_cmd,
            "duration_s": duration_s,
        }
    )
    return True
