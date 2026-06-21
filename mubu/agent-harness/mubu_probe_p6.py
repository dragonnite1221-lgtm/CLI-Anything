# ruff: noqa: F403, F405, E501
from .mubu_probe_base import *  # noqa: F403
# fmt: off
from .mubu_probe_p1 import DAILY_TITLE_PATTERNS, DEFAULT_API_HOST, DEFAULT_DAILY_EXCLUDE_KEYWORDS, DEFAULT_DAILY_FOLDER_KEYWORDS, DEFAULT_PLATFORM, DEFAULT_PLATFORM_VERSION, DEFAULT_STORAGE_ROOT  # noqa: E402,E501
from .mubu_probe_p2 import dedupe_latest_records, load_collection_records, normalized_lookup_key, numeric_values, parse_event_timestamp_ms, post_json, timestamp_ms_to_iso  # noqa: E402,E501
# fmt: on


def looks_like_daily_title(
    title: str | None,
    exclude_keywords: Iterable[str] = DEFAULT_DAILY_EXCLUDE_KEYWORDS,
) -> bool:
    if not isinstance(title, str):
        return False
    title = title.strip()
    if not title:
        return False
    if not any(pattern.match(title) for pattern in DAILY_TITLE_PATTERNS):
        return False
    lowered = title.casefold()
    return not any(keyword.casefold() in lowered for keyword in exclude_keywords)
def looks_like_daily_folder_name(
    name: str | None,
    keywords: Iterable[str] = DEFAULT_DAILY_FOLDER_KEYWORDS,
) -> bool:
    normalized_name = normalized_lookup_key(name)
    if not normalized_name:
        return False
    return any(keyword.casefold() in normalized_name for keyword in keywords)
def choose_current_daily_document(
    docs: Iterable[dict[str, Any]],
    allow_non_daily_titles: bool = False,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    sorted_docs = sorted(
        docs,
        key=lambda item: max(
            numeric_values(item.get("updated_at"), item.get("created_at")),
            default=0,
        ),
        reverse=True,
    )
    dated_docs = [doc for doc in sorted_docs if looks_like_daily_title(doc.get("title"))]
    candidates = dated_docs if dated_docs else (sorted_docs if allow_non_daily_titles else [])
    return (candidates[0] if candidates else None), candidates
def normalize_user_record(raw: dict[str, Any]) -> dict[str, Any]:
    updated_at = raw.get("|h") if isinstance(raw.get("|h"), int) else None
    return {
        "user_id": str(raw.get("id")),
        "token": raw.get("|u"),
        "display_name": raw.get("|i") or raw.get("|q"),
        "phone": raw.get("|n"),
        "photo": raw.get("|o"),
        "vip_end_date": raw.get("|w"),
        "remember": raw.get("|r"),
        "updated_at": updated_at,
        "updated_at_iso": timestamp_ms_to_iso(updated_at),
        "rev": raw.get("_rev"),
    }
def load_users(storage_root: Path = DEFAULT_STORAGE_ROOT) -> list[dict[str, Any]]:
    records = load_collection_records(
        storage_root,
        "mubu_desktop_app-rxdb-1-users*/*",
        lambda obj: isinstance(obj.get("id"), int) and isinstance(obj.get("|u"), str),
    )
    users = [
        normalize_user_record(record)
        for record in dedupe_latest_records(records, timestamp_fields=["|h"])
    ]
    users.sort(key=lambda item: item.get("updated_at") or 0, reverse=True)
    return users
def get_active_user(storage_root: Path = DEFAULT_STORAGE_ROOT) -> dict[str, Any] | None:
    users = load_users(storage_root)
    return users[0] if users else None
def build_api_headers(
    user: dict[str, Any],
    platform: str = DEFAULT_PLATFORM,
    platform_version: str = DEFAULT_PLATFORM_VERSION,
) -> dict[str, str]:
    return {
        "mubu-desktop": "true",
        "platform": platform,
        "platform-version": platform_version,
        "User-Agent": f"{platform} Mubu Electron",
        "token": user["token"],
        "userId": user["user_id"],
        "Content-Type": "application/json;",
    }
def fetch_user_info(user: dict[str, Any], api_host: str = DEFAULT_API_HOST) -> dict[str, Any]:
    return post_json(
        f"{api_host}/v3/api/user/info",
        {"enhance": True},
        build_api_headers(user),
    )
def fetch_document_versions(user: dict[str, Any], api_host: str = DEFAULT_API_HOST) -> dict[str, int]:
    response = post_json(
        f"{api_host}/v3/api/document/version/list",
        {},
        build_api_headers(user),
    )
    if response.get("code") != 0:
        raise RuntimeError(f"version list failed: {response}")
    return {
        item["docId"]: item["version"]
        for item in response.get("data", [])
        if isinstance(item, dict) and isinstance(item.get("docId"), str)
    }
def fetch_document_remote(doc_id: str, user: dict[str, Any], api_host: str = DEFAULT_API_HOST) -> dict[str, Any]:
    response = post_json(
        f"{api_host}/v3/api/document/get",
        {"docId": doc_id},
        build_api_headers(user),
    )
    if response.get("code") != 0:
        raise RuntimeError(f"document get failed for {doc_id}: {response}")
    return response["data"]
def latest_doc_member_context(events: Iterable[dict[str, Any]], doc_id: str) -> dict[str, Any] | None:
    latest: dict[str, Any] | None = None
    latest_ts = -1
    for event in events:
        if event.get("document_id") != doc_id or not event.get("member_id"):
            continue
        ts = parse_event_timestamp_ms(event.get("timestamp")) or -1
        if ts >= latest_ts:
            latest_ts = ts
            latest = {
                "document_id": doc_id,
                "member_id": event.get("member_id"),
                "last_seen_at": event.get("timestamp"),
                "event_type": event.get("event_type"),
            }
    return latest
