# ruff: noqa: F403, F405, E501
from ._test_cli_hub_base import *  # noqa: F403
from ._test_cli_hub_p0 import _make_preview_bundle  # noqa: F401,E501


def _make_preview_session(tmp_path: Path, *, with_trajectory: bool = False) -> Path:
    bundle_dir = _make_preview_bundle(tmp_path)
    session_dir = tmp_path / "live-session"
    session_dir.mkdir()
    (session_dir / "current").symlink_to(bundle_dir, target_is_directory=True)
    session = {
        "protocol_version": "preview-live/v1",
        "software": "shotcut",
        "recipe": "quick",
        "status": "active",
        "session_name": "demo-live",
        "project_path": "/tmp/demo.mlt",
        "project_name": "demo.mlt",
        "updated_at": "2026-04-20T09:00:00Z",
        "current_link": "current",
        "current_bundle_id": "20260419T104530Z_deadbeef_quick",
        "watch_command": "cli-hub previews watch /tmp/live-session --open",
        "publish_command": "cli-anything-shotcut preview live push --recipe quick",
        "inspect_command": "cli-hub previews inspect /tmp/live-session",
        "history": [
            {
                "bundle_id": "20260419T104530Z_deadbeef_quick",
                "bundle_dir": str(bundle_dir),
                "created_at": "2026-04-19T10:45:30Z",
                "status": "ok",
            }
        ],
    }
    if with_trajectory:
        trajectory = {
            "protocol_version": "preview-trajectory/v1",
            "step_count": 2,
            "current_step_id": "step-002",
            "steps": [
                {
                    "step_id": "step-001",
                    "step_index": 0,
                    "bundle_id": "20260419T104530Z_deadbeef_quick",
                    "bundle_dir": str(bundle_dir),
                    "manifest_path": str(bundle_dir / "manifest.json"),
                    "summary_path": str(bundle_dir / "summary.json"),
                    "created_at": "2026-04-19T10:45:30Z",
                    "status": "ok",
                    "cached": False,
                    "publish_reason": "live-start",
                    "command": "cli-anything-shotcut preview live start --recipe quick",
                    "command_started_at": "2026-04-19T10:45:28Z",
                    "command_finished_at": "2026-04-19T10:45:30Z",
                    "source_fingerprint": "sha256:test-a",
                },
                {
                    "step_id": "step-002",
                    "step_index": 1,
                    "bundle_id": "20260419T104530Z_deadbeef_quick",
                    "bundle_dir": str(bundle_dir),
                    "manifest_path": str(bundle_dir / "manifest.json"),
                    "summary_path": str(bundle_dir / "summary.json"),
                    "created_at": "2026-04-19T10:47:10Z",
                    "status": "ok",
                    "cached": True,
                    "publish_reason": "manual-push",
                    "command": "cli-anything-shotcut preview live push --recipe quick",
                    "command_started_at": "2026-04-19T10:47:07Z",
                    "command_finished_at": "2026-04-19T10:47:10Z",
                    "source_fingerprint": "sha256:test-b",
                },
            ],
        }
        (session_dir / "trajectory.json").write_text(json.dumps(trajectory, indent=2))
        session.update(
            {
                "trajectory_path": "trajectory.json",
                "trajectory_protocol_version": "preview-trajectory/v1",
                "trajectory_step_count": 2,
                "current_step_id": "step-002",
                "latest_command": "cli-anything-shotcut preview live push --recipe quick",
                "latest_publish_reason": "manual-push",
            }
        )
    (session_dir / "session.json").write_text(json.dumps(session, indent=2))
    return session_dir
