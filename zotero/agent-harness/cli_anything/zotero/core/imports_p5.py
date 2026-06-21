# ruff: noqa: F403, F405, E501
from .imports_base import *  # noqa: F403

# fmt: off
from .imports_p1 import _normalize_tags, _read_text_file, _require_connector, _resolve_target, _session_id  # noqa: E402,E501
from .imports_p2 import _read_attachment_manifest  # noqa: E402,E501
from .imports_p4 import _perform_attachment_upload  # noqa: E402,E501
# fmt: on


def enable_local_api(
    runtime: RuntimeContext,
    *,
    launch: bool = False,
    wait_timeout: int = 30,
) -> dict[str, Any]:
    profile_dir = runtime.environment.profile_dir
    if profile_dir is None:
        raise RuntimeError("Active Zotero profile could not be resolved")
    before = runtime.environment.local_api_enabled_configured
    written_path = runtime.environment.profile_dir / "user.js"
    from cli_anything.zotero.utils import zotero_paths  # local import to avoid cycle

    zotero_paths.ensure_local_api_enabled(profile_dir)
    payload = {
        "profile_dir": str(profile_dir),
        "user_js_path": str(written_path),
        "already_enabled": before,
        "enabled": True,
        "launched": False,
        "connector_ready": runtime.connector_available,
        "local_api_ready": runtime.local_api_available,
    }
    if launch:
        from cli_anything.zotero.core import discovery  # local import to avoid cycle

        refreshed = discovery.build_runtime_context(
            backend=runtime.backend,
            data_dir=str(runtime.environment.data_dir),
            profile_dir=str(profile_dir),
            executable=str(runtime.environment.executable)
            if runtime.environment.executable
            else None,
        )
        launch_payload = discovery.launch_zotero(refreshed, wait_timeout=wait_timeout)
        payload.update(
            {
                "launched": True,
                "launch": launch_payload,
                "connector_ready": launch_payload["connector_ready"],
                "local_api_ready": launch_payload["local_api_ready"],
            }
        )
    return payload


def import_file(
    runtime: RuntimeContext,
    path: str | Path,
    *,
    collection_ref: str | None = None,
    tags: list[str] | tuple[str, ...] = (),
    session: dict[str, Any] | None = None,
    attachments_manifest: str | Path | None = None,
    attachment_delay_ms: int = 0,
    attachment_timeout: int = 60,
) -> dict[str, Any]:
    _require_connector(runtime)
    source_path = Path(path).expanduser()
    if not source_path.exists():
        raise FileNotFoundError(f"Import file not found: {source_path}")
    content = _read_text_file(source_path)
    manifest_path = (
        Path(attachments_manifest).expanduser()
        if attachments_manifest is not None
        else None
    )
    plans = (
        _read_attachment_manifest(
            manifest_path,
            default_delay_ms=attachment_delay_ms,
            default_timeout=attachment_timeout,
        )
        if manifest_path is not None
        else []
    )
    session_id = _session_id("import-file")
    imported = zotero_http.connector_import_text(
        runtime.environment.port, content, session_id=session_id
    )
    target = _resolve_target(runtime, collection_ref, session=session)
    normalized_tags = _normalize_tags(list(tags))
    zotero_http.connector_update_session(
        runtime.environment.port,
        session_id=session_id,
        target=target["treeViewID"],
        tags=normalized_tags,
    )
    attachment_summary, attachment_results = _perform_attachment_upload(
        runtime,
        session_id=session_id,
        connector_items=imported,
        plans=plans,
    )
    return {
        "action": "import_file",
        "path": str(source_path),
        "status": "partial_success"
        if attachment_summary["failed_count"]
        else "success",
        "sessionID": session_id,
        "target": target,
        "tags": normalized_tags,
        "imported_count": len(imported),
        "items": imported,
        "attachment_summary": attachment_summary,
        "attachment_results": attachment_results,
    }
