# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403

# fmt: off
from .preview_p1 import _live_session_dir, _load_existing_live_session, _normalize_poll_ms, _now_iso, _pid_is_running, _project_file_fingerprint, _with_live_refs, _write_json  # noqa: E402,E501
from .preview_p2 import _history_item, _update_current_symlink  # noqa: E402,E501
# fmt: on


def latest(
    *,
    project_path: Optional[str] = None,
    recipe: Optional[str] = None,
    root_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Return the latest preview bundle manifest for FreeCAD."""
    manifest = find_latest_manifest(
        software="freecad",
        recipe=recipe,
        bundle_kind="capture",
        project_path=project_path,
        root_dir=root_dir,
    )
    if manifest is None:
        raise FileNotFoundError("No FreeCAD preview bundle found")
    return manifest


def _publish_live_session(
    session: Session,
    bundle_manifest: Dict[str, Any],
    *,
    recipe: str,
    root_dir: Optional[str] = None,
    refresh_hint_ms: int = DEFAULT_REFRESH_HINT_MS,
    live_mode: Optional[str] = None,
    source_poll_ms: int = DEFAULT_SOURCE_POLL_MS,
    publish_reason: str = "manual",
    command: Optional[str] = None,
) -> Dict[str, Any]:
    session_dir = _live_session_dir(session, recipe, root_dir=root_dir)
    session_dir.mkdir(parents=True, exist_ok=True)
    _update_current_symlink(session_dir, bundle_manifest["_bundle_dir"])

    existing = _load_existing_live_session(session_dir)
    now = _now_iso()
    project = session.get_project()
    trajectory = append_live_trajectory(
        session_dir,
        software="freecad",
        recipe=recipe,
        bundle_manifest=bundle_manifest,
        publish_reason=publish_reason,
        project_path=session.project_path,
        project_name=Path(session.project_path).name
        if session.project_path
        else project.get("name", "Untitled"),
        session_name=session_dir.name,
        command=command,
        command_started_at=now,
        command_finished_at=now,
    )
    current_item = dict(trajectory.get("latest_step") or _history_item(bundle_manifest))
    history = [current_item]
    for item in existing.get("history", []):
        if item.get("bundle_id") == current_item["bundle_id"]:
            continue
        history.append(item)
    history = history[:12]

    current_live_mode = live_mode or existing.get("live_mode") or "manual"
    current_source_poll_ms = _normalize_poll_ms(
        source_poll_ms
        if live_mode is not None or "source_poll_ms" not in existing
        else existing.get("source_poll_ms")
    )
    root_flag = f" --root-dir {root_dir}" if root_dir else ""
    project_flag = f" -p {session.project_path}" if session.project_path else ""
    poller = dict(existing.get("poller") or {})
    poller["running"] = _pid_is_running(poller.get("pid"))
    project_file_fingerprint = _project_file_fingerprint(session.project_path)
    source_state = dict(existing.get("source_state") or {})
    if session.project_path:
        source_state["source_type"] = "project-file"
        source_state["project_path"] = session.project_path
    source_state["project_name"] = project.get("name")
    if project_file_fingerprint:
        source_state["last_seen_fingerprint"] = project_file_fingerprint
        source_state["last_rendered_fingerprint"] = project_file_fingerprint
        source_state["last_rendered_at"] = now
    source_state["last_publish_reason"] = publish_reason
    trajectory_rel = os.path.relpath(
        Path(trajectory["_trajectory_path"]).resolve(), session_dir
    )

    payload = {
        "protocol_version": LIVE_PROTOCOL_VERSION,
        "software": "freecad",
        "recipe": recipe,
        "status": "active",
        "live_mode": current_live_mode,
        "session_name": session_dir.name,
        "project_path": session.project_path,
        "project_name": Path(session.project_path).name
        if session.project_path
        else project.get("name", "Untitled"),
        "created_at": existing.get("created_at", now),
        "updated_at": now,
        "refresh_hint_ms": int(refresh_hint_ms),
        "source_poll_ms": current_source_poll_ms,
        "preview_root_dir": root_dir,
        "current_link": "current",
        "current_bundle_id": bundle_manifest.get("bundle_id"),
        "current_bundle_dir": bundle_manifest.get("_bundle_dir"),
        "current_manifest_path": bundle_manifest.get("_manifest_path"),
        "current_summary_path": bundle_manifest.get("_summary_path"),
        "current_cached": bool(bundle_manifest.get("cached")),
        "bundle_count": len(history),
        "history": history,
        "trajectory_path": trajectory_rel,
        "trajectory_protocol_version": trajectory.get("protocol_version"),
        "trajectory_step_count": trajectory.get("step_count", 0),
        "current_step_id": trajectory.get("current_step_id"),
        "latest_command": current_item.get("command"),
        "latest_publish_reason": current_item.get("publish_reason", publish_reason),
        "source_state": source_state,
        "poller": poller,
        "publish_command": (
            f"cli-anything-freecad{project_flag} preview live push --recipe {recipe}{root_flag}"
        ).strip(),
        "watch_command": (
            f"cli-hub previews watch {session_dir} --open --poll-ms {int(refresh_hint_ms)}"
        ),
        "inspect_command": f"cli-hub previews inspect {session_dir}",
        "html_command": f"cli-hub previews html {session_dir}",
        "start_command": (
            f"cli-anything-freecad{project_flag} preview live start --recipe {recipe} "
            f"--mode {current_live_mode} --source-poll-ms {current_source_poll_ms}{root_flag}"
        ).strip(),
        "monitor_command": (
            f"cli-anything-freecad preview live monitor --session-dir {session_dir}"
        ),
    }
    _write_json(session_dir / "session.json", payload)
    return _with_live_refs(session_dir, payload)
