# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403

# fmt: off
from .preview_p1 import _load_existing_live_session, _now_iso, _project_file_fingerprint  # noqa: E402,E501
from .preview_p2 import _write_live_session_updates  # noqa: E402,E501
from .preview_p5 import live_start  # noqa: E402,E501
# fmt: on


def poll_live_session_once(session_dir: str) -> Dict[str, Any]:
    """Run one poll cycle for a live session and capture if the source changed."""
    session_path = Path(session_dir).expanduser().resolve()
    payload = _load_existing_live_session(session_path)
    now = _now_iso()
    if not payload:
        return {"action": "exit", "reason": "missing-session"}

    if payload.get("status") != "active":
        _write_live_session_updates(
            session_path,
            {
                "poller": {
                    "pid": os.getpid(),
                    "running": False,
                    "last_heartbeat": now,
                    "last_exit_reason": f"session-status:{payload.get('status')}",
                }
            },
        )
        return {"action": "exit", "reason": f"status:{payload.get('status')}"}

    if payload.get("live_mode") != "poll":
        _write_live_session_updates(
            session_path,
            {
                "poller": {
                    "pid": os.getpid(),
                    "running": False,
                    "last_heartbeat": now,
                    "last_exit_reason": f"live-mode:{payload.get('live_mode')}",
                }
            },
        )
        return {"action": "exit", "reason": f"mode:{payload.get('live_mode')}"}

    project_path = payload.get("project_path")
    current_fingerprint = _project_file_fingerprint(project_path)
    base_updates: Dict[str, Any] = {
        "poller": {
            "pid": os.getpid(),
            "running": True,
            "last_heartbeat": now,
        },
        "source_state": {
            "source_type": "project-file",
            "project_path": project_path,
        },
    }
    if current_fingerprint:
        base_updates["source_state"]["last_seen_fingerprint"] = current_fingerprint

    last_rendered = (payload.get("source_state") or {}).get("last_rendered_fingerprint")
    if not project_path or not os.path.isfile(project_path):
        base_updates["source_state"]["last_error"] = (
            f"Project path unavailable: {project_path or '(none)'}"
        )
        base_updates["source_state"]["last_error_at"] = now
        _write_live_session_updates(session_path, base_updates)
        return {
            "action": "idle",
            "reason": "missing-project",
            "project_path": project_path,
        }

    if current_fingerprint and current_fingerprint == last_rendered:
        _write_live_session_updates(session_path, base_updates)
        return {"action": "idle", "fingerprint": current_fingerprint}

    try:
        session = Session()
        project = doc_mod.open_document(project_path)
        session.set_project(project, path=project_path)
        live_payload = live_start(
            session,
            recipe=str(payload.get("recipe") or "quick"),
            root_dir=payload.get("preview_root_dir"),
            force=False,
            refresh_hint_ms=int(
                payload.get("refresh_hint_ms") or DEFAULT_REFRESH_HINT_MS
            ),
            live_mode="poll",
            source_poll_ms=int(payload.get("source_poll_ms") or DEFAULT_SOURCE_POLL_MS),
            command=str(
                payload.get("monitor_command")
                or f"cli-anything-freecad preview live monitor --session-dir {session_path}"
            ),
            publish_reason="auto-poll",
        )
        _write_live_session_updates(
            session_path,
            {
                "poller": {
                    "pid": os.getpid(),
                    "running": True,
                    "last_heartbeat": now,
                    "last_capture_status": "ok",
                    "last_capture_finished_at": _now_iso(),
                },
                "source_state": {
                    "last_seen_fingerprint": current_fingerprint,
                    "last_rendered_fingerprint": current_fingerprint,
                    "last_rendered_at": _now_iso(),
                    "last_error": None,
                    "last_error_at": None,
                },
            },
        )
        return {
            "action": "captured",
            "bundle_id": live_payload.get("current_bundle_id"),
            "fingerprint": current_fingerprint,
        }
    except Exception as exc:
        _write_live_session_updates(
            session_path,
            {
                "poller": {
                    "pid": os.getpid(),
                    "running": True,
                    "last_heartbeat": now,
                    "last_capture_status": "error",
                    "last_capture_error": str(exc),
                    "last_capture_error_at": _now_iso(),
                },
                "source_state": {
                    "last_seen_fingerprint": current_fingerprint,
                    "last_error": str(exc),
                    "last_error_at": _now_iso(),
                },
            },
        )
        return {
            "action": "error",
            "error": str(exc),
            "fingerprint": current_fingerprint,
        }
