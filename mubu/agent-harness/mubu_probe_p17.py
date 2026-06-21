# ruff: noqa: F403, F405, E501
from .mubu_probe_base import *  # noqa: F403
# fmt: off
from .mubu_probe_p1 import resolve_daily_folder_ref  # noqa: E402,E501
from .mubu_probe_p3 import load_document_metas, load_folders  # noqa: E402,E501
from .mubu_probe_p4 import folder_documents  # noqa: E402,E501
from .mubu_probe_p6 import choose_current_daily_document, fetch_document_remote, get_active_user  # noqa: E402,E501
from .mubu_probe_p7 import list_document_nodes  # noqa: E402,E501
from .mubu_probe_p8 import resolve_document_reference  # noqa: E402,E501
from .mubu_probe_p11 import dump_output  # noqa: E402,E501
from .mubu_probe_p12 import ambiguous_error_message  # noqa: E402,E501
# fmt: on


def _mubu_cmd4(ambiguous, args, candidates, docs, folder, folder_ref, folders, metas, parser, payload, selected):
    user = get_active_user(args.storage_root)
    if user is None:
        parser.error("no active user auth found in local storage")

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

    remote_doc = fetch_document_remote(selected["doc_id"], user, api_host=args.api_host)
    definition_raw = remote_doc.get("definition")
    if not isinstance(definition_raw, str):
        parser.error(f"document definition missing for: {selected['doc_id']}")
    definition = json.loads(definition_raw)
    nodes = list_document_nodes(
        definition,
        query=args.query,
        max_depth=args.max_depth,
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
        "document": {
            **selected,
            "base_version": remote_doc.get("baseVersion"),
        },
        "filters": {
            "query": args.query,
            "max_depth": args.max_depth,
            "limit": args.limit,
        },
        "total_matches": len(nodes),
        "nodes": nodes[: args.limit],
    }
    dump_output(payload, args.json)
    return 0
def _mubu_cmd5(ambiguous, args, folders, meta, metas, parser, payload):
    user = get_active_user(args.storage_root)
    if user is None:
        parser.error("no active user auth found in local storage")

    metas = load_document_metas(args.storage_root)
    folders = load_folders(args.storage_root)
    meta, ambiguous = resolve_document_reference(metas, folders, args.doc_ref)
    if meta is None:
        if ambiguous:
            parser.error(ambiguous_error_message("document", args.doc_ref, ambiguous, "doc_path"))
        parser.error(f"document not found: {args.doc_ref}")

    remote_doc = fetch_document_remote(meta["doc_id"], user, api_host=args.api_host)
    definition_raw = remote_doc.get("definition")
    if not isinstance(definition_raw, str):
        parser.error(f"document definition missing for: {meta['doc_id']}")
    definition = json.loads(definition_raw)

    nodes = list_document_nodes(
        definition,
        query=args.query,
        max_depth=args.max_depth,
    )
    payload = {
        "document": {
            "doc_id": meta["doc_id"],
            "title": meta.get("title"),
            "doc_path": meta.get("doc_path"),
            "base_version": remote_doc.get("baseVersion"),
        },
        "filters": {
            "query": args.query,
            "max_depth": args.max_depth,
            "limit": args.limit,
        },
        "total_matches": len(nodes),
        "nodes": nodes[: args.limit],
    }
    dump_output(payload, args.json)
    return 0
