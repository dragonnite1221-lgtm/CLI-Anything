# ruff: noqa: F403, F405, E501
from .mubu_probe_base import *  # noqa: F403
# fmt: off
from .mubu_probe_p1 import DEFAULT_STORAGE_ROOT  # noqa: E402,E501
from .mubu_probe_p3 import build_folder_indexes, document_meta_sort_key, load_document_metas, load_folders  # noqa: E402,E501
from .mubu_probe_p4 import dedupe_document_metas_by_logical_path, document_meta_by_id, folder_documents, load_latest_backups, search_documents  # noqa: E402,E501
from .mubu_probe_p5 import load_change_events, recent_documents  # noqa: E402,E501
from .mubu_probe_p8 import document_links, show_document, show_document_by_reference  # noqa: E402,E501
from .mubu_probe_p11 import dump_output  # noqa: E402,E501
from .mubu_probe_p12 import ambiguous_error_message  # noqa: E402,E501
from .mubu_probe_p13 import build_parser  # noqa: E402,E501
from .mubu_probe_p14 import _mubu_cmd1  # noqa: E402,E501
from .mubu_probe_p15 import _mubu_cmd2  # noqa: E402,E501
from .mubu_probe_p16 import _mubu_cmd3  # noqa: E402,E501
from .mubu_probe_p17 import _mubu_cmd4, _mubu_cmd5  # noqa: E402,E501
from .mubu_probe_p18 import _mubu_cmd6, _mubu_cmd7  # noqa: E402,E501
# fmt: on


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "docs":
        documents = load_latest_backups(args.root)
        payload = [
            {
                "doc_id": item["doc_id"],
                "title": item["title"],
                "backup_file": item["backup_file"],
                "modified_at": item["modified_at"],
            }
            for item in documents[: args.limit]
        ]
        dump_output(payload, args.json)
        return 0

    if args.command == "show":
        documents = load_latest_backups(args.root)
        metas = load_document_metas(DEFAULT_STORAGE_ROOT)
        folders = load_folders(DEFAULT_STORAGE_ROOT)
        meta = document_meta_by_id(metas, folders, args.doc_id)
        payload = show_document(
            documents,
            args.doc_id,
            max_depth=args.max_depth,
            title_override=meta.get("title") if meta else None,
            folder_path=meta.get("folder_path") if meta else None,
            doc_path=meta.get("doc_path") if meta else None,
        )
        if payload is None:
            parser.error(f"document not found: {args.doc_id}")
        dump_output(payload, args.json)
        return 0

    if args.command == "search":
        documents = load_latest_backups(args.root)
        payload = search_documents(documents, args.query, limit=args.limit)
        dump_output(payload, args.json)
        return 0

    if args.command == "changes":
        payload = load_change_events(args.log_root, doc_id=args.doc_id, limit=args.limit)
        dump_output(payload, args.json)
        return 0

    if args.command == "folders":
        folders = load_folders(args.storage_root)
        _, folder_paths = build_folder_indexes(folders)
        payload = []
        for folder in folders:
            if args.query and args.query.lower() not in (folder.get("name") or "").lower():
                continue
            payload.append({**folder, "path": folder_paths.get(folder["folder_id"], "")})
        payload.sort(key=lambda item: item.get("updated_at") or 0, reverse=True)
        dump_output(payload[: args.limit], args.json)
        return 0

    if args.command == "folder-docs":
        metas = load_document_metas(args.storage_root)
        folders = load_folders(args.storage_root)
        _, folder_paths = build_folder_indexes(folders)
        payload = [
            meta
            for meta in dedupe_document_metas_by_logical_path(metas, folder_paths)
            if meta.get("folder_id") == args.folder_id
        ]
        payload.sort(key=document_meta_sort_key, reverse=True)
        dump_output(payload[: args.limit], args.json)
        return 0

    if args.command == "path-docs":
        metas = load_document_metas(args.storage_root)
        folders = load_folders(args.storage_root)
        payload, folder, ambiguous = folder_documents(metas, folders, args.folder_ref)
        if folder is None:
            if ambiguous:
                parser.error(ambiguous_error_message("folder", args.folder_ref, ambiguous, "path"))
            parser.error(f"folder not found: {args.folder_ref}")
        dump_output(
            {
                "folder": folder,
                "documents": payload[: args.limit],
            },
            args.json,
        )
        return 0

    if args.command == "recent":
        payload = recent_documents(
            load_latest_backups(args.root),
            load_document_metas(args.storage_root),
            load_folders(args.storage_root),
            log_root=args.log_root,
            limit=args.limit,
        )
        dump_output(payload, args.json)
        return 0

    if args.command == "links":
        backups = load_latest_backups(args.root)
        metas = load_document_metas(args.storage_root)
        title_lookup = {meta["doc_id"]: meta.get("title") for meta in metas if meta.get("doc_id")}
        for backup in backups:
            title_lookup.setdefault(backup["doc_id"], backup.get("title"))
        payload = document_links(backups, args.doc_id, title_lookup=title_lookup)
        dump_output(payload, args.json)
        return 0

    if args.command == "daily":
        return _mubu_cmd6(args, folder, folder_paths, folders, meta, metas, payload)

    if args.command == "daily-current":
        return _mubu_cmd7(ambiguous, args, folder, folders, metas, parser, payload)

    if args.command == "daily-nodes":
        return _mubu_cmd4(ambiguous, args, candidates, docs, folder, folder_ref, folders, metas, parser, payload, selected)

    if args.command == "open-path":
        documents = load_latest_backups(args.root)
        metas = load_document_metas(args.storage_root)
        folders = load_folders(args.storage_root)
        payload, ambiguous = show_document_by_reference(
            documents,
            metas,
            folders,
            args.doc_ref,
            max_depth=args.max_depth,
        )
        if payload is None:
            if ambiguous:
                parser.error(ambiguous_error_message("document", args.doc_ref, ambiguous, "doc_path"))
            parser.error(f"document not found: {args.doc_ref}")
        dump_output(payload, args.json)
        return 0

    if args.command == "doc-nodes":
        return _mubu_cmd5(ambiguous, args, folders, meta, metas, parser, payload)

    if args.command == "create-child":
        return _mubu_cmd1(ambiguous, args, definition, definition_raw, folders, meta, metas, parser, payload, remote_doc, user)

    if args.command == "delete-node":
        return _mubu_cmd2(ambiguous, args, definition, definition_raw, folders, meta, metas, parser, payload, remote_doc, user)

    if args.command == "update-text":
        return _mubu_cmd3(ambiguous, args, definition, definition_raw, folders, meta, metas, parser, payload, remote_doc, user)

    parser.error("unknown command")
    return 2
