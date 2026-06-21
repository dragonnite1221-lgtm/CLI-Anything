# ruff: noqa: F403, F405, E501
from .n8n_cli_base import *  # noqa: F403

# fmt: off
from .n8n_cli_p1 import _conn, _json_flag, _load_json_arg, cli  # noqa: E402,E501
from .n8n_cli_p2 import workflow_  # noqa: E402,E501
from .n8n_cli_p14 import workflow_versions_  # noqa: E402,E501
# fmt: on


@workflow_versions_.command("stats")
@click.pass_context
def versions_stats(ctx: click.Context) -> None:
    """Show version storage statistics."""
    st = versions.stats()
    if _json_flag(ctx):
        output(st, True)
        return
    click.echo(f"\n  Versions DB: {st['db_path']}")
    click.echo(f"  Workflows tracked: {st['workflows_tracked']}")
    click.echo(f"  Total versions: {st['total_versions']}")
    size_kb = st["db_size_bytes"] / 1024
    click.echo(f"  DB size: {size_kb:.1f} KB")
    click.echo()


@workflow_.command("test")
@click.argument("workflow_id")
@click.option(
    "--data", "test_data", default=None, help="JSON data to send (inline or @file.json)"
)
@click.pass_context
def workflow_test(ctx: click.Context, workflow_id: str, test_data: str | None) -> None:
    """Test a workflow by triggering its webhook (workflow must be active with a webhook trigger)."""
    conn = _conn(ctx)
    wf = workflows.get_workflow(workflow_id, **conn)

    # Find webhook trigger node
    webhook_node = None
    for node in wf.get("nodes", []):
        if not isinstance(node, dict):
            continue
        node_type = node.get("type", "").lower()
        if "webhook" in node_type:
            webhook_node = node
            break

    if not webhook_node:
        error(
            "No webhook trigger found in this workflow. Only webhook-triggered workflows can be tested via CLI."
        )
        return

    if not wf.get("active"):
        error(
            f"Workflow is not active. Run: cli-anything-n8n workflow activate {workflow_id}"
        )
        return

    # Build webhook URL (allow : for path params like /:id, strip only dangerous chars)
    webhook_path = webhook_node.get("parameters", {}).get("path", "")
    if not webhook_path:
        webhook_id = webhook_node.get("webhookId", "")
        webhook_path = webhook_id or workflow_id
    webhook_path = re.sub(r"[^a-zA-Z0-9_\-/:.]", "", webhook_path).strip("/")
    if any(seg in {".", ".."} for seg in webhook_path.split("/")):
        error("Webhook path contains invalid dot segments")
        return

    base = conn["base_url"].rstrip("/")
    webhook_url = f"{base}/webhook/{webhook_path}"

    # Use the HTTP method configured on the webhook node (default POST)
    http_method = webhook_node.get("parameters", {}).get("httpMethod", "POST").upper()
    payload = _load_json_arg(test_data) if test_data else {}

    click.echo(f"  Triggering webhook ({http_method}): {webhook_url}")
    from cli_anything.n8n.utils.n8n_backend import DEFAULT_TIMEOUT

    resp = requests.request(
        http_method,
        webhook_url,
        json=payload if http_method in ("POST", "PUT", "PATCH") else None,
        params=payload if http_method == "GET" else None,
        timeout=DEFAULT_TIMEOUT,
    )

    if _json_flag(ctx):
        try:
            output(resp.json(), True)
        except (ValueError, AttributeError):
            output({"status": resp.status_code, "body": resp.text}, True)
        return

    if resp.ok:
        success(f"Webhook responded {resp.status_code}")
        try:
            output(resp.json(), False)
        except (ValueError, AttributeError):
            click.echo(f"  Response: {resp.text[:200]}")
    else:
        error(f"Webhook returned {resp.status_code}")


@cli.group("node")
def node_() -> None:
    """Search and explore n8n community nodes (via npm)."""


@node_.command("search")
@click.argument("query")
@click.option("--limit", default=15, type=int, help="Max results")
@click.pass_context
def node_search(ctx: click.Context, query: str, limit: int) -> None:
    """Search n8n community nodes on npm (26,000+ packages)."""
    data = nodes.search_nodes(query, limit=limit)

    if _json_flag(ctx):
        output(data, True)
        return

    pkgs = data.get("packages", [])
    if not pkgs:
        warn(f"No node packages found for '{query}'")
        return

    click.secho(
        f"\n  {data.get('total', '?'):,} packages found for '{query}' (showing {len(pkgs)}):\n",
        fg="cyan",
    )
    for p in pkgs:
        click.echo(f"    {click.style(p.get('name', '?'), fg='cyan')}")
        click.secho(
            f"      v{p.get('version', '?')}  by {p.get('author', '?')}  —  {p.get('description', '')}",
            fg="bright_black",
        )
    click.echo("\n  Use: cli-anything-n8n node info <package-name> for details")
    click.echo()
