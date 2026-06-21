# ruff: noqa: F403, F405, E501
from .mubu_probe_base import *  # noqa: F403
# fmt: off
from .mubu_probe_p1 import DEFAULT_API_HOST, DEFAULT_BACKUP_ROOT, DEFAULT_LOG_ROOT, DEFAULT_STORAGE_ROOT  # noqa: E402,E501
# fmt: on


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Probe local Mubu desktop backups and sync logs.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    docs_parser = subparsers.add_parser("docs", help="List latest known document snapshots from local backups.")
    docs_parser.add_argument("--root", type=Path, default=DEFAULT_BACKUP_ROOT)
    docs_parser.add_argument("--limit", type=int, default=20)
    docs_parser.add_argument("--json", action="store_true")

    show_parser = subparsers.add_parser("show", help="Show the latest backup tree for one document.")
    show_parser.add_argument("doc_id")
    show_parser.add_argument("--root", type=Path, default=DEFAULT_BACKUP_ROOT)
    show_parser.add_argument("--max-depth", type=int, default=None)
    show_parser.add_argument("--json", action="store_true")

    search_parser = subparsers.add_parser("search", help="Search latest backups for matching node text or note content.")
    search_parser.add_argument("query")
    search_parser.add_argument("--root", type=Path, default=DEFAULT_BACKUP_ROOT)
    search_parser.add_argument("--limit", type=int, default=20)
    search_parser.add_argument("--json", action="store_true")

    changes_parser = subparsers.add_parser("changes", help="Parse recent client-sync change events from local logs.")
    changes_parser.add_argument("--log-root", type=Path, default=DEFAULT_LOG_ROOT)
    changes_parser.add_argument("--doc-id", default=None)
    changes_parser.add_argument("--limit", type=int, default=20)
    changes_parser.add_argument("--json", action="store_true")

    folders_parser = subparsers.add_parser("folders", help="List folder metadata from local RxDB storage.")
    folders_parser.add_argument("--storage-root", type=Path, default=DEFAULT_STORAGE_ROOT)
    folders_parser.add_argument("--query", default=None)
    folders_parser.add_argument("--limit", type=int, default=50)
    folders_parser.add_argument("--json", action="store_true")

    folder_docs_parser = subparsers.add_parser("folder-docs", help="List document metadata for one folder.")
    folder_docs_parser.add_argument("folder_id")
    folder_docs_parser.add_argument("--storage-root", type=Path, default=DEFAULT_STORAGE_ROOT)
    folder_docs_parser.add_argument("--limit", type=int, default=50)
    folder_docs_parser.add_argument("--json", action="store_true")

    path_docs_parser = subparsers.add_parser("path-docs", help="List documents for one folder path or folder id.")
    path_docs_parser.add_argument("folder_ref")
    path_docs_parser.add_argument("--storage-root", type=Path, default=DEFAULT_STORAGE_ROOT)
    path_docs_parser.add_argument("--limit", type=int, default=50)
    path_docs_parser.add_argument("--json", action="store_true")

    recent_parser = subparsers.add_parser("recent", help="List recently active documents using backups, metadata, and sync logs.")
    recent_parser.add_argument("--storage-root", type=Path, default=DEFAULT_STORAGE_ROOT)
    recent_parser.add_argument("--root", type=Path, default=DEFAULT_BACKUP_ROOT)
    recent_parser.add_argument("--log-root", type=Path, default=DEFAULT_LOG_ROOT)
    recent_parser.add_argument("--limit", type=int, default=20)
    recent_parser.add_argument("--json", action="store_true")

    links_parser = subparsers.add_parser("links", help="Extract outbound Mubu document links from one document backup.")
    links_parser.add_argument("doc_id")
    links_parser.add_argument("--root", type=Path, default=DEFAULT_BACKUP_ROOT)
    links_parser.add_argument("--storage-root", type=Path, default=DEFAULT_STORAGE_ROOT)
    links_parser.add_argument("--json", action="store_true")

    daily_parser = subparsers.add_parser("daily", help="Find Daily-style folders and list the documents inside them.")
    daily_parser.add_argument("--storage-root", type=Path, default=DEFAULT_STORAGE_ROOT)
    daily_parser.add_argument(
        "--query",
        default=None,
        help="Optional folder-name substring filter. Defaults to built-in daily-folder heuristics.",
    )
    daily_parser.add_argument("--limit", type=int, default=50)
    daily_parser.add_argument("--json", action="store_true")

    daily_current_parser = subparsers.add_parser(
        "daily-current",
        help="Resolve the current daily document from one Daily-style folder.",
    )
    daily_current_parser.add_argument("folder_ref", nargs="?")
    daily_current_parser.add_argument("--storage-root", type=Path, default=DEFAULT_STORAGE_ROOT)
    daily_current_parser.add_argument("--limit", type=int, default=5)
    daily_current_parser.add_argument(
        "--allow-non-daily-titles",
        action="store_true",
        help="Fallback to the latest document even if no date-like title is found.",
    )
    daily_current_parser.add_argument("--json", action="store_true")

    daily_nodes_parser = subparsers.add_parser(
        "daily-nodes",
        help="List live nodes from the current daily document in one step.",
    )
    daily_nodes_parser.add_argument("folder_ref", nargs="?")
    daily_nodes_parser.add_argument("--storage-root", type=Path, default=DEFAULT_STORAGE_ROOT)
    daily_nodes_parser.add_argument("--api-host", default=DEFAULT_API_HOST)
    daily_nodes_parser.add_argument("--query", default=None, help="Filter nodes by plain-text substring.")
    daily_nodes_parser.add_argument("--max-depth", type=int, default=None)
    daily_nodes_parser.add_argument("--limit", type=int, default=200)
    daily_nodes_parser.add_argument(
        "--allow-non-daily-titles",
        action="store_true",
        help="Fallback to the latest document even if no date-like title is found.",
    )
    daily_nodes_parser.add_argument("--json", action="store_true")

    open_path_parser = subparsers.add_parser("open-path", help="Open one document by full path, suffix path, title, or doc id.")
    open_path_parser.add_argument("doc_ref")
    open_path_parser.add_argument("--storage-root", type=Path, default=DEFAULT_STORAGE_ROOT)
    open_path_parser.add_argument("--root", type=Path, default=DEFAULT_BACKUP_ROOT)
    open_path_parser.add_argument("--max-depth", type=int, default=None)
    open_path_parser.add_argument("--json", action="store_true")

    doc_nodes_parser = subparsers.add_parser(
        "doc-nodes",
        help="List live document nodes with node ids and update-target paths.",
    )
    doc_nodes_parser.add_argument("doc_ref")
    doc_nodes_parser.add_argument("--storage-root", type=Path, default=DEFAULT_STORAGE_ROOT)
    doc_nodes_parser.add_argument("--api-host", default=DEFAULT_API_HOST)
    doc_nodes_parser.add_argument("--query", default=None, help="Filter nodes by plain-text substring.")
    doc_nodes_parser.add_argument("--max-depth", type=int, default=None)
    doc_nodes_parser.add_argument("--limit", type=int, default=200)
    doc_nodes_parser.add_argument("--json", action="store_true")

    create_child_parser = subparsers.add_parser(
        "create-child",
        help="Build or execute one child-node creation against the live Mubu API.",
    )
    create_child_parser.add_argument("doc_ref")
    create_child_parser.add_argument("--text", required=True, help="New child plain text.")
    create_child_parser.add_argument("--note", default=None, help="Optional plain-text note for the new child.")
    create_child_parser.add_argument("--parent-node-id", default=None, help="Target parent node by id.")
    create_child_parser.add_argument("--parent-match-text", default=None, help="Target parent node by exact current plain text.")
    create_child_parser.add_argument("--parent-field", choices=["text", "note"], default="text")
    create_child_parser.add_argument("--index", type=int, default=None, help="Insert position within the parent children list.")
    create_child_parser.add_argument("--storage-root", type=Path, default=DEFAULT_STORAGE_ROOT)
    create_child_parser.add_argument("--log-root", type=Path, default=DEFAULT_LOG_ROOT)
    create_child_parser.add_argument("--api-host", default=DEFAULT_API_HOST)
    create_child_parser.add_argument("--execute", action="store_true", help="Actually POST the CHANGE event.")
    create_child_parser.add_argument("--json", action="store_true")

    delete_node_parser = subparsers.add_parser(
        "delete-node",
        help="Build or execute one node deletion against the live Mubu API.",
    )
    delete_node_parser.add_argument("doc_ref")
    delete_node_parser.add_argument("--node-id", default=None, help="Target one node by id.")
    delete_node_parser.add_argument("--match-text", default=None, help="Target one node by exact current plain text.")
    delete_node_parser.add_argument("--field", choices=["text", "note"], default="text")
    delete_node_parser.add_argument("--storage-root", type=Path, default=DEFAULT_STORAGE_ROOT)
    delete_node_parser.add_argument("--log-root", type=Path, default=DEFAULT_LOG_ROOT)
    delete_node_parser.add_argument("--api-host", default=DEFAULT_API_HOST)
    delete_node_parser.add_argument("--execute", action="store_true", help="Actually POST the CHANGE event.")
    delete_node_parser.add_argument("--json", action="store_true")

    update_text_parser = subparsers.add_parser("update-text", help="Build or execute one text update against the live Mubu API.")
    update_text_parser.add_argument("doc_ref")
    update_text_parser.add_argument("--text", required=True, help="Replacement plain text.")
    update_text_parser.add_argument("--node-id", default=None, help="Target one node by id.")
    update_text_parser.add_argument("--match-text", default=None, help="Target one node by exact current plain text.")
    update_text_parser.add_argument("--field", choices=["text", "note"], default="text")
    update_text_parser.add_argument("--storage-root", type=Path, default=DEFAULT_STORAGE_ROOT)
    update_text_parser.add_argument("--log-root", type=Path, default=DEFAULT_LOG_ROOT)
    update_text_parser.add_argument("--api-host", default=DEFAULT_API_HOST)
    update_text_parser.add_argument("--execute", action="store_true", help="Actually POST the CHANGE event.")
    update_text_parser.add_argument("--json", action="store_true")

    return parser
