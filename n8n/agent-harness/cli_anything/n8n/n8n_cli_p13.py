# ruff: noqa: F403, F405, E501
from .n8n_cli_base import *  # noqa: F403

# fmt: off
from .n8n_cli_p1 import _auto_snapshot, _clean_for_api, _conn, _json_flag  # noqa: E402,E501
from .n8n_cli_p2 import workflow_  # noqa: E402,E501
# fmt: on


@workflow_.command("patch")
@click.argument("workflow_id")
@click.option("--rename", default=None, help="Rename the workflow")
@click.option("--enable-node", default=None, help="Enable a disabled node by name")
@click.option("--disable-node", default=None, help="Disable a node by name")
@click.option(
    "--remove-node", default=None, help="Remove a node by name (and its connections)"
)
@click.option(
    "--connect",
    nargs=2,
    default=None,
    help="Connect two nodes: --connect SOURCE TARGET",
)
@click.option(
    "--disconnect",
    nargs=2,
    default=None,
    help="Disconnect two nodes: --disconnect SOURCE TARGET",
)
@click.pass_context
def workflow_patch(
    ctx: click.Context,
    workflow_id: str,
    rename: str | None,
    enable_node: str | None,
    disable_node: str | None,
    remove_node: str | None,
    connect: tuple[str, str] | None,
    disconnect: tuple[str, str] | None,
) -> None:
    """Apply incremental changes to a workflow without replacing it entirely."""
    conn = _conn(ctx)
    wf = workflows.get_workflow(workflow_id, **conn)
    nodes = wf.get("nodes", [])
    if not isinstance(nodes, list):
        nodes = []
    connections = wf.get("connections", {})
    if not isinstance(connections, dict):
        connections = {}
    changed = False

    if rename:
        wf["name"] = rename
        changed = True
        success(f"Renamed to '{rename}'")

    if enable_node:
        for n in nodes:
            if isinstance(n, dict) and n.get("name") == enable_node:
                n["disabled"] = False
                changed = True
                success(f"Enabled node '{enable_node}'")
                break
        else:
            error(f"Node '{enable_node}' not found")
            return

    if disable_node:
        for n in nodes:
            if isinstance(n, dict) and n.get("name") == disable_node:
                n["disabled"] = True
                changed = True
                success(f"Disabled node '{disable_node}'")
                break
        else:
            error(f"Node '{disable_node}' not found")
            return

    if remove_node:
        original_len = len(nodes)
        wf["nodes"] = [
            n for n in nodes if isinstance(n, dict) and n.get("name") != remove_node
        ]
        if len(wf["nodes"]) == original_len:
            error(f"Node '{remove_node}' not found")
            return
        # Clean connections
        connections.pop(remove_node, None)
        for src_conns in connections.values():
            if isinstance(src_conns, dict):
                for outputs in src_conns.values():
                    if isinstance(outputs, list):
                        for output_list in outputs:
                            if isinstance(output_list, list):
                                output_list[:] = [
                                    t
                                    for t in output_list
                                    if isinstance(t, dict)
                                    and t.get("node") != remove_node
                                ]
        changed = True
        success(f"Removed node '{remove_node}' and its connections")

    if connect:
        src, tgt = connect
        node_names = {n.get("name") for n in wf.get("nodes", []) if isinstance(n, dict)}
        if src not in node_names:
            error(f"Source node '{src}' not found")
            return
        if tgt not in node_names:
            error(f"Target node '{tgt}' not found")
            return
        src_conns = connections.setdefault(src, {})
        main_outputs = src_conns.get("main")
        if not isinstance(main_outputs, list):
            main_outputs = [[]]
            src_conns["main"] = main_outputs
        elif not main_outputs or not isinstance(main_outputs[0], list):
            main_outputs.insert(0, [])
        main_outputs[0].append({"node": tgt, "type": "main", "index": 0})
        changed = True
        success(f"Connected '{src}' -> '{tgt}'")

    if disconnect:
        src, tgt = disconnect
        if src in connections and isinstance(connections[src], dict):
            for outputs in connections[src].values():
                if isinstance(outputs, list):
                    for output_list in outputs:
                        if isinstance(output_list, list):
                            output_list[:] = [
                                t
                                for t in output_list
                                if isinstance(t, dict) and t.get("node") != tgt
                            ]
            changed = True
            success(f"Disconnected '{src}' -> '{tgt}'")
        else:
            error(f"No connections from '{src}'")
            return

    if not changed:
        error(
            "No operations specified. Use --rename, --enable-node, --disable-node, --remove-node, --connect, or --disconnect"
        )
        return

    _auto_snapshot(workflow_id, conn, "patch")
    update_data = _clean_for_api(wf)
    result = workflows.update_workflow(workflow_id, update_data, **conn)
    output(result, _json_flag(ctx))
