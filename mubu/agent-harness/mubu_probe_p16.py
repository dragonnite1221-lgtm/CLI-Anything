# ruff: noqa: F403, F405, E501
from .mubu_probe_base import *  # noqa: F403
# fmt: off
from .mubu_probe_p1 import extract_plain_text  # noqa: E402,E501
from .mubu_probe_p3 import load_document_metas, load_folders  # noqa: E402,E501
from .mubu_probe_p5 import load_change_events  # noqa: E402,E501
from .mubu_probe_p6 import fetch_document_remote, get_active_user  # noqa: E402,E501
from .mubu_probe_p7 import resolve_mutation_member_context  # noqa: E402,E501
from .mubu_probe_p8 import resolve_document_reference  # noqa: E402,E501
from .mubu_probe_p9 import resolve_node_reference_in_data  # noqa: E402,E501
from .mubu_probe_p11 import dump_output, perform_text_update  # noqa: E402,E501
from .mubu_probe_p12 import ambiguous_error_message  # noqa: E402,E501
# fmt: on


def _mubu_cmd3(ambiguous, args, definition, definition_raw, folders, meta, metas, parser, payload, remote_doc, user):
    if not args.node_id and not args.match_text:
        parser.error("update-text requires --node-id or --match-text")

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

    events = load_change_events(args.log_root, doc_id=meta["doc_id"], limit=None)
    member_context = resolve_mutation_member_context(events, meta["doc_id"], execute=args.execute)
    if member_context is None:
        parser.error(f"no member context found in sync logs for document: {meta['doc_id']}")

    remote_doc = fetch_document_remote(meta["doc_id"], user, api_host=args.api_host)
    definition_raw = remote_doc.get("definition")
    if not isinstance(definition_raw, str):
        parser.error(f"document definition missing for: {meta['doc_id']}")
    definition = json.loads(definition_raw)

    node, path, node_ambiguous = resolve_node_reference_in_data(
        definition,
        node_id=args.node_id,
        match_text=args.match_text,
        field=args.field,
    )
    if node is None or path is None:
        if node_ambiguous:
            labels = [extract_plain_text(item["node"].get(args.field)) for item in node_ambiguous[:5]]
            parser.error(f"ambiguous node reference in {meta['doc_id']}: {labels}")
        parser.error(f"node not found in {meta['doc_id']}")

    result = perform_text_update(
        user=user,
        doc_id=meta["doc_id"],
        member_id=member_context.get("member_id"),
        version=remote_doc.get("baseVersion", 0),
        node=node,
        path=path,
        new_text=args.text,
        field=args.field,
        execute=args.execute,
        api_host=args.api_host,
    )

    payload = {
        "execute": args.execute,
        "document": {
            "doc_id": meta["doc_id"],
            "title": meta.get("title"),
            "doc_path": meta.get("doc_path"),
            "base_version": remote_doc.get("baseVersion"),
        },
        "member_context": member_context,
        "target_node": {
            "node_id": node.get("id"),
            "field": args.field,
            "path": list(path),
            "current_text": extract_plain_text(node.get(args.field)),
            "new_text": args.text,
        },
        "request": result["request"],
    }
    if member_context.get("member_id") is None:
        payload["warning"] = "dry-run request uses a placeholder member context because no recent sync log entry was found"

    if args.execute:
        payload["response"] = result["response"]
        refreshed = fetch_document_remote(meta["doc_id"], user, api_host=args.api_host)
        refreshed_definition = json.loads(refreshed.get("definition") or "{}")
        refreshed_node, _, _ = resolve_node_reference_in_data(
            refreshed_definition,
            node_id=node.get("id"),
            field=args.field,
        )
        payload["verification"] = {
            "base_version_after": refreshed.get("baseVersion"),
            "node_text_after": extract_plain_text((refreshed_node or {}).get(args.field)),
            "matches_requested_text": extract_plain_text((refreshed_node or {}).get(args.field)) == args.text,
        }

    dump_output(payload, args.json)
    return 0
