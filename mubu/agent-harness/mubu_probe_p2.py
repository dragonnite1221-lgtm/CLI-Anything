# ruff: noqa: F403, F405, E501
from .mubu_probe_base import *  # noqa: F403


def post_json(
    url: str,
    payload: dict[str, Any],
    headers: dict[str, str],
    timeout: int = 20,
) -> dict[str, Any]:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} for {url}: {body[:500]}") from exc
    except URLError as exc:
        raise RuntimeError(f"request failed for {url}: {exc}") from exc

    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid JSON response from {url}: {body[:500]}") from exc
def parse_revision_generation(revision: str | None) -> int:
    if not revision:
        return 0
    head, _, _ = revision.partition("-")
    try:
        return int(head)
    except ValueError:
        return 0
def numeric_values(*values: Any) -> list[int]:
    result: list[int] = []
    for value in values:
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            result.append(value)
    return result
def timestamp_ms_to_iso(value: int | None) -> str | None:
    if value is None:
        return None
    return datetime.fromtimestamp(value / 1000, tz=timezone.utc).astimezone().isoformat(timespec="seconds")
def normalized_lookup_key(value: str | None) -> str:
    return (value or "").strip().casefold()
def parse_event_timestamp_ms(value: str | None) -> int | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None
    return int(dt.timestamp() * 1000)
def iter_json_objects_from_text(text: str) -> Iterable[dict[str, Any]]:
    decoder = JSONDecoder()
    cursor = 0
    while True:
        start = text.find('{"', cursor)
        if start == -1:
            break
        try:
            obj, consumed = decoder.raw_decode(text[start:])
        except Exception:
            cursor = start + 2
            continue
        if isinstance(obj, dict):
            yield obj
        cursor = start + consumed
def iter_storage_collection_files(storage_root: Path, pattern: str) -> Iterable[Path]:
    for path in sorted(storage_root.glob(pattern)):
        if path.is_file() and path.suffix in {".ldb", ".log"}:
            yield path
def load_collection_records(
    storage_root: Path,
    pattern: str,
    predicate,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in iter_storage_collection_files(storage_root, pattern):
        text = path.read_text(errors="ignore")
        for obj in iter_json_objects_from_text(text):
            if predicate(obj):
                records.append(obj)
    return records
def dedupe_latest_records(
    records: Iterable[dict[str, Any]],
    id_field: str = "id",
    timestamp_fields: Iterable[str] = (),
) -> list[dict[str, Any]]:
    latest_by_id: dict[str, dict[str, Any]] = {}
    timestamp_fields = tuple(timestamp_fields)

    def sort_key(item: dict[str, Any]) -> tuple[int, int]:
        return (
            parse_revision_generation(item.get("_rev") or item.get("rev")),
            max(numeric_values(*(item.get(field) for field in timestamp_fields)), default=0),
        )

    for record in records:
        record_id = record.get(id_field)
        if not isinstance(record_id, (str, int)):
            continue
        record_key = str(record_id)
        current = latest_by_id.get(record_key)
        if current is None or sort_key(record) >= sort_key(current):
            latest_by_id[record_key] = record

    return list(latest_by_id.values())
def parse_child_refs(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if not isinstance(value, str) or not value:
        return []
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return []
    if isinstance(parsed, list):
        return [item for item in parsed if isinstance(item, dict)]
    return []
