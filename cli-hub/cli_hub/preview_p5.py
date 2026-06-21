# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403
# fmt: off
from .preview_p1 import _coalesce, load_bundle, load_session  # noqa: E402,E501
from .preview_p4 import _history_from_session, _load_trajectory  # noqa: E402,E501
# fmt: on


def _apply_session_trajectory_metadata(trajectory: Optional[Dict[str, Any]], session: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if trajectory is None:
        return None
    trajectory["protocol"] = _coalesce(
        trajectory.get("protocol"),
        session.get("trajectory_protocol_version"),
    )
    trajectory["step_count"] = _coalesce(
        session.get("trajectory_step_count"),
        trajectory.get("step_count"),
    )
    trajectory["current_step_id"] = _coalesce(
        session.get("current_step_id"),
        trajectory.get("current_step_id"),
    )
    trajectory["recent_command"] = _coalesce(
        session.get("latest_command"),
        trajectory.get("recent_command"),
    )
    trajectory["recent_publish_reason"] = _coalesce(
        session.get("latest_publish_reason"),
        trajectory.get("recent_publish_reason"),
    )
    return trajectory
def _render_trajectory_text_lines(title: str, trajectory: Optional[Dict[str, Any]], *, limit: int = 5) -> List[str]:
    if not trajectory:
        return []
    lines = [
        "",
        title,
        f"  Source: {trajectory.get('source_label') or trajectory.get('mode') or 'unknown'}",
        f"  Steps: {trajectory.get('step_count', 0)}",
        f"  Published bundles: {trajectory.get('published_bundle_count', 0)}",
    ]
    if trajectory.get("current_step_id"):
        lines.append(f"  Current step: {trajectory['current_step_id']}")
    if trajectory.get("recent_command"):
        lines.append(f"  Recent command: {trajectory['recent_command']}")
    if trajectory.get("recent_publish_reason"):
        lines.append(f"  Recent publish: {trajectory['recent_publish_reason']}")
    if trajectory.get("recent_bundle_id"):
        lines.append(f"  Recent bundle: {trajectory['recent_bundle_id']}")
    entries = trajectory.get("entries", [])
    if entries:
        lines.append("  Timeline")
        for entry in entries[-limit:]:
            label = entry.get("step_label") or entry.get("stage_label") or entry.get("step_id") or "step"
            lines.append(f"    - {label}")
            if entry.get("command"):
                lines.append(f"      Command: {entry['command']}")
            if entry.get("publish_reason"):
                lines.append(f"      Publish: {entry['publish_reason']}")
            if entry.get("bundle_id"):
                lines.append(f"      Bundle: {entry['bundle_id']}")
    return lines
def inspect_bundle(bundle_ref: str) -> Dict[str, Any]:
    bundle_dir, manifest, summary = load_bundle(bundle_ref)
    return {
        "bundle_dir": str(bundle_dir),
        "manifest": manifest,
        "summary": summary,
        "artifact_count": len(manifest.get("artifacts", [])),
        "trajectory": _load_trajectory(bundle_dir, manifest, summary),
    }
def inspect_session(session_ref: str) -> Dict[str, Any]:
    session_dir, session = load_session(session_ref)
    current_bundle = None
    try:
        current_bundle = inspect_bundle(str(session_dir / session.get("current_link", "current")))
    except (FileNotFoundError, ValueError):
        current_bundle = None
    trajectory = _load_trajectory(session_dir, session)
    if trajectory is None:
        trajectory = _history_from_session(session)
    trajectory = _apply_session_trajectory_metadata(trajectory, session)
    return {
        "session_dir": str(session_dir),
        "session": session,
        "current_bundle": current_bundle,
        "trajectory": trajectory,
    }
