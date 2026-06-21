# ruff: noqa: F403, F405, E501
from .zotero_sqlite_base import *  # noqa: F403

# fmt: off
from .zotero_sqlite_p1 import _as_dicts, connect_readonly  # noqa: E402,E501
from .zotero_sqlite_p2 import _base_item_select  # noqa: E402,E501
from .zotero_sqlite_p3 import _normalize_item, fetch_items, resolve_item  # noqa: E402,E501
# fmt: on


def find_items_by_title(
    sqlite_path: Path | str,
    query: str,
    *,
    library_id: int | None = None,
    collection_id: int | None = None,
    limit: int = 20,
    exact_title: bool = False,
) -> list[dict[str, Any]]:
    query = query.strip()
    if not query:
        return []
    title_expr = """
        LOWER(
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
            )
        )
    """
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
    where.append("COALESCE(a.parentItemID, n.parentItemID, an.parentItemID) IS NULL")
    if exact_title:
        where.append(f"{title_expr} = ?")
        params.append(query.lower())
    else:
        where.append(f"{title_expr} LIKE ?")
        params.append(f"%{query.lower()}%")
    sql = (
        "SELECT * FROM ("
        + _base_item_select()
        + f"\nWHERE {' AND '.join(where)}\n) AS base\n"
        + """
        ORDER BY
            CASE
                WHEN LOWER(title) = ? THEN 0
                WHEN LOWER(title) LIKE ? THEN 1
                ELSE 2
            END,
            INSTR(LOWER(title), ?),
            dateModified DESC,
            itemID DESC
        LIMIT ?
        """
    )
    params.extend([query.lower(), f"{query.lower()}%", query.lower(), int(limit)])
    with closing(connect_readonly(sqlite_path)) as conn:
        rows = conn.execute(sql, params).fetchall()
        return [_normalize_item(conn, row, include_related=False) for row in rows]


def fetch_item_children(
    sqlite_path: Path | str, ref: str | int
) -> list[dict[str, Any]]:
    item = resolve_item(sqlite_path, ref)
    if not item:
        return []
    return fetch_items(sqlite_path, parent_item_id=int(item["itemID"]))


def fetch_item_notes(sqlite_path: Path | str, ref: str | int) -> list[dict[str, Any]]:
    children = fetch_item_children(sqlite_path, ref)
    return [child for child in children if child["typeName"] == "note"]


def fetch_item_attachments(
    sqlite_path: Path | str, ref: str | int
) -> list[dict[str, Any]]:
    children = fetch_item_children(sqlite_path, ref)
    return [child for child in children if child["typeName"] == "attachment"]


def resolve_attachment_real_path(
    item: dict[str, Any], data_dir: Path | str
) -> Optional[str]:
    raw_path = item.get("attachmentPath")
    if not raw_path:
        return None
    raw_path = str(raw_path)
    data_dir = Path(data_dir)
    if raw_path.startswith("storage:"):
        filename = raw_path.split(":", 1)[1]
        return str((data_dir / "storage" / item["key"] / filename).resolve())
    if raw_path.startswith("file://"):
        parsed = urlparse(raw_path)
        decoded_path = unquote(parsed.path)
        if parsed.netloc and parsed.netloc.lower() != "localhost":
            normalized_unc_path = decoded_path.replace("/", "\\")
            unc_path = f"\\\\{parsed.netloc}{normalized_unc_path}"
            return str(PureWindowsPath(unc_path))
        if re.match(r"^/[A-Za-z]:", decoded_path):
            return str(PureWindowsPath(decoded_path.lstrip("/")))
        return decoded_path if os.name != "nt" else str(PureWindowsPath(decoded_path))
    path = Path(raw_path)
    if path.is_absolute():
        return str(path)
    return str((data_dir / raw_path).resolve())


def fetch_saved_searches(
    sqlite_path: Path | str, library_id: int | None = None
) -> list[dict[str, Any]]:
    with closing(connect_readonly(sqlite_path)) as conn:
        rows = conn.execute(
            """
            SELECT savedSearchID, savedSearchName, clientDateModified, libraryID, key, version
            FROM savedSearches
            WHERE (? IS NULL OR libraryID = ?)
            ORDER BY savedSearchName COLLATE NOCASE
            """,
            (library_id, library_id),
        ).fetchall()
        searches = _as_dicts(rows)
        for search in searches:
            condition_rows = conn.execute(
                """
                SELECT searchConditionID, condition, operator, value, required
                FROM savedSearchConditions
                WHERE savedSearchID = ?
                ORDER BY searchConditionID
                """,
                (search["savedSearchID"],),
            ).fetchall()
            search["conditions"] = _as_dicts(condition_rows)
    return searches
