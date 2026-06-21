# ruff: noqa: F403, F405, E501
from .mubu_probe_base import *  # noqa: F403
# fmt: off
from .mubu_probe_p1 import DEFAULT_LOG_ROOT, NET_REQUEST_RE, STORE_SET_RE, TIMESTAMP_RE  # noqa: E402,E501
from .mubu_probe_p2 import numeric_values, parse_event_timestamp_ms, timestamp_ms_to_iso  # noqa: E402,E501
from .mubu_probe_p3 import build_folder_indexes  # noqa: E402,E501
# fmt: on


def parse_client_sync_line(line: str) -> dict[str, Any] | None:
    timestamp_match = TIMESTAMP_RE.search(line)
    timestamp = timestamp_match.group("timestamp") if timestamp_match else None

    request_match = NET_REQUEST_RE.search(line)
    if request_match:
        payload = json.loads(request_match.group("payload"))
        data = payload.get("data") or {}
        if payload.get("pathname") == "/v3/api/colla/events":
            return {
                "timestamp": timestamp,
                "kind": "change_request" if data.get("type") == "CHANGE" else "colla_request",
                "pathname": payload.get("pathname"),
                "document_id": data.get("documentId"),
                "member_id": data.get("memberId"),
                "event_type": data.get("type"),
                "version": data.get("version"),
                "payload": payload,
            }

    store_match = STORE_SET_RE.search(line)
    if store_match:
        payload = json.loads(store_match.group("payload"))
        if payload.get("cachedChangeset") or payload.get("unAckChangeset"):
            return {
                "timestamp": timestamp,
                "kind": "store_set",
                "document_id": store_match.group("doc_id"),
                "cached_changeset": payload.get("cachedChangeset", []),
                "unack_changeset": payload.get("unAckChangeset", []),
                "payload": payload,
            }

    return None
def iter_log_files(log_root: Path) -> list[Path]:
    files = sorted(log_root.glob("client-sync*.log*"), key=lambda path: path.stat().st_mtime, reverse=True)
    return files
def read_log_text(path: Path) -> str:
    if path.suffix == ".gz":
        with gzip.open(path, "rt", errors="replace") as handle:
            return handle.read()
    return path.read_text(errors="replace")
def load_change_events(log_root: Path = DEFAULT_LOG_ROOT, doc_id: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    if not log_root.exists():
        return events

    for path in iter_log_files(log_root):
        for line in read_log_text(path).splitlines():
            parsed = parse_client_sync_line(line)
            if not parsed:
                continue
            if doc_id and parsed.get("document_id") != doc_id:
                continue
            parsed = {"source_file": str(path), **parsed}
            events.append(parsed)

    events.sort(key=lambda item: item.get("timestamp") or "", reverse=True)
    if limit is not None:
        events = events[:limit]
    return events
def recent_documents(
    backups: Iterable[dict[str, Any]],
    document_metas: Iterable[dict[str, Any]],
    folders: Iterable[dict[str, Any]],
    log_root: Path = DEFAULT_LOG_ROOT,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    folder_by_id, folder_paths = build_folder_indexes(folders)
    activity: dict[str, dict[str, Any]] = {}

    for backup in backups:
        doc_id = backup["doc_id"]
        item = activity.setdefault(doc_id, {"doc_id": doc_id})
        item.setdefault("title", backup.get("title"))
        item["backup_file"] = backup.get("backup_file")
        item["backup_modified_at"] = backup.get("modified_at")

    for meta in document_metas:
        doc_id = meta["doc_id"]
        item = activity.setdefault(doc_id, {"doc_id": doc_id})
        item["title"] = meta.get("title") or item.get("title")
        item["folder_id"] = meta.get("folder_id")
        item["folder_path"] = folder_paths.get(meta.get("folder_id", ""), "")
        item["created_at"] = meta.get("created_at")
        item["updated_at"] = meta.get("updated_at")
        item["word_count"] = meta.get("word_count")

    for event in load_change_events(log_root=log_root, limit=None):
        doc_id = event.get("document_id")
        if not doc_id:
            continue
        item = activity.setdefault(doc_id, {"doc_id": doc_id})
        event_ts = parse_event_timestamp_ms(event.get("timestamp"))
        current = item.get("last_event_at")
        if event_ts is not None and (current is None or event_ts >= current):
            item["last_event_at"] = event_ts
            item["last_event_at_iso"] = event.get("timestamp")
            item["last_event_type"] = event.get("event_type")

    recent = list(activity.values())
    for item in recent:
        item["sort_ts"] = max(
            numeric_values(
                item.get("last_event_at"),
                item.get("updated_at"),
                item.get("backup_modified_at"),
                item.get("created_at"),
            ),
            default=0,
        )
        folder_id = item.get("folder_id")
        if folder_id and "folder_path" not in item:
            item["folder_path"] = folder_paths.get(folder_id, "")
        if item.get("created_at") is not None:
            item["created_at_iso"] = timestamp_ms_to_iso(item.get("created_at"))
        if item.get("updated_at") is not None:
            item["updated_at_iso"] = timestamp_ms_to_iso(item.get("updated_at"))
        if item.get("backup_modified_at") is not None:
            item["backup_modified_at_iso"] = timestamp_ms_to_iso(int(item.get("backup_modified_at") * 1000))

    recent.sort(key=lambda item: item.get("sort_ts", 0), reverse=True)
    if limit is not None:
        recent = recent[:limit]
    return recent
