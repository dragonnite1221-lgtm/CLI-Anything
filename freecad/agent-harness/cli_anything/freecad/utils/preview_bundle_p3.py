# ruff: noqa: F403, F405, E501
from .preview_bundle_base import *  # noqa: F403

# fmt: off
from .preview_bundle_p1 import _load_json  # noqa: E402,E501
from .preview_bundle_p2 import write_json  # noqa: E402,E501
# fmt: on


def finalize_bundle(
    bundle_dir: str,
    bundle_id: str,
    bundle_kind: str,
    software: str,
    recipe: str,
    source: Dict[str, Any],
    artifacts: list[Dict[str, Any]],
    summary: Dict[str, Any],
    cache_key: str,
    generator: Dict[str, Any],
    status: str = "ok",
    warnings: Optional[list[str]] = None,
    context: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    labels: Optional[list[str]] = None,
    source_bundles: Optional[list[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    bundle_path = Path(bundle_dir).resolve()
    summary_rel = "summary.json"
    summary_path = write_json(str(bundle_path / summary_rel), summary)
    manifest = {
        "protocol_version": PROTOCOL_VERSION,
        "bundle_id": bundle_id,
        "bundle_kind": bundle_kind,
        "software": software,
        "recipe": recipe,
        "status": status,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "cache_key": cache_key,
        "generator": generator,
        "source": source,
        "summary_path": summary_rel,
        "artifacts": artifacts,
    }
    if warnings:
        manifest["warnings"] = warnings
    if context:
        manifest["context"] = context
    if metrics:
        manifest["metrics"] = metrics
    if labels:
        manifest["labels"] = labels
    if source_bundles:
        manifest["source_bundles"] = source_bundles
    manifest_path = write_json(str(bundle_path / "manifest.json"), manifest)
    manifest["_manifest_path"] = manifest_path
    manifest["_bundle_dir"] = str(bundle_path)
    manifest["_summary_path"] = summary_path
    return manifest


def _clean_none_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in data.items() if value is not None}


def live_trajectory_path(session_dir: str | Path) -> Path:
    return Path(session_dir).expanduser().resolve() / "trajectory.json"


def load_live_trajectory(session_dir: str | Path) -> Dict[str, Any]:
    trajectory_path = live_trajectory_path(session_dir)
    if not trajectory_path.is_file():
        return {}
    return _load_json(trajectory_path)


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
