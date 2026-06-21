# ruff: noqa: F403, F405, E501
from .blender_preview_story_demo_base import *  # noqa: F403
# fmt: off
from .blender_preview_story_demo_p1 import BASELINE_START_S, FINAL_STILL_STEP_S, PREVIEW_SWITCH_LATENCY_S, TURNTABLE_STEP_S, _stage_display_cmd, _stage_story, _stage_title, load_json, write_json  # noqa: E402,E501
# fmt: on


def build_trajectory(build_manifest_path: Path, output_dir: Path) -> Dict[str, Any]:
    build_manifest = load_json(build_manifest_path)
    project_path = Path(build_manifest["project_path"]).expanduser().resolve()
    live_root = Path(build_manifest["preview_root"]).expanduser().resolve()
    final_render_path = Path(build_manifest["final_render"]["output"]).expanduser().resolve()
    turntable_path = Path(build_manifest["motion"]["video"]["video_path"]).expanduser().resolve()
    live_session = build_manifest.get("live_session") or {}
    stage_log = build_manifest.get("stage_log") or []
    if not stage_log:
        raise RuntimeError(f"No stage_log entries found in {build_manifest_path}")

    commands: List[Dict[str, Any]] = []
    t = 0.0

    def add_command(cmd_id: str, label: str, display_cmd: str, duration_s: float) -> Dict[str, Any]:
        nonlocal t
        command = {
            "index": len(commands),
            "id": cmd_id,
            "label": label,
            "display_cmd": display_cmd,
            "duration_s": float(duration_s),
            "timeline_start_s": round(t, 3),
            "timeline_end_s": round(t + float(duration_s), 3),
            "stdout": "",
            "stderr": "",
            "returncode": 0,
        }
        commands.append(command)
        t += float(duration_s)
        return command

    def bundle_payload(stage: Dict[str, Any]) -> Dict[str, Any]:
        bundle_dir = Path(stage["current_bundle_dir"]).expanduser().resolve()
        manifest_path = Path(stage["current_manifest_path"]).expanduser().resolve()
        summary_path = bundle_dir / "summary.json"
        manifest = load_json(manifest_path)
        summary = load_json(summary_path)
        artifacts = {
            item["artifact_id"]: str((bundle_dir / item["path"]).resolve())
            for item in manifest.get("artifacts", [])
        }
        return {
            "bundle_id": manifest["bundle_id"],
            "bundle_dir": str(bundle_dir),
            "manifest_path": str(manifest_path),
            "summary_path": str(summary_path),
            "artifacts": artifacts,
            "summary": summary,
        }

    baseline_command = add_command(
        "live-baseline",
        "Bring live preview online from the launch-platform baseline",
        str(
            live_session.get("start_command")
            or f"cli-anything-blender --project {project_path} preview live start --recipe quick --mode manual --root-dir {live_root}"
        ),
        BASELINE_START_S,
    )

    preview_events: List[Dict[str, Any]] = []
    baseline_stage = stage_log[0]
    preview_events.append(
        {
            "sequence_index": 1,
            "step_index": baseline_command["index"],
            "step_id": baseline_command["id"],
            "step_label": baseline_command["label"],
            "stage_id": baseline_stage["stage"],
            "stage_title": _stage_title(baseline_stage),
            "stage_story": _stage_story(baseline_stage),
            "timeline_ready_s": 0.0,
            "latency_s": 0.0,
            "bundle_count": int(baseline_stage.get("bundle_count") or 1),
            "publish_reason": f"stage:{baseline_stage['stage']}",
            "session_path": baseline_stage["session_path"],
            "session_dir": str(Path(baseline_stage["session_path"]).expanduser().resolve().parent),
            "copied_bundle": bundle_payload(baseline_stage),
        }
    )

    for sequence_index, stage in enumerate(stage_log[1:], start=2):
        command = add_command(
            f"stage-{stage['stage']}",
            str(stage.get("label") or stage["stage"]).strip(),
            _stage_display_cmd(stage),
            float(stage.get("duration_s") or 0.9),
        )
        ready_t = round(float(command["timeline_end_s"]) + PREVIEW_SWITCH_LATENCY_S, 3)
        preview_events.append(
            {
                "sequence_index": sequence_index,
                "step_index": command["index"],
                "step_id": command["id"],
                "step_label": command["label"],
                "stage_id": stage["stage"],
                "stage_title": _stage_title(stage),
                "stage_story": _stage_story(stage),
                "timeline_ready_s": ready_t,
                "latency_s": PREVIEW_SWITCH_LATENCY_S,
                "bundle_count": int(stage["bundle_count"]),
                "publish_reason": f"stage:{stage['stage']}",
                "session_path": stage["session_path"],
                "session_dir": str(Path(stage["session_path"]).expanduser().resolve().parent),
                "copied_bundle": bundle_payload(stage),
            }
        )

    add_command(
        "final-still",
        "Render final hero still",
        f"render_scene(..., output='{final_render_path}')",
        FINAL_STILL_STEP_S,
    )
    add_command(
        "turntable",
        "Package the real turntable ending",
        f"ffmpeg -> {turntable_path}",
        TURNTABLE_STEP_S,
    )

    trajectory = {
        "protocol": "blender-preview-trajectory/v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "scenario": "orbital-relay-drone",
        "scenario_title": "Orbital Relay Drone",
        "scenario_subtitle": "launch-platform baseline, step-aligned real preview checkpoints, then a real turntable ending",
        "build_manifest_path": str(build_manifest_path.resolve()),
        "project_path": str(project_path),
        "live_root": str(live_root),
        "final_render": str(final_render_path),
        "turntable_video": str(turntable_path),
        "commands": commands,
        "preview_events": preview_events,
        "notes": [
            "The first preview shown on the right is the real stage-00 launch-platform bundle, used as a live baseline instead of leaving the monitor empty.",
            "Every later preview switch is keyed from the matching real stage_log entry, so command completion and preview refresh stay aligned.",
            "The ending appends the existing real turntable video from the same run.",
        ],
    }
    write_json(output_dir / "trajectory.json", trajectory)
    return trajectory
