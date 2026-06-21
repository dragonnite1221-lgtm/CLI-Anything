# ruff: noqa: F403, F405, E501
from .preview_bundle_base import *  # noqa: F403

# fmt: off
from .preview_bundle_p3 import _clean_none_fields  # noqa: E402,E501
# fmt: on


def summarize_trajectory(
    trajectory: Dict[str, Any], *, recent_steps: int = 3
) -> Dict[str, Any]:
    steps = list(trajectory.get("steps") or [])
    latest = steps[-1] if steps else {}
    recent = steps[-max(1, int(recent_steps)) :] if steps else []
    return _clean_none_fields(
        {
            "protocol_version": trajectory.get("protocol_version"),
            "software": trajectory.get("software"),
            "recipe": trajectory.get("recipe"),
            "step_count": trajectory.get("step_count", len(steps)),
            "current_step_id": trajectory.get("current_step_id"),
            "latest_command": latest.get("command"),
            "latest_publish_reason": latest.get("publish_reason"),
            "latest_bundle_id": latest.get("bundle_id"),
            "recent_steps": [
                _clean_none_fields(
                    {
                        "step_id": item.get("step_id"),
                        "step_index": item.get("step_index"),
                        "bundle_id": item.get("bundle_id"),
                        "publish_reason": item.get("publish_reason"),
                        "command": item.get("command"),
                        "command_finished_at": item.get("command_finished_at"),
                        "status": item.get("status"),
                        "cached": item.get("cached"),
                    }
                )
                for item in recent
            ],
        }
    )


def build_live_history_item(
    bundle_manifest: Dict[str, Any],
    *,
    step_id: Optional[str] = None,
    step_index: Optional[int] = None,
    publish_reason: Optional[str] = None,
    command: Optional[str] = None,
    command_started_at: Optional[str] = None,
    command_finished_at: Optional[str] = None,
    source_fingerprint: Optional[str] = None,
    stage_label: Optional[str] = None,
    note: Optional[str] = None,
) -> Dict[str, Any]:
    source = bundle_manifest.get("source") or {}
    resolved_command = command or (bundle_manifest.get("generator") or {}).get(
        "command"
    )
    resolved_fingerprint = (
        source_fingerprint
        or source.get("project_fingerprint")
        or source.get("capture_fingerprint")
    )
    created_at = bundle_manifest.get("created_at")
    return _clean_none_fields(
        {
            "step_id": step_id,
            "step_index": step_index,
            "bundle_id": bundle_manifest.get("bundle_id"),
            "bundle_dir": bundle_manifest.get("_bundle_dir"),
            "manifest_path": bundle_manifest.get("_manifest_path"),
            "summary_path": bundle_manifest.get("_summary_path"),
            "created_at": created_at,
            "status": bundle_manifest.get("status"),
            "cached": bool(bundle_manifest.get("cached")),
            "publish_reason": publish_reason,
            "command": resolved_command,
            "command_started_at": command_started_at or created_at,
            "command_finished_at": command_finished_at or created_at,
            "source_fingerprint": resolved_fingerprint,
            "stage_label": stage_label,
            "note": note,
        }
    )
