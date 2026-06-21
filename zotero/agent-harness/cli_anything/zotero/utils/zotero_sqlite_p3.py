# ruff: noqa: F403, F405, E501
from .zotero_sqlite_base import *  # noqa: F403

# fmt: off
from .zotero_sqlite_p1 import _as_dicts, _is_numeric_ref, connect_readonly, note_html_to_text, note_preview  # noqa: E402,E501
from .zotero_sqlite_p2 import _ambiguous_reference, _base_item_select  # noqa: E402,E501
# fmt: on


def _fetch_item_fields(conn: sqlite3.Connection, item_id: int) -> dict[str, Any]:
    rows = conn.execute(
        """
        SELECT f.fieldName, v.value
        FROM itemData d
        JOIN fields f ON f.fieldID = d.fieldID
        JOIN itemDataValues v ON v.valueID = d.valueID
        WHERE d.itemID = ?
        ORDER BY f.fieldName COLLATE NOCASE
        """,
        (item_id,),
    ).fetchall()
    return {row["fieldName"]: row["value"] for row in rows}


def _fetch_item_creators(
    conn: sqlite3.Connection, item_id: int
) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT c.creatorID, c.firstName, c.lastName, c.fieldMode, ic.creatorTypeID, ic.orderIndex
        FROM itemCreators ic
        JOIN creators c ON c.creatorID = ic.creatorID
        WHERE ic.itemID = ?
        ORDER BY ic.orderIndex
        """,
        (item_id,),
    ).fetchall()
    return _as_dicts(rows)


def _fetch_item_tags(conn: sqlite3.Connection, item_id: int) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT t.tagID, t.name, it.type
        FROM itemTags it
        JOIN tags t ON t.tagID = it.tagID
        WHERE it.itemID = ?
        ORDER BY t.name COLLATE NOCASE
        """,
        (item_id,),
    ).fetchall()
    return _as_dicts(rows)


def _normalize_item(
    conn: sqlite3.Connection, row: sqlite3.Row, include_related: bool = False
) -> dict[str, Any]:
    item = dict(row)
    item["fields"] = (
        _fetch_item_fields(conn, int(row["itemID"])) if include_related else {}
    )
    item["creators"] = (
        _fetch_item_creators(conn, int(row["itemID"])) if include_related else []
    )
    item["tags"] = _fetch_item_tags(conn, int(row["itemID"])) if include_related else []
    item["isAttachment"] = row["typeName"] == "attachment"
    item["isNote"] = row["typeName"] == "note"
    item["isAnnotation"] = row["typeName"] == "annotation"
    item["parentItemID"] = (
        row["attachmentParentItemID"]
        or row["noteParentItemID"]
        or row["annotationParentItemID"]
    )
    item["noteText"] = note_html_to_text(row["noteContent"])
    item["notePreview"] = note_preview(row["noteContent"])
    return item


def resolve_item(
    sqlite_path: Path | str, ref: str | int, *, library_id: int | None = None
) -> Optional[dict[str, Any]]:
    params: list[Any]
    if _is_numeric_ref(ref):
        where = "i.itemID = ?"
        params = [int(ref)]
    else:
        where = "i.key = ?"
        params = [str(ref)]
        if library_id is not None:
            where += " AND i.libraryID = ?"
            params.append(int(library_id))
    with closing(connect_readonly(sqlite_path)) as conn:
        rows = conn.execute(
            _base_item_select() + f"\nWHERE {where}\nORDER BY i.libraryID, i.itemID",
            params,
        ).fetchall()
        if not rows:
            return None
        if len(rows) > 1 and library_id is None and not _is_numeric_ref(ref):
            _ambiguous_reference(ref, "item", rows)
        return _normalize_item(conn, rows[0], include_related=True)


def fetch_item_collections(
    sqlite_path: Path | str, ref: str | int
) -> list[dict[str, Any]]:
    item = resolve_item(sqlite_path, ref)
    if not item:
        return []
    with closing(connect_readonly(sqlite_path)) as conn:
        rows = conn.execute(
            """
            SELECT c.collectionID, c.key, c.collectionName, c.parentCollectionID, c.libraryID
            FROM collectionItems ci
            JOIN collections c ON c.collectionID = ci.collectionID
            WHERE ci.itemID = ?
            ORDER BY c.collectionName COLLATE NOCASE, c.collectionID
            """,
            (int(item["itemID"]),),
        ).fetchall()
    return _as_dicts(rows)


def fetch_items(
    sqlite_path: Path | str,
    *,
    library_id: int | None = None,
    collection_id: int | None = None,
    parent_item_id: int | None = None,
    tag: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    where = ["1=1"]
    params: list[Any] = []
    if library_id is not None:
        where.append("i.libraryID = ?")
        params.append(library_id)
    if collection_id is not None:
        where.append(
            "EXISTS (SELECT 1 FROM collectionItems ci WHERE ci.itemID = i.itemID AND ci.collectionID = ?)"
        )
        params.append(collection_id)
    if parent_item_id is None:
        where.append(
            "COALESCE(a.parentItemID, n.parentItemID, an.parentItemID) IS NULL"
        )
    else:
        where.append("COALESCE(a.parentItemID, n.parentItemID, an.parentItemID) = ?")
        params.append(parent_item_id)
    if tag is not None:
        where.append(
            """
            EXISTS (
                SELECT 1
                FROM itemTags it2
                JOIN tags t2 ON t2.tagID = it2.tagID
                WHERE it2.itemID = i.itemID AND (t2.name = ? OR t2.tagID = ?)
            )
            """
        )
        params.extend([tag, int(tag) if _is_numeric_ref(tag) else -1])
    sql = (
        _base_item_select()
        + f"\nWHERE {' AND '.join(where)}\nORDER BY i.dateModified DESC, i.itemID DESC"
    )
    if limit is not None:
        sql += f"\nLIMIT {int(limit)}"
    with closing(connect_readonly(sqlite_path)) as conn:
        rows = conn.execute(sql, params).fetchall()
        return [_normalize_item(conn, row, include_related=False) for row in rows]
