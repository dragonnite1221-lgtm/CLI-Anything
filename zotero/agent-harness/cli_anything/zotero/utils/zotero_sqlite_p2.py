# ruff: noqa: F403, F405, E501
from .zotero_sqlite_base import *  # noqa: F403

# fmt: off
from .zotero_sqlite_p1 import AmbiguousReferenceError, _as_dicts, _is_numeric_ref, connect_readonly  # noqa: E402,E501
# fmt: on


def find_collections(
    sqlite_path: Path | str,
    query: str,
    *,
    library_id: int | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    query = query.strip()
    if not query:
        return []
    needle = query.lower()
    like_query = f"%{needle}%"
    prefix_query = f"{needle}%"
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
            WHERE (? IS NULL OR c.libraryID = ?) AND LOWER(c.collectionName) LIKE ?
            GROUP BY c.collectionID, c.key, c.collectionName, c.parentCollectionID, c.libraryID, c.version
            ORDER BY
                CASE
                    WHEN LOWER(c.collectionName) = ? THEN 0
                    WHEN LOWER(c.collectionName) LIKE ? THEN 1
                    ELSE 2
                END,
                INSTR(LOWER(c.collectionName), ?),
                c.collectionName COLLATE NOCASE,
                c.collectionID
            LIMIT ?
            """,
            (
                library_id,
                library_id,
                like_query,
                needle,
                prefix_query,
                needle,
                int(limit),
            ),
        ).fetchall()
    return _as_dicts(rows)


def build_collection_tree(collections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id: dict[int, dict[str, Any]] = {}
    roots: list[dict[str, Any]] = []
    for collection in collections:
        node = {**collection, "children": []}
        by_id[int(collection["collectionID"])] = node
    for collection in collections:
        node = by_id[int(collection["collectionID"])]
        parent_id = collection["parentCollectionID"]
        if parent_id is None:
            roots.append(node)
            continue
        parent = by_id.get(int(parent_id))
        if parent is None:
            roots.append(node)
        else:
            parent["children"].append(node)
    return roots


def _ambiguous_reference(ref: str | int, kind: str, rows: list[sqlite3.Row]) -> None:
    libraries = sorted(
        {int(row["libraryID"]) for row in rows if "libraryID" in row.keys()}
    )
    library_text = (
        ", ".join(f"L{library_id}" for library_id in libraries) or "multiple libraries"
    )
    raise AmbiguousReferenceError(
        f"Ambiguous {kind} reference: {ref}. Matches found in {library_text}. "
        "Set the library with `session use-library <id>` and retry."
    )


def resolve_collection(
    sqlite_path: Path | str, ref: str | int, *, library_id: int | None = None
) -> Optional[dict[str, Any]]:
    with closing(connect_readonly(sqlite_path)) as conn:
        if _is_numeric_ref(ref):
            row = conn.execute(
                "SELECT collectionID, key, collectionName, parentCollectionID, libraryID, version FROM collections WHERE collectionID = ?",
                (int(ref),),
            ).fetchone()
        else:
            params: list[Any] = [str(ref)]
            sql = "SELECT collectionID, key, collectionName, parentCollectionID, libraryID, version FROM collections WHERE key = ?"
            if library_id is not None:
                sql += " AND libraryID = ?"
                params.append(int(library_id))
            sql += " ORDER BY libraryID, collectionID"
            rows = conn.execute(sql, params).fetchall()
            if not rows:
                return None
            if len(rows) > 1 and library_id is None:
                _ambiguous_reference(ref, "collection", rows)
            row = rows[0]
    return dict(row) if row else None


def _base_item_select() -> str:
    return """
        SELECT
            i.itemID,
            i.key,
            i.libraryID,
            i.itemTypeID,
            it.typeName,
            i.dateAdded,
            i.dateModified,
            i.version,
            COALESCE(
                (
                    SELECT v.value
                    FROM itemData d
                    JOIN fields f ON f.fieldID = d.fieldID
                    JOIN itemDataValues v ON v.valueID = d.valueID
                    WHERE d.itemID = i.itemID AND f.fieldName = 'title'
                    LIMIT 1
                ),
                n.title,
                ''
            ) AS title,
            n.parentItemID AS noteParentItemID,
            n.note AS noteContent,
            a.parentItemID AS attachmentParentItemID,
            an.parentItemID AS annotationParentItemID,
            an.text AS annotationText,
            an.comment AS annotationComment,
            a.linkMode,
            a.contentType,
            a.path AS attachmentPath
        FROM items i
        JOIN itemTypes it ON it.itemTypeID = i.itemTypeID
        LEFT JOIN itemNotes n ON n.itemID = i.itemID
        LEFT JOIN itemAttachments a ON a.itemID = i.itemID
        LEFT JOIN itemAnnotations an ON an.itemID = i.itemID
    """
