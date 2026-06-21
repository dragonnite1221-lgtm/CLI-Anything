# ruff: noqa: F403, F405, E501
from .n8n_cli_base import *  # noqa: F403

# fmt: off
from .n8n_cli_p1 import _conn, _json_flag, cli  # noqa: E402,E501
from .n8n_cli_p2 import workflow_  # noqa: E402,E501
# fmt: on


@cli.command("health")
@click.option(
    "--diagnostic", is_flag=True, default=False, help="Show detailed diagnostic info"
)
@click.pass_context
def health_check(ctx: click.Context, diagnostic: bool) -> None:
    """Check n8n instance health and connectivity."""
    conn = _conn(ctx)
    base_url = conn["base_url"]

    if not base_url:
        error("No URL configured.")
        return

    results: dict[str, Any] = {"url": base_url, "status": "unknown"}

    # Test connectivity and measure response time
    start = time.time()
    try:
        wf_data = workflows.list_workflows(**conn, limit=1)
        elapsed = round((time.time() - start) * 1000)
        results["status"] = "connected"
        results["response_ms"] = elapsed

        wf_list = wf_data.get("data", []) if isinstance(wf_data, dict) else wf_data
        results["has_workflows"] = len(wf_list) > 0
    except requests.exceptions.ConnectionError:
        results["status"] = "unreachable"
    except requests.exceptions.HTTPError as exc:
        results["status"] = f"error_{exc.response.status_code}"

    # Try to get n8n version via healthz endpoint
    try:
        resp = requests.get(f"{base_url}/healthz", timeout=5)
        if resp.ok:
            health = (
                resp.json()
                if resp.headers.get("content-type", "").startswith("application/json")
                else {}
            )
            results["n8n_status"] = health.get("status", "ok")
    except (requests.exceptions.RequestException, ValueError):
        pass  # healthz is optional

    if diagnostic:
        import os

        results["diagnostic"] = {
            "base_url": base_url,
            "api_key_set": bool(conn.get("api_key")),
            "timeout": os.environ.get("N8N_TIMEOUT", "30"),
            "python": sys.version.split()[0],
            "cli_version": VERSION,
        }

    if _json_flag(ctx):
        output(results, True)
        return

    click.echo()
    click.secho("  n8n Health Check", fg="cyan", bold=True)
    click.secho("  " + "=" * 40, fg="cyan")
    click.echo()

    click.echo(f"  Instance:  {base_url}")

    if results["status"] == "connected":
        click.secho("  Status:    Connected", fg="green")
        click.echo(f"  Response:  {results.get('response_ms', '?')}ms")
    elif results["status"] == "unreachable":
        click.secho("  Status:    Unreachable", fg="red")
    else:
        click.secho(f"  Status:    {results['status']}", fg="red")

    if diagnostic and "diagnostic" in results:
        diag = results["diagnostic"]
        click.echo()
        click.secho("  Diagnostic", fg="cyan", bold=True)
        click.echo(f"  API Key:   {'configured' if diag['api_key_set'] else 'NOT SET'}")
        click.echo(f"  Timeout:   {diag['timeout']}s")
        click.echo(f"  Python:    {diag['python']}")
        click.echo(f"  CLI:       v{diag['cli_version']}")

    click.echo()


@workflow_.group("versions")
def workflow_versions_() -> None:
    """Version history and rollback (local snapshots)."""


@workflow_versions_.command("list")
@click.argument("workflow_id")
@click.option("--limit", default=20, type=int)
@click.pass_context
def versions_list(ctx: click.Context, workflow_id: str, limit: int) -> None:
    """List stored versions for a workflow."""
    vers = versions.list_versions(workflow_id, limit=limit)
    if _json_flag(ctx):
        output(vers, True)
        return
    if not vers:
        warn(f"No versions stored for workflow {workflow_id}")
        click.echo(
            "  Versions are saved automatically when you use: update, patch, autofix --apply"
        )
        return
    click.secho(f"\n  {len(vers)} version(s) for workflow {workflow_id}:\n", fg="cyan")
    for v in vers:
        click.echo(
            f"    v{v['version_number']:>3d}  {v['created_at']}  {click.style(v['trigger'], fg='cyan'):>12s}  {v['workflow_name']}"
        )
    click.echo()
