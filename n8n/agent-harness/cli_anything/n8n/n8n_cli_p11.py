# ruff: noqa: F403, F405, E501
from .n8n_cli_base import *  # noqa: F403

# fmt: off
from .n8n_cli_p1 import _conn, _json_flag, _load_json_arg  # noqa: E402,E501
from .n8n_cli_p2 import workflow_  # noqa: E402,E501
# fmt: on


@workflow_.command("validate")
@click.argument("source")
@click.pass_context
def workflow_validate(ctx: click.Context, source: str) -> None:
    """Validate a workflow structure. Use workflow ID or @file.json."""
    conn = _conn(ctx)

    if source.startswith("@"):
        data = _load_json_arg(source)
    else:
        data = workflows.get_workflow(source, **conn)

    issues: list[str] = []
    warnings: list[str] = []

    # Check basic structure
    if not data.get("name"):
        issues.append("Missing workflow name")
    if not data.get("nodes"):
        issues.append("No nodes defined")
    if not isinstance(data.get("connections", {}), dict):
        issues.append("Invalid connections format (must be object)")

    nodes = data.get("nodes", [])
    if not isinstance(nodes, list):
        issues.append("Invalid nodes format (must be array)")
        nodes = []
    nodes = [n for n in nodes if isinstance(n, dict)]
    node_names = {n.get("name") for n in nodes}

    # Check each node
    trigger_count = 0
    for node in nodes:
        if not node.get("type"):
            issues.append(f"Node '{node.get('name', '?')}' has no type")
        if not node.get("name"):
            issues.append(f"Node of type '{node.get('type', '?')}' has no name")
        node_type_lower = node.get("type", "").lower()
        if "trigger" in node_type_lower or "webhook" in node_type_lower:
            trigger_count += 1

    if trigger_count == 0:
        warnings.append("No trigger node found — workflow cannot be activated")
    if trigger_count > 1:
        warnings.append(
            f"Multiple trigger nodes ({trigger_count}) — only one should be active"
        )

    # Check connections reference existing nodes
    for source_node, conns in data.get("connections", {}).items():
        if source_node not in node_names:
            issues.append(f"Connection from non-existent node: '{source_node}'")
        if isinstance(conns, dict):
            for conn_type, outputs in conns.items():
                if isinstance(outputs, list):
                    for output_list in outputs:
                        if isinstance(output_list, list):
                            for target in output_list:
                                if not isinstance(target, dict):
                                    continue
                                target_name = target.get("node", "")
                                if target_name and target_name not in node_names:
                                    issues.append(
                                        f"Connection to non-existent node: '{target_name}'"
                                    )

    # Check for duplicate node names
    seen_names: set[str] = set()
    for node in nodes:
        name = node.get("name", "")
        if name in seen_names:
            issues.append(f"Duplicate node name: '{name}'")
        seen_names.add(name)

    if _json_flag(ctx):
        output(
            {"valid": len(issues) == 0, "issues": issues, "warnings": warnings}, True
        )
        return

    if issues:
        click.secho(f"\n  INVALID — {len(issues)} issue(s):\n", fg="red", bold=True)
        for i in issues:
            click.secho(f"    {i}", fg="red")
    else:
        click.secho("\n  VALID", fg="green", bold=True)

    if warnings:
        click.secho(f"\n  {len(warnings)} warning(s):", fg="yellow")
        for w in warnings:
            click.secho(f"    {w}", fg="yellow")

    if not issues and not warnings:
        click.echo(f"  {len(nodes)} nodes, {trigger_count} trigger(s)")
    click.echo()
