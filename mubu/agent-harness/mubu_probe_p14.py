# ruff: noqa: F403, F405, E501
from .mubu_probe_base import *  # noqa: F403
# fmt: off
from .mubu_probe_p1 import extract_plain_text  # noqa: E402,E501
from .mubu_probe_p3 import load_document_metas, load_folders  # noqa: E402,E501
from .mubu_probe_p5 import load_change_events  # noqa: E402,E501
from .mubu_probe_p6 import fetch_document_remote, get_active_user  # noqa: E402,E501
from .mubu_probe_p7 import node_path_to_api_path, resolve_mutation_member_context  # noqa: E402,E501
from .mubu_probe_p8 import resolve_document_reference  # noqa: E402,E501
from .mubu_probe_p9 import resolve_node_reference_in_data  # noqa: E402,E501
from .mubu_probe_p11 import dump_output, perform_create_child  # noqa: E402,E501
from .mubu_probe_p12 import ambiguous_error_message  # noqa: E402,E501
# fmt: on


def _mubu_cmd1(ambiguous, args, definition, definition_raw, folders, meta, metas, parser, payload, remote_doc, user):
    if not args.parent_node_id and not args.parent_match_text:
        parser.error("create-child requires --parent-node-id or --parent-match-text")

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

    parent_node, parent_path, node_ambiguous = resolve_node_reference_in_data(
        definition,
        node_id=args.parent_node_id,
        match_text=args.parent_match_text,
        field=args.parent_field,
    )
    if parent_node is None or parent_path is None:
        if node_ambiguous:
            labels = [extract_plain_text(item["node"].get(args.parent_field)) for item in node_ambiguous[:5]]
            parser.error(f"ambiguous parent node reference in {meta['doc_id']}: {labels}")
        parser.error(f"parent node not found in {meta['doc_id']}")

    try:
        result = perform_create_child(
            user=user,
            doc_id=meta["doc_id"],
            member_id=member_context.get("member_id"),
            version=remote_doc.get("baseVersion", 0),
            parent_node=parent_node,
            parent_path=parent_path,
            text=args.text,
            note=args.note,
            index=args.index,
            execute=args.execute,
            api_host=args.api_host,
        )
    except ValueError as exc:
        parser.error(str(exc))

    created = result["request"]["data"]["events"][0]["created"][0]
    created_node = created["node"]
    payload = {
        "execute": args.execute,
        "document": {
            "doc_id": meta["doc_id"],
            "title": meta.get("title"),
            "doc_path": meta.get("doc_path"),
            "base_version": remote_doc.get("baseVersion"),
        },
        "member_context": member_context,
        "target_parent": {
            "node_id": parent_node.get("id"),
            "field": args.parent_field,
            "path": list(parent_path),
            "api_path": node_path_to_api_path(parent_path),
            "current_text": extract_plain_text(parent_node.get(args.parent_field)),
            "existing_child_count": len(parent_node.get("children") or []),
        },
        "new_child": {
            "node_id": created_node.get("id"),
            "index": created.get("index"),
            "path": created.get("path"),
            "text": args.text,
            "note": args.note,
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
            node_id=created_node.get("id"),
        )
        payload["verification"] = {
            "base_version_after": refreshed.get("baseVersion"),
            "created_node_present": refreshed_node is not None,
            "node_text_after": extract_plain_text((refreshed_node or {}).get("text")),
            "node_note_after": extract_plain_text((refreshed_node or {}).get("note")),
        }

    dump_output(payload, args.json)
    return 0
