# ruff: noqa: F403, F405, E501
from .mubu_probe_base import *  # noqa: F403
# fmt: off
from .mubu_probe_p1 import resolve_daily_folder_ref  # noqa: E402,E501
from .mubu_probe_p2 import normalized_lookup_key  # noqa: E402,E501
from .mubu_probe_p3 import build_folder_indexes, document_meta_sort_key, load_document_metas, load_folders  # noqa: E402,E501
from .mubu_probe_p4 import dedupe_document_metas_by_logical_path, folder_documents  # noqa: E402,E501
from .mubu_probe_p6 import choose_current_daily_document, looks_like_daily_folder_name  # noqa: E402,E501
from .mubu_probe_p11 import dump_output  # noqa: E402,E501
from .mubu_probe_p12 import ambiguous_error_message  # noqa: E402,E501
# fmt: on


def _mubu_cmd6(args, folder, folder_paths, folders, meta, metas, payload):
    folders = load_folders(args.storage_root)
    metas = load_document_metas(args.storage_root)
    _, folder_paths = build_folder_indexes(folders)
    logical_metas = dedupe_document_metas_by_logical_path(metas, folder_paths)
    docs_by_folder: dict[str, list[dict[str, Any]]] = {}
    for meta in logical_metas:
        folder_id = meta.get("folder_id")
        if isinstance(folder_id, str):
            docs_by_folder.setdefault(folder_id, []).append(meta)
    if args.query:
        query = normalized_lookup_key(args.query)
        matched_folders = [
            folder
            for folder in folders
            if query in normalized_lookup_key(folder.get("name"))
        ]
    else:
        matched_folders = [
            folder
            for folder in folders
            if looks_like_daily_folder_name(folder.get("name"))
            or choose_current_daily_document(docs_by_folder.get(folder.get("folder_id"), []))[0] is not None
        ]
    matched_ids = {folder["folder_id"] for folder in matched_folders}
    docs = [
        meta
        for meta in logical_metas
        if meta.get("folder_id") in matched_ids
    ]
    docs.sort(key=document_meta_sort_key, reverse=True)
    payload = {
        "folders": [
            {**folder, "path": folder_paths.get(folder["folder_id"], "")}
            for folder in matched_folders
        ],
        "documents": docs[: args.limit],
    }
    dump_output(payload, args.json)
    return 0
def _mubu_cmd7(ambiguous, args, folder, folders, metas, parser, payload):
    metas = load_document_metas(args.storage_root)
    folders = load_folders(args.storage_root)
    try:
        folder_ref = resolve_daily_folder_ref(args.folder_ref)
    except RuntimeError as exc:
        parser.error(str(exc))
    docs, folder, ambiguous = folder_documents(metas, folders, folder_ref)
    if folder is None:
        if ambiguous:
            parser.error(ambiguous_error_message("folder", folder_ref, ambiguous, "path"))
        parser.error(f"folder not found: {folder_ref}")

    selected, candidates = choose_current_daily_document(
        docs,
        allow_non_daily_titles=args.allow_non_daily_titles,
    )
    if selected is None:
        parser.error(
            f"no current daily document found in {folder['path']}; "
            "rerun with --allow-non-daily-titles or inspect with path-docs"
        )

    payload = {
        "folder": folder,
        "selection": {
            "strategy": "latest_updated_date_titled_document"
            if not args.allow_non_daily_titles
            else "latest_updated_document_with_non_daily_fallback",
            "allow_non_daily_titles": args.allow_non_daily_titles,
            "candidate_count": len(candidates),
        },
        "document": selected,
        "candidates": candidates[: args.limit],
    }
    dump_output(payload, args.json)
    return 0
