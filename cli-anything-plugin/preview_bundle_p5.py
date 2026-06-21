# ruff: noqa: F403, F405, E501
from .preview_bundle_base import *  # noqa: F403

# fmt: off
from .preview_bundle_p1 import TRAJECTORY_PROTOCOL_VERSION  # noqa: E402,E501
from .preview_bundle_p3 import _clean_none_fields, live_trajectory_path, load_live_trajectory, write_json  # noqa: E402,E501
from .preview_bundle_p4 import build_live_history_item  # noqa: E402,E501
# fmt: on


def append_live_trajectory(
    session_dir: str | Path,
    *,
    software: str,
    recipe: str,
    bundle_manifest: Dict[str, Any],
    publish_reason: str,
    project_path: Optional[str] = None,
    project_name: Optional[str] = None,
    session_name: Optional[str] = None,
    command: Optional[str] = None,
    command_started_at: Optional[str] = None,
    command_finished_at: Optional[str] = None,
    source_fingerprint: Optional[str] = None,
    stage_label: Optional[str] = None,
    note: Optional[str] = None,
) -> Dict[str, Any]:
    session_path = Path(session_dir).expanduser().resolve()
    existing = load_live_trajectory(session_path)
    steps = list(existing.get("steps") or [])
    finished_at = (
        command_finished_at
        or bundle_manifest.get("created_at")
        or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )
    started_at = command_started_at or finished_at
    step_index = len(steps) + 1
    step_id = f"step-{step_index:04d}"
    step = build_live_history_item(
        bundle_manifest,
        step_id=step_id,
        step_index=step_index,
        publish_reason=publish_reason,
        command=command,
        command_started_at=started_at,
        command_finished_at=finished_at,
        source_fingerprint=source_fingerprint,
        stage_label=stage_label,
        note=note,
    )
    steps.append(step)

    trajectory: Dict[str, Any] = dict(existing)
    trajectory.update(
        _clean_none_fields(
            {
                "protocol_version": TRAJECTORY_PROTOCOL_VERSION,
                "software": software,
                "recipe": recipe,
                "session_name": session_name or session_path.name,
                "project_path": project_path,
                "project_name": project_name,
                "created_at": existing.get("created_at", finished_at),
                "updated_at": finished_at,
                "step_count": len(steps),
                "current_step_id": step_id,
            }
        )
    )
    trajectory["steps"] = steps
    trajectory_path = write_json(str(live_trajectory_path(session_path)), trajectory)
    trajectory["_trajectory_path"] = trajectory_path
    trajectory["latest_step"] = step
    return trajectory
