# ruff: noqa: F403, F405, E402, F401, E501
from .preview_base import *
from .preview_p1 import (
    _live_session_dir,
    _now_iso,
    _pid_is_running,
    _read_json,
    _terminate_pid,
    _with_live_refs,
    _write_json,
)
from .preview_p3 import capture
from .preview_p5 import _publish_live_session

from . import preview_base as _coupbase  # noqa: E402


def live_start(
    session: Session,
    recipe: str = "quick",
    *,
    root_dir: Optional[str] = None,
    force: bool = False,
    refresh_hint_ms: int = DEFAULT_REFRESH_HINT_MS,
    live_mode: str = "poll",
    source_poll_ms: int = DEFAULT_SOURCE_POLL_MS,
    command: Optional[str] = None,
    publish_reason: str = "live-start",
) -> Dict[str, Any]:
    """Capture a preview and publish it into a live session."""
    if live_mode not in {"poll", "manual"}:
        raise ValueError("live_mode must be 'poll' or 'manual'")
    if live_mode == "poll" and (not session.project_path):
        raise RuntimeError("Poll mode requires a saved project path")
    bundle_manifest = _coupbase._COUP_GLOBALS["capture"](
        session, recipe=recipe, root_dir=root_dir, force=force, command=command
    )
    live_payload = _publish_live_session(
        session,
        bundle_manifest,
        recipe=recipe,
        root_dir=root_dir,
        refresh_hint_ms=refresh_hint_ms,
        live_mode=live_mode,
        source_poll_ms=source_poll_ms,
        publish_reason=publish_reason,
        command=command,
    )
    live_payload["bundle"] = {
        "bundle_id": bundle_manifest.get("bundle_id"),
        "bundle_dir": bundle_manifest.get("_bundle_dir"),
        "manifest_path": bundle_manifest.get("_manifest_path"),
        "cached": bool(bundle_manifest.get("cached")),
    }
    return live_payload


def live_status(
    session: Session, recipe: str = "quick", *, root_dir: Optional[str] = None
) -> Dict[str, Any]:
    """Return the live session metadata for the active project."""
    session_dir = _live_session_dir(session, recipe, root_dir=root_dir)
    session_path = session_dir / "session.json"
    if not session_path.is_file():
        raise FileNotFoundError("No Blender live preview session found")
    payload = _read_json(session_path)
    poller = dict(payload.get("poller") or {})
    if poller:
        poller["running"] = _pid_is_running(poller.get("pid"))
        payload["poller"] = poller
    trajectory = load_live_trajectory(session_dir)
    if trajectory:
        payload["trajectory_summary"] = summarize_trajectory(trajectory)
    return _with_live_refs(session_dir, payload)


def live_push(
    session: Session,
    recipe: str = "quick",
    *,
    root_dir: Optional[str] = None,
    force: bool = False,
    refresh_hint_ms: int = DEFAULT_REFRESH_HINT_MS,
    source_poll_ms: Optional[int] = None,
    command: Optional[str] = None,
    publish_reason: str = "manual-push",
) -> Dict[str, Any]:
    """Publish a fresh preview bundle into the current live session."""
    existing_mode = "manual"
    existing_source_poll_ms = DEFAULT_SOURCE_POLL_MS
    try:
        existing = live_status(session, recipe=recipe, root_dir=root_dir)
        existing_mode = existing.get("live_mode") or "manual"
        existing_source_poll_ms = int(
            existing.get("source_poll_ms") or DEFAULT_SOURCE_POLL_MS
        )
    except FileNotFoundError:
        pass
    return live_start(
        session,
        recipe=recipe,
        root_dir=root_dir,
        force=force,
        refresh_hint_ms=refresh_hint_ms,
        live_mode=existing_mode,
        source_poll_ms=int(source_poll_ms or existing_source_poll_ms),
        command=command,
        publish_reason=publish_reason,
    )


def live_stop(
    session: Session, recipe: str = "quick", *, root_dir: Optional[str] = None
) -> Dict[str, Any]:
    """Mark a live preview session as stopped while preserving its latest bundle."""
    payload = live_status(session, recipe=recipe, root_dir=root_dir)
    now = _coupbase._COUP_GLOBALS["_now_iso"]()
    poller = dict(payload.get("poller") or {})
    terminated = _terminate_pid(poller.get("pid"))
    poller["running"] = False
    poller["stopped_at"] = now
    poller["last_exit_reason"] = "manual-stop"
    poller["terminated"] = terminated
    payload["status"] = "stopped"
    payload["stopped_at"] = now
    payload["poller"] = poller
    session_dir = Path(payload["_session_dir"])
    _write_json(
        session_dir / "session.json",
        {k: v for k, v in payload.items() if not k.startswith("_")},
    )
    return _with_live_refs(session_dir, payload)
