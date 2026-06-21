# ruff: noqa: F403, F405, E501
from .imports_base import *  # noqa: F403

# fmt: off
from .imports_p1 import _normalize_attachment_int, _read_json_payload  # noqa: E402,E501
# fmt: on


def _normalize_attachment_descriptor(
    raw: Any,
    *,
    index_label: str,
    attachment_label: str,
    default_delay_ms: int,
    default_timeout: int,
) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise RuntimeError(f"{index_label} {attachment_label} must be an object")
    has_path = "path" in raw and raw.get("path") not in (None, "")
    has_url = "url" in raw and raw.get("url") not in (None, "")
    if has_path == has_url:
        raise RuntimeError(
            f"{index_label} {attachment_label} must include exactly one of `path` or `url`"
        )
    title = str(raw.get("title") or "PDF").strip() or "PDF"
    delay_ms = _normalize_attachment_int(
        raw.get("delay_ms", default_delay_ms), name="delay_ms", minimum=0
    )
    timeout = _normalize_attachment_int(
        raw.get("timeout", default_timeout), name="timeout", minimum=1
    )
    if has_path:
        source = str(raw["path"]).strip()
        if not source:
            raise RuntimeError(
                f"{index_label} {attachment_label} path must not be empty"
            )
        return {
            "source_type": "file",
            "source": source,
            "title": title,
            "delay_ms": delay_ms,
            "timeout": timeout,
        }
    source = str(raw["url"]).strip()
    if not source:
        raise RuntimeError(f"{index_label} {attachment_label} url must not be empty")
    return {
        "source_type": "url",
        "source": source,
        "title": title,
        "delay_ms": delay_ms,
        "timeout": timeout,
    }


def _extract_inline_attachment_plans(
    items: list[dict[str, Any]],
    *,
    default_delay_ms: int,
    default_timeout: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    stripped_items: list[dict[str, Any]] = []
    plans: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        copied = dict(item)
        raw_attachments = copied.pop("attachments", [])
        if raw_attachments in (None, []):
            stripped_items.append(copied)
            continue
        if not isinstance(raw_attachments, list):
            raise RuntimeError(
                f"JSON import item {index + 1} attachments must be an array"
            )
        normalized = [
            _normalize_attachment_descriptor(
                descriptor,
                index_label=f"JSON import item {index + 1}",
                attachment_label=f"attachment {attachment_index + 1}",
                default_delay_ms=default_delay_ms,
                default_timeout=default_timeout,
            )
            for attachment_index, descriptor in enumerate(raw_attachments)
        ]
        plans.append({"index": index, "attachments": normalized})
        stripped_items.append(copied)
    return stripped_items, plans


def _read_attachment_manifest(
    path: Path,
    *,
    default_delay_ms: int,
    default_timeout: int,
) -> list[dict[str, Any]]:
    payload = _read_json_payload(path, label="attachment manifest")
    if not isinstance(payload, list):
        raise RuntimeError(
            "Attachment manifest expects an array of {index, attachments} objects"
        )
    manifest: list[dict[str, Any]] = []
    seen_indexes: set[int] = set()
    for entry_index, entry in enumerate(payload, start=1):
        label = f"manifest entry {entry_index}"
        if not isinstance(entry, dict):
            raise RuntimeError(f"{label} must be an object")
        if "index" not in entry:
            raise RuntimeError(f"{label} is missing required `index`")
        index = _normalize_attachment_int(entry["index"], name="index", minimum=0)
        if index in seen_indexes:
            raise RuntimeError(f"{label} reuses import index {index}")
        seen_indexes.add(index)
        attachments = entry.get("attachments")
        if not isinstance(attachments, list):
            raise RuntimeError(f"{label} attachments must be an array")
        normalized = [
            _normalize_attachment_descriptor(
                descriptor,
                index_label=label,
                attachment_label=f"attachment {attachment_index + 1}",
                default_delay_ms=default_delay_ms,
                default_timeout=default_timeout,
            )
            for attachment_index, descriptor in enumerate(attachments)
        ]
        expected_title = entry.get("expected_title")
        if expected_title is not None and not isinstance(expected_title, str):
            raise RuntimeError(f"{label} expected_title must be a string")
        manifest.append(
            {
                "index": index,
                "expected_title": expected_title,
                "attachments": normalized,
            }
        )
    return manifest


def _item_title(item: dict[str, Any]) -> str | None:
    for field in ("title", "bookTitle", "publicationTitle"):
        value = item.get(field)
        if value:
            return str(value)
    return None


def _normalize_url_for_dedupe(url: str) -> str:
    parsed = urllib.parse.urlsplit(url.strip())
    normalized_path = parsed.path or "/"
    return urllib.parse.urlunsplit(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            normalized_path,
            parsed.query,
            "",
        )
    )
