# ruff: noqa: F403, F405, E501
from .zotero_sqlite_base import *  # noqa: F403

# fmt: off
from .zotero_sqlite_p1 import backup_database, connect_writable  # noqa: E402,E501
# fmt: on


def move_item_between_collections_record(
    sqlite_path: Path | str,
    *,
    item_id: int,
    target_collection_id: int,
    source_collection_ids: list[int],
) -> dict[str, Any]:
    backup_path = backup_database(sqlite_path)
    with closing(connect_writable(sqlite_path)) as conn:
        try:
            conn.execute("BEGIN IMMEDIATE")
            existing = conn.execute(
                "SELECT 1 FROM collectionItems WHERE collectionID = ? AND itemID = ?",
                (int(target_collection_id), int(item_id)),
            ).fetchone()
            added_to_target = False
            if not existing:
                row = conn.execute(
                    "SELECT COALESCE(MAX(orderIndex), -1) + 1 AS nextIndex FROM collectionItems WHERE collectionID = ?",
                    (int(target_collection_id),),
                ).fetchone()
                next_index = int(row["nextIndex"]) if row else 0
                conn.execute(
                    "INSERT INTO collectionItems (collectionID, itemID, orderIndex) VALUES (?, ?, ?)",
                    (int(target_collection_id), int(item_id), next_index),
                )
                added_to_target = True

            removed = 0
            for source_collection_id in source_collection_ids:
                if int(source_collection_id) == int(target_collection_id):
                    continue
                cursor = conn.execute(
                    "DELETE FROM collectionItems WHERE collectionID = ? AND itemID = ?",
                    (int(source_collection_id), int(item_id)),
                )
                removed += int(cursor.rowcount)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    return {
        "backupPath": str(backup_path),
        "itemID": int(item_id),
        "targetCollectionID": int(target_collection_id),
        "removedCount": removed,
        "addedToTarget": added_to_target,
    }
