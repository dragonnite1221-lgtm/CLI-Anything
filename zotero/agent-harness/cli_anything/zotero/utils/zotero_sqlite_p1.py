# ruff: noqa: F403, F405, E501
from .zotero_sqlite_base import *  # noqa: F403


class AmbiguousReferenceError(RuntimeError):
    """Raised when a bare Zotero key matches records in multiple libraries."""


def connect_readonly(sqlite_path: Path | str) -> sqlite3.Connection:
    path = Path(sqlite_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Zotero database not found: {path}")
    uri = f"file:{path.as_posix()}?mode=ro&immutable=1"
    connection = sqlite3.connect(uri, uri=True, timeout=1.0)
    connection.row_factory = sqlite3.Row
    return connection


def connect_writable(sqlite_path: Path | str) -> sqlite3.Connection:
    path = Path(sqlite_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Zotero database not found: {path}")
    connection = sqlite3.connect(path, timeout=30.0)
    connection.row_factory = sqlite3.Row
    return connection


def _as_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


def _is_numeric_ref(value: Any) -> bool:
    try:
        int(str(value))
        return True
    except (TypeError, ValueError):
        return False


def normalize_library_ref(library_ref: str | int) -> int:
    text = str(library_ref).strip()
    if not text:
        raise RuntimeError("Library reference must not be empty")
    upper = text.upper()
    if upper.startswith("L") and upper[1:].isdigit():
        return int(upper[1:])
    if text.isdigit():
        return int(text)
    raise RuntimeError(f"Unsupported library reference: {library_ref}")


def _timestamp_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def generate_object_key(length: int = 8) -> str:
    chooser = random.SystemRandom()
    return "".join(chooser.choice(KEY_ALPHABET) for _ in range(length))


def backup_database(sqlite_path: Path | str) -> Path:
    source = Path(sqlite_path).resolve()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    backup = source.with_name(f"{source.stem}.backup-{timestamp}{source.suffix}")
    shutil.copy2(source, backup)
    return backup


def note_html_to_text(note_html: str | None) -> str:
    if not note_html:
        return ""
    text = re.sub(r"(?i)<br\s*/?>", "\n", note_html)
    text = re.sub(r"(?i)</p\s*>", "\n\n", text)
    text = re.sub(r"(?i)</div\s*>", "\n", text)
    text = _TAG_RE.sub("", text)
    text = html.unescape(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def note_preview(note_html: str | None, limit: int = NOTE_PREVIEW_LENGTH) -> str:
    text = note_html_to_text(note_html)
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def fetch_libraries(sqlite_path: Path | str) -> list[dict[str, Any]]:
    with closing(connect_readonly(sqlite_path)) as conn:
        rows = conn.execute(
            """
            SELECT libraryID, type, editable, filesEditable, version, storageVersion, lastSync, archived
            FROM libraries
            ORDER BY libraryID
            """
        ).fetchall()
    return _as_dicts(rows)


def resolve_library(
    sqlite_path: Path | str, ref: str | int
) -> Optional[dict[str, Any]]:
    library_id = normalize_library_ref(ref)
    with closing(connect_readonly(sqlite_path)) as conn:
        row = conn.execute(
            """
            SELECT libraryID, type, editable, filesEditable, version, storageVersion, lastSync, archived
            FROM libraries
            WHERE libraryID = ?
            """,
            (library_id,),
        ).fetchone()
    return dict(row) if row else None


def default_library_id(sqlite_path: Path | str) -> Optional[int]:
    libraries = fetch_libraries(sqlite_path)
    if not libraries:
        return None
    for library in libraries:
        if library["type"] == "user":
            return int(library["libraryID"])
    return int(libraries[0]["libraryID"])


def fetch_collections(
    sqlite_path: Path | str, library_id: int | None = None
) -> list[dict[str, Any]]:
    with closing(connect_readonly(sqlite_path)) as conn:
        rows = conn.execute(
            """
            SELECT
                c.collectionID,
                c.key,
                c.collectionName,
                c.parentCollectionID,
                c.libraryID,
                c.version,
                COUNT(ci.itemID) AS itemCount
            FROM collections c
            LEFT JOIN collectionItems ci ON ci.collectionID = c.collectionID
            WHERE (? IS NULL OR c.libraryID = ?)
            GROUP BY c.collectionID, c.key, c.collectionName, c.parentCollectionID, c.libraryID, c.version
            ORDER BY c.collectionName COLLATE NOCASE
            """,
            (library_id, library_id),
        ).fetchall()
    return _as_dicts(rows)
