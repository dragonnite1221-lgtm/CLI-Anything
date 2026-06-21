# ruff: noqa: F403, F405, E501
from .zotero_sqlite_base import *  # noqa: F403

# fmt: off
from .zotero_sqlite_p1 import AmbiguousReferenceError, _as_dicts, _is_numeric_ref, _timestamp_text, backup_database, connect_readonly, connect_writable, generate_object_key  # noqa: E402,E501
from .zotero_sqlite_p2 import resolve_collection  # noqa: E402,E501
from .zotero_sqlite_p3 import fetch_items  # noqa: E402,E501
from .zotero_sqlite_p4 import fetch_saved_searches  # noqa: E402,E501
# fmt: on


def resolve_saved_search(
    sqlite_path: Path | str, ref: str | int, *, library_id: int | None = None
) -> Optional[dict[str, Any]]:
    searches = fetch_saved_searches(sqlite_path, library_id=library_id)
    if _is_numeric_ref(ref):
        for search in searches:
            if str(search["savedSearchID"]) == str(ref):
                return search
        return None

    matches = [search for search in searches if search["key"] == str(ref)]
    if not matches:
        return None
    if len(matches) > 1 and library_id is None:
        libraries = sorted({int(search["libraryID"]) for search in matches})
        library_text = ", ".join(
            f"L{library_id_value}" for library_id_value in libraries
        )
        raise AmbiguousReferenceError(
            f"Ambiguous saved search reference: {ref}. Matches found in {library_text}. "
            "Set the library with `session use-library <id>` and retry."
        )
    return matches[0]


def fetch_tags(
    sqlite_path: Path | str, library_id: int | None = None
) -> list[dict[str, Any]]:
    with closing(connect_readonly(sqlite_path)) as conn:
        rows = conn.execute(
            """
            SELECT t.tagID, t.name, COUNT(it.itemID) AS itemCount
            FROM tags t
            JOIN itemTags it ON it.tagID = t.tagID
            JOIN items i ON i.itemID = it.itemID
            WHERE (? IS NULL OR i.libraryID = ?)
            GROUP BY t.tagID, t.name
            ORDER BY t.name COLLATE NOCASE
            """,
            (library_id, library_id),
        ).fetchall()
    return _as_dicts(rows)


def fetch_tag_items(
    sqlite_path: Path | str, tag_ref: str | int, library_id: int | None = None
) -> list[dict[str, Any]]:
    tag_name: str | None = None
    with closing(connect_readonly(sqlite_path)) as conn:
        if _is_numeric_ref(tag_ref):
            row = conn.execute(
                "SELECT name FROM tags WHERE tagID = ?", (int(tag_ref),)
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT name FROM tags WHERE name = ?", (str(tag_ref),)
            ).fetchone()
        if row:
            tag_name = row["name"]
    if tag_name is None:
        return []
    return fetch_items(sqlite_path, library_id=library_id, tag=tag_name)


def create_collection_record(
    sqlite_path: Path | str,
    *,
    name: str,
    library_id: int,
    parent_collection_id: int | None = None,
) -> dict[str, Any]:
    if not name.strip():
        raise RuntimeError("Collection name must not be empty")
    backup_path = backup_database(sqlite_path)
    timestamp = _timestamp_text()
    with closing(connect_writable(sqlite_path)) as conn:
        try:
            conn.execute("BEGIN IMMEDIATE")
            cursor = conn.execute(
                """
                INSERT INTO collections (
                    collectionName,
                    parentCollectionID,
                    clientDateModified,
                    libraryID,
                    key,
                    version,
                    synced
                )
                VALUES (?, ?, ?, ?, ?, 0, 0)
                """,
                (
                    name.strip(),
                    parent_collection_id,
                    timestamp,
                    int(library_id),
                    generate_object_key(),
                ),
            )
            collection_id = int(cursor.lastrowid)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    created = resolve_collection(sqlite_path, collection_id)
    assert created is not None
    created["backupPath"] = str(backup_path)
    return created


def add_item_to_collection_record(
    sqlite_path: Path | str,
    *,
    item_id: int,
    collection_id: int,
) -> dict[str, Any]:
    backup_path = backup_database(sqlite_path)
    with closing(connect_writable(sqlite_path)) as conn:
        try:
            conn.execute("BEGIN IMMEDIATE")
            existing = conn.execute(
                "SELECT 1 FROM collectionItems WHERE collectionID = ? AND itemID = ?",
                (int(collection_id), int(item_id)),
            ).fetchone()
            created = False
            order_index = None
            if not existing:
                row = conn.execute(
                    "SELECT COALESCE(MAX(orderIndex), -1) + 1 AS nextIndex FROM collectionItems WHERE collectionID = ?",
                    (int(collection_id),),
                ).fetchone()
                order_index = int(row["nextIndex"]) if row else 0
                conn.execute(
                    "INSERT INTO collectionItems (collectionID, itemID, orderIndex) VALUES (?, ?, ?)",
                    (int(collection_id), int(item_id), order_index),
                )
                created = True
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    return {
        "backupPath": str(backup_path),
        "created": created,
        "collectionID": int(collection_id),
        "itemID": int(item_id),
        "orderIndex": order_index,
    }
